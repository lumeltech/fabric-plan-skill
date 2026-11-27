"""Supplied hash vectors, first anchors and completeness of portable construction."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from runtime.dimension_hash import generate_dimension_id,generate_dimension_hash
from runtime.anchor_measures import apply_anchors,capture_context,AnchorContractGap
from runtime.authoring_flow import require_import_contract
from runtime.planning_presentation import build_application
from runtime.scope import prepare_scope
from runtime.workflow import SUPPORTED
from runtime.identity import xxh3

ROOT=Path(__file__).resolve().parents[1]


def inputs():
    return runpy.run_path(str(ROOT/'assets/examples/anchor-measures/new-report.py'))['inputs']()


def owner(result):
    i=result['identities'][0]
    return result['raw'][f"sheets/{i['sheetId']}/visuals/{i['visualId']}/properties.json"]['properties'],i


class DimensionHashTests(unittest.TestCase):
    def test_exact_supplied_source_vectors(self):
        fixtures={
            'DimProduct[Manufacturer]':'14835107197258497178',
            'DimProduct[ColorName]':'8441616133237296584',
            'Date[Year]':'11664616959742279520',
            'Date[Quarter Name]':'12377755039553282686'}
        for source,expected in fixtures.items():
            self.assertEqual(generate_dimension_id(source),expected)
        self.assertNotEqual(generate_dimension_id('Date[Year]'),generate_dimension_id('date[Year]'))

    def test_saved_layout_hash_replay_from_original_ordered_ids(self):
        rows=['6143545636991853186','4132416716468767831','1327320752449392856','4139092083215132129']
        cols=['9375281995746324753','82274462402208218']
        self.assertEqual(generate_dimension_hash(rows,cols),'f66e5cc9a49071b9')
        for changed in ((rows[::-1],cols),(rows,cols[::-1]),(cols,rows),(rows[:-1],cols)):
            self.assertNotEqual(generate_dimension_hash(*changed),'f66e5cc9a49071b9')

    def test_empty_axes_and_unpadded_lowercase_hex(self):
        self.assertEqual(generate_dimension_hash([],[]),format(xxh3('__'),'x'))
        # Formatting is part of the contract even if the supplied layout is 16 digits.
        with patch('runtime.dimension_hash.xxh3',return_value=0xAB):
            self.assertEqual(generate_dimension_hash(['0'],[]),'ab')
        with patch('runtime.dimension_hash.xxh3',return_value=0):
            self.assertEqual(generate_dimension_hash([],[]),'0')
        self.assertNotEqual(generate_dimension_hash(['1'],[]),generate_dimension_hash([],['1']))

    def test_invalid_or_imprecise_ids_rejected(self):
        for bad in (123,None,True):
            with self.assertRaises(TypeError):generate_dimension_id(bad)
        for bad in (None,('1',),[14835107197258497178],['Date[Year]'],['01'],['-1'],['18446744073709551616'],[True]):
            with self.assertRaises((TypeError,ValueError)):generate_dimension_hash(bad,[])
        generate_dimension_hash(['0','18446744073709551615'],[])

    def test_first_anchor_base_application_retains_complete_input_and_formula(self):
        model,spec=inputs();result=build_application(model,spec);props,i=owner(result)
        s=props['visualState'];member=next(m for m in s['manage_measures'] if m['id']==i['measures']['benefits'])
        cfg=member['anchor_config']
        self.assertEqual(cfg['row_dimensions'],[i['dimensions']['Region[Region]']])
        self.assertEqual(cfg['col_dimensions'],[i['dimensions']['Calendar[Year]']])
        self.assertEqual(cfg['dimension_hash'],generate_dimension_hash(
            [d['id'] for d in s['rowDimensions']],[d['id'] for d in s['columnDimensions']]))
        self.assertNotEqual(cfg['dimension_hash'],generate_dimension_hash(cfg['row_dimensions'],cfg['col_dimensions']))
        self.assertEqual(s['totals_config']['column_sub_total'],'Left')
        self.assertEqual(require_import_contract(spec,result)['status'],'passed')
        data=next(v for k,v in result['raw'].items() if k.endswith('/dataInput.json'))['columns']
        self.assertEqual(len(data),3)
        formula=next(r for r in data if r['measureGuid']==i['measures']['cost'])['columnMeta']['measure_type']['Formula']['formula']
        self.assertIn('M_'+i['measures']['benefits'],formula)
        number=next(r for r in data if r['measureGuid']==i['measures']['benefits'])['columnMeta']['measure_type']['DataInput']
        self.assertEqual(number['allow_input'],'ReadAndEdit')

    def test_scope_does_not_drop_anchor_and_import_gate_detects_removed_or_altered(self):
        model,spec=inputs();scope=prepare_scope(spec,SUPPORTED,model)
        # Use the scope's actual returned draft key without bypassing its gap report.
        draft=scope['spec']
        self.assertEqual(draft['sheets'][0]['measures'][1]['anchor'],spec['sheets'][0]['measures'][1]['anchor'])
        result=build_application(model,spec)
        for change in ('remove','hash','display','total'):
            candidate=copy.deepcopy(result);props,i=owner(candidate)
            member=next(m for m in props['visualState']['manage_measures'] if m['id']==i['measures']['benefits'])
            if change=='remove':member.pop('anchor_config')
            elif change=='hash':member['anchor_config']['dimension_hash']='abc'
            elif change=='display':member['anchor_config']['display_at_all_levels']=True
            else:props['visualState']['totals_config']['column_sub_total']=None
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,'IMPORT_CONTRACT'):
                require_import_contract(spec,candidate)

    def test_native_and_formula_keep_types(self):
        # Native/formula display anchors use the same registry without granting input.
        from runtime.construct import planning
        from runtime.identity import Registry
        model,spec=inputs();sheet=spec['sheets'][0]
        sheet['measures'][0]['anchor']=copy.deepcopy(sheet['measures'][1]['anchor'])
        sheet['measures'][2]['anchor']=copy.deepcopy(sheet['measures'][1]['anchor'])
        _,raw,identity=planning(model,sheet,Registry())
        records=next(v['columns'] for k,v in raw.items() if k.endswith('/dataInput.json'))
        self.assertEqual([set(r['columnMeta']['measure_type']) for r in records],[{'Native'},{'DataInput'},{'Formula'}])

    def test_forecast_and_formula_locked_input_keep_configuration(self):
        from runtime.construct import planning
        from runtime.identity import Registry
        model,spec=inputs();sheet=spec['sheets'][0]
        sheet['measures'][1]['allow_input']={'BasedOnFormula':'${salary} > 0'}
        sheet['measures'].append({'key':'forecast','kind':'Forecast','label':'Salary Forecast',
            'actuals':'salary','start':'2027-01-01','end':'2027-12-31','timezone':'UTC',
            'openDefault':{'StaticValue':0},'aggregation':'Sum',
            'anchor':copy.deepcopy(sheet['measures'][1]['anchor'])})
        registry=Registry()
        _,anchored,identity=planning(model,sheet,registry)
        plain=copy.deepcopy(sheet)
        plain['sheetId']=identity['sheetId'];plain['visualId']=identity['visualId']
        for m in plain['measures']:m.pop('anchor',None)
        _,unanchored,_=planning(model,plain,registry)
        data=next(v for k,v in anchored.items() if k.endswith('/dataInput.json'))
        same=next(v for k,v in unanchored.items() if k.endswith('/dataInput.json'))
        self.assertEqual(data,same)
        forecast=next(r for r in data['columns'] if r['measureGuid']==identity['measures']['forecast'])
        self.assertEqual(forecast['columnMeta']['measure_type']['Forecast']['edit_config']['allow_input'],'ReadAndEdit')

    def test_effective_pivot_order_and_cross_axis_hashed_not_base(self):
        model,spec=inputs();result=build_application(model,spec);props,i=owner(result)
        for m in props['visualState']['manage_measures']:m.pop('anchor_config',None)
        state=props['visualState'];rows=state['rowDimensions'];cols=state['columnDimensions']
        state['pivot']={'active_id':'7','configs':[{'id':'7','hidden':False,
            'row_dimensions':[rows[1]['id'],rows[0]['id']],'col_dimensions':None}]}
        state['pivotExplorer']={'activePivot':'7'}
        c=capture_context(props,'owner')
        self.assertEqual(c['dimension_hash'],generate_dimension_hash([d['id'] for d in rows[::-1]],[d['id'] for d in cols]))
        state['pivot']['configs'][0].update(row_dimensions=[rows[0]['id']],col_dimensions=[rows[1]['id']])
        self.assertEqual(capture_context(props,'owner')['dimension_hash'],generate_dimension_hash([rows[0]['id']],[rows[1]['id']]))
        state['pivotExplorer']['activePivot']='8'
        with self.assertRaisesRegex(AnchorContractGap,'PIVOT_AMBIGUOUS'):capture_context(props,'owner')

    def test_all_existing_stale_hashes_rejected_without_rebinding(self):
        model,spec=inputs();result=build_application(model,spec);props,_=owner(result)
        props['visualState']['rowDimensions'].reverse()
        before=copy.deepcopy(props)
        with self.assertRaisesRegex(AnchorContractGap,'HASH_MISMATCH'):capture_context(props,'owner')
        self.assertEqual(props,before)

    def test_new_report_cli_is_self_contained(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/'report.json'
            proc=subprocess.run([sys.executable,str(ROOT/'assets/examples/anchor-measures/new-report.py'),'--out',str(out)],
                                cwd=folder,capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            result=json.loads(out.read_text())
            self.assertEqual(result['importContract']['status'],'passed')


if __name__=='__main__':unittest.main()
