"""Structural invariants validate_plan enforces before any write is attempted."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy, unittest
from pathlib import Path
from runtime.bridge import Query, planning_source, portable
from runtime.codec import load, loads, parts, unpack
from runtime.validate import measure_references, public_schema_view, validate_plan
from test_forecast_repair import envelope

ROOT = Path(__file__).resolve().parents[1]
BASE = envelope()
RAW = unpack(BASE)
DEFINITION = loads(parts(BASE)['definition.json'].decode('utf-8-sig'))
PAGE = DEFINITION['sheets'][0]['recordGuid']
VISUAL = next(v['visualId'] for v in DEFINITION['sheets'][0]['workloadItemEntityVisuals'] if not v.get('isEmbedded'))


def bookmark(slug, page=PAGE, meta_slug=None, visuals=None):
    return {'bookmarkSlug': slug, 'cloudMeta': {'bookmarkMeta': {'bookmarkSlug': meta_slug or slug, 'activePageId': page},
                                                'bookmarkVisualMeta': visuals or {}}}


class PlanStructure(unittest.TestCase):
    def raw(self):
        return copy.deepcopy(RAW)

    def test_forecast_plan_passes_structural_validation(self):
        report = validate_plan(self.raw())
        self.assertEqual((report['status'], report['sheets'], report['directVisuals']),
                         ('passed-structural-invariants', 2, 2))
        self.assertEqual(report['nativeRuntime'], 'not-run')

    def test_public_bookmarks_resolve_to_a_sheet_page_and_owned_visuals(self):
        raw = self.raw()
        raw['planProperties.json']['properties']['bookmarks'] = [bookmark('team-view'),
                                                                 {'bookmarkSlug': 'exec', 'cloudMeta':
                                                                     {'bookmarkMeta': {'bookmarkSlug': 'exec', 'activePageId': PAGE},
                                                                      'bookmarkVisualMeta': {VISUAL: {'visible': True}}}}]
        self.assertEqual(validate_plan(raw)['publicBookmarks'], 2)

    def test_bookmark_identity_and_page_are_refused(self):
        for label, records, message in [
            ('duplicate slug', [bookmark('x'), bookmark('x', meta_slug='z')], 'Invalid public bookmark identity/page'),
            ('renamed in cloud meta', [bookmark('x', meta_slug='y')], 'Invalid public bookmark identity/page'),
            ('unknown page', [bookmark('x', page='00000000-0000-4000-8000-000000000009')], 'Invalid public bookmark identity/page'),
            ('unowned visual', [bookmark('x', visuals={'ghost-visual': {}})], 'Bookmark visual unresolved'),
        ]:
            raw = self.raw()
            raw['planProperties.json']['properties']['bookmarks'] = records
            with self.subTest(case=label), self.assertRaisesRegex(ValueError, message):
                validate_plan(raw)

    def test_measure_references_are_walked_through_lists(self):
        self.assertEqual(measure_references({'a': [{'Measure': '1'}, {'LinkToMeasure': '2'}], 'b': [[{'Measure': '3'}]],
                                            'plain': 'M_4', 'other': {'Formula': 'COLUMN.SUM(1)'}}), {'1', '2', '3'})

    def test_automation_condition_group_is_rechecked_as_an_array(self):
        group = {'combinator': 'and', 'rules': [{'field': 'Active'}]}
        value = {'automations': [{'name': 'Notify', 'config': {'trigger': {'triggerConfig': {'conditions': group}}}}]}
        view, extensions = public_schema_view('sheets/s/visuals/v/automations.json', value)
        self.assertEqual(view['automations'][0]['config']['trigger']['triggerConfig']['conditions'], [group])
        self.assertEqual(extensions, ['Native automation conditions are one rule group; the public schema lists an array'])
        already = {'automations': [{'name': 'Notify', 'config': {'trigger': {'triggerConfig': {'conditions': [group]}}}}]}
        self.assertEqual(public_schema_view('sheets/s/visuals/v/automations.json', already), (already, []))
        # Records are only read as objects; a malformed entry cannot cancel the walk.
        loose = {'automations': ['string entry', {'name': 'No config'}]}
        self.assertEqual(public_schema_view('sheets/s/visuals/v/automations.json', loose), (loose, []))

    def test_connected_planning_graph_is_checked_with_the_plan(self):
        source = planning_source(**load(ROOT / 'assets/examples/infobridge-lineage/planning-source.request.json'))
        query = Query('Revenue', source['sourceGuid'], source['meta']).load_planning().pivot(['Region'], ['Month'], {'Revenue Plan': 'sum'})
        source['queries'] = [query.record]
        raw = self.raw()
        raw['connectedPlanning/infobridge.json'] = portable([source], [])
        self.assertEqual(validate_plan(raw)['status'], 'passed-structural-invariants')
        raw['connectedPlanning/infobridge.json']['sources'][0]['queries'][0]['transformationSteps'] = []
        with self.assertRaisesRegex(ValueError, 'Query has no source operation'):
            validate_plan(raw)

    def test_target_input_policy_normalization_is_reported_once(self):
        value = {'columns': [{'columnMeta': {'measure_type': {'DataInput': {'allow_input': 'Edit',
                                            'bound_to_filter_context': True,
                                            'column_type': {'Number': {'min_value': {'Static': 0}, 'max_value': {'Static': 10}}}}}}}]}
        view, extensions = public_schema_view('sheets/s/visuals/v/dataInput.json', value)
        policy = view['columns'][0]['columnMeta']['measure_type']['DataInput']
        self.assertEqual((policy['allow_input'], 'bound_to_filter_context' in policy), ('ReadAndEdit', False))
        self.assertEqual(policy['column_type']['Number'], {'min_value': 0, 'max_value': 10})
        self.assertEqual(extensions, ['Native target-input policy is newer than the pinned public DataInput schema'])
        self.assertEqual(public_schema_view('sheets/s/visuals/v/dataInput.json', {'columns': []})[1], [])


if __name__ == '__main__':
    unittest.main()
