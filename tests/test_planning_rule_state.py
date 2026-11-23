import copy,unittest
from unittest.mock import patch
from runtime.planning_rule_state import append_record,authored_record
from runtime.rule_factories import measure_weighted_rule,verify_saved_rule

class PlanningRuleState(unittest.TestCase):
    def setUp(self):
        self.payload=measure_weighted_rule('901','Salary allocation',['salary'],'base',{'salary':'501','base':'502'},axis='Row',weights_period='CurrentYear')
        self.props={'visualType':80,'visualState':{'manage_measures':[{'id':'501'},{'id':'502'}],'data_input_rules':[],'unrelated':{'keep':True}}}
    def test_owner_state_preserved_and_no_borrowed_audit(self):
        before=copy.deepcopy(self.props);out=append_record(self.props,self.payload,'902')
        self.assertEqual(self.props,before);self.assertEqual(out['visualState']['unrelated'],before['visualState']['unrelated'])
        record=out['visualState']['data_input_rules'][0]
        self.assertEqual(verify_saved_rule(self.payload,[record])['persistedId'],'902')
        self.assertFalse(set(record)&{'created_by','created_at','updated_by','updated_at'})
        self.assertEqual(append_record(out,self.payload,'902'),out)
    def test_rejects_wrong_owner_or_unresolved_measure(self):
        for p in ({**self.props,'visualType':203},{'visualType':80,'visualState':{'manage_measures':[{'id':'501'}]}}):
            with self.assertRaises(ValueError):append_record(p,self.payload,'902')
    def test_existing_id_and_logical_id_are_not_interchangeable(self):
        p=append_record(self.props,self.payload,'902')
        with self.assertRaises(ValueError):append_record(p,self.payload,'901')

    def test_native_envelope_type_must_be_supplied(self):
        props=copy.deepcopy(self.props);del props['visualType']
        with self.assertRaises(ValueError):append_record(props,self.payload,'902')
        out=append_record(props,self.payload,'902',visual_type=80)
        self.assertNotIn('visualType',out)
        with self.assertRaises(ValueError):append_record(props,self.payload,'902',visual_type=203)

if __name__=='__main__':unittest.main()
