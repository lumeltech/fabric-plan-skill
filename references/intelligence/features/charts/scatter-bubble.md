---
id: CH-LIB-07
name: Scatter and bubble charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-ibcs-formats/scatter-and-bubble-charts
---

# Scatter and bubble charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Relationship between two measures, optional size measure.

## When to use

- Quadrant analysis.

## UI path

Visualizations pane › Charts 100+ › Bubble/ Scatter, then pick the variant.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/chartType = "BUBBLE_PLOT"
Pointer: /properties/pivotAssignments
Observed buckets: axis (category field), AC (measure), PY (ratio measure),
                  PL (measure; reused the AC measure), stack (grouping field)
Pointer: /properties/visualState/hiddenProperties_!!!_analytics (JSON string)
```

Copy the whole saved Fabric Plan bubble object. Do not infer bubble-size
semantics, causation, or whether a visible connecting line is a fitted trend
from screenshots. Bucket `PY` is a stored role, not necessarily prior-year
revenue.

## Constraints

- Capture the actual size field and scale, reference lines and labels before
  encoding. A caption naming the size measure does not prove the binding, and
  labels may show another measure rather than size values.
- Resolve units, denominator and weighting for each axis; subtitle units can
  conflict with headline cards and value magnitudes.
- Define score weighting, eligible population and grain. Group averages do not
  establish individual-level correlation or causation, and volume does not
  prove effectiveness or individual performance.
- Intelligence chart library only; never a Power BI native visual.
- Agree on quadrant favorability from each measure's direction: high MTBF with
  low MTTR is ordinarily favorable. Never label a quadrant as best without
  checking the business definition. Size scaling and thresholds remain uncaptured.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "SCATTER_PLOT" | "BUBBLE_PLOT" | "QUADRANT_PLOT"
         (matches the decoded template id)
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"bubbleChart" (all three); bubble also
              chartType:"bubbleChart"
Observed buckets: scatter and quadrant = axis, AC, PY; bubble adds PL; one
                  scatter and one bubble add stack (the scatter without PL)
Pointer: /properties/visualState/hiddenProperties_!!!_appearance; decoded path
         charts.bubbleScatter: colorBy:"category" | "auto";
         sizeRange{min: 19 | null, max: null}
Evidence: [saved] companion-library saved owners; not isolated or re-rendered.
```

- Network graphs and packed bubbles also use `bubbleChart`; preserve the
  template id and never take a graph or packed-bubble owner as a Cartesian
  donor [saved].
- Role names do not define x, y, size or color; never fabricate a size
  measure for a scatter that has none [open].
- The `stack` role's UI label and its effect on plotted entities, legend,
  color grouping and aggregation are unresolved [open].
- Category-color and automatic-color owners are saved alternatives, not a
  default [saved]. Null `sizeRange` limits are not zero, and their sizing
  effect is unresolved [open].
- Quadrant threshold controls, per-template coordinate/size mapping and
  missing or negative sizes are unresolved [open].
- Validate entity uniqueness, point counts, units, scales, size meaning,
  tooltips and overlap.

## Related features

- `CH-AX-01`
- `CH-LBL-01`
- `CH-ANLY-01`
