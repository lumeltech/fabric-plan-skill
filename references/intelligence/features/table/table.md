---
id: TB-TABLE-01
name: Intelligence table
area: table
category: Table
status: IS-Confirmed
encoding: observed
visual: Table
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/get-started-with-reporting
---

# Intelligence table

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Tabular visual with measures, dimensions, and quick options. Native exports
register it as `INFORIVER` with visual type 15, not as an `ANALYTICS_PLUS`
chart-library visual.

## When to use

- Simple lists where Matrix features are not needed.

## UI path

Visualizations pane › Table, then assign the row dimensions.

## Definition encoding

```text
Registration: INFORIVER; /properties/visualType = 15 (Matrix uses 10)
Pointer: /properties/pivotAssignments (bucketId "rows" = row field; "ameasure" = measure)
Pointer: /properties/visualState: Matrix-like groups (rowDimensions,
  columnDimensions, totalDisplayConfig, numberFormatting, gridStyles,
  globalStyles, pagination, ranking_config, notes, toolbar, layout) plus
  showHeaderFooter:false
Evidence: live export of a UI-created test Plan (default state); not isolated by
          a before/after change or re-rendered after reapplication.
```

Copy a whole saved table. Never turn a Matrix into a table by changing the
visual type code. Table formatting and interaction values are not isolated;
follow `core/native-samples.md` before changing them.

## Constraints

- Bind a stable row key (event, transaction or record) and keep the detail
  grain distinct from aggregate quantities. Avoid duplicating facts or targets
  through joins between tables of different grain.
- Capture Table versus Matrix identity and each date's role (for example,
  start versus end date). Decide total rows consistently; totals and ranking
  are not inferred from captions.
- Validate any promised scope (single member, single date) before labeling a
  table as filtered to it.
- A screenshot grants no access. Require approved minimum-necessary fields,
  RLS/OLS, classification checks on personal fields and detail/export
  restrictions; do not expose hidden detail via search, totals or tooltips.
- Use synthetic identities in reusable examples; persist no real personal or
  patient records.
- Use the Matrix for statements and hierarchies.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/pivotAssignments (row-only: bucketId "rows" items, no measures)
Item keys: columnType:"Column", dataType:"String"
Pointer: /properties/visualState (object): gridStyles, globalStyles, columnMeta,
  rowDimensions, pagination, annotationBox, notes; no cfProps or jet_cfProps
Evidence: saved native Table owner on an Intelligence sheet [saved]
```

- Row-only tables are valid: that owner bound several String columns to
  lowercase `rows` and no measures [saved]. Preserve field identities and
  order.
- Its incidental owner `chartType:"COLUMN_VERTICAL"` does not make the Table
  a chart [saved].
- Another saved Table bound a two-level row hierarchy with several measures
  all in `ameasure`, plus a manual Notes column and footnote [saved]; see
  `MX-NOTE-01`.
- Saved null total flags and existing sorting and annotation state must be
  preserved, not filled from Matrix defaults [saved]. For pagination casing
  see `MX-PAGE-01`.
- Never require or add Matrix conditional-format collections on a Table;
  validate Table identity, row bindings, object boundaries and companion
  parts independently of Matrix-only rules.
- The companion recorded the table's root family as `TABLE`, with owner
  visual type 15, while this file records `INFORIVER`; copy the
  registration from a same-kind readback and never rewrite it. The guidance
  above wins until a capture resolves the difference [open].
- Insertion, row interactions, paging, note rendering and the relation to
  nearby filters were not tested [open]; verify filter-driven rows, sorting
  and rendering in the native UI.

## Related features

- `MX-LAY-01`
