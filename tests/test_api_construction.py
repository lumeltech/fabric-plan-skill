import unittest,copy,os,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime.pivots import compile_pivots,select_pivot
from runtime.identity import Registry
from runtime.layout import inventory,placement_batch
from runtime.native import set_home_visibility
from runtime.transport import plan_operation,Client
from runtime.codec import loads
from test_runtime import page

class PivotTests(unittest.TestCase):
    def setUp(self):
        self.s={'sheetId':'sheet','rows':['Region','Employee'],'columns':['Month'],
            'dimensions':{'Region':'101','Employee':'102','Month':'103'},'measures':{'Cost':'104'}}
    def test_default_null_and_summary_axis(self):
        r=compile_pivots([{'key':'region','name':'Region','rows':['Region'],'columns':None}],self.s,Registry(),active='region')
        self.assertEqual(r['pivot']['configs'][0],{'id':'5880676360701185739','name':'All','row_dimensions':None,'col_dimensions':None,'measures':None,'hidden':False})
        self.assertEqual(r['pivot']['configs'][1]['row_dimensions'],['101']);self.assertIsNone(r['pivot']['configs'][1]['col_dimensions'])
        self.assertEqual(r['pivot']['active_id'],r['pivotExplorer']['activePivot'])
    def test_dimension_cannot_be_on_both_axes(self):
        with self.assertRaises(ValueError): compile_pivots([{'name':'Bad','rows':['Month']}],self.s,Registry(),capabilities={'PlanningCrossPivot':True,'PlanningColumnPivot':True})
    def test_cross_axis_gate_and_unknown(self):
        for axis in [['Month'],['Missing']]:
            with self.assertRaises(ValueError): compile_pivots([{'name':'Bad','rows':axis}],self.s,Registry())
    def test_hidden_active_rejected(self):
        with self.assertRaises(ValueError): compile_pivots([{'key':'x','name':'X','rows':[],'hidden':True}],self.s,Registry(),active='x')
    def test_null_and_empty_differ(self):
        r=compile_pivots([{'name':'Totals','rows':[]}],self.s,Registry());self.assertEqual(r['pivot']['configs'][1]['row_dimensions'],[])
        with self.assertRaises(ValueError): compile_pivots([{'name':'X'}],self.s,Registry())
    def test_selection_preserves_input_state(self):
        r=compile_pivots([{'name':'Region','rows':['Region']}],self.s,Registry());r['manage_measures']=[{'id':'104'}]
        before=copy.deepcopy(r);after=select_pivot(r,r['ids']['Region']);self.assertEqual(r,before);self.assertEqual(after['manage_measures'],before['manage_measures'])

class NewNativeTests(unittest.TestCase):
    def test_real_nested_visual_etag(self):
        p=page();v=p['payload']['visuals'][0];v['properties']['etag']=v.pop('etag')
        r=placement_batch(p,'page','nav',{'x':20,'y':20,'width':560,'height':80},inventory(p)['fingerprint'])
        self.assertEqual(r['etags']['visuals']['nav'],'nav-etag')
    def test_conflicting_etag_rejected(self):
        p=page();p['payload']['visuals'][0]['properties']['etag']='other'
        with self.assertRaises(ValueError): placement_batch(p,'page','nav',{'x':20,'y':20,'width':560,'height':80},inventory(p)['fingerprint'])
    def test_visibility_requires_bool(self):
        with self.assertRaises(ValueError): set_home_visibility({},'false')
    def test_public_home_visibility_preserves_existing_layout(self):
        from unittest.mock import patch
        from runtime.home_api import visibility_via_alm
        from runtime.codec import pack,unpack
        layout={'show':False,'roles':[{'id':'existing'}]}
        raw={'planProperties.json':{'properties':{'homeLayout':layout,'other':42}}}
        envelope=pack(raw)
        def operation(client, workspace, kind, plan, **kwargs):
            nonlocal envelope
            if kind=='update':
                envelope=kwargs['definition']
            else:
                self.assertEqual(kind,'export')
            return {'body':envelope}
        with patch('runtime.home_api.plan_operation',side_effect=operation):
            visibility_via_alm(None,'workspace','plan',True,'show-home')
        props=unpack(envelope)['planProperties.json']['properties']
        self.assertEqual(props,{'homeLayout':{**layout,'show':True},'other':42})
    def test_blank_create_has_no_definition(self):
        class Fake:
            def request(self,m,r,b,**k): self.body=b;return {'status':201,'body':{'id':'new'}}
            def finish(self,r,l): return r
        c=Fake();plan_operation(c,'workspace','create-blank',name='New',label='new');self.assertEqual(c.body,{'displayName':'New'})

if __name__=='__main__': unittest.main()
