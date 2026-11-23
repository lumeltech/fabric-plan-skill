# Cross-module blend encoding (integration reference)

## Status and use

Read-only integration context for future Planning, PowerTable and InfoBridge
skills, and for recognizing and preserving existing mixed-source plans. This
release does not author any of these bindings; follow
[module boundaries](module-boundaries.md).

Evidence: one native `getDefinition` readback of a Plan whose Intelligence
sheets blend semantic-model measures with Planning-sheet measures and embed
Planning and PowerTable sheets. Encodings are **observed**: saved state only,
with no before/after isolation, runtime or writeback test. Sample names, IDs,
hosts and values are deliberately omitted.

First-party concept ([Blend measures](https://docs.fabricplan.com/planning-sheets/concepts/connected-planning/blend-measures)):
base measures come from the semantic model; live measures (inputs, formulas,
simulations, forecasts) from embedded planning sheets appear under
**From Sheets** in the Data pane; InfoBridge blends external sources.

## Public-reference coverage and limits

The [reviewed upstream definition reference](https://github.com/tmdaidevs/fabric-planning-skill/blob/ce129e8bce4663f3f6f8fff154df3c253c3fc377/references/definition-authoring.md)
documents shared sheet/visual identities, portable references and Intelligence
containers. It does not establish isolated `From Sheets` or `From Queries`
consumer bindings, their runtime behavior, or a new blend-execution endpoint.
The observed bindings below remain observed; the source-aware integration gate
is unchanged.

Keep three concepts separate:

- **Cross-module blend:** model data plus live module measures; preservation
  only in this release.
- **Matrix Blend measures:** two measures displayed in one cell; see
  [Matrix feature](../features/matrix/blend-measures.md). Model-backed use
  remains subject to native encoding evidence, not the cross-module gate.
- **Portable references:** resolve connections/items or typed variable-library
  values. They are not measure lineage or proof that a cross-module binding
  resolves. See [definition contracts](definition-structure.md#definitionjson).

Preserve `sourceVisualsMeta`, `assignmentColumnMap`, visual origin references,
and shared part identities when transporting mixed-source Plans. Do not
rewrite source IDs as model-field IDs, flatten a public Intelligence wrapper,
or copy source-module authoring instructions into the Intelligence namespace.

## Part ownership map

| Part | Future owner | Blend role | Observed shape |
|---|---|---|---|
| `definition.json` → `sheets[]` | Shared | Registers sheets and visuals | `displayName`, `isHidden`, `recordGuid`, `sheetType` (`REPORTING`, `PLANNING`, `POWERTABLE`), `workloadItemEntityVisuals[] {visualId, visualType, isEmbedded}`; top-level `cube {partitionRefIds}` |
| Host `sheet.json` | Intelligence | Places embedded foreign visuals | `reactiveVisualProperties[] {visualId, properties}`; `assignmentColumnMap` for an embedded PowerTable |
| Consumer `properties.json` | Intelligence or Planning | Binds From Sheets measures | `pivotAssignments[]` with `sourceType: "Visual"` |
| Planning `dataInput.json` | Planning | Defines live measures | `columns[] {measureGuid, name, visualId, dataInputType, boundToFilterContext, columnMeta}` |
| Planning `properties.json` | Planning | Grid state | `visualType: 80`, registration `PLANNING`; `visualState.manage_measures[] {id, label, order, visible, width}`, `aggregation_config`, `formatConfig`, `scenarioSettings`, `simulationContext` |
| `writeback.json` | Planning | Writeback destinations | `{version}` stub on most visuals; a configured Planning visual adds `destinations[]`, `excludedMeasureGuids`, `writebackType` and auto/snapshot flags |
| PowerTable `source.json`, `sourceSettings.json`, `columnConfigs.json` | PowerTable | Table source and columns | `source {connectionId, dbHost, dbName, schemaName, tableName, tableType, creationMode, sqlTargetArtifact, meta}`; `sourceSettings[] {name, recordGuid, settings, sourceId}`; `columnConfigs[] {columnGuid, columnName, displayName, columnType, visualColumnType, allowEdit, mandatory, hideColumn, sourceId, columnMeta}` |
| `connectedPlanning/infobridge.json` | InfoBridge | Registers module visuals as query sources | `sources[] {type, name, visualId, sourceGuid, meta, queries[]}`, `linkedQueries[]`, `queryGroups[]` |
| `cube/cube.json` | InfoBridge/Planning | Connected-planning partitions | `cubePartitions`, `cubePartitionMeasures`, `cubePartitionMeasureMappings`, `cubePartitionMeasureDataInputColumnMappings` (empty in the sample) |
| `commentSettings.json` | Shared | Per-sheet comment settings | Present on every sheet; not blend-specific |

PowerTable `properties.json` nests `properties.properties` and
`properties.schema` and has no `writeback.json`. A Planning visual's leftover
`chartType` is not its identity. `infobridge.json` source `meta` holds the
dataset/workspace reference, `dimensions`, `measures[] {id, measureGuid, name,
alias, columnType, dataType, aggregationType}`, `selected*` lists,
`dateOptions[] {fieldType, periodKey, formulaQuery}`, `recordCount` and
`parquetVersion`; each query holds `queryId`, `sourceId`, `type`, `visualId`,
`transformationSteps[]`, `writebackDestinations` and `writebackSettings`.

## From Sheets measure binding

```json
{
  "bucketId": "AC",
  "sourceType": "Visual",
  "customSource": true,
  "visualId": "<source Planning visual id>",
  "tableName": "<source visual display name>",
  "columnName": "<source measure label>",
  "customName": "<display label>",
  "name": "Sum of <source measure label>",
  "id": "<opaque numeric id>",
  "sourceId": "<same opaque numeric id>",
  "measureGuid": "<string or null>",
  "dataRoleType": "Measure",
  "columnType": "Column",
  "dataType": "Double",
  "aggregationType": "sum"
}
```

- Model fields use `sourceType: "PowerBI"`; From Sheets measures use
  `sourceType: "Visual"` with `customSource: true`.
- `id`/`sourceId` are short opaque numeric strings with no Plan-level registry.
  Resolution uses the source `visualId` plus `sourceId` and label; `measureGuid`
  may be null or differ from the source `dataInput.json` GUID. Never synthesize,
  renumber or re-derive them; copy them from a native capture in the same Plan.
- Each binding is mirrored in `splitByCategory.pivotValueAssignments`,
  `superFilterAssignments[].pivotAssignments` and
  `superFilterAssignments[].configuration.sort[]` (`id`, `columnId`). Preserve
  or remap every mirror together. `pivotAssignments` and the Super Filter mirror
  hold the source visual GUID in `visualId`; the `splitByCategory` mirror holds a
  short numeric source handle instead, and mirrors' `measureGuid` can differ.
- Observed consumers: KPI cards (`AC`), integrated columns (`AC` and the `PY`
  comparison bucket), horizontal integrated columns, parallel coordinates,
  treemap and Planning grids (`ameasure`) consuming another Planning visual.
  Live measures can act as actual or comparison scenarios and flow
  Planning → Planning.
- Consumers referenced Planning visuals not embedded on the consuming sheet.
  The saved state allows this; runtime behavior was not tested.

## Planning measure types

`dataInput.json` → `columns[].columnMeta.measure_type`:

| Type | Observed keys | Meaning for consumers |
|---|---|---|
| `Native` | `measure_role` (e.g. `ACMeasure`) | Model or upstream measure shown in the grid |
| `DataInput` | `allow_input`, `bound_to_filter_context`, `column_type` (`Number`, `SingleSelect`, `Person`), `on_change_formula`, `disable_write_access` | User-entered values; persistence belongs to Planning writeback |
| `Forecast` | `closed_period_config.method.LinkToMeasure`, `edit_config` | Forecast linked to an actual measure for closed periods |
| `Formula` | `formula` with `M_<measureGuid>` tokens | Calculated from grid measures, including upstream From Sheets measures |
| `Simulation` | `source_measure_id`, `simulation_range`, `simulation_slider` | What-if value derived from a source measure |
| `VisualColumn` | Nested `DataInput` text, select or person columns | Annotation-style inputs, not numeric measures |

`boundToFilterContext` 10 (native/input) versus 20 (formula) and
`dataInputType` 6/7 were observed; their exact semantics are unverified.

## Embedding

- A foreign visual stays in its owning sheet folder. The host lists it in
  `workloadItemEntityVisuals` with `isEmbedded: true` and positions it with
  `reactiveVisualProperties[].properties` (`position`, `dimension`,
  `lockAspectRatio`, `originEntityId`, `visualInteractions`, `visualStyles`).
  `scripts/plan_def.py validate` already rejects a host folder for an embedded
  visual and an embedded visual without an owning sheet.
- An embedded PowerTable adds `assignmentColumnMap` to the host `sheet.json`
  (also present in the PowerTable `visualState`):
  `{ "<source index>": { "<column label>": { columnId, label, parentPath[], source: "visual", sourceId } } }`.
  `parentPath` is `powertable-<database>-<schema>-<table>`; `columnId` and
  `sourceId` are `<base64 source index>::<base64 table>::<base64 column>`.
- In the sample no Intelligence visual bound a PowerTable column, so PowerTable
  participation was embedding only. PowerTable column bindings in Intelligence
  visuals remain uncaptured.
- InfoBridge registered only one consumed Planning visual as a source; others
  were consumed without registration. Registration is not proven necessary for
  From Sheets measures, and its role remains unverified.

## Validation in this release

`scripts/plan_def.py` checks only `sourceType` None/`PowerBI` assignments
against the field registry. Non-model assignments are handled separately:

- `validate` warns that the plan is mixed-source and lists each From Sheets
  binding (consumer visual, bucket, source `visualId`, `sourceId`, label). It
  errors when a binding's source visual is not registered in `definition.json`
  and warns when the label is missing from the source `dataInput.json`, when a
  numeric-handle mirror has no GUID-form binding, or when another non-model
  source has no source visual. Planning and PowerTable visuals' own internal
  bindings (for example `"powerTables"`) are module-owned and skipped.
- `validate --baseline <decoded readback>` errors on any added, removed or
  changed cross-module binding, enforcing preservation. Without it, a warning
  says preservation was not verified. `fields` lists the bindings separately.
- Report a mixed-source plan to the user, preserve all foreign parts and
  bindings unchanged and apply the module-boundaries blocking rule; never
  create, rebind or delete these bindings.
- Never copy writeback destinations, connection IDs, database hosts or
  workspace/tenant identifiers into briefs or skill references.

## Integration checklist for future skills

- Route ownership: Planning owns `dataInput.json`, `writeback.json` and Planning
  properties; PowerTable owns its source, settings, column and properties parts;
  InfoBridge owns `connectedPlanning/infobridge.json` and `cube/cube.json`;
  Intelligence owns consumer visuals and host placement. Keep shared
  `assignmentColumnMap` copies in sync with the PowerTable columns.
- Add a provenance-aware registry entry per live measure: source module, sheet,
  `visualId`, `sourceId`, label, `measureGuid`, measure type, `M_` formula
  dependencies, aggregation, scenario role, units and filter-context binding.
- Capture before authoring: inserting a From Sheets measure (before/after
  diff), binding a PowerTable column in an Intelligence visual, and creating
  InfoBridge sources, queries and cube partitions. Then extend `plan_def.py`
  with source-aware closure that resolves each `sourceId` in its source module.
- Test: source input or simulation changes reach consumers; renaming or
  deleting a source measure; filter and Super Filter propagation across sources;
  permissions and writeback isolation; readback preserves every foreign part
  except intended edits.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

Preservation and integration context only; none of these bindings or parts
is enabled in this release.

- **More documented module parts.** The official Plan definition article also
  lists Planning visual parts `scenarios.json` and `modelTemplate.json`, and
  PowerTable parts `approvals.json`, `automations.json` and `forms.json`; none
  was seen in this skill's readbacks [open]. They belong to their modules;
  preserve them byte-for-byte.
- **One source, several placements.** A source visual can be embedded on more
  than one host sheet, and each placement is an independent instance [saved].
  Record rectangles by source ID, instance ID and sheet ID; never normalize
  distinct instance rectangles into equality.
- **Local joins.** Host placements can join through a sheet-local ID rather
  than the GUID, and a shared owner without `preVisualId` leaves its placement
  mapping unresolved [saved]. Equal owner and reactive rectangles are not an
  identity-resolution rule.
- **Direct Planning consumers.** Resolve each binding against the actual
  source owner and its input-column `measureGuid`; keep differing split-level
  local identities unresolved [saved]. A simulation input bound in a `PY`
  bucket served as a comparison, not a prior-year calculation [saved].
- **Future registry fields.** Add grain, scenario keys, refresh dependency and
  freshness (saved input versus materialized query state) to the
  provenance-aware registry entry in the checklist above.
- **Future acceptance test.** A connected output keeps the same scenario, key
  and grain before and after an authorized save and refresh, with no double
  counting and no stale-result claim.
