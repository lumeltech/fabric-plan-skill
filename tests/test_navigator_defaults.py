"""Regression for the disabled-icon topPadding dashboard crash."""
import copy
import unittest
from pathlib import Path
from runtime.codec import load
from runtime.construct import navigator
from runtime.navigator_api import state
from runtime.navigator_defaults import complete_defaults, require_complete_defaults


class NavigatorDefaultsTests(unittest.TestCase):
    def assert_renderable(self, value):
        shape = value['style']['DEFAULT']['shapeState']
        # These nested values are accessed even when the icon is disabled.
        for padding in (shape['padding'], shape['text']['padding'], shape['icon']['padding']):
            self.assertGreaterEqual(padding['topPadding'], 0)
            self.assertGreaterEqual(padding['bottomPadding'], 0)
            self.assertGreaterEqual(padding['leftPadding'], 0)
            self.assertGreaterEqual(padding['rightPadding'], 0)
            self.assertIsInstance(padding['isEnabled'], bool)
            self.assertIsInstance(padding['isCustomPaddingSize'], bool)
        self.assertIn('customIcon', shape['icon']['iconTypeMapping']['default'])
        self.assertEqual(shape['text']['fontFamily'], 'Arial')
        self.assertTrue(require_complete_defaults(value))

    def test_all_new_navigator_kinds_include_disabled_icon_defaults(self):
        for kind in ('NAVIGATOR_BUTTON', 'PAGE_NAVIGATOR_TABS', 'BOOKMARK_TABS'):
            with self.subTest(kind=kind):
                value = state(kind)
                self.assertFalse(value['style']['DEFAULT']['shapeState']['icon']['isEnabled'])
                self.assert_renderable(value)

    def test_current_fixture_is_complete_without_runtime_repair(self):
        fixture = load(Path(__file__).resolve().parents[1] / 'fixtures/navigator-builder-20261112.json')
        self.assert_renderable(fixture)

    def test_documented_legacy_recipes_preserve_corner_profile(self):
        for recipe in range(1, 6):
            with self.subTest(recipe=recipe):
                value = navigator(recipe)
                self.assert_renderable(value)
                corner = value['style']['DEFAULT']['shapeState']['cornerRadius']
                self.assertIn('radiusTopLeft', corner)
                self.assertNotIn('topLeft', corner)

    def test_sparse_icon_is_completed_without_mutating_caller_or_overrides(self):
        value = state('PAGE_NAVIGATOR_TABS', selected_pages=['page-a'], caption='Review',
                      palette={'activeText': '#123456'})
        shape = value['style']['DEFAULT']['shapeState']
        shape['icon'] = {'isEnabled': False, 'padding': {'topPadding': 12},
                         'iconTypeMapping': {'page-a': {'src': 'provided-icon'}}}
        del shape['text']['padding']
        original = copy.deepcopy(value)
        result = complete_defaults(value)
        self.assertEqual(value, original)
        self.assert_renderable(result)
        self.assertEqual(result['style']['DEFAULT']['shapeState']['icon']['padding']['topPadding'], 12)
        self.assertEqual(result['style']['DEFAULT']['shapeState']['icon']['iconTypeMapping']['page-a'], {'src': 'provided-icon'})
        self.assertEqual(result['navigatorTabsState'], original['navigatorTabsState'])
        self.assertEqual(result['style']['DEFAULT']['shapeState']['text']['value'], 'Review')
        self.assertEqual(result['style']['DEFAULT']['shapeState']['cornerRadius'], shape['cornerRadius'])
        for name in ('HOVER', 'PRESSED', 'ACTIVE'):
            self.assertEqual(result['style'][name], original['style'][name])
        self.assertEqual(result['style']['ACTIVE']['shapeState']['icon'], {'color': '#123456'})
        self.assertEqual(complete_defaults(result), result)

    def test_new_button_keeps_destination_caption_and_palette(self):
        value = state('NAVIGATOR_BUTTON', page_target='page-b', caption='Supply',
                      palette={'fill': '#234567', 'activeText': '#FEDCBA'})
        self.assert_renderable(value)
        self.assertEqual(value['navigatorButtonState']['pageDestinationId'], 'page-b')
        self.assertEqual(value['style']['DEFAULT']['shapeState']['text']['value'], 'Supply')
        self.assertEqual(value['style']['DEFAULT']['shapeState']['fill']['fillColor'], '#234567')
        self.assertEqual(value['style']['ACTIVE']['shapeState']['icon']['color'], '#FEDCBA')

    def test_incomplete_state_rejected_by_read_only_gate(self):
        value = state()
        value['style']['DEFAULT']['shapeState']['icon'] = {'isEnabled': False}
        original = copy.deepcopy(value)
        with self.assertRaisesRegex(ValueError, 'Incomplete Navigator'):
            require_complete_defaults(value)
        self.assertEqual(value, original)

    def test_null_and_invalid_padding_fail_before_network(self):
        for key, bad in (('padding', None), ('padding', {'topPadding': '4'}),
                         ('padding', {'topPadding': -1}), ('padding', {'topPadding': float('nan')}),
                         ('padding', {'isEnabled': 'false'}), ('iconTypeMapping', None)):
            with self.subTest(bad=bad):
                value = state()
                value['style']['DEFAULT']['shapeState']['icon'][key] = bad
                with self.assertRaises(ValueError):
                    complete_defaults(value)
        value = state()
        value['style']['ACTIVE']['shapeState']['icon'] = {'padding': None}
        with self.assertRaises(ValueError):
            complete_defaults(value)

    def test_application_default_gate_catches_sparse_dashboard_navigator(self):
        from runtime.application_defaults import check_application_defaults
        from runtime.planning_presentation import build_application
        root = Path(__file__).resolve().parents[1]
        built = build_application(load(root/'fixtures/model.json'), load(root/'fixtures/finance-spec.json'))
        name = next(k for k,v in built['raw'].items() if 'navigatorState' in v.get('properties',{}).get('visualState',{}))
        result = check_application_defaults(built['raw'], built['home'])
        self.assertEqual(result['navigatorDefaultsChecked'], len(built['dashboardIdentities']))
        built['raw'][name]['properties']['visualState']['navigatorState']['style']['DEFAULT']['shapeState']['icon'] = {'isEnabled': False}
        with self.assertRaisesRegex(ValueError, 'Incomplete Navigator'):
            check_application_defaults(built['raw'], built['home'])


if __name__ == '__main__':
    unittest.main()
