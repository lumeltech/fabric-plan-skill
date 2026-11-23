import copy, math, unittest
from runtime.surfaces import home_item, home_layout
from runtime.home_fit import audit_home_fit, readable_home_layout
from runtime.workflow import compile_home

class HomeFitTests(unittest.TestCase):
    def setUp(self):
        self.items = [home_item('text', 'Your forecast assumption', 'Closed periods use actuals. Open periods: COLUMN.ADDMONTH(-1) * 1.1.'),
                      home_item('text', 'Calendar coverage', 'Review available periods before editing the forecast.'),
                      home_item('preview-cards')]
        self.rows = [{'id': 'text-row', 'itemIds': [x['id'] for x in self.items[:2]], 'widths': [60, 40], 'height': 160},
                     {'id': 'cards-row', 'itemIds': [self.items[2]['id']], 'widths': [None], 'height': 260}]

    def test_observed_percentage_like_widths_rejected(self):
        with self.assertRaisesRegex(ValueError, 'pixels'):
            home_layout(self.items, self.rows)
        report = audit_home_fit({'items': self.items, 'rows': self.rows})
        self.assertFalse(report['passed'])
        self.assertIn('narrow-text', {x['code'] for x in report['issues']})

    def test_unknown_viewport_stacks_and_releases_heights(self):
        before = copy.deepcopy((self.items, self.rows))
        result = readable_home_layout(self.items, self.rows)
        self.assertEqual(result['items'], self.items)
        self.assertEqual((self.items, self.rows), before)
        self.assertEqual([r['itemIds'][0] for r in result['rows']], [x['id'] for x in self.items])
        self.assertEqual(result['rows'][0]['id'], 'text-row')
        self.assertEqual(result['rows'][-1]['id'], 'cards-row')
        self.assertEqual(len({r['id'] for r in result['rows']}), 3)
        for row in result['rows']:
            self.assertEqual(row['widths'], [None])
            self.assertIsNone(row['height'])
            self.assertIsNone(row['defaultHeightRatio'])
            self.assertNotIn('isHeightManual', row)
        self.assertEqual(audit_home_fit(result)['issues'], [])

    def test_known_width_keeps_two_flexible_columns(self):
        result = readable_home_layout(self.items, self.rows, content_width_px=1000)
        self.assertEqual(result['rows'][0]['widths'], [None, None])
        self.assertEqual(len(result['rows']), 2)
        self.assertEqual(audit_home_fit(result, 1000)['issues'], [])
        self.assertEqual(len(readable_home_layout(self.items, self.rows, content_width_px=600)['rows']), 3)

    def test_invalid_dimensions_rejected(self):
        for value in (True, False, 0, -1, math.inf, math.nan, '60%'):
            with self.subTest(value=value):
                for field in ('widths', 'height'):
                    row = {'itemIds': [self.items[0]['id']], field: [value] if field == 'widths' else value}
                    with self.assertRaises(ValueError): home_layout(self.items[:1], [row])
                with self.assertRaises(ValueError): readable_home_layout(self.items, content_width_px=value)

    def test_fixed_height_warning_is_not_rendering_certification(self):
        layout = home_layout(self.items[:1], [{'itemIds': [self.items[0]['id']], 'widths': [600], 'height': 60}])
        report = audit_home_fit(layout, 800)
        self.assertTrue(report['passed'])
        self.assertEqual(report['issues'][0]['code'], 'fixed-text-height')
        self.assertEqual(report['rendering'], 'not-tested')

    def test_overflow_and_insufficient_flexible_remainder(self):
        layout = {'items': self.items[:2], 'rows': [{'itemIds': [x['id'] for x in self.items[:2]], 'widths': [600, 600]}]}
        self.assertFalse(audit_home_fit(layout, 1000)['passed'])
        layout['rows'][0]['widths'] = [600, None]
        self.assertIn('narrow-flex-text', {x['code'] for x in audit_home_fit(layout, 800)['issues']})

    def test_workflow_uses_readable_constructor(self):
        layout = compile_home({'blocks': [{'key': 'a', 'type': 'text', 'title': 'Your forecast assumption'},
                                        {'key': 'b', 'type': 'text', 'title': 'Calendar coverage'}],
                               'rows': [{'blocks': ['a', 'b'], 'widths': [60, 40], 'height': 160}]})
        self.assertEqual(len(layout['rows']), 2)
        self.assertTrue(all(r['height'] is None and r['widths'] == [None] for r in layout['rows']))

    def test_duplicate_row_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, 'row identity'):
            home_layout(self.items[:2], [{'id': 'same', 'itemIds': [x['id']]} for x in self.items[:2]])

    def test_hero_and_cards_stay_standalone(self):
        hero = home_item('header-image-text', 'Sales intelligence')
        result = readable_home_layout([hero, self.items[-1]])
        self.assertEqual(len(result['rows']), 2)
        with self.assertRaises(ValueError):
            readable_home_layout([hero, self.items[0]], [{'itemIds': [hero['id'], self.items[0]['id']]}], 1000)

if __name__ == '__main__': unittest.main()
