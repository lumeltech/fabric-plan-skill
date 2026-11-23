"""OneLake and SQL routing through the public constructors and recipe phases."""
import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from runtime.codec import load
from runtime.consumer_bindings import binding_query_id,find_query,assert_resolved,numeric_output_fields
from runtime.forecast_review import from_sheet_assignment
from runtime.measure_bindings import sheet_column_id,resolve_measure,registered_measure
from runtime.identity import Registry,xxh3
from runtime.linked_values import value_assignment
from runtime.bridge_identity import rebind_planning_outputs

ROOT=Path(__file__).resolve().parents[1]

class OneLakeSheetBindings(unittest.TestCase):
    def setUp(self):
        self.fixture=load(ROOT/'fixtures/onelake-linked-values.json')
        self.record=self.fixture['sourceRecord'];self.query=self.fixture['query']
        self.props={'pivotAssignments':[],'visualState':{'manage_measures':[{'id':self.record['measureGuid']}],
            'rowDimensions':[],'columnDimensions':[]}}
        self.owner={'visualId':'1','name':'Planning 1','columns':[self.record],'properties':self.props}
    def request(self):
        return {'sourceType':'Visual','visualId':'1','sourceMeasureGuid':self.record['measureGuid']}
    def companion(self,a):
        return {'measureGuid':a['measureGuid'],'name':a.get('customName',a['name']),
            'columnMeta':{'id':a['measureGuid'],'data_type':'Number','measure_type':{'Native':{'measure_role':'ACMeasure'}}}}
    def test_captured_onelake_direct_binding_matches_saved_identity(self):
        before=copy.deepcopy(self.record)
        a=from_sheet_assignment(self.record,'1','Planning 1')
        saved=self.fixture['nativeAssignments']['Visual']
        for k in ('id','sourceId','sourceType','visualId','measureGuid','aggregationType'):
            self.assertEqual(a[k],saved[k],k)
        self.assertGreater(int(a['id']),2**53);self.assertEqual(self.record,before)
        self.assertNotIn('id',self.record);self.assertNotIn('visualId',self.record)
        alm=self.fixture['exportAssignments']['Visual']
        self.assertNotEqual(alm['visualId'],a['visualId'])
        self.assertEqual(alm['id'],a['id'])
        with self.assertRaises(ValueError):from_sheet_assignment(self.record,alm['visualId'],'Planning 1')
    def test_sql_record_id_is_not_replaced_with_measure_guid(self):
        c={**self.record,'id':17,'visualId':1}
        a=from_sheet_assignment(c,'1','Planning 1')
        self.assertEqual(a['id'],'17');self.assertEqual(a['measureGuid'],str(xxh3('SUM__17')))
        c['id']=None;self.assertEqual(sheet_column_id(c),c['measureGuid'])
    def test_malformed_or_conflicting_id_is_never_silently_replaced(self):
        for value in ('',False,1.25,'label','01',str(2**64)):
            with self.subTest(value=value),self.assertRaises(ValueError):sheet_column_id({**self.record,'id':value})
        bad=copy.deepcopy(self.record);bad['columnMeta']['id']='34'
        with self.assertRaises(ValueError):sheet_column_id(bad)
        with self.assertRaises(ValueError):from_sheet_assignment({**self.record,'visualId':'2'},'1','Planning 1')
    def test_all_local_output_kinds_resolve_without_sql_id(self):
        for kind in ('DataInput','Forecast','Formula'):
            for wrapped in (False,True):
                self.record['columnMeta']['measure_type']={'VisualColumn':{kind:{}}} if wrapped else {kind:{}}
                a=resolve_measure(self.request(),sheets=[self.owner])
                self.assertEqual(a['id'],self.record['measureGuid'])
                self.assertEqual(registered_measure(self.props,self.record,'1','Planning 1',model={}),a)
    def test_source_scope_registration_and_ambiguity_are_checked(self):
        for mode in ('wrong-guid','wrong-visual','duplicate','unregistered'):
            owner=copy.deepcopy(self.owner);req=self.request()
            if mode=='wrong-guid':req.update(columnId=self.record['measureGuid'],sourceMeasureGuid='123')
            elif mode=='wrong-visual':owner['columns'][0]['visualId']='2'
            elif mode=='duplicate':owner['columns'].append(copy.deepcopy(self.record))
            else:owner['properties']['visualState']['manage_measures']=[]
            with self.subTest(mode=mode),self.assertRaises(ValueError):resolve_measure(req,sheets=[owner])
    def test_native_direct_companion_relays_original_owner(self):
        a=resolve_measure(self.request(),sheets=[self.owner]);c=self.companion(a)
        props={'pivotAssignments':[a]}
        with self.assertRaises(ValueError):from_sheet_assignment(c,'2','Consumer')
        out=registered_measure(props,c,'2','Consumer',model={},sheets=[self.owner])
        self.assertEqual(out['id'],self.record['measureGuid']);self.assertEqual(out['visualId'],'1')
    def test_captured_query_shape_passes_all_resolver_entrypoints(self):
        a=self.fixture['nativeAssignments']['InfoBridge'];q=self.query
        self.assertNotIn('sqlPk',q);assert_resolved(a,q)
        output_id=a['id'].split('[',1)[1][:-1]
        out=resolve_measure({'sourceType':'InfoBridge','queryId':q['id'],'outputId':output_id,'assignment':a},queries=[q])
        self.assertEqual(out['id'],a['id']);self.assertEqual(out['measureGuid'],a['measureGuid'])
        r=registered_measure({'pivotAssignments':[a]},self.companion(a),'2','Consumer',model={},queries=[q])
        self.assertEqual(r['queryId'],q['id'])
    def test_opaque_and_sql_query_ids_use_same_source_aware_path(self):
        for qid,pk in [('Qnew',None),('new-opaque-uuid',None),('new-guid',19)]:
            q=copy.deepcopy(self.query);q.update(id=qid,sqlPk=pk)
            f=numeric_output_fields(q)[0]
            a=value_assignment({'fields':[]},f['id'],Registry(),query_fields=[f])
            out=resolve_measure({'sourceType':'InfoBridge','queryId':qid,'outputId':f['outputId'],'assignment':a},queries=[q])
            self.assertEqual(out['queryId'],str(pk) if pk else qid)
            self.assertIs(find_query([q],binding_query_id(q)),q)
    def test_query_ambiguity_source_ids_and_malformed_sql_keys_rejected(self):
        for queries,key in [([self.query],self.query['sourceId']),([self.query,self.query],self.query['id']),
                            ([{**self.query,'sqlPk':'not-a-pk'}],self.query['id'])]:
            with self.assertRaises(ValueError):find_query(queries,key)
    def test_existing_query_companion_keeps_registered_alias(self):
        a=copy.deepcopy(self.fixture['nativeAssignments']['InfoBridge']);a['measureGuid']='15000000000000000001'
        out=registered_measure({'pivotAssignments':[a]},self.companion(a),'2','Consumer',model={},queries=[self.query])
        self.assertEqual(out['measureGuid'],a['measureGuid']);assert_resolved(out,self.query,check_measure_guid=False)
    def test_onelake_rebind_preserves_formulas_and_aliases(self):
        a=copy.deepcopy(self.fixture['nativeAssignments']['InfoBridge']);a['measureGuid']='15000000000000000001'
        q=copy.deepcopy(self.query);fid=a['id'].split('[',1)[1][:-1]
        q['meta']['selectedMeasures']=[f for f in q['meta']['selectedMeasures'] if f['id']==fid]
        next(f for f in q['meta']['selectedMeasures'] if f['id']==fid)['measureGuid']=self.record['measureGuid']
        props={'pivotAssignments':[a],'visualState':{'formula':'["15000000000000000001"] * 2'}}
        result=rebind_planning_outputs(props,[self.companion(a)],
            [{'measure_guid':a['measureGuid'],'query_guid':q['id'],'source_measure_guid':self.record['measureGuid']}],{q['id']:q})
        self.assertEqual(result['properties'],props)
    def test_example_runs_outside_workspace_with_new_ids_each_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            ids=[]
            for run in ('first','second'):
                out=Path(tmp)/run
                r=subprocess.run([sys.executable,str(ROOT/'examples/onelake-linked-values/build.py'),str(out)],cwd=tmp,capture_output=True,text=True)
                self.assertEqual(r.returncode,0,r.stderr)
                b=load(out/'construction.json');ids.append(b['identities'][0]['visualId'])
                self.assertEqual(b['defaultsCheck']['hiddenPlanningOwners'],2)
                evidence=load(out/'bindings.json')
                self.assertEqual(evidence['direct']['id'],evidence['sourceRecord']['measureGuid'])
                self.assertEqual(evidence['query']['queryId'],evidence['queryMetadata']['id'])
                self.assertEqual(evidence['runtime'],'not-tested')
            self.assertNotEqual(*ids)

if __name__=='__main__':unittest.main()
