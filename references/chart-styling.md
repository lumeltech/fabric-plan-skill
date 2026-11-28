# Chart styling

`runtime.chart_styling` gives an Analytics+ visual its own plot background, global font, theme and
data-label formatting. It applies to any `visualType` 50 visual: a recipe chart, a plain chart, a
KPI card, or every visual on a page through a page-level style.

## Contents

- [Two channels](#two-channels)
- [What a style takes](#what-a-style-takes)
- [Check and report](#check-and-report)

## Two channels

A style is written on two channels of unequal reliability. Say which one each part used.

**Data labels go to the chart store**, as the stringified `hiddenProperties_!!!_dataLabel` member of
`visualState`; no switch is on that path and `data_labels` reads it back. Key entries by the measure's
**field name** plus `default`: the product drops a key its built defaults lack, without a message.
A theme change then strips `color`, `background`, `fontSize` and `bold` from the slice and persists
the stripped version, so those four are saved rather than proven.

**Background, global font, theme and variance labels go to the AI schema channel**, as
`visualAiSchemaState` beside `visualState`, which the chart's schema compiler consumes before its
first render and then clears. That compiler loads only while the host's `planningAIAssistant` switch
is on, which it is not by default; with it off the saved object is inert: no error, no styling, and
nothing in the readback distinguishes it from a broken write.

## What a style takes

- A chart spec takes `"style"`: `{"theme", "background", "font": {"family", "size", "color",
  "responsive", "autoColor"}, "dataLabels": {"all", "measures": {<measure label>: ...}, "variance"}}`.
  `runtime.intelligence.card` takes the same key, and so does a page, where it is the page default.
  A visual's own style overrides only the options it names.
- Address a data label by the label the chart shows: the spec's `label`, or an export's `customName`.
  The writer resolves that to the field name verbatim, so a model column named ` Sales` keeps its
  leading space. An unbound name, or an option the product's validator rejects, **fails the build**
  instead of quietly doing nothing.
- `color` clears `contrastColor`, or the theme's auto-contrast color wins; `background` sets
  `showBackground`, or it reads as transparent; a `fontSize` is marked user-changed, or the
  bar-width-based size replaces it at render; `show` alone toggles labels.
- Only an ANALYTICS_PLUS chart carries a style, and `apply_chart_style` merges with what an export
  already holds. `axis`, `legend`, `measureSeries` and `rows` share the AI schema channel and are not
  written here; variance labels stay there because their store keys are resolved from the data layer
  at render time.

## Check and report

1. After building, `chart_style(properties)` reads the AI schema channel and `data_labels(properties)`
   the store slice; `runtime.ibcs_charts.describe(properties)` reports both, plus the styled fields a
   theme change strips, under `labelThemeFields`.
2. After an authorized update, export the Plan and compare the chart's `hiddenProperties_!!!_dataLabel`
   entry by entry (`default` and each measure's field name) and its `visualAiSchemaState`, including
   whether the chart cleared the latter once it rendered.
3. Report the two channels apart:
   - `show`, `display` and `position` as saved to the chart store, switch-free;
   - `color`, `background`, `fontSize` and `bold` as saved to the chart store but stripped by the next
     theme change;
   - background, global font, theme and variance labels as saved through the AI schema only, rendering
     only where `planningAIAssistant` is on; claim them rendered only from the browser;
   - rendering as not tested.
