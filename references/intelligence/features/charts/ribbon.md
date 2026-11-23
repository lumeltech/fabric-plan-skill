---
id: CH-LIB-20
name: Ribbon charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Ribbon charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Connected category bands showing relative amounts/ranks across ordered
categories or periods.

## When to use

- League changes by period.
- Series comparisons across non-temporal categories, with explicit category order.

## UI path

Visualizations pane › Charts 100+ › Special Charts (or the Special filter),
then pick the ribbon chart. Capture the ribbon variant and ranking/ band
settings.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: series bands across non-temporal categories with segment counts.
Native family, ranking, category order and ribbon styling: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- Bands across non-temporal categories are not time or member transitions.
  Bind count grain and series identities; capture fixed versus value-ranked
  band order and ties. Reconcile segments only for the defined population.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "STACKED_RIBBON_COLUMN_VERTICAL"
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"stackedChart"
Pointer: /properties/pivotAssignments (observed roles include a stack dimension)
Pointer: /properties/visualState/hiddenProperties_!!!_appearance; decoded path
         charts.ribbon (keys not recorded)
Evidence: [saved] one saved ribbon owner; not isolated or re-rendered.
```

- No other ribbon template appeared in the saved storytelling gallery [saved].
- Rank or stack ordering and ribbon crossing behavior are unresolved [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
