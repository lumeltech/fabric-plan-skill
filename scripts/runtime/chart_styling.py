"""Chart styling through the product's own AI chart-schema channel.

`visualAiSchemaState` is a top-level object of a chart's saved properties, beside
`visualState`. Before its first render the chart passes it to the schema compiler,
which runs each section through the same store services the format panels use, and
the field is then cleared. A chart keeps the styling without a state that is applied
on every load, which is what makes it the route for background, font and data-label
formatting.

Sections follow the product's schema validator (ap-web-client `src/ai/schemaValidator.ts`):
`canvas` takes theme, background and font; `dataLabel` takes `all`, `measures` keyed by
measure label and `variance`. Keys outside those lists are refused here so a wrong style
fails the build instead of being dropped in the browser. The compiler loads only when the
host's planningAIAssistant feature switch is on, so a styled chart is proven by rendering
it, not by reading the definition back. See references/ibcs-charts.md.
"""
import copy

FIELD = 'visualAiSchemaState'
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
    """Return ANALYTICS_PLUS properties whose chart carries style as its AI chart schema."""
    if properties.get('visualType') != 50:
        raise ValueError(FIELD + ' applies to an ANALYTICS_PLUS chart (visualType 50), not a '
                         + str(properties.get('visualType')))
    return with_chart_style(properties, ai_chart_state(style or {}))


def with_chart_style(properties, state):
    """Return chart properties carrying an already validated schema slice."""
    if not isinstance(state, dict) or not state:
        raise ValueError('Chart style sets nothing; give theme, background, font or dataLabels')
    out = copy.deepcopy(properties)
    # A chart restyled from an export keeps the sections it already carries.
    out[FIELD] = _deep(out.get(FIELD) or {}, state)
    return out
