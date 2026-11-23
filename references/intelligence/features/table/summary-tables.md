---
id: TB-SUM-01
name: Summary tables
area: table
category: Table
status: IS-Confirmed
encoding: unverified
visual: Table
sources:
---

# Summary tables

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Summarised table views of chart data. A toggle switches a chart or card to a
summary table of its values and back. In the table, authors can drag rows to
reorder categories, rename categories, add calculated rows (arithmetic over
row categories), skip or skip-and-hide rows from calculations, suppress nulls,
change a date category's format and invert a row's sign; the visual updates
immediately.

## When to use

- Data table under a chart.
- Checking the values behind a chart or card without leaving the sheet.
- Visual-level reordering, renaming or calculated categories that must not
  change the semantic model.

## UI path

Chart › Summary table. Select the summary-table icon at the top of the chart
or card; select it again or close the table to return. Use the row gripper to
insert a calculated row or apply Skip row, Skip and Hide, Reset skip & hide
rows, Enable suppress null or Invert row; double-click a category to rename it
or to change a date format.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Changes stay inside the visual; the semantic model is not modified. This is
  not writeback or a planning input.
- Skip row keeps a category visible but excludes it from calculations such as
  averages; Skip and Hide also hides it in the visual and the table.
- Suppress null removes null categories from both the table and the visual;
  fuller null handling sits in the Number display settings.
- A chart's default axis date format follows the summary table's date format.
- Readers can open the summary table, reorder categories or rename headers
  only when the author allows those reader controls.
- Calculated rows are visual-level categories, not model members; label them
  so readers do not mistake them for model values.

## Related features

- `TB-TABLE-01`
