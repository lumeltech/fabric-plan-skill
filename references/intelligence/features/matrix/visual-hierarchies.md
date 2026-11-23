---
id: MX-HIER-02
name: Visual hierarchies (custom grouping)
area: matrix
category: Layout and hierarchies
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
---

# Visual hierarchies (custom grouping)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Groups selected rows or columns into custom visual-level groups without
changing the model. Row groups indent their members as a child level, add an
automatically aggregated subtotal at the chosen total position and expand or
collapse. Column groups add a header label over the selected measure columns
that can be styled and aligned. Rows can also be auto-grouped by the classes
of a measure's Classification conditional-format rule.

## When to use

- Ad-hoc groupings like 'Core markets' vs 'Other'.
- Group related measure columns under one shared, collapsible header.
- Band rows by the classes of a Classification conditional-format rule.

## UI path

Matrix toolbar: Insert › Group (enabled once rows or columns are selected) ›
enter the label (rows: also the total position) › Apply. Auto-group rows:
Insert › Group dropdown › choose the classified measure; None removes it.
Remove a manual group: select it (columns: its group label) › Remove group.
Collapsible column groups: Display settings › Column Group Expand/Collapse Icon.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- The Group command stays disabled until a row or column is selected.
- Row-group subtotals are calculated automatically from the grouped members;
  choose where the total appears when creating the group.
- Column groups collapse only after Column Group Expand/Collapse Icon is on in
  Display settings; a collapsed group hides its grouped measures' values.
- With column dimensions assigned, check Group Across Columns to repeat the
  group under every column category instead of only the selected columns.
- Auto-grouping needs an existing Classification rule on the chosen measure
  and groups rows by its classes; remove it with Group › None (manual groups
  use Remove group).
- Groups exist only in the visual; model hierarchies and data are unchanged.
- Row-gripper inserts that add data-input, static or bulk-inserted rows carry
  manually entered values; that is input authoring, not enabled in this
  release. Group existing members instead.

## Related features

- `MX-HIER-01`
