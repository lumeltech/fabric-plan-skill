import copy,sys,unittest
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from runtime.codec import load,pack
from runtime.construct import planning
from runtime.identity import Registry
from runtime.input_factories import input_create
from runtime.forecast import forecast_config
from runtime.planning_integrity import guard_write

class NumericInputContracts(unittest.TestCase):
    def spec(self):
        s=load(ROOT/'fixtures/finance-spec.json')['sheets'][0]
        s['measures']=[{'kind':'Formula','key':'limit','label':'Limit','formula':'0.15','visible':False},
            {'kind':'DataInput','key':'rate','label':'Rate','aggregation':'AverageLeaf','min_value':{'Static':0},
             'max_value':{'Measure':'limit'},'default_value':{'Static':Decimal('0.03')}}]
        return s
    def build(self,s):return planning(load(ROOT/'fixtures/model.json'),s,Registry())
    def test_rate_preserves_fraction_default_and_resolves_limit(self):
        _,raw,ids=self.build(self.spec())
        records=next(v['columns'] for k,v in raw.items() if k.endswith('dataInput.json'))
        number=records[1]['columnMeta']['measure_type']['DataInput']['column_type']['Number']
        self.assertEqual(number['default_value'],{'Static':Decimal('0.03')})
        self.assertEqual(number['max_value'],{'Measure':ids['measures']['limit']})
        self.assertTrue(number['distribute_parent_value_to_children'])
        self.assertIn('limit',ids['dependencies']['rate'])
    def test_fractional_static_bound_is_rejected_in_composed_and_typed_factories(self):
        s=self.spec();s['measures'][1]['max_value']={'Static':Decimal('0.15')}
        with self.assertRaisesRegex(ValueError,'Static does not support decimal'):self.build(s)
        with self.assertRaisesRegex(ValueError,'Static does not support decimal'):
            input_create('123','Rate','Number',{'min_value':{'Static':Decimal('0.5')}},'')
    def test_explicit_distribution_override_survives(self):
        s=self.spec();s['measures'][1]['distribute']=False
        _,raw,_=self.build(s)
        r=next(v['columns'] for k,v in raw.items() if k.endswith('dataInput.json'))[1]
        self.assertFalse(r['columnMeta']['measure_type']['DataInput']['column_type']['Number']['distribute_parent_value_to_children'])
    def test_forecast_average_leaf_and_fractional_reference_bound(self):
        s={'actuals':'actual','start':'2026-01-01','end':'2026-12-31','timezone':'UTC','aggregation':'AverageLeaf',
           'referenceForecast':{'edit_config':{'number_column_metadata':{'distribute_parent_value_to_children':False}}}}
        c=forecast_config(s,{'actual':'123'},{'actual':'Native'},columns=['Date[Year]'])
        self.assertTrue(c['edit_config']['number_column_metadata']['distribute_parent_value_to_children'])
        s['referenceForecast']['edit_config']['number_column_metadata']['max_value']={'Static':Decimal('0.15')}
        with self.assertRaisesRegex(ValueError,'Static does not support decimal'):
            forecast_config(s,{'actual':'123'},{'actual':'Native'},columns=['Date[Year]'])
    def test_write_guard_rejects_bad_existing_input_payload(self):
        p=input_create('123','Rate','Number',{'min_value':{'Static':0},'max_value':{'Static':15}},'')
        p['columnMeta']['measure_type']['DataInput']['column_type']['Number']['max_value']={'Static':Decimal('0.15')}
        with self.assertRaisesRegex(ValueError,'Static does not support decimal'):
            guard_write('POST','/workspaces/w/plans/p/updateDefinition',pack({'sheets/s/visuals/v/dataInput.json':{'columns':[p]}}))

if __name__=='__main__':unittest.main()
