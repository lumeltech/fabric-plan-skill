import unittest,copy
from runtime.reference_views import audit,audit_native_capture
from runtime.page_parameters import number_parameter
from runtime.transport import HttpError

def sample():
    visual=lambda vid,embedded=False:{'visualId':vid,'visualType':'PLANNING','isEmbedded':embedded}
    return {'definition.json':{'sheets':[
      {'recordGuid':'owner','displayName':'Plan','sheetType':'PLANNING','workloadItemEntityVisuals':[visual('grid')]},
      {'recordGuid':'dashboard','displayName':'Review','sheetType':'REPORTING','workloadItemEntityVisuals':[visual('grid',True)]}]},
      'sheets/owner/visuals/grid/properties.json':{'properties':{'visualState':{}}},
      'sheets/dashboard/sheet.json':{'properties':{'entityLevelVariables':[{'id':'CALC_VARIABLE_x','type':'number','scope':'entity'}]}},
      'planProperties.json':{'properties':{'homeLayout':{'roles':[]},'bookmarks':[
        {'name':'Detail','bookmarkSlug':'B','cloudMeta':{'bookmarkMeta':{'bookmarkSlug':'B','activePageId':'dashboard',
          'activeSelection':['grid'],'entityLevelVariables':[]},'bookmarkVisualMeta':{'grid':{'manage_measures':[{'label':'Revenue'}]}}}}]}}}

class ReferenceViews(unittest.TestCase):
    def test_hidden_owner_shared_embed(self):
        r=audit(sample());self.assertEqual(r['dashboards'][0]['embeddedOwners'],[{'visualId':'grid','ownerPage':'Plan'}])
    def test_export_missing_roles_is_not_missing_home(self):
        r=audit(sample(),home_roles={'__everyone__':{'homeLayoutEnabled':True}},home_contents={'__everyone__':{'data':{'items':[{}],'rows':[{}]},'etag':'e'}})
        self.assertEqual(r['home']['exportedRoles'],0);self.assertEqual(r['home']['roles'][0]['items'],1)
        self.assertIsNone(r['home']['exportedShow'])
    def test_new_parameters_not_assumed_in_old_bookmarks(self):
        r=audit(sample());self.assertEqual(r['warnings'][0]['parameterIds'],['CALC_VARIABLE_x'])
    def test_orphan_bookmark_fails(self):
        r=sample();r['planProperties.json']['properties']['bookmarks'][0]['cloudMeta']['bookmarkVisualMeta']['bad']={}
        with self.assertRaisesRegex(ValueError,'unresolved'):audit(r)
    def test_unresolved_embed_fails(self):
        r=sample();r['definition.json']['sheets'][1]['workloadItemEntityVisuals'][0]['visualId']='absent'
        with self.assertRaisesRegex(ValueError,'owner'):audit(r)
    def test_native_capture_rejects_export_label_only(self):
        p={'payload':{'visuals':[{'id':'7','properties':{'properties':{'visualState':{'manage_measures':[{'id':'22'}]}}}}]}}
        capture={'bookmarkVisualMeta':{'7':{'manage_measures':[{'label':'Revenue'}]}}}
        with self.assertRaisesRegex(ValueError,'native measure IDs'):audit_native_capture(capture,p)
        capture['bookmarkVisualMeta']['7']['manage_measures'][0]['id']='22'
        self.assertEqual(audit_native_capture(capture,p)['identityCheck'],'passed')
    def test_parameter_fresh_identity_and_zero(self):
        a=number_parameter('Rate','rate');b=number_parameter('Rate','rate')
        self.assertNotEqual(a['entityVariable']['id'],b['entityVariable']['id'])
        self.assertEqual(a['entityVariable']['id'],a['visualGlobalVariable']['id'])
        self.assertEqual(a['calculatedVariable']['value'],0)
        self.assertFalse(a['entityVariable']['showAsPercentage'])
    def test_parameter_constraints(self):
        for value in (True,float('nan'),float('inf'),0.2):
            with self.assertRaises(ValueError):number_parameter('Rate','rate',value)
        self.assertEqual(number_parameter('Rate','rate',0.2,allow_decimal=True)['entityVariable']['value'],0.2)
    def test_parameter_names(self):
        with self.assertRaises(ValueError):number_parameter('Rate','two words')
        with self.assertRaises(ValueError):number_parameter('Rate','rate',parameter_id='reused-guid')

if __name__=='__main__':unittest.main()
