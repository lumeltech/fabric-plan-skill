---
id: CH-LIB-04
name: Area charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
---

# Area charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Filled trends, stacked or overlapping.

## When to use

- Single-series trend emphasis; cumulative totals.

## UI path

Visualizations pane › Charts 100+ › Area, then pick the variant.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/chartType = "AREA"
Pointer: /properties/visualType = 50; registration = ANALYTICS_PLUS
```

Copy the complete same-kind Fabric Plan object. Capture any reference,
extrema or delta annotations on a filled trend with the object; stacked and
overlapping variants are not isolated by this evidence.

## Constraints

- A caption does not establish stacking. Capture overlap/stack mode, series
  order, fill and card ownership; only a true cumulative stack has a top
  boundary equal to the sum of included series at each date.
- Filled lines do not prove standalone AREA ownership or cumulative values;
  never accumulate point-in-time snapshot measures. Capture smoothing and
  missing-period behavior, and avoid implying negative rates or values
  between observations that the data cannot support.
- Intelligence chart library only; never a Power BI native visual.
- For an AC line over a PY area with variance fill, capture the variance-fill
  setting and define favorable direction per measure; growth in a cost or
  adverse rate is not automatically favorable.
- Filled trends inside KPI cards need captured scenario roles and native card
  composition; the standalone AREA enum is not a card template.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
AREA (standalone): chartType and rendererType "columnChart"
PERCENTAGE_STACKED_AREA: rendererType "stackedChart"
AREA_INTEGRATED (direct): rendererType "columnChart", chartOrientation
  "vertical", actualChartType "areaChart", lineSubChartType "integratedVariance"
AREA_INTEGRATED and AREA row trellis: chartType "columnChart", rendererType
  "smallMultiplesChart" (CH-MULT-01)
Evidence: [saved] saved owners only.
```

- A standalone AREA owner differs from a KPI `CARD` that keeps an AREA
  template [saved]. Do not read the root `AREA_INTEGRATED` id as an area
  renderer, or infer colors and cost polarity from the template name [saved].
- Direct AREA_INTEGRATED owners bind three ordered axis levels plus AC and
  PL; their AC/PL area entries are enabled while the absolute and percentage
  variance entries are disabled [saved]. Keep the axis hierarchy; never
  collapse it to one category.
- Trellis AREA_INTEGRATED owners bind axis, AC, PY and `row`, some also FC;
  their `splitByCategory.pivotValueAssignments` is empty or holds AC/PY or
  AC/PY/FC, so its length is no activation test [saved]. FC in those owners
  came from Planning sources, which are not enabled in this release.
- Percentage-stacked areas show shares, not currency totals; label and
  aggregate them as shares.
- Smoothing, missing periods, average/total panel meaning and variance-tier
  rendering are unresolved [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
