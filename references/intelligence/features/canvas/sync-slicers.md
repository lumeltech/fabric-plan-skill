---
id: CV-INT-02
name: Sync slicers across sheets
area: canvas
category: Interactions
status: IS-Confirmed
encoding: observed
visual: Sheet
sources:
  - https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/PlanProperties/1.0.0/schema.json
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes
---

# Sync slicers across sheets

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Keeps slicer selections the same on several sheets.

## When to use

- Report-wide period or region.

## UI path

Sync slicer.

## Definition encoding

```text
Path: planProperties.json → syncSlicerConfig (capture sample)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Plan-level sync configuration is a documented container, not proof that
  selections synchronize at runtime. Preserve shared settings outside the
  requested Intelligence change and test every intended sheet.
- Decide which filters sync across sheets; differing period selections on
  different pages may be intentional or a sync gap. Verify the state after
  navigation.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- [saved] A `syncSlicerConfig` group can carry a name and a stored value while its
  `syncFieldChanges`, `syncFilterChanges` and per-entity `isSyncEnabled` flags are
  all `false`; a named group does not prove active synchronization.
- Test cross-sheet synchronization separately from interaction direction, and
  reconcile any bookmark snapshot that stores the selection.

## Related features

- `CV-INT-01`
