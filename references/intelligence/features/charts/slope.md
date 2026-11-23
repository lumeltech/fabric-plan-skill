---
id: CH-LIB-22
name: Slope graphs
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/visualization-library/slope-graph
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/visualization-library
---

# Slope graphs

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Connects values across comparison points for each member. Two-point change
is the common case; screenshots also present three and four axes, requiring
capture of the actual native bindings and scales.

## When to use

- Before/after comparisons.
- Multi-period or ordered-horizon profiles with explicit units and scale policy.

## UI path

Visualizations pane › Charts 100+ › Special Charts › Slope graph. First-party
docs assign the
compared members to Category, a measure to Actual(s), and the comparison
dimension to Axis. Settings › Canvas › Line color includes Individual;
each unique Axis value creates a vertical axis. Marker/Label controls use
trend colors by default; clear Use trend color for custom colors. Capture the
native mapping for separate PY/AC measures rather than guessing assignments.
The guide does not establish a multi-point trend baseline, marker-shape
controls, interpolation settings or independent-axis switches.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: two-point PY/AC member lines with labeled endpoints and
         green/red/gray line treatments.
Native family, scenario bindings, axis scale and color settings: not captured.
Visible: three/four-axis variants with independent ranges, straight/curved
         connectors, circle/diamond markers, endpoint labels, category colors
         and tooltip.
Multi-axis bindings, marker/style switches and native settings: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- Independent axis domains can make equal values appear sloped and increases
  appear downward. Calculate changes from bound values; prefer shared domains
  for direct absolute comparisons.
- Use the existing [parallel-coordinate guidance](parallel-coordinates.md) for
  profile semantics, not as proof that this chart uses that native family.
- Straight/smooth connectors, contextual versus emphasized series and marker
  shapes have no captured saved switches. Trend direction, individual color,
  profile emphasis, business favorability and interactive selection differ;
  capture the baseline for multi-point trend colors.
- Curves do not establish intermediate measurements or forecasts; test missing
  points, overlap, equal endpoints and label/tooltip identity.
- Percentage horizons require cohort/denominator definitions; scores above
  100 must not automatically be formatted as percentages.
- Resolve the bound measure before naming the chart; a panel title can name a
  different measure. Use compatible units/domains and keep endpoints visible;
  an increase is not automatically an improvement in quality.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "SLOPE_GRAPH"
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"stackedChart"
Pointer: /properties/pivotAssignments (observed roles include a stack dimension)
Pointer: /properties/visualState/hiddenProperties_!!!_appearance; decoded path
         charts.slopegraph
Evidence: [saved] one saved slope-graph owner; slope keys not isolated.
```

- Slope-styled charts with three or more axes can be `PARALLEL_COORDINATES`
  owners carrying sibling `charts.slopegraph` state; check the owner's
  chartType before applying this feature's guidance [saved].
- On those owners `charts.slopegraph` holds `colorType: "trends"`, `topNTrend`,
  `connector.markerAsConnector`, `connector.markerTrendColor` and
  `seriesLabelTrendColor` [saved]. Whether these store the documented trend
  color and marker/label settings on a `SLOPE_GRAPH` owner is unresolved
  [open].
- How the documented Category, Actual(s) and Axis wells map to saved buckets,
  including the stack role, and which point is the baseline are unresolved
  [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
- `CH-TIP-01`
- `CH-LIB-23`
