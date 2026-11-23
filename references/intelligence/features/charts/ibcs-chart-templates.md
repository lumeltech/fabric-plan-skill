---
id: CH-IBCS-01
name: IBCS chart templates C01–C13
area: charts
category: IBCS
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-ibcs-formats
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-ibcs-formats/column-and-bar-charts
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-ibcs-formats/waterfall-charts
  - https://lumel.com/ibcs/
---

# IBCS chart templates C01–C13

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

IBCS-certified chart templates (column/bar, multi-tier, waterfalls, line, area, scatter, bubble, small multiples) with comparison scenarios and strict/flexible IBCS themes.
Enforcing IBCS standards renames the comparison wells to AC, PY, PL and FC and
adds absolute and relative variance pin charts that can be kept or removed
(flexible IBCS). Variances calculate automatically once comparison measures
are mapped.

## When to use

- **Only when the user asks for IBCS.**
- Requested IBCS variance reporting: AC against PY, PL or FC with variance
  pins.

## UI path

Add an IBCS chart: Visualizations pane › Charts 100+ › IBCS filter, then pick
the chart type. On an existing chart: Chart › Templates › IBCS. Once IBCS is
requested, the pivot data window's
Enforce IBCS standards toggle (also in the advanced pivot's Advanced section)
switches a chart to IBCS notation with variance pins.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Apply with references/intelligence/ibcs/ibcs-rules.md.
- Scenario notation (AC solid, PY gray, PL outlined, FC hatched), AC/FC
  separators, relative-variance pins, integrated variance segments and
  combined AC&FC totals do not reveal the template number, theme or scenario
  mapping; capture those before authoring.
- Capture each template or composition separately, such as variance pins over
  AC columns, PY-to-AC bridges or panels combining variance steps with AC
  detail columns. Appearance does not identify a C-number or confirm
  favorability.
- Comparison charts use only the first AC measure; further Actual measures
  are not plotted. Up to three comparison measures are supported.
- PY, PL and FC must be bound semantic-model measures; Planning inputs,
  forecasts and scenarios stay blocked (module integration pending).
- Variance pins can be kept or removed; capture which pins are present rather
  than assuming them.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Evidence levels and saved IBCS signals

- Keep four levels apart: user-required design, saved native configuration,
  tested rendering or business results, and standards compliance. A template
  name or saved IBCS flag proves only saved configuration.
- Inspected charts count as IBCS-signal charts when they carry an IBCS-named
  template id, decoded `appearance.charts.theme: "ibcs"`,
  `numberFormatting.ibcsformat: true` or
  `comparisonMeasureMapping.standardNotation: true` [saved]. Saved IBCS
  signals are not proof of effective theme, runtime behaviour or standards
  compliance [open].
- Local theme split roughly evenly between `"ibcs"` and `"custom"`, and
  `standardNotation` was true, false or absent [saved]; keep each variant and
  never add a missing `comparisonMeasureMapping` group. Most column, waterfall
  and horizontal-stack owners qualified through `ibcsformat: true` alone
  [saved].
- A local `"ibcs"` string persisted after a report-level Light theme change
  [saved], so it never identifies the active report theme. Exports do not show
  which control (template, Enforce IBCS standards or theme) set a signal [open].

### Serialization

```text
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Keys: id, rendererType, chartOrientation, lockedTemplateId; actualChartType (some)
Pointer: /properties/visualState/hiddenProperties_!!!_measureConfig (JSON string)
Keys: config[] role, chart, enable, isVisible, chartIsVisible; type (variance roles)
Also: appearance (charts.theme, measuresStyle, variance),
      comparisonMeasureMapping (standardNotation), numberFormatting (ibcsformat)
Evidence: saved native exports of IBCS-signal charts [saved]
```

- `template`, `measureConfig`, `numberFormatting`, `xAxis` and `sorting` were
  JSON strings on every inspected chart; `appearance` and `yAxis` were strings
  except on one owner each; `comparisonMeasureMapping` and `dataLabel` were
  sometimes absent [saved]. Keep each boundary and absence.

### Saved native template identities

Partial decoded `template` identities with the buckets bound in those owners;
a third renderer value is `actualChartType`. Not payloads [saved].

| Template `id` | Renderer, orientation | Bound buckets | Note |
|---|---|---|---|
| `STACKED_COLUMN_VERTICAL` | `stackedChart`, vertical | 1–2 axis, AC, stack + PL, PL/FC or FC | Stack is not a scenario [saved] |
| `STACKED_COLUMN_HORIZONTAL` | `stackedChart`, horizontal | axis, AC, stack | No comparison [saved] |
| `PERCENTAGE_STACKED_VERTICAL` | `stackedChart`, vertical | 2 axis, AC, PL, FC, stack | Denominator unproven [saved] |
| `PERCENTAGE_STACKED_HORIZONTAL` | `stackedChart`, horizontal | axis, AC, stack | Not the plain stack [saved] |
| `COLUMN_VERTICAL` | `columnChart`, vertical | axis, AC + PY/FC, PL/FC or PY/PL/FC | Variance tiers [saved] |
| `COLUMN_VERTICAL` | `smallMultiplesChart`, vertical | axis, AC, PL, row | row = trellis [saved] |
| `COLUMN_HORIZONTAL` | `columnChart`, horizontal | axis, AC, PL | ΔPL bar, ΔPL% pin [saved] |
| `COLUMN_INTEGRATED_VERTICAL` | `columnChart`, vertical, `integratedVariance` | axis, AC, PL and/or FC | `_HORIZONTAL` also saved [saved] |
| `COLUMN_WATERFALL_VERTICAL` | `waterfallChart`, vertical | axis, AC, PY, PL, FC | AC `groupedBarWithWaterfall` [saved] |
| `COLUMN_WATERFALL_HORIZONTAL` | `waterfallChart`, horizontal | axis, AC, PY, PL | No comparison mapping [saved] |
| `SIDE_BY_SIDE_WATERFALL` | `columnChart`, horizontal | axis, AC, PY; or axis, PY, PL | Never add AC [saved] |
| `LINE` | `columnChart`, vertical | String hierarchy axis, AC, PY | Not a `lineChart` renderer [saved] |
| `STACKED_AREA` | `stackedChart`, vertical | axis, AC, FC, stack | Hatch flag is not visible hatch [saved] |
| `SCATTER_PLOT` | `bubbleChart`, vertical | axis, AC, PY, stack | Not a bubble donor [saved] |
| `BUBBLE_PLOT` | `bubbleChart`, vertical | axis, AC, PY, PL, stack | Mixed sources [saved] |
| `IBCS_BULLET_HORIZONTAL` | `columnChart`, horizontal, `ibcsBullet` | axis, AC, PY | Target is PY [saved] |
| `BOX_PLOT_VERTICAL` | `columnChart`, vertical, `boxplot` | axis, 5 BP + 5 BPN or 3 OBP | AC/PY in one owner [saved] |
| `MARIMEKKO_HORIZONTAL` | `otherChart`, horizontal, `marimekko` | axis, AC, PY | No stack [saved] |
| `PERCENTAGE_STACKED_MARIMEKKO_HORIZONTAL` | `stackedChart`, horizontal | axis, AC, PY, stack | `ibcsformat: false` [saved] |
| `GANTT_CHART` | `ganttChart`, vertical | task and date roles | No scenarios [saved] |

- `AREA_INTEGRATED`, `WATERFALL_VERTICAL` and `CARD` owners elsewhere carried
  all three signals; an unmarked `XVIZ_BULLET_HORIZONTAL` is not an IBCS owner
  [saved].
- Choose donors by template id, renderer, orientation, bucket cardinality,
  source kind, type, aggregation and mode, never by caption; Gantt donors also
  need matching `chartsMode.visualMode` and `ganttChartOptions.chartType`
  [saved]. Never swap direct and trellis `COLUMN_VERTICAL`, `SCATTER_PLOT` and
  `BUBBLE_PLOT`, or the two Marimekko templates.
- A user-corrected comparison chart kept `COLUMN_VERTICAL` in template `id` and
  `lockedTemplateId`; a corrected line kept `LINE` in both with
  `actualChartType: "lineChart"` [confirmed]. Check owner type, active template
  and lock together; a title proves nothing.
- Bubble `AC` was a measure without aggregation and `PY`/`PL` aggregated model
  columns [saved]; scatter and bubble buckets are coordinate or size slots, not
  scenarios. A String `LINE` axis does not establish chronology [open].
- Decoded `bulletConfig` subset:
  `{"actual":"AC","target":"PY","targetConfig":{"type":"integrated"},"targetIndicator":true,"showVarianceBar":false}`
  [saved]; not interchangeable with `XVIZ_BULLET_HORIZONTAL`.
- `boxPlotConfig` maps whiskers, quartiles and median to `BP`-family keys with
  `isAutoDataCalculation: true` [saved]; `whiskerType` `"minmax"` and
  `"MINMAX"` must not be assumed equivalent [confirmed].
- Gantt keeps `chartsMode.visualMode: "GANTT"` and `gantt*` groups such as
  `ganttChartOptions` [saved]; its `chartType` 0 (task, baseline, milestone)
  versus 1 (resource-oriented) has no verified label [open].
- The percentage Marimekko's `ibcsformat: false` beside local `"ibcs"` [saved]
  is a user-approved source-only exception, not a design rule [confirmed].
- A side-by-side waterfall bound `PY` to a Planning simulation input [saved];
  Simulation- and Planning-backed comparison slots are not enabled in this
  release.

### Scenario and variance tiers

```text
Pointer: /properties/visualState/hiddenProperties_!!!_measureConfig (JSON string)
Partial decoded config[] subset, never a replacement array:
  [{"role":"\u0394PL","chart":"varianceBar","enable":true},
   {"role":"\u0394PL%","chart":"variancePin","enable":true}]
Evidence: saved horizontal column owners [saved]
```

- Variance roles are `Δ` plus the reference bucket id, `%` for the relative
  tier, serialized as `\u0394`, with `type` `"ABSOLUTE_VARIANCE"` or
  `"RELATIVE_VARIANCE"` [saved].
- `chart` selectors: `groupedBar`, `groupedBarWithWaterfall`,
  `integratedVariance`, `waterfall` (scenario roles); `varianceBar`,
  `varianceWaterfall`, `variancePin` (variance roles) [saved]. The two absolute
  selectors are distinct, not labels for one setting.
- `enable`, `isVisible` and `chartIsVisible` are independent; binding is not an
  active tier [saved]. Saved waterfalls enabled ΔPY%/ΔPL% pins with the ΔPL bar
  disabled; one direct column enabled ΔPY/ΔPL bars with both pins disabled
  [saved]. Never enable a tier to match a donor.
- Integrated variance stores one `AC` role (`integratedVariance`), no PY/PL/FC
  roles and an enabled relative pin [saved]; overlap and pin rendering from
  that pair is not user-confirmed [open]. Its `varianceBar` was
  `isVisible: false` in every example; enabling it needs a capture [open].
- Bucket ids `AC`, `PY`, `PL`, `FC` match the Comparison 1–3 wells by position
  only [open].
- On repairs the user's latest working template wins; never infer a template
  conversion from the theme. If a chart cannot show every tier, propose
  separately captured variance charts aligned below it and confirm the layout.
- **Optional (companion default):** propose all three C03 tiers when a
  comparison exists unless the user wants columns only; record unverified
  tiers as gaps.

### Scenario styles and theme state

```text
Pointer: /properties/visualState/hiddenProperties_!!!_appearance
Partial decoded charts.measuresStyle:
  {"AC":{"pattern":"solid"},"PY":{"pattern":"solid"},
   "PL":{"pattern":"outlined"},"FC":{"pattern":"hatched"}}
Evidence: every bound owner's role record [saved]; precedence not rendered
```

- Role-keyed and field-keyed style entries coexist; PY grey is a colour rule,
  not a `pattern` value [saved].
- `stackedPattern` is separate: PL `outlined`/`partial_outlined`, FC
  `hatched`/`partial_hatched` [saved]; its rendered effect is [open].
- Trellis owners keeping `FC.pattern: "outlined"` without FC are user-approved
  dormant exceptions that never weaken FC hatching [confirmed].
- Historical before/after exports of an element-level IBCS theme showed
  [saved]: chart type `COLUMN_INTEGRATED_VERTICAL` to `COLUMN_VERTICAL`;
  `charts.theme`/`previousTheme` `"ibcs"`; `isDefaultMeta.theme: false`;
  `isStandardTheme: true`; AC solid `#262626`, PY solid `#bfbfbf`, PL outlined;
  `variance.colors`, `waterfall.breakdownVariance.colors` and
  `slopegraph.trendColor` to `#ff000a`/`#8eb900` (negative/positive);
  `measureConfig` unchanged. Recognition only, not a recipe.
- A series left on a generic colour needs its scenario well set; the companion
  attributed this to measure-name detection [open].
- Plan-level `theme.type` numbers differed between reports with IBCS-signal
  charts and have no verified UI label [open]; never write a guessed IBCS enum.
  Report-level themes can write chart-side `"custom"` markers and
  `hiddenProperties_!!!_customTheme` [saved]. Applying IBCS by definition to a
  report with no IBCS-styled chart is [open].

### Variance, numbers, axes and sorting

- `charts.variance` saved `invertColor: false`, `switchComparison: false`,
  `measureCombination: null`, `varianceDisplay: "bar"` and
  `varianceFillType: "area"` on every inspected chart;
  `varianceCustomization.enabled` on about half [saved].
- No `invertColor: true` example or isolated cost-inversion change exists
  [open]; never present it as a recipe or call cost colours compliant
  untested. Capture it first.
- All owners enabled number formatting, semantic formatting and the title
  scaling unit (`displayScalingIn: "title"`); nearly all saved
  `ibcsformat: true` and `scalingFactor: "uniform"` [saved].
- Stored: `noOfDecimal` 0 or 1, `noOfDecimalPercent` 2, decimal `"."`, mostly
  space thousands, formats `"x"`/`"-x"`, null `"hidden"`, zero `"0"`,
  `showValueColor: false` [saved]; observations, not a rounding policy.
- Misspelled `thousandSeperator`/`decimalSeperator` coexist with the correct
  keys; keep both, precedence [open]. Disabled custom-format entries do not
  prove active formatting [saved]. Uniform scaling does not prove equal units
  or axis extents [open].
- X axes were all enabled, value axes mostly, `scaleType` always linear
  [saved]. Label `display` values: `auto`, `limited`, `nthLabel`, `minMax`
  [saved]. No first/last-point flag was found, and a missing label record does
  not prove disabled labels [open].
- Sort state was ascending, descending or reset, with ranking on a few owners,
  targeting the category, native measure or variance roles, or field
  expressions [saved]; rebind expressions, and `reset` is not proven
  chronological order.

### C01–C13 correspondence

C-numbers and chart-type names below come from this feature's listed
documentation sources; no saved owner stores a C-number. Each pairing is by
documented chart type and wells only [open].

| Documented template (chart type) | Saved native template |
|---|---|
| C01 stacked column | `STACKED_COLUMN_VERTICAL` |
| C02 stacked bar | `STACKED_COLUMN_HORIZONTAL` |
| C03 multi-tier column (Overlapped column) | `COLUMN_INTEGRATED_VERTICAL`, or `COLUMN_VERTICAL` with tiers |
| C04 multi-tier bar, C06 bars with waterfall (Waterfall + bar) | `COLUMN_WATERFALL_HORIZONTAL` |
| C05 columns with waterfall (Waterfall + column) | `COLUMN_WATERFALL_VERTICAL` |
| C07–C08 line and area family | `LINE`, `STACKED_AREA` |
| C09–C10 scatter and bubble family | `SCATTER_PLOT`, `BUBBLE_PLOT` |
| C12 vertical waterfall (Side by side waterfall) | `SIDE_BY_SIDE_WATERFALL`, saved orientation `horizontal` |
| C13 small multiples | `COLUMN_VERTICAL` with `smallMultiplesChart` |

- C11 is not named in the documented overview. Tiered `COLUMN_HORIZONTAL`,
  percentage stacks, the IBCS bullet, box plot, both Marimekko templates and
  Gantt carried IBCS signals without an established C-number [open].

### Workflow notes

- Fetch the latest definition, make one bounded edit from a compatible donor,
  then read back chart type, bindings, report theme, applied-theme map, titles,
  geometry and variance roles; readback is not rendering.
- Map scenario slots from the request and the model; ask one short question
  only when two measures fit one slot equally well.
- An AC/PL `BREAKDOWN_WATERFALL_VERTICAL` bridge with a `stack` breakdown
  (both roles `groupedBarWithWaterfall`) combined two separately saved
  patterns; its per-category arithmetic is [open].

## Related features

- `MX-TPL-04`
