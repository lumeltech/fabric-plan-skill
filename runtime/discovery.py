"""Local lookup of direct reference files and supported operations."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
STOP = set('a an and as at be by for from i in into is it me my of on or please the this to use want with'.split())


def catalog():
    data = json.loads((ROOT / 'references/module-routing.json').read_text(encoding='utf-8'))
    for module in data['modules']:
        for guide in module['guides']:
            guide['command'] = 'python plan.py reference ' + guide['file']
    return data


def tokens(text):
    return set(re.findall(r'[a-z0-9]+', text.casefold())) - STOP


def discover(query='', module=None):
    data = catalog()
    matches = data['modules']
    if module:
        matches = [m for m in matches if m['id'].casefold() == module.casefold()]
        if not matches:
            raise ValueError('Unknown module '+module+'; use discover --list')
    elif query.strip():
        wanted = tokens(query)
        scored = []
        for m in matches:
            labels = [m['name'], *m['aliases']]
            corpus = ' '.join([*labels, *m['businessRequests']])
            score = len(wanted & tokens(corpus))
            score += 3 * sum(1 for phrase in labels if re.search(
                r'(?<!\w)' + re.escape(phrase.casefold()) + r'(?!\w)', query.casefold()))
            if query.strip().casefold() == m['id'].casefold():
                score += 100
            if score:
                scored.append((score, m))
        matches = [m for score, m in sorted(scored, key=lambda v: (-v[0], v[1]['id']))]
    expanded = []
    for m in matches:
        item = dict(m)
        item['operations'] = [dict(id=key, **data['actions'][key]) for key in m['operations']]
        expanded.append(item)
    return dict(release=data['release'], query=query, coverageMeaning=data['coverageMeaning'],
                count=len(expanded), modules=expanded,
                note='Local discovery only; no operation has been run.')


def render(result, compact=False):
    if not result['modules']:
        return 'No literal match. Use python plan.py discover --list, then select the relevant business guide.'
    lines = [result['note']]
    for m in result['modules']:
        lines.append(f"\n{m['id']} | {m['name']} | {m['coverage']}")
        lines.append('  Business: '+' '.join(m['businessRequests']))
        lines.append('  Direct guides:')
        lines.extend('    '+g['command'] for g in m['guides'])
        if compact:
            continue
        lines.append('  Prerequisites: '+m['prerequisites'])
        for op in m['operations']:
            lines.append(f"  Operation {op['id']} [{op['phase']}]: {op['description']}")
            if op['command']:
                lines.append('    '+op['command'])
            lines.append('    Inputs: '+op['inputs'])
            lines.append('    Callables: '+', '.join(op['symbols']))
        if not m['operations']:
            lines.append('  Guidance only; no executable operation.')
        lines.append('  Limits: '+m['limitations'])
    return '\n'.join(lines)
