"""Offline route/graph regressions, not tests of agent language understanding."""
import copy,json,unittest
from pathlib import Path
from runtime.business_intent import plan_intent,ROUTES
from runtime.discovery import catalog

ROOT=Path(__file__).resolve().parents[1]

class BusinessIntentTests(unittest.TestCase):
    def brief(self,kind,details):
        return {'request':'Business outcome','requirements':[{'id':'outcome','text':'Business outcome','intent':kind,'details':details}]}

    def test_every_selected_route_resolves_to_bundled_contract(self):
        d=catalog();m={x['id']:x for x in d['modules']}
        for kind,(modules,ops,_) in ROUTES.items():
            for mid in modules:
                for g in m[mid]['guides']:self.assertTrue((ROOT/'references'/g['file']).exists(),(kind,g))
            for op in ops:self.assertIn(op,d['actions'],kind)

    def test_hybrid_preserves_clauses_and_dependency_order(self):
        b=json.loads((ROOT/'examples/business-intent/merit-review.json').read_text())
        b['requirements'].reverse() # business prose need not arrive in execution order
        r=plan_intent(b);self.assertTrue(r['readyForAuthoring'])
        self.assertTrue((ROOT/'references'/r['defaultPolicy']['source']).is_file())
        self.assertEqual({x['text'] for x in r['requirements']},{x['text'] for x in b['requirements']})
        order=r['executionOrder']
        for x in r['requirements']:
            for parent in x['dependsOn']:self.assertLess(order.index(parent),order.index(x['id']))
        self.assertEqual(next(x for x in r['requirements'] if x['id']=='base')['modules'],['F21'])
        self.assertEqual(next(x for x in r['requirements'] if x['id']=='review')['modules'],['F19'])
        self.assertEqual(next(x for x in r['requirements'] if x['id']=='merit')['details']['maximum'],{'measureExpression':'0.08'})

    def test_missing_forecast_details_not_filled_from_case(self):
        b=self.brief('rolling-forecast',{'actuals':'sales'});before=copy.deepcopy(b)
        r=plan_intent(b);self.assertFalse(r['readyForAuthoring'])
        self.assertIn('openDefault',r['requirements'][0]['unresolved'])
        self.assertEqual(r['requirements'][0]['details'],{'actuals':'sales'})
        self.assertEqual(b,before)

    def test_semantic_transform_routes_to_bridge_not_direct_native(self):
        for transform in ['join','merge','append','sql','aggregate']:
            b=self.brief('reuse-values',{'sourceOrigin':'semantic','source':'measure','targetGrain':'mapped units','transformation':transform,'grainCompatibility':'transformation-required'})
            r=plan_intent(b)['requirements'][0]
            self.assertEqual(r['modules'],['F18'])
            self.assertIn('bridge-consumer',[a['id'] for a in r['operations']])

    def test_incompatible_direct_link_stays_unresolved(self):
        b=self.brief('reuse-values',{'sourceOrigin':'sheet','source':'input','targetGrain':'SKU','transformation':'direct','grainCompatibility':'finer-than-source'})
        self.assertFalse(plan_intent(b)['readyForAuthoring'])

    def test_unknown_and_control_requirements_not_silently_dropped(self):
        for kind,details in [('unknown',{}),('approval',{'scope':'budget','stages':['manager']}),('access-control',{'scope':'sheet','audience':'reviewers','policy':'read-only'}),('scenario',{'behavior':'native-lifecycle','scope':'application'})]:
            r=plan_intent(self.brief(kind,details))
            self.assertFalse(r['readyForAuthoring']);self.assertEqual(len(r['requirements']),1)
            self.assertEqual(r['requirements'][0]['execution'],'not-started')

    def test_invalid_dependency_and_cycle_fail_before_authoring(self):
        b=self.brief('commentary',{'grain':'Quarter','placement':'period-repeated'})
        b['requirements'][0]['dependsOn']=['absent']
        with self.assertRaisesRegex(ValueError,'Unknown dependency'):plan_intent(b)
        b['requirements'][0]['dependsOn']=['outcome']
        with self.assertRaisesRegex(ValueError,'cycle'):plan_intent(b)

if __name__=='__main__':unittest.main()
