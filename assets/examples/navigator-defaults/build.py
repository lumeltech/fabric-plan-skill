"""Construct complete native Navigator properties using only the bundled package.

Output is a local authoring example. Resolve real page/bookmark targets and host
identities before deployment; this script does not contact or repair any report.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from runtime.navigator_api import state
from runtime.navigator_defaults import require_complete_defaults
from runtime.codec import save


def build(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    variants = {
        'dashboard-pages': state('PAGE_NAVIGATOR_TABS', selected_pages=['example-estimate-page', 'example-variance-page'], caption='Planning views'),
        'saved-views': state('BOOKMARK_TABS', caption='Saved views'),
        'home-button': state('NAVIGATOR_BUTTON', page_target='example-home-page', caption='Home'),
    }
    for name, navigator in variants.items():
        require_complete_defaults(navigator)
        properties = {'visualType': 203, 'visualState': {'navigatorState': navigator},
                      'position': {'x': 24, 'y': 24}, 'dimension': {'width': 600, 'height': 60}}
        save(output / (name + '.properties.json'), {'properties': properties})
    print(json.dumps({'constructed': list(variants), 'completeDefaults': True, 'rendering': 'not-tested', 'liveWrites': 0}))


if __name__ == '__main__':
    build(sys.argv[1])
