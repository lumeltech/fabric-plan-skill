---
id: CH-LIB-23
name: Parallel coordinates
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Parallel coordinates

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Profiles connected across parallel axes, with each axis representing a
measure or a category/period value. Capture the native binding arrangement.

## When to use

- Multi-measure profiles.

## UI path

Visualizations pane › Charts 100+; type parallel in Search Charts (its
category was not captured).

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: category/period axes, connecting profiles, endpoint labels,
         differing axis ranges and one emphasized color profile.
Exact axis bindings, scale mode and highlight behavior: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Geometry alone does not establish this family's native identifier; a
  multi-axis slope graph can look the same. Capture bindings before choosing
  the engine, and do not equate it with a combo multi-axis chart template.
- Record axis domains and normalization. Shared monotonic scales within an
  axis preserve member order, but geometric slope across differently scaled
  axes does not measure value change, direction or magnitude.
- When axes hold unlike measures (count, amount, rate), show each unit and
  domain; slope across them is not growth. Leaders may differ per axis, so a
  "best member" claim needs explicit criteria, not the most prominent line.
- Intelligence chart library only; never a Power BI native visual.
- Distinguish absolute changes from profiles. Use a shared-scale line chart
  for absolute time trends unless parallel-profile comparison is explicitly
  required.
- A highlighted profile does not prove click/hover selection or brushing.
  Test the interaction; screenshot presentation does not verify its encoding.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "PARALLEL_COORDINATES" (matches the decoded template id)
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: chartType and rendererType:"stackedChart"; vertical orientation
Pointer: /properties/pivotAssignments (one String Grouping axis; two to six AC
         measure fields in contiguous order, sum aggregation where recorded)
JSON strings at /properties/visualState/hiddenProperties_!!!_<group>: appearance,
  slopeRanking, measureConfig, columnFieldsMapping, dataLabel, yAxis, cfProps,
  annotation; xAxis is an object on some owners and a JSON string on others
Decoded measureConfig: {"config":[{"role":"AC","enable":false,"isVisible":true,
  "chartIsVisible":true,"type":"ACTUAL","order":0,"isTrellis":false}]}
Decoded appearance charts.parallelCoordinates: lineStyle:"linear" | "natural";
  marker{enabled, markerSize}; colorBy:"trends" | "individual"; globalLineWidth
Decoded yAxis.yAxis1: {"scaleType":"linear","parallelCoordinateScaleType":"individual",
  "customMinMax":{"enabled":true,"customMin":null,"customMax":null}}
Evidence: [saved] companion-library saved owners; not isolated or re-rendered.
```

- Slope-oriented titles do not make these owners `SLOPE_GRAPH` or stacked
  bars; keep the template identity [saved].
- One role-level `measureConfig` entry coexists with several AC fields; do not
  add one entry per field or merge `enable`, `isVisible` and `chartIsVisible`
  [saved]. Their combined UI meaning is unresolved [open].
- Sibling `appearance.charts.slopegraph` state persists (`colorType:
  "trends"`, enabled `topNTrend`, `connector.markerAsConnector`,
  `connector.markerTrendColor`, `seriesLabelTrendColor`,
  `groupSelection.selectedGroups`) and can disagree with
  `parallelCoordinates.colorBy` [saved]. Precedence and active trend coloring
  are unresolved [open].
- `selectedGroups` holds integer keys with label/value captions, and some
  captions match no current AC field; preserve keys, captions, fields and
  modes together instead of rewriting them [confirmed].
- Decoded `slopeRanking` is separate from `topNTrend`, for example
  `{"enabled":true,"type":"top","filterBy":"variance","selectionType":"items","showOthers":false}`.
  `filterBy` can instead hold a field caption (column or custom name) rather
  than the field id, and `topNPercent` persists while `selectionType` is
  `"items"` [saved].
- Explicit `variableId: null` and an absent key are different saved states;
  preserve whichever the owner has [saved].
- `yAxis.multipleYAxis.enabled` (false) is not a substitute for
  `parallelCoordinateScaleType`; enabled custom bounds with null endpoints are
  not concrete limits [saved].
- `dataLabel.labelStyle.default` keeps `enabled`, `display: "auto"` and
  `slopeDisplay: "none"` as default flags, not proof of visible labels [saved].
- Dormant funnel, pie and other family branches, surplus per-measure style
  entries, empty Analytics `cfProps` rule arrays and empty annotation records
  do not identify the chart, add bindings or prove rules or notes [saved].
- Ranking UI labels, rank membership, independent scales and sibling trend
  controls are unresolved; the companion's ranking experiment was deferred
  [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
