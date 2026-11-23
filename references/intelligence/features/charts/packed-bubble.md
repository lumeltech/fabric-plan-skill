---
id: CH-LIB-15
name: Packed bubble charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Packed bubble charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Clustered circles sized by value: one bubble per category, sized by one
measure, without axes; Color by sets category, gradient or uniform colors.
With a fully expanded hierarchical Category, Packed circles settings add
cluster mode (children inside parents; off renders one packed chart per
level), cluster headers (position, curve, case, weight, auto color), totals
and parent/child or node opacity (1–100).

## When to use

- Overview of many members.
- Space-efficient comparison of magnitudes or proportions where precise
  reading is not required.
- Parent–child composition shown as clustered bubbles.

## UI path

Visualizations pane › Charts 100+ › Hierarchy › Packed bubble. Put the
dimension in Category and add one measure.
Settings › Canvas › Color by sets the color scheme; the Packed circles tab
appears after the hierarchy is fully drilled down with the drill buttons.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- In nested packed bubbles (parent containing child), small labels truncate.
  Provide tooltips or a table alternative; area does not support precise
  comparison.
- Capture hierarchy bindings and a drilled state before promising navigation;
  a drill instruction in a subtitle does not establish working behavior.
- Packed circles (cluster) settings are enabled only when the Category
  hierarchy is fully expanded.
- There are no axes; show values with data labels or Enable total (cluster
  totals).

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "PACKED_BUBBLE"
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"bubbleChart"
Pointer: /properties/pivotAssignments (several hierarchy levels in axis; value in AC)
Pointer: /properties/visualState/hiddenProperties_!!!_appearance; decoded path
         charts.packedBubble: cluster headers; clusterMode:false;
         colorBy:"individual"; opacityType:"childToParent"; nodeOpacity:80;
         null size bounds
Evidence: [saved] one saved packed-bubble owner; not isolated or re-rendered.
```

- Saved `axis` level order varied across hierarchy owners; validate the
  model's hierarchy rather than reordering levels by label meaning [saved].
- `PACKED_BUBBLE` is a distinct template from Cartesian `BUBBLE_PLOT` despite
  the shared renderer; never transfer bubble, treemap or sunburst groups
  [saved].
- How these keys map to the documented cluster mode, Color by and opacity
  controls, and the drill/expand behavior, parent/leaf aggregation and
  node-size meaning, are unresolved [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
