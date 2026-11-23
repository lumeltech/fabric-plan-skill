# Archetype: Operational Monitor

<!-- Design topic for the `fabric-plan-skill` skill. -->

**Reader:** operators, managers on shift. **Question:** "What needs attention now?"

## Composition

Optional example, not a required layout for operational reports. Use only
when selected in the session design; custom layouts and themes are equally
valid. The suggestions below describe this example, not all reports.

- Status KPI cards with thresholds (on track / at risk / breach).
- Exception list: Matrix filtered to items breaching a rule, sorted by severity.
- Trend of the key operational measure with a target line.
- Slicers: site/team, current period (relative date `SF-DATE-03`).

## Variants

| Variant | Example analytical fit | Layout |
|---|---|---|
| A — Status strip + exception Matrix | Many items, rule-based exceptions | KPI strip; 8-col exception Matrix with action dots/icons; 4-col trend |
| B — Small multiples | Same metric across 6–12 units | KPI strip; trellis of sparklines/columns per unit |
| C — Wallboard | Large-screen viewing | Large KPI tiles and a trend; theme and filter placement follow user/session choices |

## Rules

- Conditional formatting carries status (`MX-CF-03`), always with icons or labels.
- Sort exceptions by severity, then size.
- Relative date defaults ("last 7 days", "this month").
- Keep interactions simple; avoid deep drill on this sheet.

Typical features: `KPI-CARD-01`, `MX-CF-03`, `MX-SRT-01`, `CH-MULT-01`, `SF-DATE-03`.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Status tiles carry their target or threshold context; show data freshness
  (refresh or as-of) when the model has such a field.
- Exception lists need a threshold measure or column; never invent
  thresholds.
- Operations starting points: playbooks O1–O3 in
  domain playbooks.
- **Optional (companion default):** the companion's role budget and status
  palette (layout,
  colour) apply only when the user or
  session design selects them and never override the session theme, supplied
  designs, report-inspiration guidance or IBCS opt-in.
