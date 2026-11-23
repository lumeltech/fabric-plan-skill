---
id: MX-MISC-01
name: Miscellaneous settings
area: matrix
category: Toolbar and UX
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
---

# Miscellaneous settings

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Context menu, fiscal year start, language, right-to-left, status bar
aggregation, error handling, logo/info. Also header word wrap, quick-shortcut
icons, absolute sort, measure-header visibility and image fill, floating
toolbar, selection border, column filters, scroll thickness, common measure
width, column spacing (0–20), pin icon and scaled reading-view tooltips with
custom decimals. Interface languages: English, German, French and Spanish.

## When to use

- Fiscal calendars; RTL locales.
- Show a quick sum, average or count of selected cells in the status bar.
- Keep calculated rows working when referenced members are missing.
- Rank by magnitude regardless of sign (absolute sort).

## UI path

Display settings › Miscellaneous (Misc tab of the Display panel, opened from
Home › Settings › Display settings): View, Status bar, Cell/row/column and
Reading view tooltip sections.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.miscellaneous
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Status panel aggregation (sum, average, min, max, count of the selection)
  needs Show status bar and shows at most three aggregations; Total Rows
  Display counts underlying data rows or only the rendered visual rows.
- Global error handling turns missing-reference values into 0 inside
  calculations; when it is off, such formulas show a missing-reference error.
- Absolute sort orders by magnitude, ignoring sign. Scaling in Measure Header
  adds the Uniform scaling factor to measure headers, not just the report
  header.
- Right to left arranges columns right to left, moves row categories to the
  right and mirrors the toolbar.
- Pinned rows are visual-level duplicates; Hide pinned base rows hides the
  originals and keeps the pinned copies.
- Explorer cross-filtering lets KPI explorer selections in one visual filter
  the other Matrix and Intelligence chart visuals on the sheet.
- Diagnose replaces values with randomly generated, masked data; turn it off
  before publishing.
- Native-measure editing in reading view and edit-cell/row indicators concern
  input editing, which this release does not author. Populate missing AC with
  FC may use only a bound semantic-model forecast measure.

## Related features

- `MX-FMT-04`
