import unittest,copy,json,sys
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime.construct import build
from runtime.identity import Registry
from runtime.filters import selection,forward_filters,audit_context,prepare_context
from runtime.intelligence import slicer,card,rectangles
from runtime.intelligence_api import visibility
from runtime.readback import verify_authored
from runtime.codec import pack,unpack,parts
from runtime.scope import prepare_scope
from runtime.workflow import SUPPORTED,preflight
from runtime.validate import validate_plan,schema_report
from runtime.layout import overlap

def example(prefix='Workforce'):
    def f(t,c,typ='String',kind='Column'):
        return {'id':t+'['+c+']','tableName':t,'columnName':c,'columnType':kind,'dataType':typ}
    m={'reference':{'connectionId':'10000000-0000-4000-8000-000000000001','semanticModelId':'10000000-0000-4000-8000-000000000002',
       'semanticModelName':'Synthetic','semanticModelWorkspaceId':'10000000-0000-4000-8000-000000000003','semanticModelWorkspaceName':'Offline',
       'directLakeMode':False,'directQueryMode':False,'sourceType':'WORKLOAD','url':'https://example.invalid/current-model'},
       'fields':[f(prefix,'Name'),f(prefix,'Key','Int64'),f(prefix,'Group'),f('Time','Year','Int64'),f('Time','Month'),
                 f('Version','Name'),f('Version','Key','Int64'),f('Geography','Area'),f('Facts','Amount','Double'),f('Facts','Total','Double','Measure')]}
    s={'name':prefix+' plan','requiredCapabilities':['planning.numeric','planning.filter-context','intelligence.slicers','intelligence.cards','intelligence.embeds'],
       'sheets':[{'name':prefix+' inputs','rows':['Geography[Area]',prefix+'[Name]'],'columns':['Time[Month]'],
         'context':[{'field':'Version[Name]','values':['Proposal']}],
         'dimensionIdMappings':{prefix+'[Name]':{'ID':prefix+'[Key]'},'Version[Name]':{'ID':'Version[Key]'}},
         'measures':[{'key':'input','kind':'DataInput','label':'Planned amount','default_value':{'Static':10}}]}],
       'dashboards':[{'name':prefix+' workspace','owner':prefix+' inputs','title':'Plan the next period','description':'Review scope and edit the plan.',
         'slicers':[{'field':'Time[Year]','label':'Planning year','between':[2030,2031],'required':True},
                    {'field':'Geography[Area]','label':'Area','values':['West'],'singleSelect':True,'required':True},
                    {'field':prefix+'[Group]','label':'Group'},{'field':prefix+'[Name]','label':'Detail'}],
         'cards':[{'field':'Facts[Total]','label':'Current total'},{'field':'Facts[Amount]','aggregation':'sum','label':'Total amount'},
                  {'field':'Facts[Amount]','aggregation':'max','label':'Highest amount'}]}]}
    return m,s

def owner_parts(b):
    i=b['identities'][0];base=f'sheets/{i["sheetId"]}/visuals/{i["visualId"]}/'
    return b['raw'][base+'properties.json']['properties'],b['raw'][base+'dataInput.json']['columns']

class ContextConstruction(unittest.TestCase):
    def test_null_pivot_axes_and_decimal_filter_values(self):
        m,s=example();sheet=s['sheets'][0];sheet['pivots']=[{'rows':None,'columns':None}]
        self.assertEqual(len(prepare_context(m,sheet)[1]),1)
        f=selection(m,'Facts[Amount]',between=[Decimal('1.25'),Decimal('3.75')])
        self.assertEqual(f[0]['rangeFilter'][0]['from'],Decimal('1.25'))
    def test_context_remains_external_and_inputs_bound_in_two_businesses(self):
        for name in ['Workforce','Warehouse']:
            m,s=example(name);b=build(m,s);p,records=owner_parts(b);audit_context(p,records)
            self.assertNotIn('Version[Name]',[a['id'] for a in p['pivotAssignments']])
            self.assertEqual([a['id'] for a in p['visualState']['dimension_id_mapping']['pivot'] if a['id'].startswith('Version[')],['Version[Name]','Version[Key]'])
            self.assertEqual(records[0]['boundToFilterContext'],10)
            self.assertNotIn('filterContextHashMap',p['visualState'])
            reg=p['superFilterAssignments'][0]
            self.assertEqual(reg['pivotAssignments'][0]['bucketId'],'Category')
            self.assertEqual(reg['filter'][0]['valuesFilter'][0]['id'],['Proposal'])
            self.assertEqual(validate_plan(b['raw'])['sheets'],2)
    def test_invalid_context_is_not_silently_moved_or_unbound(self):
        for mutate in [lambda x:x['rows'].append('Version[Name]'),lambda x:x['measures'][0].update(context_bound=False),
                       lambda x:x['context'].append(copy.deepcopy(x['context'][0])),lambda x:x['context'][0].update(values=[]),
                       lambda x:x['context'][0].update(values=['A','B']),lambda x:x.update(filterContextSettings={'filterContextStatus':False})]:
            m,s=example();mutate(s['sheets'][0])
            with self.assertRaises(ValueError):build(m,s)
    def test_mirror_and_binding_corruption_detected(self):
        m,s=example();b=build(m,s);p,r=owner_parts(b)
        p['visualState']['embeddedSuperFilter']['superFilterAssignments']=[]
        with self.assertRaises(ValueError):audit_context(p,r)
    def test_range_has_no_stale_values_and_type_checks(self):
        m,s=example();p=slicer(m,s['dashboards'][0]['slicers'][0]);d=p['visualState']['slicerFilterAssignments']
        self.assertEqual(len(d),1);self.assertEqual(d[0]['filterType'],'RANGE');self.assertNotIn('valuesFilter',d[0])
        for kwargs in [{'values':['2030']},{'between':[2031,2030]},{'between':[True,2030]},{'values':[2030],'between':[2030,2031]}]:
            with self.assertRaises(ValueError):selection(m,'Time[Year]',**kwargs)
    def test_forwarding_preserves_context(self):
        m,s=example();p,_=owner_parts(build(m,s));before=copy.deepcopy(p['superFilterAssignments'])
        forward_filters(p,selection(m,'Geography[Area]',values=['West']));self.assertEqual(p['superFilterAssignments'],before)
        self.assertIn(before[0],p['visualState']['embeddedSuperFilter']['superFilterAssignments'])
        with self.assertRaises(ValueError):forward_filters(p,selection(m,'Version[Name]',values=['Other']))

class DashboardConstruction(unittest.TestCase):
    def test_rich_page_serialized_native_visuals_and_owner_reference(self):
        m,s=example();b=build(m,s);page=b['raw']['definition.json']['sheets'][1];v=page['workloadItemEntityVisuals']
        self.assertEqual([x['visualType'] for x in v].count('SUPER_FILTER'),4)
        self.assertEqual([x['visualType'] for x in v].count('ANALYTICS_PLUS'),3)
        self.assertEqual([x['visualType'] for x in v].count('BI_TEXT'),2)
        self.assertEqual(v[-1]['visualId'],b['identities'][0]['visualId']);self.assertTrue(v[-1]['isEmbedded'])
        self.assertFalse(page['isHidden'])
        p,_=owner_parts(b);self.assertEqual(len([r for r in p['superFilterAssignments'] if r.get('isContextDimension')]),1)
        self.assertEqual(len(p['superFilterAssignments']),4)
        for x in v[:-1]:
            p=b['raw'][f'sheets/{page["recordGuid"]}/visuals/{x["visualId"]}/properties.json']['properties']
            self.assertNotIn('originEntityId',p)
            if x['visualType']=='ANALYTICS_PLUS':
                self.assertEqual(p['pivotAssignments'][0]['bucketId'],'AC')
                self.assertEqual(json.loads(p['visualState']['hiddenProperties_!!!_chartsMode'])['visualMode'],'CARD')
                self.assertIn('[$Value]',json.loads(p['visualState']['hiddenProperties_!!!_kpiControls'])['gridLayout'][0]['staticText'])
                self.assertEqual(len(p['visualState']['embeddedSuperFilter']['superFilterAssignments']),3)
            if x['visualType']=='BI_TEXT':self.assertEqual(json.loads(p['visualState']['text'])['root']['type'],'root')
    def test_layout_grid_is_last_full_width_and_all_rows_aligned(self):
        for width,n,k in [(1000,4,3),(1600,7,5),(2400,12,9)]:
            l=rectangles(n,k,width=width,layout='stacked');r=l['rectangles'];g=r['grid']
            self.assertEqual(g['width'],width-48);self.assertGreaterEqual(g['height'],450)
            for name,a in r.items():
                self.assertLessEqual(a['x']+a['width'],width);self.assertLessEqual(a['y']+a['height'],l['height'])
                if name!='grid':self.assertLess(a['y']+a['height'],g['y'])
                for key,c in r.items():
                    if key!=name:self.assertFalse(overlap(a,c))
    def test_scope_and_preflight_preserve_dashboard_and_context(self):
        m,s=example();out=prepare_scope(s,SUPPORTED,m);preflight(out['spec'])
        self.assertTrue(out['completeOriginalScope']);self.assertEqual(out['spec']['dashboards'],s['dashboards'])
        self.assertEqual(out['spec']['sheets'][0]['context'],s['sheets'][0]['context'])

    def test_default_rail_and_balanced_rows(self):
        for width,n,k,c,pages in [(1000,1,0,0,1),(1600,3,0,2,2),(1920,4,5,3,7),(2400,12,9,5,9)]:
            layout=rectangles(n,k,width=width,charts=c,pages=pages)
            r=layout['rectangles']
            baseline=layout['height']-24
            self.assertEqual(r['navigator']['height'],24+36*pages)
            self.assertEqual(r['slicer:0']['x'],r['navigator']['x'])
            self.assertGreater(r['grid']['x'],r['navigator']['x']+r['navigator']['width'])
            last=r[f'slicer:{n-1}']
            self.assertEqual(last['y']+last['height'],baseline)
            last=r[f'chart:{c-1}'] if c else r['grid']
            self.assertEqual(last['y']+last['height'],baseline)
            if c:
                self.assertEqual(r['chart:0']['y'],r['grid']['y']+r['grid']['height']+16)
                self.assertEqual(last['x']+last['width'],width-24)
            if c>1:
                self.assertEqual(r['chart:0']['height'],r['chart:1']['height'])
                self.assertLessEqual(abs(r['chart:0']['width']-r['chart:1']['width']),1)
            self.assertEqual(rectangles(n,k,charts=c,layout=layout),layout)
        no_rail=rectangles(0,0)
        self.assertEqual(no_rail['rectangles']['grid']['width'],no_rail['width']-48)
    def test_missing_configuration_is_not_reported_complete(self):
        m,s=example();s.pop('dashboards');s['sheets'][0].pop('context');s['sheets'][0].pop('dimensionIdMappings')
        o=prepare_scope(s,SUPPORTED,m);self.assertFalse(o['completeOriginalScope'])
        self.assertTrue(any(x['path']=='capability:planning.filter-context' and x['status']=='omitted' for x in o['coverage']))
    def test_bad_optional_kpi_omits_only_that_visual(self):
        m,s=example();s['dashboards'][0]['cards'][0]['field']='Unknown[Revenue]'
        o=prepare_scope(s,SUPPORTED,m);self.assertFalse(o['completeOriginalScope'])
        self.assertEqual(len(o['spec']['sheets']),1);self.assertEqual(len(o['spec']['dashboards']),1)
        self.assertEqual(len(o['spec']['dashboards'][0]['cards']),2)
    def test_unresolved_card_and_ordinary_scenario_duplicate_rejected(self):
        m,s=example();s['dashboards'][0]['cards'][0]['field']='Missing[Total]'
        with self.assertRaises(ValueError):build(m,s)
        m,s=example();s['dashboards'][0]['slicers'].append({'field':'Version[Name]'})
        with self.assertRaises(ValueError):build(m,s)
    def test_query_card_uses_supplied_current_catalog_not_label_guess(self):
        m,s=example();f={'id':'Qcurrent[result-key]','sourceId':'Qcurrent[result-key]','queryId':'Qcurrent','tableName':'Current Result',
            'columnName':'Result','columnType':'Column','dataType':'Double','sourceType':'InfoBridge','measureGuid':'123'}
        spec={'field':f['id'],'label':'Planned cost','aggregation':'sum'}
        p=card(m,spec,Registry(),query_fields=[f]);self.assertEqual(p['pivotAssignments'][0]['queryId'],'Qcurrent')
        with self.assertRaises(ValueError):card(m,spec,Registry())

class GeometryTransaction(unittest.TestCase):
    def test_visibility_only_changes_selected_sheet_and_preserves_other_part_bytes(self):
        m,s=example();b=build(m,s);d=b['dashboardIdentities'][0]
        next(s for s in b['raw']['definition.json']['sheets'] if s['recordGuid']==d['sheetGuid'])['isHidden']=True
        original=pack(b['raw']);state=copy.deepcopy(original);writes=[]
        def operation(client,ws,action,plan,**kw):
            nonlocal state
            if action=='update':writes.append(kw['definition']);state=copy.deepcopy(kw['definition'])
            return {'body':copy.deepcopy(state)}
        with patch('runtime.transport.plan_operation',side_effect=operation):
            result=visibility(None,'w','p',d['sheetGuid'],True,'show');self.assertTrue(result['visible'])
            for key,value in parts(original).items():
                if key!='definition.json':self.assertEqual(value,parts(state)[key])
            self.assertFalse(unpack(state)['definition.json']['sheets'][1]['isHidden'])
            result=visibility(None,'w','p',d['sheetGuid'],True,'show');self.assertEqual(result['write'],'already-matched');self.assertEqual(len(writes),1)
    def test_readback_phased_override_does_not_skip_context_or_direct_visuals(self):
        m,s=example();b=build(m,s);d=b['dashboardIdentities'][0];actual=copy.deepcopy(b['raw'])
        actual['definition.json']['sheets'][1]['isHidden']=False
        actual[f'sheets/{d["sheetGuid"]}/sheet.json']['properties']['reactiveVisualProperties']=[{'visualId':'999','properties':{'position':{'x':24,'y':500}}}]
        with self.assertRaises(ValueError):verify_authored(actual,b['raw'])
        source=b['identities'][0];path=f'sheets/{source["sheetId"]}/visuals/{source["visualId"]}/properties.json'
        actual[path]['properties']['superFilterAssignments']=[]
        with self.assertRaises(ValueError):verify_authored(actual,b['raw'])
if __name__=='__main__':unittest.main()
