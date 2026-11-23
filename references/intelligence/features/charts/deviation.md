---
id: CH-DEV-01
name: Deviation and variance display
area: charts
category: Chart settings
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-a-dashboard
---

# Deviation and variance display

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Integrated variance (absolute/relative) against a comparison measure.

## When to use

- Actual vs plan/PY charts.

## UI path

Chart › Deviation.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/visualState/hiddenProperties_!!!_appearance (JSON string)
Decoded path: charts.variance (varianceDisplay, switchComparison, measureCombination,
              varianceCustomization, varianceLineSize, invertColor)
Pointer: /properties/visualState/hiddenProperties_!!!_commonSettings (JSON string)
Decoded keys include showCategoryDeviation and categoryDeviationLabel
```

Copy the whole settings groups from the matching native Fabric Plan visual;
individual switches are not isolated. Integrated scenario variance is distinct
from a start/end bracket: use `CH-DEV-02` for endpoint deviation.

## Constraints

- Mix shares and cumulative percentages are not integrated variance. A gap
  between shares with separate denominators is a percentage-point difference;
  resolve whether the requested comparison is absolute, percentage-point or
  relative.
- Bind each comparison baseline, unit, denominator and favorability per
  measure. A negative change can be favorable, and a low-volume member can
  still show positive growth.
- For layered displays (absolute segments, relative pins, bridges), capture
  each tier's scenario/date roles and denominator. Never sum ratios or
  non-additive counts as though they were additive contributions.
- Markers beside bars (such as triangles) have no established meaning until
  their bindings and legend are captured; do not assume a target, prior
  period or the same encoding as elsewhere.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Decoded appearance also stores variance colors at `charts.variance.colors`,
  `charts.waterfall.breakdownVariance.colors` and `charts.slopegraph.trendColor`
  [saved]. A historical theme switch changed these colors while the
  `measureConfig` variance roles stayed the same, so tier wiring is
  independent of variance coloring [saved].
- Variance tiers are `measureConfig` roles (`variancePin`, `varianceBar`)
  documented in `CH-LIB-27` [saved].
- `invertColor: false` is saved on every inspected chart, cost charts
  included [saved]. What `true` changes in rendering is unresolved [open].

## Related features

- `CH-LIB-27`
- `CH-DEV-02`
