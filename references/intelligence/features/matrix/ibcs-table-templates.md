---
id: MX-TPL-04
name: IBCS table templates T01–T05
area: matrix
category: Templates and themes
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-ibcs-formats/table-templates
  - https://lumel.com/ibcs/
---

# IBCS table templates T01–T05

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

IBCS performance tables: T01 hierarchical rows + variance columns, T02
integrated bars, T03 measure rows, T04 integrated waterfalls, T05
hierarchical + integrated bars. Each compares actuals with a model benchmark
(plan, forecast or prior year). T01/T02 set the current period beside
period-to-date with labels in the middle; T04 adds a variance waterfall and
relative-variance pins; T05 adds actual and variance bars with scale bands.

## When to use

- **Only when the user asks for IBCS.** Variance tables to plan or prior year.
- Period versus period-to-date tables (T01/T02) when periods are in columns.
- Income-statement variance tables with integrated charts (T03–T05).

## UI path

Matrix ribbon › Templates › Performance (IBCS) › T01–T05 (first-party guide).
First-party refinements: Conditional Formatting › Quick Rule › Negative on the
relative variance column; Data ribbon › Invert for cost rows; row gripper ›
Add "=" symbol; Format › Appearance › Numbers › Show Positive Sign.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample per template)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Apply together with references/intelligence/ibcs/ibcs-rules.md.
- Scenario-underlined headers, period column groups (MTD/QTD/YTD/full year),
  absolute variance bars and relative variance pins do not identify a
  T-number. Capture the selected template rather than inferring it.
- Keep variance encoding consistent across tables on a page and label
  forecast-inclusive columns AC&FC.
- Validate non-additive counts in totals and row-specific meaning, such as
  feedback polarity.
- Assign actuals to Values (AC) and PY, PL or FC measures to their wells;
  template variances derive from these model measures.
- T01/T02 need a time series in columns. Column hierarchies work but IBCS is
  not designed for them; expanding periods widens the table and adds scrolling.
- Switching templates can discard earlier customizations; choose the template
  before detailed formatting.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Build an IBCS scenario table as the standalone Matrix (`INFORIVER`/10), never
  as a chart `chartType` [saved]. An early companion build found no chart-family
  table owner and skipped the table rather than guessing one.
- The companion's IBCS-signal exports held no Matrix owners, so they add no
  T-number evidence; T01–T04 selection keys stay uncaptured [open].
- Saved Matrix configuration does not establish read-only behaviour, query
  correctness or native rendering [open].
- Inherit the confirmed report theme and apply IBCS table conventions only when
  IBCS was requested and native evidence supports them. **Optional (companion
  default):** no element-level theme on IBCS tables.
- Align vocabulary with the page's charts: the same period labels as the chart
  axis, the same category order as related charts, scenario codes (AC, PY, PL,
  FC) in headers and the unit stated once.
- Data checks before finishing (report failures; never fix the model silently):
  PY identical to AC in every cell signals a missing year shift; a `(Blank)`
  member means fact rows lack the dimension, so report its size rather than
  renaming it; the table's AC total reconciles with the page's charts.
- Current-year columns use the latest year with actuals, not the latest
  date-table year, because plan and forecast years may run ahead.
- [open] The companion's example scenario table put months in rows, categories
  in column groups, scenarios in PL, PY, FC, AC order and a spelled-out unit
  line; this differs from UN 3.3 (time in columns), UN 4.1 (scenario order) and
  UN 1.2 (unit notation) in the IBCS rules, which win.

## Related features

- `MX-VAR-01`
- `CH-IBCS-01`
