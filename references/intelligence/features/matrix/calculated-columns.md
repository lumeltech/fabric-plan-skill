---
id: MX-CALC-02
name: Calculated columns (visual measures)
area: matrix
category: Calculations
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/planning-sheets/reference/formula-syntax
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-a-dashboard
---

# Calculated columns (visual measures)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Adds measures or columns defined by formula inside the visual.

## When to use

- Ratios or differences not in the model, when the model cannot change.

## UI path

Insert › Column › Formula.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.measureAttributes, manage_measures; pivotAssignments item with 19-digit id and tableName ""
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Use [Matrix formula syntax](formula-syntax.md) for reporting calculations;
  exclude its Planning-only identifiers, advanced lookups and scripts.
- Formula-editor references and serialized `M_<id>` tokens are different
  surfaces. Preserve the actual Matrix's captured IDs and token syntax.
- The embedded Planning-grid evidence above does not verify a standalone
  reporting Matrix formula encoding; capture it before authoring.

## Related features

- `MX-FML-01`
- `MX-QF-01`
- `MX-CALC-01`
