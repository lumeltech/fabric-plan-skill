---
id: KPI-CHART-01
name: Insight charts in cards
area: kpi
category: KPI cards
status: IS-Confirmed
encoding: verified
visual: KPI card
sources:
---

# Insight charts in cards

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Sparklines and mini charts inside cards.

KPI sparkline charts are **built-in** (user-confirmed).
Use the card's native chart controls and bind its time/category axis and
numeric measures. Do not generate SVG measures or image-data measures for
sparklines, or substitute a standalone chart for the built-in capability.

## When to use

- Spark cards with 12-month trend.

## UI path

Assign the card's category first, then KPI ribbon > Sparkline > Line > Line
(the leaf command). Selecting or hovering the parent menu is not activation.
Save, wait for propagation and capture the resulting definition.

## Definition encoding

```text
Native Line capture (saved reporting KPI):
  properties.chartType and visualState.chartType remain "CARD".
  pivotAssignments: category in bucketId "axis", numeric series in AC/PL as bound.
Decoded hiddenProperties_!!!_kpiControls:
  layout: 4; previousLayout: 4; isAutoLayout: false; isDefaultLayout: false;
  isLayoutPositionChanged: true; hasStateChange: true.
  gridContainer/coreContainer/gridLayout geometry reserves room for the chart.
Decoded hiddenProperties_!!!_template:
  id: "LINE"; previousId: "LINE"; lockedTemplateId: "LINE";
  actualChartType: "lineChart".
Decoded hiddenProperties_!!!_measureConfig:
  bound series use chart: "lineChart", visible/enabled true.
Decoded hiddenProperties_!!!_appearance.charts.lineArea.lineType: "line".
Decoded hiddenProperties_!!!_responsiveLayout.isResponsiveLayoutEnabled: true.
hiddenProperties_!!!_columnFieldsMapping includes axis and activeAxisBucket metadata.
Evidence: saved native Line selection, distinct from an earlier category-only capture.
Other mini-chart types and runtime acceptance: not established by this capture.
```

Copy the coherent native template, measure configuration, appearance, mappings,
responsive layout and card/container geometry, preserving JSON-string groups.
Some renderer fields in the captured Line template still say `columnChart`;
do not independently "correct" them. Adapt series to the actual bound roles:
do not retain an unbound PL series or comparison placeholder on an AC-only card.
Never invent a `sparkline` property. A `CARD` family code or category binding
alone does not prove activation.

```text
Runtime-verified area sparkline: a UI-saved card whose template renders an AREA
  sparkline, with the time field in bucketId "axis" and a gridLayout item of type
  "chart"; rebinding AC/PY and the axis kept it working across many cards.
Legend: hiddenProperties_!!!_legendSettings.showTitleAsLegend:false (set by a UI save);
  true printed the series name under the sparkline.
Time order: hiddenProperties_!!!_sorting = {"sortBy":"category","sortType":"ascending",
  "includeOtherInSort":false,"isDefaultValue":false,"reduceOverlaps":false} sorts the
  axis oldest-first, as in native time-axis charts and cards. The template default
  {"sortBy":null,"sortType":"reset","isDefaultValue":true} drew a month axis
  newest-first in a line chart although the model sorted the months chronologically.
Evidence: user-confirmed sparkline rendering in a published report; ascending sort
  matches UI-saved time-axis charts and cards.
```

## Constraints

- Use the built-in insight charts, never SVG or image-data measures or a
  substitute standalone chart. Availability is confirmed despite unverified
  JSON; capture a working native card when settings are missing.
- Derived numeric measures are separate from chart rendering and remain
  subject to normal description and permission requirements.
- Proximity, alignment, captions or similar shapes do not prove ownership.
  Capture whether each mini chart, bar, marker, gauge or pictogram belongs to
  the card, a bullet/progress setting, another visual or a shape.
- Card and standalone evidence are not interchangeable: a line, bullet or
  waterfall enum is not a card template, and a stem/dot mini-chart does not
  prove lollipop activation. Capture the full card template and section bindings.
- Capture each insight measure, series, date grain, history window and scope
  independently; similar shapes, point counts or placement do not prove shared
  bindings or scales. Give as-at and period-to-date labels an explicit year.
- Specify scenario roles and comparison visibility. Baseline/actual bars with a
  target tick, or a baseline-difference-actual bridge, are scenario comparisons,
  not time trends; bind baseline, signed difference and actual separately.
- Define target markers, bands, average guides (and their population), extrema,
  endpoint markers and ties. Sign-colored fills/stems need a defined metric
  direction; gradient fills are decoration under strict IBCS.
- Capture interpolation, missing-period treatment and axis domains, including
  above-target values. Verify badges and labels render real values in the
  metric's units; a headline is not necessarily the average of point labels.
- Prefer an existing semantic Month column for monthly categories. Inspect its
  type, values and sort metadata; padded "01"-"12" sort chronologically, names
  need month-number ordering. For multi-year scopes use year context or an
  existing year-month field so different years' January values are not merged.
- Verify the rendered line and unchanged headline under the same filters.
  In particular, adding a monthly axis must not turn a ratio-of-totals headline
  into a sum or simple average of monthly ratios. Saved encoding alone does
  not establish correct rendering or business semantics.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

| | Split | Overlay |
|---|---|---|
| `kpiControls.layout` / `preset` | 4 / 1 | 1 / 0 |
| `gridLayout` items | one `text` | `chart` and `text` |
| Chart area | renderer fills the space the text item leaves (text narrower than `coreContainer`) | you position both; the chart fills the card under the text |

- Both shapes come from saved native cards [saved]. Whether a Split card
  without a `chart` item draws the chart is unresolved; the verified builds
  above keep one [open].
- The companion Split description sizes `coreContainer`/`gridContainer` to
  the full card, while `KPI-CARD-01` uses the card size minus 25px; that
  target guidance wins [open].
- Chart item: `{"type":"chart","isHidden":false}` in decoded
  `kpiControls.gridLayout[]` [saved].
- Some axis-bearing AREA-template cards save only text items [saved]; do not
  silently add a chart to such a card.
- Chart-bearing templates: `AREA`/`areaChart`, `LINE`/`lineChart`,
  `COLUMN_VERTICAL` and `COMPARATIVE_BULLET_VERTICAL`/`comparativeBullet`,
  all with `rendererType: "columnChart"` and `lockedTemplateId` equal to the
  id [saved].
- Bullet card: decoded `hiddenProperties_!!!_bulletConfig` =
  `{"actual":"AC","target":"PY","actualConfig":{…},"targetConfig":{…}}`
  (bar, line and arrow shapes and colours); copy it from a working bullet
  card [saved]. Its activation without a chart item is not isolated [open].
- `appearance.charts.chartBackground` is separate from a Filled panel fill;
  check both [saved].
- In Split the container is the whole card, so size the card itself. Decide
  whether the headline is the period total or the latest point.
- Saved axes include integer period keys and string period labels [saved];
  verify chronological order as above.
- One user-saved row trellis combines a time axis with a `LINE` template
  (`KPI-MULT-01`) [saved]; general trellis-plus-sparkline composition and
  rendering remain unverified [open].
- In Overlay the text item deliberately overlaps the chart item [saved];
  keep that overlap, while separate text items still get disjoint regions
  (`KPI-VAR-01`).
- **Sparkline colour.** Decoded `hiddenProperties_!!!_appearance` →
  `charts.measuresStyle` holds role-keyed entries (`AC`, `PY`) and
  measure-keyed entries (`"_Measures[Total Orders]"`, plus `TT`, `Ø`) [saved].
  Five cloned cards all drew their line in the measure-keyed donor colour;
  recolouring only the `AC` entry changed nothing [confirmed]. Recolouring the
  measure-keyed entry of the bound actual as well (`fillColor`, `borderColor`,
  `lineArea.fillColor/borderColor`, integer `lineThickness`) gave each card its
  own line colour [confirmed].

## Related features

- `KPI-CARD-01`
