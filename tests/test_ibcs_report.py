"""IBCS dashboards: Plan theme on request, a Matrix in place of the embedded grid, message title and footnotes."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import json
import unittest
from pathlib import Path
from runtime.codec import load, loads
from runtime.ibcs_report import (IBCS_THEME_TYPE, check_story, footnote_text, matrix_table,
                                 message_title, set_plan_theme)
from runtime.identity import Registry
from runtime.intelligence import rectangles

ROOT = Path(__file__).resolve().parents[1]


def model():
    return load(ROOT / 'assets/fixtures/model.json')


def table(**extra):
    out = {'label': 'Units by region', 'rows': ['Region[Region]'], 'columns': ['Period[Month]'],
           'measures': {'AC': 'Metrics[Units]', 'PL': {'field': 'Metrics[Cost]', 'label': 'Plan'}}}
    out.update(extra)
    return out


def application(dashboard, **top):
    return {'name': 'IBCS review', 'sheets': [{'name': 'Units', 'rows': ['Region[Region]'], 'columns': ['Period[Month]'],
            'measures': [{'key': 'units', 'label': 'Units', 'kind': 'Native', 'source': 'Metrics[Units]'}]}],
            'dashboards': [{'name': 'Review', 'owner': 'Units', 'slicers': [{'field': 'Region[Region]'}], 'cards': [],
                            'charts': [{'label': 'Units vs plan', 'recipe': 'C04', 'category': 'Region[Region]',
                                        'measures': {'AC': 'Metrics[Units]', 'PL': 'Metrics[Cost]'}}], **dashboard}], **top}


def runs(props):
    text = loads(props['visualState']['text'])
    return [[(n['text'], n['style'], n['format']) for n in p['children']] for p in text['root']['children']]


class PlanTheme(unittest.TestCase):
    def test_ibcs_sets_type_5_and_keeps_other_theme_members(self):
        exported = {'$schema': 'x', 'properties': {'theme': {'type': 3, 'appliedThemes': {'42': {'type': 3}}}, 'homeLayout': {'show': True}}}
        out = set_plan_theme(exported, 'ibcs')
        self.assertEqual(out['properties']['theme'], {'type': IBCS_THEME_TYPE, 'appliedThemes': {'42': {'type': 3}}})
        self.assertEqual(exported['properties']['theme']['type'], 3)
        self.assertEqual(set_plan_theme({'properties': {}}, 'ibcs')['properties']['theme'], {'type': 5})

    def test_exported_theme_members_survive_and_validate(self):
        from runtime.construct import plan_properties
        from runtime.validate import require_public_schema_acceptance
        exported = plan_properties()
        # Theme shape as the backend exports it: an id plus the per-sheet applied themes.
        exported['properties']['theme'] = {'id': 'default', 'type': 3, 'appliedThemes': {'42': {'id': 'default', 'type': 3}}}
        out = set_plan_theme(exported, 'ibcs')
        self.assertEqual(out['properties']['theme']['appliedThemes'], {'42': {'id': 'default', 'type': 3}})
        result = require_public_schema_acceptance({'planProperties.json': out})
        self.assertIn('Native theme members id and appliedThemes extend the historical public theme object', result[0]['reason'])
        bad = plan_properties()
        bad['properties']['theme'] = {'type': 5, 'colors': {}}
        with self.assertRaisesRegex(ValueError, 'colors'):
            require_public_schema_acceptance({'planProperties.json': bad})

    def test_only_named_themes_are_accepted(self):
        with self.assertRaisesRegex(ValueError, 'Supported Plan theme: ibcs'):
            set_plan_theme({'properties': {}}, 'dark')
        with self.assertRaisesRegex(ValueError, 'not an object'):
            set_plan_theme({'properties': {'theme': 5}}, 'ibcs')

    def test_build_sets_the_theme_only_when_the_spec_names_it(self):
        from runtime.planning_presentation import build_application
        plain = build_application(model(), application({}))
        self.assertNotIn('theme', plain['raw']['planProperties.json']['properties'])
        themed = build_application(model(), application({}, theme='ibcs'))
        self.assertEqual(themed['raw']['planProperties.json']['properties']['theme'], {'type': 5})


class MatrixTable(unittest.TestCase):
    def test_matrix_binds_rows_columns_and_comparison_roles(self):
        p = matrix_table(model(), table(), Registry())
        self.assertEqual(p['visualType'], 10)
        self.assertNotIn('chartType', p['visualState'])
        self.assertEqual([(a['id'], a['bucketId'], a['dataRoleType']) for a in p['pivotAssignments']],
                         [('Region[Region]', 'rows', 'Grouping'), ('Period[Month]', 'columns', 'Grouping'),
                          ('Metrics[Units]', 'ameasure', 'Measure'), ('Metrics[Cost]', 'plmeasure', 'Measure')])
        self.assertEqual(p['pivotAssignments'][-1]['customName'], 'Plan')

    def test_matrix_refuses_incomplete_or_ambiguous_tables(self):
        cases = [(table(rows=[]), 'row dimensions'),
                 (table(measures={'PY': 'Metrics[Price]'}), 'AC value'),
                 (table(measures={'AC': 'Metrics[Units]', 'stack': 'Metrics[Cost]'}), 'not stack'),
                 (table(columns=['Region[Region]']), 'each dimension once'),
                 (table(measures={'AC': 'Metrics[Units]', 'PY': ['Metrics[Price]', 'Metrics[Cost]']}), 'PY takes one measure'),
                 (table(measures={'AC': 'Metrics[Units]', 'PY': 'Metrics[Units]'}), 'same value'),
                 (table(style='ibcs'), 'Unconsumed table options: style')]
        for spec, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                matrix_table(model(), spec, Registry())


class Story(unittest.TestCase):
    def test_message_title_follows_fabrics_ibcs_title_sizes(self):
        p = message_title({'message': 'Units 5% above plan', 'subtitle': 'Units, FY2026', 'detail': 'AC vs PL'})
        self.assertEqual(p['visualType'], 202)
        self.assertEqual(runs(p), [[('Units 5% above plan', 'font-family: Arial;font-size: 18px;', 1)],
                                   [('Units, FY2026', 'font-family: Arial;font-size: 13px;', 0)],
                                   [('AC vs PL', 'font-family: Arial;font-size: 11px;', 0)]])
        self.assertEqual(p['visualStyles']['background']['backgroundColor'], '#FFFFFF')

    def test_footnotes_are_small_lines_and_optional(self):
        p = footnote_text({'message': 'm', 'footnotes': ['AC = actual', 'PL = plan']})
        self.assertEqual([r[0][0] for r in runs(p)], ['AC = actual', 'PL = plan'])
        self.assertTrue(all('font-size: 11px;' in r[0][1] for r in runs(p)))
        self.assertIsNone(footnote_text({'message': 'm'}))

    def test_story_needs_a_message_and_known_keys(self):
        with self.assertRaisesRegex(ValueError, 'needs a message'):
            check_story({'subtitle': 'x'})
        with self.assertRaisesRegex(ValueError, 'Unconsumed IBCS story options: comments'):
            check_story({'message': 'm', 'comments': ['x']})
        with self.assertRaisesRegex(ValueError, 'footnotes must be a list'):
            check_story({'message': 'm', 'footnotes': 'x'})


class Layout(unittest.TestCase):
    def test_footnotes_close_the_page_in_both_presets(self):
        for preset in (None, 'stacked'):
            with self.subTest(preset=preset):
                kw = {'width': 1600, 'charts': 2, 'layout': preset, 'footnote_lines': 3}
                r = rectangles(2, 1, **kw)
                rects = r['rectangles']
                note = rects['note']
                self.assertGreaterEqual(note['height'], 68)
                for key, other in rects.items():
                    if key != 'note' and other['x'] < note['x'] + note['width'] and note['x'] < other['x'] + other['width']:
                        self.assertLessEqual(other['y'] + other['height'], note['y'], key)

    def test_layout_without_footnotes_is_unchanged(self):
        self.assertEqual(rectangles(2, 1, width=1600, charts=2), rectangles(2, 1, width=1600, charts=2, footnote_lines=0))


class Dashboard(unittest.TestCase):
    def build(self, dashboard, **top):
        from runtime.planning_presentation import build_application
        return build_application(model(), application(dashboard, **top))

    def visuals(self, result):
        sheet = next(s for s in result['raw']['definition.json']['sheets'] if s['sheetType'] == 'REPORTING')
        return sheet, {v['visualType']: v for v in sheet['workloadItemEntityVisuals']}

    def test_matrix_replaces_the_embed_and_the_owner_page_stays_visible(self):
        result = self.build({'table': table()})
        sheet, by_type = self.visuals(result)
        self.assertIn('INFORIVER', by_type)
        self.assertNotIn('PLANNING', by_type)
        owner = next(s for s in result['raw']['definition.json']['sheets'] if s['sheetType'] == 'PLANNING')
        self.assertFalse(owner['isHidden'])
        self.assertEqual(result['presentationCheck']['inputOnVisiblePlanningPage'], 1)
        props = result['raw'][f"sheets/{sheet['recordGuid']}/sheet.json"]['properties']
        self.assertEqual(props['reactiveVisualProperties'], [])
        schemas = __import__('runtime.validate', fromlist=['x']).require_public_schema_acceptance(result['raw'])
        self.assertTrue(all(s['status'].startswith('passed') for s in schemas))

    def test_embedded_dashboards_keep_the_owner_hidden(self):
        result = self.build({})
        _, by_type = self.visuals(result)
        self.assertIn('PLANNING', by_type)
        owner = next(s for s in result['raw']['definition.json']['sheets'] if s['sheetType'] == 'PLANNING')
        self.assertTrue(owner['isHidden'])

    def test_ibcs_story_replaces_the_banner_and_fills_the_note(self):
        result = self.build({'table': table(), 'ibcs': {'message': 'Units 5% above plan', 'footnotes': ['AC = actual']}})
        sheet, _ = self.visuals(result)
        texts = []
        for v in sheet['workloadItemEntityVisuals']:
            if v['visualType'] == 'BI_TEXT':
                p = result['raw'][f"sheets/{sheet['recordGuid']}/visuals/{v['visualId']}/properties.json"]['properties']
                texts.append((p['layerProperties']['layerProperties']['name'], [r[0][0] for r in runs(p)]))
        self.assertEqual(sorted(texts), [('Footnotes', ['AC = actual']), ('Message title', ['Units 5% above plan'])])

    def test_embedded_grid_keeps_its_role_key_under_the_message(self):
        result = self.build({'ibcs': {'message': 'Units 5% above plan', 'subtitle': 'Units, FY2026'}})
        sheet, by_type = self.visuals(result)
        self.assertIn('PLANNING', by_type)
        header = next(o['properties'] for k, o in result['raw'].items()
                      if k.startswith(f"sheets/{sheet['recordGuid']}/visuals/")
                      and o['properties'].get('layerProperties', {}).get('layerProperties', {}).get('name') == 'Message title')
        lines = [[run[0] for run in r] for r in runs(header)]
        self.assertEqual(lines[:2], [['Units 5% above plan'], ['Units, FY2026']])
        self.assertEqual(lines[-1][0].strip(), 'INPUT / FORECAST')
        self.assertEqual(header['visualStyles']['background']['backgroundColor'], '#193446')

    def test_note_and_footnotes_are_one_slot(self):
        with self.assertRaisesRegex(ValueError, 'either note or IBCS footnotes'):
            self.build({'note': 'n', 'ibcs': {'message': 'm', 'footnotes': ['f']}})

    def test_matrix_caption_defaults_to_the_table_label(self):
        result = self.build({'table': table()})
        sheet, _ = self.visuals(result)
        captions = [p['properties'] for k, p in result['raw'].items() if k.startswith(f"sheets/{sheet['recordGuid']}/visuals/")
                    and p['properties'].get('layerProperties', {}).get('layerProperties', {}).get('name') == 'Table caption']
        self.assertEqual([r[0][0] for r in runs(captions[0])], ['Units by region'])


if __name__ == '__main__':
    unittest.main()
