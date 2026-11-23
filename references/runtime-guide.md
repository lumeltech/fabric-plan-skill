> v39: Rows/Columns already define storage grain. External Context is only for additional stored selections, never ordinary page/global filtering. Connected Planning owners must match Context; query outputs must retain it. Read [storage-context.md](storage-context.md) for the bundled guards and build-time query evidence.

> v37: Discover **NATIVE-COLUMN-READBACK** for OneLake `dataInputType` / `columnType` readback compatibility and duplicate-safe resumes. See [native-column-readback.md](native-column-readback.md). Reusable repairs must be promoted to the main skill, shared builder, tests and regenerated Copilot package; see [verified-authoring-flow.md](verified-authoring-flow.md).

> v36: [OneLake storage-mode From Sheets and From Queries](onelake-linked-values.md). The bundled resolvers and native recipe phases accept OneLake catalogs without SQL id/sqlPk and retain the Fabric SQL profile. Use current owner/query metadata; no task-local repair.

> v34: [Saved view reference handling](saved-view-reference.md) adds read-only snapshot/owner audits, Home role-content reads, independent PowerTable details/schema results, and an entity number-parameter constructor. It does not claim arbitrary new bookmark capture or restore.

> v31: [Backend-aware metadata recovery](metadata-backend-routing.md). Discover METADATA-BACKEND for feature-specific Fabric SQL/OneLake operations. Resolve only the collection consumed by the operation; no mutation replay or storage migration. Preserve the same artifact and all prior fixes.

> v30: [Measure-weighted distribution](measure-weighted-distribution.md) is now constructible for the captured Column / All dimensions / another Measure / source Row Use Self profile. Discover RULES or weights from another measure; use `construct-native weighted-rule`. Saved configuration is confirmed, not allocation execution. Other reference profiles and bookmark restore remain separate gaps. All prior fixes remain.

> v29 execution rule: follow [verified-authoring-flow.md](verified-authoring-flow.md). Import supported inputs, formulas, Forecast and CF together. Use documented native phases only; no reference-only staging shortcut or automatic reduced-scope deployment. The original request and import-contract checks remain authoritative. This supersedes older partial-deployment fallback wording.

> Direct numeric-column Values (v28): use [numeric-column-values.md](numeric-column-values.md). Planning, KPI cards and charts default semantic Columns to source Sum when no explicit aggregation is supplied. Planning `sourceAggregation` is independent of grid total settings; saved measure IDs are preserved.

> v27 mandatory navigation: every Intelligence dashboard includes a visible native Page Navigator, even when omitted from the prompt. The standard builder reserves space and the public Plan definition carries its complete state. The completion gate rejects missing controls. Read [the navigation contract](navigators.md#mandatory-dashboard-page-navigation-v27). All v26 padding and earlier fixes remain.

> v26 Navigator defaults: [current construction contract](navigators.md#current-construction-contract-v26). New dashboard Navigators include complete DEFAULT icon/text/shape padding even when icons are disabled. Both factories and the create adapter use the shared completion helper; the application-default gate rejects incomplete authored states. Partial state overrides and current/legacy corner profiles remain distinct.

> v25 CF: discover CONDITIONAL-FORMATTING or F15; read [conditional-formatting.md](conditional-formatting.md). New report specs support sheet.conditionalFormatting directly.

> v24 non-negotiable baseline: Arial, enabled native Home with saved overview/navigation, and Intelligence dashboard coverage for every Planning sheet apply regardless of prompt context. Read [application-defaults.md](application-defaults.md); use the full application builder and completion gate. A component build or a successful definition save alone is incomplete.

> v21 Planning-source mappings: read [infobridge-planning-identity.md](infobridge-planning-identity.md). Constructors derive DI/FORMULA lineage from owner records; destination output reconciliation is bundled. Discover INFOBRIDGE-MAPPING.

> v20: All reports use content-sized rich-text headers plus a small buffer and
> native row/column hierarchy icons `gmate`, independent of business use case.
> Read [report-presentation-defaults.md](report-presentation-defaults.md) and
> discover REPORT-PRESENTATION. Preserve intentional user overrides.

> v19: Every new Planning grid uses explicit row GT Top, row subtotal Top,
> column GT Left, column subtotal null/OFF. Preserve intentional overrides.
> Read [planning-totals-defaults.md](planning-totals-defaults.md). Measure-based
> roll-forwards recommend Measures in Rows + native Measure Model; discover
> ROLL-FORWARD and read [roll-forward-authoring.md](roll-forward-authoring.md)
> plus the complete supplied [formula reference](roll-forward-formula-patterns.md).

> v18: [measure-display-defaults.md](measure-display-defaults.md) is the default: assigned measure cards stay visible at **All**, with no selected values/ranges. Numeric Planning measures use per-measure Auto (`13: "auto"`). Apply dimension selections only to the dimension card itself; preserve all source bindings and intentional existing filters.

> v17: New editable inputs explicitly default to ReadAndEdit. Business-dependent
> locking uses BasedOnFormula with a real, resolved expression. See
> [input-editability.md](input-editability.md); preserve intentional existing locks.

> v16: Read [adaptive-business-authoring.md](adaptive-business-authoring.md)
> before choosing features. Interpret business meaning, compose patterns and
> record parameters and dependencies with `plan-intent`. The five cases are examples;
> `usecase --recipe` accepts supported adaptations. Literal search does not choose
> the business design, and no example rate, date, currency or grain is a default.

> v15: For the five end-to-end business examples, read [five-usecase-recipes.md](five-usecase-recipes.md). `usecase` packages every local and native phase; basic build/provision alone does not execute these complete linked workflows.

> v14 required default: use native integrated variance for bar/column baseline comparisons. Read [integrated-variance.md](integrated-variance.md) for exact selectors, source-preserving commands and business examples. Ordinary single-series bars are unchanged.

> v13: Read [planning-column-presentation.md](planning-column-presentation.md) for dynamic column expansion, selected sizing/default-total rules and native-measure filter cards. Expansion recovery was user-confirmed; the other defaults were subsequently requested. Preserve all existing input and formula identities.

> 2026-11-14 active formatting and identity update: read [matrix-formatting.md](matrix-formatting.md) and [dimension-leaf-keys.md](dimension-leaf-keys.md). Use `plan.py format-matrix` for selected typed formatting and `plan.py leaf-key-mapping` for stable leaf storage defaults. These newer, revision-qualified contracts supersede conflicting older general examples; original source documents remain intact. Formatting is offline-tested, not render-certified. The complete existing native CF seed is not claimed to be an exact copy of the newer source constants.

> Current module routing: use [module-routing.md](module-routing.md) or
> `python plan.py discover --module <ID>` for all F01-F30 and cross-cutting workflows.
> It connects business examples to real commands/callables and distinguishes base
> provisioning, separate phases and actual gaps. Preserve the latest targeted
> fixes; historical coverage statements below are release-scoped.

> Forecast review update: use
> [forecast-review-execution.md](forecast-review-execution.md) and the
> `runtime.forecast_review` callables through an approved external adapter. The
> separate workload phase is bundled but has no current CLI route. Report it as
> unavailable if the adapter profile is unavailable. Forecast defaults inherit a
> working reference, otherwise UTC and distribute-to-children=true.

> Current Forecast policy: forecasting requests use native Forecast with closed periods linked to actuals. Unspecified open defaults use None/Blank; explicit formula or measure defaults remain editable. Read `forecast-authoring.md` and use `runtime/forecast.py` through the composed constructor.

> PowerTable closure: use `powertable-alm-construction.md` and `configured_table` for the complete grid/source/columns/settings route. Maintenance fallback: when a connection genuinely cannot be bound, deploy a visible uninitialized sheet using `maintenance-deferred-connection.md`. Keep the completion distinction explicit. Preserve every chart Visual level field registration using `chart-visual-filters.md`.

> Current extension: read `connected-construction.md` for dimension ID mappings, PowerTable lookups, normalized contributions, embeds and the per-module fallback policy. Continue independent supported work using documented phases; v29 forbids automatic reduced-scope substitutes.

> Active Context/Intelligence construction addendum: read `references/context-intelligence.md`. External Context stays outside the grid and passes the selected scope into Planning; ordinary semantic slicers are separate. The executable constructor now covers Context, slicers, cards, text and page-local embedded geometry. Scenario rows and grid-only dashboards are not equivalent substitutes. Preserve feature-level omissions and separate saved-state checks from behavior verification.

# API-only Fabric Plan construction

The [Intelligence index](intelligence/index.md) routes detailed
[discovery](intelligence/discovery.md), [design](intelligence/design.md),
[authoring](intelligence/authoring.md) and
[management](intelligence/management.md) guidance. Use those references for
feature decisions and native-part context, then execute through this runtime
and the latest [skill contract](../SKILL.md). Retained standalone `scripts/`
commands are not bundled runtime dependencies; use `plan.py discover --module
INTELLIGENCE` for supported commands and limits.

The single SKILL.md bundles this runtime, its pinned dependencies, schemas, tests and the original detailed business/property guides. Extract locally and work entirely through HTTPS APIs. Do not use native UI steps, browser automation, source checkouts, previous reports or user-written JSON repairs. Historical UI instructions in preserved references explain product behavior; they are not an execution fallback.

## Exact completion boundary

The current release includes offline constructors and public Plan lifecycle
operations. Optional service-specific adapters are described in
[builder-integration.md](builder-integration.md) and require an external,
organization-approved profile.

It does **not** close the entire requested product feature surface. Read `api-contract-gaps.json` before promising completion. A missing request contract is not repaired by passing an arbitrary descriptor, copying an old snapshot or renaming a UI step as an API step. There are no UI fallback actions in this workflow. Complete independent authorized work and report the precise missing API contract when a required capability is blocked. Never silently omit a requested capability.

Construction, public-schema acceptance, native registration, persisted state, native calculation, input persistence, automatic propagation, effective authorization and rendered behavior are separate evidence stages. For imported Planning grids, the public definition export records the saved configuration. They do not establish native calculation, input editing, event-driven refresh, native bookmark application or rendered layout. API checks can verify geometry; they cannot establish text clipping or visual appearance by themselves. Do not add a UI-verification dependency when the user requires APIs only; report that evidence boundary.

## Prerequisites and discovery

Python 3.11+ is required. Node 24+ with system CA support is needed for the optional managed-Windows HTTPS adapter and the bundled LZUTF8 role-metadata decoder and PowerTable row encoder. All library code needed by these tools is inside the capsule; no npm/pip installation is needed. Credentials, authorized workspace/model/source access, service availability and actual source data remain runtime prerequisites.

Resolve the documented public `apiBase`, workspace ID and semantic model ID from
the current request and actual metadata. Do not derive or guess service hosts.
Optional service adapters use `applicationService` and `engineService` profiles
supplied outside this repository.

Fetch current model metadata/definition and inspect tables, columns, measures, relationships, partitions, keys, periods, scenarios and policy measures. Construct `current-model.json` in the bundled `fixtures/model.json` format using actual identities. The fixture is syntax documentation, uses reserved synthetic IDs and an `.invalid` URL, and must never be deployed. A model's source connection and the workload's semantic connection have distinct identity domains. Resolve an authorized PowerBIDatasets connection and actual model webUrl; do not select by a coincidental position or display name alone. Source SQL credentials need the SQL audience; a Power BI token is not a SQL token.

Define grain first, then columns/values, editable inputs, default sources, calculations, time/version context, policy and dependencies. Use the feature guide to choose the appropriate functional design. The agent writes the spec; the business user should not be asked to supply enum values or manually repair JSON.

## A complete executable route for the verified subset

`plan.py provision` sends the full definition and final visibility in the public create request, then aligns each dashboard and saves Home. Supported base
inputs, formulas, Forecast and CF are included together. It inventories the
request and writes scope-coverage.json, but returns mutation:none before live
creation when the convenience path would omit or substitute requirements. Use
the selected documented component recipe for those phases; do not deploy a
filtered reference-only substitute. buildRequest/importContract and candidate
checks protect the original base contents. Read verified-authoring-flow.md.

Configuration uses environment variable names, never token values:

```json
{
  "apiBase": "https://resolved-fabric-api.example.invalid/v1",
  "workspaceId": "actual-workspace-guid",
  "name": "Requested application name",
  "tokenEnvironment": "FABRIC_TOKEN",
  "authorizedMutation": true
}
```

`authorizedMutation` records the user's existing scope; it is not an additional approval flow. It does not override missing permissions. Assign `FABRIC_TOKEN` through the authorized credential channel or a process-only environment. Set `FABRIC_PLAN_HTTP_NODE` to the actual installed Node 24+ executable when Python HTTPS cannot connect; secrets travel to that child over stdin, never persisted files or argv. TLS verification remains enabled. For role metadata without that adapter, set `FABRIC_PLAN_NODE` to the installed Node executable.

```text
python plan.py provision --config current-config.json --model current-model.json --spec current-spec.json --run run/create
```

Add to the authored spec, alongside `name` and `sheets`:

```json
{
  "requiredCapabilities": ["planning.native-measure", "planning.numeric", "planning.formula", "planning.pivots", "home.text", "home.cards", "home.visibility"],
  "home": {
    "roleId": "__everyone__", "order": 1, "show": true,
    "blocks": [
      {"key": "intro", "type": "text", "title": "Planning workspace", "description": "Review assumptions, update the plan, and compare outcomes."},
      {"key": "sheets", "type": "preview-cards", "columns": 4}
    ],
    "rows": [{"blocks": ["intro"]}, {"blocks": ["sheets"]}]
  }
}
```

Add the requested Planning sheets using the bundled syntax examples. Preserve registry, sheet and visual IDs for updates. On a new report, `provision` stores the construction and journals the hash of the public create request. Resume using the same run directory and inputs. If the create response is lost, reconcile that operation before issuing another create.

`acceptance.json` reports what was actually established. It deliberately leaves engine/input/propagation/rendering stages unverified. The original APIs were exercised live; the newly composed `provision` orchestrator is tested offline and must not be described as a separately executed full live scenario.

## Expanded builder adapters

Read [builder-integration.md](builder-integration.md) for typed factories and
the optional external service-adapter boundary. Use `construct-native` offline;
`builder-api` requires an approved route/authentication profile supplied outside
the repository. The `provision` command remains restricted to its stated subset;
no missing orchestration is implied.

## Individual construction and lifecycle commands

```text
python plan.py build --model current-model.json --spec current-spec.json --out run/build
python plan.py validate run/build/raw.json --out run/preflight.json
python plan.py api create --config current-config.json --payload run/build/envelope.json --run run/create --label create-with-definition
python plan.py api export --config target-config.json --run run/export --label fresh-export
python plan.py api update --config target-config.json --payload candidate.json --run run/update --label apply-reviewed-change
python plan.py decode definition-envelope.json --out run/decoded
```

For export/update config include the actual returned `planId`. For the generic update CLI supply `baselineSha256`, the SHA256 of the canonical sorted map of part paths to their raw-byte SHA256 values. This is recomputed against a fresh export before mutation. Use `codec.patch` to replace only named parts while preserving unrelated InlineBase64 bytes. Updates use a fresh baseline, but the public API does not document a server-side compare-and-swap; do not claim the local hash check is one.

Lifecycle routes: POST `/workspaces/{workspaceId}/plans`; POST `.../plans/{planId}/getDefinition`; POST `.../plans/{planId}/updateDefinition`. Blank create sends only `displayName`; initialized create/update sends the full `definition.parts` envelope. For 202 follow Location or operation ID, honor Retry-After, poll terminal status and retrieve the operation result. `transport.Client` journals mutation intent, safe response headers and operation checkpoints. Ambiguous submissions are reconciled before any retry. Do not log credentials. An operation's Succeeded state is not proof of native behavior.

## Exact identities and complete Planning records

`identity.py` implements seed-zero XXH3 with 272 upstream vectors, string u64 validation and a collision registry. Use the correct exact external key and aggregation convention. Native, Number DataInput and Formula constructors in `construct.py` emit full column records, native `columnMeta`, measure registrations, per-axis aggregation, formatting and explicit context. Numeric defaults/bounds are native tagged operands, not flattened values. Formula references resolve through the local registry; reject missing references and cycles. Input and Formula are distinct tagged variants. Do not invent permission fields, caches, activation leases or hydrated success states.

A version/period policy uses the real model policy measure in a positive conditional AllowInput expression. Configured conditional editability does not prove a rejected API edit, effective RLS or scenario isolation. Source assignment dimensions, native context binding and user security are separate.

Saved Pivot specs use symbolic `key`, `name`, `rows`, `columns`, optional `measures`, and `hidden`. `pivots.compile_pivots` creates the native All config (xxh3 of `default_pivot`), allocates stable named IDs, resolves axes and rejects invalid cross-axis combinations. Null retains the base axis; [] explicitly removes it. Named configs cannot have both axes null. Pivots change grouping over the same input identities; they do not create another plan or scenario.

## External service adapters and post-import resolution

`session.native_session` uses the configured Power BI service root and token
environment to obtain an artifact-scoped workload session. Dashboard placement
identifies the embedded grid from its source and dashboard pages. The public
Plan definition carries the grid measures.

```text
python plan.py native home --config target-config.json --input home-request.json --run run/home --label home
# The public definition carries direct visual rectangles and page-local embedded matrix placement.
# Saved Pivot activation requires an approved external adapter; no current CLI route.
```

Service request inputs are generated from the current registry: Home
`{roleId,layout,order,show?}`; approved external placement
`{entityId,visualId,rectangle:{x,y,width,height},gap?}`; and Pivot
`{entityId,visualId,pivotId}`. `pivotId:null` selects All. A persisted-property
result does not claim that a controller fired or that an engine calculation ran.

## Home content, priority and visibility

Use `surfaces.home_item` with `home_fit.readable_home_layout` for new Home content; `workflow.compile_home` uses it automatically. Text and card rows get flexible widths and content-driven heights, with text stacked when content width is unknown. Numeric widths are pixels, never percentages. Read [Home layout fit](home-layout-fit.md) for the narrow-column regression, sizing checks, scoped repairs and rendered acceptance boundaries. `home_fit.audit_home_fit` inspects saved layouts without changing them; `native.save_home` rejects clearly narrow text widths before network submission. The low-level `surfaces.home_layout` remains available for deliberate dimensions. Minimal Lexical paragraph/text strings are bundled. Unique item/instance/row identities, special-block ownership, dimensions and references are validated. Never put HTML into Lexical or fabricate an asset source.

Absent V2 content is a successful `{data:null,etag:null}` response, not necessarily HTTP404. Existing content requires its current ETag. Save `{homeLayoutOrder,data,etag?}`, read exact content/ETag back, then read role metadata separately to verify priority and content-enabled state. The list response uses LZUTF8/Base64 in the tested environment. Its MIT decoder is pinned and included in `vendor/lzutf8`; no package fetch is needed.

Visibility belongs to `planProperties.json.properties.homeLayout.show`.
`home_api.visibility_via_alm` freshly exports, changes that one subtree,
preserves unrelated payload bytes, updates, polls and re-exports. Home role
content and visibility remain separate paths. Optional content, asset, priority
and effective-audience operations resolve through an external service profile;
see [builder-integration.md](builder-integration.md). Advanced nodes and legacy
migration remain unclosed.

## Geometry and ownership

`layout.py` and the retained JS helper implement geometry planning/auditing. Account for every current visual, margins, gaps and reserved region. Prefer an aligned summary area, compact navigation strip and wide rectangular planning workbench below. Respect actual canvas units: percentage coordinates use fractions. No-fit is explicit, never an origin fallback or silent shrink.

The full page response carries direct visual ETags at `visual.properties.etag` and page ETag at `payload.etag`. Embedded geometry belongs to the page's unique `reactiveVisualProperties` entry; direct visual geometry belongs to its own property wrapper. Never move a hidden source to position an embed. Save fresh ETags and preserve unrelated properties, then reread and audit bounds/overlap/source preservation. Already-matching state is verified without replaying a completed write.

`navigator_api.py` now constructs the supplied complete state, registers product/type 203, saves actual ETags and checks geometry/preservation. Its new corner-radius profile is kept distinct from earlier fixtures. `native.embed_sheet` and general `native.create_visual` remain documented adapters; all other initialized Intelligence visual factories and embedded registration are not fully covered. Neither offline Navigator tests nor saved geometry establish complete live dashboard behavior.

## Connected planning and maintenance contracts

Read `references/infobridge-construction.md` for synthetic construction
contracts. Treat InfoBridge as a general transformation/delivery utility, with
conditional SQL for numeric and text results. Use the offline constructors for
Planning/PowerTable sources and query operations, and use an external profile for
execution. Reconcile field catalogs, source selectors and portable/runtime IDs;
never invent caches, materialized paths or successful jobs.

A registered graph is not executed data. `builder_api.py` now implements query reload, targeted job notification polling and scoped binary output retrieval, including RLS preparation responses. Use explicit returned job identities and verified status-field mappings. The demonstrated persisted transformation branches now have constructors. Additional unobserved operators, generated import acceptance, output decoding/registration and edit-trigger propagation remain unverified. Do not label a local arithmetic demonstration as native output.

PowerTable eligibility requires actual business-dimension intent, verified Direct Lake lineage and a SQL base table with key/column metadata. Explicit table requests are handled separately. `surfaces.PHYSICAL_METADATA_SQL` and `powertable_source` are bundled. `powertable_factory.py` and `builder_api.py` now supply existing-table initialization, details/schema reads and compressed insert/update serialization/submission. Complete per-kind presentation settings, terminal job mapping and actual row persistence acceptance remain incomplete. Array import semantics may delete omitted configs; preserve complete existing collections. Do not use an old PowerTable as a construction template.

Bookmark records, full native snapshots and Navigator registration must all exist together. Native public upsert/readback and new Navigator host registration are implemented from the supplied contracts. Exact capture-options/snapshot construction, all nested portable mappings and bookmark application remain unclosed. A visible styled control or public record alone does not prove Pivot restoration. Preserve the detailed business/property guidance without treating missing implementation as supported.

## Validation and handoff

Run `python plan.py test`, `node tools/visual-placement.cjs --self-test`, and `python tools/audit_report_definitions.py --self-test`. The last helper has seven tests, no --coverage option. Extract only SKILL.md into a clean unrelated folder and repeat to detect hidden dependencies. Preserve credential-free payloads, journals and per-stage evidence in the task workspace. Do not ship account inventories, customer exports or tokens inside the capsule.

Return the actual Plan link and files requested, what was constructed/registered/persisted, and exactly what remains unverified or blocked. A requirement for complete end-to-end planning must stay incomplete while required input operations, native calculations, connected refresh or feature construction contracts are missing. The API-only constraint is absolute; unsupported behavior is reported, never silently implemented with UI steps.


## 2026-11-13 filter, KPI, query-identity and connection correction

The self-contained [consumer repair contract](consumer-repair.md) supersedes sparse KPI-store examples, lowercase filter-pane positions and any assumption that native input-record row IDs are query output-column IDs. It also records semantic-model/workspace intake and generic FabricSql OAuth connection selection. Preserve the detailed business/use-case guidance above. API readback is not rendered or financial-propagation proof.

## Planning integrity checks (v8)

Read [planning-integrity.md](planning-integrity.md). Missing known GlobalStyles
defaults are completed by build/format-matrix, and grouping field references use
canonical model names across assignments, filters and lookup metadata. Run
`check-planning-properties` before saving or `repair-planning-properties` to produce
an explicit candidate. Bundled Plan/property-batch writes reject violations.
These are offline checks; they do not require report runtime validation.

## Required presentation defaults (v9)

Read [planning-presentation.md](planning-presentation.md). Normal application builds
require rich Intelligence dashboards above their embedded Planning grids. The
complete native TEXT header writer and semantic measure palette are executable
through present-planning; build/provision apply new-application defaults. Use
check-application-presentation for offline coverage. These defaults preserve the
v8 integrity checks and all prior Forecast, formatting, From Sheets and storage fixes.
Explicit requests to skip runtime validation still take precedence; use the
verified identity/ETag reads and save-only placement options described there.


## Measure source binding (v10)

Read [measure-source-bindings.md](measure-source-bindings.md) before assigning or
replacing measures. Use `resolve-measure-binding` for exact PowerBI/Visual/InfoBridge
identities and typed metadata. Native companion records are not sheet outputs.
Reconcile ordinary filter cards with changed chart assignments; captions alone
do not identify a source. Preserve the prior formatting, forecasting and layout fixes.


## Required application baseline (v11)

Home is mandatory alongside rich Planning headers, measure colors and embedded
Intelligence dashboards. Read [application-defaults.md](application-defaults.md).
Use `check-application-defaults`; verify Home content, role metadata and workload
visibility separately. Do not silently downgrade a complete application to grids
or dashboards without its native landing page. Retain all source-binding fixes.


### v38 recipe adapter integration

Recipe extensions and quarterly review delegate all column creation to `runtime.builder_api.create_column`. The adapter resolves the current collection route before writing and validates existing/saved records with the OneLake type alias. Do not hard-code a v1 column POST in a recipe. Existing identities and pending-job boundaries are preserved.
