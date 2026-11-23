---
id: CH-LIB-10
name: Box plots
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/visualization-library
---

# Box plots

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Distribution with quartiles and outliers: whisker min, lower quartile, median,
upper quartile and whisker max per category. Variants: pre-calculated
(quartile/whisker measures), dynamic (computed from several raw-value
measures), single-measure, overlapped (prior-period boxes), combination (up to
four Actual/Comparison overlay lines, optional integrated variance) and
forecast. Conditional formatting can highlight boxes by quartile values.

## When to use

- Spread across entities.
- Distributions across periods or categories, from pre-computed statistics or
  raw value measures.
- Current versus prior-period spread (overlapped boxes) or actual/comparison
  overlays on the distribution.

## UI path

Visualizations pane › Charts 100+ › Statistical › Boxplot. Put the dimension
in Category (x-axis) and the measures in the Boxplot well. Boxplot auto
sorting in the pivot data window assigns quartile,
median and whisker roles; turn it off to choose them under Settings › Canvas ›
Boxplot, which also holds Line Type › Integrated Variance and the box (solid,
outlined, hatched), whisker, median and stem formats. Prior-period quartiles go
to Box (Overlapped); forecast quartiles to Boxplot (Forecast).

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- Pre-calculated boxes need at least lower-quartile, median and
  upper-quartile measures; dynamic boxes need Boxplot auto sorting on.
- Manual quartile, median and whisker selection works only with auto sorting
  off; the median and whiskers can be hidden.
- Single-measure boxes need the category in small multiples (not Category)
  plus Split categories into measures in the pivot data window.
- With axis hierarchies, turn off Axis › X-Axis › Category grouping for clean
  boxes; subtotal boxes are then hidden.
- Comparison, overlay and forecast wells take bound semantic-model measures
  only; Planning inputs, forecasts and scenarios stay blocked until module
  integration.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "BOX_PLOT_VERTICAL"
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"columnChart"; chartOrientation:"vertical";
              actualChartType:"boxplot"
Pointer: /properties/pivotAssignments
Observed buckets: axis; five repeated BP; optional repeated BPN or OBP;
                  optional AC, PY, PL and a tooltip role
Pointer: /properties/visualState/hiddenProperties_!!!_boxPlotConfig (JSON string)
Decoded keys: upperQuartile, medianQuartile, lowerQuartile, whiskerMax,
              whiskerMin ({measureKey}, plus enabled on median and whiskers);
              meanLine.enabled; commonSettings{isAutoDataCalculation,
              whiskerType, showBoxPlotAutoData, pattern, lineType};
              boxPlotForecast; boxPlotOverlapped
Partial: {"upperQuartile":{"measureKey":"BP"},"medianQuartile":{"measureKey":"BP1"},
          "lowerQuartile":{"measureKey":"BP2"},"whiskerMax":{"measureKey":"BP3"},
          "whiskerMin":{"measureKey":"BP4"},"meanLine":{"enabled":false}}
Evidence: [saved] every inspected saved box plot; not isolated or re-rendered.
```

- Selectors point at generated keys of the repeated `BP` assignments; every
  inspected owner used the mapping in the partial above, but treat it as
  owner-local, not a universal position rule [saved].
- `boxPlotForecast` maps `BPN` through `BPN4`; `boxPlotOverlapped` keeps
  `OBP`/`OBP1` quartile and `OBP2`/`OBP3` warning selectors. Both persist
  without matching assignments, so neither the groups nor their `showBoxPlot`
  flags prove a bound or visible extra distribution [saved].
- Do not deduplicate repeated buckets, invent missing overlay assignments or
  read business forecast meaning from a group name.
- Every inspected owner saves `isAutoDataCalculation: true` beside explicit
  selectors [saved]. This differs from the documented rule that manual
  selection needs auto sorting off; their precedence and relation are
  unresolved, the companion's one-setting test was deferred, and the
  documented rules above stand [open].
- `whiskerType` is saved as both `"minmax"` and `"MINMAX"`; keep the exported
  casing and never normalize it [confirmed]. Whether the two are equivalent is
  unresolved [open].
- Saved values include `pattern` `"solid"`, `"outlined"` or `"hatched"`,
  `lineType` `"default"` or `"integratedVariance"` and `showBoxPlotAutoData`
  true or false [saved]. Their mapping to the documented box formats and
  Line Type › Integrated Variance is not isolated [open].
- Establish from the model whether bound fields are raw observations or
  precomputed statistics, never from a caption; then validate ordered
  quartiles and whiskers, missing observations and outliers.

## Related features

- `CH-AX-01`
- `CH-LBL-01`
