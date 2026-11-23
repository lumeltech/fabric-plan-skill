---
id: MX-HIER-01
name: Expand, collapse, and hierarchy levels
area: matrix
category: Layout and hierarchies
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
---

# Expand, collapse, and hierarchy levels

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Expands or collapses rows and columns to a level, hides child rows, and controls hierarchy icons, indent, ragged hierarchies, and single-child display.

## When to use

- Default the Matrix to a readable level (e.g. Region only).
- Ragged or unbalanced hierarchies.

## UI path

Row/column context menu › Expand/Collapse; Display settings › Hierarchy settings.

## Definition encoding

```text
Pointer: /properties/visualState/rowDimensions
Column rows: externalKey "<Table>[<Column>]" with id, isNative, label
Hierarchy rows: externalKey "[<Table>[<Hierarchy>]]~||~<Table>[<Level column>]",
                one entry per level in order
Pointer: /properties/visualState/columnDimensions = [] (no column fields)
Pointer: /properties/visualState/row_expand_state_config (group present)
Expand/collapse, ragged and single-child switches: not isolated.
Evidence: live export of a UI-created test Plan (default state); not isolated by
          a before/after change or re-rendered after reapplication.
Hierarchy styling (saved): every saved multi-level Matrix had
  globalStyles.hierarchyfontWeight "bold", gridStyles.indentSpacing 10 or 16
  and gridStyles.isLevelIndent false; single-level owners may carry "semiBold".
Row toggles: tableState.expandCollapseIcon "none" hides the row icons (default in
  the saved donors; columnExpandCollapseIcon "arrows"). A user editor save set
  "plusMinusSquare" on a Matrix with three row fields and left a one-field
  Matrix at "none" [confirmed]; rows still open expanded
  (row_expand_state_config {"Grid": "Expanded"}). A collapsed default is not
  captured.
```

Copy matching Fabric Plan Matrix bindings and state, remapping every external
key/ID to registry-consistent fields. Do not borrow Planning-grid expansion
keys. Screenshots show hierarchy levels but do not encode initial expansion.

## Constraints

- Show the row icons (`expandCollapseIcon: "plusMinusSquare"`) whenever rows
  hold two or more fields, so readers recognize an expandable hierarchy;
  leave single-level rows at `"none"` [confirmed]. Mention the icons in the
  report's Help text.
- Indented labels without expansion controls may be formatting rather than a
  model/visual hierarchy. Capture parent IDs, row roles and expansion
  behavior; do not build a hierarchy from misplaced section labels.
- Gantt task grids are not established as reporting Matrices. Route Task data
  wells and expand controls to [Gantt](../charts/gantt.md); do not reuse
  Matrix rowDimensions/expansion settings because a grid looks similar.
- Visible expand/collapse controls do not establish saved initial expansion
  or cross-filter actions. Capture initial expansion, scroll behavior and
  stable parent/child bindings.
- For deep hierarchies, confirm dimension keys and target grain before
  populating lower levels; never repeat a parent target on every leaf.

## Related features

- `MX-LAY-01`
- `MX-HIER-02`
