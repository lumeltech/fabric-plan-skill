## Contents

- [When to load this file](#when-to-load-this-file)
- [SUCCESS at a glance](#success-at-a-glance)
- [UNIFY — semantic notation (mandatory in IBCS mode)](#unify--semantic-notation-mandatory-in-ibcs-mode)
  - [Terms, numbers, units, dates](#terms-numbers-units-dates)
  - [Messages, titles, legends, labels, comments](#messages-titles-legends-labels-comments)
  - [Measures](#measures)
  - [Scenarios](#scenarios)
  - [Time and structure axes](#time-and-structure-axes)
  - [Scenario analyses and variances](#scenario-analyses-and-variances)
  - [Time series and structure analyses](#time-series-and-structure-analyses)
  - [Highlighting, scaling, outliers](#highlighting-scaling-outliers)
- [Fabric Plan IBCS mapping](#fabric-plan-ibcs-mapping)
- [IBCS compliance checklist](#ibcs-compliance-checklist)
- [Additional details](#additional-details)

<!-- IBCS reference for the `fabric-plan-skill` skill. OPT-IN ONLY: load when the user asks for an IBCS report, IBCS theme, or IBCS notation. Summarised in our own words from the IBCS® Standards version 1.2 (IBCS Association, www.ibcs.com/standards, CC BY-SA 4.0). IBCS® is a registered trademark of HICHERT+FAISST GmbH. -->

# IBCS rules for Intelligence Sheets

> **Required continuation.** After this file, open
> [ibcs-rules-part-02.md](ibcs-rules-part-02.md) (SAY, STRUCTURE, EXPRESS,
> SIMPLIFY, CONDENSE, CHECK rules).

## When to load this file

Only when the user explicitly asks for **IBCS** (an IBCS report, IBCS theme,
IBCS notation, IBCS templates) or picks the IBCS report template. Otherwise use `design/design-system.md`.
When loaded, these rules **override** the design system for scenario
encoding, variance display, colours of variances, number formats, titles,
and chart choice. Set `ibcs: true` in the `Design Brief:`.

Fabric Plan Intelligence Sheets are IBCS® certified (May 2026) for chart
templates C01–C13 and table templates T01–T05, with **strict** and
**flexible** IBCS themes. Prefer those templates over hand-built notation.

## SUCCESS at a glance

| Area | Code | Intent |
|---|---|---|
| SAY | SA | Every page conveys a message, supported by evidence |
| UNIFY | UN | Same meaning → same look (semantic notation) |
| CONDENSE | CO | High information density; everything needed on one page |
| CHECK | CH | Visual integrity: no misleading scales or areas |
| EXPRESS | EX | The right chart or table for the message |
| SIMPLIFY | SI | Remove clutter and decoration |
| STRUCTURE | ST | Logical, consistent, non-overlapping, exhaustive content |

UNIFY is the defining part of IBCS and is mandatory in IBCS mode.

## UNIFY — semantic notation (mandatory in IBCS mode)

### Terms, numbers, units, dates

- **UN 1.1** One glossary of terms and abbreviations; short forms for column
  headers, longer forms for row headers.
- **UN 1.2** One number format across the report. Use metric prefixes so
  numbers show **≤ 3 digits in charts, ≤ 4 in tables**.
  - Currency as ISO code with lower-case prefix: `kEUR`, `mUSD`, `bEUR`.
  - One negative format for everything: `-123` or `(123)`.
  - Plus sign only on variances (`+13`, `+13%`).
  - Dates ISO style `YYYY-MM-DD`.

### Messages, titles, legends, labels, comments

- **UN 2.1** The message (if any) sits at the top of the page, always in the
  same place and style.
- **UN 2.2** Titles identify, never evaluate. Three lines:
  1. **Who/what**: reporting unit (entity, division, project), plus filter
     info if not exhaustive ("top ten clients").
  2. **Measure in unit** (measure bold, unit regular), plus structure or
     analysis notes: "Net sales in mEUR, by country, sorted by net sales (↓)".
  3. **Time and scenario**: "2026 AC and PL", "2026-Q1", "2025..2027".
     Use `&` for a combined series (`AC&FC`), `and` for parallel series.
  Page title top-left; object subtitles above each visual on multi-object pages.
- **UN 2.3** Legends integrated in the chart, written horizontally:
  - single series → legend in the title;
  - stacked columns → left of the first or right of the last column;
  - stacked bars → centred above the top bar;
  - line charts → at the line end.
  Data labels next to elements, horizontal, ≤ 3 digits; omit labels of tiny elements.
- **Comments and footnotes**: link comments to values with consistent
  numbered references; footnotes at the bottom of the page (sources, definitions).
  Validate year/filter alignment, favorability and rate units for numbered
  notes; screenshots do not identify templates or demonstrate strict IBCS
  compliance.

### Measures

- **UN 3.1** Basic measures vs ratios:
  - Column/bar width: basic measures **2/3** of category width; ratios **1/3**.
  - Lines: basic measures thick; ratios thin (half width).

### Scenarios

**UN 3.2** — recognise the scenario by its fill, without reading labels:

| Scenario | Code | Fill |
|---|---|---|
| Actual (measured) | AC | Solid dark (e.g. dark grey) |
| Previous year / earlier period (measured) | PY | Solid light (e.g. light grey) — only in scenario comparisons |
| Plan / Budget (fictitious) | PL / BU | Outlined (frame, white/empty fill) |
| Forecast (expected) | FC | Hatched (dark stripes) with outline |

In stacked elements apply the scenario notation to the lowest segment;
fill upper segments with shades of grey, outlined or hatched if PL/FC.

### Time and structure axes

- **UN 3.3** Time runs **left to right** on a **horizontal** axis; in tables,
  time is in **columns**. Abbreviations: `2026`, `2026-Q1`, `Jan..Mar` (two
  dots for a span), `.2026` first day, `2026.` last day. Longer periods may
  use wider categories; keep widths consistent per page.
- **UN 3.4** Structure dimensions (regions, products, customers, accounts)
  go on a **vertical** axis (bar charts); in tables, structure is in **rows**.

### Scenario analyses and variances

**UN 4.1**

- **Order:** scenarios of different years in ascending time order (PY, FC,
  PL). Use scenario labels (AC, PY), not years, in the comparison; the year
  goes in the title or header.
- **Comparison display:** overlapping columns/bars (reference behind,
  AC/FC in front) or a **scenario triangle** for the reference.
- **Absolute variance:** `ΔPL` = AC − PL (or FC − PL), `ΔPY` = AC − PY.
  - Variance columns/bars use the **same width and scale** as the base values.
  - Labels sit outside, in the direction of change.
  - Ratio variances are in percentage points (`+10pp`).
- **Relative variance:** `ΔPL%` = (AC − PL) / PL × 100, `ΔPY%` likewise.
  - Shown as **pins** (thin bars/columns) with a head marker in the
    analysed scenario's fill.
  - Show `n.a.` when uninterpretable (e.g. negative reference).
- **Variance colours:** favourable **green**, adverse **red**, neutral
  **blue**.
  - No colour available: dark/light/medium grey.
  - Colour deficiency: blue-green instead of green.
  - These are not traffic lights.
- **Variance fill:** the bar's fill shows the analysed scenario (solid for AC,
  hatched for FC).
- **Variance axis:** the axis shows the reference scenario (solid light for
  PY, double line / outlined for PL or BU).

### Time series and structure analyses

**UN 4.2**

| Analysis | Notation |
|---|---|
| Year-to-date | `_Jun 2026` |
| Year-to-go | `Jun 2026_` |
| Moving (12-month) | `~Jun 2026` |
| Average | Appended `ø` sign |
| Last-date value | Appended `.` |
| Temporal indexing | Black arrowhead at the index point, labelled `100%` |
| Structural average | `ø` appended or prefixed |
| Ranking | Arrow after the sort key: `sales ↓` |
| Structural indexing / normalizing | Arrowhead + `100%` assisting line |

### Highlighting, scaling, outliers

- **UN 5.1** Consistent highlighting:
  - assisting lines and areas;
  - difference markers between two values (green/red/blue);
  - trend arrows with the method (e.g. `CAGR +10.8%`);
  - a highlighting ellipse for the message value;
  - reference arrowheads for index/benchmark;
  - numbered comment references.
- **UN 5.2** When several charts of the same unit use different scales, show
  a **scaling line** at the same value in each chart, optionally a light
  **scale band**.
- **UN 5.3** Unimportant outliers (often huge % variances on small bases):
  cut the pin, omit the head, add an **outlier triangle** pointing in the
  direction of growth.

## Fabric Plan IBCS mapping

| IBCS need | Intelligence Sheet feature |
|---|---|
| Time series AC vs PL/PY, variance columns and pins | IBCS chart templates C01–C13 (`CH-IBCS-01`), variance charts (`CH-LIB-27`), deviation (`CH-DEV-01`) |
| Structure comparison (bars), variance bars | IBCS bar templates (`CH-IBCS-01`), column/bar (`CH-LIB-01`) |
| Variance bridges | Waterfalls (`CH-LIB-02`) — IBCS waterfall templates |
| Small multiples with scaling line / scale bands | Trellis (`CH-MULT-01`), IBCS small multiples; scale bands in variance settings |
| Statements and variance tables | IBCS table templates T01–T05 (`MX-TPL-04`), variance columns (`MX-VAR-01`), integrated bars/waterfalls (`MX-CHART-01`, `MX-CHART-03`) |
| Semantic number formats, signed variances | Number scaling (`MX-NUM-01`), semantic/IBCS formatting (`MX-NUM-03`, `numberFormatting.ibcsformat`) |
| Scenario fills (solid / outlined / hatched) | Template scenario mapping (Comparison 1/2/3) in IBCS templates; strict IBCS theme |
| Comments with references | Notes and annotations (`MX-NOTE-01`, `CV-ANN-01`, `CH-NOTE-01`) |
| Top N + others with ranking arrow | Top N (`MX-SRT-03`, `CH-SORT-01`) |

Use the **strict** IBCS theme for full compliance. Use **flexible** only
when the user accepts deviations (custom axes, reference lines, custom
number formats). Capture native samples for template settings before
authoring (`core/native-samples.md`).

## IBCS compliance checklist

- [ ] Titles: who / measure in unit / time and scenario; no evaluation in titles
- [ ] Message at the top (if the page conveys one)
- [ ] AC solid dark, PY solid light, PL outlined, FC hatched — everywhere
- [ ] Time horizontal left→right; structure vertical (bars, table rows)
- [ ] Variances labelled ΔPL / ΔPY / ΔPL% / ΔPY%, with + signs on positives
- [ ] Variance colours green / red / blue by business impact (inverted for costs)
- [ ] Absolute variances same scale as base values; relative variances as pins
- [ ] Numbers ≤ 3 digits in charts, ≤ 4 in tables; one negative format; ISO currency + k/m/b
- [ ] Legends integrated; labels horizontal; no gridlines or value axes when labelled
- [ ] Same unit → same scale across charts on a page, or scaling lines/bands
- [ ] No pie, gauge, radar, funnel, traffic-light, 3D, shadows, decorative colour
- [ ] Outliers marked with outlier indicators, not by rescaling the chart

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

Saved native template identities, scenario tiers and IBCS flags are in
IBCS chart templates; table notes
are in IBCS table templates.

### Evidence and theme boundary

- Check four things separately: user-required design, saved native
  configuration, tested rendering or business results, and standards
  compliance. Saved IBCS signals are not proof of effective theme, runtime
  behaviour or standards compliance [open].
- Never write a guessed IBCS theme enum or infer the active report theme from
  chart-side theme strings [open]; read the report-level theme and applied-theme
  map from a fresh readback.
- **Optional (companion default):** apply the chosen theme once at report
  level, avoid element-level theme changes and keep a confirmed choice on
  repairs.
- Buckets `AC`, `PY`, `PL` and `FC` are slots: scatter, bubble, box-plot and
  bullet templates reuse them for coordinates, sizes or targets [saved].
  Confirm period meaning, favourable direction and formulas separately.

### Notation additions

- Stacked scenario notation is stored apart from the main fill
  (`stackedPattern`: PL `outlined`/`partial_outlined`, FC
  `hatched`/`partial_hatched`) [saved]; whether `partial_*` realizes the
  lowest-segment rule of UN 3.2 is [open].
- PY's light grey is a colour rule; no saved `pattern` value encodes it [saved].
- Keep red and green for variances: label a line's first, minimum, maximum and
  last points in the AC colour, never with red or green markers.
- Label bridge endpoints by the bound scenario slot (a start bar bound to PL is
  labelled PL), even when a reference image labels it otherwise.
- When a monthly axis aggregates several years, state the year span in the
  title's time line (UN 2.2 span notation) or filter to one year.
- Keep one visible title owner per visual with scenario, period and unit
  context; confirm the rendered title and unit instead of enabling every
  retained title field.
- Show ΔPY or ΔPL tiers only for meaningful comparisons (aligned period, unit
  and population).

### Multi-tier column (C03) additions

- Label the front AC column in tier 1, each variance column in tier 2 and each
  pin head in tier 3, above positive and below negative values; leave the
  reference column behind unlabeled.
- Put scenario codes beside the first or last column pair and `ΔPY`/`ΔPY%` (or
  `ΔPL`/`ΔPL%`) beside their tiers, not in a separate legend box.
- More than about 25 periods: suggest a coarser period; if declined, build as
  asked and state the readability trade-off.
- A third scenario: keep AC in front and the first-named reference behind, show
  the third as scenario triangles, and keep the variance tiers on the first
  reference unless the user names another.
- One measure only: skip the variance tiers, state which comparison is missing,
  and never create a replacement measure without its own approval.
- Zero or missing reference in a period: omit that pin instead of plotting an
  infinite value, keep the `n.a.` label and footnote it.
- **Optional (companion default):** add a chart-level message line, period
  comment markers or trend arrows only when the user asks or supplies the
  content; page-level message rules still apply.

### Polarity and scaling

- The native cost-inversion control is uncaptured: no saved inversion example
  or isolated change exists [open]. Check the control, direction and rendered
  colours before calling a cost chart compliant.
- A saved uniform scaling factor does not prove equal units or axis extents
  across charts [open]; reconcile scales per UN 5.2 and CH 4.1.
- When bridge totals dwarf the steps, use a native axis break or
  focus-on-variance option with a visible break marker, never a silent
  truncation.
