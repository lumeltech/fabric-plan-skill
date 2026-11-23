---
id: CH-LIB-21
name: Tornado charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Tornado charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Two groups compared with mirrored bars.

## When to use

- Sensitivity or A vs B.
- Population profiles, paired criterion scores and side-specific product mix.
  Sensitivity use requires explicit baseline/input-change semantics.

## UI path

Visualizations pane › Charts 100+ › Special Charts (or the Special filter),
then pick the Tornado chart; exact data wells and overlay controls are
capture-gated. Do not assume a visual title encodes them.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: two measures mirrored left/right by category or period, central/left
         category labels, shaded/dashed references, cumulative percentage
         lines, capped intervals and value/share labels.
Exact native chart family, buckets and settings: not captured.
Native side, scale, overlay and label settings: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.
A mirrored-comparison presentation does not prove that the native visual
selected the Tornado family.

## Constraints

- Mirrored positive quantities are not negative facts or signed variances.
  Capture mirroring and equal-unit domains; do not negate model measures to
  imitate the display. Counts, indices, percentages and amounts need separate units.
- Bind side headings, category field and units explicitly; title measure
  order can differ from side order. Preserve category alignment.
- Cumulative lines, within-side shares, reference fills and capped intervals
  are distinct features. Capture their measures/denominators/meaning; do not
  infer sensitivity analysis, confidence intervals or native error-bar settings.
- A shared order can be descending for one side but not the other. Preserve
  matching rows rather than sorting each half independently; both overlays
  need not meet strict descending Pareto semantics.
- With independent side domains, similar lengths do not imply similar
  quantities; keep scales explicit. A rate comparison needs its own
  denominator, not a visual ratio of mirrored bar lengths.
- Intelligence chart library only; never a Power BI native visual.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "TORNADO_BAR"
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"tornadoChart"
Pointer: /properties/pivotAssignments (two AC measures)
Evidence: [saved] one saved tornado owner; side, scale and overlay keys not recorded.
```

- Which AC measure draws which side is unresolved; preserve the saved measure
  order and the complete owner [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
- `CH-ANLY-01`
- `CH-ANLY-02`
