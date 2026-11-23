---
id: CH-CF-01
name: Chart conditional formatting and comparison bands
area: charts
category: Chart formatting
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-conditional-formatting/showcase-data-points-in-charts
---

# Chart conditional formatting and comparison bands

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Colours points by rules, scales, positive/negative, and comparison bands.

## When to use

- Highlight adverse points.

## UI path

Chart › Conditional formatting.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Live default-chart export: no conditional-formatting group. appearance
`highlightColor` and commonSettings highlight keys style selection, not rules.
Rule storage: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Keep CF rules distinct from static Individual colors, series colors, trend
  colors, selection and min/max highlights. Capture which mechanism applies
  and its native owner; appearance alone does not prove a CF rule.
- Parent-hue styling in hierarchical charts can color the same member
  differently under different parents. Treat it as branch styling, not proof
  of status CF, favorability or an automatic inheritance switch.
- Bands or fills inside KPI panels, cards or Gantt bars do not prove chart CF
  activation. Capture native ownership, thresholds, units and
  inclusive/exclusive bounds; keep target-range fills separate from point color.
- Extrema emphasis (such as green maximum, red minimum) is not business
  favorability. Define rule intent, ties and missing-value handling.
- Define favorability per metric and entity, separately from numeric
  direction, with effective dates. Never treat missing data as favorable.
- For trend coloring across multiple axes, define whether the trend compares
  adjacent points, outer endpoints or another baseline.
- When phase, status, risk and progress are colored independently, capture
  each mapping; a completed-looking bar must not imply approval or clearance.
- Test exact threshold values and values outside the displayed range. Band
  colors and headline status may use different rules; reconcile them or
  explicitly distinguish them.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_cfProps (JSON string)
Decoded: rules[]; targets in applyToOptions, basedOn and nested conditions;
  numeric line/area application flags lineApplyTo and areaApplyTo (a saved
  rule had both at 2)
Evidence: [saved] saved line and bar owners.
```

- Resolve every rule target before reusing a donor: an enabled rule can
  target a measure that is not bound to the chart, and JSON or API acceptance
  does not validate it [saved]. Remap or remove obsolete rules only within
  the authorized change.
- An added empty `rules` array is not a created rule, and a "conditional"
  template id (`CONDITIONAL_BAR_*`) does not prove that rules exist [saved].
- Comparison bands: saved chart owners carry a
  `hiddenProperties_!!!_comparisonBand` group, while family bands sit in
  `bulletConfig.bulletComparisonBand` (`CH-LIB-08`) and
  `gaugeConfig.primary.comparisonGaugeBand` (`CH-LIB-12`) [saved].
- What `lineApplyTo`/`areaApplyTo` values mean, and how an inherited
  off-target rule renders, are unresolved [open].
- Dynamic titles and CF need their own active, tested examples before they
  are generalized from one chart.

## Related features

- None.
