"""Chart styling split across its two channels: the data-label store slice and the AI schema."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tests'))  # reuse the offline dashboard example
import unittest
from pathlib import Path
from runtime.chart_styling import (DATALABELS, FIELD, ai_chart_state, apply_chart_style, chart_style,
                                   data_labels, merge_styles, with_chart_style)
from runtime.construct import build
from runtime.ibcs_charts import chart_theme, describe, recipe_chart
from runtime.identity import Registry
from runtime.intelligence import card, chart, column_chart
from runtime.codec import load
from test_context_intelligence import example

ROOT = Path(__file__).resolve().parents[1]
STYLE = {'background': '#fafafa', 'font': {'color': '#1f1f1f', 'size': 12},
         'dataLabels': {'all': {'show': True, 'fontSize': 10},
                        'measures': {'Units': {'bold': True, 'position': 'outside'}},
                        'variance': {'show': True, 'display': 'minMax', 'color': '#cc0000'}}}


def props(visual_type=50):
    return {'visualType': visual_type, 'visualState': {}}


def waterfall_props():
    """One Waterfall Sheet chart as exported: AC and PY buckets, commonSettings left at its default."""
    return {'visualType': 50, 'chartType': 'COLUMN_WATERFALL_VERTICAL',
            'visualState': {'chartType': 'COLUMN_WATERFALL_VERTICAL', 'reportMode': True},
            'pivotAssignments': [
                {'bucketId': 'axis', 'dataRoleType': 'Grouping', 'name': 'Product', 'id': 'financials[Product]'},
                {'bucketId': 'AC', 'dataRoleType': 'Measure', 'name': ' Sales', 'customName': 'Sales'},
                {'bucketId': 'PY', 'dataRoleType': 'Measure', 'name': 'Gross Sales', 'customName': 'Gross Sales'}]}


def saved_labels(p):
    """The data-label slice as the chart store reads it off the saved definition."""
    from runtime.codec import loads
    value = p['visualState'].get(DATALABELS)
    return loads(value) if isinstance(value, str) else value


class SchemaState(unittest.TestCase):
    def test_style_maps_onto_the_sections_the_compiler_reads(self):
        self.assertEqual(ai_chart_state({'theme': 'ibcs', **STYLE}),
                         {'canvas': {'theme': 'ibcs', 'background': '#fafafa',
                                     'font': {'color': '#1f1f1f', 'size': 12}},
                          'dataLabel': {'all': {'show': True, 'fontSize': 10},
                                        'measures': {'Units': {'bold': True, 'position': 'outside'}},
                                        'variance': {'show': True, 'display': 'minMax', 'color': '#cc0000'}}})

    def test_a_key_or_value_the_validator_rejects_fails_the_build(self):
        bad = [{'fill': '#ffffff'}, {'font': {'weight': 'bold'}}, {'theme': 'corporate'},
               {'dataLabels': {'labelFormat': {}}}, {'dataLabels': {'all': {'colour': '#fff'}}},
               {'dataLabels': {'all': {'color': ''}}}, {'dataLabels': {'all': {'display': 'topMost'}}},
               {'dataLabels': {'all': {'position': 'middle'}}}, {'dataLabels': {'all': {'fontSize': '10'}}},
               {'dataLabels': {'all': {'show': 'yes'}}}, {'dataLabels': {'measures': {}}},
               {'dataLabels': {'measures': {'Units': {'underline': 'true'}}}},
               {'dataLabels': {'variance': {'underline': True}}}]
        for style in bad:
            with self.subTest(style=style):
                with self.assertRaises(ValueError):
                    ai_chart_state(style)

    def test_a_style_that_sets_nothing_is_refused(self):
        for empty in ({}, {'dataLabels': {}}):
            with self.subTest(style=empty):
                with self.assertRaises(ValueError) as caught:
                    apply_chart_style(props(), empty)
                self.assertIn('sets nothing', str(caught.exception))

    def test_the_state_is_a_sibling_of_the_saved_slices(self):
        p = apply_chart_style(waterfall_props(), {'background': '#fafafa', 'font': STYLE['font'],
                                                 'dataLabels': {'measures': {'Sales': {'bold': True}}}})
        self.assertEqual(p[FIELD]['canvas']['background'], '#fafafa')
        self.assertIn(FIELD, p)                      # beside visualState, not inside it
        self.assertIn(DATALABELS, p['visualState'])  # and labels inside visualState
        self.assertEqual(data_labels(p)['labelStyle'][' Sales']['fontStyle'], {'isBold': True})
        self.assertIsNone(chart_style(props()))
        self.assertIsNone(data_labels(props()))

    def test_only_an_analytics_plus_chart_carries_chart_style(self):
        for visual_type in (25, 203):
            with self.subTest(visualType=visual_type):
                with self.assertRaises(ValueError) as caught:
                    apply_chart_style(props(visual_type), STYLE)
                self.assertIn('visualType 50', str(caught.exception))

    def test_a_later_style_replaces_only_the_options_it_names(self):
        page = {'background': '#111111', 'font': {'size': 12}, 'dataLabels': {'all': {'fontSize': 10}}}
        chart_specific = {'background': '#222222', 'font': {'color': '#eeeeee'},
                          'dataLabels': {'measures': {'Units': {'bold': True}}}}
        self.assertEqual(merge_styles(page, chart_specific),
                         {'background': '#222222', 'font': {'size': 12, 'color': '#eeeeee'},
                          'dataLabels': {'all': {'fontSize': 10}, 'measures': {'Units': {'bold': True}}}})
        self.assertEqual(page['font'], {'size': 12})
        carried = with_chart_style(props(), {'canvas': {'background': '#111111', 'font': {'size': 12}}})
        self.assertEqual(with_chart_style(carried, {'canvas': {'background': '#222222'},
                                                    'dataLabel': {'all': {'show': True}}})[FIELD],
                         {'canvas': {'background': '#222222', 'font': {'size': 12}},
                          'dataLabel': {'all': {'show': True}}})


class StoreSliceDataLabels(unittest.TestCase):
    """Data labels written where the format panel writes them, so no feature switch is needed."""

    def test_labels_land_in_the_chart_store_slice_not_the_ai_channel(self):
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'all': {
            'bold': True, 'color': 'red', 'background': 'green'}}})
        saved = saved_labels(p)
        for key in ('default', ' Sales', 'Gross Sales'):
            entry = saved['labelStyle'][key]
            self.assertEqual(entry['fontStyle'], {'isBold': True})
            self.assertEqual(entry['fontColor'], 'red')
            self.assertFalse(entry['contrastColor'])
            self.assertEqual(entry['background'], 'green')
            self.assertTrue(entry['showBackgroundColor'])
        self.assertNotIn(FIELD, p)

    def test_the_store_keys_labels_by_measure_name_not_by_bucket(self):
        """savePropertyAgainstRole is false in the product's defaults, so AC/PY are dead keys.

        A key absent from the built default labelStyle is dropped on load
        (DataLabelStateService.ts:791), which is how a role-keyed write saves cleanly and renders
        as nothing.
        """
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'all': {'bold': True}}})
        self.assertEqual(sorted(saved_labels(p)['labelStyle']), [' Sales', 'Gross Sales', 'default'])
        self.assertNotIn('AC', saved_labels(p)['labelStyle'])
        self.assertNotIn('PY', saved_labels(p)['labelStyle'])

    def test_the_measure_field_name_is_used_exactly_as_the_model_spells_it(self):
        """The key is the measure's fieldName (' Sales', leading space), not its display label."""
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'measures': {'Sales': {'bold': True}}}})
        self.assertEqual(list(saved_labels(p)['labelStyle']), [' Sales'])

    def test_the_slice_is_a_stringified_value_like_the_other_sections(self):
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'all': {'bold': True}}})
        self.assertIsInstance(p['visualState'][DATALABELS], str)

    def test_a_measure_is_addressed_by_the_name_the_chart_shows(self):
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'measures': {'Sales': {'bold': True}}}})
        self.assertEqual(list(saved_labels(p)['labelStyle']), [' Sales'])

    def test_a_measure_the_chart_does_not_have_fails_the_build(self):
        with self.assertRaises(ValueError) as caught:
            apply_chart_style(waterfall_props(), {'dataLabels': {'measures': {'Margin': {'bold': True}}}})
        self.assertIn('Margin', str(caught.exception))
        self.assertIn('Sales', str(caught.exception))

    def test_show_is_the_only_way_labels_are_switched_on_or_off(self):
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'all': {'bold': True}}})
        self.assertNotIn('enabled', saved_labels(p)['labelStyle'][' Sales'])
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'all': {'show': False}}})
        self.assertFalse(saved_labels(p)['labelStyle'][' Sales']['enabled'])

    def test_a_second_write_keeps_the_labels_it_does_not_name(self):
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'measures': {'Sales': {'bold': True}}}})
        p = apply_chart_style(p, {'dataLabels': {'measures': {'Gross Sales': {'color': 'red'}}}})
        saved = saved_labels(p)['labelStyle']
        self.assertEqual(saved[' Sales'], {'fontStyle': {'isBold': True}})
        self.assertEqual(saved['Gross Sales'], {'fontColor': 'red', 'contrastColor': False})

    def test_a_label_option_the_product_does_not_take_is_refused(self):
        for bad in ({'all': {'colour': 'red'}}, {'all': {'position': 'middle'}}, {'labelStyle': {}},
                    {'all': {'bold': 'yes'}}):
            with self.subTest(labels=bad):
                with self.assertRaises(ValueError):
                    apply_chart_style(waterfall_props(), {'dataLabels': bad})

    def test_only_an_analytics_plus_chart_carries_data_labels(self):
        with self.assertRaises(ValueError):
            apply_chart_style(props(203), {'dataLabels': {'all': {'bold': True}}})

    def test_a_chart_with_no_bound_measures_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            apply_chart_style({'visualType': 50, 'visualState': {}, 'pivotAssignments': []},
                              {'dataLabels': {'all': {'bold': True}}})
        self.assertIn('no bound measures', str(caught.exception))

    def test_data_labels_read_back_from_the_definition(self):
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'all': {'bold': True}}})
        self.assertEqual(data_labels(p)['labelStyle'][' Sales'], {'fontStyle': {'isBold': True}})
        self.assertIsNone(data_labels(waterfall_props()))

    def test_a_measure_style_overrides_only_the_options_it_names(self):
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'all': {'fontSize': 10, 'bold': False},
                                                                 'measures': {'Sales': {'bold': True}}}})
        saved = saved_labels(p)['labelStyle']
        self.assertEqual(saved[' Sales'], {'fontSize': 10, 'isUserChangedFontSize': True, 'fontStyle': {'isBold': True}})
        self.assertEqual(saved['Gross Sales'], {'fontSize': 10, 'isUserChangedFontSize': True, 'fontStyle': {'isBold': False}})

    def test_a_font_size_is_marked_as_user_changed(self):
        """Without isUserChangedFontSize a bar-width-based size replaces the authored one at render."""
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'all': {'fontSize': 10}}})
        for entry in saved_labels(p)['labelStyle'].values():
            self.assertEqual(entry['fontSize'], 10)
            self.assertTrue(entry['isUserChangedFontSize'])

    def test_variance_labels_still_need_the_ai_channel(self):
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'variance': {'show': True, 'display': 'minMax'}}})
        self.assertEqual(p[FIELD], {'dataLabel': {'variance': {'show': True, 'display': 'minMax'}}})
        self.assertNotIn(DATALABELS, p['visualState'])


class ThemeOwnedFields(unittest.TestCase):
    """The product treats label color, background, size and bold as theme-derived and strips them."""

    def test_describe_names_the_styled_fields_a_theme_change_will_strip(self):
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'all': {
            'bold': True, 'color': 'red', 'background': 'green', 'fontSize': 10, 'position': 'outside'}}})
        self.assertEqual(describe(p)['labelThemeFields'],
                         ['background', 'fontColor', 'fontSize', 'fontStyle.isBold'])

    def test_a_style_of_only_store_safe_fields_reports_nothing_to_strip(self):
        p = apply_chart_style(waterfall_props(), {'dataLabels': {'all': {'show': True, 'position': 'auto'}}})
        self.assertEqual(describe(p)['labelThemeFields'], [])


class Builders(unittest.TestCase):
    def model(self):
        return load(ROOT / 'assets/fixtures/model.json')

    def chart_spec(self, **extra):
        return {'label': 'Sales by Region', 'chartType': 'COLUMN_VERTICAL', 'category': 'Region[Region]',
                'measures': {'AC': {'field': 'Metrics[Units]', 'label': 'Units'},
                             'PY': {'field': 'Metrics[Price]', 'label': 'Price'}}, **extra}

    def test_recipe_chart_keeps_its_theme_and_gains_the_style(self):
        p = recipe_chart(self.model(), self.chart_spec(style=STYLE), Registry())
        self.assertEqual(chart_theme(p), 'ibcs')
        saved = data_labels(p)['labelStyle']
        self.assertEqual(saved['Units']['position'], 'outside')
        self.assertTrue(saved['Units']['fontStyle']['isBold'])
        self.assertEqual(saved['Price']['fontSize'], 10)
        self.assertTrue(saved['Units']['enabled'])
        self.assertEqual(p[FIELD]['dataLabel']['variance']['display'], 'minMax')
        self.assertEqual(describe(p)['style']['canvas']['background'], '#fafafa')

    def test_a_chart_on_the_plan_theme_can_still_be_styled(self):
        p = recipe_chart(self.model(), self.chart_spec(theme='plan', style={'theme': 'ibcs'}), Registry())
        self.assertEqual(chart_theme(p), 'plan')
        self.assertEqual(p[FIELD], {'canvas': {'theme': 'ibcs'}})

    def test_plain_column_chart_and_card_take_a_style(self):
        model = self.model()
        column = column_chart(model, {'label': 'Sales by Region', 'category': 'Region[Region]',
                                      'field': 'Metrics[Units]', 'style': STYLE}, Registry())
        self.assertEqual(column[FIELD]['canvas']['font']['size'], 12)
        kpi = card(model, {'field': 'Metrics[Units]', 'label': 'Units',
                           'style': {'background': '#fafafa'}}, Registry())
        self.assertEqual(kpi[FIELD], {'canvas': {'background': '#fafafa'}})
        self.assertEqual(chart(model, {'label': 'Sales by Region', 'category': 'Region[Region]',
                                       'field': 'Metrics[Units]', 'style': STYLE}, Registry())[FIELD],
                         column[FIELD])

    def test_an_unknown_style_option_is_named(self):
        with self.assertRaises(ValueError) as caught:
            chart(self.model(), {'label': 'Sales by Region', 'category': 'Region[Region]',
                                 'field': 'Metrics[Units]', 'style': {'shadow': True}}, Registry())
        self.assertIn('Unconsumed chart style options: shadow', str(caught.exception))


class PageReach(unittest.TestCase):
    def built(self):
        model, spec = example()
        page = spec['dashboards'][0]
        page['style'] = {'background': '#fafafa', 'font': {'color': '#1f1f1f'},
                         'dataLabels': {'all': {'fontSize': 10}}}
        page['charts'] = [{'label': 'Amount by area', 'category': 'Geography[Area]', 'field': 'Facts[Amount]',
                           'aggregation': 'sum', 'style': {'background': '#000000'}},
                          {'label': 'Total by area', 'category': 'Geography[Area]', 'field': 'Facts[Total]'}]
        spec['requiredCapabilities'].append('intelligence.charts')
        return build(model, spec)

    def test_a_page_style_reaches_every_card_and_chart(self):
        raw = self.built()['raw']
        named = {}
        for path, entry in raw.items():
            if not path.endswith('properties.json'):
                continue
            p = entry['properties']
            if p.get('visualType') == 50:
                named[p['layerProperties']['layerProperties']['name']] = p
        self.assertEqual(len(named), 5)  # three KPI cards and two charts
        for p in named.values():
            self.assertEqual(p[FIELD]['canvas']['font']['color'], '#1f1f1f')
            self.assertEqual({e['fontSize'] for e in data_labels(p)['labelStyle'].values()}, {10})
        charts = [name for name, p in named.items() if p['visualState'].get('chartType') != 'CARD']
        self.assertEqual(len(charts), 2)
        self.assertEqual({named[n][FIELD]['canvas']['background'] for n in charts}, {'#fafafa', '#000000'})
        self.assertEqual(named['Amount by area'][FIELD]['canvas']['background'], '#000000')

    def test_a_page_with_no_style_writes_no_chart_state(self):
        model, spec = example()
        for path, entry in build(model, spec)['raw'].items():
            if path.endswith('properties.json'):
                self.assertNotIn(FIELD, entry['properties'])


if __name__ == '__main__':
    unittest.main()
