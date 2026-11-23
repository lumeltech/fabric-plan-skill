---
id: CH-LIB-18
name: Decomposition tree
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Decomposition tree

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Breaks a measure into dimensional contributions; a decomposition alone does
not establish causal relationships.

## When to use

- 'Why' analysis by drilling dimensions.

## UI path

Visualizations pane › Tree. The decomposition tree is its own top-level
visual, not a Charts 100+ chart type.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: root measure, dimension branches, node values/counts, mini bars,
         expand controls and dimension summary boxes.
Exact family enum, bindings, selected path and node settings: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- A contribution tree is not proof of AI splits or causal analysis. Capture
  dimension order, analysis measure, signed scales, node counts and path state.
- Reconcile additive parent/child values and define ranking by signed amount,
  absolute magnitude or percent. A listed dimension level is not proof it was
  expanded; a caption does not verify interaction behavior.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Saved Analytics owners of other families, including cards, carry a
  `hiddenProperties_!!!_decompositionTree` JSON string among many dormant
  family groups; its presence does not identify a decomposition tree [saved].
- The companion library recorded no decomposition-tree template id, renderer
  or bindings; the capture gate above stands [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
