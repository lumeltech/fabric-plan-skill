---
id: MX-TROW-01
name: Template rows
area: matrix
category: Calculations
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
---

# Template rows

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Inserts one formula row that is created automatically in every group across
the row hierarchy, instead of adding calculated rows one by one. Options set
its position (First, Auto or Last), shared styling, inclusion in totals or
charts, and whether column totals use the formula.

## When to use

- Standard statement lines repeated in every group of a hierarchy.
- The same calculated line under each region, category or account group.

## UI path

Matrix toolbar: Insert › Insert Row › Template row; enter a title and formula ›
Create. Edit or delete it from the template row's Row gripper.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Position First or Last places the row first or last in each category
  wherever it was added; Auto places it above the selected row.
- Include in total adds the row to subtotals and totals; Include in charts is
  available only while Include in total is off.
- Evaluate columns before rows: on, column totals use the row formula; off,
  they sum the row's values.
- Apply the same style to all rows copies formatting to every instance.
- Matrix filters detect template rows like other inserted rows.
- Use formula template rows only; data-input or writeback rows belong to other
  modules and are not enabled in this release.

## Related features

- `MX-CALC-01`
