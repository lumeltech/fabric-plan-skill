---
id: MX-EXP-01
name: Export to PDF and Excel
area: matrix
category: Pagination and export
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/export-high-quality-pdf-and-excel-reports
---

# Export to PDF and Excel

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Formatted export with page setup, headers, footers, comments, and conditional
formatting. Exports the entire Matrix or selected columns to PDF or Excel with
number scaling, calculated rows/columns and notes. PDF setup covers content
order, page size (incl. custom), orientation, fit scaling, margins, font, cover
image, comment replies, filter info, footnotes and decimals. Excel exports run
Fully Expanded, With Expand/Collapse or in Current State.

## When to use

- Distribution of report packs.
- Paginated PDF statements with repeated headers/footers, comments and notes.
- Excel hand-offs that keep the row hierarchy, formatting and calculated rows.

## UI path

Export tab or Export icon (first-party guides).
Select columns first to export only those; otherwise the entire Matrix is used.
PDF: Page Setup > set options > Update, then Entire Matrix or Selected
Columns > PDF Report. Excel: Export Report > Fully Expanded, With
Expand/Collapse or Current State; Export Settings picks header/footer content,
Repeat Totals and Repeat Label. Download the file from the link.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.readViewConfig.export (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- The first-party reading/editing guide distinguishes reading-mode
  PNG/JPG/PDF snapshots from Matrix Excel/CSV data exports requiring edit
  permissions. Use the authorized mode and test the actual output, including
  offscreen content; a snapshot is not a full data export.
- Excel export has operational boundaries: custom separators, blended columns,
  hatching, signed row headers, pinned rows, themes, padding, in-cell charts,
  images and dropdown input columns do not carry over.
- Excel flattens multi-color cells to one color, turns notes into unnumbered
  plain indicators, keeps only a comments column and caps custom icon sets at
  3 conditions.
- Screenshots and a scrollable Matrix establish no export result. Before
  claiming export readiness, test the generated output for complete rows and
  column groups, repeated headers, hierarchy, totals, notes, page breaks,
  accounting signs, units and per-share precision.
- Limits: 500k cells to Excel, 100k cells to PDF and 10 MB per PDF (Compress
  PDF helps); filter the report to reduce volume.
- Excel keeps expand/collapse for row hierarchies only. Table layout disables
  With Expand/Collapse and Current State; selected-column exports allow only
  Current State.
- Excel ignores default page breaks (one sheet); a row-dimension page break
  writes one sheet per category. Collapsed split subtotals export blank unless
  Repeat Totals is on.
- PDF drops image columns but keeps in-cell charts; the Page Setup font
  overrides data fonts. Header/footer charts or images reach Excel only with
  Show Header & Footer as Image.

## Related features

- `MX-PAGE-01`
