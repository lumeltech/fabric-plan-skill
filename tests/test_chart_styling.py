"""Chart styling written as the product's own AI chart schema: keys, placement and page reach."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tests'))  # reuse the offline dashboard example
import unittest
from pathlib import Path
from runtime.chart_styling import (FIELD, ai_chart_state, apply_chart_style, chart_style, merge_styles,
                                   with_chart_style)
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
        p = apply_chart_style(props(), STYLE)
        self.assertEqual(p[FIELD]['canvas']['background'], '#fafafa')
        self.assertEqual(p['visualState'], {})
        self.assertEqual(chart_style(p)['dataLabel']['measures']['Units']['bold'], True)
        self.assertIsNone(chart_style(props()))

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
        self.assertEqual(p[FIELD]['dataLabel']['measures']['Units']['position'], 'outside')
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
            self.assertEqual(p[FIELD]['dataLabel']['all']['fontSize'], 10)
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
