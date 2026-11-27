import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,unittest
from pathlib import Path
from runtime.codec import load
from runtime.construct import planning
from runtime.identity import Registry
from runtime.input_factories import input_create
from runtime.forecast import forecast_config
from runtime.input_policy import allow_input
from runtime.scope import prepare_scope
from runtime.business_intent import plan_intent

ROOT=Path(__file__).resolve().parents[1]

class InputEditabilityTests(unittest.TestCase):
    def make(self,kind='Number',**kw):
        return input_create('401','Entry',kind,{},'config',**kw)['columnMeta']['measure_type']

    def forecast(self,**kw):
        spec={'actuals':'actual','start':'2026-01-01','end':'2026-12-31','timezone':'UTC',**kw}
        return forecast_config(spec,{'actual':'101','eligible':'102'},{'actual':'Native','eligible':'Native'},columns=['Date[Year]'])

    def test_numeric_and_typed_and_visual_inputs_default_both(self):
        for kind in ['Number','ShortText','LongText','SingleSelect','MultiSelect','Date','Person','Checkbox']:
            for visual in [False,True]:
                with self.subTest(kind=kind,visual=visual):
                    p=self.make(kind,visual_column=visual)
                    if visual:p=p['VisualColumn']
                    self.assertEqual(p['DataInput']['allow_input'],'ReadAndEdit')

    def test_explicit_edit_and_formula_preserved_and_resolved(self):
        self.assertEqual(self.make(allow_input='Edit')['DataInput']['allow_input'],'Edit')
        p=self.make('LongText',allow_input={'BasedOnFormula':'${eligible} > 0'},measures={'eligible':'102'})
        self.assertEqual(p['DataInput']['allow_input'],{'BasedOnFormula':'M_102 > 0'})

    def test_simulation_defaults_both(self):
        settings={'source_measure_id':'base','simulation_slider':True,'simulation_range':10,
          'distribute_parent_value_to_children':False,'simulation_value_align':'Right','variance_formatting_style':'None'}
        p=input_create('401','Simulate','Simulation',settings,'config',measures={'base':'102'})
        self.assertEqual(p['columnMeta']['measure_type']['DataInput']['allow_input'],'ReadAndEdit')

    def test_invalid_or_unresolved_condition_does_not_fall_back(self):
        for value in [None,'ReadOnly',{'BasedOnFormula':''},{'BasedOnFormula':'${missing} > 0'},{'BasedOnFormula':'M_999 > 0'}]:
            with self.subTest(value=value),self.assertRaises(ValueError):allow_input(value,{'eligible':'102'})

    def test_forecast_mode_and_condition_use_edit_config(self):
        self.assertEqual(self.forecast()['edit_config']['allow_input'],'ReadAndEdit')
        self.assertEqual(self.forecast(allow_input='Edit')['edit_config']['allow_input'],'Edit')
        c=self.forecast(allow_input={'BasedOnFormula':'${eligible} > 0'})
        self.assertEqual(c['edit_config']['allow_input'],{'BasedOnFormula':'M_102 > 0'})
        self.assertEqual(c['closed_period_config']['method'],{'LinkToMeasure':'101'})
        self.assertEqual(c['open_period_config']['method'],{'DataInput':'Blank'})

    def test_reference_gate_not_silently_copied_or_erased(self):
        ref={'edit_config':{'allow_input':{'BasedOnFormula':'M_999 > 0'}}};before=copy.deepcopy(ref)
        with self.assertRaisesRegex(ValueError,'explicit policy'):self.forecast(referenceForecast=ref)
        c=self.forecast(referenceForecast=ref,allow_input={'BasedOnFormula':'${eligible} > 0'})
        self.assertEqual(c['edit_config']['allow_input'],{'BasedOnFormula':'M_102 > 0'})
        self.assertEqual(ref,before)
        self.assertEqual(self.forecast(referenceForecast={'edit_config':{'allow_input':'Edit'}})['edit_config']['allow_input'],'ReadAndEdit')

    def test_base_constructor_default_and_existing_condition(self):
        s=load(ROOT/'assets/fixtures/finance-spec.json')['sheets'][0]
        s['measures']=[{'kind':'Formula','key':'eligible','label':'Eligibility','formula':'1'},
          {'kind':'DataInput','key':'entry','label':'Entry'},
          {'kind':'DataInput','key':'gated','label':'Gated','allow_input':{'BasedOnFormula':'${eligible} > 0'}}]
        _,raw,ids=planning(load(ROOT/'assets/fixtures/model.json'),s,Registry())
        records=next(v['columns'] for k,v in raw.items() if k.endswith('dataInput.json'))
        self.assertEqual(records[1]['columnMeta']['measure_type']['DataInput']['allow_input'],'ReadAndEdit')
        self.assertEqual(records[2]['columnMeta']['measure_type']['DataInput']['allow_input'],{'BasedOnFormula':'M_'+ids['measures']['eligible']+' > 0'})

    def test_conditional_business_request_routes_f30(self):
        b=load(ROOT/'assets/examples/business-intent/conditional-input.json');p=plan_intent(b)
        self.assertEqual(p['requirements'][0]['modules'],['F30'])
        b['requirements'][0]['details'].pop('expression')
        self.assertFalse(plan_intent(b)['readyForAuthoring'])

if __name__=='__main__':unittest.main()
