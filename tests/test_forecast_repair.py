"""Regression: the scoped ALM Forecast repair route over a full offline build."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy, inspect, json, os, subprocess, tempfile, unittest
from pathlib import Path
from runtime.codec import load, loads, parts, scoped_candidate
from runtime.construct import build
from runtime.forecast_repair import repair_definition

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ['Calendar[Year]', 'Calendar[Quarter]', 'Calendar[YearMonth]']
CALENDAR = [('Year', 'Int64'), ('Quarter', 'Int64'), ('MonthName', 'String'),
            ('YearMonth', 'String'), ('MonthStart', 'DateTime'), ('Week', 'Int64')]
COPIED = ('forecast_version', 'closed_period_till', 'auto_close_forecast_settings',
          'disable_write_access', 'forecast_allowed_user_permissions')


def forecast_sheet(name, actual, forecast, reference=None, start='2031-01-01', end='2031-12-31'):
    measure = {'key': forecast, 'label': forecast, 'kind': 'Forecast', 'actuals': actual,
               'start': start, 'end': end, 'timezone': 'UTC'}
    if reference:
        measure['referenceForecast'] = reference
    return {'name': name, 'rows': ['Region[Region]'], 'columns': COLUMNS, 'measures': [
        {'key': actual, 'label': actual, 'kind': 'Native', 'source': 'Metrics[Units]'}, measure]}


def envelope(reference=None, target=None, ref_start='2031-01-01', ref_end='2031-12-31'):
    model = load(ROOT / 'assets/fixtures/model.json')
    for name, typ in CALENDAR:
        model['fields'].append(dict(id='Calendar[' + name + ']', tableName='Calendar',
                                    columnName=name, columnType='Column', dataType=typ))
    reference = reference if reference is not None else {
        'forecast_version': 2, 'closed_period_till': '2031-06-30T00:00:00.000Z',
        'auto_close_forecast_settings': {'auto_close_by': 3, 'extend_range': 'Extended'},
        'disable_write_access': True, 'forecast_allowed_user_permissions': False,
        'edit_config': {'number_column_metadata': {'distribute_parent_value_to_children': False}}}
    spec = {'name': 'Scoped Forecast repair', 'sheets': [
        forecast_sheet('Monthly Forecast', 'Actual units', 'Forecast units', target),
        forecast_sheet('Correct Version', 'Actual units', 'Reference forecast', reference, ref_start, ref_end)]}
    return build(model, spec)['envelope']


REQUEST = {'target_sheet': 'Monthly Forecast', 'reference_sheet': 'Correct Version',
           'target_forecast': 'Forecast units', 'reference_forecast': 'Reference forecast'}


def replace(base, **changes):
    """The same envelope with only these complete parts swapped in."""
    return scoped_candidate(base, changes)[0]


def column(raw, prefix, name):
    data = loads(raw[prefix + 'dataInput.json'].decode('utf-8-sig'))
    return data, next(c for c in data['columns'] if c['name'] == name)


def prefixes(base, definition):
    """(target, reference) part prefixes for the two Planning grids."""
    out = {}
    for sheet in definition['sheets']:
        for visual in sheet['workloadItemEntityVisuals']:
            if visual.get('isEmbedded') or visual['visualType'] != 'PLANNING':
                continue
            out[sheet['displayName']] = 'sheets/' + sheet['recordGuid'] + '/visuals/' + visual['visualId'] + '/'
    return out


class ForecastRepairTests(unittest.TestCase):
    def setUp(self):
        self.base = envelope()
        self.raw = parts(self.base)
        self.definition = loads(self.raw['definition.json'].decode('utf-8-sig'))
        self.sheets = prefixes(self.raw, self.definition)
        self.target_parts = {self.sheets['Monthly Forecast'] + 'dataInput.json',
                             self.sheets['Monthly Forecast'] + 'properties.json'}
        self.reference_column = column(self.raw, self.sheets['Correct Version'], 'Reference forecast')[1]
        self.target_column = column(self.raw, self.sheets['Monthly Forecast'], 'Forecast units')[1]

    def repair(self, base=None, **request):
        return repair_definition(base or self.base, **{**REQUEST, **request})

    def test_only_the_target_forecast_definition_changes(self):
        candidate, summary = self.repair()
        after = parts(candidate)
        changed = {p for p in after if self.raw.get(p) != after[p]}
        self.assertEqual(changed, set(summary['changedParts']))
        self.assertEqual(changed, {self.sheets['Monthly Forecast'] + 'dataInput.json'})
        # Identical parts are dropped from the patch, and a freshly built grid already
        # carries Sum/Sum row aggregation plus a visible member, so properties.json
        # rejoins the change set only when the reference state actually differs.
        self.assertEqual(self.raw['definition.json'], after['definition.json'])
        self.assertEqual(summary['postSaveValidation'], 'not-run')
        self.assertEqual(summary['referenceSheet'], 'Correct Version')

    def test_reference_behaviour_lands_and_target_identity_survives(self):
        candidate, summary = self.repair()
        after = parts(candidate)
        _, target = column(after, self.sheets['Monthly Forecast'], 'Forecast units')
        old = target['columnMeta']['measure_type']['Forecast']
        ref = self.reference_column['columnMeta']['measure_type']['Forecast']
        for key in COPIED:
            self.assertEqual(old[key], ref[key], key)
        self.assertEqual(old['forecast_period'], ref['forecast_period'])
        self.assertEqual(old['edit_config']['number_column_metadata']['distribute_parent_value_to_children'], False)
        # The consumer keeps its own identity: measureGuid, and the actuals binding, which
        # is not one of the copied keys, so the reference never re-points the target.
        self.assertEqual(summary['measureGuid'], target['measureGuid'])
        before = self.target_column['columnMeta']['measure_type']['Forecast']
        self.assertEqual(old['closed_period_config'], before['closed_period_config'])
        self.assertNotEqual(old['forecast_version'], before['forecast_version'])
        self.assertNotEqual(ref['forecast_version'], before['forecast_version'])
        self.assertEqual(column(after, self.sheets['Correct Version'], 'Reference forecast')[1], self.reference_column)

    def test_grid_state_gains_reference_aggregation_and_visible_member(self):
        prefix = self.sheets['Correct Version']
        props = loads(self.raw[prefix + 'properties.json'].decode('utf-8-sig'))
        state = props['properties']['visualState']
        rid = next(m['id'] for m in state['manage_measures'] if m['label'] == 'Reference forecast')
        state['aggregation_config'] = {'measure_aggregation': {rid: {'row': 'Max', 'column': 'Sum'}}}
        candidate, summary = self.repair(replace(self.base, **{prefix + 'properties.json': props}))
        after = parts(candidate)
        self.assertIn(self.sheets['Monthly Forecast'] + 'properties.json', summary['changedParts'])
        state = loads(after[self.sheets['Monthly Forecast'] + 'properties.json'].decode('utf-8-sig'))['properties']['visualState']
        mid = summary['measureGuid']
        self.assertEqual(state['aggregation_config']['measure_aggregation'][mid], {'row': 'Max', 'column': 'Sum'})
        member = next(m for m in state['manage_measures'] if m['id'] == mid)
        self.assertTrue(member['visible'])
        self.assertEqual(member['label'], 'Forecast units')
        for dimension in state['columnDimensions']:
            self.assertIn(dimension['timeIntervalUnit'], ('Year', 'Quarter', 'Month'))
            self.assertNotIn('isNative', dimension)

    def test_missing_aggregation_and_member_fall_back_to_defaults(self):
        prefix = self.sheets['Monthly Forecast']
        props = loads(self.raw[prefix + 'properties.json'].decode('utf-8-sig'))
        state = props['properties']['visualState']
        state['manage_measures'] = [m for m in state['manage_measures'] if m['label'] != 'Forecast units']
        state.pop('aggregation_config', None)
        candidate, summary = self.repair(replace(self.base, **{prefix + 'properties.json': props}))
        after = parts(candidate)
        after_state = loads(after[prefix + 'properties.json'].decode('utf-8-sig'))['properties']['visualState']
        mid = summary['measureGuid']
        self.assertEqual(after_state['aggregation_config']['measure_aggregation'][mid], {'row': 'Sum', 'column': 'Sum'})
        member = next(m for m in after_state['manage_measures'] if m['id'] == mid)
        self.assertEqual((member['label'], member['visible']), ('Forecast units', True))
        self.assertLessEqual(member['order'], len(after_state['manage_measures']))

    def test_embedded_visual_rows_are_not_candidates(self):
        # A real export lists the dashboard embed under the same sheet, and it has no dataInput part.
        definition = copy.deepcopy(self.definition)
        sheet = definition['sheets'][0]
        sheet['workloadItemEntityVisuals'].append({'visualId': 'embed-1', 'visualType': 'PLANNING', 'isEmbedded': True})
        base = replace(self.base, **{'definition.json': definition})
        _, summary = self.repair(base)
        self.assertEqual(set(summary['changedParts']), {self.sheets['Monthly Forecast'] + 'dataInput.json'})
        sheet['workloadItemEntityVisuals'] = [{'visualId': 'embed-1', 'visualType': 'PLANNING', 'isEmbedded': True}]
        with self.assertRaisesRegex(ValueError, 'Missing/ambiguous native Forecast'):
            self.repair(replace(self.base, **{'definition.json': definition}))

    def test_documented_refusals(self):
        for label, call, message in [
            ('no such sheet', lambda: self.repair(target_sheet='No such sheet'), 'Missing/ambiguous sheet'),
            ('empty sheet name', lambda: self.repair(target_sheet=''), 'Missing/ambiguous sheet'),
            ('non-forecast column', lambda: self.repair(target_forecast='Actual units'), 'Missing/ambiguous native Forecast'),
            ('no such forecast', lambda: self.repair(reference_forecast='Forecast'), 'Missing/ambiguous native Forecast'),
            ('horizon mismatch', lambda: self.repair(base=envelope(ref_start='2030-01-01')), 'Reference horizon differs'),
        ]:
            with self.subTest(case=label), self.assertRaisesRegex(ValueError, message):
                call()

    def test_reference_edit_dependency_is_refused(self):
        prefix = self.sheets['Correct Version']
        data = copy.deepcopy(loads(self.raw[prefix + 'dataInput.json'].decode('utf-8-sig')))
        forecast = next(c for c in data['columns'] if c['name'] == 'Reference forecast')['columnMeta']['measure_type']['Forecast']
        for mutate, case in [
            (lambda e: e['edit_config'].__setitem__('on_change_formula', 'COLUMN.SUM(1)'), 'reference formula'),
            (lambda e: e['edit_config']['number_column_metadata'].__setitem__('min_value', {'Measure': '99'}), 'reference measure default'),
        ]:
            with self.subTest(case=case):
                mutate(forecast)
                with self.assertRaisesRegex(ValueError, 'require explicit remapping'):
                    self.repair(replace(self.base, **{prefix + 'dataInput.json': data}))

    def test_command_writes_candidate_and_change_manifest(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as td:
            tmp = Path(td)
            (tmp / 'request.json').write_text(json.dumps(REQUEST), encoding='utf-8')
            (tmp / 'baseline.json').write_text(json.dumps(self.base), encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/plan.py'), 'forecast-repair',
                 '--baseline', str(tmp / 'baseline.json'), '--input', str(tmp / 'request.json'),
                 '--out', str(tmp / 'candidate')],
                capture_output=True, text=True, cwd=ROOT, env={**os.environ, 'FABRIC_SKILL_OFFLINE_TEST': '1'})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('publish with plan.py api update', result.stdout)
            manifest = load(tmp / 'candidate.changes.json')
            self.assertEqual(manifest['changedParts'], [self.sheets['Monthly Forecast'] + 'dataInput.json'])
            self.assertEqual(manifest['postSaveValidation'], 'not-run')
            candidate = load(tmp / 'candidate')
            self.assertEqual(set(parts(candidate)), set(self.raw))
            local, _ = self.repair()
            self.assertEqual(parts(candidate), parts(local))

    def test_shipped_example_request_matches_the_signature(self):
        example = load(ROOT / 'assets/examples/forecast-repair.request.json')
        self.assertEqual(set(example), set(inspect.signature(repair_definition).parameters) - {'envelope'})


if __name__ == '__main__':
    unittest.main()
