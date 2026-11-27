"""Decomposition and organization trees: TREE visuals with both selectors and the tree's own roles."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import unittest
from pathlib import Path
from runtime.codec import load
from runtime.identity import Registry
from runtime.intelligence import chart, classify_visual, complete_card_state
from runtime.tree_visuals import tree_requirements, tree_visual

ROOT = Path(__file__).resolve().parents[1]


def model():
    return load(ROOT / 'assets/fixtures/model.json')


def roles(p):
    return [(a['id'], a['bucketId'], a['dataRoleType']) for a in p['pivotAssignments']]


class TreeVisuals(unittest.TestCase):
    def build(self, spec):
        return tree_visual(model(), spec, Registry())

    def test_decomposition_tree_breaks_a_measure_down_by_levels(self):
        p = self.build({'label': 'Units drivers', 'tree': 'decomposition',
                        'levels': ['Region[Region]', 'Product[Product]'], 'measure': 'Metrics[Units]'})
        self.assertEqual(p['visualType'], 25)
        self.assertEqual((p['chartType'], p['visualState']['chartType']), ('DECOMPOSITION_TREE', 'DECOMPOSITION_TREE'))
        self.assertEqual(roles(p), [('Region[Region]', 'rows', 'Grouping'), ('Product[Product]', 'rows', 'Grouping'),
                                    ('Metrics[Units]', 'ameasure', 'Measure')])
        self.assertEqual([a['order'] for a in p['pivotAssignments'][:2]], [0, 1])
        self.assertEqual(p['superFilterAssignments'], [])
        self.assertEqual([r['switch'] for r in tree_requirements(p)], ['decomposition tree'])

    def test_organization_tree_uses_parent_fields_and_sparkline_roles(self):
        p = self.build({'label': 'Org', 'tree': 'organization', 'levels': ['Employee[Employee]'],
                        'parent': 'Account[Account]', 'fields': ['Region[Region]'], 'sparkline': ['Period[Month]'],
                        'measure': {'field': 'Metrics[Hours]', 'label': 'Hours'}})
        self.assertEqual(p['chartType'], 'ORGANIZATION_TREE')
        self.assertEqual(roles(p), [('Employee[Employee]', 'rows', 'Grouping'), ('Account[Account]', 'parentid', 'Grouping'),
                                    ('Region[Region]', 'fieldid', 'Grouping'), ('Period[Month]', 'columns', 'Grouping'),
                                    ('Metrics[Hours]', 'ameasure', 'Measure')])
        self.assertEqual(p['pivotAssignments'][-1]['customName'], 'Hours')
        needs = tree_requirements(p)
        self.assertEqual([r['switch'] for r in needs], ['organization tree', 'organization tree parent-data mapping'])
        self.assertIn('removes the parent identifier', needs[1]['whenOff'])

    def test_organization_tree_needs_no_measure(self):
        p = self.build({'label': 'Org', 'tree': 'organization', 'levels': ['Region[Region]', 'Employee[Employee]']})
        self.assertEqual([b for _, b, _ in roles(p)], ['rows', 'rows'])
        self.assertEqual([r['switch'] for r in tree_requirements(p)], ['organization tree'])

    def test_incomplete_or_mismatched_trees_are_refused(self):
        cases = [({'label': 'T', 'tree': 'decomposition', 'levels': ['Region[Region]']}, 'measure it breaks down'),
                 ({'label': 'T', 'tree': 'decomposition', 'levels': [], 'measure': 'Metrics[Units]'}, 'at least one level'),
                 ({'label': 'T', 'tree': 'decomposition', 'levels': ['Region[Region]'], 'measure': 'Metrics[Units]',
                   'parent': 'Account[Account]'}, 'belong to an organization tree'),
                 ({'label': 'T', 'tree': 'organization', 'levels': ['Region[Region]'], 'sparkline': ['Period[Month]']},
                  'sparkline needs a measure'),
                 ({'label': 'T', 'tree': 'organization', 'levels': ['Region[Region]'], 'parent': ['A[A]', 'B[B]']},
                  'one parent identifier'),
                 ({'label': 'T', 'tree': 'organization', 'levels': ['Region[Region]'], 'fields': ['Region[Region]']},
                  'each dimension once'),
                 ({'label': 'T', 'tree': 'row', 'levels': ['Region[Region]']}, 'decomposition and organization trees only'),
                 ({'label': 'T', 'tree': 'radial', 'levels': ['Region[Region]']}, 'decomposition or organization'),
                 ({'label': 'T', 'tree': 'organization', 'levels': ['Metrics[Units]']}, 'Semantic measures belong in Values'),
                 ({'label': 'T', 'tree': 'organization', 'levels': ['Region[Region]'], 'layout': 'radial'},
                  'Unconsumed tree options: layout')]
        for spec, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.build(spec)

    def test_dispatcher_and_classification_know_the_native_tree(self):
        p = chart(model(), {'label': 'Drivers', 'tree': 'decomposition', 'levels': ['Region[Region]'],
                            'measure': 'Metrics[Units]'}, Registry())
        self.assertEqual(classify_visual(p)['engine'], 'native tree')
        self.assertEqual(classify_visual({'visualType': 50, 'chartType': 'DECOMPOSITION_TREE'})['engine'], 'Analytics+ chart')
        with self.assertRaisesRegex(ValueError, 'Refusing to retype a Decomposition tree'):
            complete_card_state(p)


class DashboardTrees(unittest.TestCase):
    def test_dashboard_places_a_tree_in_a_chart_slot(self):
        from runtime.planning_presentation import build_application
        from runtime.validate import require_public_schema_acceptance
        spec = {'name': 'Tree review', 'sheets': [{'name': 'Units', 'rows': ['Region[Region]'], 'columns': ['Period[Month]'],
                'measures': [{'key': 'units', 'label': 'Units', 'kind': 'Native', 'source': 'Metrics[Units]'}]}],
                'dashboards': [{'name': 'Drivers', 'owner': 'Units', 'slicers': [{'field': 'Region[Region]'}], 'cards': [],
                                'charts': [{'label': 'Units drivers', 'tree': 'decomposition',
                                            'levels': ['Region[Region]', 'Product[Product]'], 'measure': 'Metrics[Units]'}]}]}
        result = build_application(model(), spec)
        sheet = next(s for s in result['raw']['definition.json']['sheets'] if s['sheetType'] == 'REPORTING')
        trees = [v for v in sheet['workloadItemEntityVisuals'] if v['visualType'] == 'TREE']
        self.assertEqual(len(trees), 1)
        props = result['raw'][f"sheets/{sheet['recordGuid']}/visuals/{trees[0]['visualId']}/properties.json"]['properties']
        self.assertEqual(props['visualType'], 25)
        self.assertNotIn('embeddedSuperFilter', props['visualState'])
        self.assertEqual(result['presentationCheck']['coveredByRichDashboard'], 1)
        needs = result['dashboardIdentities'][0]['treeRequirements']
        self.assertEqual(list(needs), [trees[0]['visualId']])
        self.assertEqual(needs[trees[0]['visualId']][0]['switch'], 'decomposition tree')
        self.assertTrue(all(s['status'].startswith('passed') for s in require_public_schema_acceptance(result['raw'])))


if __name__ == '__main__':
    unittest.main()
