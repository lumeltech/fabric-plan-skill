---
id: CH-LIB-14
name: Sunburst charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Sunburst charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Hierarchical composition in concentric rings. Parent wedges contain child
wedges; repeated labels retain their parent path, and the center can show
the root total. Screenshot evidence covers two and three data-ring levels.

## When to use

- Two- to three-level composition.

## UI path

Visualizations pane › Charts 100+ › Hierarchy, then pick the sunburst chart.
The exact data wells and settings paths were not captured; do not inherit
legacy UI.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: two- and three-level hierarchies with center totals, nested wedges,
         parent-tinted colors and internal labels.
Native chart identifier, field mapping, ring/center settings and drill: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- Visual geometry establishes hierarchy presentation, not unobserved settings.
  A title naming another chart type does not change that; native family
  identity still requires capture.
- Bind a disjoint additive weight at a defined grain. Reconcile parent/child
  totals with raw values, allowing only display-rounding gaps; do not add all
  rings together or force a balancing leaf.
- Define parent versus root shares, full-path node identity and repeated
  member handling. Distinct counts across overlapping branches may not add.
  A full-span single child repeats its parent's quantity, not extra volume.
- Capture inner radius, ring widths, center total, label orientation and
  inherited colors from the same chart family; never reuse `DONUT_CHART`
  or guessed sunburst keys. Toolbar icons do not verify drill/expand behavior.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "SUNBURST_CHART"
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"pieChart"
Pointer: /properties/pivotAssignments (several hierarchy levels in axis; value in AC)
Evidence: [saved] one saved sunburst owner; ring and label keys not recorded.
```

- The sunburst shares the `pieChart` renderer with pies and donuts but is a
  separate hierarchy template; donut settings do not transfer [saved].
- Copy the full sunburst owner; its ring, center and label keys were not
  documented, and treemap or packed-bubble groups must not be transferred
  [open].
- Saved `axis` level order varied across hierarchy owners; validate the
  target hierarchy instead of reordering levels by label meaning [saved].
- Drill/expand behavior and parent/leaf aggregation are unresolved [open].

## Related features

- `CH-HIER-01`
- `CH-MEAS-01`
- `CH-LBL-01`
