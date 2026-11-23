import copy,unittest
from pathlib import Path
from runtime.codec import load
from runtime.planning_presentation import build_application
from runtime.application_defaults import check_application_defaults,home_defaults,require_delivery_phases,public_home_layout,require_business_navigation
from runtime.measure_bindings import semantic_measure,resolve_measure
from runtime.forecast_review import from_sheet_assignment,comparison_chart
ROOT=Path(__file__).resolve().parents[1]

class RequiredDefaultsTests(unittest.TestCase):
    def test_partial_dashboard_coverage_in_public_definition(self):
        from runtime.construct import build
        from runtime.planning_presentation import application_defaults
        from runtime.codec import unpack
        model = load(ROOT/'fixtures/model.json')
        spec = application_defaults(model, load(ROOT/'fixtures/finance-spec.json'))
        dashboard = spec['dashboards'][0]
        spec['dashboards'] = [dashboard]
        for sheet in spec['sheets']:
            sheet.pop('hidden', None)
        raw = unpack(build(model, spec)['envelope'])
        sheets = raw['definition.json']['sheets']
        owners = [sheet for sheet in sheets if sheet['sheetType'] == 'PLANNING']
        self.assertGreater(len(owners), 1)
        for owner in owners:
            self.assertEqual(owner['isHidden'], owner['displayName'] == dashboard['owner'])
        self.assertEqual(len(require_business_navigation(raw)), 1)

    def build(self):return build_application(load(ROOT/'fixtures/model.json'),load(ROOT/'fixtures/finance-spec.json'))
    def test_all_four_defaults_built_without_optional_flags(self):
        b=self.build();r=check_application_defaults(b['raw'],b['home'])
        self.assertTrue(b['raw']['planProperties.json']['properties']['homeLayout']['show'])
        self.assertEqual(r['richPlanningHeaders'],r['planningOwners']);self.assertEqual(r['homeContent'],'passed')
        self.assertTrue({'text','preview-cards'}<={i['type'] for i in b['home']['items']})

    def test_business_navigation_hides_owners_but_preserves_embedded_identity(self):
        b=self.build();sheets=b['raw']['definition.json']['sheets']
        owners=[s for s in sheets if s['sheetType']=='PLANNING']
        self.assertTrue(owners);self.assertTrue(all(s['isHidden'] is True for s in owners))
        direct={v['visualId'] for s in owners for v in s['workloadItemEntityVisuals'] if not v.get('isEmbedded')}
        embedded={v['visualId'] for s in sheets if s['sheetType']=='REPORTING' for v in s['workloadItemEntityVisuals'] if v.get('isEmbedded')}
        self.assertTrue(direct<=embedded)
        owners[0]['isHidden']=False
        with self.assertRaisesRegex(ValueError,'must be hidden'):check_application_defaults(b['raw'],b['home'])

    def test_home_excludes_current_owners_without_mutating_other_cards(self):
        layout={'items':[{'type':'preview-cards','instanceState':{'previewCards':{'columns':3,'unSelectedEntityIds':['9']}}}]}
        mapping={'new-owner-guid':{'entityId':'12','visualId':'27'}}
        out=public_home_layout(layout,mapping)
        self.assertEqual(out['items'][0]['instanceState']['previewCards']['unSelectedEntityIds'],['9','12'])
        self.assertEqual(layout['items'][0]['instanceState']['previewCards']['unSelectedEntityIds'],['9'])
        self.assertEqual(public_home_layout(out,mapping),out)
        with self.assertRaisesRegex(ValueError,'native Planning owner'):public_home_layout(layout,{'guid':{'entityId':'copied-guid'}})

    def test_business_powertable_is_visible_independently_of_hidden_owners(self):
        raw={'definition.json':{'sheets':[{'recordGuid':'master','displayName':'Product Master','sheetType':'POWERTABLE','isHidden':False}]}}
        self.assertEqual(require_business_navigation(raw),[])
        raw['definition.json']['sheets'][0]['isHidden']=True
        with self.assertRaisesRegex(ValueError,'PowerTable must be visible'):require_business_navigation(raw)
    def test_home_cannot_silently_be_hidden(self):
        s=load(ROOT/'fixtures/finance-spec.json');s['home']={'show':False}
        with self.assertRaisesRegex(ValueError,'cannot be hidden'):home_defaults(s)
    def test_home_content_and_visibility_are_independent_requirements(self):
        b=self.build()
        with self.assertRaisesRegex(ValueError,'description and available'):check_application_defaults(b['raw'],{'items':[]})
        b['raw']['planProperties.json']['properties']['homeLayout']['show']=False
        with self.assertRaisesRegex(ValueError,'visibility'):check_application_defaults(b['raw'],b['home'])
    def test_auto_title_and_missing_colors_fail_completion(self):
        b=self.build();p=next(v['properties'] for k,v in b['raw'].items() if k.endswith('/properties.json') and 'manage_measures' in v.get('properties',{}).get('visualState',{}))
        before=copy.deepcopy(p['visualState']['chartCustomTitle'])
        p['visualState']['chartCustomTitle']['customTitle']['elements'][0]['content']='[fields]'
        with self.assertRaises(ValueError):check_application_defaults(b['raw'],b['home'])
        p['visualState']['chartCustomTitle']=before;p['visualState']['formatConfig']['measure']={}
        with self.assertRaisesRegex(ValueError,'source-role'):check_application_defaults(b['raw'],b['home'])
    def test_existing_home_blocks_are_preserved_and_missing_cards_added(self):
        s=load(ROOT/'fixtures/finance-spec.json');s['home']={'blocks':[{'key':'kept','type':'text','title':'Keep me','description':'Existing business guidance'}],'rows':[{'blocks':['kept']}],'order':4}
        a=home_defaults(s);self.assertEqual(a['home']['blocks'][0],s['home']['blocks'][0]);self.assertEqual(a['home']['order'],4)
        self.assertEqual(home_defaults(a),a)

    def test_arial_rejects_global_and_effective_measure_overrides(self):
        for level in ('global','measure','header','home'):
            b=self.build();p=next(v['properties'] for k,v in b['raw'].items() if k.endswith('/properties.json') and 'manage_measures' in v.get('properties',{}).get('visualState',{}));vs=p['visualState']
            if level=='global':vs['globalStyles']['fontFamily']='Segoe UI'
            elif level=='measure':
                mid=vs['manage_measures'][0]['id']
                vs['formatConfig']['measure'][mid].append({'format':{'4':'Calibri'},'order':9999})
            elif level=='header':vs['chartCustomTitle']['customTitle']['elements'][0]['content']='<p style="font-family:Calibri;">Same business title</p>'
            else:
                item=next(i for i in b['home']['items'] if i['type']=='text')
                item['instanceState']['text']['title']=item['instanceState']['text']['title'].replace('font-family: Arial','font-family: Calibri')
            with self.subTest(level=level),self.assertRaisesRegex(ValueError,'Arial'):check_application_defaults(b['raw'],b['home'])

    def test_component_only_construction_is_never_application_complete(self):
        from runtime.construct import build
        b=build(load(ROOT/'fixtures/model.json'),load(ROOT/'fixtures/finance-spec.json'))
        self.assertTrue(b['raw']['planProperties.json']['properties']['homeLayout']['show'])
        self.assertFalse(b['evidence']['applicationComplete'])
        with self.assertRaisesRegex(ValueError,'missing rich'):require_delivery_phases(b,home_visible=True,dashboard_geometry=[],dashboard_visibility=[])

    def test_public_delivery_checks_visibility_and_geometry_without_claiming_role_content(self):
        b=self.build();ids=[d['sheetGuid'] for d in b['dashboardIdentities']]
        args=dict(home_visible=True,dashboard_geometry=ids,dashboard_visibility=ids)
        result=require_delivery_phases(b,**args)
        self.assertEqual(result['mandatoryDefaults'],'passed')
        self.assertEqual(result['roleSpecificHome'],'not-published')
        for field,missing in [('home_visible',False),('dashboard_geometry',[]),('dashboard_visibility',[])]:
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'Incomplete application'):
                require_delivery_phases(b,**{**args,field:missing})

    def test_reference_content_cannot_remove_required_dashboards(self):
        b=self.build();sheets=b['raw']['definition.json']['sheets']
        b['raw']['definition.json']['sheets']=[s for s in sheets if s['sheetType']!='REPORTING']
        with self.assertRaisesRegex(ValueError,'missing rich'):check_application_defaults(b['raw'],b['home'])

class BindingRegressionTests(unittest.TestCase):
    def test_dax_record_cannot_be_used_as_sheet_output(self):
        c={'id':'17','visualId':2,'measureGuid':'33','name':'Same caption','columnMeta':{'id':'33','data_type':'Number','measure_type':{'Native':{'measure_role':'ACMeasure'}}}}
        with self.assertRaisesRegex(ValueError,'Native companions'):from_sheet_assignment(c,'2','Owner')
    def test_visual_formula_unwraps_real_native_tag(self):
        c={'id':'17','visualId':2,'measureGuid':'33','name':'Output','columnMeta':{'id':'33','data_type':'Number','measure_type':{'VisualColumn':{'Formula':{'formula':'1'}}}}}
        s={'name':'Owner','visualId':'2','columns':[c],'properties':{'visualState':{'manage_measures':[{'id':'33'}]}}}
        req={'sourceType':'Visual','visualId':'2','columnId':'17','sourceMeasureGuid':'33'}
        a=resolve_measure(req,sheets=[s]);self.assertEqual(a['sourceType'],'Visual');self.assertEqual(a['id'],'17')
        req['sourceMeasureGuid']='34'
        with self.assertRaisesRegex(ValueError,'must agree'):resolve_measure(req,sheets=[s])
    def test_same_caption_chart_binding_does_not_keep_stale_filter(self):
        from runtime.chart_filters import chart_field_filter
        model={'fields':[{'id':'Finance[Current]','columnName':'Current','tableName':'Finance','columnType':'Measure','dataType':'Double'}]}
        dax=semantic_measure(model,'Finance[Current]','PY');wrong={**dax,'id':'17','sourceId':'17','sourceType':'Visual','visualId':'2','columnType':'Column'}
        category={'id':'Region[Name]','sourceId':'Region[Name]','columnName':'Name','name':'Name','tableName':'Region','sourceType':'PowerBI','columnType':'Column','dataType':'Text','dataRoleType':'Grouping','bucketId':'category','order':0}
        p={'visualType':50,'pivotAssignments':[category,wrong],'visualState':{},'superFilterAssignments':[chart_field_filter(wrong)]}
        out=comparison_chart(p,{**dax,'bucketId':'AC'},dax)
        cards=[r for r in out['superFilterAssignments'] if r.get('isDefaultMeasure')]
        self.assertTrue(all(r['isDaxMeasure'] for r in cards))
        self.assertTrue(all(r['pivotAssignments'][-1]['sourceType']=='PowerBI' for r in cards))
        self.assertEqual(len(cards),2)
        self.assertIn(category,out['pivotAssignments'])

if __name__=='__main__':unittest.main()
