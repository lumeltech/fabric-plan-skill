<!-- Core reference for the `fabric-plan-skill` skill. Used by discovery (metric decisions in the report spec) and by validation of business-critical values. Merged from a companion Intelligence authoring library. -->

# Metric contract, period semantics and acceptance cases

Merged from the companion Intelligence authoring library. Additive only:
mode guides, the other core references and the permission-gated
model-measures process take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

## Contents

- [Period semantics before period labels](#period-semantics-before-period-labels)
- [Metric contract](#metric-contract)
- [Acceptance cases](#acceptance-cases)
- [Reconciliation record](#reconciliation-record)
- [Additional details](#additional-details)

## Period semantics before period labels

A user correction in the companion work rejected MTD/YTD labels on measures
that were not real period calculations [confirmed]. Keep one consistent metric
or statement-line definition and vary only the intended date and scenario
context. Existing filtered totals can be valid, but their equivalence must be
shown; names, bucket role letters and plausible totals are not proof.

For each MTD, YTD or full-year calculation record the calendar (fiscal or
calendar), as-of rule, selected-year and selected-month behavior, start/end
inclusivity, source grain, actual coverage, comparison (plan or budget) dates
and the composition of any forecast or latest estimate.

- On monthly facts an MTD value is the available month total, not a
  through-today, day-level calculation; say so in the spec.
- Fiscal YTD needs an explicit fiscal calendar.
- Test a non-year-end month, a historical year, a year without actuals or a
  future year, and the relevant organization filters.
- Validate the arithmetic independently: MTD matches its one-month ledger; YTD
  matches the period start through the cutoff; full year covers the complete
  selected year; actual and comparison use identical date boundaries; a latest
  estimate does not double-count overlapping actual and forecast periods.
- Prefer suitable existing model calculations, then the reporting time
  functions in Matrix formula syntax
  and quick formulas. Any remaining gap follows `model-measures` unchanged.
- The companion library also proposes new calculation items or groups as a
  period remedy. This skill never creates calculation groups or items; its
  measures-only, permission-gated process wins [open].

## Metric contract

Record these items per business-critical metric in the report spec (Measures
or Implementation notes). This is a reporting contract, not a Plan JSON
schema. Keep verified facts, owner decisions and unknowns separate; a familiar
metric name is not a definition. Reuse one documented contract instead of
copying it per visual.

| Item | Record |
|---|---|
| Identity and meaning | Exact model or visual-measure ID, expression or lineage, business question, responsible owner |
| Population and grain | Included and excluded records, eligibility, dimensional grain, distinct-count identity, supported slicing paths |
| Calculation | Numerator and denominator or base aggregation, sign convention, unit, currency/FX basis, scale and rounding |
| Time and comparison | Date role, fiscal or calendar basis, as-of or closed-period cutoff, actual/reference scenarios and matched coverage |
| Roll-up | Additive dimensions, weighted-ratio behavior, distinct-count totals, period-end treatment, subtotal rules |
| Exceptional inputs | Blank versus zero, zero or negative denominator, missing baseline, negative values, sparse or new members |
| Freshness | Data snapshot or refresh time |
| Acceptance | Expected result and its independent basis, explicit context, tolerance with units, evidence status |

Do not impose one variance-percent convention when the reference is zero or
negative; ask the metric owner for the formula, display and favorable
direction. Do not assume averages are unweighted, or that a headcount measure
is a period-end snapshot, without reading its definition.

## Acceptance cases

Use the smallest relevant set:

| Case | What to establish |
|---|---|
| One known leaf or member | Query and rendered value agree with an independently supplied or reconciled expected result |
| Subtotal and total | Recomputed from the approved definition; percentages, averages and distinct counts are never summed |
| Partial versus full period | Actual and reference coverage are aligned, or labeled as intentionally different |
| Blank, zero and negative baseline | Agreed calculation and display; no fabricated zero, infinity or favorable color |
| Filter change and reset | Intended population changes, comparisons keep their baseline, default context reopens correctly |
| Time boundary | Prior year, fiscal boundary and latest closed period use the intended dates |

Cases for connected outputs from other modules are out of scope in this
release; see module boundaries.

## Reconciliation record

Keep one row per case with the validation evidence (for example beside
`_build/feature-log.md`):

| Metric/source ID | Case and actual filter context | Snapshot/as-of | Expected raw result and independent basis | Queried result | Rendered value/format | Tolerance and units | Status and evidence |
|---|---|---|---|---|---|---|---|

- Set tolerances before judging. Never widen one after a failure merely to
  pass; when absolute and relative tolerances both apply, record the rule,
  including behavior near zero.
- Reconcile raw numbers separately from scaled or rounded labels.
- Test under the real report, page, visual, identity and calculation-group
  context. An unfiltered DAX result is diagnostic, not equivalent to a card
  under page filters. Use the same data snapshot, or identify refresh drift,
  before blaming the visual.
- Use the statuses in validation layers
  with a reason. The independent basis must come from outside the measure under
  test; querying the same expression twice is only a consistency check.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Scenario scope

- Before binding a measure to an actual or reference role, read its
  expression for an explicit scenario filter. In the companion reconciliation
  against user-supplied reference values, measures without one were the main
  risk: they combine scenarios unless the visual, page or slicer context
  selects one [confirmed].
- A query-scoped measure definition used to simulate a case, such as a stale
  forecast, tests a hypothetical. Label the result as a temporary simulation
  and never report it as persisted model data or behavior.

### Companion measure layer

The companion library added a dashboard layer of explicit scenario, period
and variance model measures for each statement line in one batch, preferring
them to calculation groups. Here, variances and period logic are built in
Fabric Plan where possible, calculation groups are never created, and each
remaining model measure needs its own approval under
model-measures; that process wins [open].
