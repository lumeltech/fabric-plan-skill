"""Run from any directory; uses only this package. No network or target IDs."""
import argparse
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from runtime.anchor_measures import apply_anchors


def example():
    profile = json.loads((Path(__file__).parent/'saved-profile.json').read_text(encoding='utf-8'))
    props = copy.deepcopy(profile['properties'])
    state = props['visualState']
    # The example deliberately adds a synthetic existing formula registration.
    # Its independent formula/inputs remain intact when only display is anchored.
    mid = '9007199254750001'
    state['manage_measures'].append({'id': mid, 'label': 'Example regional formula', 'order': 99, 'visible': True})
    rows = state['rowDimensions']; cols = state['columnDimensions']
    state['totals_config']['column_sub_total'] = None
    return apply_anchors(props, 'synthetic-current-owner', [{
        'measure_id': mid, 'row_fields': [rows[0]['externalKey']],
        'column_fields': [cols[0]['externalKey']], 'display_at_all_levels': False}])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    Path(args.out).write_text(json.dumps(example(), indent=2)+'\n', encoding='utf-8')
    print('Synthetic anchor candidate saved; no native write or runtime test.')
