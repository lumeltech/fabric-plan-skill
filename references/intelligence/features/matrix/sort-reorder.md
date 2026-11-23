---
id: MX-SRT-01
name: Sort and reorder
area: matrix
category: Sort, filter, Top N
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/sorting-data
---

# Sort and reorder

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Basic and advanced sort, absolute sort, manual row/column reorder. Ascending
or descending (A→Z/Z→A) sorts work on numeric and non-numeric columns such as
text, date and dropdown, at each hierarchy level. Advanced sort orders by
several dimensions or several measures. Drag-and-drop reorder sets a custom
order for rows, columns and measures.

## When to use

- Ranked lists; natural order for time.
- Fixed business order for categories or measures that no sort key provides.
- Multi-key ordering by several dimensions (or several measures).

## UI path

Column header › Sort; gripper › Reorder.
Column gripper › Sort › Sort Asc/Desc; Remove Sort or the header sort icon
clears it. The toolbar Sort button opens advanced sort. Drag a row gripper up
or down; drag a column/measure gripper or reorder in the Manage columns list.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.sorting
UI-saved measure sort: {is_absolute_sort:false,
  sort_type:{ColWithMeasure:{id:"<column id>", sort_order:"DESC" | "ASC"}}}
The column id is not the manage_measures id: Net Sales (measure 2055735705734354016)
  sorted as column 9594185143568086416, which also keyed formatConfig.column.
Evidence: one user editor save on a rows-only variance Matrix, read back.
```

How the column id derives from the measure is not established. Reuse a saved
`sorting` group only on a Matrix with the same measure ids and no column
dimension, and check the order on screen; otherwise sort in the editor.

## Constraints

- Period columns may run newest to oldest. Use explicit period and
  statement-line order keys; never sort headings or subtotals by amount.
- Section labels sitting above unrelated lines indicate a binding or order
  problem; resolve it before reproducing the layout.
- A screenshot's row or column order does not establish a saved
  manual-reorder configuration.
- Advanced sort uses either row dimensions or measures, not both together.
- Rows can be reordered only within their hierarchy level; visual columns
  cannot be reordered, unlike visual measures.
- Sorting applies at each hierarchy level; children stay grouped under their
  parent.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- [open] A month-year field displayed shuffled on a grid; the recorded response
  was the model's chronological sort plus the visual's own sort settings. That
  grid was not a reporting Matrix, so check the rendered period order rather than
  relying on the model sort alone.

## Related features

- `MX-SRT-03`
