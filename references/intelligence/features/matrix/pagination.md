---
id: MX-PAGE-01
name: Pagination
area: matrix
category: Pagination and export
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/pagination-and-formatting-for-reports
---

# Pagination

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Splits the Matrix into pages with rows per page, row/column/section breaks, and page controls.

## When to use

- Report packs; long lists without scrolling.

## UI path

Home › Pagination.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.pagination (enable, pageRowCount, autoRowCount, paginationHeight, view), page_config
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Vertical scrollbars or partially visible statements do not establish
  pagination, repeated/frozen headers or complete export. Capture page
  settings and test all rows, headings, subtotals and disclosures; never
  reconcile a full statement from only its visible viewport.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/pagination, /properties/visualState/page_config (objects, partial)
Fragment: {"pagination": {"enable": false, "view": "browser"},
           "page_config": {"view": "Browser", "column_break": null, "pagination_type": null}}
Evidence: saved Table owner (visual type 15) [saved]; Matrix values not isolated
```

- The two `view` keys live in different groups and save different casing
  [saved]; never normalize them, and keep null `column_break` and
  `pagination_type` values null.
- Optional companion guidance (this skill's layout rules win, and they allow
  internal scroll for large matrices): size the Matrix for its required
  rows, columns, headers and toolbar without scrollbars, or reflow or split
  detail into paginated or navigable pages; never truncate required data
  merely to remove a scrollbar.

## Related features

- `MX-HF-01`
- `MX-EXP-01`
