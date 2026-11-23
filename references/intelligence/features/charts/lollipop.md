---
id: CH-LIB-24
name: Lollipop charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Lollipop charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Dot-and-stem bars: one stem and marker per category for the bound measures,
offered as Vertical lollipop among the Special charts. Individual marker color
sets per-point line and marker colors; Category format changes marker and line
styles. Number, legend, data label, small-multiple, conditional formatting,
sorting and Top N ranking settings apply.

## When to use

- Lighter alternative to bars.
- Rankings and comparisons of individual values, or highlighting outliers.
- Survey results and other per-category value comparisons.

## UI path

Visualizations pane › Charts 100+ › Special Charts › Vertical lollipop. Put the
dimension in Category and add the measures. Settings › Canvas › Individual
marker color and Category format
style the markers and lines.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Define whether values are totals or averages and the exposure denominator.
  Stale narrative text naming another member or date is not evidence of the
  current rank or of a fault.
- Intelligence chart library only; never a Power BI native visual.
- Stem/dot mini charts in KPI cards are insight-chart presentation, not
  evidence of the standalone lollipop chart; preserve this feature's
  native-family capture gate.
- Label every point and reconcile counts with the same status population used
  in related visuals.
- Order ordinal bands such as age groups by their bounds. Define whether
  counts mean units, orders or customers; never treat label counts as distinct
  buyers without model evidence.
- Individual marker colors are manual styling, not status or favorability;
  use conditional formatting rules for data-driven colors.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Candidate: /properties/chartType = "PIN_VERTICAL" (UI name unconfirmed)
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"columnChart"
Pointer: /properties/pivotAssignments (axis + AC)
Evidence: [saved] one saved storytelling owner; not isolated or re-rendered.
```

- Whether `PIN_VERTICAL` is the documented Vertical lollipop is unresolved;
  capture a UI-created lollipop before writing that id [open].
- `columnChart` also renders column, range, dumbbell, arrow, dot and box-plot
  templates; classify by template id, not renderer [saved].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
