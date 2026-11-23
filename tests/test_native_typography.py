import unittest,copy,json
from unittest.mock import patch
from runtime.application_typography import normalize_arial,font_issues

class NativeTypographyTests(unittest.TestCase):
    def test_expanded_boundaries_preserve_data(self):
        p={'formula':'{"fontFamily":"Consolas"}','pivotAssignments':[{'id':'field'}],
           'visualState':{'manage_measures':[], 'title':'{"style":"font-family: Calibri; color: red"}',
             'hiddenProperties_!!!_appearance':json.dumps({'charts':{'fontFamily':'Segoe UI'},'other':7}),
             'formatConfig':{'measure':{'m':[{'format':{'4':'Calibri','3':'red'},'order':1}]}},
             'formula':'["fontFamily"]', 'random':'{"fontFamily":"keep"}'}}
        before=copy.deepcopy(p);out=normalize_arial(p)
        self.assertEqual(p,before);self.assertEqual(out['formula'],p['formula'])
        self.assertEqual(out['pivotAssignments'],p['pivotAssignments'])
        self.assertEqual(out['visualState']['random'],p['visualState']['random'])
        self.assertEqual(out['visualState']['formatConfig']['measure']['m'][0]['format']['3'],'red')
        self.assertFalse(font_issues(out['visualState']))
        self.assertEqual(normalize_arial(out),out)
