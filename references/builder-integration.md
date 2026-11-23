> v37: Discover **NATIVE-COLUMN-READBACK** for OneLake `dataInputType` / `columnType` readback compatibility and duplicate-safe resumes. See [native-column-readback.md](native-column-readback.md). Reusable repairs must be promoted to the main skill, shared builder, tests and regenerated Copilot package; see [verified-authoring-flow.md](verified-authoring-flow.md).

> v36: [OneLake storage-mode From Sheets and From Queries](onelake-linked-values.md). The bundled resolvers and native recipe phases accept OneLake catalogs without SQL id/sqlPk and retain the Fabric SQL profile. Use current owner/query metadata; no task-local repair.

> v35: Saved measure-weighted rules are Planning-owner configuration. Row/All/Measure/CurrentYear and the earlier Column profile have constructors; use the verified engine route or the documented ETag-aware saved-state writer and check readback. See [measure-weighted-distribution.md](measure-weighted-distribution.md). [SQL definition discovery](sql-definition-discovery.md) supplies actual PowerTable keys/types without a separate SQL login.

> v34: [Saved view reference handling](saved-view-reference.md) adds read-only snapshot/owner audits, Home role-content reads, independent PowerTable details/schema results, and an entity number-parameter constructor. It does not claim arbitrary new bookmark capture or restore.

> v31: [Backend-aware metadata recovery](metadata-backend-routing.md). Discover METADATA-BACKEND for feature-specific Fabric SQL/OneLake operations. Resolve only the collection consumed by the operation; no mutation replay or storage migration. Preserve the same artifact and all prior fixes.

> v30: [Measure-weighted distribution](measure-weighted-distribution.md) is now constructible for the captured Column / All dimensions / another Measure / source Row Use Self profile. Discover RULES or weights from another measure; use `construct-native weighted-rule`. Saved configuration is confirmed, not allocation execution. Other reference profiles and bookmark restore remain separate gaps. All prior fixes remain.

> v29 execution rule: follow [verified-authoring-flow.md](verified-authoring-flow.md). Import supported inputs, formulas, Forecast and CF together. Use documented native phases only; no reference-only staging shortcut or automatic reduced-scope deployment. The original request and import-contract checks remain authoritative. This supersedes older partial-deployment fallback wording.

> Direct numeric-column Values (v28): use [numeric-column-values.md](numeric-column-values.md). Planning, KPI cards and charts default semantic Columns to source Sum when no explicit aggregation is supplied. Planning `sourceAggregation` is independent of grid total settings; saved measure IDs are preserved.

> v27 mandatory navigation: every Intelligence dashboard includes a visible native Page Navigator, even when omitted from the prompt. The standard builder reserves space and the public Plan definition carries its complete state. The completion gate rejects missing controls. Read [the navigation contract](navigators.md#mandatory-dashboard-page-navigation-v27). All v26 padding and earlier fixes remain.

> v26 Navigator defaults: [current construction contract](navigators.md#current-construction-contract-v26). New dashboard Navigators include complete DEFAULT icon/text/shape padding even when icons are disabled. Both factories and the create adapter use the shared completion helper; the application-default gate rejects incomplete authored states. Partial state overrides and current/legacy corner profiles remain distinct.

> 2026-11-14 active formatting and identity update: read [matrix-formatting.md](matrix-formatting.md) and [dimension-leaf-keys.md](dimension-leaf-keys.md). Use `plan.py format-matrix` for selected typed formatting and `plan.py leaf-key-mapping` for stable leaf storage defaults. These newer, revision-qualified contracts supersede conflicting older general examples; original source documents remain intact. Formatting is offline-tested, not render-certified. The complete existing native CF seed is not claimed to be an exact copy of the newer source constants.

Current authoring rules: read [forecast-time-intelligence.md](forecast-time-intelligence.md)
for non-composite calendar axes, one-time Visual Columns and shared versus local
as-of controls. Read [formula-equality.md](formula-equality.md): native comparisons
use `==`; single `=` is reserved for variable declarations. These rules supersede
older comparison examples; original supplied documents remain preserved.


> Current module routing: use [module-routing.md](module-routing.md) or
> `python plan.py discover --module <ID>` for all F01-F30 and cross-cutting workflows.
> It connects business examples to real commands/callables and distinguishes base
> provisioning, separate phases and actual gaps. Preserve the latest targeted
> fixes; historical coverage statements below are release-scoped.

> Forecast review update: use
> [forecast-review-execution.md](forecast-review-execution.md) and the
> `runtime.forecast_review` callables through an approved external adapter. The
> phase is bundled but has no current CLI route. Forecast defaults inherit a
> working reference, otherwise UTC and distribute-to-children=true.

# Standalone builder contract integration

The offline factories and optional service adapters are bundled directly in the
runtime. Service endpoints and authentication details are intentionally not
bundled; execution requires an organization-approved external profile.

The attachment supplies implementation evidence rather than live deployment evidence. This integration implements the closed portions as local factories and API adapters. It does not turn unresolved contracts into supported features or rename persistence as calculation. No live API calls were made for this integration.

## What the attachment resolves

| Area | Newly bundled implementation | Remaining boundary |
|---|---|---|
| Native columns | Nine typed metadata/create factories, optional select `advanced` style, optional VisualColumn, Formula, explicit inner configuration ID, native context encoding, create/readback and companion registration | Inner ID policy must come from the selected factory; async provisioning jobs, value edits/evaluation, Forecast and full lookup/row-model factories are not closed |
| Dynamic Cube contract | Current `MultiDimensionSettings` validation for `cubeModel:"DYNAMIC"`, per-key lookup dimensions and preservation of saved DataInput/Forecast `cube_partition_measure_id`/`cube_model` bindings | This validates request/final saved shapes only; Cube provisioning, refresh and allocation remain unclosed |
| Rules | New wrapper; Lock; Equal, SelfWeight and ManualInput row distribution; captured Column and Row/CurrentYear measure-reference profiles; symbolic weighted-rule factory; Planning-state save and readback; tagged MinMax | Engine mount/auth profile when using New; allocation execution, additional period ranges and reference profiles |
| InfoBridge | Query inventory/meta/transforms; bodyless query reload; targeted notification polling; job/worker alias mapping; RLS-pending versus Parquet stream handling | More transformation factories, source-reload body, output decoding/catalog verification and edit-triggered downstream propagation |
| PowerTable | Existing-table create payload; create/details/schema adapters; insert/update row serialization with vendored LZUTF8; explicit save route/version | Returned source/visual mapping, terminal job response schema, full typed presentation settings, physical row readback and other write operations |
| Bookmarks | Public slug-keyed upsert, fresh ETags, independently read persisted capture, safe replay | Complete capture-options/snapshot factory, all nested portable references and restore/application API |
| Navigator | Complete supplied state, new product/type 203 registration, fresh ETags, geometry and state readback, preservation of neighbors | Target compatibility, owner registration behavior and navigation/rendering have not been checked live |
| Home | Multipart PNG/JPEG/SVG upload, scoped asset metadata readback, fileId-to-imageConfig mapping, explicit PUT/POST provider choice, role-order PATCH and effective layout GET | Route compatibility, effective audience policy, asset rendering, rich Lexical/legacy migration branches |

The broad statement that all these route contracts are missing is now obsolete.
The narrower boundaries above remain real. `api-contract-gaps.json` is the
machine-readable inventory; `implementation-status.json` records the sanitized
offline evidence and the external adapter boundary.

## Runtime files and CLI

The agent authors command inputs from current business requirements and actual API metadata. These are internal execution files, not a request for the business user to edit JSON.

| CLI action | Function and input fields |
|---|---|
| `construct-native input` | `input_factories.input_create(measure_id,label,kind,settings,configuration_id,...)` |
| `construct-native formula` | `input_factories.formula_create(measure_id,label,formula,measures,...)` |
| `construct-native cube-settings` | `cube_contract.multi_dimension_settings(referenceMeasures,newPartitions,existingPartitions,...)` |
| `construct-native rule` | `rule_factories.new_rule(logical_id,name,rule_type,rows?,columns?,measures?,disabled?)` |
| `construct-native powertable-source` | `powertable_factory.existing_source(table,connection,explicit?)` |
| `construct-native powertable-rows` | `powertable_factory.row_save(metadata,operation,records,conditions?,visual_meta,relations?,generated_keys?)` |
| `construct-native navigator` | `navigator_api.state(kind?,page_target?,bookmark_target?,web_url?,selected_pages?,hidden_bookmarks?,caption?,palette?)` |
| `builder-api column-create` | `{visual_id,payload,version?}`; `payload` is the native factory output |
| `builder-api column-register` | `{entity_id,visual_id,payload,row_aggregation,column_aggregation,format_entries,visible?}` |
| `builder-api rule-create` | `{payload}` plus config engine mount verification |
| `builder-api bridge-inventory` | `{workload_id}` |
| `builder-api bridge-query` | `{query_id}` |
| `builder-api bridge-reload` | `{query_id}`; preserves returned job IDs |
| `builder-api bridge-poll` | `{workload_id,job_ids,event_id_fields,status_field,timestamp_field?,query_id?,target_visual_ids?,aliases?,max_polls?,interval?}` |
| `builder-api bridge-stream` | `{source_id,skip?,limit?}`; writes returned binary separately |
| `builder-api powertable-initialize` | `{payload}` from existing-table constructor |
| `builder-api powertable-schema` | `{source_id}` resolved from actual returned source |
| `builder-api powertable-save` | `{source_id,payload,version,route_shape}` |
| `builder-api bookmark-upsert` | `{slug,capture}`; complete capture required, not synthesized from a caption |
| `builder-api navigator-create` | `{entity_id,visual_guid,navigator_state,rectangle,pages,bookmarks,gap?}`; catalogs must be current |
| `builder-api home-upload` | `{path,workload_id}`; existing authorized image bytes |
| `builder-api home-priority` | `{orders:[{roleId,homeLayoutOrder}]}` |
| `builder-api home-effective` | `{}` |

```text
python plan.py construct-native input --input authored-input.json --out native-column.json
# Invoke the listed builder_api callables through an approved external adapter.
python plan.py native home --config destination-profile.json --input home-request.json --run run/home --label home
```

Each operation writes credential-free evidence, carries actual response identities forward, and reports its exact completion stage. Reuse the run directory and stable label for the same operation. Uncertain submissions are reconciled before further writes. Do not change a label to bypass uncertainty or an ETag conflict.

The `provision` command now prepares a supported scope and coverage ledger before its narrower internal validator. Unsupported modules are isolated instead of vetoing independent creation. The component adapters remain separately callable phases; they are not automatically a universal business-request compiler. Try those adapters before choosing a fallback, and report each alternative or omission. See `connected-construction.md` and `runtime/scope.py`.

## Destination profile and compatibility choices

Public API and workload/engine APIs use different authentication contexts. Resolve the real environment and workload token origin with `session.native_session`. The CLI requires explicit `builderApiBase` and `builderSurface`; it does not invent a proxy mount by replacing hostname strings. The builder base must share the token metadata's trusted origin. A different engine host needs its separately established authentication contract; this adapter will stop rather than send credentials there.

```json
{
  "apiBase": "https://resolved-fabric-api.example.invalid/v1",
  "powerbiApiBase": "https://resolved-powerbi-api.example.invalid",
  "workspaceId": "actual-workspace-guid",
  "planId": "actual-created-plan-guid",
  "tokenEnvironment": "FABRIC_TOKEN",
  "authorizedMutation": true,
  "builderSurface": "application",
  "builderApiBase": "https://metadata-returned-host.example.invalid/verified/application/mount",
  "targetVisualId": "actual-numeric-visual-id",
  "homeWriteMethod": "PUT"
}
```

This is syntax documentation using invalid placeholder endpoints; never submit it. `authorizedMutation` records existing user authorization. `targetVisualId` is needed for context-scoped PowerTable operations. Rule submission additionally requires `builderSurface:"engine"` and `engineRulesMountVerified:true`, set only after confirming the selected destination mount and authorization. A Boolean is not verification by itself.

| Contract difference | Explicit treatment |
|---|---|
| Home content method | The selected external profile defines the supported method. Set `homeWriteMethod` deliberately; never retry another verb after an ambiguous mutation. |
| Native context binding | Inner `bound_to_filter_context` is Boolean. The implemented outer profile is 10=true, 20=false. Legacy 0/1 polarity was not established; that profile rejects instead of guessing. |
| Column create versions | V31 checks the documented V1/V2 column catalogs independently, then uses the selected documented column writer. Explicit versions are strict; no mutation fallback. Readback uses the same selected version. Read success alone does not prove write capability. Async column jobs are pending, not InfoBridge jobs. |
| PowerTable URL | `version` must be v3/v4 and `route_shape` must be `source-qualified` or `context-only`. The frontend and validator forms are separate evidence; no automatic fallback rewrites. |
| Navigator appearance | New `navigator-builder-20261112.json` uses the supplied `topLeft/topRight/bottomRight/bottomLeft` corner names. Earlier `navigator-spec-*` fixtures retain their documented legacy shape. Never merge both sets into one version. |
| Bookmark identities | Logical slug, portable recordGuid and runtime visual/page IDs are distinct. Native upsert uses slug. Portable import mappings are documented separately; no recursive find-and-replace of all IDs. |

## Phase-specific acceptance

### Inputs, formulas and rules

Resolve actual native IDs with the bundled collision-safe registry. `configuration_id` is intentionally explicit because the attachment does not establish one universal relationship between that inner ID and outer `measureGuid`. Do not use an empty ID merely because a synthetic fixture does. Resolve the selected factory's behavior first.

Nine typed factories cover Number, ShortText, LongText, SingleSelect, MultiSelect, Date, Person, Checkbox and Simulation. They enforce known enum/tag shapes, stable select values, UTF-8 byte limits, finite numerical values, bounds and required Simulation settings. Unknown branches are rejected. An options-source marker of Lookup is not a complete lookup binding. Formula constructors resolve symbolic references and preserve the optional VisualColumn wrapper.

Column creation and companion registration are separate phases. Verify both the inner metadata and outer context/type/name identity in the current native catalog. Then preserve the owner's existing properties while registering measure order/visibility, per-axis aggregation and formatting under current ETags. A queued provisioning response is not registered. The native engine's input-edit, calculation and lock-enforcement tests remain separate.

The rule factory distinguishes logical `rule_id` from the backend-generated persisted rule ID. Manual allocation weights require nonnegative values and a positive total as conservative builder policy; this does not prove the engine's rounding, lock exclusion or total conservation. Only the documented Row/CurrentYear and Column measure-reference profiles are accepted; additional period-range/reference syntax is rejected. After an accepted rule write, resolve its returned persisted ID and check execution separately.

### Connected refresh

Keep the existing graph/append grain validation. Reload the actual query using the documented bodyless POST. Poll only returned job record IDs, explicitly mapping a returned worker execution ID when necessary. The notification's exact ID/status/timestamp field mapping is an environment profile, not a guessed field name. Source evidence gives status meanings: 100 queued, 210 running, 200 success, 211 partial failure, 400 failure, 499 cancelled.

Empty events, unrelated successful events and partial failures never complete the run. All expected jobs must succeed; timestamps prevent an older event in a later poll from regressing completed work. ISO timestamp strings must have a consistent normalized format before lexicographic ordering; supply numeric timestamps or normalize a verified response profile when formats differ. Missing or contradictory statuses stop verification.

The Parquet route may return HTTP202 with user/RLS preparation jobs. Poll them and retrieve the same scoped stream again. A PAR1 container check is only binary retrieval; no Parquet decoder or financial-value proof is implied. To accept connected planning, compare actual source and consumer values, dimension grain and financial totals after execution. Automatic edit-trigger propagation requires its own observed API evidence; a manual reload cannot establish it.

### Maintenance

Initialize an authorized existing SQL table with creationMode 2 only after the three source eligibility gates. Carry forward the returned source object and actual owner visual identity; do not assume the source object is a scalar ID. Read its details and schema before constructing rows.

The serializer writes inner JSON, LZUTF8/Base64, then outer octet JSON. It preserves Unicode, large integers and decimal precision. Inserts follow exported metadata order and omit only independently verified database-generated keys. The documented empty create rowIds and empty update oldRecords arrays are accepted; they do not establish a complete audit trail. Updates require complete scalar primary-key conditions, editable scalar values, explicit changed-column names and valid audit metadata types. SQL type/domain conversion still requires the actual schema; decimal strings are not silently changed to floats.

Writeback submission remains `rowsSaved:not-verified`. Inspect the bundled job list/log/error routes from the attachment, resolve their actual terminal response schema, and independently reread physical rows. Never equate a submitted job with a saved table. Delete, upsert, replaceAll, distribute and SCD semantics are not mapped to ordinary inserts/updates.

### Navigation and Home

Construct Navigator state from the new fixture, validate every page/bookmark reference against current catalogs, preflight geometry before creation, register product/type 203, and save full state under `visualState.navigatorState` with actual page/visual ETags. Preserve all neighboring state. A created visual lacking the expected ETag response remains a retained incomplete identity; do not create a duplicate. Bounds and overlap checks do not prove clipping/rendering.

Public bookmark persistence accepts a complete captured snapshot only. It fetches fresh state/ETag, skips already-matching state, verifies returned ETag correspondence and rereads the capture. The generic synthetic snapshot in tests is deliberately not a product capture recipe. The missing capture/restore contracts remain listed.

For Home, upload actual permitted image bytes using multipart file/workloadId/feature fields and scoped workload authentication. Validate returned and reread fileId, workload, feature, MIME and size. Use the opaque `fileId` as `imageConfig.source`; do not substitute a URL. Save content with the selected provider method, then verify role order and workload visibility separately. Read effective user layout to inspect audience selection. These operations are nontransactional: retain receipts and recover owned state; never delete assets speculatively.

## Offline test evidence

Run `python plan.py test` with Node configured for the compressed payload tests. New suites exercise all nine input factories, explicit unsupported branches, lossless row serialization, write-route choices, job ownership/failure/staleness, bookmark ETags/replay, Navigator registration/geometry/preservation and Home upload/provider behavior. Tests use synthetic records and blocked network connections. A second independent pass found and drove fixes for seven validation defects plus documented empty-array compatibility. Test success establishes local construction and adapter behavior, not live service compatibility.
