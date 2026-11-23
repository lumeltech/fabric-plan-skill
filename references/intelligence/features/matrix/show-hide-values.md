---
id: MX-SHOW-01
name: Show or hide values, rows, and columns
area: matrix
category: Layout and hierarchies
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
---

# Show or hide values, rows, and columns

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Hides cells, rows, columns, measures, headers, or measures for selected periods.
Manage columns hides a measure under every column category; saved measure time
ranges (date picker, relative last-n periods or date functions) show or hide
measures per period and switch instantly. Skip row removes a row from totals
and exports; Skip and show row excludes it from totals but keeps it visible.

## When to use

- Hide helper measures used only by formulas.
- Hide future months for actuals.
- Exclude a row from totals, hidden (skip) or still shown (skip and show).

## UI path

Column/row gripper › Hide. Matrix toolbar: Show/hide drop-down (cells, rows,
columns; Rows › Unhide), Manage columns (measures), Show/hide Measures (time
ranges). Row gripper › Hide row, Show All Rows, Skip row, Skip and show row;
Column gripper › Hide Column, Show All Columns.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.manage_measures / measureAttributes (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Hidden rows still count in totals and subtotals; Skip row excludes a row
  from totals and exports, Skip and show row from totals only.
- Hiding a column hides that instance only; unchecking a measure in Manage
  columns hides it under every column category.
- Hidden cells grey out the Style and Alignment formatting options.
- Restore hidden or skipped rows from Show/hide › Rows, or use Show All Rows /
  Show All Columns on the grippers.
- A measure time range needs a name, measures and an interval; turn its Show
  toggle off to hide those measures for the range instead.

## Related features

- `MX-CALC-02`
