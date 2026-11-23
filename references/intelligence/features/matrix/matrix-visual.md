---
id: MX-VIS-01
name: Matrix visual identity and bindings
area: matrix
category: Layout and hierarchies
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/get-started-with-reporting
---

# Matrix visual identity and bindings

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

The base reporting Matrix on an Intelligence sheet: row and column
dimensions (hierarchies allowed) with measures in scenario buckets, for exact
values, hierarchy detail, reconciliation and commentary. It is read-only
reporting, not an editable embedded Planning grid or a PowerTable sheet.
Its details were merged from the companion Intelligence authoring library;
tags: [saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

## When to use

- Exact values and multi-level hierarchies beside charts and KPI cards.
- Reconciling totals or attaching commentary to cells (`MX-NOTE-01`).
- Use the Table (`TB-TABLE-01`) for flat row lists; editable grids need an
  embedded Planning sheet, which this release does not author.

## UI path

Visualizations pane › Matrix, then assign row and column dimensions and the
measures. Ribbons: Matrix (layouts, charts, number formats, templates, filter
context, columns to display), Format and Data (sort, filter, rank,
translations, custom rows and columns). The Writeback ribbon is not enabled
in this release.

## Definition encoding

```text
Registration: INFORIVER; /properties/visualType = 10
Pointer: /properties/pivotAssignments (bucketId rows, columns, ameasure,
  plmeasure, pymeasure; optional annotation)
Pointer: /properties/visualState (object-valued groups, not
  hiddenProperties_!!!_* JSON strings)
Companions: visuals/{visualId}/dataInput.json and writeback.json beside
  properties.json
Evidence: saved native exports studied by the companion library [saved];
  no before/after capture in this skill
```

The authoring guide also lists `fcmeasure`.
The groups exist in native exports, but values are not isolated: copy a
complete same-kind owner or run `core/native-samples.md` before changing them.

- Role cardinalities vary between saved owners (several row fields, several
  `ameasure` fields, one `plmeasure`) and set no hierarchy-depth or
  measure-count limit [saved]. Storage-role names do not prove a measure's
  business meaning (`MX-VAR-01`).
- Saved owners carry `dataInput.json` (native measure records) and a
  `writeback.json` without configured destinations [saved]. Preserve both;
  neither shows editing or writeback, which belong to other modules.
- When rebinding, replace field identities only: `columnType` and
  `dataRoleType` keep the value "Measure"; bulk-replacing that string with
  "_Measures" corrupted both [saved].
- A registered Matrix reference can lack its `properties.json` in an export
  [saved]; treat its settings as unknown, never infer them from companions.
- A hidden owner exported with root `ANALYTICS_PLUS`, owner type 10,
  rows/ameasure bindings and mixed Matrix/chart state was identified by the
  user in the UI as a Matrix [confirmed]. Preserve both identities; never
  rewrite the root type, drop unfamiliar state or use it as a chart or Matrix
  donor. Its migration and runtime behaviour are unknown [open].

## Constraints

- Copy a complete matching owner with its companion parts; never rebuild a
  Matrix from visible row and column assignments. Preserve field IDs, grain,
  formatting, totals, sorting and filter context.
- Keep hierarchy expansion and total display separate from measure
  aggregation (`MX-AGG-01`, `MX-TOT-01`), and keep notes, annotation
  bindings, Notes column and footnote state at their own owners.
- Hidden-sheet duplicates are separate owners [saved]: count visible and
  hidden owners separately and never treat a duplicate as an extra live
  example.
- Verify leaf and total values, filter changes, hierarchy navigation and
  commentary scope in the native page. Saved configuration does not prove
  read-only permissions, query correctness or rendering [open].
- **Matrix initialization needs the model `url`.** API-created Plans whose
  `semanticModelReference` lacked `url` (and had `artifactId: null`) failed every
  Matrix with `Failed to initialize application: unreachable` (WASM log:
  ``missing field `url` ``); a later `updateDefinition` adding it did not
  persist. Creating the Plan with the legacy reference **including**
  `url: https://app.powerbi.com/groups/<workspaceId>/datasets/<modelId>` persisted
  it, and both Matrices initialized and rendered data [confirmed].
  Include `url` at create time; do not rely on adding it later.
- Engine measure ids appear field-stable across UI saves (`_Measures[Net Sales]`
  saved the same id in separate Matrices; Var/Var% ids are role-stable and
  their template CF rules rendered). A CF rule keyed to another field's id did
  nothing [confirmed]; whether pinning a field's id from another save makes a
  colour-scale rule render is unverified [open].
- **Row height.** Newer-format owners (native-insights) have no
  `row_height_config`; `globalStyles.rowHeight` alone left rows at the default.
  Adding `row_height_config` (`default_row_height`, `sub_total_row_height`,
  empty `custom_row_height` and `row_level_height`) applied the height
  [confirmed].
- **Status bar.** A newer-format owner showed a "Rows: n Columns: m" bar with
  zoom and paging under the grid although `miscellaneous.enableFooter` was
  false. Setting `miscellaneous.isUserChangedFooter: true` (as in older owners)
  hid it [confirmed].
- For optional no-scroll fit guidance, see `MX-PAGE-01`.

## Related features

- `MX-LAY-01` — saved `layout_type` values
- `TB-TABLE-01` — separate visual type 15 table
