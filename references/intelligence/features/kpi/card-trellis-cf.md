---
id: KPI-MULT-01
name: Card trellis, ranking, and conditional formatting
area: kpi
category: KPI cards
status: IS-Confirmed
encoding: unverified
visual: KPI card
sources:
---

# Card trellis, ranking, and conditional formatting

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Repeats cards per member, ranks them, and colours them by rules.

## When to use

- Per-region KPI tiles.

## UI path

Card › Trellis / Rules.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Presentation evidence: screenshots only.
Visible: repeated per-member card grid with a value and supporting count.
Exact trellis object, ranking, scrolling and formatting rules: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Repeated cards are not proof of a native trellis object versus separate
  cards. Capture grouping, scroll/layout behavior, the ordering measure, ties
  and the filter context of supporting counts.
- A grid of distinct metric panels is not necessarily repeated members of one
  trellis; capture each panel's ownership and composition.
- Visible or consistent colors do not identify a conditional-formatting
  configuration. Capture rule scope, metric-specific favorability, threshold
  equality and missing-data behavior.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Row-trellis wiring (decoded hiddenProperties_!!!_<group> values are JSON strings):
pivotAssignments: AC/comparisons plus the grouping field {bucketId "row",
  columnType "Column", dataRoleType "Grouping"}
chartsMode: visualMode "CARD"
template: rendererType "smallMultiplesChart"; id/chartType vary
  (COLUMN_VERTICAL with chartType "columnChart"; LINE with actualChartType
  "lineChart"; chartType "waterfallChart")
columnFieldsMapping: row[] {name, hierarchy, hierarchyLevel, fromOrder,
  from "group", fieldName}; linearTrellis true
measureConfig: config[*].isTrellis true on every entry, variance included
trellisSettings: gridSize {row, column}; gridLayout "compactCard" | "grid" |
  "singleRow"; display "scroll"; panelScale "auto" | "individual";
  averagePanel and totalPanel disabled
smallMultipleAppearance: panelBorder {enabled true, thickness 1, isDefault false}
superFilterAssignments: matching row entry, configuration.visualType "FACET",
  filterMode "basic"
splitByCategory.pivotValueAssignments: headline copy; may be []
Evidence: [saved] saved native card trellises
```

- Put the group on `row`, not `axis`: a card with only an axis assignment
  was wrongly treated as a trellis [confirmed]. Assignments or inherited
  defaults alone do not prove rendering.
- Classify by `rendererType`; `template.chartType` may still say
  `columnChart` [saved].
- A trellis's `gridLayout` holds one text item, not a per-panel inventory
  [saved].
- Never create missing `measureConfig` entries or pad an empty split list;
  clone a working trellis or set the mode in the UI [saved].
- `gridSize` sets layout, not membership [saved]. Agree member selection and
  overflow; a default 3x3 copied from a non-trellis card is no evidence.
- Responsive state is donor-specific: a fixed-grid trellis saved
  `responsiveLayout.isResponsiveLayoutEnabled: false`; a user-edited one kept
  it true with `isTrellisResponsiveLayoutEnabled: false`,
  `kpiControls.isResponsiveTrellis: true`, `isAutoSeriesHeightEnabled: true`
  and `trellisSettings.isResponsiveGrid: false` [saved]. Copy the whole
  combination; never toggle flags singly.
- Year groupings may carry decoded `groupStateMeta.customName` keyed by the
  field: {name "YYYY", isDateFormat true, timeUnit "YEAR", isDefault true}
  [saved]. Use it only on year fields.
- Re-point per-measure keys `appearance.charts.measuresStyle`,
  `numberFormatting.customFormat`, `panelSorting` and
  `stackedSorting.sortBy`; some donor entries are inert (`enabled: false`,
  `isDefaultValue: true`) [saved].
- Panel borders stay at weight 1 and do not replace the outer container
  border; the non-trellis weight-0 reset does not apply [saved].
- A user-approved option: one row trellis with a shared time `axis` and an
  existing AC/PY pair replaced several per-member trend cards [confirmed].
  It is not a default.
- A trellis converted from a single-member card kept a static member label;
  verify each panel's dynamic label before reuse [open].
- Check every panel's label, value, comparison and chart at the intended
  zoom; if anything clips, enlarge or reflow on-canvas, since a valid grid
  does not prove fit [confirmed].
- UI: assign Actual(s)/comparison and Trellis Row, set the grid in KPI
  ribbon › Data › Trellis, then style, save and read back the full wiring.
- The Data group also lists Conditional Formatting, Sort, Top N and
  Aggregation; their card encodings are uncaptured [open].
- Column trellis, multi-comparison trellis and waterfall-template panel
  rendering remain unverified [open].
- On a trellis card, `appearance.charts.chartBackground` sits behind and
  between the panels while `smallMultipleAppearance.panelBackground` fills
  each panel; one shared Filled colour merged the panel gaps into a single
  block, so keep the two fills distinct [open].
- A saved `trellisSettings.display: "scroll"` with a single-row `gridSize`
  was one report's donor mode, not a default or a fit test [saved]. Under
  the optional
  no-scroll acceptance,
  size or reflow the trellis so no panel needs scrolling.

## Related features

- `KPI-CARD-01`
