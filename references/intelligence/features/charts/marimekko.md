---
id: CH-LIB-09
name: Marimekko charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Marimekko charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Two-dimensional share by variable-width columns.

## When to use

- Market share by segment and region.

## UI path

Visualizations pane › Charts 100+ › Marimekko, then pick the variant.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: bands of different heights, segments across a percentage axis and
         two values in some labels.
Native family, orientation, weighting and measure bindings: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- Mosaic presentation is not a confirmed Marimekko enum. Isolate orientation,
  band-size and within-band share roles. Do not mix measures with different
  units or infer which measure controls area from labels alone.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Template id (owner chartType where recorded) -> decoded template rendererType:
  MARIMEKKO_HORIZONTAL                      otherChart
  STACKED_MARIMEKKO_HORIZONTAL              stackedChart
  PERCENTAGE_MARIMEKKO_VERTICAL             otherChart
  PERCENTAGE_STACKED_MARIMEKKO_HORIZONTAL   stackedChart
  PERCENTAGE_STACKED_MARIMEKKO_VERTICAL     stackedChart
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys (percentage-stacked vertical): chartOrientation:"vertical";
              actualChartType:"column"
Pointer: /properties/pivotAssignments (axis, AC, PY; stacked variants add stack;
         saved order axis, AC, PY, stack; sourceType "PowerBI")
Pointer: /properties/visualState/hiddenProperties_!!!_appearance; decoded path
         charts.marimekko (non-stacked owner): showBorder:true;
         borderColor:"#ffffff"; borderSize:1
Pointer: /properties/visualState/hiddenProperties_!!!_marimekkoScaleAxis
         (decoded; preserve the exported form): enabled:true; type:"limits";
         syncWithXAxis:false; widthValue:"actual" | "percentage";
         decimalPlaces:1 | 0
Evidence: [saved] one owner each for the first four variants and two
          percentage-stacked vertical owners; saved alternatives, not a
          default copy or isolated change.
```

- Preserve template id and orientation together; reproduce a variant from its
  complete owner, never from these fragments.
- AC, PY and `stack` are native slots; which measure sets band width or
  segment height in each variant is unverified [open].
- In one saved owner `PY` held a distinct-count metric, not a prior-year value
  [saved]. Name metrics truthfully; never swap a count for a currency measure
  while keeping its label, and recheck units, sizes and labels after rebinding.
- `charts.marimekko` borders are chart-internal segment styling, not the outer
  visual frame [saved].
- The `widthValue` and `decimalPlaces` alternatives are saved values, not
  defaults; their UI control, the width/height formulas, normalization
  denominator and zero or negative category handling are unresolved [open].
- Check meaningful part-to-whole use, nonnegative sizes, total shares, category
  widths and stacked legend consistency; percentage axis labels are not
  verified normalization.

## Related features

- `CH-AX-01`
- `CH-LBL-01`
