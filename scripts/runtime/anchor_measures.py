"""Anchor construction using native dimension identities and ordered-pivot hashes.

Configuration persistence does not prove leaf propagation or edit enforcement.
The supplied XXH3 contract supports the first anchor without a saved donor.
"""
import copy
import hashlib
import json

from .identity import native_id
from .dimension_hash import generate_dimension_hash


class AnchorContractGap(ValueError):
    """The selected branch needs current native evidence before construction."""


def _dimensions(properties):
    state = properties['visualState']
    axes = {}
    seen = set()
    for axis, key in (('rows', 'rowDimensions'), ('columns', 'columnDimensions')):
        values = state.get(key)
        if not isinstance(values, list):
            raise ValueError('Current native rowDimensions and columnDimensions required')
        fields = set()
        for d in values:
            native_id(d['id'])
            field = d.get('externalKey')
            if not isinstance(field, str) or not field:
                raise ValueError('Resolve an exact externalKey for each native dimension')
            if d['id'] in seen or field in fields:
                raise ValueError('Ambiguous or duplicate dimension identity')
            seen.add(d['id']); fields.add(field)
        axes[axis] = copy.deepcopy(values)
    # Resolve the established saved Pivot contract before hashing or binding.
    # None inherits the base axis; an explicit [] is an empty axis.
    pivot = state.get('pivot') or {}
    active = pivot.get('active_id')
    explorer = state.get('pivotExplorer') or {}
    if explorer.get('activePivot') not in (None, active):
        raise AnchorContractGap('ANCHOR_PIVOT_AMBIGUOUS: resolve current active pivot')
    if active is not None:
        configs = pivot.get('configs', [])
        matches = [c for c in configs if c.get('id') == active]
        if len(matches) != 1 or matches[0].get('hidden'):
            raise AnchorContractGap('ANCHOR_PIVOT_AMBIGUOUS: active pivot is absent or hidden')
        available = {d['id']: d for values in axes.values() for d in values}
        resolved = {}
        for axis, key in (('rows', 'row_dimensions'), ('columns', 'col_dimensions')):
            ids = matches[0].get(key)
            if ids is None:
                resolved[axis] = axes[axis]
                continue
            if not isinstance(ids, list):
                raise ValueError('Current Pivot axes must be explicit ID lists or null')
            for value in ids: native_id(value)
            if len(ids) != len(set(ids)) or not set(ids) <= set(available):
                raise AnchorContractGap('ANCHOR_PIVOT_AMBIGUOUS: unknown or duplicate pivot dimensions')
            resolved[axis] = [copy.deepcopy(available[value]) for value in ids]
        ids = [d['id'] for values in resolved.values() for d in values]
        if len(ids) != len(set(ids)):
            raise AnchorContractGap('ANCHOR_PIVOT_AMBIGUOUS: dimension occurs on both pivot axes')
        axes = resolved
    return axes


def _members(properties):
    members = properties['visualState'].get('manage_measures')
    if not isinstance(members, list):
        raise ValueError('Current complete managed measure registry required')
    ids = [native_id(m['id']) for m in members]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate managed measure identity')
    return members


def _signature(properties):
    # This digest is a LOCAL stale-evidence guard, never the native dimension_hash.
    # Include ordered native dimensions, source assignments and saved pivot state.
    state = properties['visualState']
    value = {'axes': _dimensions(properties),
             'assignments': [a for a in properties.get('pivotAssignments', [])
                             if a.get('bucketId') in ('rows', 'columns')],
             'view': {k: state[k] for k in ('pivot', 'pivotExplorer') if k in state}}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def capture_context(properties, owner_visual_id):
    """Compute a hash from the current ordered pivot and guard its saved context.

    ALM callers use the exact visual GUID; native callers use its exact returned
    numeric owner ID. Evidence cannot move between those identity namespaces.
    """
    if not isinstance(owner_visual_id, str) or not owner_visual_id:
        raise ValueError('Actual owning visual identity required')
    axes = _dimensions(properties)
    allowed = {axis: {d['id'] for d in values} for axis, values in axes.items()}
    computed = generate_dimension_hash([d['id'] for d in axes['rows']],
                                       [d['id'] for d in axes['columns']])
    hashes = set()
    witnesses = []
    for m in _members(properties):
        cfg = m.get('anchor_config')
        if not isinstance(cfg, dict) or not cfg.get('dimension_hash'):
            continue
        rows, cols = cfg.get('row_dimensions'), cfg.get('col_dimensions')
        if not isinstance(rows, list) or not isinstance(cols, list):
            raise ValueError('Malformed current saved anchor dimensions')
        if not rows and not cols:
            continue  # Empty defaults are not evidence of an enabled anchor.
        if (not set(rows) <= allowed['rows'] or not set(cols) <= allowed['columns']
                or len(rows) != len(set(rows)) or len(cols) != len(set(cols))):
            raise AnchorContractGap('ANCHOR_STALE_DIMENSIONS: current saved anchor does not match the owner axes')
        value = cfg['dimension_hash']
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Invalid saved dimension_hash')
        hashes.add(value)
        witnesses.append({'measure_id': m['id'], 'anchor_config': copy.deepcopy(cfg)})
    if len(hashes) > 1:
        raise AnchorContractGap('ANCHOR_HASH_CONFLICT: reconcile current owner anchors before changing them')
    if hashes and hashes != {computed}:
        raise AnchorContractGap('ANCHOR_HASH_MISMATCH: saved anchor hash does not match current ordered pivot; do not copy or silently rebind it')
    return {'owner_visual_id': owner_visual_id, 'layout_signature': _signature(properties),
            'dimension_hash': computed, 'witnesses': witnesses,
            'origin': 'computed-current-pivot-xxh3'}



def _resolve(fields, dimensions, axis):
    if not isinstance(fields, list) or any(not isinstance(f, str) for f in fields):
        raise ValueError(axis + ' fields must be an explicit list of exact externalKeys; [] means All/Total')
    if len(fields) != len(set(fields)):
        raise ValueError('Duplicate anchor field')
    by_key = {d['externalKey']: d for d in dimensions}
    missing = set(fields) - set(by_key)
    if missing:
        raise ValueError('Anchor field absent from ' + axis + ' axis: ' + ', '.join(sorted(missing)))
    # Canonical order follows current axes. Do not add omitted row parents:
    # Product-only is deliberately different from Region x Product.
    result = [d for d in dimensions if d['externalKey'] in fields]
    if axis == 'columns':
        parents = []
        for d in dimensions:
            if d.get('isTimeDimension') or d.get('timeIntervalUnit'):
                if d['externalKey'] in fields and not set(parents) <= set(fields):
                    raise ValueError('Include the current calendar parents for the selected time level')
                parents.append(d['externalKey'])
    return [d['id'] for d in result]


def apply_anchors(properties, owner_visual_id, requests, *, context=None, expose_entry_totals=True):
    """Return a copied candidate changing only anchor subtrees and required totals.

    Requests contain measure_id, row_fields, column_fields, optional
    display_at_all_levels. Fields are exact current semantic externalKeys, not
    labels, storage ID mappings or hashes. Formula/input records stay untouched.
    """
    if not isinstance(expose_entry_totals, bool):
        raise ValueError('expose_entry_totals must be Boolean')
    current = capture_context(properties, owner_visual_id)
    if context is not None and context != current:
        raise AnchorContractGap('ANCHOR_CONTEXT_CHANGED: owner, dimensions or saved anchor evidence changed; recapture')
    if not isinstance(requests, list) or not requests:
        raise ValueError('Explicit nonempty anchor requests required')
    axes = _dimensions(properties)
    result = copy.deepcopy(properties)
    state = result['visualState']
    members = {m['id']: m for m in _members(result)}
    seen, changes, required_totals = set(), [], set()
    for request in requests:
        required = {'measure_id', 'row_fields', 'column_fields'}
        if not required <= request.keys() or set(request) - required - {'display_at_all_levels'}:
            raise ValueError('Use measure_id, row_fields, column_fields and optional display_at_all_levels')
        mid = native_id(request['measure_id'])
        if mid not in members or mid in seen:
            raise ValueError('Resolve one current managed measure per request; do not create or duplicate it')
        seen.add(mid)
        rows = _resolve(request['row_fields'], axes['rows'], 'rows')
        cols = _resolve(request['column_fields'], axes['columns'], 'columns')
        if not rows and not cols:
            raise ValueError('An enabled anchor needs at least one row or column dimension')
        display = request.get('display_at_all_levels', False)
        if not isinstance(display, bool):
            raise ValueError('display_at_all_levels must be Boolean, not an input-permission setting')
        before = copy.deepcopy(members[mid].get('anchor_config'))
        cfg = copy.deepcopy(before) if isinstance(before, dict) else {}
        cfg.update(row_dimensions=rows, col_dimensions=cols, display_at_all_levels=display,
                   dimension_hash=current['dimension_hash'])
        members[mid]['anchor_config'] = cfg
        changes.append({'measure_id': mid, 'before': before, 'after': copy.deepcopy(cfg)})
        for axis, ids in (('rows', rows), ('columns', cols)):
            prefix = 'row' if axis == 'rows' else 'column'
            if not ids:
                required_totals.add(prefix + '_grand_total')
            elif ids[-1] != axes[axis][-1]['id']:
                required_totals.add(prefix + '_sub_total')
    # Anchors needing Year/Quarter entry are a scoped exception to the general
    # column-subtotal-off default. Keep ordinary sheets and unrelated totals.
    totals = state.setdefault('totals_config', {})
    total_changes = {}
    for key in sorted(required_totals):
        if totals.get(key) not in ('Top', 'Bottom', 'Left', 'Right'):
            if not expose_entry_totals:
                raise ValueError('Required anchor entry total is hidden: ' + key)
            target = 'Top' if key.startswith('row_') else 'Left'
            total_changes[key] = {'before': totals.get(key), 'after': target}
            totals[key] = target
    return {'properties': result, 'changes': changes, 'totals_changes': total_changes,
            'status': 'local-candidate', 'hash_origin': current['origin'],
            'runtime_validation': 'not run'}
