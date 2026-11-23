---
id: MX-AGG-01
name: Row and column aggregation
area: matrix
category: Totals and aggregation
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
---

# Row and column aggregation

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Sets how each measure aggregates at parent rows and total columns (sum, average, min, max, first, last …).

## When to use

- Ratios, balances (last value), averages.

## UI path

Column gripper › Aggregation.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.aggregation_config (measure_aggregation, row_measure_aggregation, row_dimension_aggregation)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Never sum ratio measures.

## Related features

- `MX-TOT-01`
