# Archetype: Comparative Benchmark

<!-- Design topic for the `fabric-plan-skill` skill. -->

**Reader:** managers, finance. **Question:** "How do we compare — to plan, to last year, to peers?"

## Composition

Optional example, not a required layout for financial or comparison reports.
Use only when selected in the session design; custom layouts and themes are
equally valid. The suggestions below describe this example, not all reports.

- Variance Matrix: AC, PL/PY, Δ, Δ% with integrated variance bars.
- Ranking: sorted bar or Top N Matrix with rank.
- Bridge: waterfall from PY/PL to AC by driver.
- Slicers: period, scenario comparison, segment.

## Variants

| Variant | Example analytical fit | Layout |
|---|---|---|
| A — Variance Matrix hero | Many line items | Full-width Matrix with variance columns, CF on Δ%, waterfall below |
| B — Ranking + bridge | Entity comparison | 6-col ranked bar; 6-col waterfall; Top N Matrix below |
| C — Small multiples | Same comparison across segments | Trellis of AC vs PL charts per segment |

## Rules

- Always show both compared values and the difference.
- Variance colour: favourable/adverse, inverted for lower-is-better.
- Same scale across small multiples.
- IBCS variance notation only if IBCS was requested.

Typical features: `MX-VAR-01`, `MX-CHART-01`, `MX-CF-02`, `MX-SRT-03`, `CH-LIB-02`, `CH-MULT-01`.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- **Critical contract:** sign and favourable direction per measure, driver
  order, and reconciliation from leaves to totals.
- Bridge contributions are existing measures sliced by a dimension, or a
  documented visual calculation, and reconcile from start to end.
- Show at most two comparisons per visual and compare like periods (YTD to
  the last closed period; full year only with an outlook measure).
- Finance starting points: playbooks F2, F3 and F9 in
  domain playbooks.
- **Optional (companion default):** V1 (variance Matrix, bridge and trend) or
  C1 (six small multiples) slots on the
  companion grid; this applies only
  when the user or session design selects it and never overrides the session
  theme, supplied designs, report-inspiration guidance or IBCS opt-in.
