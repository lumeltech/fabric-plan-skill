---
id: CH-LIB-02
name: Waterfall charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: verified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-ibcs-formats/waterfall-charts
---

# Waterfall charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Bridges from a start to an end value through increases and decreases.

## When to use

- Variance bridges PY → AC, PL → AC.

## UI path

Visualizations pane › Charts 100+ › Waterfall, then pick the variant.

## Definition encoding

```text
Pointer: /properties/chartType = "WATERFALL_SINGLE_MEASURE_VERTICAL" (default
         single-measure waterfall); "COLUMN_WATERFALL_VERTICAL" observed earlier
Pointer: /properties/visualType = 50; registration = ANALYTICS_PLUS
Pointer: /properties/pivotAssignments (bucketId "axis" = category; "AC" = measure)
Pointer: /properties/visualState/hiddenProperties_!!!_waterfallTotalLabels = {"labels": []}
Single-measure bridge (runtime-verified): axis = a step dimension sorted by its model
  sort-by column, AC = one signed impact measure; a visual-level VALUES include filter
  on the step field keeps only the start and step members; the native total bar closes
  the bridge, and waterfallTotalLabels.labels[].text renames it to the end
  scenario's label; commonSettings.showTotalBar:true.
Evidence: live export of a UI-created test Plan (default state); bridge rendering and
          total label user-confirmed in a published report.
```

The two waterfall enums are distinct; never convert one into the other.
Copy the saved Fabric Plan waterfall and bindings/settings. A bridge with
member contributions and a variance annotation is presentation evidence
only. Confirm scenario endpoints and sign semantics in the registry; the enum
alone does not configure the bridge.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- Bind start/end scenarios explicitly, including mini bridges inside KPI
  cards; a variance label can name a different scenario than the bound value.
  Validate start + signed steps = end (for example `LM + delta = AC`).
- Reconcile additive amounts at one target, date and grain with aligned
  periods, not period totals or percentages. Require comparable populations
  before reconciling period deltas to annual totals.
- Capture level versus contribution roles. Non-additive percentages need a
  defensible attribution method; never sum member rates to force a group
  change, and label percentage-point versus relative change distinctly.
- Distinguish contribution steps from totals/subtotals and reconcile the
  bridge to the accounting definition. Anchor subtotals, draw them distinctly
  from increases and avoid truncated or duplicate labels.
- A bridge from zero to an anchored total Variance bar explains the aggregate
  gap, not target-to-actual levels. Do not count companion AC detail columns
  again as bridge steps.
- Faded fills or bases do not establish IBCS, axis-break settings or native
  card ownership; capture them. A subtitle naming a calculation such as CAGR
  does not prove that calculation.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Ids -> rendererType:
  WATERFALL_SINGLE_MEASURE_VERTICAL, WATERFALL_SINGLE_MEASURE_HORIZONTAL,
  WATERFALL_VERTICAL, COLUMN_WATERFALL_VERTICAL -> "waterfallChart"
  STACKED_WATERFALL_VERTICAL, BREAKDOWN_WATERFALL_VERTICAL,
  PAIRED_WATERFALL_VERTICAL -> "stackedChart"
Horizontal single-measure: owner chartType, id, previousId and lockedTemplateId
  all WATERFALL_SINGLE_MEASURE_HORIZONTAL; chartOrientation "horizontal"
WATERFALL_VERTICAL: actualChartType "groupedBarWithWaterfall"; binds axis, AC
  and exactly one of PL, PY or FC
Evidence: [saved] saved owners; not isolated by a before/after capture.
```

```text
Pointer: hiddenProperties_!!!_appearance (JSON string) -> charts.waterfall
Keys (single-measure owner): isGrandTotalEnabled, isInterimTotalEnabled and
  isVarianceEnabled true; enabled 1px solid connector lines; subtotal/total,
  intermediate and summation bar styles; stack color; subgroup settings
Pointer: hiddenProperties_!!!_waterfallTotalLabels -> labels[] auto record:
  text "Total", fontSize, measureKey "AC", isVisible true, isDirectUserEdit false
Evidence: [saved]
```

- The auto "Total" record materializes on save; `isDirectUserEdit: false`
  marks it as not user-authored [saved].
- WATERFALL_VERTICAL keeps its AC `groupedBarWithWaterfall` entry enabled and
  visible, while its percentage `variancePin` saves `enable: true`,
  `chartIsVisible: true` and `isVisible: false` [saved]. What renders from
  that mix is unresolved [open].
- Roles seen: `axis`, `AC`, `PY`, `PL` and one or more `stack` [saved].
  Paired and stacked variants save stack mapping `from: "group"`, and some
  breakdowns stack the synthetic Measures category with native grouping
  (`CH-SPLIT-01`) [saved].
- Breakdown of existing measures by a category (user correction): bind the
  real category field on `axis`, keep the synthetic Measures stack, list each
  existing measure once and register the visual filter. Test negative cases
  for a missing axis field and repeated measure entries; a nonempty synthetic
  stack or a correct total does not prove the intended analysis [confirmed].
  This does not make a semantic axis mandatory for every measure-only
  waterfall [confirmed].
- `comparisonMeasureMapping.config.AC` resolves the bound AC measure next to
  `standardNotation: true` and `fieldsMeta` role names; never turn these into
  new model measures [saved].
- Some waterfalls save `legendSettings.showTitleAsLegend: false`, and title
  heights differ per variant (`CH-DISP-01`) [saved]. The horizontal
  column-waterfall (`COLUMN_WATERFALL_HORIZONTAL`, `CH-IBCS-01`) saves
  `chartSettings.viewMode: 1` [saved]; its UI label is unknown [open].
  `xAxis.enableScroll: "auto"` is not a passed no-scroll test [saved].
- Saved owners also carry `hiddenProperties_!!!_intermediateSumContextMenu`
  [saved]. Its role in interim totals is unresolved [open].
- Choose the variant by question: single-measure bridge, scenario comparison,
  composition (stacked or breakdown) or paired change. Validate each variant
  on its own; a working single-measure bridge does not validate the others.
- A saved side-by-side waterfall bound a Planning simulation input in its
  `PY` slot [saved]; Planning inputs are not enabled in this release.
  Side-by-side IBCS waterfalls follow `CH-IBCS-01`.
- Interim-total creation, breakdown accumulation, paired semantics and the
  filter response of native totals are unresolved [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
