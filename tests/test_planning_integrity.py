import copy,unittest,tempfile
from runtime.codec import pack,load
from runtime.construct import build
from runtime.matrix_formatting import compile_formatting
from runtime.planning_integrity import DEFAULTS,check_styles,complete_styles,check_properties,repair_properties,guard_write
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def example():
    a=dict(id='Region[Country]',sourceId='unchanged-source',sourceType='PowerBI',columnType='Column',dataRoleType='Grouping',tableName='Region',columnName='Country',name='Market',customName='Market',isRenamed=True)
    return dict(pivotAssignments=[a],visualState=dict(globalStyles={'fontFamily':'Arial','fontSize':'12','futureOption':True},
        manage_measures=[{'id':'18446744073709550001','label':'EST LC FC Amt','formula':'[source]'}],
        rowDimensions=[dict(id='stable-row',externalKey='Region[Country]',isNative=True,label='Market')],columnDimensions=[],
        dimension_id_mapping={'mappings':{'Region[Country]':{'Skip':{}}},'pivot':[dict(id='Region[Country]',source_type='PowerBI',column_type='Column',column_name='Country',name='Market',custom_name='Market')]},
        filters=[dict(pivotAssignments=[copy.deepcopy(a)],configuration={'name':'Market'},
            sort={'columnId':'Region[Country]','columnName':'Market'},
            filterDTO={'columnIds':['Region[Country]'],'columnNames':['Market'],'tableNames':['Region'],'sourceType':['PowerBI'],'columnType':['Column'],'valuesFilter':[{'value':'France','label':'France'}]})]),
        unrelated={'sourceType':'Visual','columnType':'Column','dataRoleType':'Measure','id':'18446744073709550001','sourceId':'123','name':'Business label','columnName':'Source label'})

class PlanningIntegrityTests(unittest.TestCase):
    def test_absent_defaults_completed_preserving_explicit_and_unknown(self):
        before=example();original=copy.deepcopy(before);after=repair_properties(before)['properties']
        self.assertEqual(before,original);self.assertTrue(set(DEFAULTS)<=set(after['visualState']['globalStyles']))
        self.assertEqual(after['visualState']['globalStyles']['fontFamily'],'Arial')
        self.assertTrue(after['visualState']['globalStyles']['futureOption']);check_properties(after)

    def test_names_reconciled_across_assignment_dimension_lookup_filter_sort_dto(self):
        r=repair_properties(example());p=r['properties'];vs=p['visualState'];f=vs['filters'][0]
        self.assertEqual(p['pivotAssignments'][0]['name'],'Country');self.assertFalse(p['pivotAssignments'][0]['isRenamed'])
        self.assertEqual(vs['rowDimensions'][0]['label'],'Country')
        self.assertEqual(vs['dimension_id_mapping']['pivot'][0]['name'],'Country')
        self.assertIsNone(vs['dimension_id_mapping']['pivot'][0]['custom_name'])
        self.assertEqual(f['pivotAssignments'][0]['name'],'Country');self.assertEqual(f['configuration']['name'],'Country')
        self.assertEqual(f['sort']['columnName'],'Country');self.assertEqual(f['filterDTO']['columnNames'],['Country'])

    def test_storage_identifiers_values_formulas_and_from_sheets_unchanged(self):
        a=example();b=repair_properties(a)['properties'];av=a['visualState'];bv=b['visualState']
        self.assertEqual(a['unrelated'],b['unrelated']);self.assertEqual(av['manage_measures'],bv['manage_measures'])
        self.assertEqual(av['dimension_id_mapping']['mappings'],bv['dimension_id_mapping']['mappings'])
        self.assertEqual(av['filters'][0]['filterDTO']['valuesFilter'],bv['filters'][0]['filterDTO']['valuesFilter'])
        for k in ('id','sourceId'):self.assertEqual(a['pivotAssignments'][0][k],b['pivotAssignments'][0][k])
        self.assertEqual(av['rowDimensions'][0]['id'],bv['rowDimensions'][0]['id'])

    def test_idempotent_repair(self):
        once=repair_properties(example());twice=repair_properties(once['properties'])
        self.assertEqual(twice['changes'],[]);self.assertEqual(twice['properties'],once['properties'])

    def test_invalid_types_fail_without_silent_overwrite(self):
        for k,v in [('fontSize',14),('fontSize','14px'),('headerHeight',True),('headerFormat','false'),('fontStyle',None)]:
            p=example();p['visualState']['globalStyles'][k]=v;before=copy.deepcopy(p)
            with self.subTest(k=k,v=v),self.assertRaises(ValueError):repair_properties(p)
            self.assertEqual(p,before)

    def test_read_edit_modes_independent_and_border_null_zero_preserved(self):
        s={'globalStyles':{'columnStyle':{'custom':{'read':{'background':'#123456','borderSides':None,'borderWidth':0}}}}}
        out=complete_styles(s)['globalStyles']['columnStyle']['custom']
        self.assertEqual(out['read']['background'],'#123456');self.assertNotEqual(out['edit']['background'],'#123456')
        self.assertIsNone(out['read']['borderSides']);self.assertEqual(out['read']['borderWidth'],0)

    def test_current_model_required_identity_cannot_be_guessed(self):
        with self.assertRaises(ValueError):repair_properties(example(),{'fields':[]})
        p=example();p['pivotAssignments'][0]['id']='Market'
        with self.assertRaises(ValueError):repair_properties(p)
        model={'fields':[dict(id='Region[Country]',tableName='Region',columnName='Country',columnType='Column')]}
        check_properties(repair_properties(example(),model)['properties'],model)

    def test_check_rejects_alias_and_missing_defaults(self):
        p=example()
        with self.assertRaises(ValueError):check_properties(p)
        p['visualState']=complete_styles(p['visualState'])
        with self.assertRaisesRegex(ValueError,'Inconsistent semantic'):check_properties(p)

    def test_filter_parallel_arrays_must_align(self):
        p=example();p['visualState']['filters'][0]['filterDTO']['tableNames']=[]
        with self.assertRaisesRegex(ValueError,'inconsistent lengths'):repair_properties(p)

    def test_public_writes_reject_unchecked_payload(self):
        bad=example();good=repair_properties(bad)['properties']
        for p,ok in [(bad,False),(good,True)]:
            requests=[('/v1/workspaces/workspace/plans',pack({'entities/plan/visuals/grid/properties.json':{'properties':p}})),
                ('/v1/workspaces/workspace/plans/id/updateDefinition',pack({'entities/plan/visuals/grid/properties.json':{'properties':p}})),
                ]
            for route,body in requests:
                if ok:guard_write('POST',route,body)
                else:
                    with self.subTest(route=route),self.assertRaises(ValueError):guard_write('POST',route,body)

    def test_http_client_rejects_before_credentials_journal_or_adapter(self):
        from runtime.transport import Client
        calls=[]
        with tempfile.TemporaryDirectory() as folder:
            client=Client('https://api.fabric.microsoft.com/v1','UNSET_INTEGRITY_TEST_TOKEN',journal=folder,adapter=lambda *args:calls.append(args))
            with self.assertRaisesRegex(ValueError,'Incomplete Planning globalStyles'):
                client.request('POST','/workspaces/w/plans',pack({'sheets/s/visuals/v/properties.json':{'properties':example()}}),label='rejected')
            self.assertEqual(calls,[]);self.assertEqual(list(Path(folder).iterdir()),[])

    def test_builder_and_formatting_compiler_complete_defaults(self):
        raw=build(load(ROOT/'fixtures/model.json'),load(ROOT/'fixtures/finance-spec.json'))['raw']
        count=0
        for path,v in raw.items():
            p=v.get('properties',{}) if isinstance(v,dict) else {}
            if 'manage_measures' in p.get('visualState',{}):check_properties(p);count+=1
        self.assertGreater(count,0)
        check_styles(compile_formatting({'globalStyles':{'fontSize':'12'},'manage_measures':[]},{})['state'])

if __name__=='__main__':unittest.main()
