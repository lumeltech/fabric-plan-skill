---
id: MX-PIN-01
name: Pin rows and columns
area: matrix
category: Layout and hierarchies
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
---

# Pin rows and columns

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Freezes chosen rows or columns so they stay visible while scrolling. Pinned
rows appear in a pinned section at the top and stay there across pages; pinned
columns move to the left, ahead of other columns. Freeze row/column, Freeze
grand total and Stick Measure to Last are related position options.

## When to use

- Wide month grids: pin the row header and total column.
- Keep a key category row visible across pages.
- Bring the latest period's column next to the row labels.

## UI path

Rows: hover the row › Pin icon. Columns: Column gripper › Pin column. Unpin:
click the pin icon, or gripper › Un-pin column / Un-pin all. Freeze: Row
gripper › Actions › Freeze row; Column gripper › Freeze column.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- A pinned row also stays at its original position; unpin it from either
  place.
- Pinned rows remain pinned while paging through a multi-page Matrix.
- Frozen rows and columns are kept in Excel and PDF exports.
- Freeze grand total (Row gripper) fixes the grand-total row at the top in
  multi-page scrolling layouts.
- Stick Measure to Last (Column gripper) keeps one designated measure in the
  last position even when fields are added.

## Related features

- `MX-COLW-01`
