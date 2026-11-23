---
id: KPI-VAR-01
name: Variance on KPI cards
area: kpi
category: KPI cards
status: IS-Confirmed
encoding: verified
visual: KPI card
sources:
---

# Variance on KPI cards

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Absolute and % variance with colour and arrows against a comparison measure.

Fabric Plan KPI cards have **built-in variance icons** (user-confirmed).
Configure those controls; do not create SVG measures, image-data measures or
separate decorative visuals to reproduce the icons. Bind the actual/comparison
measures and define favorable direction in the card settings.

## When to use

- Every KPI should have a comparison.

## UI path

Card › Variance.

## Definition encoding

```text
Pointer: /properties/visualState/hiddenProperties_!!!_kpiControls (JSON string)
Decoded path: variance
Default keys: accentBar, border, colors, icon, percentage, showVariance,
              showVarianceColorAccent, showVarianceColorBorder, style,
              treatZeroAsNeutral, value, varianceDisplay
Earlier saved values: showVariance:false, value:true, percentage:true,
              icon.enabled:true, icon.positiveIcon.value:"up",
              icon.negativeIcon.value:"down", varianceDisplay:"percentage"
Evidence: live export of a UI-created test Plan (default state); not isolated by
          a before/after change or re-rendered after reapplication.
```

The controls exist, but saved examples kept `showVariance` false; do not
assert that this fragment activates a visible comparison. Copy a matching
whole card or isolate the active control. Screenshots of comparison text and
colored arrows are presentation evidence only.

```text
Runtime-verified comparison via card rich text (prior year):
  kpiControls.measures = {varianceMeasures:["ΔPY"], variancePercentageMeasures:["ΔPY%"]}
    (both empty on an actual-only card)
  kpiControls.gridLayout[].staticText mentions: [$Value.PY] (comparison value),
    [$VarianceIcon.ΔPY] (direction icon), [$Value.ΔPY%] (relative change)
  kpiControls.variance: colors {positive, negative, neutral}, treatZeroAsNeutral:true
Evidence: cloned from a native prior-year card; values, arrows and percentages
  user-confirmed in a published report.
```

For a ratio KPI (such as a margin %), show the comparison value and direction
icon only and report the change in percentage points elsewhere; a relative %
change of a ratio misleads.

## Constraints

- Built-in feature availability is confirmed; exact activation/template JSON
  still follows the native-sample gate. Missing encoding is not a reason to
  implement an SVG workaround or create a semantic-model measure for an icon.
- Bind each comparison to an explicit scenario/version measure, period scope
  and baseline label; capture native icon rules instead of inferring them from
  placement. Bind multiple baselines independently; success against one does
  not imply another. Do not invent multi-baseline JSON.
- Define period baselines precisely (prior year versus prior period, year-aware
  prior months, period-to-date scope, selected versus prior range exposure);
  keep them independent of slider intervals, preserve non-time filters and use
  unrounded values.
- Set favorable direction per metric from model descriptions and business
  policy, not badge colors or sign; invert colours for lower-is-better. Costs,
  durations, returns, attrition and clinical outcomes need explicit direction,
  applied consistently across repeated cards.
- Comparison arrows are distinct from target-based KPI status. Attainment is a
  ratio, not variance, and rates are not comparison deltas; reconcile each gap
  to its own scenario/version and period scope.
- Label rate changes in percentage points, distinct from relative percent, and
  verify absolute/relative pairs share one baseline. Format count changes as
  integers and keep days distinct from currency amounts.
- Set a neutral threshold and precision so near-zero changes never show as
  negative zero with a down arrow; define zero/negative-denominator treatment.
- Recompute weighted and composite rates from numerator/denominator under one
  approved grain/weighting, not by averaging displayed percentages. Separate
  value- from count-weighted rates and snapshot balances from flows.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Decoded path: hiddenProperties_!!!_kpiControls → variance
Preset-variance fragment: {"showVariance":true,"value":true,"percentage":true,
  "varianceDisplay":"percentage","icon":{"enabled":true}}
varianceDisplay values: "percentage", "value", "valuePercentage"
Variance item: its own gridLayout text item (id "staticId_TopBottom_2",
  measureKey "AC", format.link.text "[$Variance]", data-id "TITLE_VARIANCE")
Evidence: [saved] saved native card owners
```

- Many saved cards keep `showVariance: false` while retaining
  `varianceDisplay`, the `TITLE_VARIANCE` token and variance measure lists;
  which control renders variance, and their precedence, is unresolved, so the
  rich-text route above stays the verified path [open].
- User-saved cards used `"percentage"` on an amount card and `"value"` on
  profit-type cards whose baseline can be negative [confirmed]; choose per
  card and check favourable direction.
- Give title/value and variance disjoint regions: update pixel and
  percentage geometry together, and add about 24px of card height per extra
  delta line, scaling `coreContainer`, `gridContainer` and items together.
- Colours also exist at decoded `hiddenProperties_!!!_appearance` →
  `charts.variance.colors` {positive, negative, neutral}, beside
  `charts.variance.invertColor` [saved].
- Companion guidance sets `invertColor: true` for lower-is-better metrics,
  but every inspected saved owner keeps it false and its card effect is
  untested [open].
- `hiddenProperties_!!!_measureConfig` holds scenario entries plus absolute
  and percentage variance tiers; saved scenario cards disabled the variance
  tiers while scenario entries stayed enabled [saved].
- A text-grid AC/PY card kept an AC entry with `chart: "integratedVariance"`
  and visible flags but no chart item; flags alone do not prove a rendered
  chart [saved].
- The single-comparison path is confirmed [confirmed]. PY/PL/FC slots allow
  more, but complete multi-comparison rendering is unverified: confirm every
  delta's reference and label, or agree separate cards [open].
- KPI ribbon › Presets › Variance › first design ("Preset 1") applies a
  variance layout and may reset typography; restore it afterwards. The UI
  name is not proven to equal `preset: 1` [open].
- Newly added period-relative measures rendered blank or misleading card
  comparisons although explicitly filtered queries looked plausible
  [confirmed]. Query each measure under the card's effective report, page,
  visual and identity context, and compare the rendered card with it.
- Native split sparkline cards keep a trailing `[$Variance]` paragraph with
  `showVariance: false` [saved]; add one only when a comparison is bound.

## Related features

- `KPI-CARD-01`
