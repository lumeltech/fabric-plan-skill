---
id: CH-LIB-33
name: Dumbbell, arrow and dot plots
area: charts
category: Chart library
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
---

# Dumbbell, arrow and dot plots

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Point-comparison storytelling charts drawn per category without bars: a
dumbbell joins two values, an arrow plot points from one value to another and
a dot plot places several values on one shared scale. Each is a separate
native template from the range, pin and slope charts.

## When to use

- Gap between two scenarios or measures per category (dumbbell).
- Direction and size of change from a reference to a current value (arrow).
- Several scenario values per category on one common scale (dot plot).
- Choose from the analytical question (gap, change, interval, rank), not the
  gallery heading.

## UI path

Visualizations pane › Charts 100+ › Special Charts (storytelling charts; the
Special filter also lists them), or type dumbbell, arrow or dot in Search
Charts. The exact variant labels, data wells and settings paths were not
captured; confirm them in the UI before giving step-by-step instructions.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/chartType = "DUMBBELL_HORIZONTAL" | "ARROW_PLOT_HORIZONTAL" |
         "DOT_PLOT_VERTICAL"; visualType 50 (ANALYTICS_PLUS)
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"columnChart" (all three)
Pointer: /properties/pivotAssignments
Observed buckets: dumbbell and arrow = axis, AC, PY; the dot plot adds PL
Evidence: [saved] one companion-library saved owner per template; not isolated
          by a before/after change, re-published or re-rendered.
```

Tags: [saved] saved exports, [confirmed] user-confirmed, [open] unresolved.
Copy the complete saved owner of the same template and rebind it; the
fragment above is not a visual. Follow `core/native-samples.md` before writing
this feature into a definition.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- The shared `columnChart` renderer also draws column, range, pin and box-plot
  templates; preserve the template id rather than classifying by renderer
  [saved].
- Slot names do not establish which value is the start, end, arrow head or
  emphasized dot; capture that mapping before labeling endpoints [open].
- A stored PY role need not hold prior year; in other saved charts it held
  plan or forecast measures [saved]. Bind and title each point's measure
  explicitly.
- Paired or connected points are not uncertainty intervals, min/max
  observations or a time series; use the range chart for a defined interval.
- Put all points of a row on one domain and unit. Keep overlapping points'
  identities and values readable, check zero handling and baseline direction,
  and judge favorability per measure, not from arrow direction alone.
- Label, connector, marker and sort settings were not recorded; never infer
  them from the template name [open].

## Related features

- `CH-LIB-19` — range plots share the renderer and AC/PY roles.
- `CH-LIB-24` — lollipop/pin single-value comparison.
