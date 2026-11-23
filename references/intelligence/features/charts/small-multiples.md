---
id: CH-MULT-01
name: Small multiples (trellis)
area: charts
category: Chart layout
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/compare-data-with-small-multiples
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-ibcs-formats/small-multiples
---

# Small multiples (trellis)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Repeats a chart per member with shared scales, totals, and average panels.

## When to use

- Same comparison across segments.

## UI path

Chart › Trellis.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/pivotAssignments (axis = month field; AC = measure; row = panel field)
Pointer: /properties/visualState/hiddenProperties_!!!_trellisSettings (JSON string)
Decoded keys: gridSize:{row:2,column:3}; averagePanel.enabled:true;
              totalPanel.enabled:false; panelScale:"individual"; xAxis:"all"; yAxis:"all"
```

Copy the full group and matching facet bindings. Screenshots show member
panels with an average panel, but average-panel aggregation is not isolated.

## Constraints

- Choose scales explicitly: the observed sample uses **individual** panel
  scales, not a shared scale. Use consistent scales when magnitude comparison
  is the goal; label differing scales when analyzing within-panel trends.
- Screenshot arrangement does not prove native trellis composition, member
  filtering or completeness. Capture object structure, panel order, domains,
  heading totals and guide calculations before copying a layout.
- If panels repeat identical totals, test facet-specific filter context.
  Reconcile each panel independently and use chronological date keys.
- Define average-panel weighting and distinguish total panels from an average
  panel. Recompute rates per panel rather than adding them like quantities.
- Keep category order aligned across panels, title ranked subsets explicitly
  (for example Top N) and use display names in panel titles.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Trellis owners' template: chartType "columnChart", rendererType
  "smallMultiplesChart" (seen for LINE, AREA, AREA_INTEGRATED and
  COLUMN_INTEGRATED_VERTICAL); actualChartType per family
hiddenProperties_!!!_trellisSettings further values: gridLayout "grid" |
  "gridVariedRow"; display "scroll"; panelScale "auto" | "individual";
  gridSize also 1x5, 3x1 and 4x1; xAxis "auto" | "all" | "stickyBottom";
  yAxis "auto" | "all"; averagePanel.enabled and totalPanel.enabled set
  independently
hiddenProperties_!!!_smallMultipleAppearance (JSON string) keys: panelTitle,
  panelBackground, panelBorder, panelSpacing, panelInnerSpacing, matrixLabel,
  panelHeader, accent and shadow settings
Evidence: [saved] saved owners only.
```

- Facet buckets are `row` and `column`; hierarchical trellis keeps several
  ordered axis, row and column levels [saved]. Preserve their order and
  `splitByCategory`; never flatten levels into one label.
- `splitByCategory.pivotValueAssignments` can be empty despite a row binding
  and the trellis renderer; the KPI split-value pattern is not required for
  chart trellis [saved].
- `panelSpacing` values (such as 0 or 3) are internal panel spacing, not
  dashboard gutters [saved].
- Saved owners also carry `hiddenProperties_!!!_trellisGridResize` and
  `hiddenProperties_!!!_multiChartTypeTrellis` [saved]. Their meaning is
  unresolved [open].
- Match donors by actual renderer; never pool ordinary and trellis owners of
  one family [saved].
- Optional (user-edited example): one shared row trellis can replace several
  separate per-member trend visuals that repeat the same comparison and time
  series; verify every panel label and overflow in the UI [confirmed].
- Insertion route, axis sharing and stickiness, scrolling, panel order, scale
  control and average/total calculations are unresolved [open].
- `display: "scroll"` is saved trellis state, not a passed no-scroll test
  [saved]. Under the optional
  no-scroll acceptance,
  fit or reflow the panels instead of relying on trellis scrolling.

## Related features

- None.
