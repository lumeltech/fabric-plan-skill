import copy,json,unittest
from pathlib import Path
from runtime.codec import load
from runtime.construct import build
from runtime.planning_presentation import apply_presentation,measure_roles,application_defaults,build_application,check_application,PALETTE
ROOT=Path(__file__).resolve().parents[1]
def sample():
    model=load(ROOT/'fixtures/model.json');spec=load(ROOT/'fixtures/finance-spec.json');b=build(model,spec)
    path=next(k for k in b['raw'] if k.endswith('/dataInput.json'))
    props=b['raw'][path.replace('dataInput.json','properties.json')]['properties'];records=b['raw'][path]['columns']
    return model,spec,b,props,records
class PresentationTests(unittest.TestCase):
    def test_complete_text_canvas_replaces_automatic_mentions(self):
        _,_,_,p,c=sample();p['visualState']['chartCustomTitle']={'customTitle':{'elements':[{'id':'preserved','type':'DEFAULT_TITLE','content':'[fields]'}]},'unrelated':7}
        x=apply_presentation(p,c,'Estimate & review','Adjust eligible inputs; review calculated outcomes.')['properties']['visualState']
        canvas=x['chartCustomTitle']['customTitle'];e=canvas['elements'][0]
        self.assertEqual(e['id'],'preserved');self.assertEqual(e['type'],'TEXT');self.assertEqual(e['layout']['w'],64)
        self.assertTrue({'position','dimension','layout','content'}<=e.keys());self.assertNotIn('[fields]',e['content'])
        self.assertIn('Estimate &amp; review',e['content']);self.assertEqual(x['chartCustomTitle']['unrelated'],7);self.assertTrue(x['showHeaderFooter'])

    def test_roles_from_typed_sources_not_names(self):
        _,_,_,p,c=sample();r=measure_roles(p,c)
        self.assertIn('powerbi',{v['role'] for v in r.values()});self.assertIn('formula',{v['role'] for v in r.values()})
        self.assertIn('input',{v['role'] for v in r.values()})
        p['visualState']['manage_measures'][0]['label']='Formula editable input';self.assertEqual(measure_roles(p,c),{**r,p['visualState']['manage_measures'][0]['id']:{**r[p['visualState']['manage_measures'][0]['id']],'label':'Formula editable input'}})

    def test_explicit_recolor_preserves_calculation_and_conditional_formats(self):
        _,_,_,p,c=sample();before=copy.deepcopy(p);p['visualState']['jet_cfProps']={'enabled':True,'rules':[{'name':'preserve'}]}
        out=apply_presentation(p,c,'Description','Review configured values.',override_colors=True)['properties']
        self.assertEqual(p['pivotAssignments'],out['pivotAssignments']);self.assertEqual(p['visualState']['manage_measures'],out['visualState']['manage_measures'])
        self.assertEqual(out['visualState']['jet_cfProps'],p['visualState']['jet_cfProps'])
        for mid,role in measure_roles(p,c).items():
            formats=out['visualState']['formatConfig']['measure'][mid]
            self.assertTrue(any(e['format'].get('3')==PALETTE[role['role']]['text'] for e in formats))
            self.assertTrue(all(e in formats for e in before['visualState']['formatConfig']['measure'][mid]))

    def test_safe_html_and_repair_idempotence(self):
        _,_,_,p,c=sample();a=apply_presentation(p,c,'<Title>','A & B',override_colors=True)['properties']
        b=apply_presentation(a,c,'<Title>','A & B',override_colors=True)['properties']
        self.assertEqual(a,b);self.assertIn('&lt;Title&gt;',a['visualState']['chartCustomTitle']['customTitle']['elements'][0]['content'])

    def test_existing_explicit_colors_preserved_by_default(self):
        _,_,_,p,c=sample();mid=p['visualState']['manage_measures'][0]['id']
        p['visualState']['formatConfig']['measure'][mid][0]['format']['3']='#112233'
        b=apply_presentation(p,c,'Title','Description')['properties']
        self.assertEqual(p['visualState']['formatConfig']['measure'][mid],b['visualState']['formatConfig']['measure'][mid])

    def test_app_adds_header_slicers_charts_and_embed_for_each_owner(self):
        m,s,_,_,_=sample();original=copy.deepcopy(s);out=build_application(m,s)
        self.assertEqual(s,original);self.assertEqual(out['presentationCheck']['coveredByRichDashboard'],len(s['sheets']))
        self.assertEqual(len(out['dashboardIdentities']),len(s['sheets']))
        for d in out['dashboardIdentities']:
            rr=d['layout']['rectangles'];self.assertGreaterEqual(rr['grid']['height'],560)
            self.assertEqual(rr['chart:0']['y'],rr['grid']['y']+rr['grid']['height']+16)
            self.assertEqual(rr['navigator']['x'],rr['slicer:0']['x'])

    def test_existing_dashboard_controls_and_filters_retained(self):
        m=load(ROOT/'fixtures/context-dashboard-model.json');s=load(ROOT/'fixtures/context-dashboard-spec.json');out=application_defaults(m,s)
        for a,b in zip(s['dashboards'],out['dashboards']):self.assertEqual(a['slicers'],b['slicers']);self.assertEqual(a['cards'],b['cards']);self.assertTrue(b['charts'])

    def test_missing_dashboard_is_explicit_failure(self):
        _,_,b,_,_=sample()
        with self.assertRaisesRegex(ValueError,'missing rich'):check_application(b['raw'])

    def test_input_only_requires_resolved_chart_source(self):
        m,s,_,_,_=sample();s['sheets'][0]['measures']=[{'kind':'DataInput','key':'one','label':'Input'}]
        with self.assertRaisesRegex(ValueError,'real dimension and numeric source'):application_defaults(m,s)

    def test_card_alone_does_not_satisfy_chart_requirement(self):
        m,s,_,_,_=sample();b=build_application(m,s)
        for path,v in b['raw'].items():
            p=v.get('properties',{}) if isinstance(v,dict) else {}
            if p.get('visualType')==50:p['chartType']='CARD'
        with self.assertRaisesRegex(ValueError,'missing rich'):check_application(b['raw'])

if __name__=='__main__':unittest.main()
