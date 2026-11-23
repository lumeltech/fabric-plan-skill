---
id: CH-LIB-01
name: Column and bar charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-ibcs-formats/column-and-bar-charts
---

# Column and bar charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Vertical or horizontal bars, clustered, stacked, 100% stacked.

## When to use

- Ranking and period comparison.

## UI path

Visualizations pane › Charts 100+ › Bar/ Column, then pick the variant.

## Definition encoding

```text
Pointer: /properties/chartType = "COLUMN_VERTICAL" (default column chart);
         "COLUMN_HORIZONTAL" observed for bars
Pointer: /properties/visualType = 50; registration = ANALYTICS_PLUS
Pointer: /properties/pivotAssignments (bucketId "axis" = category; "AC" = measure)
Evidence: live export of a UI-created test Plan (default state); not isolated by
          a before/after change or re-rendered after reapplication.
```

Copy the saved chart and its companion settings, not just the enum. Default
copies differed only in position, size and layer name. Ranked bars with
value/share labels are presentation evidence only; clustered and stacked
variants need capture.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- If every stack segment repeats the category total, validate exclusivity and
  filter context before using stack totals. Actual/plan columns with variance
  segments are a different composition; never add a difference twice.
- Capture stack, segment-label, row-total and Total-row behavior; the saved
  horizontal-bar enum does not establish it. Confirm whether Other is a source
  category or a generated grouping rather than assuming Top N.
- Capture comparison-marker roles, settings and current/plan domains. Ticks
  alone do not establish bullet-chart encoding; marker colors and outlined
  columns are not universal scenario codes (an outline is not always Plan).
- For bucketed categories such as aging or size bands, define mutually
  exclusive bounds, units/currency, one numeric or chronological order and
  the as-of date; never sum multiple balance snapshots.
- Overlapping actual/plan bars with one label per row hide the smaller value;
  show both values or an explicit variance. Use one hue or status coloring,
  not arbitrary per-category colors.
- Give each chart a distinct title and explicit value measure. Sign-colored
  change columns start at zero; do not title them as cumulative contribution,
  which needs a waterfall.
- Showing history outside the selected period needs an explicit date-scope
  contract.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Keys: id, previousId, lockedTemplateId, chartType, rendererType,
      chartOrientation, actualChartType
Column-family ids -> template chartType/rendererType:
  COLUMN_VERTICAL, COLUMN_HORIZONTAL, SIDE_BY_SIDE_BAR -> "columnChart"
  CLUSTER_COLUMN_VERTICAL, STACKED_COLUMN_VERTICAL,
  STACKED_COLUMN_HORIZONTAL -> "stackedChart"
  Integrated and win/loss ids: see CH-LIB-27
Evidence: [saved] in every inspected saved owner; no before/after capture.
```

```text
Semantic-stack cluster (axis + AC + text stack column), partial:
Pointer: hiddenProperties_!!!_measureConfig (JSON string) ->
  {"config":[{"role":"AC","enable":false,"isVisible":true,"chartIsVisible":true,
  "type":"ACTUAL","order":0,"isTrellis":false}]}
Decoded field mapping also keeps linearTrellis:true; no groupMeasureAssignments.
Evidence: [saved]
```

- Classify the owner by registration and numeric `visualType` before reading
  a template: text (`BI_TEXT`/202), shape (`BI_SHAPE`/201), Super Filter
  (`SUPER_FILTER`/60) and embedded Planning grid (80) owners also save
  `chartType: "COLUMN_VERTICAL"` [saved]. A `CARD` owner that keeps a column
  template is a KPI card (`KPI-CHART-01`), not a standalone chart [saved].
- On repairs, clone the latest user-saved preset and check its active and
  locked templates; forcing an older template or formatting undid user fixes
  [confirmed].
- Record owner `chartType`, template `id`, template `chartType` and
  `rendererType` separately; the renderer name `stackedChart` does not make a
  chart stacked [saved]. Some saved column owners keep an empty
  `lockedTemplateId`; do not fill it [saved].
- Saved chart owners also carry dormant groups of other families (bullet,
  gauge, radar and others). Their presence, edits inside them or case-only
  color changes do not identify the active family or a visible change [saved].
  A page caption never overrides the serialized family [saved].
- Roles seen: `axis`, `AC`, `PY`, `PL`, `row`, `column` and `stack` [saved].
  STACKED_COLUMN_HORIZONTAL adds `stack` to axis + AC [saved]. One saved
  side-by-side bar binds only axis + `PY`; never add a fabricated AC to it
  [saved]. Whether that binding renders a complete chart is unresolved [open].
- Two existing measures as clustered columns (user correction): keep both
  measures and group them natively (`transformMeasure: "groupMeasure"` with
  the synthetic Measures category in `stack`; encoding in `CH-SPLIT-01`).
  Never replace them with one generic measure split by a scenario dimension
  because the totals reconcile [confirmed]. Clusters grouped by a real
  dimension stay valid when its members are the intended series [confirmed].
- The corrected cluster saves template `id`, `previousId` and
  `lockedTemplateId` = `CLUSTER_COLUMN_VERTICAL` with the `stackedChart`
  renderer, while `visualState.chartType` still says `COLUMN_VERTICAL`; the
  same save dropped the obsolete scenario-dimension filter registration
  [saved]. Rendered legend and bar order are not proven by assignment order
  [open].
- Keep both cluster modes: never inject the synthetic grouping into a
  semantic-stack cluster, and `linearTrellis` alone does not prove a rendered
  trellis [saved].
- Insert route, measure-group synchronization, nested row/column expansion,
  axis sharing and limits are unresolved [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
