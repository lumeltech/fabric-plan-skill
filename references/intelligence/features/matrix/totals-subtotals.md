---
id: MX-TOT-01
name: Totals and subtotals
area: matrix
category: Totals and aggregation
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-financial-reports
---

# Totals and subtotals

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Shows, positions, and labels grand totals and subtotals; freezes totals.

## When to use

- Additive measures; statements with subtotal lines.

## UI path

Home › Totals.

The financial-report guide documents Matrix ribbon > Aggregation > Row Grand
Total > Off for hiding the generic grand total; it does not define statement formulas.

## Definition encoding

```text
Registration: INFORIVER; /properties/visualType = 10 (Matrix)
Pointer: /properties/visualState/totalDisplayConfig (object)
Default keys: grandTotalHeight, subTotalHeight, totalsDisplay, totalCustomTitle
  (grandTotalTitle:"All", columnGrandTotalTitle:"Grand Total",
   totalColumnSuffix:"Total", splitTotalRowSuffix:"Total")
Additional pointer: /properties/visualState/totals_config (object)
Native reporting-Matrix capture after Row Grand Total > Off:
  column_grand_total: null
  column_sub_total: null
  freeze_total: false
  row_grand_total: null
  row_sub_total: "Top"
Evidence: default reporting-Matrix export plus a later native reporting-Matrix
          total-Off capture; other total controls were not isolated.
Row grand-total label: totalCustomTitle.grandTotalTitle ("All" by default);
  setting "Total" rendered "Total" on the grand-total row.
```

Earlier evidence for `totals_config` came only from a Planning grid; the
new reporting-Matrix capture establishes that this group also exists here.
Copy the matching complete reporting state; do not transplant Planning
layouts or infer other switches from this one capture.
A visible All row does not establish aggregation semantics for ratios.

User-finalized full-detail matrices kept the grand total at the top and
frozen (`row_grand_total: "Top"`, `freeze_total: true`, sub-totals and
column totals `null`) [saved]. Their totals used
`aggregation_config.measure_aggregation.<measureId>.row: "Sum"` for additive
measures and `null` for ratio measures such as margin % [saved].

## Constraints

- Never sum parent and leaf rows, gross and net lines, or per-share values
  together. Reconcile statement totals to their components; hiding All or
  styling borders does not repair arithmetic. Validate every statement
  section before claiming balanced statements.
- If a headline total differs from the Matrix All row by a simple multiple,
  check scope and parent/leaf double counting before trusting either total;
  rounded similarity is not proof of a root cause.
- Recompute ratios, ratings, percentages and distinct counts at their defined
  grain from underlying totals; never sum or naively average displayed
  values. When zero totals sit beside a high completion ratio, resolve scope,
  parent/leaf allocation and ratio measures before display.
- Determine filtered versus all-member totals and Table versus Matrix
  ownership; reconcile All to cards under identical scope. Do not judge
  completeness from a scrolled viewport.
- Define categorical totals such as status or assignee explicitly rather than
  showing an arbitrary first member.
- Gantt aggregate settings require their own capture, not Matrix
  totalDisplayConfig. Do not sum child progress percentages, confuse summed
  duration with phase span or add parent budgets to leaf amounts.
- Grand total on does not change measure aggregation.
- Newer-format Matrix owners (for example native-insights) carry
  `visualState.totalRowsDisplay: "underlyingData"`. Removing it hid the
  grand-total row while `totals_config.row_grand_total` stayed `"Bottom"`;
  restoring it brought the row back [confirmed]. Keep it when cloning.
- UI save [saved]: `totals_config.column_grand_total: "Right"` added a Total
  column; `columnTitleConfigs {id:"16017913890930171270", levelId:"", value:"Total"}`
  renamed the grand total ("All" by default); `formatConfig.row["16017913890930171270"]`
  styled the grand-total row (bold, top border). The same id appeared in two
  Matrices, so it looks like a fixed grand-total key.

## Related features

- `MX-AGG-01`
