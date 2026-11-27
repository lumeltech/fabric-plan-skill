"""Regression: large portable IDs must not leak into native source selector slots."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from runtime.codec import load,pack
from runtime.bridge import Query,planning_source,portable
from runtime.bridge_identity import planning_catalog,check_planning_graph,resolve_planning_output,rebind_planning_outputs
from runtime.bridge_operations import editable_source
from runtime.connected_components import bridge_consumer
from runtime.planning_integrity import guard_write,check_properties,default_global_styles

ROOT=Path(__file__).resolve().parents[1]
EXAMPLE=ROOT/'assets/examples/infobridge-lineage'

class PlanningLineageTests(unittest.TestCase):
    def request(self):return load(EXAMPLE/'planning-source.request.json')
    def graph(self):
        r=self.request();s=planning_source(**r)
        q=Query('Revenue',s['sourceGuid'],s['meta']).load_planning().pivot(['Region'],['Month'],{'Revenue Plan':'sum'})
        s['queries']=[q.record];return portable([s],[])
    def test_owner_types_and_u64_strings_survive_every_stage(self):
        r=self.request();original=copy.deepcopy(r);g=self.graph();s=g['sources'][0]
        byname={f['name']:f for f in s['meta']['measures']}
        self.assertEqual(byname['Unit Forecast']['columnType'],'DI')
        self.assertEqual(byname['Revenue Plan']['columnType'],'FORMULA')
        self.assertGreater(int(byname['Unit Forecast']['measureGuid']),2**63-1)
        q=s['queries'][0];pivot=q['transformationSteps'][1]['meta']['value']
        for f in [*s['meta']['measures'],*s['meta']['selectedMeasures'],*s['meta']['includeMeasures'],*q['meta']['measures'],*q['meta']['selectedMeasures'],*pivot['sourceMeasures'],*pivot['removeColumns']]:
            if f.get('name') not in byname:continue
            expected=byname[f['name']]
            self.assertEqual((f['id'],f['measureGuid'],f['columnType'],f['isHierarchyColumn']),(expected['id'],expected['id'],expected['columnType'],False))
        self.assertEqual(r,original)
    def test_input_and_native_owners_are_di(self):
        r=self.request()
        for kind in ('DataInput','Native'):
            r['owner_columns'][0]['columnMeta']['measure_type']={kind:{}}
            self.assertEqual(planning_source(**r)['meta']['measures'][0]['columnType'],'DI')
    def test_raw_catalog_cannot_silently_omit_lineage(self):
        r=self.request()
        with self.assertRaisesRegex(ValueError,'measureGuid'):Query('x','s',r['catalog'])
        r.pop('owner_columns')
        with self.assertRaises(ValueError):planning_source(**r)
    def test_name_only_owner_match_conflicts_and_numeric_ids_rejected(self):
        for mutation in ('wrong-id','name','kind','guid','type','number','hierarchy','duplicate'):
            r=self.request();f=r['catalog']['measures'][0]
            if mutation=='wrong-id':f['id']='wrong-id'
            elif mutation=='name':f['name']='Different owner'
            elif mutation=='kind':r['owner_columns'][0]['columnMeta']['measure_type']={'Unknown':{}}
            elif mutation=='guid':f['measureGuid']='unrelated'
            elif mutation=='type':f['columnType']='FORMULA'
            elif mutation=='number':f['id']=int(f['id'])
            elif mutation=='hierarchy':f['isHierarchyColumn']=True
            else:r['owner_columns'].append(copy.deepcopy(r['owner_columns'][0]))
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):planning_source(**r)
    def test_native_domain_is_explicit_and_keeps_guid_separate(self):
        r=self.request()
        for f,c in zip(r['catalog']['measures'],r['owner_columns']):f['id']=str(c['id'])
        with self.assertRaises(ValueError):planning_catalog(r['catalog'],r['owner_columns'])
        out=planning_catalog(r['catalog'],r['owner_columns'],identity_mode='native')
        self.assertEqual(out['measures'][0]['id'],'31')
        self.assertEqual(out['measures'][0]['measureGuid'],r['owner_columns'][0]['measureGuid'])
    def test_query_derivatives_do_not_receive_owner_type(self):
        r=self.request();s=planning_source(**r)
        q=Query('x',s['sourceGuid'],s['meta']).load_planning().add('Ratio','"Revenue Plan"/"Unit Forecast"','derived-ratio',requires=['Revenue Plan','Unit Forecast'])
        self.assertNotIn('measureGuid',q.fields()['Ratio'][1]);self.assertNotIn('columnType',q.fields()['Ratio'][1])
        q.rename('Revenue Plan','Renamed Revenue','derived-rename')
        rename=q.record['transformationSteps'][-1]['meta']['value']
        self.assertEqual(rename['sourceColumn']['columnType'],'FORMULA')
        self.assertNotIn('measureGuid',q.fields()['Renamed Revenue'][1])
        s['queries']=[q.record];portable([s],[])
    def test_prewrite_guard_rejects_bad_transform_before_network(self):
        g=self.graph();g['sources'][0]['queries'][0]['transformationSteps'][1]['meta']['value']['sourceMeasures'][0].pop('measureGuid')
        with self.assertRaisesRegex(ValueError,'measureGuid'):
            guard_write('POST','/v1/workspaces/w/plans/p/updateDefinition',pack({'connectedPlanning/infobridge.json':g}))
    def test_powertable_does_not_get_planning_metadata(self):
        r=self.request();s=editable_source('Lookup','v',r['catalog'],destination_id='d',mde_source_id='m',table_name='Rates')
        self.assertNotIn('measureGuid',s['meta']['measures'][0]);check_planning_graph({'sources':[s]})
    def test_current_query_lineage_resolves_output_and_preserves_internal_alias(self):
        r=load(EXAMPLE/'resolve-output.request.json');f=resolve_planning_output(**r)
        self.assertEqual(f['id'],'77[12]');self.assertEqual(f['queryId'],'77');self.assertEqual(f['columnType'],'Column')
        bundle=bridge_consumer(f,'new-visual','15000000000000000001','Review Revenue')
        self.assertEqual(bundle['assignment']['measureGuid'],'15000000000000000001')
        self.assertEqual(bundle['dataInputColumn']['measureGuid'],'15000000000000000001')
        for mode in ('missing','duplicate','empty','wrong-label'):
            test=copy.deepcopy(r);fields=test['query']['meta']['selectedMeasures']
            if mode=='missing':fields[0].pop('measureGuid')
            elif mode=='duplicate':fields.append(copy.deepcopy(fields[0]))
            elif mode=='empty':test['query']['meta']['selectedMeasures']=[]
            else:test['expected_name']='Wrong label'
            with self.subTest(mode=mode),self.assertRaises(ValueError):resolve_planning_output(**test)
    def test_query_sort_uses_output_caption_not_opaque_id(self):
        f=resolve_planning_output(**load(EXAMPLE/'resolve-output.request.json'))
        a=bridge_consumer(f,'v','12','Revenue')['assignment']
        p={'pivotAssignments':[a],'visualState':{'globalStyles':default_global_styles()},'superFilterAssignments':[{'pivotAssignments':[a],'configuration':{'sort':[{'columnId':'77[12]','queryId':'77','columnName':'Revenue Plan'}]}}]}
        check_properties(p)
        p['superFilterAssignments'][0]['configuration']['sort'][0]['columnName']='Wrong'
        with self.assertRaisesRegex(ValueError,'Query sort descriptor'):check_properties(p)
    def test_package_only_example_runs_from_unrelated_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=subprocess.run([sys.executable,str(EXAMPLE/'build.py'),tmp],cwd=tmp,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            graph=load(Path(tmp)/'infobridge.json');self.assertEqual(len(graph['sources']),1)
            self.assertEqual(load(Path(tmp)/'resolved-field.json')['id'],'77[12]')

    def test_rebind_preserves_formulas_storage_internal_id_and_filter_scope(self):
        r=load(EXAMPLE/'resolve-output.request.json');q=r['query'];mid='15000000000000000001'
        a=bridge_consumer(resolve_planning_output(**r),'v',mid,'Review Revenue')['assignment']
        a.update(id=q['id']+'[portable]',sourceId=q['id']+'[portable]',queryId=q['id'])
        props={'pivotAssignments':[a],'visualState':{'formula':'["'+mid+'"] * 2','storage':{'stableKey':mid},'other':'retain'},'superFilterAssignments':[{'filter':[],'pivotAssignments':[copy.deepcopy(a)],'configuration':{'sort':[{'id':a['id'],'columnId':a['id'],'columnName':a['columnName'],'queryId':a['queryId']}]}}]}
        cols=[{'measureGuid':mid,'columnMeta':{'measure_type':{'Native':{}}}}]
        request={'properties':props,'owner_columns':cols,'queries':{q['id']:q},'bindings':[{'measure_guid':mid,'query_guid':q['id'],'source_measure_guid':r['expected_measure_guid']}]}
        before=copy.deepcopy(request);out=rebind_planning_outputs(**request)['properties']
        self.assertEqual(request,before);self.assertEqual(out['visualState'],props['visualState'])
        self.assertEqual(out['pivotAssignments'][0]['id'],'77[12]');self.assertEqual(out['pivotAssignments'][0]['measureGuid'],mid)
        self.assertEqual(out['pivotAssignments'][0]['name'],'Review Revenue')
        self.assertEqual(out['superFilterAssignments'][0]['filter'],[])
        self.assertEqual(out['superFilterAssignments'][0]['configuration']['sort'][0]['columnId'],'77[12]')
        cols[0]['columnMeta']['measure_type']={'Formula':{}}
        with self.assertRaises(ValueError):rebind_planning_outputs(**request)

if __name__=='__main__':unittest.main()
