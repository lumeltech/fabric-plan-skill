"""IBCS dashboard parts: the Plan theme, a Matrix table and story text.

The Plan theme is Plan-wide, so set it only when the request asks for it. A Matrix
(`INFORIVER`, type 10) takes the place of the embedded Planning grid on an IBCS
dashboard. It reads model or registered query values, not the grid's input
cells. Story text follows Fabric's own IBCS report title: a bold 18px message,
then 13px and 11px lines. Footnotes are 11px lines.
"""
import copy

IBCS_THEME_TYPE = 5
PLAN_THEMES = {'ibcs': IBCS_THEME_TYPE}
MATRIX_BUCKETS = {'AC': 'ameasure', 'PY': 'pymeasure', 'PL': 'plmeasure', 'FC': 'fcmeasure'}
TABLE_KEYS = {'label', 'rows', 'columns', 'measures'}
STORY_KEYS = {'message', 'subtitle', 'detail', 'footnotes'}
WHITE = '#FFFFFF'


def set_plan_theme(plan_properties, theme):
    """Return planProperties with the named Plan theme; other theme members are kept."""
    if theme not in PLAN_THEMES:
        raise ValueError('Supported Plan theme: ' + ', '.join(PLAN_THEMES))
    out = copy.deepcopy(plan_properties)
    props = out.setdefault('properties', {})
    current = props.get('theme')
    if current is not None and not isinstance(current, dict):
        raise ValueError('The exported Plan theme is not an object; inspect it before changing the theme')
    props['theme'] = {**(current or {}), 'type': PLAN_THEMES[theme]}
    return out


def matrix_table(model, spec, registry, *, query_fields=()):
    """Build an Intelligence Matrix from model dimensions and AC/PY/PL/FC values.

    spec: {"label", "rows": [dimension...], optional "columns": [dimension...],
    "measures": {"AC": field or {"field", "aggregation", "label"} or a list,
    "PY"/"PL"/"FC": one field each}}.
    """
    from .construct import field
    from .ibcs_charts import measure_entries
    from .intelligence import base
    from .linked_values import value_assignment
    unknown = set(spec) - TABLE_KEYS
    if unknown:
        raise ValueError('Unconsumed table options: ' + ', '.join(sorted(unknown)))
    if not isinstance(spec.get('label'), str) or not spec['label'].strip():
        raise ValueError('Matrix table needs a non-empty label')
    rows, columns = spec.get('rows'), spec.get('columns', [])
    if not isinstance(rows, list) or not rows or not isinstance(columns, list):
        raise ValueError('Matrix table needs a list of row dimensions and an optional list of column dimensions')
    if len(set(rows + columns)) != len(rows + columns):
        raise ValueError('Use each dimension once across the Matrix rows and columns')
    raw = spec.get('measures')
    if not isinstance(raw, dict) or 'AC' not in raw:
        raise ValueError('Matrix table needs measures with an AC value')
    stray = sorted(set(raw) - set(MATRIX_BUCKETS))
    if stray:
        raise ValueError('Matrix measure buckets are AC, PY, PL and FC, not ' + ', '.join(stray))
    assignments = [field(model, key, 'rows', i) for i, key in enumerate(rows)]
    assignments += [field(model, key, 'columns', i) for i, key in enumerate(columns)]
    seen = {}
    for bucket in MATRIX_BUCKETS:
        if bucket not in raw:
            continue
        items = measure_entries(bucket, raw[bucket])
        if bucket != 'AC' and len(items) > 1:
            raise ValueError('Matrix bucket ' + bucket + ' takes one measure')
        for order, item in enumerate(items):
            a = value_assignment(model, item['field'], registry, query_fields=query_fields, bucket='ameasure',
                                 order=order, label=item.get('label'), aggregation=item.get('aggregation'))
            a['bucketId'] = MATRIX_BUCKETS[bucket]
            a['customName'] = item.get('label', a.get('customName', a['columnName']))
            identity = (a['id'], a.get('aggregationType'))
            if identity in seen:
                raise ValueError('The same value is bound to ' + seen[identity] + ' and ' + bucket)
            seen[identity] = bucket
            assignments.append(a)
    p = base(10, spec['label'])
    p['pivotAssignments'] = assignments
    return p


def _text(value, key):
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError('IBCS ' + key + ' must be non-empty text')
    return value.strip()


def check_story(story):
    """Validate a dashboard's IBCS story block and return its normalized lines."""
    if not isinstance(story, dict):
        raise ValueError('The IBCS story must be an object')
    unknown = set(story) - STORY_KEYS
    if unknown:
        raise ValueError('Unconsumed IBCS story options: ' + ', '.join(sorted(unknown)))
    message = _text(story.get('message'), 'message')
    if message is None:
        raise ValueError('The IBCS story needs a message: the one statement the page should convey')
    notes = story.get('footnotes', [])
    if not isinstance(notes, list):
        raise ValueError('IBCS footnotes must be a list of lines')
    return {'message': message, 'subtitle': _text(story.get('subtitle'), 'subtitle'),
            'detail': _text(story.get('detail'), 'detail'),
            'footnotes': [_text(n, 'footnote') for n in notes]}


def message_title(story, *, name='Message title'):
    """BI_TEXT message title: bold 18px message, optional 13px and 11px lines."""
    from .intelligence import rich_text
    s = check_story(story)
    paragraphs = [[{'text': s['message'], 'size': 18, 'bold': True, 'color': None}]]
    for key, size in (('subtitle', 13), ('detail', 11)):
        if s[key]:
            paragraphs.append([{'text': s[key], 'size': size, 'color': None}])
    return rich_text(paragraphs, name=name, background=WHITE)


def footnote_text(story, *, name='Footnotes'):
    """BI_TEXT with one 11px paragraph per footnote, or None when there are none."""
    from .intelligence import rich_text
    notes = check_story(story)['footnotes']
    if not notes:
        return None
    return rich_text([[{'text': n, 'size': 11, 'color': None}] for n in notes], name=name, background=WHITE)
