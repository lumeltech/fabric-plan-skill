"""Independent tests of useful partial provisioning; mocked APIs only."""
import copy
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from runtime.codec import load,pack,unpack
from runtime.scope import prepare_scope
from runtime.workflow import SUPPORTED,provision,preflight

ROOT=Path(__file__).resolve().parents[1]

def model():return load(ROOT/'fixtures/model.json')
def base_sheet():
    return {'name':'Workforce','rows':['Employee[Employee]'],'columns':['Period[Month]'],
        'measures':[{'key':'base','kind':'Native','label':'Base','source':'Metrics[BasePay]'},
                    {'key':'input','kind':'DataInput','label':'Plan','default_value':{'Measure':'base'}},
                    {'key':'result','kind':'Formula','label':'Result','formula':'${input} * 1.1'}]}
def spec():
    return {'name':'Synthetic Partial App','requiredCapabilities':['planning.native-measure','planning.numeric','planning.formula'],
            'sheets':[base_sheet()]}

class IndependentScopeTests(unittest.TestCase):
    def test_unsupported_measure_removes_only_its_dependency_chain(self):
        request=spec();s=request['sheets'][0]
        s['measures'] += [{'key':'text','kind':'DataInput','inputKind':'Text','label':'Comment'},
                         {'key':'bad1','kind':'Formula','label':'Dependent','formula':'${text}'},
                         {'key':'bad2','kind':'Formula','label':'Dependent twice','formula':'${bad1}'}]
        before=copy.deepcopy(request);scope=prepare_scope(request,SUPPORTED,model())
        self.assertEqual(request,before)
        self.assertEqual([m['key'] for m in scope['spec']['sheets'][0]['measures']],['base','input','result'])
        self.assertFalse(scope['completeOriginalScope']);preflight(scope['spec'])

    def test_measure_hierarchy_uses_recorded_flat_alternative(self):
        request=spec();request['sheets'][0]['measureModelConfig']={'requested':'tree'}
        scope=prepare_scope(request,SUPPORTED,model())
        self.assertEqual(len(scope['spec']['sheets'][0]['measures']),3)
        self.assertNotIn('measureModelConfig',scope['spec']['sheets'][0])
        self.assertTrue(any(r['status']=='alternative' and r['path'].endswith('measureModelConfig') for r in scope['coverage']))

    def test_unknown_control_capability_preserves_readonly_data(self):
        request=spec();request['requiredCapabilities'].append('planning.approval-locking')
        scope=prepare_scope(request,SUPPORTED,model())
        self.assertEqual([m['key'] for m in scope['spec']['sheets'][0]['measures']],['base'])

    def test_top_level_omitted_control_cannot_leave_editable_inputs(self):
        request=spec();request['security']={'inputAccess':'approved-only'}
        scope=prepare_scope(request,SUPPORTED,model())
        self.assertNotIn('DataInput',[m['kind'] for s in scope['spec']['sheets'] for m in s['measures']])

    def test_measure_level_omitted_control_cannot_leave_editable_input(self):
        request=spec();request['sheets'][0]['measures'][1]['approvalRequired']=True
        scope=prepare_scope(request,SUPPORTED,model())
        self.assertNotIn('input',[m['key'] for s in scope['spec']['sheets'] for m in s['measures']])
        self.assertNotIn('result',[m['key'] for s in scope['spec']['sheets'] for m in s['measures']])

    def test_invalid_sheet_does_not_remove_independent_sheet(self):
        request=spec();bad=base_sheet();bad['name']='Missing source';bad['rows']=['Absent[Name]'];request['sheets'].append(bad)
        scope=prepare_scope(request,SUPPORTED,model())
        self.assertEqual([s['name'] for s in scope['spec']['sheets']],['Workforce'])

    def test_home_image_becomes_explicit_native_text(self):
        request=spec();request['home']={'blocks':[{'key':'hero','type':'image','title':'Make decisions','description':'Plan together'},
            {'key':'unused','type':'unsupported'}], 'rows':[{'blocks':['hero','unused'],'widths':[70,30]}]}
        scope=prepare_scope(request,SUPPORTED,model());home=scope['spec']['home']
        self.assertEqual(home['blocks'],[{'key':'hero','type':'text','title':'Make decisions','description':'Plan together'}])
        self.assertEqual(home['rows'],[{'blocks':['hero']}]);self.assertFalse(scope['completeOriginalScope'])

    def test_removed_measure_selection_uses_default_pivot(self):
        request=spec();s=request['sheets'][0]
        s['measures'].append({'key':'unsupported','kind':'Forecast','label':'Unsupported'})
        s['pivots']=[{'name':'Picked','rows':['Employee[Employee]'],'measures':[{'key':'unsupported','aggregation':'Sum'}]}]
        s['activePivot']='Picked'
        scope=prepare_scope(request,SUPPORTED,model())
        self.assertNotIn('pivots',scope['spec']['sheets'][0]);self.assertNotIn('activePivot',scope['spec']['sheets'][0])

    def test_no_supported_data_leaves_remote_untouched(self):
        request=spec();request['sheets'][0]['measures']=[{'key':'only','kind':'Forecast','label':'Unsupported'}]
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as run, patch('runtime.workflow.Client') as client:
            result=provision({},model(),request,run)
            self.assertIsNone(result['planId']);self.assertEqual(result['mutation'],'none');client.assert_not_called()

    def test_provision_does_not_deploy_a_reduced_substitute_for_uncomposed_scope(self):
        request=spec();request['requiredCapabilities'].append('infobridge.connected-propagation')
        request['bridge']={'requested':'connected scenario'}
        server={'definition.json':{'sheets':[]},'planProperties.json':{'properties':{'retainedServerField':True}}}
        actions=[]
        def operation(client,workspace,action,plan_id=None,**kwargs):
            nonlocal server
            actions.append(action)
            if action=='create-blank':return {'body':{'id':'synthetic-new-plan'},'status':201}
            if action=='export':return {'body':pack(server),'status':200}
            if action=='update':server=unpack(kwargs['definition']);return {'body':{},'status':200}
            raise AssertionError(action)
        config={'authorizedMutation':True,'name':request['name'],'apiBase':'https://example.invalid/fabric',
            'workspaceId':'new-workspace','tokenEnvironment':'NO_TOKEN_USED'}
        with tempfile.TemporaryDirectory(dir=ROOT.parent) as run, patch('runtime.workflow.Client',return_value=object()), \
             patch('runtime.workflow.plan_operation',side_effect=operation):
            result=provision(config,model(),request,run)
            self.assertIsNone(result['planId']);self.assertEqual(actions,[])
            self.assertEqual(result['mutation'],'none');self.assertFalse(result['originalScopeComplete'])
            self.assertTrue((Path(run)/'scope-coverage.json').exists())
            self.assertFalse((Path(run)/'acceptance.json').exists())
            self.assertEqual(server['definition.json']['sheets'],[])

if __name__=='__main__':unittest.main()
