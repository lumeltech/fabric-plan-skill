---
id: CH-LIB-19
name: Range charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Range charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Min–max or interval per category. The documented purpose is showing data
variability by comparing minimum and maximum values across categories; range
charts are grouped with the storytelling charts. Number, legend, data label,
small-multiple, conditional formatting, sorting and Top N ranking settings
apply.

## When to use

- Variability bands.
- Comparing the minimum-to-maximum spread across categories.

## UI path

Visualizations pane › Charts 100+ › Special Charts, then pick the range chart;
range charts are listed with the storytelling charts.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Paired or connected dots (dumbbells) comparing scenarios or categories on a
  shared axis do not establish a native Range enum, interval statistic,
  min/max semantics or confidence interval. Capture the actual family.
- Capture each measure/scenario identity, shared domain and card ownership.
  Preserve identities and exact values when points overlap, and avoid
  truncated series legends.
- Connected markers across categories are not uncertainty limits, min/max
  observations or a time series.
- User confirmation includes interval/min-max availability. These variants
  are not established by screenshot presentation, and confirmation is not
  native encoding evidence for a connected-dot display.
- Intelligence chart library only; never a Power BI native visual.
- Documentation states the purpose but not the data-role setup; capture which
  bound measures supply the minimum and maximum before authoring.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "RANGE_PLOT_VERTICAL"
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"columnChart"
Pointer: /properties/pivotAssignments (axis, AC, PY)
Evidence: [saved] one saved range-plot owner; range settings not recorded.
```

- Which of AC and PY supplies the minimum or maximum endpoint is unresolved
  [open].
- `DUMBBELL_HORIZONTAL` and `ARROW_PLOT_HORIZONTAL` owners share this renderer
  and the AC/PY roles; capture a connected-dot chart's template id before
  calling it a range chart [saved].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
