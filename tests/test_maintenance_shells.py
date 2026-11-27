import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import unittest,copy
from runtime.maintenance_shells import blank_powertable,add_deferred_powertables
from runtime.codec import pack,parts,unpack
from runtime.validate import Schemas
from runtime.construct import schema

class MaintenanceShellTests(unittest.TestCase):
 def baseline(self):
  return pack({'definition.json':{'sheets':[{'displayName':'Existing','recordGuid':'00000000-0000-4000-8000-000000000001','order':3}]},'unknown.json':{'keep':['exact bytes',1]}})
 def test_blank_has_native_sheet_without_fake_source(self):
  sh,raw,m=blank_powertable('Employee Master',4,table='dbo.DimEmployee')
  self.assertEqual(sh['sheetType'],'POWERTABLE');self.assertFalse(sh['isHidden']);self.assertEqual(sh['workloadItemEntityVisuals'],[])
  self.assertEqual(len(raw),1);self.assertTrue(Schemas().check(next(iter(raw.values())),schema('Sheets/Sheet')))
  self.assertFalse(m['nativeSourceCreated']);self.assertEqual(m['intendedTable'],'dbo.DimEmployee')
 def test_add_preserves_untouched_bytes_and_filters(self):
  env=self.baseline();env['definition']['parts']+=pack({'chart/properties.json':{'properties':{'superFilterAssignments':[{'id':'keep','filterValues':['selected']}],'visualState':{'embeddedSuperFilter':{'context':'keep'}}}}})['definition']['parts']
  before=copy.deepcopy(env);after,m=add_deferred_powertables(env,[{'name':'Employee Master','table':'dbo.DimEmployee'},{'name':'Region Master'}])
  self.assertEqual(env,before)
  for k,v in parts(before).items():
   if k!='definition.json':self.assertEqual(parts(after)[k],v)
  sheets=unpack(after)['definition.json']['sheets'];self.assertEqual(len(sheets),3);self.assertEqual([x['order'] for x in sheets],[3,4,5]);self.assertEqual(len(m),2)
 def test_existing_sheet_never_cleared(self):
  with self.assertRaisesRegex(ValueError,'Existing sheet name'):add_deferred_powertables(self.baseline(),[{'name':'existing'}])
 def test_duplicate_identity_rejected(self):
  with self.assertRaisesRegex(ValueError,'identity'):add_deferred_powertables(self.baseline(),[{'name':'Other','sheetGuid':'00000000-0000-4000-8000-000000000001'}])
 def test_duplicate_request_rejected(self):
  with self.assertRaises(ValueError):add_deferred_powertables(self.baseline(),[{'name':'New'},{'name':'new'}])
 def test_blank_name_and_invalid_guid_rejected(self):
  for kw in ({'name':' ','order':1},{'name':'New','order':-1},{'name':'New','order':1,'sheet_guid':'bad'}):
   with self.assertRaises(ValueError):blank_powertable(**kw)
