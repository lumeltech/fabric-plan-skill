---
id: MX-BLEND-01
name: Blend measures
area: matrix
category: Layout and hierarchies
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/planning-sheets/concepts/connected-planning/blend-measures
---

# Blend measures

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Combines two measures into one blended column (e.g. value with variance in one
cell). Blend direction places the second measure below the first (Vertical,
default) or beside it (Horizontal). Source-column formatting, including
conditional formatting such as icons and data bars, carries into the blend.

## When to use

- Compact executive tables.
- Show a value with its ratio or variance in one cell.
- Pair a value with its data bar or icon without extra columns.

## UI path

Matrix toolbar: Insert › Blend (Column group) inserts a blank blended column
and opens the Blend measure panel (title, measures, Blend direction › Create;
Update after changes). Selecting the two source columns first supplies the
measures. Hide the source columns via Manage Columns.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- The linked cross-module concept is a terminology/boundary reference, not
  evidence for this Matrix feature's within-cell JSON encoding. The reviewed
  [upstream coverage](../../core/upstream-references.md) likewise does not
  establish those keys; this feature remains `unverified`.
- This Matrix feature combines measures within one cell. It is not the
  cross-module blending of other modules' measures described in
  [module boundaries](../../core/module-boundaries.md).
- Blend only measures available to this Matrix: bound semantic-model measures
  or native Matrix calculations.
- Source columns stay visible until unticked in Manage Columns.
- Later formatting changes to a source column, such as font style, size or its
  conditional-format rule, also update the blended column.
- Changing Blend direction needs Update in the Blend measure panel.

## Related features

- `MX-VAR-01`
