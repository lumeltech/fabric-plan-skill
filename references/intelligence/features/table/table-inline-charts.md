---
id: TB-CHART-01
name: Inline charts and blended measures in tables
area: table
category: Table
status: IS-Confirmed
encoding: unverified
visual: Table
sources:
---

# Inline charts and blended measures in tables

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Sparklines, bars, and blended measures inside table cells. A measure column
can render as an inline win-loss, lollipop or waterfall chart. Canvas options
set the fill pattern (solid, hatched, outlined), positive/negative colours,
bar padding and flip; data labels can be hidden, overlap the bar and show the
value, % of total or both. Blend combines related measures into one titled
column, laid out horizontally or vertically with padding.

## When to use

- Compact comparison tables.
- Variance columns that read faster as bars or waterfalls than as numbers.
- Pairing two related measures, such as absolute and relative variance, in
  one column to save width.

## UI path

Table › Inline charts. Select a measure column and choose the chart type;
select the chart column › Configure for Canvas and Data label settings; the
1.2 (number) button reverts the column to values. The table's Blend button
opens a side pane for Title, Measure 1/2, Blend direction and Padding.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Blending combines existing measures within one table column; it is not
  cross-module or cross-source blending.
- Base measures stay visible after blending; hide them from the column
  gripper or the measure series configuration to avoid duplicates.
- Bar padding defaults to 0 and labels sit beside bars unless Bar overlap is
  on. Reset Canvas discards custom inline-chart settings.
- Grand-total and variance grand-total rows can also render charts; switch
  these off in the table canvas settings to keep totals numeric.
- Fill patterns use IBCS notation (solid, hatched, outlined); align them with
  the scenario styling used elsewhere in the report.

## Related features

- `TB-TABLE-01`
