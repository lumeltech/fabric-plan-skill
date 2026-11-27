import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import unittest,copy,json
from runtime.consumer_bindings import output_catalog,resolve_assignment,assert_resolved
from runtime.filters import ensure_axis_filters
from runtime.construct import sheet_properties
from runtime.intelligence import complete_card_state

class ConsumerRepairTests(unittest.TestCase):
 def setUp(self):
  self.query={'id':'Qcurrent','sqlPk':'7','sourceId':'source-current','name':'Workforce',
      'status':400,'meta':{'measures':[{'id':'18446744073709551614','name':'Pay','type':'DOUBLE','dataType':'NUMERIC'}]}}
  self.assignment={'id':'7[11]','sourceId':'7[11]','queryId':'7','tableName':'Workforce',
      'columnName':'Pay','sourceType':'InfoBridge','columnType':'Column','aggregationType':'sum','bucketId':'AC'}
 def test_small_row_id_rejected_even_when_label_matches(self):
  with self.assertRaises(ValueError):assert_resolved(self.assignment,self.query)
 def test_lossless_catalog_identity_and_domain(self):
  f=output_catalog(self.query)[0];self.assertEqual(f['id'],'7[18446744073709551614]')
  a=resolve_assignment(self.assignment,self.query,expected_output_id=f['outputId'])
  self.assertEqual(a['bucketId'],'AC');self.assertEqual(assert_resolved(a,self.query)['queryStatus'],400)
  self.assertEqual(assert_resolved(a,self.query)['dataPropagation'],'not-tested')
 def test_query_owner_and_name_not_substitutable(self):
  a=copy.deepcopy(self.assignment);a['queryId']='8'
  with self.assertRaises(ValueError):resolve_assignment(a,self.query,expected_output_id='18446744073709551614')
  a=copy.deepcopy(self.assignment);a['columnName']='Different'
  with self.assertRaises(ValueError):resolve_assignment(a,self.query,expected_output_id='18446744073709551614')
 def test_no_guess_from_ordinal(self):
  with self.assertRaises(ValueError):resolve_assignment(self.assignment,self.query,expected_output_id='11')
 def test_final_selection_excludes_removed_source_field(self):
  self.query['meta']['selectedMeasures']=[{'id':'generated-output','name':'Contribution','type':'DOUBLE'}]
  self.assertEqual([f['outputId'] for f in output_catalog(self.query)],['generated-output'])
  self.query['meta']['selectedMeasures']=[]
  self.assertEqual(output_catalog(self.query),[])
 def test_partial_kpi_variance_and_outer_mode_repaired(self):
  p={'visualState':{'hiddenProperties_!!!_kpiControls':json.dumps({'variance':{'showVariance':False},'title':{'style':{'color':'#123456'}}})}}
  fixed=complete_card_state(p);k=json.loads(fixed['visualState']['hiddenProperties_!!!_kpiControls'])
  self.assertEqual(fixed['chartType'],'CARD');self.assertIn('color',k['variance']['style'])
  self.assertEqual(k['title']['style']['color'],'#123456');self.assertIn('prefix',k['title'])
  self.assertNotIn('chartType',p);self.assertEqual(complete_card_state(fixed),fixed)
 def test_filter_position_enum_and_context_preservation(self):
  self.assertEqual(sheet_properties()['properties']['filterPanePosition'],'RIGHT')
  context={'isContextDimension':True,'pivotAssignments':[{'id':'Scenario[Name]'}],'filter':[{'value':'Budget'}]}
  a={'id':'Region[Name]','columnName':'Name','sourceType':'PowerBI','columnType':'Column','bucketId':'rows','dataRoleType':'Grouping','dataType':'Text'}
  p={'pivotAssignments':[a],'superFilterAssignments':[copy.deepcopy(context)]}
  ensure_axis_filters(p);ensure_axis_filters(p)
  self.assertEqual(len(p['superFilterAssignments']),2);self.assertEqual(p['superFilterAssignments'][0],context)
  self.assertEqual(p['superFilterAssignments'][1]['position'],'RIGHT')
  self.assertNotIn('isContextDimension',p['superFilterAssignments'][1])
