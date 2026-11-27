import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,unittest
from runtime.consumer_bindings import audit_visual_consumers,restore_import_bindings
from runtime.chart_filters import ensure_chart_filters

class ImportBindingReconciliationTests(unittest.TestCase):
 def setUp(self):
  self.queries={'7':{'id':'Qcurrent','sqlPk':'7','sourceId':'S-current','name':'Workforce','status':400,
    'meta':{'selectedMeasures':[{'id':'18446744073709551614','name':'Pay','type':'DOUBLE'}]}}}
  a={'id':'7[18446744073709551614]','sourceId':'7[18446744073709551614]','queryId':'7',
     'tableName':'Workforce','columnName':'Pay','sourceType':'InfoBridge','columnType':'Column',
     'aggregationType':'sum','bucketId':'AC','dataRoleType':'Measure','dataType':'Double','measureGuid':'existing-alias'}
  self.intent={'visualType':50,'pivotAssignments':[a]};ensure_chart_filters(self.intent)
  self.current=copy.deepcopy(self.intent)
  for a in (self.current['pivotAssignments'][0],self.current['superFilterAssignments'][0]['pivotAssignments'][0]):
   a.update(id='7[11]',sourceId='7[11]')
  self.current['superFilterAssignments'][0]['configuration']['sort'][0].update(id='7[11]',columnId='7[11]')
 def test_jointly_wrong_chart_and_filter_rejected(self):
  with self.assertRaises(ValueError):audit_visual_consumers(self.current,self.queries)
 def test_repairs_six_references_without_changing_alias_or_input(self):
  before=copy.deepcopy(self.current);fixed,changes=restore_import_bindings(self.current,self.intent,self.queries)
  self.assertEqual(fixed,self.intent);self.assertEqual(self.current,before);self.assertEqual(len(changes),6)
  self.assertEqual(fixed['pivotAssignments'][0]['measureGuid'],'existing-alias')
  self.assertEqual(audit_visual_consumers(fixed,self.queries)['infoBridgeReferences'],2)
 def test_unrelated_setting_drift_is_not_overwritten(self):
  self.current['superFilterAssignments'][0]['configuration']['hide']=True
  with self.assertRaises(ValueError):restore_import_bindings(self.current,self.intent,self.queries)
 def test_missing_current_metadata_rejected(self):
  with self.assertRaises(ValueError):restore_import_bindings(self.current,self.intent,{})
 def test_invalid_intent_cannot_authorize_old_row_ids(self):
  with self.assertRaises(ValueError):restore_import_bindings(self.current,self.current,self.queries)
 def test_idempotent_valid_properties_preserve_pending_status(self):
  fixed,changes=restore_import_bindings(self.intent,self.intent,self.queries)
  self.assertEqual(changes,[])
  check=audit_visual_consumers(fixed,self.queries)
  self.assertEqual(check['catalogChecks'][0]['queryStatus'],400)
  self.assertEqual(check['dataPropagation'],'not-tested')
