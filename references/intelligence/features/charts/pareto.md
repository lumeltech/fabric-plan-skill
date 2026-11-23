---
id: CH-ANLY-02
name: Pareto counts and cumulative percentage
area: charts
category: Chart analytics
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Pareto counts and cumulative percentage

## What it does

Combines descending category magnitudes with a cumulative share line to show
where the selected population is concentrated.

## When to use

- Rank recorded incident causes or other nonnegative category contributions.
- Identify high-contribution categories without asserting causation.

## UI path

Visualizations pane › Charts 100+; search pareto in Search Charts or start from
a Combo variant. The exact Pareto template or combination settings are not
captured. Do not invent a chart-family enum.

## Definition encoding

```text
Presentation evidence: screenshots only.
Visible: descending horizontal category counts plus a cumulative percentage line.
Native family, buckets, cumulative calculation and axis settings: not captured.
```

Follow [native sample capture](../../core/native-samples.md). Screenshots do
not establish whether the cumulative series is computed by the visual or
supplied by a measure.

## Calculation and validation

- Bind category and nonnegative magnitude at a consistent filter scope.
  Sort descending, with deterministic tie ordering.
- Define cumulative share as running category magnitude divided by the total
  of the agreed population. Aggregate before rounding and format as percent.
- Define Top N/Other behavior. If the denominator includes hidden categories,
  the last visible point need not be 100%; label that scope explicitly.
- Exclude double counting or explicitly disclose overlapping categories.
  For incidents, resolve whether counts are distinct IDs or event records.
- Test empty/all-zero populations without dividing by zero, and test filter
  changes, ties, omitted categories and the final cumulative value.
- Do not add an 80% reference line automatically; add it only when requested
  or part of the approved design.

## Constraints

- On mirrored layouts, compute each side's cumulative share from its own total
  in the shared displayed row order. Never reorder one side independently and
  misalign categories; if a side is not strictly descending, present it as a
  cumulative share, not a strict Pareto.
- Native visual configuration remains unverified.
- A smooth/connected line does not establish a causal or predictive model.
- Preserve separate count and percentage scales with readable labels.

## Related features

- `CH-SORT-01`
- `CH-LIB-05`
- `CH-MULTI-01`
- `CH-LBL-01`
