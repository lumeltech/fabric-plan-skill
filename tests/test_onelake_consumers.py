import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,unittest
from pathlib import Path
from runtime.codec import load
from runtime.consumer_bindings import output_catalog,numeric_output_fields,resolve_assignment,assert_resolved,binding_query_id
from runtime.bridge_operations import execution_map
from runtime.identity import Registry
from runtime.linked_values import value_assignment
from runtime.planning_presentation import build_application
ROOT=Path(__file__).resolve().parents[1]

class OneLakeConsumers(unittest.TestCase):
    def query(self,qid='Qfresh'):
        return {'id':qid,'sourceId':'current-source','name':'Saved Plan Outputs','meta':{'selectedMeasures':[{'id':'18446744073709551614','name':'PlanPay','type':'DOUBLE'}]}}
    def test_sql_and_onelake_are_distinct_lossless_domains(self):
        q=self.query();self.assertEqual(output_catalog(q)[0]['id'],'Qfresh[18446744073709551614]')
        q['sqlPk']='19';self.assertEqual(output_catalog(q)[0]['id'],'19[18446744073709551614]')
        q['sqlPk']=None;self.assertEqual(execution_map([q]),{'Qfresh':'Qfresh'})
    def test_explicit_malformed_sql_id_does_not_silently_switch_profile(self):
        for value in ('',False,'Qfake',3.5):
            q={**self.query(),'sqlPk':value}
            with self.assertRaises(ValueError):binding_query_id(q)
    def test_current_output_identity_required_and_empty_selection_respected(self):
        q=self.query();f=numeric_output_fields(q)[0];a=value_assignment({'fields':[]},f['id'],Registry(),query_fields=[f])
        self.assertEqual(assert_resolved(a,q)['binding'],'matched-current-query-output')
        bad=copy.deepcopy(a);bad['queryId']='Qanother'
        with self.assertRaises(ValueError):assert_resolved(bad,q)
        q['meta']['selectedMeasures']=[];self.assertEqual(output_catalog(q),[])
    def test_generated_application_has_linked_grid_cards_and_comparison_chart(self):
        from runtime.storage_context import query_contract
        model=load(ROOT/'assets/fixtures/model.json');q=self.query()
        proof=query_contract(q,[{'rows':['Region[Region]'],'columns':['Period[Month]'],'context':[]}],{})
        fields=numeric_output_fields(q,storage_context=proof)
        field=fields[0]['id']
        spec={'name':'Synthetic OneLake Test','queryFields':fields,'sheets':[{'name':'Pay','rows':['Region[Region]'],'columns':['Period[Month]'],'measures':[{'key':'pay','label':'Plan Pay','kind':'Native','source':field},{'key':'double','label':'Double Pay','kind':'Formula','formula':'${pay} * 2'}]}],
            'dashboards':[{'name':'Pay Review','owner':'Pay','slicers':[{'field':'Region[Region]'}],'cards':[{'field':field,'label':'Plan Pay','aggregation':'sum'}],'charts':[{'category':'Period[Month]','field':field,'label':'Plan Pay trend','aggregation':'sum'}]}]}
        b=build_application(model,spec);self.assertEqual(b['defaultsCheck']['hiddenPlanningOwners'],1)
        linked=[]
        for v in b['raw'].values():linked.extend(a for a in v.get('properties',{}).get('pivotAssignments',[]) if a.get('sourceType')=='InfoBridge')
        self.assertEqual(len(linked),3)
        for a in linked:self.assertEqual(a['queryId'],'Qfresh');assert_resolved(a,self.query())

    def test_context_key_can_be_native_helper_without_becoming_axis_descriptor(self):
        from runtime.construct import planning,field
        model=load(ROOT/'assets/fixtures/model.json')
        model['fields'].append({'id':'Version[Key]','tableName':'Version','columnName':'Key','columnType':'Column','dataType':'Int64'})
        spec={'name':'Context key','rows':['Region[Region]'],'columns':['Period[Month]'],
            'context':[{'field':'Version[Version]','values':['Budget']}],
            'lookupContextAssignments':[field(model,'Version[Version]','rows',1)],
            'dimensionIdMappings':{'Version[Version]':{'ID':'Version[Key]'}},
            'measures':[{'key':'key','label':'Key helper','kind':'Native','source':'Version[Key]','sourceAggregation':'sum','visible':False}]}
        d,raw,i=planning(model,spec,Registry());p=raw[f'sheets/{i["sheetId"]}/visuals/{i["visualId"]}/properties.json']['properties']
        self.assertEqual(next(a for a in p['pivotAssignments'] if a['id']=='Version[Key]')['bucketId'],'ameasure')
        desc=next(a for a in p['visualState']['dimension_id_mapping']['pivot'] if a['id']=='Version[Key]')
        self.assertNotEqual(desc['bucket_type'],'ameasure')

if __name__=='__main__':unittest.main()
