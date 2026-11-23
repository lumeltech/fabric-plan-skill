# Archetype: Executive Summary

<!-- Design topic for the `fabric-plan-skill` skill. -->

**Reader:** leadership. **Question:** "Are we on track, and where should I look?" **Scan time:** ≤ 10 s.

## Composition

Optional example, not a required layout for leadership or executive reports.
Use only when selected in the session design; custom layouts and themes are
equally valid. The suggestions below describe this example, not all reports.

- 3–6 KPI cards with comparison (plan / PY) and ▲/▼ change.
- One lead visual answering the main question (trend vs plan, or variance by segment).
- One supporting visual (ranking or mix). Optional compact variance Matrix.
- 1–3 slicers: period preset, top-level geography or business unit.

## Variants

| Variant | Example analytical fit | Layout |
|---|---|---|
| A — KPI row + hero trend | Monthly grain with plan/PY | KPI row; 8-col trend (column AC + plan line); 4-col ranking bar |
| B — KPI row + variance Matrix | Many segments, finance audience | KPI row; full-width Matrix with variance columns and integrated bars |
| C — KPI column + two-up | Few KPIs, two equally important views | Left 3-col KPI stack; two 4.5-col charts |

## Rules

- Every KPI has a comparison; no orphan absolute numbers.
- Lead visual is the largest region.
- Default slicer: current fiscal year / YTD preset (`SF-DATE-04`).
- Avoid tables with > 8 columns on this sheet; link to a detail sheet instead.

Typical features: `KPI-CARD-01`, `CH-LIB-01`, `MX-VAR-01`, `MX-CHART-01`, `SF-DATE-04`.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- **Critical contract:** an honest comparison basis, one date and scenario
  scope shared by cards and charts, and a readable hierarchy.
- Finance starting points: playbooks F1, F2 and F5 in
  domain playbooks.
- **Optional (companion default):** E1 or E2 slots on the
  companion grid with 3–4 KPI cards
  and at most seven elements; this applies only when the user or session
  design selects it and never overrides the session theme, supplied designs,
  report-inspiration guidance or IBCS opt-in.
