---
id: CH-LIB-16
name: Funnel and pyramid charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Funnel and pyramid charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Drop-off across ordered stages.

## When to use

- Nested pipeline stages only.

## UI path

Visualizations pane › Charts 100+ › Funnel, then pick the variant (type
pyramid in Search Charts if it is not listed there).

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: funnel-shaped categories labeled with counts and shares.
Native family, shape options and bindings: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Alternative outcomes, severity classes and won/lost statuses are not nested
  conversion stages. Prefer bars for independent categories; do not infer
  drop-off, progression or value-proportional area from a funnel shape.
- Intelligence chart library only; never a Power BI native visual.
- Capture the native family, category order and count/share denominator. Do
  not claim conversion from largest-stage-normalized percentages or
  adjacent-stage differences.
- Define event deduplication and the counted population; an event-log
  population is not interchangeable with an aggregate measure of the same
  activity.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "FUNNEL" | "EXECUTIVE_FUNNEL_HORIZONTAL"
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"otherChart"
Pointer: /properties/pivotAssignments (axis = stages; AC = value; one executive
         funnel adds a row trellis)
Pointer: /properties/visualState/hiddenProperties_!!!_funnel (JSON string)
Decoded keys: chartType:"funnel" | "pyramid"; isInverted; isCurved;
              dynamicSlope; chart width (100); curve height (25); pinched;
              pinchCount; includeTotalSum
Partial: {"chartType":"pyramid","isInverted":false,"isCurved":true,"dynamicSlope":false}
Evidence: [saved] companion-library saved owners; not isolated or re-rendered.
```

- A pyramid keeps owner chartType `FUNNEL` with decoded inner
  `chartType: "pyramid"`; preserve both layers and never invent a `PYRAMID`
  root value [saved].
- Width, curve-height and pinch values are native settings, not proven units
  or algorithms; `includeTotalSum` does not justify summing nonadditive
  conversion rates [open].
- Optional companion default; this skill's design rules win: the user
  reduced the chart title allocation of standard and executive funnels from
  48 px to 35 px while keeping two-line titles. Start there, validate actual
  fit and never force it on longer titles [confirmed].
- That correction left inner geometry and stage bindings unchanged (funnel,
  width 100, curved, non-inverted, no dynamic slope, curve height 25,
  unpinched, pinch count 1, total sum on) [saved]. Its rendering and clipping
  were not runtime-tested [open].
- Stage sorting, curved or pinched geometry, totals and inversion behavior are
  unresolved [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
