---
id: MX-CHART-04
name: Pin and circular charts in cells
area: matrix
category: In-cell charts
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
---

# Pin and circular charts in cells

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Pin (lollipop), bar, and circular charts drawn per row in the selected measure
column(s). Pins: Simple, Bar Colored or Marker Colored lollipop. Bars: Solid,
Colored, Invert-colored, Range (min–max) or Square Area. Circular: a pie or
donut per row, sliced across the selected measures. The Customize tab sets
axes, reference lines/bands, data labels, colours and scaling; pins add
outliers, fill patterns and marker type/size.

## When to use

- Compact comparison per row.
- Value-focused comparisons where bar length matters less (pins).
- Per-row ranges or rating bands (range bars, comparison bands).
- Each row's mix across a few measures (pie or donut).

## UI path

Select the measure column(s) › Matrix toolbar: Home › Chart section › Pin chart
or Bar chart drop-down; Pie and Donut are listed under the Bullet chart
drop-down › Customize tab. Customize › Remove chart deletes the chart.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Circular charts show no data labels by default; turn on Show Label.
  Appearance sets a colour per measure slice.
- Measure scaling defaults to Universal (one min/max across all measures);
  choose Individual when the measures differ greatly in magnitude.
- Bar axis config adds Row level scaling (Universal or By level). Percentage
  labels scale to the grand total (Universal) or parent (By level) and need a
  row hierarchy.
- Reference lines sit at Average, Median, Standard deviation, Mid value or a
  Constant, in front of or behind the data; several can be added and toggled
  off. Reference bands start at Min, Zero or a Constant.
- Pin outliers flag values beyond Negative/Positive or Min/Max thresholds;
  comparison bands (Solid bar only) rate values by value or percentage ranges.
- Auto fit column options do not resize columns that hold charts.
- Outlined and hatched fill patterns follow IBCS notation; IBCS remains opt-in.

## Related features

- `MX-CHART-01`
