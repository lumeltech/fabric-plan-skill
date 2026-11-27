"""Compare the constructor with independently captured, sanitized persisted JSON."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,unittest
from pathlib import Path
from runtime.codec import load,dumps,loads
from runtime.rule_factories import new_rule,measure_weighted_rule,distribute_columns_by_measure,verify_saved_rule,distribute_rows

class MeasureWeightedRules(unittest.TestCase):
    def test_row_current_year_matches_saved_planning_rule(self):
        saved=load(Path(__file__).resolve().parents[1]/'assets/fixtures/measure-weighted-row-rule.json')
        request=measure_weighted_rule(saved['rule_id'],saved['name'],['target'],'basis',
            {'target':'9007199254740993','basis':'18446744073709551615'},axis='Row',weights_period='CurrentYear')
        self.assertEqual(verify_saved_rule(request,[saved])['persistedId'],'102')
        self.assertNotIn('Column',request['ruleOperation']['New']['rule_type']['Distribute']['operation'])

    def test_row_rejects_unsupported_period_or_column_profile_mixing(self):
        for axis,period in [('Row',None),('Row','CurrentMonth'),('Column','CurrentYear')]:
            with self.subTest(axis=axis,period=period),self.assertRaises(ValueError):
                measure_weighted_rule('1','x',['target'],'basis',{'target':'2','basis':'3'},axis=axis,weights_period=period)
    def setUp(self):
        self.saved=load(Path(__file__).resolve().parents[1]/'assets/fixtures/measure-weighted-column-rule.json')
        self.request=measure_weighted_rule('9007199254741001','Distribute target using budget weights',
            ['target'],'budget',{'target':'9007199254740993','budget':'18446744073709551615'},axis='Column')
    def test_matches_independent_saved_shape(self):
        result=verify_saved_rule(self.request,[self.saved])
        self.assertEqual(result['persistedId'],'101')
        self.assertNotEqual(result['persistedId'],result['ruleId'])
        self.assertEqual(result['execution'],'not-tested')
        self.assertNotIn('id',self.request['ruleOperation']['New'])
    def test_uses_exact_measure_identity_and_absent_self_row(self):
        value=loads(dumps(self.request))['ruleOperation']['New']['rule_type']['Distribute']['operation']['Column']
        self.assertEqual(value,self.saved['rule_type']['Distribute']['operation']['Column'])
        self.assertEqual(value['reference']['MeasureIdWithReference'],{'measure':{'Measure':'18446744073709551615'}})
    def test_rebinds_without_captured_ids_or_label_matching(self):
        p=measure_weighted_rule('31','Fresh rule',['new_input'],'new_weight',
            {'new_input':'42','new_weight':'43'},axis='Column',columns={'Selected':['52']},rows={'Selected':['62']})['ruleOperation']['New']
        self.assertEqual(p['measures'],{'SelectedMeasures':['42']})
        self.assertEqual(p['columns'],{'Selected':['52']});self.assertEqual(p['rows'],{'Selected':['62']})
        self.assertEqual(p['rule_type'],distribute_columns_by_measure('43'))
    def test_unknown_reference_or_wrong_axis_is_not_silently_substituted(self):
        for kwargs in ({'axis':'Row'},{'axis':'column'},{'axis':'Column','weight_measure':'unresolved'},
                       {'axis':'Column','target_measures':[]},{'axis':'Column','target_measures':['target','target']}):
            request={'logical_id':'1','name':'x','target_measures':['target'],'weight_measure':'budget',
                'measure_ids':{'target':'2','budget':'3'},**kwargs}
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):measure_weighted_rule(**request)
    def test_extra_row_range_fields_or_self_measure_are_not_guessed(self):
        cases=[]
        for key,val in [('row','Self'),('period','All'),('range_operation','Average')]:
            p=copy.deepcopy(self.saved['rule_type']);p['Distribute']['operation']['Column']['reference']['MeasureIdWithReference'][key]=val;cases.append(p)
        p=copy.deepcopy(self.saved['rule_type']);p['Distribute']['operation']['Column']['reference']['MeasureIdWithReference']['measure']='SelfMeasure';cases.append(p)
        p=copy.deepcopy(self.saved['rule_type']);p['Distribute']['operation']['Column']['apply_to_dimensions']={'SelectedDimensions':['1']};cases.append(p)
        for p in cases:
            with self.subTest(p=p),self.assertRaises(ValueError):new_rule('1','x',p)
    def test_wrong_saved_source_target_scope_or_enabled_flag_fails(self):
        for key,value in [('rule_type',distribute_columns_by_measure('44')),('measures',{'SelectedMeasures':['55']}),
            ('columns',{'Selected':['66']}),('rows',{'Selected':['77']}),('is_disabled',True),('name','changed')]:
            p=copy.deepcopy(self.saved);p[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):verify_saved_rule(self.request,[p])
        for rows in ([],[self.saved,self.saved]):
            with self.assertRaises(ValueError):verify_saved_rule(self.request,rows)
    def test_existing_row_branches_preserved(self):
        for ref,weights in [('Equal',None),('SelfWeight',None),('ManualInput',{'11':1,'12':2})]:
            kind=distribute_rows(ref,weights=weights)
            self.assertEqual(new_rule('1','old row',kind)['ruleOperation']['New']['rule_type'],kind)
    def test_period_scope_not_widened_to_all(self):
        with self.assertRaises(ValueError):measure_weighted_rule('1','x',['target'],'budget',
            {'target':'2','budget':'3'},axis='Column',columns={'PeriodRange':{'from':'Nov','to':'Dec'}})

if __name__=='__main__':unittest.main()
