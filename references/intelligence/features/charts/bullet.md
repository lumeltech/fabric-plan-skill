---
id: CH-LIB-08
name: Bullet charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Bullet charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Value versus a target marker, optionally with comparison values or qualitative
bands. Screenshot evidence covers bar/marker and segmented-background
presentations, not threshold semantics or native chart-family IDs.

## When to use

- Target attainment.

## UI path

Visualizations pane › Charts 100+ › Bullet, then pick the variant; IBCS
bullets are also listed under the IBCS filter. Card ownership and the chart
type of comparison panels are not established by screenshots.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: AC bar with comparison bars, lines, ticks or triangles, with or
         without legends; optional gray background bands.
Exact chart family, card ownership, qualitative bands and settings: not captured.
Band definitions, native enum and marker/range settings: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Capture each comparison series and marker identity (PY, Target, Budget or
  other), scale and ownership. Marker color or shape is not a universal
  scenario code, and a gray bar may be a scenario such as PY, not a band.
- Capture tick and guide-line bindings independently; a target caption does
  not prove they share one target, a qualitative band or a bullet template.
- Intelligence chart library only; never a Power BI native visual.
- Comparison presentation is not a verified bullet enum. Capture native
  ownership and bindings before authoring.
- Align AC/PY/Budget units and domain within each graphic. Verify budget
  direction, missing/out-of-range targets and exact target-value access.
- Capture numeric band thresholds before assigning qualitative labels; never
  infer boundaries from band widths or reuse another chart's role mapping.
  Keep all markers visible outside the bands and verify within-panel scales.
- Show attainment above 100% and its markers without silently clipping them.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Ids, all rendererType "columnChart": IBCS_BULLET_VERTICAL,
  COMPARATIVE_BULLET_HORIZONTAL, XVIZ_BULLET_HORIZONTAL,
  QUALITATIVE_BULLET_VERTICAL, CONDITIONAL_BAR_VERTICAL,
  CONDITIONAL_BAR_HORIZONTAL
Pointer: /properties/visualState/hiddenProperties_!!!_bulletConfig (JSON string)
Decoded keys (partial): actual "AC", target "PY", additionalTarget "",
  actualConfig.type "bar", targetConfig.type "line", showVarianceBar (true in
  one variant, false in another), varianceBarPosition "outside",
  targetIndicator false, targetAchieved true; nested actual, target,
  additional-target, statistical, progress, style and variance settings
bulletComparisonBand: enable true, dynamic false, showInLegend false,
  basedOn "maxValue", noOfBands 3, flip false, divergingColors false,
  gradientColors false; ranges kept in saved order
Pointer: hiddenProperties_!!!_measureConfig: AC and PY entries with chart
  "bulletChart", type "ACTUAL", yAxis "yAxis1", order 0 and 1; absolute and
  relative variance entries disabled and chart-hidden
Evidence: [saved] few saved owners per id; not isolated by a before/after capture.
```

- Roles seen: `axis`, `AC`, `PY` and optional `PL`; one owner binds several
  AC/PY measures without an axis, another two axis levels [saved]. Existing
  model measures carry `columnType: "Measure"` with no `aggregationType`;
  never swap them for summed columns [saved].
- An empty `additionalTarget` is not a bound third measure, even when
  additional-target styling remains [saved]. Stored `targetAchieved` is not a
  calculated business result; validate attainment separately [saved].
- "Conditional" in a template id does not prove CF rules exist; the inspected
  rule arrays were empty [saved]. An enabled band configuration does not
  prove visible bands or their scale [open].
- An IBCS-named template is no reason to apply IBCS notation; IBCS stays
  opt-in (`CH-IBCS-01`).
- Band boundaries and visibility, target-achieved behavior, variance polarity
  and placement variants are unresolved [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
