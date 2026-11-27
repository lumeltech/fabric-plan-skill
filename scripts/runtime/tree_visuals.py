"""Decomposition and organization trees for Intelligence dashboards.

A tree is a TREE visual (type 25, spelled `TREE` in the definition) that the
Matrix engine renders. The definition carries what Fabric saves when a tree is
added from the Elements pane: the tree type in both chartType selectors and pivot
assignments in the tree's roles. The tree derives its layout and node settings
on load, so none are written here.

Availability is a tenant setting. Fabric loads a decomposition or organization
tree only when its tree switch is on, and an organization tree reads a parent
identifier only when parent-data mapping is on. A readback proves the tree was
saved, not that the destination shows it.
"""
TREE_TYPES = {'decomposition': 'DECOMPOSITION_TREE', 'organization': 'ORGANIZATION_TREE'}
NOT_OFFERED = {'row', 'measure', 'column'}
SPEC_KEYS = {'label', 'tree', 'levels', 'measure', 'parent', 'fields', 'sparkline'}
ORG_ONLY = ('parent', 'fields', 'sparkline')


def is_tree(spec):
    """True when a dashboard chart spec asks for a tree."""
    return 'tree' in spec


def _dimensions(spec, key):
    value = spec.get(key, [])
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
        raise ValueError('Tree ' + key + ' takes model dimension IDs')
    return value


def tree_visual(model, spec, registry, *, query_fields=()):
    """Build a decomposition or organization tree from model dimensions and values.

    spec: {"label", "tree": "decomposition" | "organization", "levels": [dimension...],
    "measure": field or {"field", "aggregation", "label"} or a list}. An organization
    tree also takes optional "parent" (one identifier dimension), "fields" (node
    detail dimensions) and "sparkline" (dimensions, with a measure).
    """
    from .construct import field
    from .ibcs_charts import measure_entries
    from .intelligence import base
    from .linked_values import value_assignment
    unknown = set(spec) - SPEC_KEYS
    if unknown:
        raise ValueError('Unconsumed tree options: ' + ', '.join(sorted(unknown)))
    kind = spec.get('tree')
    if kind in NOT_OFFERED:
        raise ValueError('Fabric\'s editor offers decomposition and organization trees only; '
                         + str(kind) + ' trees are not built here')
    if kind not in TREE_TYPES:
        raise ValueError('Tree type must be decomposition or organization')
    if not isinstance(spec.get('label'), str) or not spec['label'].strip():
        raise ValueError('Tree needs a non-empty label')
    if kind == 'decomposition' and any(k in spec for k in ORG_ONLY):
        raise ValueError('Parent, fields and sparkline belong to an organization tree')
    levels = _dimensions(spec, 'levels')
    if not levels:
        raise ValueError('Tree needs at least one level dimension')
    parent, fields, sparkline = (_dimensions(spec, k) for k in ORG_ONLY)
    if len(parent) > 1:
        raise ValueError('An organization tree takes one parent identifier')
    dims = levels + parent + fields + sparkline
    if len(set(dims)) != len(dims):
        raise ValueError('Use each dimension once across levels, parent, fields and sparkline')
    measures = measure_entries('measure', spec['measure']) if 'measure' in spec else []
    if kind == 'decomposition' and not measures:
        raise ValueError('A decomposition tree needs the measure it breaks down')
    if sparkline and not measures:
        raise ValueError('A sparkline needs a measure')

    assignments = [field(model, key, 'rows', i) for i, key in enumerate(levels)]
    for bucket, keys in (('parentid', parent), ('fieldid', fields), ('columns', sparkline)):
        for i, key in enumerate(keys):
            a = field(model, key, 'columns' if bucket == 'columns' else 'rows', i)
            a['bucketId'] = bucket
            assignments.append(a)
    seen = set()
    for order, item in enumerate(measures):
        a = value_assignment(model, item['field'], registry, query_fields=query_fields, bucket='ameasure',
                             order=order, label=item.get('label'), aggregation=item.get('aggregation'))
        a['customName'] = item.get('label', a.get('customName', a['columnName']))
        identity = (a['id'], a.get('aggregationType'))
        if identity in seen:
            raise ValueError('The same value is bound twice to the tree')
        seen.add(identity)
        assignments.append(a)

    p = base(25, spec['label'])
    p['chartType'] = p['visualState']['chartType'] = TREE_TYPES[kind]
    p['pivotAssignments'] = assignments
    return p


def tree_requirements(properties):
    """Tenant switches a built tree depends on, with what Fabric does when each is off."""
    chart_type = properties.get('chartType')
    dropped = 'The page does not load the tree.'
    needs = []
    if chart_type == 'DECOMPOSITION_TREE':
        needs.append({'switch': 'decomposition tree', 'whenOff': dropped})
    if chart_type == 'ORGANIZATION_TREE':
        needs.append({'switch': 'organization tree', 'whenOff': dropped})
        if any(a.get('bucketId') == 'parentid' for a in properties.get('pivotAssignments', [])):
            needs.append({'switch': 'organization tree parent-data mapping',
                          'whenOff': 'Fabric removes the parent identifier when the tree first renders and saves that change.'})
    return needs
