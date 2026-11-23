> v29 execution rule: follow [verified-authoring-flow.md](verified-authoring-flow.md). Import supported inputs, formulas, Forecast and CF together. Use documented native phases only; no reference-only staging shortcut or automatic reduced-scope deployment. The original request and import-contract checks remain authoritative. This supersedes older partial-deployment fallback wording.

> v21 Planning-source mappings: read [infobridge-planning-identity.md](infobridge-planning-identity.md). Constructors derive DI/FORMULA lineage from owner records; destination output reconciliation is bundled. Discover INFOBRIDGE-MAPPING.

> 2026-11-14 active formatting and identity update: read [matrix-formatting.md](matrix-formatting.md) and [dimension-leaf-keys.md](dimension-leaf-keys.md). Use `plan.py format-matrix` for selected typed formatting and `plan.py leaf-key-mapping` for stable leaf storage defaults. These newer, revision-qualified contracts supersede conflicting older general examples; original source documents remain intact. Formatting is offline-tested, not render-certified. The complete existing native CF seed is not claimed to be an exact copy of the newer source constants.

> Current module routing: use [module-routing.md](module-routing.md) or
> `python plan.py discover --module <ID>` for all F01-F30 and cross-cutting workflows.
> It connects business examples to real commands/callables and distinguishes base
> provisioning, separate phases and actual gaps. Preserve the latest targeted
> fixes; historical coverage statements below are release-scoped.

> Forecast review update: use
> [forecast-review-execution.md](forecast-review-execution.md) and the bundled
> `runtime.forecast_review` callables for From Sheets SUM, quarterly
> commentary/variance, negative formatting and comparison charts. This separate
> workload phase requires an approved external adapter and has no current CLI
> route. Do not treat its convenience-provisioner omission as missing code, but
> do report it as unavailable when the adapter profile is unavailable. Forecast
> defaults inherit a working reference, otherwise UTC and
> distribute-to-children=true.

> Maintenance fallback: when a requested PowerTable cannot be bound, deploy a visible native PowerTable sheet with deferred connection using `maintenance-deferred-connection.md`. Do not omit the sheet solely for a connection gap. Preserve chart Visual level field registrations using `chart-visual-filters.md`.

# Connected application construction and graceful deployment

> Active Context/Intelligence construction addendum: read `references/context-intelligence.md`. External Context stays outside the grid and passes the selected scope into Planning; ordinary semantic slicers are separate. The executable constructor now covers Context, slicers, cards, text and page-local embedded geometry. Scenario rows and grid-only dashboards are not equivalent substitutes. Preserve feature-level omissions and separate saved-state checks from behavior verification.

This supplement adds reusable code from an authorized live Plan export inspected on 2026-11-13. It is evidence of saved configuration, not proof of calculation, rendering, refresh, SQL writes or rename persistence. The application contained 21 sheets, 12 InfoBridge queries, five embedded Planning references, three configured dimension mappings and 14 database lookup columns. No reference report, source checkout, export file, credential or environment ID is needed by these constructors. All business names and field choices below are illustrative parameters.

## Continue independent work

The default is the complete requested flow using verified bundled contracts.
Use selected component adapters when a feature needs a separate phase.
`prepare-scope` is a local diagnostic and coverage ledger; `provision` does not
deploy its reduced output when a requirement is omitted or substituted. Keep
unsupported requirements visible, continue independent supported preparation,
and explain exact gaps. A reference-only sheet is appropriate when requested,
not as an improvised replacement for editable planning.

An explicitly requested narrower deliverable may use its supported route. Do
not weaken controls, substitute a different business process, or drop inputs,
formulas and CF to obtain a successful import. The broader adapter catalog still
applies: features absent from the convenience provisioner may have documented
component phases. Read verified-authoring-flow.md before composing them. Never
replace unknown data with zero or deploy formulas with unresolved dependencies.

## Dimension ID Mapping: construct descriptors as well as the map

Use `runtime.dimension_mapping.dimension_mapping(model, assignments, mappings, descriptor_only_assignments=(), skip_support=None)` or `construct-native dimension-mapping`. The normal Planning builder accepts `dimensionIdMappings`, `dimensionSkipSupport` and `lookupContextAssignments` and writes the result at `properties.visualState.dimension_id_mapping`.

Example business grain: Employee x Month, with Scenario as storage context. Display employee names, but persist coordinates against a same-table stable employee key. Department is a descriptive grouping only if the retained Employee key already identifies the intended entity. The observed native strategies are:

```json
{
  "People[Name]": {"ID": "People[Key]"},
  "People[Team]": {"Skip": {}},
  "Version[Name]": {"ID": "Version[Key]"}
}
```

`skip_support={"People[Team]":"People[Name]"}` makes the retained key basis explicit. Skip removes that descriptive level from the coordinate identity; it must not remove an independent business dimension. Do not invent Label/Lookup/Parent variants from this ID/Skip evidence.

Every ID pair requires **both full native descriptors** in `dimension_id_mapping.pivot`. The constructor includes original semantic descriptors and appends the key descriptors, with `aggregation_type`, `bucket_type`, `column_name`, `column_type`, `custom_name`, `external_data_type`, `field_parameter_data_type`, `group_data_type`, `id`, `name`, `order`, `relationships` and `source_type`. It copies the mapped label's role/order to the key descriptor and resolves the key's real data type and name from model metadata. It checks same-table keys, duplicate/conflicting descriptors and explicit Skip support. Native IDs remain separate from business member keys.

The lookup descriptor list is **not** the visible row/column assignment list. Do not add the hidden ID fields to the visible grid. For context-only dimensions, pass explicit semantic descriptor-only assignments alongside the actual context assignment. This adds the lookup pair without adding a row level. It does not configure storage context by itself: author `filterContextSettings`, the actual context dimension/selection, and input binding separately. Do not copy saved filter-context hashes or invent their algorithm.

Before writing inputs, query the current model to check that each key is non-null and identifies the intended entity, that key-to-label lookup is unambiguous, and that the mapping retains the required grain. Period key mapping is not chronological sorting. For an existing populated sheet, changing label/ID/Skip strategies is a coordinate change, not automatic migration. Preserve existing data and plan an authorized migration if necessary. API readback proves the map and descriptors persisted; label-change retention still requires an authorized data test.

## P&L: normalize every contribution before append

The observed application appends workforce, operating expense, revenue, supply cost and a separate discount contribution. It computes gross profit, total operating expense, EBITDA, operating income and signed net result afterward. This is a pattern, not a mandated five-source template.

Choose canonical reporting dimensions, their **order**, exact output aliases, period and scenario, metric names/types, currency and sign convention before building any query. Keep semantic master dimensions on the intended sheet axes and linked query measures in Values. Use `runtime.connected_components.contribution` to add explicitly typed additive contribution measures and finish with a grouping Pivot at the chosen reporting grain. Optional `dimension_formulas` creates explicit account/category dimensions before the metric projection. `append_check` then requires identical ordered roles/names/types and context semantics across every input. `contribution` rejects dropping the declared period or scenario even if the caller's semantics label still says they exist.

`contribution` uses `CAST((expression) AS DOUBLE)` for every contribution metric, including intentional zero contributions, so `0.0` cannot quietly infer a narrower DECIMAL type than other queries. A zero requires `zeroIsValid=true`; it means that stream contributes nothing to that account, not that missing data was substituted. Aggregate detail to the destination grain: removing an Employee or Product column alone is not aggregation. A final Pivot drops unneeded detail and sums additive metrics at the shared grain. Nonadditive rates, margins, prices and balances require their own explicit aggregation/calculation rule; do not sum them using this additive helper.

The exported example itself had reordered Opex dimensions, DECIMAL zero metrics alongside DOUBLE measures, and some incomplete selected-field type metadata. Its append exists, but those details are **not** a model for canonical normalization. Validate the actual materialized output schema; metadata declarations alone are insufficient.

Discounts must be counted once. Either feed net revenue directly with no second discount stream, or feed gross revenue as the initial net contribution and append `net - gross` as a negative discount contribution. With positive cost amounts: gross profit = net revenue - COGS; operating expense = compensation + other operating expense; EBITDA = gross profit - operating expense; operating income = EBITDA - depreciation. Do not adopt these policies where the business uses different signs or account classifications.

`Query.filter_equals` implements the observed Filter Rows operation (`type:180`) with an **array** of clauses, first `condition:"Where"`, then `"And"` or `"OR"`. Each clause contains `operator:{name:"is",value:"="}`, `sourceColumn`, scalar `value`, and configuration-validation flag `isValid`. It resolves current output aliases, checks text/numeric values and accepts the runtime's Decimal JSON numbers. This is the equality branch only. `isValid` is not proof of a successful query job. Use supported separate branches for range/date/null predicates; never guess their shapes.

Audit every transform for unavailable Year/date fields and lost scenario/currency axes. The reference's revenue-driver query had narrow member filters and dropped Scenario; those are report-specific choices, not defaults. Do not inherit them. If a fixed scenario is intended, establish and validate that restriction explicitly before using a special fixed-context route; the general contribution constructor requires the scenario in the output grain.

## Bind linked values using the destination catalog

`runtime.connected_components.bridge_consumer(field, visual_id, measure_id, label, order=0, aggregation='sum')` builds four coordinated objects: `assignment`, `dataInputColumn` (Native measure), `manageMeasure`, and `measureAggregation`. Resolve `field.id`, `queryId`, column/table names, data type and source type from the actual destination InfoBridge output catalog after import/materialization. Do not hash a label to invent the output key. Allocate/resolve the native measure identity using the documented identity domain, and preserve it as a decimal u64 string.

The assignment uses `sourceType:"InfoBridge"`, `customSource:true`, `bucketId:"ameasure"`, `queryId`, exact `id/sourceId`, `measureGuid` and the selected aggregation. The companion Native record uses the same measure identity and destination visual ID. Add all four objects through the existing registration/property writers; assignment-only construction is incomplete. Keep source declaration GUIDs, portable query GUIDs, execution query IDs, output field IDs and runtime visual IDs separate. Use existing reconciliation helpers and fresh catalogs after import.

Initial connected refresh is optional for deployment; the user may refresh manually. Validate saved wiring independently of materialization. When refresh testing is requested, execute upstream source/query jobs in dependency order using the bundled reload/poll/stream adapters and check terminal success, materialized columns, row counts, values and downstream recalculation. Do not seed `recordCount`, `parquetVersion`, `flatData`, success/error caches, old runtime IDs or source job state from a report. A saved graph does not prove edit-trigger propagation. See [business-navigation.md](business-navigation.md).

## Embedded planning: one owner, page-local placement

Use `embedded_planning(owner_sheet, visual_id)` to construct a portable dashboard reference to a directly owned Planning visual. The report export contained five such references. The hidden Planning owner keeps its properties, formulas and inputs; the Intelligence dashboard declares the same portable visual GUID with `isEmbedded:true`. Do not create a second visual identity or duplicate the owner's dataInput part beneath the dashboard.

After API creation/import, read the dashboard's complete native inventory and resolve actual runtime visual IDs. Place the embedded visual in the dashboard's `reactiveVisualProperties` entry using `runtime.layout.place_native`, fresh page ETags and `runtime.layout.audit`. An override's runtime `visualId` is not the portable GUID. Its `originEntityId` must belong to the destination runtime; do not copy the example's small integer strings.

The example uses a 1600 x 1002 canvas with `elementScalingUnit:"percentage"`: position and dimensions are fractions from 0 to 1, not percentages from 0 to 100 and not pixels. It reserves the lower area for a broad rectangular workbench. Derive a fresh layout for the requested content: consistent margins, aligned filter/card rows, a compact navigator and a readable full-width workbench. Validate all neighbors, reserved regions and bounds; preserve source-owner geometry. Use the native page readback to verify the effective rectangle. API geometry does not establish pixel-perfect rendering.

## PowerTable lookup and column construction

`runtime.table_columns.column_config` / `construct-native table-column` supports observed integer/bit, decimal, date, database-lookup and distinct-text-option records from actual SQL metadata. It generates fresh configuration `recordGuid` values. `columnGuid` and `columnName` remain the physical SQL column name. Database-generated identity keys are hidden, read-only and not mandatory input fields. Types, nullability, primary/unique/composite constraints and lengths come from the database; do not invent these from semantic labels.

For a foreign key, the physical key remains the value while `displayName` can show the remote label. The constructor checks the actual lookup table, key/label existence, key type compatibility and single-column uniqueness. A composite relationship needs its own complete contract. Its native shape is:

```json
{
  "columnGuid":"ProductKey", "columnName":"ProductKey",
  "columnType":2, "visualColumnType":3, "displayName":"Title",
  "columnMeta":{
    "selectionMethod":"LOAD_FROM_DATABASE", "options":[],
    "optionLinking":{"lookupConfig":[{
      "id":"ProductKey", "label":"Title", "linkingColumn":"Key",
      "schema":"ops", "table":"Products", "order":0
    }]}
  }
}
```

This abbreviated example omits the generated record GUID, physical `dbMeta` and default/editability fields; use the constructor for the complete record. A distinct text column uses `selectionMethod:"DISTINCT_VALUES"` and an empty `optionLinking`; it is not a foreign-key lookup. Date formatting uses `DEFAULT_LOCALE`; decimal presentation has `noOfDecimals` independently of SQL precision/scale.

Wrap complete records in `PowerTable/ColumnConfigs/1.0.0/schema.json` as `columnConfigs:[...]`. Reconcile with existing records using the bundled preservation-aware helper; omission does not mean delete. Keep these separate from row-save metadata. The portable PowerTable properties part has an additional nested `properties` envelope. The source owns its `recordGuid`; `sourceSettings[*].sourceId` refers to that source record, not the visual. A reference's `creationMode:3` is import-file provenance, not an existing-table requirement. Use native `creationMode:2` when initializing an existing SQL table; do not change modes to conceal a credential failure.

Select authorized SQL base tables with verified keys/lineage. Use the existing initialization, schema/readback and compressed insert/update adapters. Preserve actual returned IDs and settings. Do not copy broad `all_users` row-access filters or enable row deletion just because a sample contains them. Rendering a lookup and saving its underlying SQL key require separate acceptance evidence.

## Intelligence state hygiene and reference auditing

`ANALYTICS_PLUS` and `SUPER_FILTER` state in the export shows chart/card and semantic slicer assignments. Several `hiddenProperties_!!!_*` values are JSON **strings**; others are objects. Preserve the declared type for each property. `plan-readable.json` expands serialized JSON for inspection; it is not a round-trip deployment source. The original decoded parts preserve string encodings.

The reference also contained stale chart-formatting/pivot fields from another configuration, extra test queries, saved member filters and runtime caches. Never copy whole visual-state objects as a universal initializer. Construct selected fields/properties with current identities, validate nested references, and use supported base presentation where full chart styling is unavailable. The observed P&L flat measure list does not prove a complete expandable measure-hierarchy contract.

Run `python plan.py audit-definition decoded.json --out audit.json`. The auditor checks owner/embedded relationships, descriptor completeness, lookup configurations, append schema differences and unresolved query consumers. GUID path matching is case-insensitive and case-colliding paths are rejected. Unknown/incomplete type metadata stays unknown; a matching label does not establish type compatibility. The saved reference passed ownership/mapping-reference checks, but its append schemas were not exactly identical. This audit does not contact the service or mutate anything.

## Verification and delivery

Run `python plan.py test` after extraction. New synthetic tests cover lookup-key/label separation, generated keys, descriptor-only context, missing mapping pairs, duplicate IDs, Decimal filters, append grain/types, scenario loss, Year drift, consumer companions and embedded ownership. Independently test scope fallback with mixed supported/unsupported modules. Preserve the original feature/business/property documents and report their hashes during packaging.

Return the actual saved artifact and the coverage ledger. Clearly separate construction, definition persistence, runtime registration, data operations and visual verification. A narrower deliverable is acceptable only when that is the requested scope; claiming omitted or unverified functionality as complete is not.
