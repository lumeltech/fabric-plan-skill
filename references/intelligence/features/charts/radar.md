---
id: CH-LIB-17
name: Radar and polar charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Radar and polar charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Multivariate comparison across categories.

## When to use

- Profiles across 5–8 attributes.

## UI path

Visualizations pane › Charts 100+ › Radar/Polar. Capture the exact radar/polar
variant and its settings.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: multiple series profiles across category spokes, point/value labels.
Native family, radial domains, label controls and polar alternatives: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- Radar presentation is not a polar variant or saved enum. Define category
  order, shared units/radial scales and missing categories. Polygon area is
  not an additive total, and changing spoke order changes its shape.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "RADAR_CHART"
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"otherChart"
Pointer: /properties/pivotAssignments (axis + one or more AC; optional row trellis)
Pointer: /properties/visualState/hiddenProperties_!!!_radar (JSON string)
Decoded keys: chartType:"radar"; gridShape:"circular" | "linear";
              seriesType:"line" | "column" | "area"; fillOpacity:30;
              enableDots:true; dotSize:5; customMinMaxEnable:true with null
              bounds; axis-label and value-axis visibility; grid margin, color
              and width; line/border thickness; fonts; markers
Partial: {"chartType":"radar","gridShape":"circular","seriesType":"line","fillOpacity":30}
Evidence: [saved] every inspected saved radar owner; not isolated or re-rendered.
```

- No polar template appeared in any inspected owner, including one on a page
  that mentions polar charts; a page name does not establish a polar variant
  [saved].
- Polar naming, scale normalization, null-bound behavior and series switching
  are unresolved [open].
- Preserve measure-specific styling and small-multiple state when rebinding.

## Related features

- `CH-AX-01`
- `CH-LBL-01`
