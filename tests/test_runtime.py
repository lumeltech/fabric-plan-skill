import unittest,copy,os,tempfile,socket,sys
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from runtime.codec import *
from runtime.identity import *
from runtime.construct import build,navigator,acyclic
from runtime.bridge import *
from runtime.surfaces import *
from runtime.layout import inventory,audit,find,placement_batch,verify_unchanged
from runtime.validate import validate_plan,Schemas,SchemaGap,Invalid,schema_report
from runtime.transport import Client,HttpError,plan_operation
def setUpModule():
    # Test suite is explicitly offline. HTTP adapter tests have no sockets.
    def deny(*a,**k): raise RuntimeError('Network forbidden in offline suite')
    socket.create_connection=deny
    socket.socket.connect=deny
def model(): return load(ROOT/'fixtures/model.json')
def finance(): return load(ROOT/'fixtures/finance-spec.json')
def built(): return build(model(),finance())
def page():
    def p(x,y,w,h): return {'position':{'x':x,'y':y},'dimension':{'width':w,'height':h},'unrelated':{'preserve':True}}
    return {'statusCode':200,'payload':{'etag':'page-etag','properties':{'properties':{'canvasStyle':{'dimension':{'width':600,'height':500,'elementScalingUnit':'pixel'}},
      'reactiveVisualProperties':[{'visualId':'linked','properties':p(20,230,560,240)}],'pageFilter':'keep'}},
      'visuals':[{'id':'nav','etag':'nav-etag','properties':{'properties':p(20,20,560,80)}},
                 {'id':'linked','isEmbedded':True,'properties':{'properties':p(0,0,400,600)}}]}}
def field_fixture(name,kind='dimensions'):
    return {'id':'field-'+name,'name':name,'alias':name,'type':'DOUBLE' if kind=='measures' else 'VARCHAR',
            'dataType':'NUMERIC' if kind=='measures' else 'TEXT_COLUMN', **({'measureGuid':'field-'+name,'columnType':'DI','isHierarchyColumn':False} if kind=='measures' else {})}
def cat(): return {'dimensions':[field_fixture('Region'),field_fixture('Employee'),field_fixture('Version')],
                  'columns':[field_fixture('Month','columns')],'measures':[field_fixture('Cost','measures')]}
def contribution(name='Workforce'):
    return Query(name,'source-'+name,cat()).load_planning().pivot(['Region','Version'],['Month'],{'Cost':'sum'}).result({'currency':'USD','sign':'expense-positive','period':'month','version':'explicit'})
class IdentityTests(unittest.TestCase):
    def test_upstream_272_vectors(self):
        for v in load(ROOT/'fixtures/xxh3-vectors.json'):
            data=v['text'].encode() if 'text' in v else bytes((i*137+19)%256 for i in range(v['length']))
            self.assertEqual(str(xxh3(data)),v['expected'],v.get('length',v.get('text')))
    def test_u64_reject_number(self):
        with self.assertRaises(ValueError): native_id(9007199254740993)
    def test_u64_extremes(self):
        self.assertEqual(native_id('18446744073709551615'),'18446744073709551615')
        for bad in ['18446744073709551616','01','-1','1e3']:
            with self.assertRaises(ValueError): native_id(bad)
    def test_preserve_registry_and_collisions(self):
        r=Registry(); a=r.custom('salary'); self.assertEqual(r.custom('salary'),a)
        with self.assertRaises(ValueError): r.bind('other',a)
    def test_semantic_prefix(self):
        r=Registry(); a=r.semantic('Metrics[Units]','Measure'); b=r.semantic('Metrics[Units]','Column','sum'); self.assertNotEqual(a,b)
class CodecTests(unittest.TestCase):
    def test_lossless_numbers_and_presence(self):
        text='{"long":18446744073709551615,"fraction":1.1234567890123456789,"empty":{},"null":null,"a":1,"A":2}'
        x=loads(text); self.assertEqual(loads(dumps(x)),x); self.assertEqual(x['fraction'],Decimal('1.1234567890123456789'))
    def test_duplicate_key_rejected(self):
        with self.assertRaises(ValueError): loads('{"a":1,"a":2}')
    def test_raw_bytes_preserved(self):
        env=pack({'one.json':{'a':1},'two.json':{'p':None}}); old=parts(env); new=patch(env,{'one.json':{'a':2}},{'one.json':sha(old['one.json'])})
        self.assertEqual(env['definition']['parts'][1],new['definition']['parts'][1]); self.assertEqual(unpack(new)['one.json']['a'],2)
    def test_drift_rejected(self):
        with self.assertRaises(ValueError): patch(pack({'one.json':{}}),{'one.json':{}},{'one.json':'wrong'})
    def test_paths_and_case_collisions(self):
        for p in ['../x','/x','a\\b','C:x','a/./b']:
            with self.assertRaises(ValueError): safe_path(p)
        with self.assertRaises(ValueError): pack({'A.json':{},'a.json':{}})
class ConstructionTests(unittest.TestCase):
    def test_finance_is_model_driven(self):
        b=built(); r=validate_plan(b['raw']); self.assertEqual(r['sheets'],4); self.assertEqual(r['measureRecords'],15)
        self.assertTrue(all('dataInput' not in p or b['raw'][p]['columns'] for p in b['raw']))
    def test_nonfinance_no_unrequested_features(self):
        b=build(model(),load(ROOT/'fixtures/capacity-spec.json')); self.assertEqual(len(b['identities']),1)
        self.assertNotIn('connectedPlanning/infobridge.json',b['raw']); self.assertNotIn('bookmarks',b['raw']['planProperties.json']['properties'])
    def test_unknown_model_field(self):
        s=finance(); s['sheets'][0]['rows'][0]='Imaginary[Field]'
        with self.assertRaises(ValueError): build(model(),s)
    def test_missing_model_url(self):
        m=model(); del m['reference']['url']
        with self.assertRaises(ValueError): build(m,finance())
    def test_measure_cycle(self):
        with self.assertRaises(ValueError): acyclic({'a':['b'],'b':['a']})
    def test_formula_placeholder_not_label_replacement(self):
        from runtime.construct import expression
        self.assertEqual(expression('${x} + IF(1 > 0, 2, 3)',{'x':'999'}),'M_999 + IF(1 > 0, 2, 3)')
        with self.assertRaises(ValueError): expression('${missing}',{'x':'999'})
    def test_missing_activation_detected(self):
        b=built(); k=next(k for k in b['raw'] if k.endswith('properties.json') and '/visuals/' in k)
        b['raw'][k]['properties']['visualState']['manage_measures'].pop()
        with self.assertRaises(ValueError): validate_plan(b['raw'])
    def test_missing_companion_detected(self):
        b=built(); k=next(k for k in b['raw'] if k.endswith('dataInput.json')); del b['raw'][k]
        with self.assertRaises(ValueError): validate_plan(b['raw'])
    def test_context_binding_not_boolean(self):
        b=built(); k=next(k for k in b['raw'] if k.endswith('dataInput.json')); col=next(c for c in b['raw'][k]['columns'] if 'DataInput' in c['columnMeta']['measure_type']); col['boundToFilterContext']=True
        with self.assertRaises(ValueError): validate_plan(b['raw'])
    def test_visual_column_input_context_binding_is_validated(self):
        spec=finance();spec['sheets'][0]['measures'][2]['visual_column']=True
        b=build(model(),spec);validate_plan(b['raw'])
        k=next(k for k in b['raw'] if k.endswith('dataInput.json')
            and any('VisualColumn' in c['columnMeta']['measure_type'] for c in b['raw'][k]['columns']))
        col=next(c for c in b['raw'][k]['columns'] if 'VisualColumn' in c['columnMeta']['measure_type'])
        col['columnMeta']['measure_type']['VisualColumn']['DataInput']['bound_to_filter_context']=False
        with self.assertRaises(ValueError):validate_plan(b['raw'])
    def test_tagged_input_measure_reference_is_resolved_within_owner(self):
        b=built();k=next(k for k in b['raw'] if k.endswith('dataInput.json'))
        col=next(c for c in b['raw'][k]['columns'] if 'DataInput' in c['columnMeta']['measure_type'])
        col['columnMeta']['measure_type']['DataInput']['column_type']['Number']['default_value']={'Measure':'999'}
        with self.assertRaises(ValueError):validate_plan(b['raw'])
    def test_native_public_conflicts_are_not_hidden(self):
        report=schema_report(built()['raw']); conflicts=[x for x in report if x['status']=='schema-conflict']
        self.assertEqual(len([x for x in conflicts if x['path'].endswith('dataInput.json')]),4)
        home=[x for x in conflicts if x['path']=='planProperties.json']
        self.assertEqual(len(conflicts),5);self.assertEqual(len(home),1)
        self.assertIn('homeLayout',home[0]['reason']) # Native object vs historical public string schema.
    def test_row_height_uses_native_owner(self):
        b=built(); k=next(k for k in b['raw'] if k.endswith('properties.json') and '/visuals/' in k)
        vs=b['raw'][k]['properties']['visualState']; self.assertNotIn('rowHeight',vs['globalStyles']); self.assertEqual(vs['row_height_config']['default_row_height'],26)
        self.assertEqual(vs['row_height_config']['custom_row_height']['16017913890930171270'],26)
        # The inspected format writer uses counters; new ordered entries retain them.
        self.assertEqual(vs['formatConfig']['formatSize'],sum(len(entries) for entries in vs['formatConfig']['measure'].values()))
        vs['row_height_config']['default_row_height']=26.5
        with self.assertRaises(ValueError):validate_plan(b['raw'])
    def test_measure_cannot_be_grouping_field(self):
        s=finance(); s['sheets'][0]['rows']=['Metrics[Expense]']
        with self.assertRaises(ValueError): build(model(),s)
    def test_readonly_source_formulas_omit_binding(self):
        b=built()
        for k,v in b['raw'].items():
            if k.endswith('dataInput.json'):
                for c in v['columns']:
                    if 'DataInput' not in c['columnMeta']['measure_type']: self.assertNotIn('boundToFilterContext',c)
    def test_context_boolean_is_not_coerced(self):
        s=finance(); s['sheets'][0]['measures'][2]['context_bound']='false'
        with self.assertRaises(ValueError): build(model(),s)
    def test_inverted_static_bounds(self):
        s=finance(); m=s['sheets'][0]['measures'][2]; m['min_value']={'Static':200}; m['max_value']={'Static':100}
        with self.assertRaises(ValueError): build(model(),s)
    def test_invalid_column_axis_aggregation(self):
        s=finance(); s['sheets'][0]['measures'][-1]['columnAggregation']='THIS_IS_NOT_AN_AGGREGATION'
        with self.assertRaises(ValueError): build(model(),s)
    def test_navigator_defaults_and_variants(self):
        for i in (1,2,3,4,5): self.assertIn('shapeState',navigator(i)['style']['DEFAULT'])
        with self.assertRaises(ValueError): navigator(6)
class BridgeTests(unittest.TestCase):
    def test_year_drift_rejected(self):
        with self.assertRaises(ValueError): Query('W','s',cat()).pivot(['Region','Year'],['Month'],{'Cost':'sum'})
    def test_wrong_axis_rejected(self):
        with self.assertRaises(ValueError): Query('W','s',cat()).pivot(['Region','Month'],[],{'Cost':'sum'})
    def test_remove_is_not_aggregation(self):
        a=Query('W','s',cat()).load_planning().remove(['Employee']).result({})
        with self.assertRaises(ValueError): append_check([a,a])
    def test_append_matching_and_context(self):
        a=contribution(); b=contribution('Other'); append_check([a,b]); b['semantics']['currency']='EUR'
        with self.assertRaises(ValueError): append_check([a,b])
    def test_append_dimension_mismatch(self):
        a=contribution(); b=contribution('Other'); b['meta']['selectedDimensions'][0]['alias']='RegionName'
        with self.assertRaises(ValueError): append_check([a,b])
    def test_typed_zero_requires_meaning(self):
        with self.assertRaises(ValueError): Query('W','s',cat()).add('Revenue','CAST(0.0 AS DOUBLE)','new')
    def test_empty_writeback_rejected(self):
        q=contribution(); q['writebackSettings']={}; s={'sourceGuid':q['sourceId'],'queries':[q]}
        with self.assertRaises(ValueError): validate_graph({'sources':[s]})
    def test_two_identity_domains(self):
        a=[{'sourceType':'InfoBridge','id':'old','sourceId':'field','queryId':'portable','bucketId':'ameasure','position':'preserve'}]
        mp={('portable','field'):{'queryId':'runtime','id':'tbl[field]'}}
        c=[{'sourceType':'InfoBridge','queryId':'runtime','id':'tbl[field]','sourceId':'native-field','tableId':'27'}]
        out=reconcile_assignments(a,mp,c); self.assertEqual(out[0]['queryId'],'runtime'); self.assertEqual(out[0]['tableId'],'27'); self.assertEqual(out[0]['position'],'preserve')
        with self.assertRaises(ValueError): reconcile_assignments(a,mp,[])
    def test_sql_rewrite_scoped(self):
        q={'meta':{'queries':['old'],'unrelated':'old'},'transformationSteps':[{'meta':{'value':{'sqlQuery':'SELECT * FROM {{query_id:old}}','caption':'old'}}}]}
        x=reconcile_execution(q,{'old':'new'}); self.assertIn('{{query_id:new}}',x['transformationSteps'][0]['meta']['value']['sqlQuery']); self.assertEqual(x['meta']['unrelated'],'old')
    def test_planning_selections_are_arrays(self):
        with self.assertRaises(ValueError): planning_source('W','v',cat(),True,[])
class SurfaceTests(unittest.TestCase):
    def test_home_roundtrip(self):
        x=home_item('header-image-text','Plan','Review assumptions'); y=home_item('preview-cards'); l=home_layout([x,y],[{'itemIds':[x['id']]},{'itemIds':[y['id']]}])
        self.assertEqual(loads(x['instanceState']['text']['title'])['root']['children'][0]['children'][0]['text'],'Plan'); self.assertEqual(len(l['rows']),2)
    def test_home_bad_rows(self):
        a=home_item('text','A')
        with self.assertRaises(ValueError): home_layout([a],[{'itemIds':['bad']}])
    def test_no_fake_asset(self):
        with self.assertRaises(ValueError): home_item('image',asset='blob:123')
    def test_bookmark_owner_and_slug(self):
        b=bookmark('Region','p','v',{'pivot':{'value':'synthetic'}}); self.assertEqual(b['bookmarkSlug'],b['cloudMeta']['bookmarkMeta']['bookmarkSlug']); self.assertEqual(b['bookmarkType'],20)
    def test_maintenance_three_gates(self):
        t={'physicalType':'U','primaryKey':['Key'],'columns':[{'name':'Key'}]}
        with self.assertRaises(ValueError): maintenance_eligible(t)
        self.assertTrue(maintenance_eligible(t,explicit=True))
    def test_column_reconciliation_preserves_omissions(self):
        c={'columnGuid':'key','columnName':'Key','columnType':6,'columnMeta':{},'displayName':'Key'}
        self.assertEqual(reconcile_column_configs([c],[]),[c])
class LayoutTests(unittest.TestCase):
    def test_owner_geometry_ignored_for_embed(self):
        p=page(); self.assertEqual(inventory(p)['visuals']['linked']['rectangle']['y'],230); self.assertEqual(audit(p,gap=16)['count'],2)
    def test_missing_and_duplicate_override(self):
        for mode in ('missing','duplicate'):
            p=page(); a=p['payload']['properties']['properties']['reactiveVisualProperties']; a.clear() if mode=='missing' else a.append(copy.deepcopy(a[0]))
            with self.assertRaises(ValueError): inventory(p)
    def test_no_fit_never_origin(self):
        self.assertIsNone(find({'width':100,'height':100},{'width':100,'height':100},[],margin=10))
    def test_empty_and_mixed_unit_rejected(self):
        p=page(); p['payload']['visuals']=[]
        with self.assertRaises(ValueError): inventory(p)
        p=page(); p['payload']['properties']['properties']['canvasStyle']['dimension']['elementScalingUnit']='points'
        with self.assertRaises(ValueError): inventory(p)
    def test_stale_and_source_preserved(self):
        p=page(); inv=inventory(p); r={'x':20,'y':200,'width':560,'height':270}
        with self.assertRaises(ValueError): placement_batch(p,'page','linked',r,'wrong')
        batch=placement_batch(p,'page','linked',r,inv['fingerprint']); self.assertEqual(batch['visuals'],{})
        after=copy.deepcopy(p); after['payload']['properties']=batch['workloadEntities']['page']; verify_unchanged(p,after,'linked',r,gap=16)
        after['payload']['visuals'][1]['properties']['properties']['position']['x']=99
        with self.assertRaises(ValueError): verify_unchanged(p,after,'linked',r)
    def test_overlap_and_bounds(self):
        p=page(); p['payload']['properties']['properties']['reactiveVisualProperties'][0]['properties']['position']['y']=50
        with self.assertRaises(ValueError): audit(p)
    def test_alignment_independent(self):
        p=page(); audit(p,alignment_groups=[{'ids':['nav','linked'],'axis':'x'}])
        with self.assertRaises(ValueError): audit(p,alignment_groups=[{'ids':['nav','linked'],'axis':'height'}])
class TransportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); os.environ['TEST_TOKEN']='mock-secret'; self.calls=[]
    def client(self,responses):
        def adapter(method,url,headers,body):
            self.calls.append((method,url,body)); item=responses.pop(0)
            if isinstance(item,Exception): raise item
            return item
        return Client('https://api.fabric.microsoft.com/v1','TEST_TOKEN',journal=self.tmp.name,adapter=adapter,sleep=lambda t:None)
    def test_202_location_then_result(self):
        c=self.client([{'status':202,'headers':{'Location':'https://api.fabric.microsoft.com/v1/operations/op','Retry-After':'0'},'body':None},
          {'status':200,'headers':{},'body':{'status':'Running'}},{'status':200,'headers':{},'body':{'status':'Succeeded'}},{'status':200,'headers':{},'body':{'definition':{'parts':[]}}}])
        r=c.finish(c.request('POST','/workspaces/w/plans/p/getDefinition',{},label='export'),'export'); self.assertIn('definition',r['body']); self.assertTrue(self.calls[-1][1].endswith('/result'))
    def test_read_throttle(self):
        c=self.client([{'status':429,'headers':{'retry-after':'0'},'body':{}},{'status':200,'headers':{},'body':{'value':1}}]); self.assertEqual(c.request('GET','/x')['status'],200)
    def test_uncertain_create_not_repeated(self):
        c=self.client([TimeoutError()])
        with self.assertRaises(RuntimeError): c.request('POST','/plans',{},label='create')
        with self.assertRaisesRegex(RuntimeError,'UNCERTAIN'): c.request('POST','/plans',{},label='create')
        self.assertEqual(len(self.calls),1)
    def test_rejected_write_not_success(self):
        c=self.client([{'status':403,'headers':{},'body':{}}])
        for _ in range(2):
            with self.assertRaises(HttpError): c.request('POST','/plans',{},label='create')
        self.assertEqual(len(self.calls),1)
    def test_untrusted_location(self):
        c=self.client([])
        with self.assertRaises(ValueError): c.finish({'status':202,'headers':{'location':'https://evil.invalid/steal'},'body':None},'a')
    def test_config_cannot_expand_public_origin(self):
        allowed=['api.fabric.microsoft.com','extra.invalid']
        with self.assertRaises(ValueError):
            Client('https://extra.invalid/v1','TEST_TOKEN',allowed,self.tmp.name)
        c=Client('https://api.fabric.microsoft.com/v1','TEST_TOKEN',allowed,self.tmp.name,
                 adapter=lambda *args:self.fail('Credential sent outside Fabric'))
        with self.assertRaises(ValueError):
            c.request('GET','https://extra.invalid/next')
    def test_update_rechecks_changed_destination_without_submitting(self):
        from runtime.codec import pack,definition_hash
        from runtime.transport import plan_operation
        before=pack({'example.json':{'value':1}})
        changed=pack({'example.json':{'value':2}})
        c=self.client([{'status':200,'headers':{},'body':changed}])
        with self.assertRaisesRegex(ValueError,'Destination changed'):
            plan_operation(c,'w','update','p',definition=before,baseline_hash=definition_hash(before))
        self.assertEqual([url.rsplit('/',1)[-1] for _,url,_ in self.calls],['getDefinition'])
    def test_credentials_not_journaled(self):
        c=self.client([{'status':201,'headers':{},'body':{'id':'new'}}]); c.request('POST','/plans',{},label='create')
        self.assertTrue(all('mock-secret' not in f.read_text() for f in Path(self.tmp.name).glob('*')))
    def test_completed_create_resume(self):
        c=self.client([{'status':201,'headers':{},'body':{'id':'new'}}]); first=c.request('POST','/plans',{},label='create'); self.assertEqual(c.request('POST','/plans',{},label='create'),first); self.assertEqual(len(self.calls),1)
    def test_child_workload_token_not_persisted(self):
        c=self.client([{'status':200,'headers':{},'body':{'Token':'child-workload-secret','TargetUriHost':'example.invalid'}}])
        r=c.request('POST','/token',{},label='token'); self.assertEqual(r['body']['Token'],'child-workload-secret')
        self.assertTrue(all('child-workload-secret' not in f.read_text() for f in Path(self.tmp.name).glob('*')))
        with self.assertRaises(RuntimeError): c.request('POST','/token',{},label='token')
class SchemaTests(unittest.TestCase):
    def test_transitive_closure(self):
        s=Schemas()
        def walk(x,url):
            if isinstance(x,dict):
                if '$ref' in x:
                    import urllib.parse
                    u,frag=urllib.parse.urldefrag(urllib.parse.urljoin(url,x['$ref'])); self.assertIn(u,s.docs); pointer_get(s.docs[u],frag)
                for v in x.values(): walk(v,url)
            elif isinstance(x,list):
                for v in x: walk(v,url)
        for u,d in s.docs.items(): walk(d,u)
    def test_unknown_keywords_fail_closed(self):
        s=Schemas()
        with self.assertRaises(SchemaGap): s._check({}, {'inventedValidation':True},'https://example.invalid','$')
    def test_object_enum_equality_ignores_key_order(self):
        s=Schemas(); s._check({'a':1,'b':2},{'const':{'b':2,'a':1}},'https://example.invalid','$')
        with self.assertRaises(Invalid): s._check(True,{'const':1},'https://example.invalid','$')
if __name__=='__main__': unittest.main()
