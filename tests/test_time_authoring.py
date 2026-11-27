import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,importlib.util
from pathlib import Path
import unittest
from runtime.codec import parts,unpack
from runtime.construct import expression
from runtime.forecast import resolve_time_levels
from runtime.formula_syntax import equality_issues,check_formula,repair_equality
from runtime.time_authoring import preferred_calendar_axis,prefer_forecast_axis,apply_time_axis,add_time_column,time_expression
from runtime.discovery import discover
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('time_example',ROOT/'assets/examples/forecast-time-intelligence/build.py')
example=importlib.util.module_from_spec(s);s.loader.exec_module(example)

class FormulaEqualityTests(unittest.TestCase):
    def test_repairs_comparison_only(self):
        source='var test = 0; VAR "FX=label" = 1; IF(AND(test = 0, [Measure = label] = 0), "a=b", 1) // a = b'
        out=repair_equality(source)
        self.assertEqual(len(out['changes']),2)
        self.assertIn('var test = 0',out['formula']);self.assertIn('VAR "FX=label" = 1',out['formula'])
        self.assertIn('[Measure = label] == 0',out['formula']);self.assertTrue(out['formula'].endswith('// a = b'))
        self.assertEqual(repair_equality(out['formula'])['changes'],[])
    def test_preserves_existing_operators_literals_and_comments(self):
        formula='IF(AND(M_123 == 0, M_124 >= 0, M_125 <= 0, M_126 != 0), "escaped\\\"=text", 0) /* = */'
        self.assertEqual(check_formula(formula),formula)
    def test_factory_rejects_invalid_comparison(self):
        with self.assertRaisesRegex(ValueError,'Comparison requires =='):expression('IF(${x} = 0, 1, 0)',{'x':'123'})
        self.assertEqual(expression('var n = 0; IF(${x} == n, 1, 0)',{'x':'123'}),'var n = 0; IF(M_123 == n, 1, 0)')
    def test_unclosed_literals_rejected(self):
        for formula in ('"not closed','[not closed','/* not closed'):
            with self.assertRaises(ValueError):equality_issues(formula)
    def test_apostrophe_and_quoted_bracket_reference(self):
        self.assertEqual(repair_equality("IF([Customer's amount] = 0, 1, 0)")['formula'],"IF([Customer's amount] == 0, 1, 0)")
        self.assertEqual(check_formula('IF(["label ] = text"] == 0, 1, 0)'), 'IF(["label ] = text"] == 0, 1, 0)')

class TimeAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=example.sample()
    def test_new_builder_replaces_composite(self):
        model,spec,result,*_=self.data
        props=next(v['properties'] for k,v in result['raw'].items() if k.endswith('/properties.json'))
        self.assertEqual([d['externalKey'] for d in props['visualState']['columnDimensions']],['Calendar[Year]','Calendar[Quarter]','Calendar[MonthName]'])
        self.assertEqual(spec['sheets'][0]['columns'][-1],'Calendar[YearMonth]')
    def test_resolved_calendar_and_week_parentage(self):
        model=self.data[0]
        yearly=preferred_calendar_axis(model,'Calendar','Year');self.assertEqual(yearly['columns'],['Calendar[Year]'])
        weekly=preferred_calendar_axis(model,'Calendar','Week');self.assertEqual(len(weekly['columns']),2)
        nested=preferred_calendar_axis(model,'Calendar','Week',week_parentage_valid=True)
        self.assertEqual(len(resolve_time_levels(nested['columns'],nested['columnTimeLevels'])),4)
        nested['columnTimeLevels']['Calendar[Week]'].pop('parentageValidated')
        with self.assertRaisesRegex(ValueError,'parentage'):resolve_time_levels(nested['columns'],nested['columnTimeLevels'])
    def test_missing_quarter_fallback_and_explicit_field_resolution(self):
        model=copy.deepcopy(self.data[0]);model['fields']=[f for f in model['fields'] if f['id']!='Calendar[Quarter]']
        self.assertEqual(preferred_calendar_axis(model,'Calendar')['columns'],['Calendar[Year]','Calendar[MonthName]'])
        with self.assertRaises(ValueError):preferred_calendar_axis(model,'Unknown')
    def test_composite_exception_and_nondates(self):
        model,spec,*_=self.data;s=copy.deepcopy(spec['sheets'][0]);s['columns'].append('Product[Product]')
        with self.assertRaises(ValueError):prefer_forecast_axis(model,s)
        s=copy.deepcopy(spec['sheets'][0]);s['allowCompositeTimeAxis']=True
        with self.assertRaises(ValueError):prefer_forecast_axis(model,s)
        s.update(compositeTimeAxisReason='Explicitly requested composite label',columnTimeLevels={'Calendar[Year]':'Year','Calendar[Quarter]':'Quarter','Calendar[YearMonth]':'Month'})
        self.assertEqual(prefer_forecast_axis(model,s),s)
    def test_candidate_preserves_other_parts_axis_and_companions(self):
        model,spec,result,request,candidate,manifest,_=self.data
        before=parts(result['envelope']);after=parts(candidate);changed=manifest['changedParts']
        self.assertEqual({k for k in before if before[k]!=after[k]},set(changed))
        b=unpack(result['envelope']);a=unpack(candidate)
        dp=next(k for k in b if k.endswith('/dataInput.json'));pp=dp.replace('dataInput','properties')
        self.assertEqual(a[dp]['columns'][:-1],b[dp]['columns'])
        self.assertEqual(a[pp]['properties']['pivotAssignments'],b[pp]['properties']['pivotAssignments'])
        self.assertEqual(a[pp]['properties']['visualState']['columnDimensions'],b[pp]['properties']['visualState']['columnDimensions'])
        self.assertEqual(a[pp]['properties']['visualState']['totals_config'],b[pp]['properties']['visualState']['totals_config'])
        last=a[dp]['columns'][-1];self.assertIn('VisualColumn',last['columnMeta']['measure_type'])
        self.assertIn('EOMONTH(DATE(VR_CALC_VARIABLE_example_asof))',manifest['formula'])
        self.assertIn('BLANK',manifest['formula'])
    def test_duplicate_and_unresolved_source_rejected(self):
        _,_,result,request,candidate,*_=self.data
        with self.assertRaises(ValueError):add_time_column(candidate,**request)
        bad=copy.deepcopy(request);bad['source_id']='123'
        with self.assertRaises(ValueError):add_time_column(result['envelope'],**bad)
    def test_formula_shapes_and_input_visual_column(self):
        for period in ('MTD','QTD','YTD'):
            self.assertEqual(time_expression('123',period,'DATE(VR_CALC_VARIABLE_x)'),f'SUM({period}(M_123, 0, DATE(VR_CALC_VARIABLE_x)))')
        note=self.data[-1];self.assertIn('VisualColumn',note['columnMeta']['measure_type'])
        self.assertEqual(note['columnMeta']['measure_type']['VisualColumn']['DataInput']['allow_input'],'ReadAndEdit')
    def test_axis_repair_preserves_storage_and_unrelated_settings(self):
        model,_,result,*_=self.data
        props=next(v['properties'] for k,v in result['raw'].items() if k.endswith('/properties.json'))
        original=copy.deepcopy(props)
        new=apply_time_axis(props,model,['Calendar[Year]','Calendar[MonthName]'])
        self.assertEqual(new['visualState']['manage_measures'],original['visualState']['manage_measures'])
        self.assertEqual(new['visualState']['aggregation_config'],original['visualState']['aggregation_config'])
        self.assertEqual(props,original)
    def test_discoverability(self):
        for query in ('monthly forecasting','one-time column','as-of date','QTD','SELECTEDVALUE'):
            self.assertIn('TIME-INTELLIGENCE',[m['id'] for m in discover(query)['modules']])
        self.assertIn('FORMULA-SYNTAX',[m['id'] for m in discover('double equals')['modules']])
    def test_whole_candidate_invariants(self):
        from runtime.validate import validate_plan
        validate_plan(unpack(self.data[4]))
    def test_shared_cutoff_cannot_silently_become_local(self):
        from runtime.business_intent import plan_intent
        result=plan_intent({'request':'A dashboard cutoff controls QTD in all sheets','requirements':[
          {'id':'cutoff','text':'shared cutoff','intent':'time-intelligence','details':{
            'source':'forecast','period':'QTD','cutoffScope':'dashboard','cutoffControl':'parameter',
            'cutoff':'selected date','aggregation':'Sum','missingPolicy':'Blank'}}]})
        self.assertFalse(result['readyForAuthoring'])
        self.assertIn('shared dashboard',result['requirements'][0]['unresolved'][0])

if __name__=='__main__':unittest.main()
