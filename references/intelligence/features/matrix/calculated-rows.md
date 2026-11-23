---
id: MX-CALC-01
name: Calculated rows
area: matrix
category: Calculations
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/planning-sheets/reference/formula-syntax
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-financial-reports
---

# Calculated rows

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Inserts rows computed by formula (e.g. Gross Margin = Revenue − COGS), with
aggregated rows and formula debugging. The editor lists 50+ functions with
syntax and examples, autocompletes and flags errors with line numbers. Parent
rows can be formula rows; Insert Sum of rows / Insert Avg of rows aggregate a
selection. Row options: Include in total, Include in charts, Evaluate column
before rows, custom scaling and Bind for cross filter/RLS.

## When to use

- Statements whose lines are not in the model.
- Margins, ratios or variances between existing rows, kept in row context.
- Sum or average of selected sibling rows without a new model measure.

## UI path

Select the anchor row > Data ribbon > Insert Row > Insert Formula.
Use Ctrl+Space for suggestions and the References tab for supported operands.
Name the row, pick functions from the Functions tab and click a row (or type a
child as Parent.Child) to add operands. For aggregates, select the rows first
to enable Insert Sum of rows / Insert Avg of rows in the same menu. Select a
cell to see its formula in the formula bar; edit, hide or delete via Manage Rows.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/insertRows.json (separate part)
rows[]: id, name, visualId, rowMeta
rowMeta: id, title, description, previous_row_id, include_in_total,
         bind_for_cross_filter, cross_filter_config, row_type.CalculatedRow
row_type.CalculatedRow: formula, description, bind_for_cross_filter,
                       deferred: "DIColumns", include_in_chart
Formula operands: R_<native row ID>, not display labels.
Observed cross_filter_config:
  selection_type: "row"; row_id: <chosen source row ID>;
  dimension_id: null; dimension_type: null.
Evidence: native saved reporting-Matrix gross/net profit row captures.
```

Copy a complete same-kind native row and its schema, preserving required
metadata and resolving operands in the target Matrix. Do not put inserted
rows into invented `visualState` keys or reuse another report's operand IDs.
Save and wait for state propagation before capture; reconcile the UI's row
count with `insertRows.json` rather than trusting an immediate readback.

## Constraints

- Statement rows need signed arithmetic for deductions such as tax and
  minority interest, gross-to-net asset lines and cash reconciliation.
  Displayed totals may be existing model measures, not inserted formulas.
  Resolve line IDs and operand scope; never create a balancing plug, blanket
  ABS calculation or summed per-share values (EPS) to reproduce totals.
- Read [Matrix formula syntax](formula-syntax.md); choose row-context
  identifiers and test parent/grand totals.
- Use editor-provided references in the UI and captured IDs/tokens in the
  definition. Do not invent serialized formulas from display labels.
- Include in total adds the row to its parent and grand totals; keep it off
  for calculated subtotal/profit lines, ratios, memo or check rows to avoid
  double counting. Include in charts is available only when
  Include in total is off.
- For ratio, % or variance rows enable Evaluate column before rows, so totals
  apply the formula to total values instead of summing child-column results.
- A formula row may not fit the report-level number scaling; set custom
  scaling on that row instead of rescaling the report.
- Without Bind for cross filter/RLS, rows that reference other rows ignore
  cross-filtering and row-level security; bind them to a reference row or
  dimension member so restricted users see only permitted values.
- The binding checkbox alone is insufficient: use Choose Row and select the
  intended native reference row. Capture its cross-filter metadata and test
  changed filters and a restricted identity; stored flags do not prove RLS.

## Related features

- `MX-FML-01`
- `MX-CALC-02`
- `MX-TPL-02`
