---
id: MX-HEAD-01
name: Dynamic measure headers
area: matrix
category: Layout and hierarchies
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-financial-reports
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/context-awareness
---

# Dynamic measure headers

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Makes headers change with filter context (e.g. 'Revenue FY2026').
Rename a measure header and append predefined functions (current month,
quarter or fiscal quarter, with + or − offsets such as previous month), the
current filter or slicer selection, or a value referenced from the grid.

## When to use

- Headers must show the selected year or scenario.
- Rolling period labels (current or previous month/quarter) without manual edits.
- Fiscal-quarter labels that follow the fiscal year start month.

## UI path

Column gripper › Rename › Dynamic. Or double-click the measure header and press
Ctrl+Space to list predefined functions and filters. Fiscal start: Display
settings › Misc › Fiscal year start month.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.columnMeta / row_label_meta (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- A plain rename is static text; only functions, filter selections or grid
  references make the header dynamic.
- The built-in fiscal-quarter function follows the Fiscal year start month set
  in Display settings › Misc.
- Filter and slicer selections are offered for headers only when filter context
  applies to the visual (`MX-CTX-01`).
- A referenced grid value must come from a field bound to the visual; hide that
  field via Manage columns if it should not display.

## Related features

- `MX-CTX-01`
