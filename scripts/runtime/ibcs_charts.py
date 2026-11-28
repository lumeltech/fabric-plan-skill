"""IBCS chart recipes as native Analytics+ chart templates with checked buckets.

A recipe selects a native chart template (`chartType`) and binds a category, an
optional stack dimension and measures into the template's buckets. Bucket limits
follow the product's chart templates; each recipe adds the minimum bindings from
the IBCS recipe catalog. A definition carries what the product saves when a
chart is added: both chartType selectors and the pivot assignments. The chart
derives its template state on first render.

Every chart built here also saves the chart's own IBCS theme with that theme's
measure and variance colors, so it keeps IBCS scenario notation under any Plan
theme; "theme": "plan" opts a chart out. A "style" on the chart spec is written
separately as the chart's AI chart schema (runtime.chart_styling): plot background,
global font and data-label formatting. The rest of the IBCS look (ranking, deviation
callouts, number format) is not written here; see references/ibcs-charts.md.
"""
import copy
from functools import lru_cache
from pathlib import Path
from .paths import ASSETS

APPEARANCE = 'hiddenProperties_!!!_appearance'
# 'ibcs' saves the chart's own IBCS theme; 'plan' leaves the chart on the Plan theme.
CHART_THEMES = ('ibcs', 'plan')
MEASURE_BUCKETS = ('AC', 'PY', 'PL', 'FC')
_REFERENCES = {'AC': (1, 1), 'PY': (0, 1), 'PL': (0, 1), 'FC': (0, 1)}


def _template(*, measures=None, stack=False, needs_stack=False, axis_max=None,
              min_buckets=1, fallback=None):
    return {'measures': dict(measures or _REFERENCES), 'stack': stack,
            'needsStack': needs_stack, 'axisMax': axis_max,
            'minBuckets': min_buckets, 'fallback': fallback}


# Measure limits are (min, max) per bucket. A stacked template with one measure
# and no stack renders as its plain fallback, so the builder refuses that shape.
TEMPLATES = {
    'COLUMN_VERTICAL': _template(),
    'COLUMN_HORIZONTAL': _template(),
    'STACKED_COLUMN_VERTICAL': _template(stack=True, fallback='COLUMN_VERTICAL'),
    'STACKED_COLUMN_HORIZONTAL': _template(stack=True, fallback='COLUMN_HORIZONTAL'),
    'PERCENTAGE_STACKED_VERTICAL': _template(stack=True, fallback='COLUMN_VERTICAL'),
    'PERCENTAGE_STACKED_HORIZONTAL': _template(stack=True, fallback='COLUMN_HORIZONTAL'),
    'COLUMN_WATERFALL_VERTICAL': _template(min_buckets=2),
    'COLUMN_WATERFALL_HORIZONTAL': _template(min_buckets=2),
    'LINE': _template(measures={**_REFERENCES, 'AC': (1, 27)}),
    'AREA': _template(measures={**_REFERENCES, 'AC': (1, 27)}),
    'STACKED_AREA': _template(measures={'AC': (1, 1), 'FC': (0, 1)}, stack=True, needs_stack=True),
    'SCATTER_PLOT': _template(measures={'AC': (1, 1), 'PY': (1, 1)}, stack=True),
    'BUBBLE_PLOT': _template(measures={'AC': (1, 1), 'PY': (1, 1), 'PL': (1, 1)}, stack=True),
    'SIDE_BY_SIDE_WATERFALL': _template(measures={**_REFERENCES, 'PY': (1, 1)}, axis_max=1, min_buckets=2),
}

# Recipe code -> (name, allowed chart types with the default first, required buckets).
RECIPES = {
    'C01': ('Stacked Column', ('STACKED_COLUMN_VERTICAL',), ('axis', 'AC', 'PL', 'FC', 'stack')),
    'C02': ('Stacked Bar', ('STACKED_COLUMN_HORIZONTAL',), ('axis', 'AC', 'stack')),
    'C03': ('Overlapped Column', ('COLUMN_VERTICAL',), ('axis', 'AC', 'PY', 'FC')),
    'C04': ('Overlapped Bar', ('COLUMN_HORIZONTAL',), ('axis', 'AC', 'PL')),
    'C05': ('Waterfall + Column', ('COLUMN_WATERFALL_VERTICAL',), ('axis', 'AC', 'PY')),
    'C06': ('Waterfall + Bar', ('COLUMN_WATERFALL_HORIZONTAL',), ('axis', 'AC', 'PY')),
    'C07': ('Line', ('LINE',), ('axis', 'AC')),
    'C08': ('Stacked Area', ('STACKED_AREA', 'AREA'), ('axis', 'AC')),
    'C09': ('Scatter', ('SCATTER_PLOT',), ('axis', 'AC', 'PY')),
    'C10': ('Bubble', ('BUBBLE_PLOT',), ('axis', 'AC', 'PY', 'PL')),
    'C11': ('Related Driver Panels', ('LINE',), ('axis', 'AC')),
    'C12': ('Side-by-Side Waterfall', ('SIDE_BY_SIDE_WATERFALL',), ('axis', 'AC', 'PY')),
    'C13': ('Overlapped Column, date/forecast', ('COLUMN_VERTICAL',), ('axis', 'AC')),
}

# A panel recipe is one chart per measure: related drivers have their own scales, so each gets its own panel.
PANEL_RECIPES = {'C11'}
SPEC_KEYS = {'label', 'recipe', 'chartType', 'category', 'stack', 'measures', 'theme', 'style'}
MEASURE_KEYS = {'field', 'aggregation', 'label'}


@lru_cache(maxsize=1)
def _ibcs_theme():
    from .codec import load
    return load(ASSETS / 'fixtures/ibcs-chart-theme.json')


def ibcs_palette():
    """Colors and fill patterns of the chart's IBCS theme, for a design brief or readback report."""
    return copy.deepcopy(_ibcs_theme()['palette'])


def _swap(value, table):
    if isinstance(value, dict):
        return {k: _swap(v, table) for k, v in value.items()}
    return table.get(value, value) if isinstance(value, str) else value


def role_style(role):
    """Measure style the IBCS theme gives a role: AC, PY, PL, FC or an additional actual (AC1 to AC29)."""
    theme = _ibcs_theme()
    if role in theme['measuresStyle']:
        return copy.deepcopy(theme['measuresStyle'][role])
    extra = theme['additionalActuals']
    if role not in extra['colors']:
        raise ValueError('The IBCS chart theme has no measure style for role ' + repr(role))
    colors = extra['colors'][role]
    # Additional actuals share one style and differ only in their color and highlight color.
    return _swap(extra['style'], {'{color}': colors['color'], '{highlightColor}': colors['highlightColor']})


def measure_roles(properties):
    """Roles the chart gives its bound values: AC, AC1, AC2... for further actuals, then PY, PL, FC."""
    counts = {}
    for a in properties.get('pivotAssignments', []):
        if a.get('bucketId') in MEASURE_BUCKETS:
            counts[a['bucketId']] = counts.get(a['bucketId'], 0) + 1
    roles = []
    for bucket in MEASURE_BUCKETS:
        if bucket in counts:
            roles.append(bucket)
            if bucket == 'AC':
                roles += ['AC' + str(i) for i in range(1, counts[bucket])]
    return roles


def _appearance(properties):
    from .codec import loads
    value = properties.get('visualState', {}).get(APPEARANCE)
    if value is None:
        return {}
    value = loads(value) if isinstance(value, str) else copy.deepcopy(value)
    if not isinstance(value, dict):
        raise ValueError('The saved chart appearance is not an object; inspect it before changing the chart theme')
    return value


def chart_theme(properties):
    """Name the theme a chart keeps as its own, or 'plan' when the chart follows the Plan theme."""
    charts = _appearance(properties).get('charts')
    meta = charts.get('isDefaultMeta') if isinstance(charts, dict) else None
    own = isinstance(meta, dict) and meta.get('theme') is False
    return charts['theme'] if own and charts.get('theme') else 'plan'


def apply_chart_theme(properties, theme='ibcs'):
    """Return chart properties that keep the IBCS theme as the chart's own theme.

    Saves what the chart saves when IBCS Theme is picked in its theme menu, limited
    to the theme selection and its colors: the measure style of every bound role
    (AC solid dark, PY solid light, PL outlined, FC hatched) and the variance colors.
    Series colors come from the theme itself, so explicit group and category colors
    are cleared, as the chart does on a theme change. Every other saved setting is
    kept. Use it on a new chart or on a freshly exported one.
    """
    from .codec import dumps
    from .construct import merge
    from .intelligence import classify_visual
    if theme != 'ibcs':
        raise ValueError('Supported chart theme: ibcs')
    observed = classify_visual(properties)
    if properties.get('visualType') != 50 or observed:
        raise ValueError('The IBCS chart theme applies to an ANALYTICS_PLUS chart (visualType 50), not a '
                         + (observed['visual_type'] if observed else 'visual of type ' + str(properties.get('visualType'))))
    roles = measure_roles(properties)
    if not roles:
        raise ValueError('Bind the chart measures before applying the IBCS chart theme')
    state = merge(_appearance(properties), _ibcs_theme()['appearance'])
    charts = state['charts']
    styles = charts.get('measuresStyle')
    styles = styles if isinstance(styles, dict) else {}
    for role in roles:
        styles[role] = role_style(role)
    charts['measuresStyle'] = styles
    for key in ('groupStyle', 'categoryStyle'):
        if key in charts:
            charts[key] = {}
    out = copy.deepcopy(properties)
    out.setdefault('visualState', {})[APPEARANCE] = dumps(state).strip()
    return out


def is_recipe_chart(spec):
    """True when a dashboard chart spec selects a recipe or a native chart template."""
    return 'recipe' in spec or 'chartType' in spec


def required_buckets(code, chart_type=None):
    """Buckets a recipe chart must bind: the recipe minimum plus the template's own."""
    _, types, required = RECIPES[code]
    template = TEMPLATES[chart_type or types[0]]
    out = list(required)
    out += [b for b, (low, _) in template['measures'].items() if low and b not in out]
    if template['needsStack'] and 'stack' not in out:
        out.append('stack')
    return out


def recipes():
    """Return the recipe catalog: code -> name and required buckets per chart type."""
    return {code: {'name': name, 'chartTypes': list(types),
                   'requiredBuckets': {t: required_buckets(code, t) for t in types}}
            for code, (name, types, _) in RECIPES.items()}


def resolve_chart_type(spec):
    """Return (recipe code or None, chartType) for a recipe chart spec."""
    code = spec.get('recipe')
    chart_type = spec.get('chartType')
    if code is not None:
        if code not in RECIPES:
            raise ValueError('Unknown IBCS recipe ' + repr(code) + '; the catalog has ' + ', '.join(RECIPES))
        allowed = RECIPES[code][1]
        if chart_type is None:
            chart_type = allowed[0]
        elif chart_type not in allowed:
            raise ValueError(code + ' uses chartType ' + ' or '.join(allowed) + ', not ' + str(chart_type))
    if chart_type not in TEMPLATES:
        raise ValueError('Unsupported chart template ' + repr(chart_type) + '; supported: ' + ', '.join(TEMPLATES))
    return code, chart_type


def measure_entries(bucket, value):
    items = value if isinstance(value, list) else [value]
    if not items:
        raise ValueError('Bind at least one field to measure bucket ' + bucket)
    out = []
    for item in items:
        if isinstance(item, str):
            item = {'field': item}
        if not isinstance(item, dict) or not isinstance(item.get('field'), str):
            raise ValueError('Measure bucket ' + bucket + ' takes a field ID or {"field": ...}')
        unknown = set(item) - MEASURE_KEYS
        if unknown:
            raise ValueError('Unconsumed measure options in ' + bucket + ': ' + ', '.join(sorted(unknown)))
        out.append(item)
    return out


def _check(code, chart_type, spec, measures):
    template = TEMPLATES[chart_type]
    bound = {'axis'} | ({'stack'} if spec.get('stack') else set()) | set(measures)
    if code is not None:
        missing = [b for b in RECIPES[code][2] if b not in bound]
        if missing:
            raise ValueError(code + ' (' + RECIPES[code][0] + ') needs bindings for '
                             + ', '.join(missing) + '; resolve them from the model before creating the chart')
        if code in PANEL_RECIPES and sum(len(items) for items in measures.values()) != 1:
            raise ValueError(code + ' (' + RECIPES[code][0] + ') takes one measure per panel; add one '
                             + code + ' chart for each driver')
    for bucket, (low, high) in template['measures'].items():
        count = len(measures.get(bucket, []))
        if count < low:
            raise ValueError(chart_type + ' needs ' + str(low) + ' measure in bucket ' + bucket)
        if count > high:
            raise ValueError(chart_type + ' takes at most ' + str(high) + ' measure(s) in bucket ' + bucket)
    if len(measures) < template['minBuckets']:
        raise ValueError(chart_type + ' compares at least ' + str(template['minBuckets'])
                         + ' measures in different buckets (AC plus PY, PL or FC)')
    if spec.get('stack') and not template['stack']:
        raise ValueError(chart_type + ' has no stack bucket')
    if template['needsStack'] and not spec.get('stack'):
        raise ValueError(chart_type + ' needs a stack dimension')
    if template['fallback'] and not spec.get('stack') and len(measures) < 2:
        raise ValueError(chart_type + ' with one measure and no stack renders as ' + template['fallback']
                         + '; bind a stack dimension or measures in two buckets')


def recipe_chart(model, spec, registry, *, query_fields=()):
    """Build one recipe chart from semantic dimensions and Values fields.

    spec: {"label", "recipe" and/or "chartType", "category", optional "stack",
    "measures": {"AC": field or {"field", "aggregation", "label"} (a list for
    LINE/AREA), "PY"/"PL"/"FC": ...}, optional "theme" and optional "style"}.
    Field IDs come from the current model or a registered query catalog; nothing is
    inferred from labels.
    The chart keeps the IBCS chart theme, whether it names a recipe or only a
    "chartType"; "theme": "plan" leaves it on the Plan theme. "style" is the chart's
    background, font and data-label formatting; see runtime.chart_styling.
    """
    from .chart_filters import ensure_chart_filters
    from .construct import field
    from .intelligence import base
    from .linked_values import value_assignment
    unknown = set(spec) - SPEC_KEYS
    if unknown:
        raise ValueError('Unconsumed chart options: ' + ', '.join(sorted(unknown)))
    for key in ('label', 'category'):
        if not isinstance(spec.get(key), str) or not spec[key].strip():
            raise ValueError('Recipe chart needs a non-empty ' + key)
    code, chart_type = resolve_chart_type(spec)
    theme = spec.get('theme', 'ibcs')
    if theme not in CHART_THEMES:
        raise ValueError('Chart theme is ' + ' or '.join(CHART_THEMES) + ', not ' + repr(theme))
    raw = spec.get('measures')
    if not isinstance(raw, dict) or not raw:
        raise ValueError('Recipe chart needs measures keyed by bucket (AC, PY, PL, FC)')
    allowed = TEMPLATES[chart_type]['measures']
    stray = [b for b in raw if b not in allowed]
    if stray:
        raise ValueError(chart_type + ' has no measure bucket ' + ', '.join(stray)
                         + '; use ' + ', '.join(allowed))
    measures = {b: measure_entries(b, raw[b]) for b in MEASURE_BUCKETS if b in raw}
    _check(code, chart_type, spec, measures)

    category = field(model, spec['category'], 'rows', 0)
    category['bucketId'] = 'axis'
    assignments = [category]
    if spec.get('stack'):
        if spec['stack'] == spec['category']:
            raise ValueError('Use different fields for the category and the stack')
        stack = field(model, spec['stack'], 'columns', 0)
        stack['bucketId'] = 'stack'
        assignments.append(stack)
    seen = {}
    for bucket, items in measures.items():
        for order, item in enumerate(items):
            a = value_assignment(model, item['field'], registry, query_fields=query_fields, bucket=bucket,
                                 order=order, label=item.get('label'), aggregation=item.get('aggregation'))
            a['customName'] = item.get('label', a.get('customName', a['columnName']))
            identity = (a['id'], a.get('aggregationType'))
            if identity in seen:
                raise ValueError('The same value is bound to ' + seen[identity] + ' and ' + bucket
                                 + '; compare different measures')
            seen[identity] = bucket
            assignments.append(a)

    p = base(50, spec['label'])
    p['chartType'] = chart_type
    p['visualState']['chartType'] = chart_type
    p['pivotAssignments'] = assignments
    p = ensure_chart_filters(p)
    if theme == 'ibcs':
        p = apply_chart_theme(p)
    if spec.get('style'):
        from .chart_styling import apply_chart_style
        p = apply_chart_style(p, spec['style'])
    return p


def describe(properties):
    """Summarize a chart's template, bucket bindings and theme for a design brief or readback."""
    from .chart_styling import chart_style, data_labels, theme_owned_fields
    vs = properties.get('visualState', {})
    chart_type = properties.get('chartType', vs.get('chartType'))
    buckets = {}
    for a in properties.get('pivotAssignments', []):
        buckets.setdefault(a.get('bucketId'), []).append(a.get('customName') or a.get('name') or a.get('id'))
    codes = [code for code, (_, types, _) in RECIPES.items() if chart_type in types]
    return {'chartType': chart_type, 'recipes': codes, 'buckets': copy.deepcopy(buckets),
            'selectorsAgree': properties.get('chartType') == vs.get('chartType'),
            'theme': chart_theme(properties), 'style': chart_style(properties),
            # Read back apart: the labels need no feature switch, but a theme change strips the
            # fields named in labelThemeFields. The schema needs the switch.
            'dataLabels': data_labels(properties), 'labelThemeFields': theme_owned_fields(properties)}
