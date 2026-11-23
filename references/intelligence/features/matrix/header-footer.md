---
id: MX-HF-01
name: Header and footer
area: matrix
category: Pagination and export
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-financial-reports
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/pagination-and-formatting-for-reports
---

# Header and footer

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Adds text, images, charts, and KPI cards to the Matrix header and footer.
Containers split into cells (left, right, top or bottom) that can be resized,
swapped, copied or reset. Elements add page numbers (Page X of Y, Page X/Y,
Page X), dates, symbols, data fields and slicer selections. Cells take
alignment, fill, shadow and borders; containers take border styles, margins
and left/right placement. Presets insert ready-made headers and footers.

## When to use

- Printed or exported packs.
- Title, period, units, logo and filter context repeated on every page.
- Page numbers, timestamps, headline KPIs or a small chart above a statement.

## UI path

Header > More options > Edit, or double-click the header.
Header & Footer ribbon controls alignment/background; Split adds containers;
the container + control inserts logo/text (financial-report guide).
Header & Footer ribbon > Presets > Header or Footer applies a preset; for a
footer, select Header & Footer in the Format ribbon first (pagination guide).
Insert element adds Date, Slicer, page numbers, symbols or data fields; the
header context menu shows or hides the header/footer and resets the header.
Select Close Editor to finish.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.miscellaneous (enableFooter, footerText …) (capture sample)
Evidence: none yet
```

Footer: not yet captured. Run `core/native-samples.md` before writing it.

Matrix title (header title element), observed in user-finalized saved
reporting matrices [saved]:

```text
Pointer: /properties/visualState/chartCustomTitle/customTitle
  layoutType "CUSTOM", layout "left-col", containerPosition "top"
  containerMeta {height ≈ 45, width = visual width px}
  elements[0] {type "DEFAULT_TITLE", id "left-col", align "left",
               verticalAlign "MIDDLE", content <rich-text HTML>}
Content example: <p><b><span style="font-size: 14px">Title<br/></span></b>
  <span style="font-size: 12px"><em>Subtitle.</em></span></p>
```

Use this built-in title and subtitle instead of canvas text boxes above the
Matrix, and give the reclaimed height to the Matrix [confirmed]. Edit the
title in the UI or copy a complete titled owner; the other element keys
(layout grid, margins, borders) were not isolated.

## Constraints

- A visible title, logo, units line or period banner may belong to the Matrix
  header or the canvas. Determine ownership before editing; capture the
  image/text/container encoding rather than guessing.
- Period labels for flow statements such as cash flow must describe periods,
  not snapshot dates. Test repeated headers and unit/per-share exceptions in
  exported output.
- A preset replaces the current header or footer after a warning; Reset
  restores the default header and drops its customizations.
- The footer stays hidden until shown and starts with default date and page
  number content; replace or confirm it before export.
- Data-field elements show dimension values or measure totals, not row values;
  check them against the report's filters and units.
- PDF Page Setup shows the header/footer on the first or every page; Excel
  includes footer content only when selected in Export Settings.
- Header/footer charts and images reach Excel only as pictures via Show
  Header & Footer as Image.

## Related features

- `MX-PAGE-01`
