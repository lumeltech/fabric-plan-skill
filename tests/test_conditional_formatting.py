import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,json,unittest
from pathlib import Path
from runtime.matrix_formatting import compile_formatting,symbolic_rules,CF_SNAPSHOT
from runtime.planning_presentation import build_application,application_defaults
from runtime.workflow import preflight,SUPPORTED
from runtime.scope import prepare_scope
from runtime.forecast_review import apply_negative_variance,negative_variance_rule
from runtime.codec import load

ROOT=Path(__file__).resolve().parents[1]
AMOUNT='18446744073709550001';HELPER='18446744073709550002'
def state():
 return {'manage_measures':[{'id':AMOUNT,'label':'Amount'},{'id':HELPER,'label':'Check'}],
   'rowDimensions':[{'id':'category'},{'id':'product'}],'columnDimensions':[{'id':'month'}],
   'business':{'inputs':'preserve','formula':'M_'+AMOUNT+' == 0'},'filters':[{'opaque':True}]}
def request(key='check',icon=None):
 return {'id':key,'label':'Below zero','target':AMOUNT,'test':HELPER,'operator':'<','threshold':0,
   'rowScope':'child','columnScope':'both','excludeRowTotal':True,'excludeColumnTotal':False,
   'appearance':{'icon':icon,'iconColor':'#A60000'} if icon else {'textColor':'#A60000'}}

class CurrentCFContractTests(unittest.TestCase):
 def test_discovery_text_routes_render_and_cf_is_prominent(self):
  from runtime.discovery import discover,render
  all_modules=discover()
  self.assertTrue(render(all_modules))
  for query in ('CF rules missing in Manage Rules','red arrows and unfavorable variance','create a new report with conditional formatting'):
   result=discover(query)
   self.assertTrue(any(m['id'] in ('CONDITIONAL-FORMATTING','F15') for m in result['modules'][:3]))
   self.assertTrue(render(result))

 def test_current_wire_identity_selectors_references_and_complete_shape(self):
  before=state();out=compile_formatting(before,{'rules':[request(),request('arrow','down'),request('flag','flag')]})['state']
  self.assertEqual(before,state());self.assertEqual(out['business'],before['business']);self.assertEqual(out['filters'],before['filters'])
  self.assertEqual(out['cfProps'],out['jet_cfProps']);self.assertEqual(len(out['cfProps']['rules']),3)
  for r in out['cfProps']['rules']:
   self.assertTrue(r['name'].startswith(AMOUNT));self.assertTrue(r['newRule']);self.assertTrue(r['autoFontColor'])
   self.assertTrue(set(CF_SNAPSHOT['ruleSeed'])<=set(r))
   for k in ('highlightedColumnMembers','highlightedRowMembers','selectedColumnMeasures'):self.assertIsNone(r[k])
   self.assertEqual(r['highlightedMeasure'],AMOUNT);self.assertEqual(r['basedOn'],HELPER);self.assertEqual(r['bubbleBasedOn'],HELPER)
   self.assertEqual(r['ranking']['row_dimension_id'],'product');self.assertFalse(r['includeNull'])
   c=r['conditions'][0];self.assertEqual(c['operator'],'<');self.assertEqual(c['comparisonValue'],0)
   for k in ('basedOn','comparisonMeasure','calculationMeasure1','calculationMeasure2','fromMeasure','toMeasure'):self.assertEqual(c[k],HELPER)
   self.assertNotIn('${',json.dumps(r));self.assertFalse(r['applyBackgroundColor'])
  self.assertFalse(out['cfProps']['rules'][2]['applyTextColor'])

 def test_migration_and_repeat_do_not_duplicate_or_change_unrelated_rules(self):
  s=compile_formatting(state(),{'rules':[request()]})['state']
  legacy=copy.deepcopy(s['jet_cfProps']['rules'][0]);legacy.update(name='check',newRule=False,highlightedRowMembers=[])
  legacy['conditions'][0].update(calculationMeasure1='0',future='keep')
  untouched={'name':'user-rule','opaque':['do','not','change']}
  s['cfProps']['rules']=[copy.deepcopy(untouched),copy.deepcopy(legacy)]
  s['jet_cfProps']['rules']=[copy.deepcopy(legacy)]
  out=compile_formatting(s,{'rules':[request()]})['state']
  self.assertEqual(out['cfProps']['rules'][0],untouched)
  self.assertEqual(out['cfProps']['rules'][1],out['jet_cfProps']['rules'][0])
  self.assertEqual(out['cfProps']['rules'][1]['conditions'][0]['future'],'keep')
  self.assertEqual(compile_formatting(out,{'rules':[request()]})['state'],out)

 def test_invalid_or_ambiguous_requests_fail_without_mutation(self):
  for mutation in ({'test':'missing'},{'operator':'='},{'threshold':True}):
   s=state();r=request();r.update(mutation)
   with self.assertRaises(ValueError):compile_formatting(s,{'rules':[r]})
   self.assertEqual(s,state())
  s=compile_formatting(state(),{'rules':[request()]})['state'];old=copy.deepcopy(s['cfProps']['rules'][0]);old['name']='check';s['cfProps']['rules'].append(old)
  with self.assertRaises(ValueError):compile_formatting(s,{'rules':[request()]})
  with self.assertRaises(ValueError):symbolic_rules([request()],{'other':AMOUNT})

 def test_no_rows_and_explicit_legacy_profile(self):
  s=state();s['rowDimensions']=[]
  out=compile_formatting(s,{'rules':[request()],'mirrorCompatibilityRules':False})['state']
  self.assertNotIn('cfProps',out);self.assertIsNone(out['jet_cfProps']['rules'][0]['ranking']['row_dimension_id'])
  self.assertNotIn('cfProps',compile_formatting(state(),{'rules':[]})['state'])

 def test_forecast_helper_uses_current_shared_contract(self):
  r=negative_variance_rule(AMOUNT);self.assertTrue(r['name'].startswith(AMOUNT));self.assertTrue(r['newRule'])
  out=apply_negative_variance({'visualState':state()},AMOUNT)
  self.assertEqual(out['visualState']['cfProps'],out['visualState']['jet_cfProps'])
  self.assertEqual(out,apply_negative_variance(out,AMOUNT))

 def test_standard_builder_constructs_a_fresh_complete_report_with_symbolic_rules(self):
  model=load(ROOT/'assets/fixtures/model.json');spec=load(ROOT/'assets/examples/conditional-formatting/application.json')
  scoped=prepare_scope(application_defaults(model,spec),SUPPORTED,model)
  self.assertTrue(scoped['completeOriginalScope']);preflight(scoped['spec'])
  first=build_application(model,spec);second=build_application(model,spec)
  self.assertNotEqual(first['identities'][0]['sheetId'],second['identities'][0]['sheetId'])
  self.assertEqual(len(first['dashboardIdentities']),2);self.assertTrue(first['raw']['planProperties.json']['properties']['homeLayout']['show'])
  for i,identity in enumerate(first['identities']):
   vs=first['raw'][f"sheets/{identity['sheetId']}/visuals/{identity['visualId']}/properties.json"]['properties']['visualState']
   self.assertEqual(vs['cfProps'],vs['jet_cfProps']);self.assertEqual(len(vs['cfProps']['rules']),[4,3][i])
   for r,expected in zip(vs['cfProps']['rules'],spec['sheets'][i]['conditionalFormatting']):
    self.assertEqual(r['highlightedMeasure'],identity['measures'][expected['target']])
    self.assertEqual(r['basedOn'],identity['measures'][expected['test']])
    self.assertEqual(r['conditions'][0]['operator'],expected['operator'])
   self.assertEqual(vs['globalStyles']['fontFamily'],'Arial')

if __name__=='__main__':unittest.main()
