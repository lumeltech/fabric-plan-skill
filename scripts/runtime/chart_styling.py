"""Chart styling, written on whichever channel the product actually reads.

Two channels, and they are not equally reliable.

**Data labels go to the chart store.** The format panel writes `dataLabel.labelStyle` in the
chart store, and that slice persists as the stringified `hiddenProperties_!!!_dataLabel` member
of the chart's `visualState` (`ap-web-client/src/pages/Fabric/Fabric.service.ts:114,905-931`,
`ap-core/src/store/utils/StatePersistHelper.ts:1653-1663`). On load the host re-reads it and deep
merges it over the theme defaults (`Fabric.service.ts:672-786`, `ModuleProps.builder.ts:76`,
`ap-core/src/store/utils/StoreUtils.ts:683-709`). Nothing on that path checks a feature switch, so
this is the route that changes what a planner sees.

**Background, global font and theme go to the AI schema channel.** `visualAiSchemaState` is a
top-level object of a chart's saved properties, beside `visualState`. Before its first render the
chart passes it to the schema compiler, which runs each section through the same store services the
format panels use, and the field is then cleared. The compiler loads only while the host's
`planningAIAssistant` feature switch is on (`ap-web-client/src/ai/loadChartAISchemaBridge.ts:16`).
With the switch off the saved object is inert: no error and no styling. So these three are claimed
only as saved, never as rendered, and a chart styled this way must be checked in the browser.
Variance labels stay here too, because their store keys are resolved from the data layer at render
time and cannot be authored offline.

Friendly option names map onto store keys through
`ap-web-client/src/ai/schema/dataLabelFieldMap.ts`. Keys the product's validator does not take are
refused here, so a wrong style fails the build instead of being dropped in the browser. See
references/ibcs-charts.md.
"""
import copy

from .codec import dumps, loads

FIELD = 'visualAiSchemaState'
# The persisted chart-store slice the Data Label panel writes. A bare `dataLabel` key in
# visualState is dropped: the host only splits `_!!!_` keys (Fabric.service.ts:767-777).
DATALABELS = 'hiddenProperties_!!!_dataLabel'
THEMES = ('dark', 'midNight', 'colorBlindDark', 'colorBlindWhite', 'whiteAndBlue', 'ibcs',
          'inforiver', 'native', 'lumel', 'custom')
FONT_KEYS = ('family', 'size', 'color', 'responsive', 'autoColor')
LABEL_KEYS = ('show', 'display', 'position', 'fontSize', 'color', 'bold', 'italic', 'underline',
              'background', 'showBackground')
# The variance label is its own label and has no underline control.
VARIANCE_KEYS = tuple(k for k in LABEL_KEYS if k != 'underline')
LABEL_DISPLAYS = ('auto', 'limited', 'minMax', 'minOnly', 'maxOnly', 'firstLast', 'firstOnly',
                  'lastOnly', 'nthLabel', 'none', 'outlier', 'nthAndLast')
LABEL_POSITIONS = ('auto', 'outside', 'insideTop', 'insideCenter', 'insideBottom', 'center')
STYLE_KEYS = {'theme', 'background', 'font', 'dataLabels'}
FLAGS = {'show', 'bold', 'italic', 'underline', 'showBackground', 'responsive', 'autoColor'}
COLORS = {'color', 'background'}
ENUMS = {'display': LABEL_DISPLAYS, 'position': LABEL_POSITIONS}
# Friendly data-label option -> chart store key, from dataLabelFieldMap.ts.
LABEL_STORE = {'show': 'enabled', 'display': 'display', 'position': 'position',
               'fontSize': 'fontSize', 'color': 'fontColor', 'background': 'background',
               'showBackground': 'showBackgroundColor'}
# Bold, italic and underline live in a nested group, not beside the other fields.
LABEL_FONT_STORE = {'bold': 'isBold', 'italic': 'isItalic', 'underline': 'isUnderLine'}


def _option(value, key, where):
    if key in FLAGS:
        if not isinstance(value, bool):
            raise ValueError(where + ' ' + key + ' is true or false')
    elif key in COLORS:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(where + ' ' + key + ' needs a color string')
        return value.strip()
    elif key == 'size' or key == 'fontSize':
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(where + ' ' + key + ' needs a positive font size')
    elif key in ENUMS:
        if value not in ENUMS[key]:
            raise ValueError(where + ' ' + key + ' is ' + ' or '.join(ENUMS[key]) + ', not ' + repr(value))
    elif key == 'family':
        if not isinstance(value, str) or not value.strip():
            raise ValueError(where + ' font family needs a name')
        return value.strip()
    return value


def _options(value, allowed, where):
    if not isinstance(value, dict):
        raise ValueError(where + ' takes an object of format options')
    unknown = set(value) - set(allowed)
    if unknown:
        raise ValueError(where + ' supports ' + ', '.join(allowed) + ', not ' + ', '.join(sorted(unknown)))
    return {k: _option(v, k, where) for k, v in value.items()}


def _canvas(style):
    canvas = {}
    if 'theme' in style:
        theme = style['theme']
        if theme not in THEMES:
            raise ValueError('canvas theme is ' + ' or '.join(THEMES) + ', not ' + repr(theme))
        canvas['theme'] = theme
    if 'background' in style:
        canvas['background'] = _option(style['background'], 'background', 'canvas')
    if 'font' in style:
        canvas['font'] = _options(style['font'], FONT_KEYS, 'canvas font')
    return canvas


def _data_labels(value):
    if not isinstance(value, dict):
        raise ValueError('dataLabels takes all, measures and variance')
    unknown = set(value) - {'all', 'measures', 'variance'}
    if unknown:
        raise ValueError('dataLabels has no section ' + ', '.join(sorted(unknown))
                         + '; use all, measures or variance')
    out = {}
    for key in ('all', 'variance'):
        if key in value:
            out[key] = _options(value[key], LABEL_KEYS if key == 'all' else VARIANCE_KEYS,
                                'data label ' + key)
    if 'measures' in value:
        measures = value['measures']
        if not isinstance(measures, dict) or not measures:
            raise ValueError('data label measures names at least one measure label')
        out['measures'] = {}
        for name, style in measures.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError('data label measures are keyed by the measure label the chart shows')
            out['measures'][name.strip()] = _options(style, LABEL_KEYS, 'data label ' + repr(name))
    return out


def _label_entry(options, where):
    """Return one friendly data-label style as the store entry the format panel writes."""
    checked = _options(options, LABEL_KEYS, where)
    entry, font = {}, {}
    for key, value in checked.items():
        if key in LABEL_FONT_STORE:
            font[LABEL_FONT_STORE[key]] = value
        else:
            entry[LABEL_STORE[key]] = value
    # A theme-driven contrast color wins over fontColor while contrastColor is on.
    if 'fontColor' in entry:
        entry['contrastColor'] = False
    # background is only read when the label's background is switched on.
    if 'background' in entry and 'showBackgroundColor' not in entry:
        entry['showBackgroundColor'] = True
    if font:
        entry['fontStyle'] = font
    return entry


def _bound_measures(properties):
    """Return the chart's value roles in order, and every name each role answers to.

    The store keys labels by role, because `commonSettings.savePropertyAgainstRole` is on in the
    product's defaults (`ap-core/src/store/models/commonSettings.ts:383`). Authoring stays with the
    name the chart shows, so both the `customName` and the model column name are accepted.
    """
    roles, by_name = [], {}
    for a in properties.get('pivotAssignments', []):
        if a.get('dataRoleType') != 'Measure':
            continue
        role = a.get('bucketId')
        if not role or role in roles:
            continue
        roles.append(role)
        for name in (a.get('customName'), a.get('name'), a.get('columnName')):
            if name and name not in by_name:
                by_name[name] = role
    return roles, by_name


def data_label_entries(labels, properties):
    """Return {role: store entry} for a friendly dataLabels section, variance excepted.

    Variance labels are keyed by a name the data layer resolves while the chart renders, so they
    stay on the AI schema channel and are not returned here.
    """
    if not isinstance(labels, dict):
        raise ValueError('dataLabels takes all, measures and variance')
    unknown = set(labels) - {'all', 'measures', 'variance'}
    if unknown:
        raise ValueError('dataLabels has no section ' + ', '.join(sorted(unknown))
                         + '; use all, measures or variance')
    roles, by_name = _bound_measures(properties)
    out = {}
    if 'all' in labels:
        if not roles:
            raise ValueError('The chart has no bound measures, so its data labels cannot be addressed')
        entry = _label_entry(labels['all'], 'data label all')
        out = {role: entry for role in roles}
    if 'measures' in labels:
        measures = labels['measures']
        if not isinstance(measures, dict) or not measures:
            raise ValueError('data label measures names at least one measure label')
        if not roles:
            raise ValueError('The chart has no bound measures, so its data labels cannot be addressed')
        for name, style in measures.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError('data label measures are keyed by the measure label the chart shows')
            name = name.strip()
            role = by_name.get(name, name if name in roles else None)
            if role is None:
                raise ValueError('The chart has no measure named ' + repr(name) + '; it binds '
                                 + ', '.join(sorted(by_name)))
            out[role] = _deep(out.get(role) or {}, _label_entry(style, 'data label ' + repr(name)))
    return out


def data_labels(properties):
    """Return the chart's saved data-label store slice, or None when it carries none."""
    value = properties.get('visualState', {}).get(DATALABELS)
    if value is None:
        return None
    if isinstance(value, str):
        value = loads(value)
    if not isinstance(value, dict):
        raise ValueError('The saved ' + DATALABELS + ' is not an object; inspect it before restyling')
    return copy.deepcopy(value)


def with_data_labels(properties, entries):
    """Return chart properties whose data-label slice carries these role entries."""
    if not entries:
        raise ValueError('Data labels set nothing; give all or measures')
    out = copy.deepcopy(properties)
    if out.get('visualType') != 50:
        raise ValueError(DATALABELS + ' applies to an ANALYTICS_PLUS chart (visualType 50), not a '
                         + str(out.get('visualType')))
    visual_state = out.setdefault('visualState', {})
    saved = data_labels(out) or {}
    label_style = saved.setdefault('labelStyle', {})
    for role, entry in entries.items():
        label_style[role] = _deep(label_style.get(role) or {}, entry)
    visual_state[DATALABELS] = dumps(saved).strip()
    return out


def ai_chart_state(style):
    """Return the schema sections a friendly chart style maps to, empty when it asks for nothing.

    style: {"theme", "background", "font": {"family", "size", "color", "responsive", "autoColor"},
    "dataLabels": {"all"/"variance": {"show", "display", "position", "fontSize", "color", "bold",
    "italic", "underline", "background", "showBackground"}, "measures": {<measure label>: ...}}}.
    Data labels are addressed by the measure label the chart shows, the same name the chart spec's
    valueLabel or customName gives.
    """
    if not isinstance(style, dict):
        raise ValueError('Chart style takes theme, background, font and dataLabels')
    unknown = set(style) - STYLE_KEYS
    if unknown:
        raise ValueError('Unconsumed chart style options: ' + ', '.join(sorted(unknown))
                         + '; supported: theme, background, font, dataLabels')
    out = {}
    canvas = _canvas(style)
    if canvas:
        out['canvas'] = canvas
    if 'dataLabels' in style:
        labels = _data_labels(style['dataLabels'])
        if labels:
            out['dataLabel'] = labels
    return out


def _deep(base, override):
    """Return base with override merged in; a value that is not an object replaces what it meets."""
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def merge_styles(*styles):
    """Return one chart style where a later style replaces only the options it names."""
    out = {}
    for style in styles:
        if style:
            out = _deep(out, style)
    return out


def chart_style(properties):
    """Return the AI chart schema a chart's properties carry, or None when it carries none."""
    value = properties.get(FIELD)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError('The saved ' + FIELD + ' is not an object; inspect it before restyling the chart')
    return copy.deepcopy(value)


def apply_chart_style(properties, style):
    """Return ANALYTICS_PLUS properties carrying style on the channel the product reads it from.

    `dataLabels` all and measures go to the chart's own data-label store slice, which needs no
    feature switch. Theme, background and global font go to the AI schema channel, which does, and
    so does the variance label; both are reported as saved, not as rendered.
    """
    if properties.get('visualType') != 50:
        raise ValueError(FIELD + ' applies to an ANALYTICS_PLUS chart (visualType 50), not a '
                         + str(properties.get('visualType')))
    if not isinstance(style, dict):
        raise ValueError('Chart style takes theme, background, font and dataLabels')
    unknown = set(style) - STYLE_KEYS
    if unknown:
        raise ValueError('Unconsumed chart style options: ' + ', '.join(sorted(unknown))
                         + '; supported: theme, background, font, dataLabels')
    out = copy.deepcopy(properties)
    labels = style.get('dataLabels') or {}
    entries = data_label_entries(labels, out) if labels else {}
    if entries:
        out = with_data_labels(out, entries)
    canvas = {key: value for key, value in style.items() if key != 'dataLabels'}
    if labels.get('variance'):
        canvas['dataLabels'] = {'variance': labels['variance']}
    state = ai_chart_state(canvas) if canvas else {}
    if state:
        out = with_chart_style(out, state)
    if not entries and not state:
        raise ValueError('Chart style sets nothing; give theme, background, font or dataLabels')
    return out


def with_chart_style(properties, state):
    """Return chart properties carrying an already validated schema slice."""
    if not isinstance(state, dict) or not state:
        raise ValueError('Chart style sets nothing; give theme, background, font or dataLabels')
    out = copy.deepcopy(properties)
    # A chart restyled from an export keeps the sections it already carries.
    out[FIELD] = _deep(out.get(FIELD) or {}, state)
    return out
