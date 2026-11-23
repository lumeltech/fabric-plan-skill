---
id: CH-LIB-05
name: Combo charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-multi-measure-charts
---

# Combo charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Columns and lines together on shared or separate axes. Variants: Column +
line, Column + area, Column + column, Stacked column + line, Stacked column +
area and a vertical multi-axis chart with a separate y-axis per measure. One
dimension sits on the category axis with two or more measures; Series sets
each measure's chart type and y-axis, with focused axis settings per measure.

## When to use

- Volume vs rate (e.g. revenue and margin %).
- Related measures with different scales or units, such as amounts and
  quantities.
- Part-to-whole stacked columns with an overlaid trend or target line/area.
- Several same-unit series side by side (Column + column).

## UI path

Visualizations pane › Charts 100+ › Combo, then pick the variant (Vertical
Multi Axis Chart for one y-axis per measure). Put the dimension in Category
and add the measures; use
Home › Series to set each measure's chart type and axis, and Settings › Canvas
for appearance.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Capture each series type (column, line, area or stem) and its axis.
  Same-unit measures such as actual and plan quantities should share one
  comparable axis; label rate axes with percent units.
- Intelligence chart library only; never a Power BI native visual.
- Rates require confirmed normalization factors and eligible-unit or exposure
  denominators, not raw-count aggregation.
- Capture any companion data table with the series/axis settings. Avoid
  truncated table values and confirm future periods respect the date filter.
- Column + column suits series sharing one axis, unit and scale; for different
  scales use line/area overlays or the multi-axis variant (one y-axis per
  measure, each labeled with its unit).

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Combo ids -> rendererType:
  COLUMN_ADDITIONAL_MEASURE_LINE_VERTICAL,
  COLUMN_ADDITIONAL_MEASURE_COLUMN_VERTICAL,
  COLUMN_ADDITIONAL_MEASURE_AREA_VERTICAL -> "columnChart"
  STACKED_COLUMN_ADDITIONAL_MEASURE_VERTICAL,
  STACKED_COLUMN_ADDITIONAL_MEASURE_AREA_VERTICAL -> "stackedChart"
Pointer: /properties/pivotAssignments: one axis plus two or three ordered "AC"
  assignments; no secondaryAxis bucket and no groupMeasureAssignments
Pointer: hiddenProperties_!!!_measureConfig (JSON string), partial config[]:
  roles AC, AC1, AC2; type "ACTUAL" then "ADDITIONAL_ACTUAL"; chart "groupedBar"
  (column + column); yAxis "yAxis1"; order 0..n; enable, isVisible and
  chartIsVisible true
Evidence: [saved] few saved owners per id; a column + column owner had three AC.
```

- `AC1` and `AC2` are series-config aliases, not bucket ids; never create
  such buckets [saved]. Combo owners store their measures as repeated `AC`
  assignments, unlike comparison charts that plot only the first AC
  (`CH-CALC-01`) [saved].
- Do not inject the clustered measure-group mode (`CH-SPLIT-01`) into a combo
  [saved]. Each series' drawing type comes from the native preset, not from a
  field caption [saved].
- Several series do not by themselves need a secondary axis; use the
  multi-axis family (`VA` buckets, `CH-MULTI-01`) only when its template is
  the active one.
- Series-to-drawing mapping, secondary-scale controls, negative stacked
  values and the UI for adding or reordering a third measure are unresolved
  [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
- `CH-DISP-01`
- `CH-ANLY-02`
