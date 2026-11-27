import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,unittest
from runtime.export_lineage import reconcile

class ExportLineageTests(unittest.TestCase):
 def fixture(self):
  field={'id':'123','measureGuid':'123','name':'Compensation','columnType':'DI','isHierarchyColumn':False}
  owner={'measureGuid':'123','name':'Compensation','columnMeta':{'measure_type':{'Formula':{'formula':'[salary] * 2'}}}}
  return {'sheets/s/visuals/v/dataInput.json':{'columns':[owner]},'connectedPlanning/infobridge.json':{'sources':[{'sourceGuid':'src','visualId':'v','type':'PLANNING','meta':{'measures':[field],'includeMeasures':[dict(field,columnType='FORMULA')]},'queries':[]}]}}
 def test_only_type_metadata_changes(self):
  raw=self.fixture();before=copy.deepcopy(raw);changes,log=reconcile(raw)
  self.assertEqual(raw,before);self.assertEqual(len(log),1)
  expected=copy.deepcopy(before['connectedPlanning/infobridge.json']);expected['sources'][0]['meta']['measures'][0]['columnType']='FORMULA'
  self.assertEqual(changes,{'connectedPlanning/infobridge.json':expected})
 def test_wrong_owner_identity_is_rejected(self):
  raw=self.fixture();raw['sheets/s/visuals/v/dataInput.json']['columns'][0]['measureGuid']='999'
  with self.assertRaisesRegex(ValueError,'identity'):reconcile(raw)
 def test_non_type_drift_is_rejected(self):
  raw=self.fixture();raw['connectedPlanning/infobridge.json']['sources'][0]['meta']['includeMeasures'][0]['measureGuid']='999'
  with self.assertRaisesRegex(ValueError,'Non-type'):reconcile(raw)
 def test_reverse_type_change_is_not_assumed(self):
  raw=self.fixture();raw['sheets/s/visuals/v/dataInput.json']['columns'][0]['columnMeta']['measure_type']={'DataInput':{}}
  with self.assertRaisesRegex(ValueError,'Unobserved'):reconcile(raw)
 def test_already_consistent_keeps_graph_byte_preservation_path(self):
  raw=self.fixture();raw['connectedPlanning/infobridge.json']['sources'][0]['meta']['measures'][0]['columnType']='FORMULA'
  self.assertEqual(reconcile(raw),({},[]))

if __name__=='__main__':unittest.main()
