---
id: CH-LIB-12
name: Gauges
area: charts
category: Chart library
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
---

# Gauges

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Value against a bounded scale.

## When to use

- Bounded ratios only.

## UI path

Visualizations pane › Charts 100+ › Gauge, then pick the variant.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/chartType = "ANGULAR_GAUGE"
Pointer: /properties/pivotAssignments (AC = actual measure; PY bucket = comparison measure)
Pointer: /properties/visualState/hiddenProperties_!!!_gaugeConfig (JSON string)
Decoded keys: primaryActual = "AC"; primaryTarget = "PY"
```

Copy the saved Fabric Plan gauge and complete settings. A semicircle
target-achievement presentation does not isolate range, angle or
percentage-display controls. The `PY` bucket can hold a plan target, not a
prior-year measure; bind it to the approved comparison measure.

## Constraints

- Resolve cohort, numerator/denominator and filter context before rendering
  success, especially when related totals are zero. The saved gauge family
  does not validate a measure binding or a zero fallback.
- Capture card versus standalone ownership, scale and target tick.
- Intelligence chart library only; never a Power BI native visual.
- Define target, range and overachievement behavior; do not clamp at 100%
  or assume a screenshot percentage establishes the stored maximum.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Ids: ANGULAR_GAUGE, LINEAR_GAUGE_HORIZONTAL; template rendererType, chartType
  and actualChartType "gaugeChart"
Pointer: hiddenProperties_!!!_gaugeConfig (JSON string), further keys:
  primaryMax "PL", primaryMin "FC"; secondary slots AC1-AC4; chartType
  "semi-circle" (in angular and linear owners alike); start/end angles
  -135/135; reverseAxis false; roundedEdge false; linearGaugeWidthHeight and
  a gap setting (linear owner 32 and 0; angular null and 1)
Bands: primary.comparisonGaugeBand {enabled, noOfBands, comparedSeries
  "dynamic", gaugeBandConfig[]}; entries chain fromMeasure/toMeasure through
  bucket aliases "bands" and "bands1"; custom bounds null
Evidence: [saved] saved owners only.
```

- `gaugeConfig.chartType` does not select the family; keep the owner and
  template id [saved].
- Configured but unbound slots (targets, minimum, secondary AC1-AC4) are not
  bindings; never fabricate a target or minimum [saved]. Saved bindings: AC
  only, AC plus a `row` trellis, and AC + PY on the linear gauge [saved].
- In dynamic band mode, retained percentage thirds are not active bounds; the
  last band has no `toMeasure` and PL supplies the maximum [saved].
- The inspected dynamic bands were bound through the `bands` bucket to
  editable Planning inputs [saved]; that source is not enabled in this
  release. Binding model measures to `bands` is uncaptured [open].
- Test ordered boundaries, a maximum above the last boundary, blank, equal or
  reversed thresholds, and values outside the range.
- Bounds for unbound roles, numeric units, semi-circle relevance in linear
  mode and threshold semantics are unresolved [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
