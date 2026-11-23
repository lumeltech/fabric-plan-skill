## Contents

- [8. Chart rules](#8-chart-rules)
- [9. Titles and storytelling](#9-titles-and-storytelling)
- [10. Number and locale formats](#10-number-and-locale-formats)
- [11. Branding](#11-branding)
- [12. Semantic model conventions](#12-semantic-model-conventions)
- [13. Per-report workflow](#13-per-report-workflow)
- [14. Pre-flight checklist](#14-pre-flight-checklist)
- [Additional details](#additional-details)

<!-- Design topic for the `fabric-plan-skill` skill. Continuation of design-system.md. Open this file directly from the skill reference index. -->

# Design system - Part 2

Continuation of `design-system.md`.

Style and shell examples apply only when selected in the session profile, not
as universal defaults or report-type rules. Analytical correctness,
accessibility and native-encoding requirements still apply.

## 8. Chart rules

Use only the Intelligence chart library (`references/intelligence/features/charts/`),
Matrix, tables and KPI cards.

- **Bars** (`CH-LIB-01`): sorted by value; start at zero (never force a zero
  axis when bars can go negative); labels outside the bar end; variance bars
  use the session's favorable/adverse styles with explicit metric direction.
- **Lines** (`CH-LIB-03`): session's distinguishable scenario styles; shaded
  area only on single-line charts, starting at zero. Slope charts (`CH-LIB-22`):
  prefer labeled straight segments for discrete comparisons; an approved curved
  style needs native capture and must not imply unmeasured intermediate values
  ([slope graphs](../features/charts/slope.md)). Independent axis scales must
  not be interpreted as absolute change from the screen angle.
- **Matrix and tables** (`MX-*`, `TB-*`): header/banding per the session
  profile; totals need valid aggregation and a reader purpose; signed columns
  use the chosen semantic styles. Row-level tables group by one ID only, other
  attributes as left-aligned text.
- **Donut or pie** (`CH-LIB-06`): only where share is the question, ≤ 5 slices.
- **Funnel** (`CH-LIB-16`): only for nested stages; unordered categories stay as bars.
- **Scatter** (`CH-LIB-07`): average reference lines on both axes, dashed trend
  line (`CH-ANLY-01`), quadrant explanation in Help.
- **Waterfall** (`CH-LIB-02`): distinguish increases, decreases and totals with
  the session's semantic styles and documented favorability.
- **Gantt, treemap, ribbon (use quarters), combo or Pareto, in-cell charts,
  Sankey, Marimekko** are available for variety.
- **Every colour-coded visual has a visible colour key** (legend), not only in Help.
- **Time axes:** monthly charts show closed months only; long ranges use a
  continuous month axis without a scroll bar; in combos, give the line a
  contrasting hue.
- Every data visual has a **descriptive subtitle or tooltip (≤ 240
  characters)** explaining what it shows **(check)**.
- Look up every formatting setting in the feature file; don't guess.

## 9. Titles and storytelling

- **Titles stay plain** and state the visual's purpose ("Revenue vs budget").
- **Stories go in the subtitle** of the lead visual only: at most one per
  sheet, many sheets none; never on KPI cards, tables (unless the lead visual)
  or slicers.
- A story must add what the KPI cards don't show, never restate a card.
  Patterns: change over time, peak or latest value, leader or problem item,
  spread across items.
- Build stories from a model text measure, Matrix/chart note or text element
  bound to context (`MX-CTX-01`, `CV-ANN-01`); fall back to the plain subtitle
  when no sentence can be formed.

## 10. Number and locale formats

Set `{{CUR}}` once and use it everywhere; never mix currencies **(check)**.

| Kind | Display | Example |
|---|---|---|
| Money, billions | `{{CUR}}` + 2 decimals + B | {{CUR}} 2.04B |
| Money, millions | `{{CUR}}` + 1 decimal + M | {{CUR}} 485.4M |
| Money, thousands / exact | `{{CUR}}` + K / exact with separators | {{CUR}} 38K |
| Percent | 1 decimal | 18.6% |
| Delta | ▲ / ▼ + 1 decimal | ▲ 4.2% |
| Counts | thousands separator | 10,412 |
| Dates | `dd mmm yyyy` | 30 Sep 2026 |

- Use Matrix number scaling and semantic formatting (`MX-NUM-01`, `MX-NUM-03`)
  and chart/card number settings, not per-cell custom strings.
- Compact forms on cards and axes; exact values in tooltips and Matrices.
- Very large percentages become "per unit spent" amounts.
- Small values in bar labels: no scaling.
- Slicers list only periods with data (hide blanks and future periods) **(check)**
  (`SF-DISP-01`).

## 11. Branding

- Apply the [inspiration library's logo treatment](report-inspiration.md#branding-and-logo-treatment)
  only with approved source assets; screenshots are placement references, not
  reusable logo files or image-encoding evidence.
- Use the user's approved branding and placements from the session profile;
  header, footer, Help or rail logos are options, not mandatory regions. Use
  suitable supplied light/dark background variants where needed.
- Company name, credit line and contact details are project inputs, not
  requirements to repeat in a prescribed shell.

## 12. Semantic model conventions

This skill reads the model, never changes it. Use these to judge it and report
gaps:

- Star schema; naming `[Fact] …`, `[Dim] …`, `[Param] …`; display folders;
  descriptions on every table, column and measure.
- Every field a report uses must exist in the model **(check)** (field registry
  closure).
- Use a unique label (name plus ID) for people, never a bare name.
- Variance % over mixed accounts divides by the sum of absolute plan values;
  show "No plan" when zero.
- Missing measures are listed as model gaps for a semantic-model skill.

## 13. Per-report workflow

1. Write the spec (discovery mode): use case, audience, cadence, sheets, drill
   sheets, measures.
2. Report model gaps first; build only on fields that exist.
3. Author, then validate (`plan_def.py validate`); fix every error.
4. Publish to a test plan; open every sheet in reading and editing mode; check
   Help and Info controls, their close/back behavior and tooltips.
5. Review against these rules and get sign-off.
6. Keep the decoded definition and spec as the source of truth; record any
   UI-only change back into them.
7. Turn all feedback into a rule here and, where possible, an automatic check.

## 14. Pre-flight checklist

- [ ] Sheet title names the sheet; context and branding follow the approved design
- [ ] Help and Info actions/content verified (or opt-out); per-visual subtitle or tooltip
- [ ] Canvas, regions and component sizing match the approved session layout and stay usable
- [ ] One font family; one currency; compact units
- [ ] KPI comparisons use the chosen native treatment and correct favorable direction
- [ ] Bars have meaningful order, readable labels and valid baselines; scenario styles distinguishable
- [ ] Colour map consistent; colour key on every colour-coded visual; no red/green-only signal
- [ ] Drill sheets: source visual, Drill link, Back, Selected X label, hidden from navigation
- [ ] Interactions: click filters everything; slicers and labels untouched; exceptions justified
- [ ] Story subtitle (if any): one per sheet, lead visual, adds new information
- [ ] Session tokens, button/navigation styles and page-role layouts reused across reports
- [ ] No report type forces a palette, shell or layout; custom choices supported
- [ ] Only Intelligence chart library visuals; IBCS only if requested

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### More chart rules

- Choose orientation for the labels: long category names read better on
  horizontal bars or a horizontal bridge; do not keep a vertical bridge only
  because an earlier sheet used it.
- Keep axis tick labels regular weight; reserve bold for axis titles and
  group headers.
- Clutter, label density and inherited reference lines are covered by the
  finishing pass.

### More number rules

- Never add a custom scale suffix that repeats the native scale, such as an
  "M" suffix on values already scaled to millions [confirmed].
- Automatic scaling must not change the meaning of a percentage or a unit
  rate; keep formats suited to percentages, counts, currency and unit rates.
- Showing a grand total does not mean every measure should sum; set totals and
  measure aggregation separately.
- State each sheet's currency scale in its subtitle.

### More text rules

- Numbers in any text come from bound data; never invent or hard-code figures.
- Keep titles content-bound as the bindings, scope and filters change
  (typography).
- Treat measure display names in a visual as content too: rename them when
  the binding, period or scenario changes, so no alias or reference caption
  contradicts the data.
