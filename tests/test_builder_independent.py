"""Synthetic workforce extension contract tests. No network, UI, or old report."""
import base64
import copy
import os
from pathlib import Path
import shutil
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.codec import loads
from runtime.home_api import decode_roles
from runtime.input_factories import input_create, metadata
from runtime.powertable_factory import row_save
from runtime.rule_factories import distribute_rows, min_max, new_rule

TOKEN_ENV = 'FABRIC_PLAN_BUILDER_TEST_TOKEN'


def comment_payload():
    return input_create('501', 'Manager Comment', 'LongText',
        {'maximum_length': 2000, 'allow_entry_on_totals_or_subtotals': False}, '',
        measures={'canEdit': '401'}, context_bound=False,
        allow_input={'BasedOnFormula': '${canEdit} > 0'})


def native_page():
    return {'statusCode': 200, 'payload': {'etag': 'page-1',
        'properties': {'properties': {'canvasStyle': {'dimension': {
            'width': 1000, 'height': 800, 'elementScalingUnit': 'pixel'}},
            'reactiveVisualProperties': [], 'unrelatedPageState': {'keep': True}}},
        'visuals': [{'id': '101', 'visualType': 80, 'properties': {'etag': 'owner-1',
            'properties': {'position': {'x': 20, 'y': 180}, 'dimension': {'width': 560, 'height': 280},
                           'visualState': {'unrelatedInputState': 'keep'}}}}]}}


class IndependentBuilderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        (self.directory / 'temp').mkdir()
        env = patch.dict(os.environ, {TOKEN_ENV: 'synthetic-builder-token',
            'TEMP': str(self.directory / 'temp'), 'TMP': str(self.directory / 'temp')})
        env.start(); self.addCleanup(env.stop)
        network = patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden'))
        network.start(); self.addCleanup(network.stop)

    def node(self):
        value = os.environ.get('FABRIC_PLAN_NODE') or shutil.which('node')
        if not value:
            self.skipTest('Optional Node runtime unavailable for LZUTF8')
        return value

    def salary_inputs(self):
        metadata_rows = [
            {'id': 'EmployeeId', 'dataType': 'int', 'isPrimaryKey': True, 'isNullable': False, 'isEditable': False},
            {'id': 'Salary', 'dataType': 'decimal', 'isNullable': False, 'isEditable': True},
            {'id': 'Department', 'dataType': 'nvarchar', 'isNullable': True, 'isEditable': True}]
        records = [{'Salary': '82000'}]
        conditions = [{'EmployeeId': '7'}]
        audit = {'rowIds': ['7'], 'oldRecords': [{'EmployeeId': '7', 'Salary': '80000', 'Department': 'Operations'}],
                 'updatedColumns': ['Salary'], 'optionsMeta': {}}
        return metadata_rows, records, conditions, audit

    def test_workforce_typed_inputs_keep_exact_native_contracts(self):
        comment = comment_payload()
        checkbox = input_create('502', 'Reviewed', 'Checkbox', {'default_value': {'Static': False}, 'edit_on_total': False}, '')
        option = {'display_name': 'Operations', 'value': 'D-OPS', 'color': '', 'icon': '', 'order': 0}
        settings = {'options_source': {'Static': [option]}, 'default_value': {'Static': option},
                    'allow_user_to_add_new_option': False, 'prevent_null': True}
        before = copy.deepcopy(settings)
        department = input_create('503', 'Department', 'SingleSelect', settings, '')
        self.assertEqual([p['columnType'] for p in (comment, checkbox, department)], [101, 11, 2])
        self.assertEqual(comment['boundToFilterContext'], 20)
        self.assertEqual(comment['columnMeta']['measure_type']['DataInput']['allow_input'], {'BasedOnFormula': 'M_401 > 0'})
        self.assertEqual(checkbox['columnMeta']['data_type'], 'Boolean')
        self.assertEqual(department['columnMeta']['measure_type']['DataInput']['column_type']['SingleSelect']['default_value'], {'Static': option})
        self.assertEqual(settings, before)

    def test_text_default_cannot_violate_minimum_length(self):
        with self.assertRaises(ValueError):
            metadata('LongText', {'minimum_length': 10, 'default_value': {'Static': 'x'}})

    def test_picklist_unknown_default_rejects(self):
        option = {'display_name': 'Operations', 'value': 'D-OPS', 'color': '', 'icon': '', 'order': 0}
        other = {**option, 'value': 'D-OTHER'}
        with self.assertRaises(ValueError):
            metadata('SingleSelect', {'options_source': {'Static': [option]}, 'default_value': {'Static': other}})

    def test_bounded_allocation_uses_separate_rules_and_preserves_inputs(self):
        weights = {'701': 0.6, '702': 0.4}
        allocation = new_rule('801', 'Allocate by team weights',
            distribute_rows('ManualInput', ['601'], weights), measures={'SelectedMeasures': ['401']})
        bounds = new_rule('802', 'Capacity bounds', min_max({'Static': {'value': 0}}, {'Static': {'value': 200}}),
                          measures={'SelectedMeasures': ['401']})
        self.assertEqual(allocation['ruleOperation']['New']['rule_type']['Distribute']['operation']['Row']['reference'], {'ManualInput': {'weights': weights}})
        self.assertEqual(bounds['ruleOperation']['New']['measures'], {'SelectedMeasures': ['401']})
        self.assertEqual(weights, {'701': 0.6, '702': 0.4})
        with self.assertRaises(ValueError): distribute_rows('ManualInput', weights={'701': 0})
        with self.assertRaises(ValueError): min_max({'Static': {'value': 200}}, {'Static': {'value': 0}})
    def test_salary_update_encoding_preserves_key_and_unrelated_values(self):
        meta, records, conditions, visual_meta = self.salary_inputs()
        original = copy.deepcopy((meta, records, conditions, visual_meta))
        payload = row_save(meta, 'update', records, conditions=conditions, visual_meta=visual_meta, node=self.node())
        inner = decode_roles(payload['data'], self.node())['updateData']
        self.assertEqual(inner['records'], [{'Salary': '82000'}])
        self.assertEqual(inner['conditions'], [{'EmployeeId': '7'}])
        self.assertEqual(inner['visualMeta']['oldRecords'][0]['Department'], 'Operations')
        self.assertEqual((meta, records, conditions, visual_meta), original)
        self.assertEqual(payload['actions'], ['update'])
        # The supplied section 6.5 explicitly documents these empty serializer
        # arrays. Their shape is valid when no selected audit profile requires more.
        example_meta = [
            {'id': 'Id', 'dataType': 'int', 'isPrimaryKey': True, 'isNullable': False, 'isEditable': False},
            {'id': 'Amount', 'dataType': 'decimal', 'isPrimaryKey': False, 'isNullable': True, 'isEditable': True}]
        insert = row_save(example_meta, 'insert', [['1250']], generated_keys=['Id'],
                          visual_meta={'rowIds': [], 'optionsMeta': {}}, node=self.node())
        self.assertEqual(decode_roles(insert['data'], self.node())['createData'],
                         {'records': [['1250']], 'visualMeta': {'rowIds': [], 'optionsMeta': {}}})
        update = row_save(example_meta, 'update', [{'Amount': '1300'}], conditions=[{'Id': '42'}],
            visual_meta={'rowIds': ['42'], 'oldRecords': [], 'updatedColumns': ['Amount'], 'optionsMeta': {}}, node=self.node())
        self.assertEqual(decode_roles(update['data'], self.node())['updateData']['visualMeta']['oldRecords'], [])

    def test_salary_update_rejects_invalid_known_key_and_audit_shapes(self):
        mutations = [
            ('rowIds string', lambda r, c, v: v.update(rowIds='7')),
            ('optionsMeta null', lambda r, c, v: v.update(optionsMeta=None)),
            ('oldRecords null', lambda r, c, v: v.update(oldRecords=None)),
            ('structured key', lambda r, c, v: c[0].update(EmployeeId={'not': None})),
            ('null nonnullable salary', lambda r, c, v: r[0].update(Salary=None))]
        for name, mutate in mutations:
            with self.subTest(case=name):
                meta, records, conditions, visual_meta = self.salary_inputs()
                mutate(records, conditions, visual_meta)
                with self.assertRaises(ValueError):
                    row_save(meta, 'update', records, conditions=conditions, visual_meta=visual_meta, node=self.node())

if __name__ == '__main__':
    unittest.main()
