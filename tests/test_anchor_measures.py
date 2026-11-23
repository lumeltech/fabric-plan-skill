"""Offline preservation, owner evidence, business routing and native save boundary."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from runtime.anchor_measures import AnchorContractGap, apply_anchors, capture_context
from runtime.business_intent import plan_intent
from runtime.discovery import discover

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    p = json.loads((ROOT/'examples/anchor-measures/saved-profile.json').read_text(encoding='utf-8'))['properties']
    s = p['visualState']
    # Independent records must remain untouched regardless of anchor display.
    p['sentinelDataInput'] = {'formula': '["9007199254742020"] * 2',
                             'allow_input': {'BasedOnFormula': 'isOpen == 1'},
                             'storageMappings': {'leaf': 'unchanged'}, 'values': [1, 2, 3]}
    s['aggregation_config'] = {'measure_aggregation': {'123': {'row': 'AverageLeaf', 'column': 'AverageLeaf'}}}
    s['manage_measures'].append({'id': '123', 'label': 'Current Benefits', 'order': 90, 'visible': True, 'customSetting': 7})
    s['totals_config']['column_sub_total'] = None
    return p


def request(p, rows=None, cols=None):
    s = p['visualState']
    return {'measure_id': '123',
            'row_fields': [s['rowDimensions'][0]['externalKey']] if rows is None else rows,
            'column_fields': [s['columnDimensions'][0]['externalKey']] if cols is None else cols,
            'display_at_all_levels': False}


class AnchorTests(unittest.TestCase):
    def test_four_key_saved_profile_without_ui_enable_and_all_21_cases(self):
        p = fixture(); members = [m for m in p['visualState']['manage_measures'] if m.get('anchor_config')]
        self.assertEqual(len(members), 21)
        for m in members:
            self.assertEqual(set(m['anchor_config']), {'row_dimensions','col_dimensions','dimension_hash','display_at_all_levels'})
            self.assertFalse(m['anchor_config']['display_at_all_levels'])
        context = capture_context(p, 'owner')
        self.assertEqual(len(context['witnesses']), 21)

    def test_exact_id_binding_preservation_and_required_subtotal_exception(self):
        p = fixture(); before = copy.deepcopy(p)
        out = apply_anchors(p, 'owner', [request(p)])
        self.assertEqual(p, before)
        result = out['properties']; s = result['visualState']
        m = next(m for m in s['manage_measures'] if m['id']=='123')
        self.assertEqual(m['customSetting'], 7); self.assertTrue(m['visible'])
        self.assertEqual(m['anchor_config']['row_dimensions'], [s['rowDimensions'][0]['id']])
        self.assertGreater(int(m['anchor_config']['row_dimensions'][0]), 2**53)
        self.assertEqual(s['totals_config']['column_sub_total'], 'Left')
        # Remove only the requested edits; the full property graph is identical.
        del m['anchor_config']; s['totals_config']['column_sub_total'] = None
        self.assertEqual(result, before)

    def test_hidden_repetition_retains_formula_values_and_permissions(self):
        p = fixture()
        hidden = apply_anchors(p, 'owner', [request(p)])['properties']
        r = request(p); r['display_at_all_levels'] = True
        displayed = apply_anchors(p, 'owner', [r])['properties']
        self.assertEqual(hidden['sentinelDataInput'], p['sentinelDataInput'])
        m = next(m for m in displayed['visualState']['manage_measures'] if m['id']=='123')
        m['anchor_config']['display_at_all_levels'] = False
        self.assertEqual(displayed, hidden)

    def test_row_only_and_column_only_have_all_total_entry(self):
        p = fixture(); p['visualState']['totals_config']['column_grand_total'] = None
        a = apply_anchors(p, 'owner', [request(p, cols=[])])
        self.assertEqual(a['properties']['visualState']['totals_config']['column_grand_total'], 'Left')
        self.assertEqual(a['properties']['visualState']['totals_config']['column_sub_total'], None)
        p['visualState']['totals_config']['row_grand_total'] = None
        b = apply_anchors(p, 'owner', [request(p, rows=[])])
        self.assertEqual(b['properties']['visualState']['totals_config']['row_grand_total'], 'Top')

    def test_no_invented_product_parent(self):
        p = fixture(); product = p['visualState']['rowDimensions'][2]
        out = apply_anchors(p, 'owner', [request(p, rows=[product['externalKey']])])
        cfg = out['changes'][0]['after']
        self.assertEqual(cfg['row_dimensions'], [product['id']])

    def test_empty_unknown_duplicate_wrong_axis_and_label_rejected_atomically(self):
        p = fixture(); original = copy.deepcopy(p)
        cases = [request(p, rows=[], cols=[]), request(p, rows=['Entity Continent']),
                 request(p, cols=[p['visualState']['rowDimensions'][0]['externalKey']]),
                 {**request(p), 'measure_id': '999'}, {**request(p), 'is_enabled': True},
                 {**request(p), 'display_at_all_levels': 'false'}]
        for bad in cases:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                apply_anchors(p, 'owner', [request(p), bad])
            self.assertEqual(p, original)
        r = request(p); r['row_fields'] *= 2
        with self.assertRaises(ValueError):apply_anchors(p, 'owner', [r])

    def test_calendar_parent_must_be_selected(self):
        p = fixture(); month = p['visualState']['columnDimensions'][-1]
        with self.assertRaises(ValueError):apply_anchors(p, 'owner', [request(p, cols=[month['externalKey']])])
        all_columns = [d['externalKey'] for d in p['visualState']['columnDimensions']]
        out = apply_anchors(p, 'owner', [request(p, cols=list(reversed(all_columns)))])
        self.assertEqual(out['changes'][0]['after']['col_dimensions'], [d['id'] for d in p['visualState']['columnDimensions']])

    def test_first_anchor_computes_hash_and_conflicting_hashes_fail(self):
        p = fixture()
        for m in p['visualState']['manage_measures']:m.pop('anchor_config', None)
        first = apply_anchors(p, 'owner', [request(p)])
        self.assertEqual(first['hash_origin'], 'computed-current-pivot-xxh3')
        self.assertEqual(first['changes'][0]['after']['dimension_hash'], capture_context(p,'owner')['dimension_hash'])
        p = fixture(); p['visualState']['manage_measures'][0]['anchor_config']['dimension_hash'] = 'other'
        with self.assertRaisesRegex(AnchorContractGap, 'ANCHOR_HASH_CONFLICT'):capture_context(p, 'owner')

    def test_foreign_owner_stale_evidence_and_removed_dimension_rejected(self):
        p = fixture(); context = capture_context(p, 'owner')
        with self.assertRaises(AnchorContractGap):apply_anchors(p, 'different-owner', [request(p)], context=context)
        q = copy.deepcopy(p); q['visualState']['rowDimensions'].reverse()
        with self.assertRaises(AnchorContractGap):apply_anchors(q, 'owner', [request(q)], context=context)
        q = copy.deepcopy(p); q['visualState']['rowDimensions'].pop(0)
        with self.assertRaisesRegex(AnchorContractGap, 'ANCHOR_STALE_DIMENSIONS'):capture_context(q, 'owner')

    def test_hiding_entry_total_requires_deliberate_resolution(self):
        p = fixture()
        with self.assertRaisesRegex(ValueError, 'entry total is hidden'):
            apply_anchors(p, 'owner', [request(p)], expose_entry_totals=False)

    def test_business_variations_route_without_requiring_a_donor_hash(self):
        for query in ('regional benefits hidden employee leaf formulas', 'plant quarterly scrap assumptions',
                      'product price policy shared across regions', 'hide repeated assumptions at hierarchy levels'):
            self.assertIn('F20', [m['id'] for m in discover(query)['modules'][:3]])
        details = dict(measure='benefits', sheetGrain=['Region','Employee','Month'], rowDimensions=['Region'],
                       columnDimensions=['Year'], consumers=['Employee Cost'], displayAtAllLevels=False,
                       )
        brief = {'request':'Show regional benefits but only employee costs below.',
                 'requirements':[{'id':'display','text':'retain benefits in formulas, hide repeated rows',
                                  'intent':'display-anchor','details':details}]}
        planned = plan_intent(brief)
        self.assertTrue(planned['readyForAuthoring'])
        self.assertEqual([op['id'] for op in planned['requirements'][0]['operations']], ['anchor-construct'])
        self.assertEqual(planned['requirements'][0]['unresolved'], [])
        self.assertEqual(details['displayAtAllLevels'], False)

    def test_pool_is_not_misrouted_to_copy_and_no_dimensionless_constant(self):
        d = dict(measure='Bonus',sheetGrain=['Employee','Year'],rowDimensions=[],columnDimensions=['Year'],
                 eligibleScope='unlocked',aggregation='Sum',distribution='copy',consumers=['Cost'],
                 displayAtAllLevels=False,hashEvidence='current-owner-saved-anchor',valueSemantics='amount-pool')
        r = {'request':'Allocate a bonus pool','requirements':[{'id':'pool','text':'bonus pool',
             'intent':'shared-assumption','details':d}]}
        self.assertFalse(plan_intent(r)['readyForAuthoring'])
        d['distribution']='weights'; d['columnDimensions']=[]
        self.assertFalse(plan_intent(r)['readyForAuthoring'])

    def test_cli_and_example_work_from_empty_directory(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t)/'out.json'
            run = subprocess.run([sys.executable, str(ROOT/'examples/anchor-measures/example.py'),'--out',str(out)], cwd=t,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(json.loads(out.read_text())['status'], 'local-candidate')
            p = fixture(); source = Path(t)/'input.json'
            source.write_text(json.dumps({'properties':p,'owner_visual_id':'owner','requests':[request(p)]}))
            run = subprocess.run([sys.executable,str(ROOT/'plan.py'),'construct-native','anchor','--input',str(source),'--out',str(out)],cwd=t,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertFalse(json.loads(out.read_text())['changes'][0]['after']['display_at_all_levels'])

    def test_build_does_not_silently_ignore_anchor_requirements(self):
        from runtime.construct import planning
        for option in ({'anchor':{}}, {'anchor_config':{}}, {'anchorConfig':{}}):
            with self.assertRaisesRegex(ValueError, 'Use per-measure anchor'):
                planning({}, {'name':'Example','measures':[dict(key='x',**option)]}, None)


if __name__ == '__main__':unittest.main()
