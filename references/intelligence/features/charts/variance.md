---
id: CH-LIB-27
name: Variance charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
---

# Variance charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Absolute and relative variance bars between scenarios.

## When to use

- AC vs PL/PY comparisons.

## UI path

Visualizations pane › Charts 100+; integrated variance charts are listed under
the IBCS filter, or type variance in Search Charts.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/chartType = "COLUMN_INTEGRATED_VERTICAL"
Pointer: /properties/pivotAssignments (axis = month field; AC = actual measure; PL = plan measure)
Pointer: /properties/visualState/hiddenProperties_!!!_appearance (JSON string)
Decoded path: charts.variance (varianceDisplay, measureCombination, invertColor)
Additional part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/chartType = "WIN_AND_LOSS_HORIZONTAL"
```

These are Fabric Plan's stored chart families, not generic variance type
names. Screenshots show integrated absolute bars plus a separate relative
strip, and diverging variance bars. Copy complete matching objects; the
separate-strip switch and sign/percentage semantics require isolation.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- Relative and absolute variance strips above paired scenario columns form a
  multi-section layout. Capture it and compare units/scales; the native family
  alone does not establish every section or its activation.
- For relative-variance pins over AC/FC columns with variance segments and a
  combined AC&FC total, confirm label, scenario and color semantics; costs
  need inverted favorability.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Integrated (overlapped) columns: id COLUMN_INTEGRATED_VERTICAL or
  COLUMN_INTEGRATED_HORIZONTAL; rendererType "columnChart"; chartOrientation
  per id; actualChartType "integratedVariance"
Win/loss: WIN_AND_LOSS_VERTICAL and WIN_AND_LOSS_HORIZONTAL; rendererType
  "columnChart"; bind axis + AC
Pointer: /properties/visualState/hiddenProperties_!!!_measureConfig (JSON string)
Decoded config[] (partial): one "AC" role with chart "integratedVariance" draws
  the AC/reference overlap; relative tier "Δ<bucket>%" (e.g. "ΔPL%") with chart
  "variancePin", type "RELATIVE_VARIANCE"; absolute tier "Δ<bucket>" with chart
  "varianceBar", type "ABSOLUTE_VARIANCE"
Evidence: [saved] saved owners; pins enabled and visible, and every inspected
  absolute tier saved isVisible:false.
```

- Bind `AC` and the literal bucket of the real reference (`PY`, `PL` or
  `FC`); `measureConfig` needs no separate reference role [saved]. Saved
  owners bind axis + AC + PL, axis + AC + PY (one also PL) or
  axis + AC + PL + FC; keep FC even when the pin compares PL [saved].
- `enable`, `isVisible` and `chartIsVisible` are independent flags; preserve
  each [saved]. Turning on the absolute tier is schema-consistent, but its
  rendering is unverified [open].
- `invertColor: false` was saved on every inspected owner, including cost
  charts; it does not establish cost polarity [saved].
- A user-corrected "overlapped" monthly comparison was a plain
  `COLUMN_VERTICAL` (`id` and `lockedTemplateId` both `COLUMN_VERTICAL`) with
  AC and plan bindings: judge the family from owner type, active template and
  lock together, never from a title [confirmed].
- Whether the UI's Overlapped Column type always saves these integrated ids
  is unresolved [open]. Row-trellis integrated owners: `CH-MULT-01`.
- Optional companion default: when a comparison exists, propose the scenario
  overlap, absolute variance and relative variance pins on one shared category
  axis unless only columns are wanted. Report an unverified tier as a gap, not
  as complete; if one visual cannot show the tiers, propose separately
  verified variance charts aligned below and confirm the layout first.
- Give the scenario and absolute tiers one unit and scale. Leave the relative
  pin out where the reference is zero or missing; with only one measure, skip
  the variance tiers and say which comparison is missing. IBCS tier notation
  stays opt-in (`CH-IBCS-01`).

## Related features

- `CH-AX-01`
- `CH-LBL-01`
