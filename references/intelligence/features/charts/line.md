---
id: CH-LIB-03
name: Line charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-ibcs-formats/area-and-line-charts
---

# Line charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Trends over time with line, spline, and step styles.

## When to use

- Trends with ≤ 5 series.

## UI path

Visualizations pane › Charts 100+ › Line, then pick the variant.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/chartType = "LINE"
Pointer: /properties/pivotAssignments (axis = month field; AC = rolling measure)
Pointer: /properties/visualState/hiddenProperties_!!!_appearance (JSON string)
Integrated line (actual vs prior year): chartType "LINE_INTEGRATED" with buckets
  axis (month field), AC, PY and Tooltip; rendered as expected in a published report.
Month order: set hiddenProperties_!!!_sorting to ascending by "category" (CH-SORT-01);
  the template's "reset" default drew the months newest-first.
```

Copy the saved Fabric Plan line and companion state. Average, extrema and
endpoint-delta annotations on a rolling trend are separate features, not
implied by `LINE`. Spline/step switches remain uncaptured.

## Constraints

- Smooth connectors across independent axes do not establish `LINE`, a spline
  switch or intermediate values; capture the actual family/style. Use shared
  scales for absolute time trends; an equal-endpoint arch is not growth.
- Capture intended date-filter exceptions, such as history beyond the selected
  period, and comparison roles; neither a caption nor a shared curve shape
  proves a binding.
- Intelligence chart library only; never a Power BI native visual.
- Splines can overshoot between points; use straight segments for financial
  values and label every comparison line, such as a dashed PY.
- By default add no point markers, data labels, sparklines or analytics
  overlays to line charts; ask the user whether they want them [confirmed].
  Comparison lines stay distinguishable by style and legend.
- When titles and legends name different scenarios, resolve scenario/version
  from bindings; captions do not prove the plotted scenario. Sort periods by
  date keys, independent of value ranking.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Line-family ids -> rendererType:
  LINE, LINE_INTEGRATED, BASELINE_LINE -> "columnChart"
  CLUSTER_LINE, STACKED_LINE -> "stackedChart"
  LINE row trellis -> chartType "columnChart", rendererType
  "smallMultiplesChart", actualChartType "lineChart" (CH-MULT-01)
Evidence: [saved] saved owners; a columnChart renderer for LINE is native.
```

```text
Pointer: hiddenProperties_!!!_appearance (JSON string) -> charts.lineArea
Keys: interpolation, marker, baseline and percent styling; marker.display
  "limited" | "auto" (marker density)
Per series: charts.measuresStyle.<role>.lineArea.marker {enabled, useSeriesColor}
Grouped lines: charts.groupStyle["C0-%-<group caption>"].lineArea.borderColor
Pointer: hiddenProperties_!!!_legendSettings: legendMarkerStyle "lineAndMarkers"
Evidence: [saved] user-finished saved lines; not isolated one change at a time.
```

- A user-corrected line kept `LINE` in both `id` and `lockedTemplateId` with
  `actualChartType: "lineChart"`; check owner type, active template and lock
  together, not the title [confirmed].
- Roles seen: `axis`, `AC`, `PY`, `stack`, `row`, `Tooltip` and
  `TextCategory` [saved]. Some clustered and stacked lines group measures
  natively (`groupMeasureAssignments` with a synthetic stack; `CH-SPLIT-01`),
  and one LINE binds several ordered axis levels plus a row trellis [saved].
- Group-style keys can use short scenario captions, and older full-measure
  style entries can remain beside them [saved]. Which style map wins is
  unresolved [open].
- Match donors by actual renderer; never pool ordinary and small-multiple
  LINE owners [saved].
- An enabled PY entry in `measureConfig.config` and a legend label do not
  prove a visible comparison stroke. In a native LINE trellis, PY was enabled
  but its `appearance.charts.measuresStyle.PY.lineArea` held only an empty
  marker object; explicit styling made the comparison visible [confirmed]:

  ```text
  appearance.charts.measuresStyle.PY:
    borderColor, fillColor: <comparison color>
    lineArea: {borderColor, fillColor, lineThickness: 1.5, lineStyle: "solid",
               marker: <preserved native marker settings>}
  ```

  Merge these leaves without replacing other native line/marker settings.
  A medium gray was readable on a light canvas; color and thickness remain
  design choices. Preserve the actual-series style, bindings and renderer,
  and check every trellis panel after refresh. This is a confirmed trellis
  variant, not proof of all line-family or grouped-style precedence.
- Text roles do not change numeric aggregation [saved]. A saved
  `TextCategory` or `Tooltip` binding does not prove that its text renders
  [open].
- Saved lines can also take numeric series from an embedded Planning visual
  (`sourceType: "Visual"`, `customSource: true`) or text from InfoBridge
  outputs [saved]; such bindings are not enabled in this release.
- Interpolation, missing-date gaps, baseline behavior and normalization are
  uncaptured [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
