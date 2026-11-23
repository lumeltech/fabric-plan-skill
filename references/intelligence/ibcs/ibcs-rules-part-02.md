## Contents

- [SAY — convey a message](#say--convey-a-message)
- [STRUCTURE — organize content](#structure--organize-content)
- [EXPRESS — choose proper visualization](#express--choose-proper-visualization)
- [SIMPLIFY — avoid clutter](#simplify--avoid-clutter)
- [CONDENSE — increase information density](#condense--increase-information-density)
- [CHECK — ensure visual integrity](#check--ensure-visual-integrity)
- [Additional details](#additional-details)

<!-- IBCS reference for the `fabric-plan-skill` skill. Continuation of ibcs-rules.md. OPT-IN ONLY. Summarised in our own words from the IBCS® Standards version 1.2 (IBCS Association, www.ibcs.com/standards, CC BY-SA 4.0). -->

# IBCS rules - Part 2

Continuation of `ibcs-rules.md`.

## SAY — convey a message

| Rule | Apply on an Intelligence Sheet |
|---|---|
| SA 1.1 Know own goals | Decide whether the sheet informs (detect), explains, or asks for a decision (suggest). |
| SA 1.2 Know target audience | Record audience and expectations in the report spec. |
| SA 2.1–2.3 Introduce: situation, problem, question | Narrative sheets open with context; dashboards may skip this. |
| SA 3.1 Detect, explain, or suggest | Phrase the message as a finding, an explanation, or a recommendation. |
| SA 3.2 Say message first | Message text element at the top of the sheet. |
| SA 4.1 Provide evidence | Each message is backed by the visual directly below it. |
| SA 4.2 Use precise words | Numbers and named drivers, not "significant" or "strong". |
| SA 4.3 Highlight message | Highlighting ellipse / emphasis on the value the message cites. |
| SA 4.4–4.5 Name sources, link comments | Footnote with source; numbered comment references. |
| SA 5.1–5.2 Summarize | Repeat the message and state consequences on summary sheets. |

Interactive dashboards ("statistics") may have no message; static reports
and review packs should.

## STRUCTURE — organize content

| Rule | Apply |
|---|---|
| ST 1.1–1.4 Consistency | Items in one list are the same kind; consistent statement types, wording, and visuals across sheets. |
| ST 2.1–2.3 Non-overlapping | Sheets, measures, and dimension members do not overlap (MECE): e.g. don't mix "Europe" and "Germany" as siblings. |
| ST 3.1–3.2 Exhaustive | Show "Others"/"Rest" so parts add up to the total (Top N + Others). |
| ST 4.1–4.2 Reasoning | Deductive (premise → conclusion) or inductive (grouped evidence → conclusion) storylines. |
| ST 5.1–5.3 Visualize structure | Sheet order and grouping reflect the storyline; Matrix hierarchies with indent and subtotal lines; notes grouped. |

## EXPRESS — choose proper visualization

**EX 1.1 Chart types** (time horizontal, structure vertical):

| Analysis | Time series (horizontal axis) | Structure (vertical axis) |
|---|---|---|
| One series | Single columns | Single bars |
| Composition | Stacked columns (all values same sign, ≤ ~5 series) | Stacked bars |
| Scenario comparison | Overlapping columns or scenario triangles | Overlapping bars or triangles |
| Absolute variance | Variance columns (same scale as base) | Variance bars |
| Relative variance | Vertical pins | Horizontal pins |
| Contribution / bridge | Column waterfall (growth or variance) | Bar waterfall (variance) |
| Many data points | Lines (≤ 3 intersecting; else small multiples) | — |
| Two measures per element | Scatter / bubble (two value axes) | — |

**EX 1.2 Table types**: statements with time or scenarios in columns,
structure in rows; embed variance bars and pins in tables (T01–T05).

| Rule | Replace with |
|---|---|
| EX 2.1 Pie and ring charts | Bars or stacked column |
| EX 2.2 Gauges, speedometers | Bullet-like bars with target, or columns with variance |
| EX 2.3 Radar and funnel charts | Bars |
| EX 2.4 Spaghetti charts | Small multiples |
| EX 2.5 Traffic lights | Variance values and pins |

- **EX 3.1** Prefer quantities to text; **EX 3.2** avoid text-only slides.
- **EX 4.1–4.2** Add scenarios and variances wherever they help judgement.
- **EX 5.1–5.3** Show tree structures (decomposition / ROI trees), clusters,
  and correlations (scatter) when the question is about structure or
  relationships.

## SIMPLIFY — avoid clutter

- **SI 1.1–1.3** Clean layout. Use a white background (no coloured or filled
  backgrounds), and no animations or transitions.
- **SI 2.1–2.3** No borders, frames, shadows, or pseudo-3D. No decorative
  colours or fonts. Colour carries meaning only.
- **SI 3.1** Replace gridlines and value axes with data labels.
- **SI 3.2** Right-align numbers instead of drawing vertical lines.
- **SI 4.1–4.3** Remove extra, obvious, and repeated words. Put the unit
  once in the title, not in every label.
- **SI 5.1–5.3** Omit labels for tiny values, avoid long numbers, and drop
  labels that add nothing.

In Fabric Plan: set visual container `border`/`shadow` off, hide gridlines and
value axes when data labels are on, white canvas background.

## CONDENSE — increase information density

- **CO 1.1–1.3** Use small fonts (still legible), small elements, and small
  objects. This lets more information fit on one sheet.
- **CO 2.1–2.2** Use narrow margins and little empty space.
- **CO 3.1–3.2** Add data points (more periods) and dimensions (scenarios,
  variances) rather than spreading them over pages.
- **CO 4.1–4.5** Use these combined forms:
  - overlay charts (e.g. AC over PL);
  - multi-tier charts (values + absolute variance + relative variance stacked
    vertically, sharing the time axis);
  - extended charts (actual + forecast in one series);
  - chart elements embedded in tables (integrated bars/pins/waterfalls);
  - explanations embedded in charts.
- **CO 5.1–5.2** Show small multiples and related charts on one page.

In Fabric Plan: multi-tier IBCS chart templates; Matrix integrated bars and
waterfalls (`MX-CHART-01`, `MX-CHART-03`); trellis (`CH-MULT-01`).

## CHECK — ensure visual integrity

| Rule | Apply |
|---|---|
| CH 1.1 Avoid truncated axes | Bars/columns start at zero. If impossible, show the axis break clearly. |
| CH 1.2 Avoid logarithmic axes | Linear scales for business data. |
| CH 1.3 Avoid different class sizes | Equal time buckets; consistent category widths. |
| CH 2.1 Avoid clipped elements | Do not cut bars; use outlier indicators. |
| CH 2.2 Creative scaling solutions | Scale bands, outlier triangles, magnifying insets. |
| CH 3.1–3.2 Correct areas/volumes | Prefer length (linear) comparisons over area or volume. |
| CH 3.3 Misleading map areas | Don't encode values only in coloured map regions. |
| CH 4.1 Identical scale for the same unit | Same unit on one page → same scale, or scaling lines. |
| CH 4.2 Size charts to given data | Size chart height to its data range. |
| CH 4.3–4.4 Scaling and outlier indicators | Scaling lines/bands; outlier triangles. |
| CH 5.1–5.2 Inflation and currency impact | Show adjusted values or separate the effects when they matter. |

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### CHECK — completion gates

- Before calling an IBCS sheet finished, validate complete ownership and
  serialization; reconcile scenarios, variance formulas and units; render
  notation, cost polarity, axes, labels and titles; test filters and sorting;
  then apply the design rules and the IBCS checklist.
- Record a product limitation only after a reproducible UI or runtime test;
  unverified behaviour stays "to confirm", not "unsupported".
- Data checks (report each failure; never fix the model silently):
  - PY equal to AC in every cell means the PY measure is not shifted by a year.
  - A `(Blank)` member means fact rows lack the dimension; report its size and
    never rename it to hide it.
  - Totals of the same AC measure agree across the bridge, the table and the
    multi-year chart on one page.
  - The report-level theme and applied-theme map match the user's choice;
    chart-side theme strings do not establish it [saved].
  - Each KPI answers a distinct question with a labelled same-period
    comparison, and existing measures were reused before approved additions.
- "Current year" is the latest year with actuals, not the latest date-table
  year; plan and forecast years may run ahead.

### CONDENSE — performance-dashboard pattern

**Optional (companion default):** a 1600 x 900 canvas with 40 px margins, 8 px
snapping and gaps of at least 16 px, in three bands. Use it only when the user
picks this composition; otherwise the design system's grid and margins apply.

| Band | Height | Contents |
|---|---|---|
| A KPI strip | 120 px | four 368 x 120 KPI cards with 16 px gaps |
| B chart row | 288 px | three 496 x 288 charts: variance bridge, monthly trend line, multi-year scenario columns |
| C detail | remaining height | scenario Matrix only if every required row and column fits without scrolling; otherwise reflow or use another sheet |

- Group bands A and B in their own containers. Left to right, the bridge
  explains the total, the line shows the trend and the year chart gives the
  multi-year context.
- Slots are starting geometry, not proof of fit; check clipping and scrollbars
  after rendering.
- Label the trend line's first, minimum, maximum and last points only; keep the
  bridge in model category order unless the user asks to sort by variance.
- [open] Companion layout defaults differ from this file: a light-grey canvas
  with white visual surfaces and mandatory KPI outer borders (SI 1.1–2.3), and
  a multi-year chart with FC behind AC as the reference (UN 4.1 keeps AC and FC
  in front). The rules here win.
