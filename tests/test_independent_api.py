"""Independent API regressions: mocks only, portable paths, synthetic data."""
import copy
import json
import os
from pathlib import Path
import runpy
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.codec import load, loads, pack, unpack
from runtime.home_api import decode_roles
from runtime.identity import Registry
from runtime.layout import audit, verify_unchanged
from runtime.pivots import compile_pivots
from runtime.transport import Client
from runtime.workflow import preflight, provision

TOKEN_ENV = 'FABRIC_PLAN_INDEPENDENT_TEST_TOKEN'


def rectangle(x=20, y=20, width=200, height=100):
    return {'position': {'x': x, 'y': y}, 'dimension': {'width': width, 'height': height}}


def native_page():
    state = {'pivot': {'configs': [{'id': '301', 'name': 'Summary', 'hidden': False}], 'active_id': None},
             'pivotExplorer': {'activePivot': None}, 'manage_measures': [{'id': '401'}]}
    props = {**rectangle(), 'visualState': state, 'pivotAssignments': []}
    return {'statusCode': 200, 'payload': {'etag': 'page-1',
        'properties': {'properties': {'canvasStyle': {'dimension': {
            'width': 600, 'height': 500, 'elementScalingUnit': 'pixel'}},
            'pageFilter': 'preserve', 'reactiveVisualProperties': []}},
        'visuals': [{'id': '101', 'visualType': 80,
                     'properties': {'etag': 'visual-1', 'properties': props}}]}}


class WorkflowServer:
    def __init__(self, mutate_policy=False, create_lro=False, update_lro=False, lose_update=False):
        self.raw = {'definition.json': {'sheets': [], 'serverUnknownInitialization': {'retainMe': True}},
                    'planProperties.json': {'properties': {'serverUnknownDefault': 'retain-me'}}}
        self.creates = self.updates = 0
        self.mutate_policy, self.create_lro = mutate_policy, create_lro
        self.update_lro, self.lose_update = update_lro, lose_update
        self.expired_create = self.expired_update = False

    def public(self, method, url, headers, body):
        if method == 'POST' and url.endswith('/plans'):
            self.creates += 1
            self.raw=unpack(loads(body.decode('utf-8')))
            if self.create_lro:
                return self.pending('create')
            payload = {'id': 'synthetic-plan'}
        elif '/operations/create' in url:
            if self.expired_create:
                return {'status': 410, 'headers': {}, 'body': {'error': 'Expired operation'}}
            payload = {'id': 'synthetic-plan'} if url.endswith('/result') else {'status': 'Succeeded'}
        elif '/operations/update' in url:
            if self.expired_update:
                return {'status': 410, 'headers': {}, 'body': {'error': 'Expired operation'}}
            payload = {} if url.endswith('/result') else {'status': 'Succeeded'}
        elif url.endswith('/getDefinition'):
            payload = pack(self.raw)
        elif url.endswith('/updateDefinition'):
            self.updates += 1
            self.raw = unpack({'definition': loads(body.decode('utf-8'))['definition']})
            if self.mutate_policy:
                path = next(p for p in self.raw if p.endswith('/dataInput.json'))
                record = next(c for c in self.raw[path]['columns'] if 'DataInput' in c['columnMeta']['measure_type'])
                record['columnMeta']['measure_type']['DataInput']['allow_input'] = 'Edit'
            if self.lose_update:
                self.lose_update = False
                raise OSError('Simulated response loss after update applied')
            if self.update_lro:
                return self.pending('update')
            payload = {}
        else:
            raise AssertionError('Unexpected mocked route: ' + url)
        return {'status': 201 if url.endswith('/plans') else 200, 'headers': {}, 'body': payload}

    @staticmethod
    def pending(operation):
        return {'status': 202, 'headers': {
            'location': 'https://api.fabric.microsoft.com/v1/operations/' + operation, 'retry-after': '0'}, 'body': {}}

class IndependentApiTests(unittest.TestCase):
    def test_model_cli_discovers_tmdl_twice_without_recipe_or_native_flag(self):
        import base64
        from contextlib import redirect_stdout
        from io import StringIO

        api = 'https://api.fabric.microsoft.com/v1'
        config = self.directory / 'destination.json'
        config.write_text(json.dumps({'apiBase': api, 'tokenEnvironment': TOKEN_ENV,
            'modelReference': {'semanticModelWorkspaceId': 'workspace', 'semanticModelId': 'model'}}))
        run = self.directory / 'discovery'
        model_route = api + '/workspaces/workspace/semanticModels/model'
        definition = model_route + '/getDefinition?format=TMDL'
        operations = []
        tmdl = "table 'Sales Data'\n\tcolumn Country\n\t\tdataType: string\n\tmeasure 'Gross Revenue' = 1\n\t\tformatString: #,0\n"
        envelope = {'definition': {'parts': [{'path': 'definition/tables/Sales Data.tmdl',
            'payloadType': 'InlineBase64', 'payload': base64.b64encode(tmdl.encode()).decode()}]}}

        def respond(client, method, url, headers, body):
            status, metadata = 200, {}
            if (method, url) == ('GET', model_route):
                payload = {'displayName': 'Sales model'}
            elif (method, url) == ('POST', definition):
                operations.append(api + '/operations/' + str(len(operations) + 1))
                status, metadata, payload = 202, {'location': operations[-1], 'retry-after': '0'}, {}
            elif method == 'GET' and url in operations:
                payload = {'status': 'Succeeded'}
            elif method == 'GET' and url == operations[-1] + '/result':
                payload = envelope
            else:
                self.fail(f'Unexpected discovery request: {method} {url}')
            return {'status': status, 'headers': metadata, 'body': payload}

        argv = ['plan.py', 'usecase', 'model', '--config', str(config), '--run', str(run)]
        with patch.object(sys, 'argv', argv), patch.object(Client, '_http', respond), redirect_stdout(StringIO()):
            for _ in range(2):
                runpy.run_path(str(ROOT / 'plan.py'), run_name='__main__')
        self.assertEqual(len(operations), 2)
        model = load(run / 'current-model.json')
        self.assertEqual(model['reference']['semanticModelName'], 'Sales model')
        self.assertEqual([(f['id'], f['dataType']) for f in model['fields']],
                         [('Sales Data[Country]', 'String'), ('Sales Data[Gross Revenue]', 'Double')])
        self.assertEqual(load(run / 'model-definition.json'), envelope)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        (self.directory / 'temp').mkdir()
        env = patch.dict(os.environ, {TOKEN_ENV: 'synthetic-test-token',
            'TEMP': str(self.directory / 'temp'), 'TMP': str(self.directory / 'temp')})
        env.start()
        self.addCleanup(env.stop)
        self.network = patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden'))
        self.network.start()
        self.addCleanup(self.network.stop)

    def test_orphan_override_is_not_a_complete_inventory(self):
        page = native_page()
        page['payload']['properties']['properties']['reactiveVisualProperties'] = [
            {'visualId': '102', 'properties': rectangle()}]
        with self.assertRaisesRegex(ValueError, 'Orphan'):
            audit(page)

    def test_unrelated_page_property_drift_fails_readback(self):
        before = native_page()
        after = copy.deepcopy(before)
        after['payload']['properties']['properties']['pageFilter'] = 'unexpected change'
        with self.assertRaisesRegex(ValueError, 'Unrelated page'):
            verify_unchanged(before, after, '101', {'x': 20, 'y': 20, 'width': 200, 'height': 100})

    def test_false_string_does_not_enable_cross_axis_capability(self):
        sheet = {'sheetId': 'sheet', 'rows': ['Employee'], 'columns': ['Month'],
            'dimensions': {'Employee': '501', 'Month': '502'}, 'measures': {'Hours': '503'}}
        with self.assertRaisesRegex(ValueError, 'Boolean'):
            compile_pivots([{'name': 'Swap', 'rows': ['Month'], 'columns': ['Employee']}], sheet, Registry(),
                capabilities={'PlanningCrossPivot': 'false', 'PlanningColumnPivot': 'false'})

    def test_compressed_roles_preserve_unicode_and_u64(self):
        node = os.environ.get('FABRIC_PLAN_NODE') or shutil.which('node')
        if not node:
            self.skipTest('Optional Node runtime unavailable for LZUTF8 test')
        text = '{"__everyone__":{"title":"R\u00e9sum\u00e9 \u2013 \u6d4b\u8bd5","runtimeId":18446744073709551615}}'
        program = "const fs=require('node:fs');const lz=require(process.argv[1]);process.stdout.write(lz.compress(fs.readFileSync(0,'utf8'),{outputEncoding:'Base64'}));"
        compressed = subprocess.run([node, '-e', program, str(ROOT / 'vendor/lzutf8/lzutf8.js')],
            input=text.encode('utf-8'), capture_output=True, check=True, timeout=30).stdout.decode('ascii')
        self.assertEqual(decode_roles(compressed, node), json.loads(text))

class WorkflowRegressionTests(unittest.TestCase):
    setUp = IndependentApiTests.setUp

    def inputs(self):
        model = load(ROOT / 'fixtures/model.json')
        spec = {'name': 'Synthetic Capacity', 'requiredCapabilities': [
            'planning.numeric', 'planning.native-measure', 'planning.conditional-edit-policy'],
            'sheets': [{'name': 'Capacity', 'rows': ['Employee[Employee]'], 'columns': ['Period[Month]'],
                'measures': [
                    {'key': 'allowed', 'kind': 'Native', 'source': 'Metrics[CanEdit]', 'label': 'CanEdit'},
                    {'key': 'hours', 'kind': 'DataInput', 'label': 'Available Hours',
                     'min_value': {'Static': 0}, 'allow_input': {'BasedOnFormula': '${allowed} > 0'}}]}]}
        config = {'apiBase': 'https://api.fabric.microsoft.com/v1',
            'workspaceId': 'workspace', 'name': spec['name'], 'tokenEnvironment': TOKEN_ENV, 'authorizedMutation': True}
        return config, model, spec

    def run_workflow(self, server, directory):
        config, model, spec = self.inputs()
        def client(base, env, allowed=None, journal=None):
            return Client(base, env, allowed, journal, server.public, sleep=lambda seconds: None)
        with patch('runtime.workflow.Client', client):
            return provision(config, model, spec, directory)

    def test_public_create_contains_visibility_and_complete_grid(self):
        server = WorkflowServer()
        self.run_workflow(server, self.directory / 'create')
        flags = {s['sheetType']:s['isHidden'] for s in server.raw['definition.json']['sheets']}
        self.assertEqual(flags, {'PLANNING':True, 'REPORTING':False})
        self.assertTrue(server.raw['planProperties.json']['properties']['homeLayout']['show'])
        records = next(v['columns'] for k,v in server.raw.items() if k.endswith('/dataInput.json'))
        rule = next(c['columnMeta']['measure_type']['DataInput'] for c in records
                    if 'DataInput' in c['columnMeta']['measure_type'])
        self.assertIsInstance(rule['allow_input'], dict)
        self.assertEqual((server.creates, server.updates), (1, 0))

    def test_completed_create_resume_does_not_recreate_or_publish(self):
        server = WorkflowServer(create_lro=True)
        directory = self.directory / 'create-expiry'
        self.run_workflow(server, directory)
        server.expired_create = True
        self.run_workflow(server, directory)
        self.assertEqual((server.creates, server.updates), (1, 0))

    def test_public_create_reports_role_specific_home_gap(self):
        server = WorkflowServer()
        result = self.run_workflow(server, self.directory / 'public-only')
        self.assertEqual(result['home']['visibility'], 'public-create')
        self.assertEqual(result['home']['content'], 'constructed-locally-not-published')
        self.assertEqual(result['phaseErrors'][0]['status'], 'unsupported')
        self.assertFalse(result['originalScopeComplete'])
        self.assertEqual(result['dashboards'][0]['geometrySource'], 'public-create')

    def test_hidden_dashboard_is_rejected_before_create(self):
        from runtime.application_defaults import require_business_navigation
        raw = {'definition.json': {'sheets': [
            {'sheetType':'REPORTING','displayName':'Revenue','isHidden':True}]}}
        with self.assertRaisesRegex(ValueError,'public create'):
            require_business_navigation(raw)

    def test_invalid_home_controls_fail_preflight(self):
        for bad in ({'order': -1}, {'order': True}, {'show': 'false'}, {'roleId': ''}):
            with self.subTest(control=bad):
                _, _, spec = self.inputs()
                spec['requiredCapabilities'] += ['home.text', 'home.visibility']
                spec['home'] = {'blocks': [{'key': 'intro', 'type': 'text', 'title': 'Capacity'}],
                    'rows': [{'blocks': ['intro']}], **bad}
                with self.assertRaises(ValueError):
                    preflight(spec)


if __name__ == '__main__':
    unittest.main()
