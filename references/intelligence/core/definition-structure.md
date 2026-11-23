## Contents

- [Envelope](#envelope)
- [Part map](#part-map)
- [.platform](#platform)
- [definition.json](#definitionjson)
- [planProperties.json](#planpropertiesjson)
- [sheets/{sheetId}/sheet.json (REPORTING)](#sheetssheetidsheetjson-reporting)
- [sheets/{sheetId}/visuals/{visualId}/properties.json](#sheetssheetidvisualsvisualidpropertiesjson)
- [Bucket assignment objects](#bucket-assignment-objects)
- [Observed visualState groups](#observed-visualstate-groups)
- [Additional details](#additional-details)

<!-- Core reference for the `fabric-plan-skill` skill. Source: https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/plan-definition plus one decoded native readback (agentic_plan_creation/build_1793864601821/readback.json). -->

# Plan definition structure for Intelligence Sheets

Official reference:
`https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/plan-definition`.
Everything marked *observed* comes from a saved native export and may change
between product versions — always diff against a fresh `getDefinition`.

## Envelope

```json
{
  "definition": {
    "format": "PlanV1",
    "parts": [
      { "path": "definition.json", "payload": "<base64 UTF-8 JSON>", "payloadType": "InlineBase64" }
    ]
  }
}
```

- Every part is base64 of UTF-8 JSON. Readback files may begin with a BOM;
  read them as `utf-8-sig`.
- `updateDefinition` **replaces the whole definition**. Send every part,
  including unchanged ones. An omitted part is deleted.
- Use `scripts/plan_def.py unpack|pack` instead of hand-encoding.
- `PlanV1` is the documented format. The existing local packer emits a
  `definition.parts` envelope without the optional format selector; do not
  confuse transport format with a part's `$schema` version.
- Check [versioned public contracts and provenance](upstream-references.md).
  Local structural validation does not replace checking those schema contracts.

## Part map

| Path | Required | Purpose |
|---|---|---|
| `.platform` | returned by getDefinition; optional on create | Item metadata (type, displayName, logicalId) |
| `definition.json` | yes | Semantic model binding + ordered sheet list |
| `planProperties.json` | yes | Theme, edit/read pane config, workload-level filters, variables, sync slicers, drill-through |
| `cube/cube.json` | no | Cube partitions (planning/writeback) — preserve unchanged |
| `connectedPlanning/infobridge.json` | no | InfoBridge — preserve unchanged |
| `sheets/{sheetId}/sheet.json` | yes per sheet | Canvas, page filters, placements of embedded visuals |
| `sheets/{sheetId}/commentSettings.json` | PLANNING/POWERTABLE | Comment settings (observed on REPORTING too — preserve) |
| `sheets/{sheetId}/visuals/{visualId}/properties.json` | yes per owned visual | Visual configuration |
| `sheets/{sheetId}/visuals/{visualId}/writeback.json` | optional | Writeback destinations (observed as empty `destinations` on a slicer) |

`{sheetId}` is the sheet `recordGuid`. Embedded visuals have **no** folder on
the hosting Intelligence sheet; they are owned by the source sheet.

## .platform

```json
{ "metadata": { "type": "Plan", "displayName": "<name>", "description": "<text>" },
  "config": { "version": "2.0", "logicalId": "00000000-0000-0000-0000-000000000000" } }
```

Applied on update only through the Core Items route:
`POST /workspaces/{workspaceId}/items/{itemId}/updateDefinition?updateMetadata=true`,
with the complete definition and explicit metadata intent. Do not append the
parameter to `/plans/{planId}/updateDefinition`. Ordinary rename/description
changes use PATCH metadata.

## definition.json

```json
{
  "$schema": ".../plan/definition/Definition/1.0.0/schema.json",
  "workloadItemName": "<plan display name>",
  "cube": { "partitionRefIds": [] },
  "semanticModelReference": { "...": "see below" },
  "sheets": [
    { "recordGuid": "<sheetId>", "displayName": "Plan Summary", "sheetType": "REPORTING", "isHidden": false,
      "workloadItemEntityVisuals": [
        { "visualId": "<planning visual id>", "visualType": "PLANNING", "isEmbedded": true },
        { "visualId": "<slicer visual id>",  "visualType": "SUPER_FILTER", "isEmbedded": false }
      ] }
  ]
}
```

**semanticModelReference** — two documented forms:

- *Portable* (preferred for new items, supports variable-library references):
  `{ "connection": { "connectionId": "..." }, "semanticModel": { "workspaceId": "...", "itemId": "..." } }`
- *Legacy* (what native exports currently contain, observed):
  required `connectionId`, `semanticModelId`, `semanticModelName`, `semanticModelWorkspaceId`,
  `semanticModelWorkspaceName`, `directLakeMode`, `directQueryMode`,
  `sourceType: "WORKLOAD"`, plus observed `artifactId`, `datasetRelations`,
  `recordGuid`, `url`.

Portable `connection` and `semanticModel` also accept typed variable-library
references. These are strings matching `$(...)`, not invented object wrappers;
resolve an existing library/variable using its documented syntax and expected
`ConnectionReference` or `ItemReference` type. The common schema checks the
string shape, not whether the variable exists. Preserve the reference form
and remap real target references deliberately during clone/rebind.

Use `REPORTING` for this skill's Intelligence sheets. The documented type list
does not contain `INTELLIGENCE`. The published root schema currently restricts
registration `visualType` to module values, whereas native Intelligence exports
also use values such as `INFORIVER`, `ANALYTICS_PLUS` and `SUPER_FILTER`.
Preserve native values and record the discrepancy; do not rewrite them to
Planning enums to force schema conformance.

When editing an exported definition, keep the form it already uses. Rebinding
is a `semanticModelReference` change followed by `updateDefinition`
(management mode), and requires the new model to contain every referenced field.

## planProperties.json

`{ "$schema", "properties": { ... } }`. Required: `workloadModeConfig.EDIT/READ`
(pane visibility: `showDataPane`, `showFieldsPane`, `showElementsPane`,
`showFilterPane`, `showBookmarksPane`, `showCommentsPane`,
`showPersonalizePane`, `showVariablesPane`; `showLumelAIPane` is optional).
EDIT and READ have different required pane sets; both require `showDataPane`,
but READ does not require the authoring-only fields/elements panes. Optional, observed:
`theme {type, appliedThemes}`, `workloadLevelFilterAssignments`,
`workloadLevelQueryFilterAssignments`, `workloadLevelVariables`,
`syncSlicerConfig`, `syncVisualsState`, `drillThroughConfig`,
`reportPageTooltipEntities`, `pageGroupingMeta`, `favoriteCharts`,
`quickMeasureConfig`, `timeIntervalMapping`, `dataStreamerConfig`, `homeLayout`.
The public schema requires `pageGroupMapping` and `pageGroups` inside an
included `pageGroupingMeta`; do not flatten them or delete unknown fields.
Its theme contract is narrower than observed native theme state; preserve
the native state and report the schema discrepancy rather than stripping it.
A UI save keys `theme.appliedThemes` by sheet numeric id (`{"1": {"type": 3}, …}`);
add an entry for each sheet added.

## sheets/{sheetId}/sheet.json (REPORTING)

The documented wrapper is `{ "$schema", "properties": { ...page settings... } }`.
Page-setting keys include (not all are individually required):
`pageLevelFilterAssignments`, `entityLevelVariables`,
`filterPanePosition` (`LEFT|RIGHT|TOP|BOTTOM`), `topPositionFilterExpandConfig`,
`commentary`, `canvasStyle`, `assignmentColumnMap`, `visualGroupMap`,
`sourceVisualsMeta`, `controlPanePosition`. Observed extras:
`excludedFilterContextAssignments`, `filterContextUserConfig`,
`reactiveVisualProperties`.

**canvasStyle** (observed): `background`, `border`, `cornerRadius`,
`dimension {type, width, height, elementScalingUnit:"percentage"}`,
`gridLineSettings {showGridLines, snapToGrid, gridLayoutType, gridRows, gridColumns}`,
`isAutoLayoutDisabled`, `isLocked`, `mobileCanvas`, `scrollToZoom`, `shadow`,
`showSmartGuide`, `showVisualGuide`, `verticalAlign`, `wallpaper`.
Documented example: `type: DEFAULT_16_9, width 1600, height 900`; observed
native: `type: RESPONSIVE, width 1810, height 1051`.

**reactiveVisualProperties** — placement of **embedded** visuals on this sheet:

```json
[{ "visualId": "1", "properties": {
    "position": { "x": 0.21, "y": 0.005 }, "dimension": { "width": 0.785, "height": 0.99 },
    "originEntityId": "1", "lockAspectRatio": false, "visualInteractions": {}, "visualStyles": { } } }]
```

Geometry is **normalized** (0–1 of canvas) on percentage-mode sheets.
A native user-corrected sheet also saves explicit `elementScalingUnit: "pixel"`
with pixel-valued owner placements. Preserve each sheet's declared unit; convert
placements explicitly when cloning between units. Never put pixel placements
on a percentage-mode sheet.

**commentary** — `annotation.settings` and `notes.settings` (display style,
indicator, marker, foot notes). See `features/matrix/notes-and-annotations.md`.

## sheets/{sheetId}/visuals/{visualId}/properties.json

### Public Intelligence container versus observed native visual parts

The [published Intelligence schema](https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/Intelligence/Properties/1.0.0/schema.json)
requires `$schema`, a page `properties` wrapper, and a `visuals` **array**:

```text
properties: {schema, properties: {...page settings...}}
visuals: [{id, visualType, properties: {schema, properties: {...visual config...}, etag?}}]
```

Each visual has an `id` and numeric `visualType`. Preserve embedded/origin
references and stringified internal state. Do not flatten these wrappers,
replace the array with an ID-keyed map, or manufacture extra per-visual parts.

Native exports inspected by this skill also contain the flat owned-visual
shape below. These are distinct evidence shapes, not interchangeable recipes.
Inspect the part's schema and a fresh same-kind readback before editing.
The field-closure helper walks nested objects, but its geometry checks do not
fully validate the public nested container. Check the versioned schema and
rendered layout separately; never claim full schema certification.

### Observed flat owned-visual shape

`{ "$schema", "properties": { ... } }`. Observed keys on owned visuals:

| Key | Meaning |
|---|---|
| `visualType` | Observed codes: 10 Matrix (`INFORIVER`), 50 charts/cards (`ANALYTICS_PLUS`), 60 slicer, 201 shape, 202 text, 203 navigator; 80 is Planning |
| `chartType` | Chart kind string (present even on non-chart visuals) |
| `position {x,y}`, `dimension {width,height}` | Normalized placement |
| `originEntityId`, `preVisualId` | Entity ids (strings). After a UI save every visual carries `originEntityId` = its origin sheet's numeric id (creation order; moving sheets does not change it) and `preVisualId` continues one plan-wide counter |
| `layerProperties {layerProperties:{name, isHidden, groupIds}, order}` | Layers pane name, visibility, z-order |
| `pivotAssignments[]` | Field/measure bindings per bucket |
| `superFilterAssignments[]` | Slicer field configuration + filter state |
| `groupMeasureAssignments[]`, `splitByCategory`, `transformMeasure`, `advanceLookup` | Advanced binding options |
| `sortingConfig[]` | Visual-level sort |
| `visualInteractions {<originId>: {dataInteractionType}}` | Edit interactions (filter / highlight / none) |
| `visualStyles` | Background, border, corner radius, padding, shadow, rotation, tooltip style |
| `lockAspectRatio`, `shapeType`, `groupName`, `mobileProperties` | Misc |
| `visualState` | Engine state (Matrix / Super Filter / chart settings). The public Intelligence schema uses an object; inner groups can contain stringified JSON. Preserve native state and each group's encoding. |

Native reporting evidence recorded in feature files supersedes generic or
Planning-grid assumptions.
In inspected charts, individual groups are themselves JSON strings at
`/properties/visualState/hiddenProperties_!!!_analytics`,
`hiddenProperties_!!!_appearance`, etc. JSON pointers name the stored string;
paths inside its decoded object are identified separately in feature files.
Never replace these with invented `visualState.analytics` keys.

## Bucket assignment objects

Model column (observed):

```json
{ "bucketId": "category", "columnName": "Financial Year", "columnType": "Column",
  "dataRoleType": "Grouping", "dataType": "String", "id": "[Dim] Date[Financial Year]",
  "sourceId": "[Dim] Date[Financial Year]", "name": "Financial Year", "order": 0,
  "sourceType": "PowerBI", "tableName": "[Dim] Date", "isFlatHierarchy": false,
  "formatString": "", "contents": "", "distinctValueCount": 3 }
```

Model measure: `columnType: "Measure"`, `id: "Measure[<name>]"`, plus
`customName`, `measureGuid`, `formatString`. Inserted measures use
`id = sourceId = <19-digit id>` and `tableName: ""`.

Buckets observed: `rows`, `columns`, `ameasure`, `category`. Chart-specific
buckets (series, small multiples, tooltip) must be captured from a native sample.

## Observed visualState groups

**Super Filter (`visualType` 60):** `categoryCustomizeSettings`, `dateSettings`,
`displaySettings`, `facetSettings`, `filterContextProperties`,
`filterHiddenSettings`, `hierarchySettings`, `interactionStateSettings`,
`locale`, `measureFilterSettings`, `playAxisSettings`, `presetSettings`,
`rankSettings`, `readModeToolbar`, `reportMode`, `toolbarSettings`, `visualStyles`.

**Grid engine (`visualType` 80, shared with Matrix — confirm on a standalone Matrix):**
`aggregation_config`, `annotationBox`, `cfProps`, `jet_cfProps`,
`chartCustomTitle`, `columnDimensions`, `rowDimensions`, `columnMeta`,
`embeddedSuperFilter`, `filterContextProperties`, `globalStyles`, `gridStyles`,
`layout {layout_type, measure_layout}`, `measureAttributes`, `manage_measures`,
`miscellaneous`, `numberFormatting`, `page_config`, `pagination`,
`ragged_hierarchy_config`, `ranking_config`, `readModeToolbar`,
`readViewConfig`, `row_height_config`, `row_label_meta`, `themeColors`,
`toolbar`, `totals_config`, `visualStyles`.

Feature files name the group they touch. The group name is evidence of where a
feature lives; the exact values still need a native sample unless the feature
file says `encoding: verified`.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- **Visual part envelope.** Some saved exports wrap a visual's
  `properties.json` in `$schema`, `eventTriggers` and `properties` [saved].
  For a new visual, copy the complete envelope of a same-sheet or same-kind
  donor and replace only the inner `properties` object.
- A new Super Filter part sent with only `properties` passed local JSON checks
  but read back as an empty shell after an import that timed out; the cause of
  the timeout was not established [open].
- **Root keys.** Some exports also carry `appDBconnection` at the root of
  `definition.json` [saved]. Preserve unused root keys; a key's name does not
  establish that it is optional.
- **Legacy binding.** Change the legacy set consistently: a new
  `semanticModelId` alone updates neither `connectionId` nor the workspace ID
  and name. Never write a partial legacy reference.
- **Include `url` when creating.** Supply
  `url: https://app.powerbi.com/groups/<workspaceId>/datasets/<modelId>` in the
  legacy reference of a create payload; it persisted and Matrices initialized,
  whereas Plans created without it failed Matrix startup (`MX-VIS-01`)
  [confirmed].
- **Plan-wide state.** A visual's own `properties.json` does not capture the
  filter, sync, drill-through or tooltip context held in `planProperties.json`;
  preserve that state during visual edits.
- **Home layout.** `planProperties.json → properties.homeLayout` is plan-level
  home-page state, separate from sheets, canvases and visuals [saved];
  inventory and preserve it independently.
- **Companions.** Preserve optional parts when present unless the change
  removes their feature, and never create empty companion files in place of
  native configuration.
