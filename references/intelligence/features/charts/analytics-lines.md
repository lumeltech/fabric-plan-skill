---
id: CH-ANLY-01
name: Reference lines, bands, error bars, trend lines
area: charts
category: Chart analytics
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
---

# Reference lines, bands, error bars, trend lines

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Adds targets, averages, bands, error bars, trend lines, and additional series.

## When to use

- Targets on trends; scatter averages.

## UI path

Chart › Analytics.

## Definition encoding

```text
Pointer: /properties/visualState/hiddenProperties_!!!_analytics (JSON string)
Default keys: additionalSeries, connectorLine, errorBar, instanceId,
              referenceBand, referenceLine, trendLine
Earlier saved entries: referenceLine[] (enabled:true, orientation:"horizontal",
              type:"average", lineStyle:"dashed", labelText:"Avg");
              trendLine[] (enabled:true, type:"polynomial", lineStyle:"dotted")
Evidence: live export of a UI-created test Plan (default state); not isolated by
          a before/after change or re-rendered after reapplication.
```

Saved Fabric Plan settings supersede generic `visualState.analytics` guesses.
Decode/edit/re-encode the group string. Copy the full group and remap every
measure reference through field closure; stored constants/IDs are not reusable
business targets. Bands/error bars/additional series were not isolated.
A screenshot alone cannot identify trend type; read it from the saved group.

## Constraints

- A labeled average or reference value does not prove its statistic,
  weighting, filter scope or the series it applies to. Resolve each, plus
  band bounds and inclusivity, before reuse.
- Capture error-bar interval method and units before calling caps confidence
  limits, tolerances or targets; the observed `errorBar` group does not isolate
  them. Keep lower/upper bounds correct when axis direction reverses.
- A target band is not a confidence interval. Guides, bands and trend lines
  shown inside cards may be card-owned; capture the owning visual.
- Record trend type, degree and window. A smooth line does not identify the
  regression type; trend lines are descriptive, not forecasts. Rolling
  averages are measures, not trend lines.
- For crossing reference lines on scatter/bubble charts, define each
  threshold, its aggregation, label and filter recomputation; screenshots do
  not establish them.
- Gantt date references (Today, custom date, range, labels, offsets) are
  native Gantt settings; capture them separately from this chart-engine group.
  A holiday marker does not establish a working calendar, and a last-checked
  label does not prove a live date reference.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- An inherited `referenceLine[]` entry with `type: "average"` was switched off
  by saving `enabled: false`; the entry stays in the array [saved]. Use this
  to remove an overlay that does not serve the comparison; it is not a rule
  to hide every reference line.

## Related features

- None.
