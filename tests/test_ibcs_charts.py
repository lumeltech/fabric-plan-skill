"""IBCS recipe charts: native template selectors plus bucket bindings the template accepts."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import unittest
from pathlib import Path
from runtime.chart_filters import audit_chart_filters
from runtime.codec import load
from runtime.codec import loads
from runtime.ibcs_charts import (APPEARANCE, RECIPES, TEMPLATES, apply_chart_theme, chart_theme, describe,
                                 ibcs_palette, measure_roles, recipe_chart, recipes, required_buckets, role_style)
from runtime.identity import Registry
from runtime.intelligence import chart, column_chart

ROOT = Path(__file__).resolve().parents[1]
VALUES = {'AC': 'Metrics[Units]', 'PY': 'Metrics[Price]', 'PL': 'Metrics[Cost]', 'FC': 'Metrics[Expense]'}


def model():
    return load(ROOT / 'assets/fixtures/model.json')


def spec(code, *buckets, **extra):
    measures = {b: VALUES[b] for b in buckets if b in VALUES}
    out = {'label': code + ' chart', 'recipe': code, 'category': 'Region[Region]', 'measures': measures}
    if 'stack' in buckets:
        out['stack'] = 'Product[Product]'
    out.update(extra)
    return out


def buckets(p):
    return [(a['id'], a['bucketId']) for a in p['pivotAssignments']]


def appearance(p):
    return loads(p['visualState'][APPEARANCE])['charts']


class RecipeCharts(unittest.TestCase):
    def build(self, s):
        return recipe_chart(model(), s, Registry())

    def test_every_recipe_builds_with_its_required_bindings(self):
        for code, (name, types, _) in RECIPES.items():
            with self.subTest(code=code):
                required = required_buckets(code)
                p = self.build(spec(code, *required))
                self.assertEqual(p['visualType'], 50)
                self.assertEqual(p['chartType'], types[0])
                self.assertEqual(p['visualState']['chartType'], types[0])
                self.assertEqual(sorted(b for _, b in buckets(p)), sorted(required))
                audit_chart_filters(p)
                self.assertTrue(describe(p)['selectorsAgree'])

    def test_c01_binds_category_stack_and_three_measures(self):
        p = self.build(spec('C01', 'axis', 'AC', 'PL', 'FC', 'stack'))
        self.assertEqual(buckets(p), [('Region[Region]', 'axis'), ('Product[Product]', 'stack'),
                                      ('Metrics[Units]', 'AC'), ('Metrics[Cost]', 'PL'), ('Metrics[Expense]', 'FC')])
        roles = {a['bucketId']: a['dataRoleType'] for a in p['pivotAssignments']}
        self.assertEqual(roles, {'axis': 'Grouping', 'stack': 'Grouping', 'AC': 'Measure', 'PL': 'Measure', 'FC': 'Measure'})

    def test_missing_recipe_binding_is_named(self):
        with self.assertRaisesRegex(ValueError, r'C01 .*needs bindings for FC'):
            self.build(spec('C01', 'AC', 'PL', 'stack'))
        with self.assertRaisesRegex(ValueError, r'C02 .*stack'):
            self.build(spec('C02', 'AC'))

    def test_unknown_recipe_and_template_are_refused(self):
        with self.assertRaisesRegex(ValueError, "Unknown IBCS recipe 'C14'; the catalog has C01, .*C11, C12, C13$"):
            self.build(spec('C14', 'AC'))
        s = spec('C03', 'AC', 'PY', 'FC')
        del s['recipe']
        s['chartType'] = 'PIE_CHART'
        with self.assertRaisesRegex(ValueError, 'Unsupported chart template'):
            self.build(s)

    def test_recipe_chart_type_must_be_one_the_recipe_names(self):
        with self.assertRaisesRegex(ValueError, 'C03 uses chartType COLUMN_VERTICAL'):
            self.build(spec('C03', 'AC', 'PY', 'FC', chartType='LINE'))

    def test_c08_mixed_variant_uses_area_with_several_actuals(self):
        s = spec('C08', 'AC', chartType='AREA')
        s['measures']['AC'] = [{'field': 'Metrics[Units]', 'label': 'Direct'}, {'field': 'Metrics[Hours]', 'label': 'Retail'}]
        p = self.build(s)
        self.assertEqual(p['chartType'], 'AREA')
        actuals = [a for a in p['pivotAssignments'] if a['bucketId'] == 'AC']
        self.assertEqual([(a['order'], a['customName']) for a in actuals], [(0, 'Direct'), (1, 'Retail')])

    def test_c11_is_one_line_panel_per_driver(self):
        panels = [self.build({**spec('C11', 'AC'), 'label': label, 'measures': {'AC': field}})
                  for label, field in (('Units', VALUES['AC']), ('Price', VALUES['PY']), ('Cost', VALUES['PL']))]
        self.assertEqual([(p['chartType'], buckets(p)[1]) for p in panels],
                         [('LINE', (VALUES['AC'], 'AC')), ('LINE', (VALUES['PY'], 'AC')), ('LINE', (VALUES['PL'], 'AC'))])
        for extra in ({'AC': [VALUES['AC'], VALUES['PY']]}, {'AC': VALUES['AC'], 'PY': VALUES['PY']}):
            with self.assertRaisesRegex(ValueError, 'C11 .Related Driver Panels. takes one measure per panel'):
                self.build({**spec('C11', 'AC'), 'measures': extra})

    def test_native_stacked_area_needs_a_stack(self):
        with self.assertRaisesRegex(ValueError, 'STACKED_AREA needs a stack'):
            self.build(spec('C08', 'AC'))

    def test_native_stacked_area_takes_only_an_actual_and_a_forecast(self):
        self.assertEqual(self.build(spec('C08', 'AC', 'FC', 'stack'))['chartType'], 'STACKED_AREA')
        for bucket in ('PY', 'PL'):
            with self.assertRaisesRegex(ValueError, 'STACKED_AREA has no measure bucket ' + bucket):
                self.build(spec('C08', 'AC', bucket, 'stack'))

    def test_stacked_template_without_stack_needs_two_measures(self):
        s = {'label': 'Stacked', 'chartType': 'STACKED_COLUMN_VERTICAL', 'category': 'Region[Region]',
             'measures': {'AC': VALUES['AC']}}
        with self.assertRaisesRegex(ValueError, 'renders as COLUMN_VERTICAL'):
            self.build(s)
        s['measures']['PY'] = VALUES['PY']
        self.assertEqual(self.build(s)['chartType'], 'STACKED_COLUMN_VERTICAL')

    def test_percentage_stacked_templates_are_available_without_a_recipe(self):
        for chart_type in ('PERCENTAGE_STACKED_VERTICAL', 'PERCENTAGE_STACKED_HORIZONTAL'):
            s = {'label': '100%', 'chartType': chart_type, 'category': 'Region[Region]',
                 'stack': 'Product[Product]', 'measures': {'AC': VALUES['AC']}}
            self.assertEqual(self.build(s)['visualState']['chartType'], chart_type)

    def test_bucket_limits_follow_the_template(self):
        s = spec('C03', 'AC', 'PY', 'FC')
        s['measures']['AC'] = [VALUES['AC'], 'Metrics[Hours]']
        with self.assertRaisesRegex(ValueError, 'at most 1 measure'):
            self.build(s)
        with self.assertRaisesRegex(ValueError, 'has no stack bucket'):
            self.build(spec('C03', 'AC', 'PY', 'FC', stack='Product[Product]'))
        with self.assertRaisesRegex(ValueError, 'has no measure bucket FC'):
            self.build({'label': 'Scatter', 'recipe': 'C09', 'category': 'Region[Region]',
                        'measures': {'AC': VALUES['AC'], 'PY': VALUES['PY'], 'FC': VALUES['FC']}})

    def test_comparison_templates_need_two_measures(self):
        s = {'label': 'Bridge', 'chartType': 'COLUMN_WATERFALL_VERTICAL', 'category': 'Region[Region]',
             'measures': {'AC': VALUES['AC']}}
        with self.assertRaisesRegex(ValueError, 'at least 2 measures'):
            self.build(s)
        with self.assertRaisesRegex(ValueError, 'BUBBLE_PLOT needs 1 measure in bucket PL'):
            self.build({'label': 'Bubble', 'chartType': 'BUBBLE_PLOT', 'category': 'Region[Region]',
                        'measures': {'AC': VALUES['AC'], 'PY': VALUES['PY']}})

    def test_bindings_keep_dimension_and_measure_roles(self):
        with self.assertRaisesRegex(ValueError, 'Semantic measures belong in Values'):
            self.build(spec('C03', 'AC', 'PY', 'FC', category='Metrics[Hours]'))
        with self.assertRaisesRegex(ValueError, 'different fields'):
            self.build(spec('C02', 'AC', 'stack', stack='Region[Region]'))
        s = spec('C03', 'AC', 'PY', 'FC')
        s['measures']['PY'] = VALUES['AC']
        with self.assertRaisesRegex(ValueError, 'same value is bound to AC and PY'):
            self.build(s)

    def test_unconsumed_options_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'Unconsumed chart options: legend'):
            self.build(spec('C03', 'AC', 'PY', 'FC', legend=True))
        s = spec('C03', 'AC', 'PY', 'FC')
        s['measures']['AC'] = {'field': VALUES['AC'], 'color': '#000000'}
        with self.assertRaisesRegex(ValueError, 'Unconsumed measure options in AC: color'):
            self.build(s)

    def test_catalog_lists_every_recipe_with_a_supported_template(self):
        catalog = recipes()
        self.assertEqual(sorted(catalog), sorted(RECIPES))
        for entry in catalog.values():
            self.assertTrue(set(entry['chartTypes']) <= set(TEMPLATES))
        self.assertEqual(catalog['C08']['requiredBuckets'], {'STACKED_AREA': ['axis', 'AC', 'stack'],
                                                             'AREA': ['axis', 'AC']})
        self.assertEqual(catalog['C10']['requiredBuckets']['BUBBLE_PLOT'], ['axis', 'AC', 'PY', 'PL'])


class ChartTheme(unittest.TestCase):
    def build(self, s):
        return recipe_chart(model(), s, Registry())

    def test_recipe_chart_keeps_the_ibcs_theme_with_scenario_notation(self):
        charts = appearance(self.build(spec('C01', 'AC', 'PL', 'FC', 'stack')))
        self.assertEqual((charts['theme'], charts['isStandardTheme'], charts['isDefaultMeta']),
                         ('ibcs', True, {'theme': False}))
        styles = charts['measuresStyle']
        self.assertEqual(sorted(styles), ['AC', 'FC', 'PL'])
        self.assertEqual({r: (s['fillColor'], s['pattern']) for r, s in styles.items()},
                         {'AC': ('#262626', 'solid'), 'PL': ('#4e4e4e', 'outlined'), 'FC': ('#262626', 'hatched')})
        self.assertEqual(charts['variance']['colors'], {'positive': '#8eb900', 'negative': '#ff000a', 'neutral': '#DDDDDD'})

    def test_previous_period_is_a_lighter_solid_than_actual(self):
        styles = appearance(self.build(spec('C03', 'AC', 'PY', 'FC')))['measuresStyle']
        self.assertEqual((styles['PY']['fillColor'], styles['PY']['pattern']), ('#bfbfbf', 'solid'))
        self.assertNotEqual(styles['AC']['fillColor'], styles['PY']['fillColor'])

    def test_every_recipe_saves_a_style_for_each_bound_role(self):
        for code in RECIPES:
            with self.subTest(code=code):
                p = self.build(spec(code, *required_buckets(code)))
                self.assertEqual(describe(p)['theme'], 'ibcs')
                self.assertEqual(sorted(appearance(p)['measuresStyle']), sorted(measure_roles(p)))

    def test_theme_plan_leaves_a_recipe_chart_on_the_plan_theme(self):
        p = self.build(spec('C03', 'AC', 'PY', 'FC', theme='plan'))
        self.assertNotIn(APPEARANCE, p['visualState'])
        self.assertEqual(describe(p)['theme'], 'plan')

    def test_native_template_without_a_recipe_keeps_the_ibcs_theme_too(self):
        s = {'label': 'Stacked', 'chartType': 'STACKED_COLUMN_VERTICAL', 'category': 'Region[Region]',
             'stack': 'Product[Product]', 'measures': {'AC': VALUES['AC']}}
        p = self.build(s)
        self.assertEqual(chart_theme(p), 'ibcs')
        self.assertEqual(sorted(appearance(p)['measuresStyle']), ['AC'])
        self.assertEqual(appearance(self.build({**s, 'theme': 'ibcs'})), appearance(p))
        self.assertNotIn(APPEARANCE, self.build({**s, 'theme': 'plan'})['visualState'])

    def test_overlapped_columns_from_a_template_show_actual_and_previous_period(self):
        s = {'label': 'Overlap', 'chartType': 'COLUMN_VERTICAL', 'category': 'Region[Region]',
             'measures': {'AC': VALUES['AC'], 'PY': VALUES['PY']}}
        styles = appearance(self.build(s))['measuresStyle']
        self.assertEqual({r: (v['fillColor'], v['pattern']) for r, v in styles.items()},
                         {'AC': ('#262626', 'solid'), 'PY': ('#bfbfbf', 'solid')})

    def test_unknown_chart_theme_is_refused(self):
        with self.assertRaisesRegex(ValueError, "Chart theme is ibcs or plan, not 'dark'"):
            self.build(spec('C03', 'AC', 'PY', 'FC', theme='dark'))

    def test_further_actuals_take_the_additional_actual_roles(self):
        s = spec('C08', 'AC', chartType='AREA')
        s['measures']['AC'] = [VALUES['AC'], 'Metrics[Hours]', VALUES['PY']]
        p = self.build(s)
        self.assertEqual(measure_roles(p), ['AC', 'AC1', 'AC2'])
        styles = appearance(p)['measuresStyle']
        self.assertEqual([styles[r]['fillColor'] for r in ('AC', 'AC1', 'AC2')], ['#262626', '#666666', '#858585'])
        self.assertEqual(styles['AC1']['lineArea']['marker'], {'enabled': False, 'useSeriesColor': False,
                                                              'color': '#666666', 'size': 6, 'type': 'circleFilled'})

    def test_role_styles_are_complete_and_carry_no_placeholder(self):
        keys = set(role_style('AC'))
        for role in ['AC', 'PY', 'PL', 'FC'] + ['AC' + str(i) for i in range(1, 30)]:
            style = role_style(role)
            self.assertEqual(set(style), keys, role)
            self.assertNotIn('{', repr(sorted(self.leaves(style))), role)
        with self.assertRaisesRegex(ValueError, "no measure style for role 'AC30'"):
            role_style('AC30')

    def leaves(self, value):
        if isinstance(value, dict):
            return [leaf for v in value.values() for leaf in self.leaves(v)]
        return [str(value)]

    def test_palette_matches_the_saved_measure_styles(self):
        palette = ibcs_palette()
        for role, entry in palette['measures'].items():
            style = role_style(role)
            self.assertEqual(entry, {k: style[k] for k in ('fillColor', 'borderColor', 'pattern')})
        self.assertEqual(palette['variance'], appearance(self.build(spec('C04', 'AC', 'PL')))['variance']['colors'])
        for color in palette['series']:
            channels = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
            self.assertLessEqual(max(channels) - min(channels), 16, color + ' is not a neutral grey')

    def test_theme_applies_to_an_exported_chart_and_keeps_its_other_settings(self):
        p = self.build(spec('C03', 'AC', 'PY', 'FC', theme='plan'))
        p['visualState'][APPEARANCE] = '{"charts":{"theme":"custom","isDefaultMeta":{"theme":true},"showFCLine":false,' \
            '"measuresStyle":{"Units":{"lineArea":{"marker":{}}},"AC":{"lineArea":{"marker":{}}}},' \
            '"groupStyle":{"g":{"fillColor":"#ff0000"}},"variance":{"varianceLineSize":6}},"tables":{"keep":1}}'
        before = loads(p['visualState'][APPEARANCE])
        self.assertEqual(chart_theme(p), 'plan')
        out = apply_chart_theme(p)
        self.assertEqual(loads(p['visualState'][APPEARANCE]), before)
        state = loads(out['visualState'][APPEARANCE])
        charts = state['charts']
        self.assertEqual(state['tables'], {'keep': 1})
        self.assertEqual((charts['theme'], charts['isDefaultMeta']['theme'], charts['showFCLine']), ('ibcs', False, False))
        self.assertEqual(charts['variance']['varianceLineSize'], 6)
        self.assertEqual(charts['variance']['colors']['positive'], '#8eb900')
        self.assertEqual(charts['groupStyle'], {})
        self.assertEqual(charts['measuresStyle']['Units'], {'lineArea': {'marker': {}}})
        self.assertEqual(charts['measuresStyle']['AC'], role_style('AC'))
        self.assertEqual(apply_chart_theme(out), out)

    def test_theme_is_refused_for_other_visuals_and_unbound_charts(self):
        p = self.build(spec('C03', 'AC', 'PY', 'FC', theme='plan'))
        with self.assertRaisesRegex(ValueError, 'Supported chart theme: ibcs'):
            apply_chart_theme(p, 'dark')
        with self.assertRaisesRegex(ValueError, 'Bind the chart measures'):
            apply_chart_theme({**p, 'pivotAssignments': [a for a in p['pivotAssignments'] if a['bucketId'] == 'axis']})
        with self.assertRaisesRegex(ValueError, 'not a KPI card'):
            apply_chart_theme({**p, 'chartType': 'CARD'})
        with self.assertRaisesRegex(ValueError, 'not a visual of type 10'):
            apply_chart_theme({**p, 'visualType': 10})
        with self.assertRaisesRegex(ValueError, 'appearance is not an object'):
            apply_chart_theme({**p, 'visualState': {**p['visualState'], APPEARANCE: '[]'}})


# Charts on the pages of the IBCS business reporting templates: (page, recipe, chartType, bound buckets).
# A chart without a recipe is built from its template alone, such as actual against previous year on a table page.
TEMPLATE_PAGES = [
    ('C01', 'C01', 'STACKED_COLUMN_VERTICAL', ('AC', 'PL', 'FC', 'stack')),
    ('C02', 'C02', 'STACKED_COLUMN_HORIZONTAL', ('AC', 'stack')),
    ('C03', 'C03', 'COLUMN_VERTICAL', ('AC', 'PY', 'PL', 'FC')),
    ('C04', 'C04', 'COLUMN_HORIZONTAL', ('AC', 'PL')),
    ('C05', 'C05', 'COLUMN_WATERFALL_VERTICAL', ('AC', 'PY', 'PL', 'FC')),
    ('C06', 'C06', 'COLUMN_WATERFALL_HORIZONTAL', ('AC', 'PY', 'PL')),
    ('C07', 'C07', 'LINE', ('AC',)),
    ('C08', 'C08', 'STACKED_AREA', ('AC', 'stack')),
    ('C09', 'C09', 'SCATTER_PLOT', ('AC', 'PY')),
    ('C10', 'C10', 'BUBBLE_PLOT', ('AC', 'PY', 'PL')),
    ('C11', 'C11', 'LINE', ('AC',)),
    ('C12', 'C12', 'SIDE_BY_SIDE_WATERFALL', ('AC', 'PY', 'PL')),
    ('C13', 'C13', 'COLUMN_VERTICAL', ('AC', 'PL')),
    ('C13', 'C04', 'COLUMN_HORIZONTAL', ('AC', 'PL')),
    ('T01', 'C04', 'COLUMN_HORIZONTAL', ('AC', 'PL')),
    ('T01', None, 'COLUMN_HORIZONTAL', ('AC', 'PY')),
    ('T02', 'C04', 'COLUMN_HORIZONTAL', ('AC', 'PL')),
    ('T02', None, 'COLUMN_HORIZONTAL', ('AC', 'PY')),
    ('T03', 'C04', 'COLUMN_HORIZONTAL', ('AC', 'PL')),
    ('T04', 'C12', 'SIDE_BY_SIDE_WATERFALL', ('AC', 'PY')),
]


class TemplatePages(unittest.TestCase):
    def test_every_template_page_chart_builds_with_the_ibcs_theme(self):
        for page, code, chart_type, bound in TEMPLATE_PAGES:
            with self.subTest(page=page, chartType=chart_type, bound=bound):
                s = {'label': page + ' chart', 'category': 'Region[Region]',
                     'measures': {b: VALUES[b] for b in bound if b in VALUES}}
                s.update({'recipe': code} if code else {'chartType': chart_type})
                if 'stack' in bound:
                    s['stack'] = 'Product[Product]'
                p = recipe_chart(model(), s, Registry())
                self.assertEqual((p['chartType'], p['visualState']['chartType']), (chart_type, chart_type))
                self.assertEqual(chart_theme(p), 'ibcs')
                self.assertEqual(sorted(appearance(p)['measuresStyle']), sorted(b for b in bound if b in VALUES))
                audit_chart_filters(p)

    def test_template_pages_cover_every_recipe_and_only_supported_templates(self):
        self.assertEqual({code for _, code, _, _ in TEMPLATE_PAGES if code}, set(RECIPES))
        self.assertTrue({chart_type for _, _, chart_type, _ in TEMPLATE_PAGES} <= set(TEMPLATES))

    def test_previous_year_beside_a_table_is_drawn_as_a_previous_period_not_a_plan(self):
        s = {'label': 'AC vs PY', 'chartType': 'COLUMN_HORIZONTAL', 'category': 'Region[Region]',
             'measures': {'AC': VALUES['AC'], 'PY': VALUES['PY']}}
        styles = appearance(recipe_chart(model(), s, Registry()))['measuresStyle']
        self.assertEqual((styles['PY']['pattern'], styles['PY']['fillColor']), ('solid', '#bfbfbf'))
        self.assertNotIn('PL', styles)


class RecipeGuide(unittest.TestCase):
    def test_guide_table_matches_the_recipe_catalog(self):
        import re
        text = (ROOT / 'references/ibcs-charts.md').read_text(encoding='utf-8')
        rows = re.findall(r'^\| (C\d\d) \| ([^|]+) \| `([A-Z_]+)`', text, re.M)
        self.assertEqual({code: (name.strip(), chart_type) for code, name, chart_type in rows},
                         {code: (name, types[0]) for code, (name, types, _) in RECIPES.items()})

    def test_guide_color_table_matches_the_chart_theme(self):
        import re
        text = (ROOT / 'references/ibcs-charts.md').read_text(encoding='utf-8')
        palette = ibcs_palette()
        rows = re.findall(r'^\| [^|]+ \| [^|]+ \| (AC|PY|PL|FC) \| (\w+) \| `(#[0-9A-Fa-f]{6})` \|$', text, re.M)
        self.assertEqual({bucket: (fill, color) for bucket, fill, color in rows},
                         {bucket: (entry['pattern'], entry['fillColor']) for bucket, entry in palette['measures'].items()})
        variance = dict(re.findall(r'^\| (Desirable|Undesirable) variance \| [^|]+ \| \| solid \| `(#[0-9A-Fa-f]{6})` \|$', text, re.M))
        self.assertEqual(variance, {'Desirable': palette['variance']['positive'], 'Undesirable': palette['variance']['negative']})
        self.assertIn('greys from `' + palette['series'][0] + '`', text)
        self.assertIn('(`' + palette['variance']['neutral'] + '`)', text)

    def test_ibcs_and_stacked_requests_route_to_the_guide(self):
        from runtime.discovery import discover
        for query in ('stacked charts', 'IBCS C01 stacked column', 'waterfall chart'):
            self.assertEqual(discover(query)['modules'][0]['id'], 'IBCS-CHARTS', query)


class DashboardCharts(unittest.TestCase):
    def test_plain_column_chart_selects_its_template(self):
        p = column_chart(model(), {'category': 'Region[Region]', 'field': 'Metrics[Units]', 'label': 'Units'}, Registry())
        self.assertEqual((p['chartType'], p['visualState']['chartType']), ('COLUMN_VERTICAL', 'COLUMN_VERTICAL'))
        self.assertEqual(buckets(p), [('Region[Region]', 'axis'), ('Metrics[Units]', 'AC')])

    def test_variance_chart_keeps_both_selectors_on_the_integrated_template(self):
        p = column_chart(model(), {'category': 'Region[Region]', 'field': 'Metrics[Units]',
                                   'comparisonField': 'Metrics[Price]', 'label': 'Units vs price'}, Registry())
        self.assertEqual((p['chartType'], p['visualState']['chartType']),
                         ('COLUMN_INTEGRATED_VERTICAL', 'COLUMN_INTEGRATED_VERTICAL'))

    def test_dispatcher_routes_recipe_specs(self):
        p = chart(model(), spec('C04', 'AC', 'PL'), Registry())
        self.assertEqual(p['chartType'], 'COLUMN_HORIZONTAL')
        p = chart(model(), {'category': 'Region[Region]', 'field': 'Metrics[Units]', 'label': 'Units'}, Registry())
        self.assertEqual(p['chartType'], 'COLUMN_VERTICAL')

    def test_generated_dashboard_carries_recipe_charts(self):
        from runtime.planning_presentation import build_application
        s = {'name': 'IBCS review', 'sheets': [{'name': 'Units', 'rows': ['Region[Region]'], 'columns': ['Period[Month]'],
              'measures': [{'key': 'units', 'label': 'Units', 'kind': 'Native', 'source': 'Metrics[Units]'}]}],
             'dashboards': [{'name': 'Review', 'owner': 'Units', 'slicers': [{'field': 'Region[Region]'}], 'cards': [],
                             'charts': [spec('C01', 'AC', 'PL', 'FC', 'stack'), spec('C04', 'AC', 'PL')]}]}
        result = build_application(model(), s)
        charts = [o['properties'] for o in result['raw'].values()
                  if o.get('properties', {}).get('chartType') in TEMPLATES]
        self.assertEqual(sorted(p['chartType'] for p in charts), ['COLUMN_HORIZONTAL', 'STACKED_COLUMN_VERTICAL'])
        for p in charts:
            self.assertEqual(p['visualState']['chartType'], p['chartType'])
            self.assertEqual(chart_theme(p), 'ibcs')
            audit_chart_filters(p)


if __name__ == '__main__':
    unittest.main()
