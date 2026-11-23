import unittest
from unittest.mock import patch
from runtime.transport import Client
from runtime.public_alignment import check_placements, fresh_matrix_ids
from runtime.codec import load
from runtime.planning_presentation import build_application
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublicDashboardDelivery(unittest.TestCase):
    def test_default_definition_contains_all_visual_rectangles(self):
        built = build_application(load(ROOT/'fixtures/context-dashboard-model.json'),
                                  load(ROOT/'fixtures/context-dashboard-spec.json'))
        for dashboard in built['dashboardIdentities']:
            self.assertEqual(check_placements(built['raw'], dashboard)['visualCount'], len(dashboard['placements']))
            vid = dashboard['ownerGuid']
            owner, = [s for s in built['raw']['definition.json']['sheets']
                      if any(v['visualId'] == vid and not v.get('isEmbedded') for v in s['workloadItemEntityVisuals'])]
            self.assertTrue(owner['isHidden'])
            original = built['raw'][f"sheets/{owner['recordGuid']}/visuals/{vid}/properties.json"]['properties']
            evidence = check_placements(built['raw'], dashboard)
            self.assertEqual(evidence['embeddedPlacement'], 'report-local-ids')
            self.assertEqual(evidence['rendering'], 'not-tested')
            self.assertNotEqual(original['position'], {k: dashboard['placements'][vid][k] for k in ('x','y')})

    def test_ten_pages_share_two_sources_and_keep_page_specific_rectangles(self):
        from copy import deepcopy
        spec = load(ROOT/'fixtures/context-dashboard-spec.json')
        source = deepcopy(spec['sheets'][0])
        source['name'] = 'Second planning sheet'
        spec['sheets'].append(source)
        template = spec['dashboards'][0]
        spec['dashboards'] = [
            {**deepcopy(template), 'name': f'Page {i + 1}', 'owner': spec['sheets'][i % 2]['name'],
             'width': 1400 + 32 * i, 'viewport': {'width': 1600, 'height': 1000}}
            for i in range(10)]
        app = build_application(load(ROOT/'fixtures/context-dashboard-model.json'), spec)
        raw = app['raw']
        owners = raw['definition.json']['sheets'][:2]
        self.assertEqual(len(app['dashboardIdentities']), 10)
        widths = set()
        for i, page in enumerate(app['dashboardIdentities']):
            expected_id = str(i % 2 + 1)
            source_guid = owners[i % 2]['workloadItemEntityVisuals'][0]['visualId']
            self.assertEqual(source_guid, page['ownerGuid'])
            props = raw[f"sheets/{page['sheetGuid']}/sheet.json"]['properties']
            override, = props['reactiveVisualProperties']
            self.assertEqual(override['visualId'], expected_id)
            self.assertEqual(override['properties']['originEntityId'], expected_id)
            self.assertEqual(check_placements(raw, page)['embeddedPlacement'], 'report-local-ids')
            widths.add(override['properties']['dimension']['width'])
        self.assertEqual(len(widths), 10)

    def test_origin_and_visual_counters_are_independent(self):
        sheets = [
            {'workloadItemEntityVisuals': [
                {'visualId': 'label', 'visualType': 'TEXT'},
                {'visualId': 'a', 'visualType': 'PLANNING'}]},
            {'workloadItemEntityVisuals': [
                {'visualId': 'a', 'visualType': 'PLANNING', 'isEmbedded': True},
                {'visualId': 'b', 'visualType': 'PLANNING'}]}]
        self.assertEqual(fresh_matrix_ids(sheets), {
            'a': {'originEntityId': '1', 'visualId': '2'},
            'b': {'originEntityId': '2', 'visualId': '3'}})

    def test_internal_endpoints_rejected_before_credentials_or_submission(self):
        client = Client('https://api.fabric.microsoft.com/v1', 'UNSET_TEST_TOKEN', journal=ROOT,
                        adapter=lambda *args: self.fail('Unexpected submission'))
        for route in ('/CoreAPI/v1/access/roles/layout/', '/metadata/v201606/generatemwctokenv2'):
            with self.subTest(route=route), self.assertRaisesRegex(ValueError, 'public Fabric'):
                client.request('POST',route,label='forbidden')
