---
id: MX-CHART-01
name: In-cell charts (variance bars, bullets, sparklines)
area: matrix
category: In-cell charts
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
---

# In-cell charts (variance bars, bullets, sparklines)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Embeds charts in columns: change/deviation bars, bullets, clustered bars, bars, pins, progress, data bars.

## When to use

- Variance tables with visual magnitude.
- Target attainment per row.

## UI path

Insert › Chart.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.chart_config
UI-saved in-cell bar on a measure column: {"<measure id>": {chart_type:"Bar",
  sub_chart_type:"BarInitial", formula_type:"CURR", custom_outlier:null}} with
  formatConfig.measure codes "25":"BarInitial" and "26":"<colour>" (MX-NUM-01).
Variance bars, bullets and percentage markers: screenshots only; not captured.
```

The bar encoding comes from one user editor save. Capture the other chart
types before writing them.

## Constraints

- A visible variance presentation does not establish every bar, bullet,
  sparkline or pin variant listed here. Capture each selected variant
  (absolute bars, relative pins, overlapping AC/PY bars) separately rather
  than assuming CF data-bar encoding.
- Aligned bars in another visual do not prove Matrix ownership or the same
  template. Capture aggregate weighting for total rows; composite KPIs must
  follow their semantic definition, not drawn bar lengths.
- Separate expense favorability from arithmetic sign and preserve the numeric
  value alongside the visual magnitude. These are not Tornado charts.
- Preserve exact values and full row labels; visible rows in a scrolling
  table do not establish exhaustive totals or a template ID.

## Related features

- `MX-CHART-02`
- `MX-VAR-01`
