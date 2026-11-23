---
id: CH-LIB-13
name: Treemap charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Treemap charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Nested rectangles sized by value, showing proportions within a hierarchy; no
explicit measure configuration is required. Several Category dimensions form a
drillable hierarchy; Expand all level drills every category at once instead of
only the clicked one. With multiple measures, Measure grouping separates each
measure into its own group with header options. Tile layouts and inner/outer
padding are configurable.

## When to use

- Hierarchical share.
- Part-to-whole comparisons across many categories, drilling from parent to
  child.
- Composition of several measures side by side with Measure grouping.

## UI path

Visualizations pane › Charts 100+ › Hierarchy › Treemap. Put one or more
dimensions in Category and add the measures. Settings › Canvas: Tile, Expand
all level, Measure grouping (header)
and inner padding (between measures) or outer padding (between groups).

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- Expand all level applies only with more than one Category dimension.
- Header customization appears only when Measure grouping is on.
- Capture hierarchy bindings and the drilled state before promising drill
  navigation.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "TREE_MAP" (matches the decoded template id)
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"otherChart"
Observed bucket sets: several axis levels + AC; two axis levels + AC;
                      one each of axis, AC, PY and stack
Pointer: /properties/visualState/hiddenProperties_!!!_treeMap (JSON string)
Decoded keys: tileType:"binary" | "squarify"; leavesOnly:false; innerPadding:3;
              outerPadding:0 | 2; enableParentLabel:true; expand-all,
              category-filter and header flags; parent-label styling; total
              value; opacity
Partial: {"tileType":"squarify","outerPadding":0,"innerPadding":3,"leavesOnly":false,"enableParentLabel":true}
Evidence: [saved] companion-library saved owners; not isolated or re-rendered.
```

- A `stack` binding is not automatically a second hierarchy level, and `PY` is
  not automatically a size or comparison encoding [open].
- Keep `innerPadding` and `outerPadding` separate from dashboard gutters, and
  preserve the remaining label, opacity, category and expansion state.
- How `tileType` maps to the documented Tile control, the effective hierarchy,
  comparison/stack encoding and parent-label rendering are unresolved [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
