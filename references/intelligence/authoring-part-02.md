## Contents

- [ID generation](#id-generation)
- [Visual recipes](#visual-recipes)
  - [Super Filter slicer](#super-filter-slicer)
  - [Matrix](#matrix)
  - [Chart](#chart)
  - [KPI card](#kpi-card)
  - [Text and shape elements](#text-and-shape-elements)
  - [Embedded Planning grid](#embedded-planning-grid)
- [Edit patterns](#edit-patterns)
- [Validation rules applied by plan_def.py](#validation-rules-applied-by-plan_defpy)
- [Troubleshooting](#troubleshooting)
- [Additional details](#additional-details)

<!-- Mode reference for the `fabric-plan-skill` skill. Continuation of authoring.md. Open this file directly from the skill reference index. -->

# Authoring mode - Part 2

Continuation of `authoring.md`.

## ID generation

| Namespace | Format | Rule |
|---|---|---|
| Sheet `recordGuid` | UUID v4 | New per sheet; never reuse a source plan's ID |
| Visual ID | UUID v4 | New per owned visual |
| `originEntityId` / `preVisualId` | Integer string | Next free integer on that sheet when authoring; UI saves rewrite `originEntityId` on every visual to its origin sheet's numeric id (creation order, see [CV-ELEM-02](features/canvas/navigation-buttons.md)) and `preVisualId` to a plan-wide counter (both valid) |
| Inserted measure ID | 19-digit integer string | Random, unique in the plan; formulas use `M_<id>` |
| Slicer filter ID | `filter_<unix-ms>_<9 chars>` | Unique per assignment |
| Plan display name | `<name> <unix-ms>` | Suffix when creating test copies |

`plan_def.py` prints fresh IDs: `python -I scripts/plan_def.py ids --uuid 3 --mid 2`.

## Visual recipes

Use the observed keys in the feature files and
[native samples](core/native-samples.md). Feature files state which encodings
are runtime-verified; the rest are observed saved settings, not feature-isolated
runtime verification. Never rename storage keys to product labels. Clone same-kind
native visuals and reset their caches and stored selections
([cloning native visuals](core/invariants.md#cloning-native-visuals)).

### Super Filter slicer

- `properties.visualType: 60`; registration `visualType: "SUPER_FILTER"`.
- `pivotAssignments`: one `category` bucket item per field.
- `superFilterAssignments[]`: `{ bucketId: "category", configuration: {
  visualType: "FACET" | …, filterMode, filterOperator, singleSelect, selectAll,
  sort[], topN{…}, name, … }, filter: [], filterLevel: "visual", id,
  isDefault, isDaxMeasure, isDefaultMeasure, pivotAssignments: [ same field ] }`
  — one entry per bound field.
- `visualState` groups: `facetSettings`, `dateSettings`, `hierarchySettings`,
  `measureFilterSettings`, `playAxisSettings`, `presetSettings`,
  `rankSettings`, `toolbarSettings`, `displaySettings`,
  `categoryCustomizeSettings`, `interactionStateSettings`, `minModeSettings`
  (pop-up), `filterHiddenSettings` (contains `isRegistered`, `savedFilters`,
  `customPresets`, `selectedDatePreset`), `filterContextProperties`,
  `readModeToolbar`, `visualStyles`.
- Slicer kind: `configuration.visualType` `FACET`, `DATE` or `NUMERIC`.
  Hierarchy is not a separate type: `facetSettings.enableFacetMode: false`
  plus per-level assignments ([hierarchy filter](features/slicers/hierarchy-filter.md)).
  Facet views: `facetViewType` `tile`, `toggle`, `checkbox`, `dropdown`,
  `textArea`. Pop-up: `minModeSettings.enableMinModeFilter: true`.
  Capture MEASURE, TREEMAP and PLAY_AXIS settings before authoring them.
- Selection/default: `visualState.slicerFilterAssignments` (VALUES include);
  single choice adds `forcedSelection` and a DESC sort for newest-first.
- Titles: `toolbarSettings.customTitleText` with `showTitle: true`; pop-up
  launchers show no title, so add a text label.
- Long lists default to a dropdown facet showing its own title; use pop-up
  mode only after the user approves it ([pop-up mode](features/slicers/popup-mode.md)).
- Copy the native filter-state trio (see `core/invariants.md`).

### Matrix

- Standalone Fabric Plan Matrix: `properties.visualType: 10`, registration
  `visualType: "INFORIVER"` (the storage enum, not a separate product).
  Observed state includes `rowDimensions`, `columnDimensions`, `formatConfig`,
  `numberFormatting`, `totalDisplayConfig`, `cfProps`, `ranking_config`,
  `pagination`, `page_config`, `globalStyles`, `gridStyles`, `themeColors`,
  `toolbar`, `manage_measures`, `row_height_config`.
  A later native reporting capture also contains `totals_config`; see
  [totals and subtotals](features/matrix/totals-subtotals.md) for the observed
  total-Off group. Do not substitute Planning-grid `layout` or code 80.
- Buckets: `rows`, `columns`, `ameasure` (Actual), `plmeasure` (Budget/Plan),
  `fcmeasure` (Forecast). Bind scenarios to their native roles, not all to
  `ameasure`, when scenario variance semantics are required.
- Native T05 selection stores
  `template_config: {"template":"T05","template_type":"Ibcs"}`.
  Preserve generated variance-measure IDs and configure their visibility;
  selecting a template alone does not establish strict IBCS compliance.
- Inserted rows are a separate `insertRows.json` part using captured `R_<id>`
  operands; see [calculated rows](features/matrix/calculated-rows.md).

### Chart

- `properties.visualType: 50`, registration `ANALYTICS_PLUS`.
  Use exact native `properties.chartType` values from the feature files
  (`LINE`, `DONUT_CHART`, etc.), not generic Power BI type names.
- Chart settings frequently live in JSON **strings** under
  `visualState["hiddenProperties_!!!_<group>"]`. Decode the group once,
  edit, and serialize back to a string; preserve the source representation.
- Buckets are chart-specific: observed examples include `axis`, `AC`, `PL`,
  `PY`, `row`, `stack`. Scenario bucket names are roles, not proof of business
  meaning (the gauge binds Plan Revenue to `PY`).
- Time axes: set `hiddenProperties_!!!_sorting` to ascending by `category`;
  measure-ranked bars use `sortBy: "Measure[…]"`, `sortType: "descending"`
  ([sorting](features/charts/sort-rank.md)).

### KPI card

- Native card: registration `ANALYTICS_PLUS`, code 50, `chartType: "CARD"`.
  Copy the whole saved card state, including `hiddenProperties_!!!_kpiControls`.
  Sparkline and categorical content require their own binding/template evidence.
  Apply the Number-Format-off workaround only if an `undefined` suffix occurs.
- For requested sparklines, bind category before choosing the native leaf
  command; use [Line capture guidance](features/kpi/insight-charts.md).
  Retain exactly one outer/internal title and only bound comparison roles;
  verify headline units and totals after adding the axis.
- Runtime-verified prior-year card: clone a UI-saved sparkline card, rebind
  `axis`/`AC`/`PY`, convert PL role tokens to PY, size the inner grid to the
  card minus 25px, use a short static title and set
  `legendSettings.showTitleAsLegend: false` ([KPI cards](features/kpi/kpi-cards.md)).

### Text and shape elements

- Native registrations `BI_TEXT`/202 and `BI_SHAPE`/201 exist in native
  exports. Copy same-kind objects; `shapeType` alone does not identify an element.
  Return navigation uses `BI_RUNTIME_INPUT`/203 and `navigatorState`.
  Images still need a native image sample.

### Embedded Planning grid

Reference-only until module integration; preserve existing entries and do not
add embeddings in this release. See [module boundaries](core/module-boundaries.md).

- Owned by its Planning sheet; on the Intelligence sheet add only:
  - registration `{ visualId, visualType: "PLANNING", isEmbedded: true }`;
  - `reactiveVisualProperties[]` entry `{ visualId: <originEntityId>, properties: { position, dimension, originEntityId, lockAspectRatio, visualInteractions, visualStyles } }`.
- Observed: the reactive entry's `visualId` held the sheet-local entity id
  (`"1"`), not the GUID. Mirror the native sample.

## Edit patterns

| Request | Pattern |
|---|---|
| Move/resize | Change normalized `position`/`dimension` in every placement copy |
| Rebind a field | Replace the bucket item with the registry field, keep companion keys |
| Add a measure to a Matrix | Append to `pivotAssignments` `ameasure` with next `order`; check `measureAttributes` |
| Change slicer type | Change `configuration.visualType` and the matching settings group from a native sample (hierarchy: `enableFacetMode: false` plus per-level assignments) |
| Apply a feature | Open the feature file; apply its encoding; log it |
| Hide a sheet | `definition.json → sheets[i].isHidden: true` (keep the sheet) |
| Reorder sheets | Reorder `definition.json → sheets[]` (or `order` if present) |

## Validation rules applied by plan_def.py

- Parts: required parts present; every JSON parses; `$schema` present.
- Sheets: every `definition.json` sheet has `sheets/<id>/sheet.json`; no orphan sheet folders.
- Visuals: every non-embedded registration has a visual folder with
  `properties.json`; embedded registrations have none on the hosting sheet;
  visual IDs unique.
- Geometry: positions and sizes within [0,1], positive, no overlaps between
  owned visuals (warning), `originEntityId` unique per sheet except native
  sheet-id stamps (values from 1 to the sheet count may repeat).
- Formulas: every `M_<id>` resolves to a measure ID in the plan.
- Fields (mandatory `--registry`): every model field in every part — field
  objects (`tableName`/`columnName`) and text references (`columnId`,
  `rankDimension`, `rankMeasure`, `searchDimension`, `playAxisCategory`, …) —
  resolves to the live model. Measures match by name model-wide.
- Security: no `Authorization`, `Bearer`, or `MWCToken` strings.

## Troubleshooting

| Symptom after publish | Check |
|---|---|
| Slicer shows field, filter card empty | Registration part of the filter trio (`filterHiddenSettings.isRegistered`, page/visual assignments) |
| "Some fields used in this sheet are no longer available" | Field closure against the registry; table prefixes |
| Visual at top-left over the header | Placement copies disagree; normalized vs pixel values |
| `#REF!` or raw `M_` text | Inserted measure ID mismatch |
| KPI shows `…undefined` | KPI Number Format off |
| Embedded grid empty | Registration present but source Planning visual ID changed |
| "[object Object] is not valid JSON" | Double-encoded part |
| Matrix CF rules have no effect | Rules must target the engine's `manage_measures`/`rowDimensions` ids from the newest readback, in `highlightedMeasure`, `highlightedMeasureName`, `bubbleBasedOn` and `conditions[].basedOn`/`comparisonMeasure`; a cloned rule keeps its donor's target ([MX-CF-01](features/matrix/cf-rules.md)). A Matrix colour scale is a `targetValue` rule with `colorScaleApplyTo: "continuous"`, not a `colorScale` rule ([MX-CF-02](features/matrix/cf-data-bars-color-scales.md)). |
| "No data" with default filters | Stale stored selection or preselected date preset copied from a template |
| Months run newest to oldest | Time-axis `sorting` still `reset`; set ascending by `category` |
| Button Actions panel shows no page | `pageDestinationId` must be the target sheet's numeric id |
| Tabs or buttons open the wrong page after sheets were added | Sheet ids follow creation order, not position; keep them in the build manifest and use them for `selectedPages`, `pageDestinationId` and `originEntityId` ([CV-ELEM-02](features/canvas/navigation-buttons.md)). |
| Readback gains a `BI_REPORTING` sheet with one `UNKNOWN` visual and no parts | Explore Model was opened in the editor ([CV-EXPL-01](features/canvas/explore-model.md)); treat it as scratch state, not a user page. |
| A multi-level Matrix shows no expand/collapse icons | Set `tableState.expandCollapseIcon: "plusMinusSquare"` on Matrices whose rows hold two or more fields ([MX-HIER-01](features/matrix/manage-hierarchies.md)). |
| Old visual overlaps its replacement | Omitted visuals are not deleted; reuse, hide or delete in the UI |
| Dropdown list cropped in a filter band | Give it room; a pop-up (`minModeSettings`) only with the user's approval |
| Sparkline prints its series name | `legendSettings.showTitleAsLegend: false` |
| Create fails `ImportFailed … UNIQUE constraint failed: comment_settings.recordGuid` | A copied `commentSettings.json` kept its donor's root `recordGuid`; give every sheet's copy a new UUID (the key is at the part root, not under `properties`). Nothing is created, so fix and resubmit once. |
| Update fails `ImportFailed … Event-trigger replacement rollback failed`, even for an unchanged round trip | The user deleted visuals in the editor; re-emit them hidden under their original ids from the pre-deletion readback ([removing visuals](core/invariants.md#after-the-user-deletes-visuals-in-the-editor)). |
| Panels, bands or frames hide the charts, slicers or Matrix drawn on them | `layerProperties.order`: a **lower** order paints in front ([CV-LAYER-01](features/canvas/layers-elements.md)). Give backgrounds larger orders than the content they frame, and accent bars or badges on a card a lower order than the card; do not assign orders in build sequence. |
| A cloned shape shows an unexpected logo or icon | The donor's `shapeState.icon.isEnabled` is still true; disable it unless the icon is intended. |
| Matrix shows an auto title such as "Net Sales by Category, Month" | `chartCustomTitle.customTitle.elements` was emptied; keep one native `DEFAULT_TITLE` element and set its `content` (title + subtitle) instead. |
| KPI comparison line for the second slot (PL) shows the PY change | A `[$Value.ΔPL%]` / `[$VarianceIcon.ΔPL]` mention derived from the ΔPY tokens rendered the PY change [confirmed]. Use the native `[$Value.PL]` value mention for the second baseline until a UI-saved ΔPL mention is captured. |
| Every KPI sparkline keeps the donor's line colour | Recolour the measure-keyed `appearance.charts.measuresStyle` entry of the bound actual, not only `AC` ([KPI-CHART-01](features/kpi/insight-charts.md)). |
| A KPI card cloned for another measure still shows the old one | Card text mentions are role-based (`[$Value]`, `[$Value.PY]`, `[$Value.PL]`, `[$Value.ΔPY%]`); the measure appears as `_Measures[<name>]` in pivot ids, `measureConfigMap`, `measuresStyle`, `customTheme`, `numberFormatting.customFormat` and sort/rank keys. Replace that exact token everywhere and set the pivot `columnName`/`name`/`formatString`. For a lower-is-better measure swap `kpiControls.variance.colors` positive/negative. |
| Tile slicer shows only a search box, or nothing but a scroll dot | Turn off `facetSettings.enableCategorySearch` and give the facet room for its title plus a tile row: 132px fitted a 26px title and 30px tiles, 100px still scrolled ([SF-FACET-01](features/slicers/facet-filter.md)). |
| Matrix shows a "Rows: n Columns: m" bar with zoom and paging | Set `miscellaneous.isUserChangedFooter: true` with `enableFooter: false` ([MX-VIS-01](features/matrix/matrix-visual.md)). |
| Matrix grand-total row disappeared | `totalRowsDisplay: "underlyingData"` was removed from a newer-format owner; keep it ([MX-TOT-01](features/matrix/totals-subtotals.md)). |
| Matrix rows ignore `globalStyles.rowHeight` | The owner lacks `row_height_config`; add it with `default_row_height` and `sub_total_row_height` ([MX-VIS-01](features/matrix/matrix-visual.md)). |
| Percent column shows a doubled sign ("25.80%%") | A model percent measure carries `formatConfig` code `"9":"%"`; remove `"9"`/`"11"` from it and keep them only on engine-computed variance % columns ([MX-NUM-01](features/matrix/number-scaling.md)). |
| Extra Matrix column shows the full measure name | Set `customName` and `isRenamed: true` on its pivot assignment; a `manage_measures` label alone does not rename it ([MX-VAR-01](features/matrix/variance-columns.md)). |

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### ID remapping

- Keep registries for sheets, visual instances, measures, queries, pivots and
  bookmarks, and record an old-to-new map for every remapped identity; remap
  only identities that must change.
- Keep semantic field IDs distinct from display labels and runtime counters
  (identifiers).

### Diagnostic sequence

1. Identify the plan, sheet, visual and the exact observed behavior.
2. Preserve the raw definition and the last working readback before changing
   anything.
3. Check cheap local facts first: JSON shape, field IDs, reference closure,
   numeric wrappers and geometry.
4. Read the current saved state through `getDefinition` (management).
5. Compare with the smallest relevant working native sample; never reset a
   whole report to diagnose one property.
6. If a generator or script produced the artifact, fix it there as well.
7. Verify at the layer that failed and report what remains unverified.

Respect an explicit user scope limit (for example layout only) and do not
investigate excluded issues.

### Additional troubleshooting

| Symptom | Check |
|---|---|
| A new visual reads back as an empty shell | Its part lacked the donor's complete envelope (definition structure) |
| Readback has fewer sheets or visuals than the package | Persistence gap (validation layers); do not re-create |
| Import fails without useful detail | Keep the raw payload; compare one controlled change at a time with a working export; a generic error does not prove an environment incompatibility |
| A copied sheet exists but is empty | Measures, properties and assignments must travel with the complete parts |
| Labels render but every measure is blank | Scenario context, page and slicer filters and relationships at the displayed intersection; never mask blanks with zeros |
| A new visual sits below the canvas | Bounds and the free-rectangle procedure (invariants) |
| Container membership lost after a clone | `groupIds` use the container's local `preVisualId` [saved] |
| A chart patch also changed a Text or Shape | Filter by family before `chartType` (visual identity) |

### Scope and authorization

- A user redirect that puts work on hold supersedes it; do not resume or
  retry the held work without a new request.
- A read-only learning boundary and a later, separately authorized edit are
  distinct scopes: the earlier boundary does not block the new work, and the
  new authorization covers only what it names.
- Within an approved scope, proceed without repeated confirmation: ask only
  for information or access that blocks the next step and continue
  independent work meanwhile. The greenfield, model-measure and publishing
  approval gates still apply.
- A local builder or script can undo the user's saved corrections. Rebuild
  from the latest readback, port the corrections into the builder and never
  rerun a superseded builder over a visual the user has since corrected.
