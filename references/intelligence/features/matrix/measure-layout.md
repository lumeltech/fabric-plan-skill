---
id: MX-LAY-02
name: Measures in rows or columns
area: matrix
category: Layout and hierarchies
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-financial-reports
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-ibcs-formats/table-templates
---

# Measures in rows or columns

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Places measures as columns (default) or as rows, e.g. for statements with many measures.

## When to use

- Many measures and few periods: measures in rows.
- IBCS T03 table with measure rows.

## UI path

Home › Layout › Measure layout.

For measure header groups, the financial-report guide documents selecting
measures > Matrix ribbon > Layout > Group > Create Group. Grouping and
measures-in-rows are different controls; capture their bindings separately.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.layout.measure_layout
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- A spanning period banner or statement appearance does not prove a
  measure-layout or grouping setting. Resolve period dimension versus
  separate measures, and account members versus measure rows.
- Do not apply balance-sheet snapshot aggregation to income or cash-flow
  periods.
- For period rows with nested column groups and repeated scenario/variance
  measures, capture nested column assignments and measure order separately;
  the observed layout setting alone does not establish that pivot.

## Related features

- `MX-LAY-01`
- `MX-TPL-04`
