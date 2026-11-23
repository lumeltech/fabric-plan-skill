---
id: KPI-CARD-01
name: KPI cards
area: kpi
category: KPI cards
status: IS-Confirmed
encoding: verified
visual: KPI card
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/get-started-with-intelligence-sheets
---

# KPI cards

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Headline value with comparison, variance, and optional mini chart; prebuilt templates.

Use the built-in [variance icons](kpi-variance.md) and
[sparkline charts](insight-charts.md), not SVG measures. These are native KPI
features confirmed by the user; a missing saved configuration requires a
native sample, not custom rendering.

## When to use

- Typically 3–6 headline numbers per sheet; an approved dense scorecard may
  use more if comparison labels and values remain readable.

## UI path

Visualizations pane › KPIs, then assign the measure to Actual(s) and any
comparison measures to Comparison.

## Definition encoding

```text
Pointer: /properties/chartType = "CARD"; /properties/visualType = 50
Registration: ANALYTICS_PLUS
Pointer: /properties/pivotAssignments (default card: bucketId "AC" = measure)
Pointer: /properties/visualState/hiddenProperties_!!!_kpiControls (JSON string)
Decoded keys: preset, layout, measures, groups, coreContainer, title, total,
              variance, tooltip, individualKpiControls, minimalViewConfig
Evidence: live export of a UI-created test Plan (default state); not isolated by
          a before/after change or re-rendered after reapplication.
```

Copy the full saved Fabric Plan card including template/container bindings.
The family enum does not isolate headline, sparkline, categorical or formula
content. A copied card can materialize extra default groups without a
behavior change; compare against the original before treating a difference
as a feature setting.

```text
Runtime-verified build (actual + prior year + monthly sparkline):
  Clone a UI-saved sparkline card; rebind fields by exact id replacement.
  pivotAssignments: bucketId "axis" (time field), "AC" (measure), "PY" (comparison).
  From a native AC+PL card: rename role tokens PL→PY, ΔPL→ΔPY, ΔPL%→ΔPY% in the
  assignments and visualState groups except gaugeConfig and kpiControls; inside
  kpiControls rich text the comparison scenario index becomes Δ1 (native PY
  cards index PY as scenario 1 and PL as 2). An AC-only card drops the PL role from
  pivots, assignments, measureConfig, measureConfigMap, fieldsMeta, seriesLabels,
  dataTable and numberFormatting.customFormat.
  kpiControls.gridContainer and coreContainer = card width/height minus 25px;
  gridLayout percentage geometry splits text and chart (60/40 kept titles readable).
Evidence: values reconciled to DAX and rendering user-confirmed in a published report.
```

## Constraints

- Long measure names in the `[$Title]` mention overflowed the card; replace
  the mention with a short static title in the title paragraph and keep exactly
  one title. A 60/40 text/chart split kept titles readable at about 350px wide;
  check narrower cards at the target viewport.
- Opening a page in edit mode can save normalization that re-enables
  `legendSettings.enabled` and recomputes grid geometry; read cards back after
  any editor save.
- Capture each card's measure and container roles. A title that disagrees with
  its bound value (such as a quantity title over a duration) needs definition
  resolution, not a copied title.
- Define each score or composite rate's numerator, denominator and weighting,
  reconcile it to approved factors before showing supporting percentages, and
  add target comparisons where the model provides them.
- If the value shows an 'undefined' suffix, turn Number Format off.
- Sparkline availability does not require adding one to every card. Establish
  currency, rate and duration units from the model.
- When a card has a sparkline, keep it clearly visible: about a third of the
  card height, with no sparkline data labels or point markers unless the user
  asks [confirmed]. See
  [dashboard standards](../../design/dashboard-standards.md#kpi-cards).
- A uniform tile grid, or several support values in one card, does not prove a
  native trellis or one saved container. Capture card/container composition
  rather than inferring it from alignment; use native components and keep
  labels readable.
- Give every period-based card (period-to-date, previous day, etc.) an explicit
  date anchor.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Card mode, template and buckets

```text
Pointer: /properties/visualState/hiddenProperties_!!!_chartsMode (JSON string)
Decoded: visualMode "CARD" in every inspected saved card owner
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Retained under CARD: COLUMN_VERTICAL, AREA, LINE or COLUMN_INTEGRATED_VERTICAL
  with rendererType "columnChart"; WATERFALL_VERTICAL with "waterfallChart";
  AC/PY/PL scenario cards add chartOrientation "vertical" and actualChartType
  "groupedBar"; row trellises use "smallMultiplesChart" (KPI-MULT-01)
Evidence: [saved] saved native card owners
```

- Classify a card by root family and `chartsMode`, never by its retained
  template: a CARD keeping a waterfall or column template is not a chart.
  Keep mode, template and elements together [saved].
- Check `id`, `previousId` and `lockedTemplateId` against the latest
  user-saved card; forcing an older donor's template or formatting undid
  user fixes [confirmed].

| UI bucket | `bucketId` | Kind, observed maximum |
|---|---|---|
| Category | `axis` | category; embedded trend only |
| Actual(s) | `AC` | measure, 1–27; required even when UI metadata says `isOptional: true` |
| Comparison 1 / 2 / 3 | `PY` / `PL` / `FC` | one measure each |
| Trellis Row / Column | `row` / `column` | grouping field |
| Tooltip-Measures | `Tooltip` | measure, 30 |
| Tooltip-Text categories | `TextCategory` | text measure, 30 (`KPI-CAT-01`) |

Bucket metadata and saved owners [saved]; limits are build-specific. The
`column` trellis role is inferred, not captured [open].

- `fieldsMeta` indexes roles (AC 0, PY 1, PL 2, FC 3) and does not replace
  assignments [saved]. Slots are storage roles: user-saved single-comparison
  cards hold a budget in `PL` in one report and a plan in `PY` in another
  [confirmed]. When editing a card, keep its saved slot and mappings rather
  than renaming them to match a label; several `AC` measures are not a
  comparison.
- Rebind ids and table names only at their owners: a blanket rename of the
  measure table also rewrote the `columnType`/`dataRoleType` value
  `"Measure"` and broke the card [confirmed]. Rebind `pivotAssignments` with
  matching `superFilterAssignments`, reconcile the
  `splitByCategory.pivotValueAssignments` copy when the headline changes, and
  re-point measure-keyed formatting, appearance and sorting entries [saved].
- UI copy JSON (root `config`, `meta`, `apiVersion`, `timeStamp`) is not a
  persisted definition; never paste its trees into `properties`. Its
  `essentials`, `measureConfig`, `columnChart.chartMeta` and `dimensions` are
  render-derived [saved]. A copied text-only card shows
  `discreteChartConfig.actualChartTemplateId: "CARD"` and `isCardMode: true`
  while `template.id` stays `COLUMN_VERTICAL` [saved].
- Leave `focusPanel.kpiControls` (a second layout copy) and dormant
  gantt, sankey, waterfall, table and slicer defaults in card state
  untouched; their role on a card, including whether a default average line
  renders, is unknown [open].

### UI route

- Select the card for the KPIs pane (Assign Data, Advanced) and the KPI
  ribbon: drop the headline into Actual(s), add comparisons, then use the
  hover pencil for title/value/variance layout.
- Recorded KPI ribbon groups: Presets (Simple, Variance, Advanced),
  Appearance, Border, Shadow, Insert (Add, Layout), Chart (Sparkline, Charts
  Options), Data (Trellis, Conditional Formatting, Sort, Top N, Aggregation),
  Settings (Themes, Data Label), Export, Reset, Quick Access. KPI Border and
  Accent set side, weight and colour (Border also radius), separately from
  Layout › Effects › Border on the container. Confirm labels in the UI.

### Placement and review

- A new card saved past the canvas edge (normalized y above 1) on a full
  sheet was a user-reported defect [confirmed]. Shrink it while legible, or
  ask before compacting other visuals or moving it to another sheet.
- Read `canvasStyle.dimension.elementScalingUnit` first: saved sheets use
  `"percentage"` (normalized placement) or `"pixel"` [saved]. Pixel
  `kpiControls` internals are card-local, never sheet coordinates.
- Treat clipped titles, values, comparisons or chart marks as defects and
  enlarge or reflow on-canvas; saved geometry does not prove fit
  [confirmed]. The minimum usable card size is unconfirmed [open].
- Prefer one card pairing an existing actual and comparison over separate
  actual, plan, variance and variance-% cards; use the remaining cards for
  complementary metrics.
- Card measures from Planning or InfoBridge sources, with their save and
  refresh dependencies, are not enabled in this release.
- The companion library records saved native notes on card owners, while
  `CH-NOTE-01` says notes are for charts and tables only, not cards; that
  target guidance wins until a native capture resolves it [open].

## Related features

- `KPI-VAR-01`
- `KPI-CHART-01`
- `KPI-CAT-01`
