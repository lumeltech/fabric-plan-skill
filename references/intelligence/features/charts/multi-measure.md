---
id: CH-MULTI-01
name: Multi-measure and multi-axis charts
area: charts
category: Chart data
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/visualization-library/multi-axis-chart
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-multi-measure-charts
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/visualization-library
---

# Multi-measure and multi-axis charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Different chart type per measure and multiple axes.

## When to use

- Measures with different units, clearly labelled.

## UI path

First-party docs: Visualizations pane › Charts 100+ › Combo › Vertical/Horizontal
Multi Axis Chart.
Assign the dimension to Category and measures to Axis; use Series for each
measure's chart type and Data Label › Value display for label selection.
Settings › Canvas › Category format controls chart/marker appearance.
Capture the resulting native bindings/settings rather than inventing keys.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Presentation evidence: screenshots only.
Visible: solid and dashed trends with separately labeled left/right axes.
Exact per-series axis assignments and settings: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Map each series to its axis and units explicitly, and capture the native
  series-to-axis mapping. Identical units do not prove identical domains or
  one saved container.
- Dual-axis appearance does not prove a specific combination-chart family.
- Independent scales can manufacture apparent agreement or correlation,
  especially for actual versus plan quantities; consider aligned panels.
- Never compare lengths of unlike measures (an amount versus units, a rate
  versus revenue) on an unlabeled common scale; label separate axes/units or
  use aligned panels.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Ids: COLUMN_ADDITIONAL_MULTIPLE_AXIS_VERTICAL and
  COLUMN_ADDITIONAL_MULTIPLE_AXIS_HORIZONTAL; chartType and rendererType
  "multipleAxisChart"; chartOrientation per id
Pointer: /properties/pivotAssignments: category axis plus value-axis buckets
  VA1..VA4 (seen: VA1-VA4 one each; two in VA1 + one in VA2; two in VA1 only)
Pointer: hiddenProperties_!!!_measureConfig (JSON string), partial config[]:
  roles VA1 and VA11 (second VA1 measure); type "MULTIPLE_AXIS_CHART";
  chart "groupedBar"; yAxis "yAxis1"; order 0; enable, isVisible and
  chartIsVisible true
Evidence: [saved] saved owners; no maximum axis count established.
```

- `VA11` is a config alias, not a bucket; never create a `VA11` bucket or
  renumber the second measure onto a new axis [saved]. A VA slot can hold
  more than one measure, and a horizontal template does not mean two axes are
  active [saved].
- Tick labels (user correction): use regular-weight x-axis tick labels,
  `hiddenProperties_!!!_xAxis.label.isBold: false`, on vertical and
  horizontal multi-axis charts alike; keep axis titles, category-group
  headers, measure-axis colors and unit formats separate [confirmed]. Check
  the flag on every matching owner, not only the one in view [confirmed].
- Optional companion default (the design system and session theme take
  precedence): regular, non-italic 10 px tick labels; number format Auto with
  one decimal, an empty suffix and the scaling unit shown in the title;
  automatic title mode [confirmed]. Keep correctly configured Millions
  scaling rather than forcing Auto [confirmed].
- Never apply one number format to every axis for consistency; mixed-unit
  axes keep independent formats [confirmed]. Data-specific axis options (a
  step of 2 on an hour axis, rotated labels) are not blanket defaults [saved].
- After rebinding, retitle the chart to the bound measures; a title naming
  other measures is a title/data mismatch to flag, not evidence of meaning.
- Axis synchronization, axis side and per-series display switching are
  unresolved [open].

## Related features

- `CH-LIB-05`
