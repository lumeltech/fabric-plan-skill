"""Plan item operations through the journaled public client; no sockets."""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from runtime.codec import save
from runtime.transport import Client, plan_operation

BASE = 'https://api.fabric.microsoft.com/v1'
PLANS = BASE + '/workspaces/w/plans'


def ok(body=None, status=200):
    return {'status': status, 'headers': {}, 'body': body}


NOT_FOUND = {'status': 404, 'headers': {}, 'body': {'errorCode': 'ItemNotFound'}}


class PlanItemTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        os.environ['TEST_TOKEN'] = 'mock-secret'
        self.calls = []

    def client(self, responses):
        def adapter(method, url, headers, body):
            self.calls.append((method, url, json.loads(body) if body else None))
            return responses.pop(0)
        return Client(BASE, 'TEST_TOKEN', journal=self.tmp.name, adapter=adapter, sleep=lambda t: None)

    def test_list_follows_every_page(self):
        c = self.client([ok({'value': [{'id': 'a'}], 'continuationUri': PLANS + '?continuationToken=t'}),
                         ok({'value': [{'id': 'b'}]})])
        result = plan_operation(c, 'w', 'list')
        self.assertEqual(result['body']['value'], [{'id': 'a'}, {'id': 'b'}])
        self.assertEqual([(m, u) for m, u, _ in self.calls], [('GET', PLANS), ('GET', PLANS + '?continuationToken=t')])

    def test_get_reads_plan_metadata(self):
        c = self.client([ok({'id': 'p', 'displayName': 'Budget'})])
        self.assertEqual(plan_operation(c, 'w', 'get', 'p')['body']['displayName'], 'Budget')
        self.assertEqual(self.calls, [('GET', PLANS + '/p', None)])
        with self.assertRaises(ValueError):
            plan_operation(c, 'w', 'get')

    def test_rename_patches_only_supplied_properties(self):
        c = self.client([ok({'id': 'p'})])
        plan_operation(c, 'w', 'rename', 'p', name='Budget 2027', description='Annual budget', label='rename')
        self.assertEqual(self.calls, [('PATCH', PLANS + '/p', {'displayName': 'Budget 2027', 'description': 'Annual budget'})])
        for kwargs in ({}, {'name': ''}, {'name': 7}, {'description': 'x' * 257}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                plan_operation(c, 'w', 'rename', 'p', label='bad', **kwargs)
        self.assertEqual(len(self.calls), 1)

    def test_delete_confirms_the_target_then_verifies_absence(self):
        c = self.client([ok({'id': 'p', 'displayName': 'Budget'}), ok(), NOT_FOUND])
        result = plan_operation(c, 'w', 'delete', 'p', name='Budget', confirm_plan_id='p', label='delete')
        self.assertEqual([(m, u) for m, u, _ in self.calls],
                         [('GET', PLANS + '/p'), ('DELETE', PLANS + '/p'), ('GET', PLANS + '/p')])
        self.assertIs(result['verifiedAbsent'], True)

    def test_only_item_not_found_proves_absence(self):
        cases = [(ok({'id': 'p', 'displayName': 'Budget'}), False),
                 ({'status': 404, 'headers': {}, 'body': {'errorCode': 'WorkspaceNotFound'}}, None),
                 ({'status': 404, 'headers': {}, 'body': None}, None),
                 ({'status': 403, 'headers': {}, 'body': {'errorCode': 'InsufficientPrivileges'}}, None)]
        for index, (check, expected) in enumerate(cases):
            with self.subTest(check=check):
                c = self.client([ok({'id': 'p', 'displayName': 'Budget'}), ok(), check])
                result = plan_operation(c, 'w', 'delete', 'p', name='Budget', confirm_plan_id='p', label='delete-' + str(index))
                self.assertIs(result['verifiedAbsent'], expected)

    def test_delete_refuses_an_unconfirmed_or_mismatched_target(self):
        c = self.client([ok({'id': 'p', 'displayName': 'Other'})])
        for kwargs in ({'name': 'Budget'}, {'name': 'Budget', 'confirm_plan_id': 'q'}, {'confirm_plan_id': 'p'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                plan_operation(c, 'w', 'delete', 'p', label='delete', **kwargs)
        self.assertEqual(self.calls, [])
        with self.assertRaisesRegex(ValueError, 'display name'):
            plan_operation(c, 'w', 'delete', 'p', name='Budget', confirm_plan_id='p', label='delete')
        self.assertEqual([m for m, _, _ in self.calls], ['GET'])

    def test_resumed_delete_replays_the_journal_without_a_second_delete(self):
        c = self.client([ok({'id': 'p', 'displayName': 'Budget'}), ok(), NOT_FOUND, NOT_FOUND])
        plan_operation(c, 'w', 'delete', 'p', name='Budget', confirm_plan_id='p', label='delete')
        result = plan_operation(c, 'w', 'delete', 'p', name='Budget', confirm_plan_id='p', label='delete')
        self.assertEqual([m for m, _, _ in self.calls], ['GET', 'DELETE', 'GET', 'GET'])
        self.assertIs(result['verifiedAbsent'], True)


class PlanItemCommandTests(unittest.TestCase):
    def run_api(self, action, config):
        import plan
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'destination.json'
            save(destination, {'apiBase': BASE, 'tokenEnvironment': 'TEST_TOKEN', 'workspaceId': 'w', **config})
            argv = ['scripts/plan.py', 'api', action, '--config', str(destination), '--run', str(Path(directory) / 'run'),
                    '--label', action]
            with patch.object(sys, 'argv', argv), patch('runtime.transport.Client'), \
                    patch('runtime.transport.plan_operation', return_value={'status': 200, 'body': {}}) as operation, \
                    redirect_stdout(io.StringIO()):
                plan.main()
            return operation.call_args

    def test_reads_need_no_mutation_authorization(self):
        for action in ('list', 'get'):
            with self.subTest(action=action):
                self.assertEqual(self.run_api(action, {'planId': 'p'}).args[2], action)

    def test_rename_and_delete_need_authorization_but_no_payload(self):
        for action in ('rename', 'delete'):
            with self.subTest(action=action):
                with self.assertRaisesRegex(ValueError, 'authorizedMutation'):
                    self.run_api(action, {'planId': 'p', 'name': 'Budget'})
                call = self.run_api(action, {'planId': 'p', 'name': 'Budget', 'description': 'Annual',
                                             'confirmDeletePlanId': 'p', 'authorizedMutation': True})
                self.assertEqual((call.args[2], call.kwargs['description'], call.kwargs['confirm_plan_id']),
                                 (action, 'Annual', 'p'))


if __name__ == '__main__':
    unittest.main()
