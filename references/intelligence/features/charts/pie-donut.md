---
id: CH-LIB-06
name: Pie and donut charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
---

# Pie and donut charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Part-to-whole with slices.

## When to use

- Share with ≤ 5 parts only.

## UI path

Visualizations pane › Charts 100+ › Pie/ donut, then pick the variant.

## Definition encoding

```text
Pointer: /properties/chartType = "DONUT_CHART"
Pointer: /properties/pivotAssignments (bucketId "axis" = category; "AC" = measure)
Pointer: /properties/visualState/hiddenProperties_!!!_pieChartSettings (JSON string)
Default donut: group absent. Earlier saved donut: pieInnerRadius = 50;
               pieDonutType = "fullCircle"
Evidence: live export of a UI-created test Plan (default state); not isolated by
          a before/after change or re-rendered after reapplication.
```

Copy the full saved donut. Settings groups can be absent until changed; do not
add them with guessed values. Screenshots show center totals and
category/value/% labels, but those label controls are not isolated; do not
invent `centerTotal` or contribution keys.

## Constraints

- Nested hierarchy rings are not independent donut series; a center hole and
  total do not justify `DONUT_CHART` or its radius settings. Use the
  [sunburst reference](sunburst.md); never add parents and leaves together.
- If every slice shows the overall total or equal shares, investigate
  dimension/measure context. Slices of an exclusive partition must reconcile
  once to the center total; never divide a duplicated total by category count.
- Define each counted entity or amount, the center total and the selected
  versus all-member denominator. Reconcile center totals with related cards or
  tables, and status slices with the same classified rows, not just totals.
- Label every slice, including small ones, and confirm shares total 100%
  within display rounding. Expose complete legends with full text for
  truncated labels, and retain zero/unknown status semantics.
- Intelligence chart library only; never a Power BI native visual.
- Keep value-weighted and count-based donuts distinct. Define bucket bounds and
  Other grouping; never imply amounts from counts or treat units as distinct
  customers.
- Map boolean categories to readable labels and keep missing separate from
  declined-to-answer values. Keep category colors consistent across related
  visuals rather than copying conflicting palettes.
- Use native chart identity, not stale captions. The observed full-circle
  settings do not verify offset slices or label configuration.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "PIE_CHART" | "DONUT_CHART" | "VARIABLE_PIE_CHART"
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"pieChart" (all three); donuts also
              id:"DONUT_CHART", chartType:"pieChart"
Pointer: /properties/visualState/hiddenProperties_!!!_chartsMode (JSON string)
Decoded keys (donuts): visualMode:"CHART"
Pointer: /properties/visualState/hiddenProperties_!!!_pieChartSettings (JSON string)
Decoded keys (donuts): pieInnerRadius:50; pieDonutType:"fullCircle";
              enablePieExplosion:false; allowWheelSwitch:true; startAngle,
              endAngle, padRadius, cornerRadius, rotation, outerPadding: null
Pointer: /properties/visualState/hiddenProperties_!!!_appearance; decoded path
         charts: individualCategoryColor:true; individualColor:false
Evidence: [saved] every inspected saved pie, donut and variable-pie owner (the
          donut-only keys in every saved donut); not isolated or re-rendered.
```

- Companion default for every new pie and any default-formatting reset: keep
  `individualCategoryColor: true` with `individualColor: false`. They are
  different settings; `individualColor` does not give slices distinct
  category colors, and one value measure does not justify coloring every
  slice alike [confirmed].
- In the companion library this pie default overrides generic resets whose
  category-color flag is false; it does not establish other donut-specific
  behavior [confirmed].
- The user-supplied runtime configuration names the same fragment
  `config.appearance` [confirmed]. Keep the exported object or JSON-string
  form of `appearance`, and reserialize only a string [saved].
- Optional guidance only: the copy-the-full-donut and no-guessed-groups rules
  above govern writing. Verify both flags in fresh readback and inspect the
  rendered slices, or report rendering as unverified.
- Variable pies also bind `PY` [saved]. Whether that slot sets radius, width
  or another geometry is unresolved; do not label it from the template name
  or assume the chart suits the question [open].
- Keep saved `null` geometry fields; never replace them with zero [saved].
  Radius unit and range, explosion and wheel-switch effects are unresolved;
  the companion's one-setting wheel-switch test was deferred [open].
- The sunburst template also uses the `pieChart` renderer; the renderer alone
  does not identify a pie [saved].
- Before finishing, check shares and totals, missing or negative categories,
  legend-color consistency and label collisions; a saved color flag does not
  prove accessibility.

## Related features

- `CH-AX-01`
- `CH-LBL-01`
