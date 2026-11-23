---
id: MX-LAY-01
name: Layout options (hierarchy, outline, table, stepped)
area: matrix
category: Layout and hierarchies
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/get-started-with-reporting
---

# Layout options (hierarchy, outline, table, stepped)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Switches the Matrix between hierarchy (indented, expandable), outline, flat table, stepped, and drill-down layouts.

## When to use

- Hierarchy layout for drillable dimensions (Region › Country).
- Table layout for flat lists and export-like views.

## UI path

Home › Layout.

## Definition encoding

```text
Family evidence: definition.json#/sheets
Standalone Matrix registration: INFORIVER; properties.visualType:10.
Observed reporting state groups: formatConfig, layoutSizes, uiSettings.
Exact reporting layout switch: not isolated.
```

The earlier `layout.layout_type:"Table"` hint came from a Planning grid. Later
user-finalized reporting matrices also carry it (see Additional details), but
do not hand-write it into a Matrix: set it in the UI or copy a complete
same-kind owner. Indented hierarchy rows or separate dimension columns in a
screenshot do not identify the saved layout.

## Constraints

- Performance mode changes how drill works; see MX-LAY-03.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/layout/layout_type (string inside the layout object)
Values seen: "Hierarchy" (row hierarchy with a column field), "Table" (measures, no row hierarchy)
Evidence: saved standalone INFORIVER/10 reporting matrices [saved]
```

- Saved reporting matrices do carry `layout.layout_type`, and one saved
  owner had no `layout` group at all [saved]. Absence is no licence to
  insert a guessed enum.
- The rule above still applies: never hand-write `layout_type`; let it
  travel only inside a complete copied same-kind owner. Whether a changed
  value switches the rendered layout is untested [open].
- User-finalized full-detail matrices with two or three row levels (for
  example Region › State or Category › Subcategory › Product) were switched
  to `"Table"` in the UI [confirmed]: each level renders as its own column,
  sized by `columnMeta.<rowDimensionId>.width` (`MX-COLW-01`), with
  `measure_layout: null` and `tableState.expandCollapseIcon: "none"`
  [saved]. Use it for full-detail lists; keep the indented hierarchy for
  drill views.

## Related features

- `MX-LAY-02`
- `MX-HIER-01`
