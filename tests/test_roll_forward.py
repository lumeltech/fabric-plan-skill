"""Offline presentation/routing regressions; no native calculation assertions."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from runtime.roll_forward import apply_totals_defaults,roll_forward_presentation,TOTALS_DEFAULTS
from runtime.column_presentation import apply_column_presentation,expand_columns
from runtime.construct import build
from runtime.codec import load
from runtime.discovery import discover,catalog
from runtime.business_intent import plan_intent
ROOT=Path(__file__).resolve().parents[1]

class RollForwardTests(unittest.TestCase):
    def request(self):return load(ROOT/'assets/examples/roll-forward-presentation.request.json')

    def test_totals_defaults_preserve_explicit_user_choices_and_freeze(self):
        p={'visualState':{'totals_config':{'row_grand_total':None,'column_sub_total':'Right','freeze_total':True}}}
        before=copy.deepcopy(p);out=apply_totals_defaults(p)
        self.assertEqual(out['visualState']['totals_config'],dict(TOTALS_DEFAULTS,row_grand_total=None,column_sub_total='Right',freeze_total=True))
        self.assertEqual(p,before)
        reset=apply_totals_defaults(p,reset=True)['visualState']['totals_config']
        self.assertEqual(reset,dict(TOTALS_DEFAULTS,freeze_total=True))
        for invalid in [False,'Off',0]:
            with self.assertRaises(ValueError):apply_totals_defaults({'visualState':{'totals_config':{'column_sub_total':invalid}}})

    def test_new_build_partial_overrides_and_symbolic_hierarchy(self):
        model=load(ROOT/'assets/fixtures/model.json');base=load(ROOT/'assets/fixtures/finance-spec.json')
        for overrides in ({},{'column_grand_total':None},{'row_sub_total':'Bottom','column_sub_total':'Right'}):
            spec=copy.deepcopy(base)
            for sheet in spec['sheets']:
                sheet['totals_config']=overrides;sheet['columnPresentation']='preserve'
                visible=[m for m in sheet['measures'] if m.get('visible',True)]
                sheet['measureHierarchy']=[{'measure':m['key'],'level':0 if i<2 else 1} for i,m in enumerate(visible)]
            result=build(model,spec)
            for identity in result['identities']:
                vs=result['raw'][f"sheets/{identity['sheetId']}/visuals/{identity['visualId']}/properties.json"]['properties']['visualState']
                self.assertEqual(vs['totals_config'],dict(TOTALS_DEFAULTS,freeze_total=False,**overrides))
                self.assertEqual(vs['layout']['measure_layout'],'Rows')
                self.assertEqual({n['id'] for n in vs['measure_tree']},{m['id'] for m in vs['manage_measures'] if m['visible']})

    def test_column_helpers_do_not_remove_off_or_touch_totals_in_expansion_only(self):
        p=self.request()['properties'];p['visualState']['totals_config']={'column_grand_total':None,'column_sub_total':None}
        self.assertEqual(apply_column_presentation(p)['visualState']['totals_config'],p['visualState']['totals_config'])
        self.assertEqual(expand_columns(p)['visualState']['totals_config'],p['visualState']['totals_config'])

    def test_hierarchy_preserves_business_state_and_exact_large_ids(self):
        r=self.request();p=r['properties'];vs=p['visualState'];mid=r['hierarchy'][1]['id']
        vs['manage_measures'].append({'id':'hidden','label':'helper','visible':False,'order':12,'source':'retain'})
        vs['measure_tree']=[{'id':mid,'level':0,'meta':{'hide_in':None,'node_type':{'Measure':{'aggregation':'Formula'}},'rules':['retained']}}]
        vs['measure_tree_node_expand_state']={'expanded':{'foreign':True},'other':'keep'}
        vs['ragged_hierarchy_config']={'enabled':True,'other':3}
        vs['dimension_id_mapping']={'mappings':{'source':'stable'}}
        p['inputRecords']=[{'formula':'unchanged','allow_input':{'BasedOnFormula':'lock'},'stored':[1,0]}]
        vs['aggregation_config']={'special':'preserve'};vs['formatConfig']={'measure':{mid:[{'format':{'3':'#abcdef','13':'auto'}}]}}
        before=copy.deepcopy(p);out=roll_forward_presentation(**r);new=out['visualState']
        self.assertEqual(p,before)
        self.assertEqual(out['inputRecords'],before['inputRecords'])
        for key in ('dimension_id_mapping','aggregation_config','formatConfig'):self.assertEqual(new[key],vs[key])
        strip=lambda mm:{m['id']:{k:v for k,v in m.items() if k!='order'} for m in mm}
        self.assertEqual(strip(new['manage_measures']),strip(vs['manage_measures']))
        self.assertEqual(new['measure_tree'][1]['meta'],vs['measure_tree'][0]['meta'])
        self.assertTrue(new['measure_tree_node_expand_state']['expanded'][mid])
        self.assertNotIn('foreign',new['measure_tree_node_expand_state']['expanded'])
        self.assertFalse(new['ragged_hierarchy_config']['enabled'])
        self.assertEqual(roll_forward_presentation(out,r['hierarchy']),out)

    def test_invalid_or_incomplete_hierarchy_never_silently_hides_measures(self):
        r=self.request()
        for mutation in ('missing','duplicate','foreign','number','jump','bool','negative','first'):
            h=copy.deepcopy(r['hierarchy'])
            if mutation=='missing':h.pop()
            elif mutation=='duplicate':h[-1]['id']=h[0]['id']
            elif mutation=='foreign':h[-1]['id']='not-current'
            elif mutation=='number':h[-1]['id']=int(h[-1]['id'])
            else:h[0 if mutation=='first' else 2]['level']={'jump':3,'bool':True,'negative':-1,'first':1}[mutation]
            with self.assertRaises(ValueError,msg=mutation):roll_forward_presentation(r['properties'],h)

    def test_varied_prompts_find_the_complete_roll_forward_module(self):
        for prompt in ['cash runway and funding shortfall','stock depletion and replenishment','invoice cohorts and collections timing','staffing exits depend on opening headcount','unearned revenue recognition and cancellations','roll forward','carry forward balances']:
            self.assertIn('ROLL-FORWARD',[m['id'] for m in discover(prompt)['modules'][:3]],prompt)
        data=plan_intent(load(ROOT/'assets/examples/roll-forward-intent.json'))
        self.assertIn('ROLL-FORWARD',data['requirements'][0]['modules'])
        self.assertIn('ReadAndEdit',(ROOT/'references/roll-forward-authoring.md').read_text())
        brief=load(ROOT/'assets/examples/roll-forward-intent.json');del brief['requirements'][0]['details']['seedAuthority']
        self.assertIn('seedAuthority',plan_intent(brief)['requirements'][0]['unresolved'])

    def test_complete_source_matches_preservation_manifest(self):
        entries=load(ROOT/'assets/preservation-manifest.json')
        entry=entries[0]
        b=b''.join((ROOT/path).read_bytes() for path in entry['preservedFiles'])
        self.assertEqual(hashlib.sha256(b).hexdigest(),entry['sha256'])
        text=b.decode('utf-8-sig')
        for heading in ['Treasury cash flow forecast','Inventory and replenishment forecast','Accounts receivable and collections forecast','Headcount and hiring forecast','Deferred revenue forecast','Instructions to add to the authoring skill']:
            self.assertIn(heading,text)

    def test_advertised_examples_execute_from_an_unrelated_working_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            for command,example in [('planning-totals','planning-totals.request.json'),('roll-forward-presentation','roll-forward-presentation.request.json'),('plan-intent','roll-forward-intent.json')]:
                out=Path(folder)/(command+'.json')
                run=subprocess.run([sys.executable,str(ROOT/'scripts/plan.py'),command,'--input',str(ROOT/'assets/examples'/example),'--out',str(out)],cwd=folder,capture_output=True,text=True)
                self.assertEqual(run.returncode,0,run.stderr);self.assertTrue(out.exists())

if __name__=='__main__':unittest.main()
