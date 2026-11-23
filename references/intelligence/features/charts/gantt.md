---
id: CH-LIB-28
name: Gantt charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/plan-projects-with-gantt-charts
---

# Gantt charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Timeline with tasks, milestones, connectors, resources, zoom, holidays.

## When to use

- Project plans.

## UI path

Visualizations pane › **Gantt**, a top-level visual rather than a Charts 100+
chart type. The first-party guide
documents these controls (native storage still requires capture):

| Surface | Documented controls |
|---|---|
| Hierarchy | Ordered dimensions in **Task**; drill-down icon expands subtasks |
| Intervals | **Start Date**, **End Date** data wells |
| Completion | Completion measure in **Progress** |
| Events | Measures identifying milestones in **Milestone** |
| Links | Dependency field in **Connect to** |
| References | **References > Analytics > Add new reference**; Today/custom dates or date ranges, label and offset |
| Bar style | **Gantt Options > Data colors**; fill for pending and track for completed segments, parent/child colors, styles and borders |
| Connectors | **Connector** section for line/arrow colors, style and thickness |
| Headers | **Gantt Options > Timeline** for each level's header/date format, colors and padding |
| Grid | **Gantt Options > Grid** for fonts/background and grid-line color/thickness |
| Columns | **Gantt Options > Columns** for task/subtask titles, **Actual duration** and Hours/Days/Weeks/Months/Years units |
| Zoom | **Gantt Options > General > Zoom Option > Button**; **Settings > Zoom levels > Enabled**, levels and intervals |
| Milestone style | **Gantt > Milestones**, color/icon and **Icon configuration > Individual** for separate milestone fields |
| Labels | **Settings > Data Labels**, inside/outside position, font/background and offset |

Documented milestone custom-icon upload is an option, not a requirement to
generate images. Exact baseline bindings, dependency types/lags, progress
rollup and extra-column storage are not established by this guide. A holiday
reference line is not proof that working-duration arithmetic excludes it.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: task hierarchy, extra task-grid columns, timeline bars, outlined or
         patterned companion bars, progress labels, date-time intervals,
         dependencies, milestones, reference line, multi-level scales and zoom.
Exact task/date/baseline/progress settings and dependency links: not captured.
Documentation establishes UI controls, not JSON keys or saved settings.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Intelligence chart library only; never a Power BI native visual. Reuse the
  analytical contract, not domain-specific layouts or colors.
- Bind stable task, parent and predecessor IDs, not display names; capture
  link types/lag support and diagnose cycles/orphans. Connectors and legends
  do not prove edges, milestones, scheduling, critical path or leveling.
- Capture start/end dates, bar meanings, progress units and status rules.
  Define whether a date selection filters by task date, interval overlap or
  intentional history; the timeline can extend outside it.
- Capture zoom bounds, header formats (week numbers with year), label
  offsets, reference dates and calendar/timezone behavior. A last-checked
  caption does not verify refresh or a live Today line.
- Parent progress cells above 100% can be sums of child percentages while bars
  show weighted completion. Define source scale and approved weighting; align
  grid/bar semantics rather than summing percentages or clamping the result.
- Separate working duration, elapsed phase span, effort and crew capacity.
  Zero-day milestones differ from missing actual dates; patterned companion
  bars do not independently establish planned/actual/baseline field roles.
- Do not borrow reporting Matrix hierarchy, totals or icon keys for the Gantt
  grid. Capture native ownership, extra columns and each aggregate rule;
  never persist personal assignee names in reusable sample fragments.
- Status, phase and risk colors may be independent. Approved or Complete
  labels are not operational or regulatory authorization; a Gantt view grants
  no right to edit tasks or Planning data.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "GANTT_CHART"
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: id:"GANTT_CHART"; rendererType:"ganttChart"; chartOrientation:"vertical"
Pointer: /properties/visualState/hiddenProperties_!!!_chartsMode (JSON string)
Decoded keys: visualMode:"GANTT"; prevVisualMode:"GANTT"
State groups at /properties/visualState/hiddenProperties_!!!_<group>:
  ganttChartOptions, ganttDataLabel, ganttDisplayColumns, ganttDynamicMarker,
  ganttMarkers, ganttMilestoneOptions, ganttTooltip, ganttZoomLevel, cfProps
Decoded ganttChartOptions (partial): {"chartType":0,"durationUnitType":"day",
  "inclusiveEndDate":false,"schedulingType":"none","renderAsOverlappingBar":true}
Other saved Gantt state (preserve in place): rowHeight, dataFormat:"DD-MM-YYYY",
  connector, criticalPathMeta, effortMeta, plannedBarGap, dataGrid, gridStyle,
  timeLineMeta, timelineRange{startData, endDate}, zoomMeta, padding, scrollbar
Observed buckets: axis (task/resource levels, String Grouping); startDate,
  endDate, plannedStartDate, plannedEndDate (DateTime Measure); progress and
  displayMeasure (Int64 Measure, sum); displayCategory (Measure-role String or
  DateTime); milestone (repeatable DateTime); milestoneName (String);
  connectTo, connectorType (String Measure, first)
Partial assignment: {"bucketId":"plannedStartDate","columnType":"Column",
  "dataType":"DateTime","dataRoleType":"Measure","aggregationType":"earliest"}
Evidence: [saved] companion-library saved owners; not isolated or re-rendered.
```

- Group boundaries vary by owner: `ganttChartOptions` and `ganttDisplayColumns`
  can be objects or JSON strings and `ganttMarkers` an array or JSON string,
  while the other groups were JSON strings [saved]. Earlier all-string
  examples are not a rule to stringify every group; preserve each owner's
  boundary and never deploy expanded analysis objects [confirmed].
- Never invent `ganttConfig` or `ganttChart` groups. Dormant Gantt groups also
  persist on non-Gantt Analytics owners; only the `GANTT_CHART` template
  identifies a Gantt [saved].
- Match a Gantt donor by template, renderer, `ganttChartOptions.chartType`,
  typed role cardinality and aggregation; a different task/resource or field
  contract is not a baseline.
- `ganttChartOptions.chartType` 0 appeared on task-oriented owners and 1 on a
  resource-oriented owner; that is an association, not an enum mapping
  [saved].
- Some owners omit `schedulingType`, `inclusiveEndDate`,
  `renderAsOverlappingBar`, `criticalPathMeta`, `effortMeta` and
  `plannedBarGap`; absence is not null or false, so never inject them [saved].
  Retained scheduling fields beside `schedulingType: "none"` do not prove
  active scheduling [open].
- No saved Gantt owner binds AC/PY/PL/FC scenario slots; do not force scenario
  roles onto the chart [saved].
- Date aggregation differed between owners (later ones used `"earliest"`); a
  date shown through `displayCategory` does not replace the timeline date
  roles [saved].
- Bucket ids track the documented Task, Start Date, End Date, Progress,
  Milestone and Connect to wells by name; that mapping is not isolated [open].
- `ganttDisplayColumns` keeps `taskName`, `rowNumbering`, `actualDuration` and
  `plannedDuration` apart from field-keyed columns whose keys mix
  aggregation-prefixed, bracket and function-style spellings [saved]. Alias
  precedence is unresolved; never prune or rewrite those keys [open].
- `allowMilestoneFromData` was false where milestone fields were bound and
  true where they were not; it is not a milestone visibility test [saved].
  Same-date milestones were on, and same-planned-date and null-as-milestone
  options off, in every inspected owner [saved].
- `isConnectorHidden: false` and connector styling persist without
  `connectTo`/`connectorType` bindings; styling does not prove dependencies
  [saved].
- Tooltip entries for task, start, end, planned dates and progress are
  enabled, and `progressBarDisplay` is `"bar"`, even when planned or progress
  fields are unbound; check bindings before claiming those values show [saved].
- Data labels were saved shown, adaptive and overlap-allowed in every
  inspected owner [saved].
- `ganttZoomLevel` stores `zoomLevelEnabled`, `threshold` and `zoomLevel` as
  an array of level arrays, not one time unit [saved]:

```text
{"zoomLevelEnabled":true,"zoomLevel":[[{"type":"YEAR","interval":1,"level":"top"},
 {"type":"QUARTER","interval":1,"level":"mid","format":""},
 {"type":"MONTH","interval":1,"level":"low","format":"MMM"}]],"threshold":50}
```

- Keep the exported `timelineRange.startData` spelling beside `endDate`; do
  not rename it [saved].
- A `ganttMarkers` entry saves `enabled`, numeric `dateType`, `date1Type` and
  `date2Type` selectors, `showLine` and `showText` [saved]. Clock and timezone
  behavior are unresolved [open].
- Analytics `hiddenProperties_!!!_cfProps.rules` entries carry `ganttApplyTo`
  label/value pairs (Datagrid 1, Timeline Bar 2 and Status flag 4 seen); this
  is not a complete enum or a Matrix `cfProps`/`jet_cfProps` collection, and
  populated but unselected `ganttTimelineOptions` do not activate targets
  [saved]. Partial rule:
  `{"enabled":true,"ruleType":"rule","ganttApplyTo":[{"label":"Datagrid","value":1}]}`.
- Unresolved: chartType enum labels, end-date inclusion (the companion's
  one-setting test was deferred), resource overlap, critical path, dependency
  semantics, date-selector meanings, progress scaling and conditional-format
  rendering [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
