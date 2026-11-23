---
id: CH-CALC-01
name: Calculated measures and advanced pivot
area: charts
category: Chart data
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Calculated measures and advanced pivot

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Visual-level formula measures and an advanced pivot (designer view) for
Intelligence charts, cards and tables. The formula editor combines measures
bound to the visual (type # for suggestions); results go to the Actual or
Comparison wells and plot like model measures. The advanced pivot maps
measures to Actual/Comparison wells (variances calculate automatically) and
dimensions to axis/row/column/legend, and filters categories and values.

## When to use

- Derived measures without model changes.
- Reconfiguring many measures and dimensions while the chart re-renders live.
- Visual-level filtering of dimension members or measure values.

## UI path

Data › Calculated measure. The ribbon's Formula button (Data group) opens the
Calculated Measure pane, as does the formula icon in the pivot data window's
measures section; maximize the editor for long formulas. Edit or delete a
calculated measure from the pivot data window. The advanced pivot opens by
default when the visual is full-size or fills about 75% of the canvas;
Settings › Others › Hide advance pivot turns it off. Its Advanced section
holds split-measure and combine row/column dimension options.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Visual-level only: formulas use measures already bound from the semantic
  model and never change the model. Field-closure, formula-subset and
  measure-permission rules still apply (`core/invariants.md`).
- Never reference From Sheets, query, external-file or cross-module measures;
  record such requests as blocked: module integration pending.
- Comparison charts plot only the first measure in the Actual well; other
  Actual measures are not drawn. Up to three comparison measures are supported.
- Measures are auto-assigned to wells (Actual by default); lock measures or set
  a default bucket to keep a user-defined assignment.
- Pivot filtering is available only in the advanced pivot (designer) view.
- IBCS enforcement in the Advanced section is opt-in; enable it only when the
  user asks for IBCS.
- Documented UI steps are not encoding evidence; capture a native sample
  before writing calculated measures into a definition.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Decoded `hiddenProperties_!!!_comparisonMeasureMapping` holds `config`,
  `allMeasures`, `defaultBucket` (seen `"auto"`) and `standardNotation`
  [saved]. Whether `defaultBucket` is the pivot's default-bucket setting is
  unresolved [open].
- `standardNotation: true` also appears on a non-IBCS grouped-measure cluster,
  and saved owners carry `ibcsformat` as true or false [saved]. Which flag the
  Enforce IBCS standards toggle writes is unresolved [open].
- `fieldsMeta` role names saved beside a comparison mapping are native
  metadata, not new measures [saved].

## Related features

- None.
