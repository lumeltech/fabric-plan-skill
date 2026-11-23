---
id: CH-HIER-01
name: Hierarchies and drill in charts
area: charts
category: Chart data
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Hierarchies and drill in charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Drill down/up and expand on hierarchical axes, including unbalanced and single-child hierarchies.

## When to use

- Region › Country drill.

## UI path

Chart › Hierarchy.

## Definition encoding

```text
Presentation evidence: screenshots only.
Exact hierarchy/drill switch: not isolated in the approved evidence.
```

A visible multi-level axis (such as Year/Quarter) is not proof of working
drill down/up. Bind both registry fields in a captured same-kind Fabric Plan
chart; do not invent hierarchy properties. See `core/native-samples.md` for
capture.

## Constraints

- Use full-path member IDs so repeated labels under different parents stay
  distinct; retain single-child branches.
- Never add parent values again to their children or double count levels;
  capture how parent values aggregate.
- Expand/collapse or hierarchy-arrow icons do not verify drill, expand or
  parent/root total changes; capture and test each action independently.
- Capture expansion state separately from selection/filter interactions.
- Specify whether share labels divide by the overall or the parent total, and
  include off-screen (scrolled) members in reconciliation.
- Capture actual/plan roles at each level; plans may have coarser grain than
  actuals.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/pivotAssignments: child level added after the parent in "axis"
Pointer: /properties/drilldown/drillFields/axis: dataRole "axis", drillType
  "DOWN", child level queryName
Evidence: [saved] a user-corrected drill source whose owner changed from a
  Matrix (10) to a chart (50); not isolated one change at a time.
```

- Saved drill-down state is neither a destination drill-through registration
  nor proof of navigation; destinations belong to `CV-INT-03` [confirmed].
- Gate drill tests on the source field wells, the requested child level and
  the native drill state; a negative check must fail when the child level is
  missing [confirmed].
- Several saved owners bind two or three ordered `axis` assignments (bullet,
  line, integrated area); that is saved hierarchy cardinality, not verified
  drill behavior [saved].
- Saved owners also carry `hiddenProperties_!!!_categoryExpandCollapseMapping`,
  `hiddenProperties_!!!_categoryStateMeta` and
  `hiddenProperties_!!!_categoryIndexMap` [saved]. Their role in expansion
  state is unresolved [open].
- Test each drill level plus back, reset and reopen in the rendered chart.

## Related features

- None.
