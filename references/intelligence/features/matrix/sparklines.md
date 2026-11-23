---
id: MX-CHART-02
name: Sparklines and trend charts in cells
area: matrix
category: In-cell charts
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
---

# Sparklines and trend charts in cells

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Small trend lines per row with markers and bands.

## When to use

- Trend context next to the current value.

## UI path

Insert › Chart › Sparkline.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Presentation evidence: screenshots only.
Visible: trend lines per row with colored point markers.
Exact trend bindings, marker rules and settings: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Screenshots confirm only the visible row-trend presentation, not bands or
  every sparkline option.
- Define date grain, missing periods, common versus row-local scale, parent
  aggregation and marker semantics. Do not infer extrema from marker color.
- For latest-period or minimum highlights in a trend column, capture chart
  type, highlight rules, measure binding and scale independently.

## Related features

- `MX-CHART-01`
