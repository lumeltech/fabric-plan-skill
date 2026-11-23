---
id: MX-CF-02
name: Data bars and colour scales
area: matrix
category: Conditional formatting
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-conditional-formatting/highlight-tabular-data-with-conditional-formatting
---

# Data bars and colour scales

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Shows magnitude with in-cell bars or a colour gradient. Colour scales can
colour backgrounds, fonts, data bars, action dots or bubble charts, applied
column-wise, row-wise or table-wise and optionally based on another measure.
Scale types include Sequential, Diverging, Qualitative, Continuous variants
and Custom ranges, with built-in schemes, bands and Reverse color. Data bars
add Hide value, a min/max range, left/right alignment and +/- colours.

## When to use

- Compare magnitudes down a column.
- Heat-map a whole grid (table-wise) or each row across periods (row-wise).
- Shade one measure by the values of another measure (Based on).

## UI path

Home › Conditional formatting › Data bars / Color scale. One-click: select a
column or cell first; hovering a colour scale previews it. Custom rule:
Conditional formatting › Create Rule › Format by: Color scale › Color scale
for: background, font or data bars.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.cfProps.rules[]
  (keep jet_cfProps identical)
Colour scale (UI-saved): ruleType:"targetValue" (not "colorScale"), colorScaleApplyTo:"continuous",
  colorScaleColorFor:"background", heatMapType:"columnHeatMap", ruleFor:"child",
  targetValueType:"percent", basedOn = highlightedMeasure = bubbleBasedOn = engine measure id,
  conditions[0].basedOn/comparisonMeasure = same id,
  colorScheme {colors:[100 hex steps min→max], minColor, maxColor, middleColor, numberOfRanges:5}.
  The rule also carries default targetValues/actionTargetValues/textGroupValues/iconGroupValues.
In-cell data bar (UI-saved, MX-CHART-01): visualState.chart_config
  {"<measure id>": {chart_type:"Bar", sub_chart_type:"BarInitial", formula_type:"CURR",
   custom_outlier:null}} plus formatConfig.measure["<measure id>"] entries
  {"25":"BarInitial"} and {"26":"<bar colour>"} (last entry wins).
Evidence: user editor save on a heatmap and a variance Matrix, read back with getDefinition;
  the native heatmap donor carried the same targetValue rule.
```

Clone the complete saved rule, change only the target ids and `colorScheme`
(generate the 100-step list for a new colour pair), and keep it in both
`cfProps` and `jet_cfProps`. Authored `ruleType:"colorScale"` rules
(chart-family schema) painted nothing in a Matrix [confirmed]; a builder that
drops `targetValue` rules from a donor deletes its colour scale. Cloned scales
rendered on engine ids taken from saved Matrices (a heatmap measure, a
variance set's Δ %) but not on an extra measure whose id the builder invented;
apply such a scale in the editor and capture the saved id.

## Constraints

- One-click options are enabled only when a cell or column is selected; the
  result can then be customised as a rule.
- Rules default to Values only; set Row hierarchy levels to Totals only or
  Values and Totals before bars or colours include subtotals and totals.
- Data-bar Min/max limits bars to values inside the range. Columns holding
  positive and negative values switch to separate positive/negative colours.
- Min, max and center colours apply to the Continuous scale types; Custom
  defines value or percentage ranges that can be added, deleted or reversed.
- Number of bands defaults to 5 and updates the scheme's gradient steps.
- Auto font color (on by default) keeps text readable on background scales;
  turning it off can make values in dark cells unreadable.
- Include null decides whether null values take part in the formatting; Hide
  value shows only the bar or colour.

## Related features

- `MX-CF-01`
