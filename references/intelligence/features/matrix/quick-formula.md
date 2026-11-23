---
id: MX-QF-01
name: Quick formulas
area: matrix
category: Calculations
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/planning-sheets/reference/formula-syntax
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-a-dashboard
---

# Quick formulas

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

One-click running total, % growth, % of parent or total, lead/lag, ranking,
variance, smart analysis. Each preset inserts a visual measure or column from
a base measure: running total (optionally continuous across leaf rows),
% running total, % contribution with an optional progress bar, lead/lag by
n periods, overall or in-group ranking, variance between any two measures and
empty spacer columns/measures. % Contribution row adds the row equivalent.

## When to use

- Fast derived columns without writing formulas.
- Period-over-period growth or lead/lag comparisons along a time series.
- Rankings and shares of parent or grand total in hierarchical tables.

## UI path

Insert › Quick formula.
Choose the preset, Insert as (visual measure or column) and the base measure.
Smart analysis needs a selected cell and adds % contribution or % variance
against it; % Contribution row sits under Insert Row and needs a selected row.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Consult [Matrix formula syntax](formula-syntax.md) when a quick formula
  needs a custom expression. A function catalog does not verify a quick-formula
  preset or its encoding; capture the actual preset separately.
- Overall ranking leaves subtotals unranked; ranking within a group also
  ranks subtotals.
- The default variance uses the first measures in the AC/PY/PL/FC wells; use
  Insert variance for any other pair of measures or formula fields.
- Continuous Total runs the total across all leaf rows regardless of their
  group; % running total is shown as a share of the matching total/subtotal.
- Smart analysis inserts a measure or a column depending on whether the
  column field has categories.
- Empty columns and measures are spacers and accept no values. Quick-formula
  measures can be referenced in custom formulas.

## Related features

- `MX-FML-01`
- `MX-CALC-02`
- `MX-VAR-01`
