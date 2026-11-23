---
name: fabric-plan-skill
description: "Create and update native Fabric Plan applications from business requirements and semantic models. Follow verified bundled flows; preserve inputs, formulas, Forecast and CF during import. Enforce Arial, enabled Home, Intelligence and complete Page Navigators. Supports numeric Values with default Sum, native CF, formula equality, forecasting, connected planning, InfoBridge, PowerTable, dimension mapping and selected measure-weighted rules. Supports anchors for business-grain assumptions and hidden repeated instances with native XXH3 dimension hashing, including first-anchor creation. Includes Fabric SQL/OneLake From Sheets and From Queries bindings, bounded metadata recovery, saved-rule and import checks. Use for Plan authoring and repair, not ordinary Power BI reports."
---

# Fabric Plan - GitHub Copilot skill

This expanded skill includes its runtime, examples, schemas, reference guides and
offline tests. No capsule extraction, Codex-specific tool, source checkout or old
report is needed. Use Python 3.11+; Node 24+ is needed by the applicable compressed
payload/HTTPS adapters. Start with `plan.py discover`, then read selected guides.

## Current contract and precedence

This file is the current operating contract. The versioned sections below are
supporting history and feature evidence; their version ordering is not the
authority. When wording conflicts, use the current order below:

1. This section, the authoring/publication/transport matrices, the mandatory
   delivery gates and the essential invariants.
2. `plan.py discover`, `references/module-routing.json`, the selected topical
   guides and the implementation they reference.
3. Dated release notes and historical evidence.

### Application profiles

| Profile | When it applies | Required behavior |
|---|---|---|
| New complete application | User asks to create a complete Plan application | Apply the full application baseline: Arial, native Home, Intelligence dashboard coverage, Page Navigators and the complete requested business scope. |
| Extension | User asks to add a feature or module to an existing application | Add only the requested and dependent surfaces; preserve unrelated state and rerun affected baselines and delivery gates. |
| Scoped repair | User asks to fix one existing behavior, visual or property | Preserve the rest, avoid unrelated expansion and verify only the affected and safety-critical surfaces. Full new-application defaults do not authorize unrelated writes. |
| Read-only/reference | User asks for inspection, design, audit or a reference deliverable | Do not mutate a live artifact. Package or hand off only the explicitly requested output. |

Record the selected profile before planning. Do not relabel a scoped repair as a
new complete application or silently narrow a new complete application.

### Transport and execution boundary

| Route | Current role | Authoritative execution |
|---|---|---|
| Public Plan definition | Default creation, export, update, geometry, visibility, definitions and readback | `plan.py build`, `provision`, `api`, `decode`, `encode`, validators and documented local helpers |
| Native Home | Role-specific Home layout and visibility work permitted after explicit authorization | `plan.py native home` and the integrated Home save/readback phases |
| Approved external service adapter | Native column, rule, bookmark, Navigator, PowerTable, InfoBridge, placement or forecast-review work whose route is outside the public definition | Invoke the named Python callable only with an organization-approved profile; not a shipped CLI command |
| Unavailable contract | Any route without a documented public factory or approved adapter profile | Do not invent an endpoint or UI fallback. Prepare independent work, record the gap and return `mutation: none` unless the user explicitly approves revised scope |

The presence of a parser choice or runtime module is not a route unless its
command passes the active `plan.py` guard. `plan.py discover` must show only
reachable CLI commands; callable-only phases identify their Python symbols.

## Packaging and publication boundary

Treat the local project tree, the skill distribution bundle and the published
Fabric Plan as separate deliverables.

- **Publishing a report:** publish only the validated Plan definition and its
  required report assets through the documented Fabric workflow. Never upload
  or attach the repository folder or `_build/` as part of the report.
- **Sharing the reusable skill:** package the skill instructions and only the
  references, scripts, assets and native samples needed to use it. Exclude
  `_build/`, `_brief/`, `_samples/`, generated caches such as `__pycache__/` and
  task-specific outputs by default. Include a particular build artifact only
  when the user requests it or a documented dependency requires it.
- **Before packaging:** verify the bundle's file list against the allowlist
  below; confirm required relative reference paths and native-sample paths still
  resolve; then report excluded generated/work-in-progress content. If an
  excluded sample is a documented dependency of an included guide or workflow,
  include only that reviewed dependency at its expected relative path and record
  the exception. Never ship a broken required reference or include an entire
  workspace just to satisfy one dependency.

### Skill-bundle allowlist

- Root instructions and entry point: `SKILL.md`, `plan.py`, `README.md` and
  `LICENSE`; include `.gitignore` only when present and needed.
- Required runtime resources: `runtime/`, `references/`, `schemas/`, `tools/`
  and `vendor/`, including required licenses and transitive dependencies.
- Only the `examples/`, `fixtures/`, `tests/`, approved assets and reviewed
  native samples needed by the included instructions, workflows or checks.
  Directory membership alone does not approve every file for distribution.

| Local directory | Purpose and distribution rule |
|---|---|
| [assets/](assets/) | Design templates, themes and evidence resources. Include only required, reviewed reusable assets; do not treat this directory as permission to publish every asset with a report. |
| [_samples/](_samples/) | Native export/reference samples. Exclude by default; include particular sanitized samples only when requested or required by a documented dependency. Preserve required sheet/visual paths and filenames. |
| [_brief/](_brief/) | Task-specific requirements, field registries and design contracts. Local working material, excluded by default; keep new task briefs outside the installed skill. |
| [_build/](_build/) | Local workspace for generated definitions, validation evidence and readbacks, not a report dependency or default skill-bundle content. Keep new task outputs outside the installed skill. |

Review any explicitly included output or sample for credentials, live target
identities and confidential business data. Synthetic GUIDs alone do not make an
export safe to share. This instruction defines the packaging boundary; it does
not authorize a report publication, upload or release.

## Intelligence reference routing

For Intelligence work, run `python plan.py discover --module INTELLIGENCE`
and open the [Intelligence index](references/intelligence/index.md). Select
only the mode and feature files needed for the current request:

| Need | Intelligence guide |
|---|---|
| Model-backed report requirements and field inventory | [Discovery](references/intelligence/discovery.md), then its linked continuation |
| Visual choice, layout, accessibility and design brief | [Design](references/intelligence/design.md) |
| Native definition parts, visual configuration and focused edits | [Authoring](references/intelligence/authoring.md), then its linked continuation |
| Export, publish, update and readback considerations | [Management](references/intelligence/management.md), then its linked continuation |
| A missing semantic-model measure | [Model measures](references/intelligence/model-measures.md), only with explicit model-write permission |
| Matrix, charts, KPI, slicers, tables and canvas features | [Feature master list](references/intelligence/feature-master-list.md), then the relevant area index and feature file |

These are bundled Intelligence references, not a separate skill or execution
toolchain. The latest application defaults, source-aware bindings and deployment
rules in this file remain authoritative. Use the shipped `plan.py` routes and
bundled runtime instead of historical `scripts/` commands in retained guides.
Keep task briefs, decoded definitions and operation journals outside the skill
root. The [module boundaries](references/intelligence/core/module-boundaries.md)
explain ownership; they do not disable supported Planning embeds, From Sheets or
InfoBridge bindings. Feature IDs are Intelligence-local; qualify them as
`intelligence:<ID>` in cross-module records. Native `encoding` status and
`[saved]` / `[confirmed]` / `[open]` evidence retain their existing meaning and
do not establish runtime acceptance.

## Semantic model discovery (v47)

Run `python plan.py usecase model --config destination.json --run runs/model`
to discover the configured semantic model through the public Fabric API.
The command requests the model's Tabular Model Definition Language (TMDL)
representation, reads the supported table declarations, and normalizes the
current measures/columns into the field catalog at
`runs/model/current-model.json`. It writes the raw model definition beside that
catalog. This standalone command takes only the destination config and run
directory.

## New report deployment and embedded sheet visibility (v48)

Use `plan.py provision` for standard reports. In the initial public
`POST /v1/workspaces/{workspaceId}/plans`, set
`definition.json` -> `sheets[].isHidden` to `true` on each Planning sheet whose
grid is embedded in a visible Intelligence dashboard. Keep its dashboard visible
and use it as the Explorer and Home destination. A Planning sheet without a
visible embed stays visible by default. Keep business PowerTables visible and
enable Home in the submitted plan properties.

Apply this default in multi-sheet and custom recipes too. A request for a Home
card for each planning activity points to each activity's dashboard. Preserve
the owner's sheet ID and grid ID for editing, formulas and From Sheets links.
Carry the visibility flags through subsequent definition updates and handoffs.

### v50 API contract for every deployment

Author the canvas, direct visual rectangles, navigation, visibility and
embedded matrix placement in the public Plan definition. During fresh builds,
the runtime declares Planning sheets and their direct visuals first and derives
the numeric string origin entity ID and visual ID only from that generated
declaration sequence. Use that pair in each dashboard's
`sheet.properties.reactiveVisualProperties` entry and reuse it when dashboards
share a matrix, while writing each page's own position and dimension. This
order-based calculation is the sole fresh-build exception; it is not permission
to infer identities for an existing or imported destination. Keep GUIDs for the
source sheet, visual declarations, part paths and connected measure bindings.

Use native workload calls only for role-specific Home layout through the shipped
route. Other workload operations are not CLI capabilities; they require an
explicitly approved external adapter profile or remain unavailable. For existing
Plans, preserve the destination's saved placement IDs when updating geometry
through the public definition. For imports with unknown allocation order, obtain
the mapping from that destination before changing placement. A public export
verifies the saved definition. Verify visible placement in Reading mode. In the
MSIT Mid Market validation, a GUID-keyed override survived export while the
matrix rendered over the header.

## Size Intelligence dashboards for the Reading view

When the prompt leaves layout open, use the builder's left-rail layout. Put the full-width header first, the vertical Page Navigator above the left-hand slicers, the embedded Planning matrix at the top of the main area, and equal-sized charts beneath it. Both columns finish at the same baseline. When a user specifies another arrangement, pass that geometry in the dashboard's `layout` option. See [Intelligence dashboard layouts](references/context-intelligence.md).

For each dashboard, identify the primary work area and size the matrix for readable rows and periods. Fit every adjacent chart and filter column to the same content baseline. Reserve space for fixed headers and navigation, subtract the gutters, and allocate the remaining height across the flexible containers in that column. Give comparable charts equal heights. Give comparable slicers equal space and allow a slicer with more choices a larger share. Use `runtime.stack_layout.fit_stack(top, bottom, gap, weights)` to calculate positions and heights together so rounding preserves the final edge.

Use the drawable width and height inside the Reading view, excluding open
panes, toolbar and zoom controls. With fit-to-width, the available height in
canvas units is `canvas width x drawable height / drawable width`. If a viewport
is unavailable, state the assumed target aspect ratio. Recompute positions from
the selected canvas and content on each page. For a matrix with content below
it, reserve the lower visuals and their gutters before assigning its height.

In addition to checking bounds and overlaps, measure the bottom gap of **each column** against the target Reading viewport. When a matrix has additional pages, extend the page-local embedded matrix into the available space and refit the adjacent stacks. Check the final edge of the last chart, matrix and last slicer against the common baseline within one canvas unit. Apply the same principle across rows for horizontal layouts. Treat the geometry calculation as a prediction for the target viewport, and distinguish saved dimensions from observed row counts.

Pass the measured drawable dimensions as dashboard `viewport` when available. For a custom design that should use extra height, describe its flexible rows in `layout.fitColumns`. The builder fits each declared column to the common bottom margin, retains fixed rows and gaps, and checks the final rectangles. Treat an explicitly specified fixed canvas as fixed. Keep the placement identities of an existing embedded matrix when changing its rectangle. See the custom column example in [Intelligence dashboard layouts](references/context-intelligence.md).

Range Control Room is a regression example. A 2240 x 960 page had a 24-unit
bottom margin yet left roughly 400 screen pixels below its content in a
2523 x 1491 drawable area. At that same width a 1320-unit canvas lets a matrix
starting at y = 196 use 1100 units of height with a 24-unit bottom margin. These
dimensions apply to this example.

## Current package property reconciliation

The current packages contract adds dynamic Cube request settings and saved
bindings that older guides omitted. `MultiDimensionSettings` accepts
`cubeModel:"DYNAMIC"` and per-key `lookups`; saved DataInput/Forecast records can
carry `cube_partition_measure_id` and `cube_model:"DYNAMIC"`. Use
`construct-native cube-settings` for the local source-contract shape and preserve
returned cube identities; this does not close Cube provisioning, refresh or
allocation acceptance.

Matrix number formatting accepts `autoLocaleNumberFormat` and the
`"1000000000000"` scaling wire value. The auto-locale value is feature-gated:
new host visuals can default it to true, while existing reports retain their
explicit saved value. New Planning constructions also preserve the frontend
grand-total row-height seed in `row_height_config.custom_row_height`; never move
row heights into `globalStyles`. Requested row heights are native `u32` values,
not fractional pixels.

Planning aggregation accepts every current native scalar method plus the tagged
`WeightedAverage` / `WeightedAverageRow` variants. Resolve a weighted measure
symbolically and preserve a row weight as an exact native string ID. Single- and
multi-select inputs preserve optional `advanced` style metadata. Formula rows
can use the native `LEAVES` row-member identifier when their target context
supports it.


## Anchor measures and native dimension hashing (v43)

Consider anchors when an assumption belongs at a broader business grain than
the detailed plan, or is needed by leaf formulas but should not repeat at every
hierarchy level. Read [anchor-measures.md](references/anchor-measures.md) and
[anchor-business-cases.md](references/anchor-business-cases.md); discover F20.
The full PPT text/notes, worked arithmetic, saved JSON shape and package-only
example are bundled. Use the real decision grain; preserve detailed formulas,
ReadAndEdit/formula locks, source identities and existing distribution.
`display_at_all_levels: false` hides repeated instances where supported; it does
not delete values, hide the whole measure, grant input rights or create a lookup.
The supplied hash contract is now implemented in the bundled builder. It creates
the first anchor in a new report or updates an existing owner without a donor
hash. Use per-measure `anchor` options in base builds, or the scoped anchor helper
for existing typed measures. The hash uses ALL ordered dimensions in the current
pivot, not only selected anchor dimensions. Read [dimension-hashing.md](references/dimension-hashing.md).
Required entry totals are exposed; stale saved hashes are rejected. The temporary
v42 authoring suspension is lifted. All v40 and earlier fixes remain.

## Actual and forecast review boundaries

For QTD/full-quarter reviews, resolve actuals for closed months before aggregating
forecast-only driver outputs. Keep missing actuals distinct from a deliberately
zero forecast-only movement. Read [actual-forecast-review.md](references/actual-forecast-review.md).

## Native chart typography completion (v40)

The service can expand chart styles after import with non-Arial defaults, even
when the authored definition uses Arial. The public-definition path must author
Arial and pass the offline application-default checks. A native
`finish_native_typography` helper exists for an explicitly approved external
service-adapter profile; it is not automatically invoked by `provision`,
`usecase deploy`, or another shipped CLI route and is therefore not a default
delivery claim. When that approved route is selected, it performs fresh reads,
normalizes documented font/style boundaries, saves with current ETags, and checks
readback without changing formulas, bindings or stored inputs. Do not apply it
during an unrelated scoped repair. Read
[native-typography.md](references/native-typography.md). Report native
typography as pending when the approved phase was not run. All v39 and earlier
OneLake, Context, navigator, aggregation and conditional-formatting fixes remain.

## Storage Context and connected consistency (v39)

Rows and Columns already define the input storage grain. Do not repeat those
dimensions in Context. Add Context only for a field outside the axes when the
saved input must be stored against its single selected member, commonly Scenario
or Version. Page filters, global filters and ordinary dashboard slicers affect
the view; they do not add storage dimensions. Do not create unnecessary Context.

From Sheets and From Queries must preserve the same storage Context across
source and destination owners: semantic fields, ID mappings and selected
scenario/version. Never replace source Version with destination Year/Quarter.
The shared recipe guards and query-lineage check reject mismatches before writes.
Existing populated storage coordinates require a retention/migration plan before
changing their Context. Discover **STORAGE-CONTEXT** and read
[storage-context.md](references/storage-context.md). All v38 and earlier fixes
remain; configuration checks do not establish runtime input isolation.

## Storage-aware native recipe creation (v38)

For OneLake artifacts, recipe extensions and quarterly review now use the shared
`create_column` adapter. It validates the current owner catalog, selects that
collection's established v1/v2 route before a write, accepts the v37 readback
aliases, and resumes matching saved columns without duplicate creation. Pending
column jobs stop dependent registrations. Never blindly replay a failed mutation
at another URL. All earlier CF, navigation, mapping and OneLake link fixes remain.
Read [native-column-readback.md](references/native-column-readback.md).

## OneLake native-column readback and portable repairs (v37)

For Plan artifacts in **OneLake storage mode**, saved native columns may return
`dataInputType` instead of the create payload's `columnType`. The bundled builder
accepts that readback alias while rejecting conflicting/wrong types and retaining
metadata, identity, name and context checks. Resume with the same owner and
measure ID: a matching current record returns `already-matched` without another
create POST. Do not rename write fields or bypass validation. Discover
**NATIVE-COLUMN-READBACK** and read
[native-column-readback.md](references/native-column-readback.md).

Whenever authoring reveals a reusable local repair, promote it into the main
skill, shared bundled builder and regression tests, then regenerate the GitHub
Copilot package from that same source. Update discoverable guidance and verify a
clean extraction without task-local scripts, cached reports or chat history.
A task-only patch is not completion of a reusable fix. Preserve all earlier
fixes and exclude credentials, target identities and task-specific business data.
Follow [verified-authoring-flow.md](references/verified-authoring-flow.md).

## OneLake storage mode: From Sheets and From Queries (v36)

These are storage-mode-specific binding contracts for **Plan artifacts in OneLake
mode**, including migrated artifacts. Inspect the current artifact's native
catalogs; do not assume Fabric SQL row IDs exist. From Sheets uses source
`measureGuid` as `id/sourceId` when the current column record has no `id`.
From Queries uses the current opaque query `id` plus selected output-field ID
when `sqlPk` is absent/null. Retain the numeric row-ID/sqlPk routes for Fabric SQL.
Never invent SQL IDs, switch storage modes, or replace a direct sheet link with
an InfoBridge pipeline just because a SQL-only property is absent.

The bundled binding resolver, registered-measure resolver, forecast-review and
business-recipe phases handle both modes. Discover **ONELAKE-CONSUMERS** and read
[onelake-linked-values.md](references/onelake-linked-values.md) before constructing
either route. Use the bundled helpers and package-only example; do not index
`record['id']` or `query['sqlPk']` in a task-local workaround. Initial refresh stays
optional. Correct saved wiring is distinct from runtime calculation verification.
All earlier CF, allocation, Home, hidden-owner and navigator defaults still apply.

## Planning measure-weighted row rules (v35)

Saved allocation rules belong to the Planning owner, including when that owner
is embedded in Intelligence. A current saved UI example verifies **Row / All
dimensions / another Measure / CurrentYear weights**. Use
`measure_weighted_rule(..., axis="Row", weights_period="CurrentYear")` and the
current owner's target/weight IDs. Read
[measure-weighted-distribution.md](references/measure-weighted-distribution.md).
The weighting period is distinct from destination period/scenario scope. Retain
the Column profile separately; never swap axes to fit a missing constructor.
Bookmarks are optional requirements, not a prerequisite for saved allocation
rules, Page Navigators, or Intelligence dashboards.
Use the current Planning owner, including when it is embedded in Intelligence.
`runtime.planning_rule_state.save_rule` persists the complete rule through the
existing ETag-aware properties batch route and checks exact readback. Keep this
configuration evidence separate from runtime redistribution, locks and totals.
For requested PowerTables, discover actual physical keys and types through the
authorized Fabric SQL definition export when needed; see
[sql-definition-discovery.md](references/sql-definition-discovery.md).

## Saved view and PowerTable reference handling (v34)

For a reference containing bookmarks, navigators, shared Planning embeds,
parameters, Home or PowerTable, discover **SAVED-VIEW-REFERENCE** and read
[saved-view-reference.md](references/saved-view-reference.md). Use the bundled
reference audit, native bookmark reader and Home role-content reader. Native
bookmark measure IDs differ from the export's label-only entries; current page
parameters are not automatically part of older bookmark snapshots.

PowerTable details and physical schema are read independently, preserving partial
success without claiming writeback. The number-parameter constructor emits a
fresh, consistent page/Planning-variable bundle. Arbitrary new bookmark capture
and runtime restore remain distinct from observed saved configuration. Keep the
verified authoring flows and all earlier defaults, including optional initial
refresh, hidden Planning owners and shared dashboard embeds.

## OneLake query consumers (v33)

Treat storage profiles separately using current metadata. Fabric SQL query Values
use `sqlPk[outputFieldId]`; OneLake query Values use the actual registry
`id[outputFieldId]` when `sqlPk` is absent/null. Preserve the query and output IDs
as exact strings, including Q-prefixed IDs. Never invent a numeric replacement.
The bundled consumer resolver, execution map, Planning builder and Intelligence
cards/charts handle both forms. Discover **ONELAKE-CONSUMERS** and read
[onelake-query-consumers.md](references/onelake-query-consumers.md).
Initial refresh remains optional. Saved wiring and runtime results are separate.
New-report page visibility is included in the public create definition. Formula descriptors that the
service relabels DI are reconciled only against the same export's exact owner
records by `export_lineage.reconcile` before re-import. No previous graph or repair script is needed.

## Business navigation and optional initial refresh (v32)

Expose native Home, Intelligence dashboards with their actual embedded Planning
visuals, and requested PowerTables. Hide the underlying standalone Planning
sheets; preserve their owners, inputs and connections. The bundled application
builder and completion checks enforce this navigation default. Home cards exclude
current owner pages, and dashboard Page Navigators exclude hidden pages.

Initial InfoBridge refresh is optional and may be performed manually by the user.
Do not block deployment solely on initial materialization when the saved wiring
is valid. Verify current source/query/consumer identities and context separately;
missing bindings still need resolution. Never describe skipped refresh or data
propagation checks as passed. Discover **BUSINESS-NAVIGATION** or **INITIAL-REFRESH**
and read [business-navigation.md](references/business-navigation.md).

## Backend-aware metadata recovery (v31)

Plan metadata is Fabric SQL by default; OneLake-enabled new or migrated artifacts
use OneLake. Do not treat V1 `findAll` / `findPaginatedRows` as a global outage.
Discover **METADATA-BACKEND** and read
[metadata-backend-routing.md](references/metadata-backend-routing.md).
For feature-specific operations that consume metadata, session helpers use the documented SQL/OneLake
GET routes independently for entities and columns, retain validated profiles for
the same artifact, and stop after the bounded alternative fails. No mutation
replay, storage migration or blanket version rewrite. Resume the existing Plan.

Preserve all prior fixes and the complete base import. Catalog recovery does not
prove financial results, new writes or dashboard rendering. OneLake InfoBridge
`Q...` query identities must not be coerced into the numeric SQL consumer profile.

## Measure-weighted distribution is supported (v30)

For saved allocation rules using another measure's weights, discover **RULES**
or "weights from another measure" and read
[measure-weighted-distribution.md](references/measure-weighted-distribution.md).
The bundled `construct-native weighted-rule` command now constructs the captured
**Column / All dimensions / Measure / source Row Use Self** profile with exact
native IDs. It also supplies saved-rule comparison and an isolated example.
Do not substitute Equal, SelfWeight, parent-input distribution or an improvised
flow. Keep inputs, formulas, Forecast and CF in the established base import.

The Column source rule is confirmed in properties and Fabric export; the v35
Row profile is separately captured. Neither proves runtime execution of a newly
generated rule. Unobserved reference profiles still require their own contracts.
Period/scenario, locks and totals need runtime validation.
The separate bookmark capture/restore gap remains. All prior fixes are retained.

## Verified build flow is mandatory (v29)

Follow the established bundled flow; do not invent a replacement workflow.
Import supported semantic Values, Number inputs, formulas, Forecast and CF
**together**. A separate typed/native feature is never a reason to strip other
components or deploy reference-only placeholders. Use documented recipe phases
only, preserve the original request, and check the candidate before import.

`build` captures `buildRequest` and verifies `importContract`. `provision` refuses
to deploy an automatically reduced scope; `prepare-scope` is local diagnosis.
Resumed constructions and candidates are checked again. Unsupported typed metadata
cannot silently become a Number input. Native metadata failures first use the documented bounded SQL/OneLake read
profile (v31); failures of both handlers stop dependent writes. Never replay a
mutation at another version or create duplicate Plans. Continue independent supported work; explain precise capability
gaps instead of changing the business flow.

Discover **VERIFIED-AUTHORING-FLOW**, "reference-only import", "stripped inputs",
"findPaginatedRows", or "planning grid validation". Read
[verified-authoring-flow.md](references/verified-authoring-flow.md) before composing
an end-to-end build. This rule supersedes older automatic partial-deployment
fallback wording. All prior defaults and fixes remain. Offline checks establish
these safeguards, not a repair of backend initialization or live UI behavior.

## Direct numeric-column Values default to Sum (v28)

When the intended metric is a numeric semantic Column rather than an explicit
DAX measure, assign it directly to Values with `aggregationType: "sum"` by
default. Preserve the Column identity and honor explicit source aggregation.
Do not create a DAX wrapper or promote numeric dimension codes to measures.

Planning Native specs use `sourceAggregation` for the source query, separately
from `aggregation` / `columnAggregation` for grid totals. Intelligence cards,
charts and automatic dashboards use the same source-aware factory. Existing
registered measure IDs survive UI aggregation changes; never rehash them during
reuse. From Sheets and InfoBridge retain their own source identities.

Discover `NUMERIC-COLUMN-VALUES`, "implicit measure", "direct column assignment"
or "default sum". Read [numeric-column-values.md](references/numeric-column-values.md).
The isolated example at `examples/numeric-column-values/build.py` needs no old
report, chat or task script. The synthetic Sum fixture covers the saved shape;
package checks do not establish runtime calculation. All prior fixes remain.

## Mandatory Page Navigator on every Intelligence dashboard (v27)

Every new Intelligence dashboard must include a visible native **Page Navigator**,
even when the prompt or reference omits navigation. `build` / `build_application`
now add `BI_RUNTIME_INPUT` / `203` with `PAGE_NAVIGATOR_TABS`, complete Arial and
padding defaults, and a reserved strip above each embedded Planning grid. Tabs
include all normal visible pages; `selectedPages` is omitted so no cached IDs or
empty selection can break navigation. Buttons and bookmark tabs do not replace it.

The public create request includes the full Navigator state and its rectangle. The completion gate rejects missing, hidden or unregistered controls,
incorrect tab kinds, restricted targets, incomplete padding and invalid placement.
Discover `NAVIGATOR`, `INTELLIGENCE` or `APPLICATION-DEFAULTS`; read
[the mandatory navigation contract](references/navigators.md#mandatory-dashboard-page-navigation-v27).
All previous fixes remain. The user confirmed the prior live navigators are
visible; package checks do not establish every navigation action or live behavior.


## Navigator render defaults (v26)

For dashboard navigation, a white screen or a `topPadding` error, discover
`NAVIGATOR` and read [navigators.md](references/navigators.md#current-construction-contract-v26).
Both bundled Navigator factories emit complete DEFAULT text, icon and padding
settings, including disabled icons. Use `navigator_api.state` for new dashboards;
never replace the icon object with only `{"isEnabled": false}`. Sparse state
styles remain overrides, and current versus legacy corner-radius profiles remain
separate. New Navigator text defaults to Arial.

The creation adapter completes missing render members before saving, and the
application-default gate rejects incomplete authored Navigator definitions.
`examples/navigator-defaults/build.py` constructs all three kinds from package
resources alone. No report cache or repair script is needed. Static checks and
saved-definition evidence do not establish live rendering. All previous fixes
below remain in force.

## Conditional-formatting rules recognized by the native UI (v25)

For CF, missing **Manage Rules**, variance colors, arrows or comment flags, read
[conditional-formatting.md](references/conditional-formatting.md). Discover
`CONDITIONAL-FORMATTING` (also F15). New reports put `conditionalFormatting` in
each sheet spec with stable measure keys; the standard builder resolves IDs and
emits the complete current native profile into both CF stores. No post-deploy
repair script or reference report is required. Existing-rule edits use
`format-matrix` with current native IDs and preserve unrelated user rules.

The bundled UI-derived seed includes null unrestricted selectors, stable native
rule names and all condition measure references. Saved JSON counts alone do not
prove UI recognition. The prior repair was user-confirmed; fresh construction
checks do not inherit that runtime claim. The standalone two-sheet example at
`examples/conditional-formatting/build.py` works from an isolated package copy.
All latest defaults and fixes below remain in force.

## Complete-application defaults (v24)

Every **new complete application** profile uses **Arial**, an **enabled native
Home landing page**, **Intelligence dashboard coverage for every Planning
sheet**, and a visible native **Page Navigator on every Intelligence dashboard**.
A two-sheet brief, screenshot recreation, reference JSON, simple use case,
missing mention of Home/dashboard, quick deploy, or request to skip validation
does not waive these defaults in that profile. Apply preservation-first
extension and scoped-repair profiles instead of expanding unrelated surfaces.

- Use Arial for authored grids, measure/header overrides, rich text, Home text,
  slicers and chart text. A reference screenshot's different font is not a reason
  to change this application default.
- Set `planProperties.properties.homeLayout.show = true` and save native Home
  content with a business overview, starting instructions and sheet-navigation
  cards. A visibility flag without native role content is incomplete.
- Cover every Planning owner with an Intelligence workspace containing a header,
  semantic-dimension slicers, meaningful charts and its embedded Planning grid.
  Preserve standalone Planning owners and complete dashboard geometry/visibility.
- Include a native Page Navigator on every Intelligence dashboard with complete
  padding, Arial, all visible page targets and reserved space above the grid.

Use `build` / `build_application` and the applicable native provisioning phases.
`construct.build` only assembles components and now explicitly reports
`applicationComplete: false`; it is never a completed application delivery.
Run `check-application-defaults` on the final authored definition and Home data,
then require successful Home and dashboard save phases before reporting complete.
The reusable `require_delivery_phases` gate is called by the bundled deployment
paths. Report pending or failed required phases as incomplete, even after a
successful definition save. Skipping runtime validation still saves every default.

Discover `APPLICATION-DEFAULTS` and read
[application-defaults.md](references/application-defaults.md). Retain all previous
formula, Forecast, InfoBridge, PowerTable, input-policy, header-sizing and hierarchy
fixes. These defaults do not authorize unrelated live writes during a read-only
request or scoped repair; distinguish repair completion from application completion.


## Forecast hierarchy, visual columns and as-of controls (v23)

For monthly Forecasts, prefer actual non-composite
**Year -> Quarter -> Month** fields. Future-period extension Columns contain
only a valid date hierarchy.
Use Year/Quarter/Month/Week only with verified week parentage; otherwise preserve
the model's valid weekly hierarchy. Record explicit composite-field exceptions.

For one-time commentary, adjustments or QTD/MTD/YTD alongside that grid, evaluate
**Visual Input Columns** or **Formula Visual Columns** appended once per row
context. Preserve the primary time grain and resolve the input's storage context.
For dynamic as-of controls, first evaluate
**Intelligence slicer -> DAX SELECTEDVALUE -> exposed Planning measure ->
Formula Visual Column**. Use a sheet
parameter for sheet-local control or when the shared route is unsuitable. Keep
the history needed for aggregation and resolve the year for month-name choices.

Native Planning comparisons always use **`==`**; single **`=`** is for variable
declarations. This does not change DAX/SQL syntax. Shared formula constructors now
reject single-equals comparisons while preserving declarations, strings and labels.

Read [forecast-time-intelligence.md](references/forecast-time-intelligence.md) and
[formula-equality.md](references/formula-equality.md). Discover `TIME-INTELLIGENCE`
and `FORMULA-SYNTAX`; commands `planning-time-axis`, `planning-time-column`,
`check-formula-syntax` and `repair-formula-equality` prepare local results.
The standalone example works from bundled resources without prior chat or local
repair scripts. All previous fixes remain. Offline checks and saved-definition
evidence do not establish runtime calculation, dashboard interaction or writeback.

## PowerTable lookup and source metadata (v22)

For ID-backed PowerTable policy/master columns, use explicit database key/label
lookups from the current SQL catalog, including ordered chained lookups where
needed. Keep stored keys separate from display labels. Lookup presentation must
preserve existing editability; pass `allow_edit=False` for new read-only keys and
`allow_add=False` when inserts are disabled. Do not turn every ID into a lookup.

Configured PowerTables include destination-derived `source.meta.connectionName`,
`workspaceId`, `workspaceName`, `databaseId` and `dbDisplayName`. Never substitute a
reference report's connection or source identities. The builder rejects missing
display metadata for complete ALM grids. The separate initialization request is
not a complete configured source.

Read [powertable-lookup-source-metadata.md](references/powertable-lookup-source-metadata.md).
Discover `POWERTABLE-CONFIG`, `POWERTABLE` or `LOOKUP`. The bundled
`repair-powertable-config` command prepares only the affected columns/source parts;
it preserves IDs, locks, row actions and unrelated encoded parts. The standalone
example covers new authoring and repair without any chat or task-local script.
The live Supply Policy update remained pending at the last status check; this
release does not claim a completed deployment or validated target UI. All prior
fixes and resources remain.


## InfoBridge Planning-source identity (v21)

Planning-backed InfoBridge sources and queries must carry explicit owner
`measureGuid`, source `columnType` (`DI` or `FORMULA`) and `isHierarchyColumn:false`
in their catalogs and transformation field descriptors. Resolve these from current
owner records; never infer them from labels or reuse portable IDs as native selectors.
The bundled constructors accept `owner_columns` and reject incomplete mappings.
After import, resolve consumer fields from current query output lineage and keep
existing internal aliases, formulas, inputs and storage intact.

Read [infobridge-planning-identity.md](references/infobridge-planning-identity.md).
Discover `INFOBRIDGE-MAPPING` or F18. `bridge-planning-catalog`,
`check-bridge-mappings`, `resolve-bridge-output` and `bind-bridge-outputs` provide
local construction/reconciliation. The standard create/update writer checks
Planning-source mappings before sending. The bundled example and regression tests
need no previous chat, report cache or task repair script. All earlier fixes remain.

## Content-sized headers and hierarchy icons (v20)

For every new applicable report, regardless of business use case, compute the
rich-text header height from its content, font sizes and available width. Add
`max(8px, ceil(contentHeight * 8%))`, round up to the native 10px grid, and keep
the outer header, canvas, text height and layout height synchronized. Avoid fixed
large minimum heights. This is content-based authoring, not runtime auto-resize.

Default both native hierarchy icons to **`gmate`**:
`tableState.expandCollapseIcon` and `tableState.columnExpandCollapseIcon` under
visualState. These apply to all use cases, including reports with measures in
rows. Preserve explicit user overrides during unrelated repairs.

Read [report-presentation-defaults.md](references/report-presentation-defaults.md).
Discover `REPORT-PRESENTATION`; `fit-planning-header` and
`planning-hierarchy-icons` create scoped local candidates. The normal Planning
constructor applies both defaults. All v19 and earlier resources/fixes remain.
No tests or validation ran for the original v20 release, at the user's request.

## Roll-forward balances and totals defaults (v19)

For balances carried between periods (cash runway, inventory/replenishment,
receivables/collections, staffing/attrition, deferred/unearned revenue), start with
[roll-forward-authoring.md](references/roll-forward-authoring.md), then read the
complete matched case and shared patterns in
[roll-forward-formula-patterns.md](references/roll-forward-formula-patterns.md).
The supplied markdown is preserved byte-for-byte, including every formula,
worked table, assumption, caveat and test scenario. Discover with
`python plan.py discover --module ROLL-FORWARD`; `plan-intent` routes the semantic
outcome `balance-roll-forward` even when the prompt uses different wording.

For roll-forwards expressed as measures, recommend **Measures in Rows plus a
logical native Measure Model**:
`Opening -> movement drivers -> Closing -> diagnostics`.
Use current string IDs, `measure_tree`, expanded parents and consistent measure
order. The local `roll-forward-presentation` helper preserves formulas, input and
Forecast definitions, source identities, aggregation and storage mappings. Read
the guide before choosing recurrence vs cumulative ranges: balance-dependent
attrition/caps cannot use the independent-movement shortcut.

Every new applicable Planning grid defaults to row GT **Top**, row subtotal
**Top**, column GT **Left**, column subtotal **null/OFF**. Read
[planning-totals-defaults.md](references/planning-totals-defaults.md). These are
explicit authoring defaults, not omitted native settings. Users can override
them; unrelated repairs preserve intentional existing choices. `planning-totals`
creates a local candidate, while the new-sheet constructor applies defaults.
All v18 and earlier fixes remain. Runtime validation follows the user's request.

## Measure display defaults (v18)

Keep assigned measure cards visible in the side filter panel and initialize them
to **is (All)**: `filter: []`, no preset selected values/range, null numeric bounds.
Do not hide/remove measure cards. A requested Year/Region selection applies only
to that dimension's own card, never to grouping context inside a measure card.
Preserve intentional user filters during unrelated repairs.

Every new numeric Planning measure defaults to per-measure Auto number scaling:
`formatConfig.measure[resolvedId]` includes `{"format":{"13":"auto"},"order":N}`.
This includes semantic/query/From Sheets values, inputs, Forecast and formulas.
Keep percentages, currency, precision, formulas and storage units intact. Explicit
business formatting overrides the default; typed text/date/checkbox inputs are
excluded. Do not confuse per-measure `auto` with global `autoFixed` or copy Matrix
format keys to Charts. See [measure-display-defaults.md](references/measure-display-defaults.md)
and `planning-display-defaults`; F03/F07/F22 routes expose the commands and examples.
All previous fixes, including ReadAndEdit and formula-based locks, remain.

## Allow Input authoring default (v17)

New editable inputs must explicitly use **In both Read and Edit mode**
(`allow_input: "ReadAndEdit"`). Apply this to **all Data Input types**: Number,
Simulate, Text (short/long), Checkbox, Person, List (single/multi select), Date,
commentary and supported visual columns, plus Forecast edit configuration.
Do not rely on the native omitted-field default, which is Edit.

When business rules require conditional locking/unlocking, choose **Allow Input
based on formula** and write the actual eligibility expression using resolved
current references (`{"BasedOnFormula":"expression"}`). Keep it separate from
default-value formulas, on-change actions and formatting. Preserve existing
intentional policies in scoped repairs; honor an explicit edit-only request.
Read [input-editability.md](references/input-editability.md); route conditional
eligibility through F30 / `conditional-input`. All prior defaults remain.

## Adaptive business authoring (v16)

Interpret the business meaning before choosing a recipe. Read
[adaptive-business-authoring.md](references/adaptive-business-authoring.md) for
every new or materially changed request. Equivalent business outcomes should
receive the same feature choices even when the wording differs; changed grain,
units, time horizon, source or calculation must change the design.

The five cases are composable examples, not the limit of the skill. Decompose the
request, resolve current sources, choose features by their business distinctions,
record assumptions and dependencies, then execute every requested phase. Never
force a mixed workflow into one recipe or infer a rate/date/currency from a sample.
Retain all mandatory presentation, source identity, numeric and column fixes.

`discover` is a literal lookup, not semantic understanding. The agent reasons over
the user's meaning; `plan-intent --input business-brief.json --out decision-plan.json`
records those decisions, selected guides/actions, dependencies and unresolved
requirements. It does not deploy or prove runtime behavior. Use the complete
module directory for unmatched intents. `usecase build/deploy --recipe adapted.json`
supports variations within the documented recipe pipeline; compose separate module
helpers for other workflows. See examples/business-intent/merit-review.json.

## Fresh-session reproducibility for the five business cases (v15)

For sales targets, workforce merit, expense budgeting, rolling forecast/quarterly
review and connected currency/risk outlook, start with
[five-usecase-recipes.md](references/five-usecase-recipes.md) and `plan.py usecase list`.
The package contains the five original business prompts, complete symbolic specs,
ordered native phases and expected outputs. Use these instead of relying on this
chat, a task-local script, old report IDs or an agent's recollection.

For a matching case, inspect `usecase show` and run `usecase build` with the target model catalog. Author linked measures, commentary, formulas, chart bindings and geometry in the public definition, or start from a complete portable business definition on the same model. The specialized recipes with pending native extensions stop before creating an item. Only Home layout has a native save phase.

`usecase deploy` currently supports only a recipe whose original definition is
complete in the public route. The shipped five recipes contain required
post-import `steps`, `quarterly`, or `comparisons`; deployment therefore stops
before mutation until those features are authored through the approved public or
external-adapter phases. Treat `usecase build` as construction evidence, not
end-to-end deployment evidence, for those recipes.

Reproduce the same business structure, calculations and presentation, with all
latest fixes. Generate fresh IDs and timestamped names and use current model data.
Do not promise byte/pixel-identical output or validated runtime behavior from an
offline build. An explicit changed requirement takes precedence over the recipe.

## Complete-application baseline (v11)

Every **new complete application** profile must include **all four**:
source-role measure colors, rich-text Planning descriptions/legends,
Intelligence dashboards with headers/slicers/charts/embedded Planning grids, and
a **visible native Home landing page** with a business overview and sheet-navigation
cards. These are required even when the business prompt does not enumerate them.
Extension and scoped-repair profiles preserve those surfaces when in scope and
do not expand unrelated application behavior. Never silently omit a requested
baseline or report complete delivery while its construction/save phase is
missing.

For numeric Data Input and Forecast measures, read
[numeric-input-constraints.md](references/numeric-input-constraints.md): AverageLeaf
can have parent-to-children distribution enabled; do not restrict it to Sum.
Default it on for AverageLeaf unless explicitly disabled. Static min/max bounds
must be whole numbers. Preserve percentage units and existing stored values;
use a resolved measure-based bound when a fractional limit is required.

Read [application-defaults.md](references/application-defaults.md). Use `build` /
`build_application` and `provision`; they now include Home content and visibility.
Use `check-application-defaults` for the complete baseline. Saving only a Home
layout does not make the Home tab visible: check its workload show flag and the
effective role content separately. Preserve other role layouts and all prior fixes.

Follow the user's latest validation instruction. Validate saved properties and
Home content/visibility when requested; distinguish those results from UI and
calculation checks. A previous request to skip validation is not permanent.

## Required integrated variance charts (v14)

For every Intelligence bar/column comparison against a baseline, use **native
integrated variance** by default. AC/PY assignments or grouped bars alone do not
satisfy this requirement. Read [integrated-variance.md](references/integrated-variance.md).
The shipped vertical recipe aligns `COLUMN_INTEGRATED_VERTICAL`, its serialized
template and the `integratedVariance` measure configuration. Retain the baseline
assignment, current source IDs, category grouping, filters and business captions.

Use `integrated-variance` for a style-only existing-chart candidate;
`comparison_chart` selects it automatically for resolved typed measures.
`column_chart` / dashboard chart specs accept `comparisonField` for semantic
comparisons. Resolve From Sheets/query bindings before the post-import chart phase.
Preserve configured sign/color meaning; higher cost is not inherently favorable.
Ordinary single-series bars are unaffected. Honor explicit alternative styles.
All earlier defaults and fixes remain required, including native Home, rich-text
headers, source-role colors, embedded Planning and the v13 column recipe.

## Planning column presentation (v13)

For new Planning sheets, initialize expansion from every actual bound column
dimension ID, fill missing sizing defaults, use native-default column totals
unless explicitly specified, and register ordinary native-measure filter cards.
Read [planning-column-presentation.md](references/planning-column-presentation.md)
and use `planning-column-presentation` for existing-property candidates. Honor
deliberate collapsed views and explicit sizing/totals. The user confirmed only
the expansion repair; the other three items are additional requested defaults.

## Route every business request to its guide and execution path

From this skill directory, use **[module-routing.md](references/module-routing.md)** and
the read-only `plan.py discover` command. This directory covers **all F01-F30
modules and ten cross-cutting workflows**. Each entry provides business triggers,
selected functional guides, exact shipped CLI commands or Python callables,
inputs/dependencies, examples, execution phase and explicit limits.

```text
python plan.py discover --list
python plan.py discover "rolling forecast quarterly commentary variance"
python plan.py discover --module F09
python plan.py discover --module POWERTABLE --json
```

Map every requested outcome as **business clause -> functional guide -> command
or callable -> prerequisites -> execution phase -> result**. Read only the
selected guide sections. Use the business distinctions and examples already in
feature-contracts.md; do not select modules from keywords alone or ask customers
for internal module names. See [routing-examples.md](references/routing-examples.md)
for complete forecast/review, connected cost, maintenance and control workflows.

The directory identifies four construction states: **integrated**, **separate
phase**, **partial**, and **guide only**. Discoverability is not a claim that every
feature has a complete executable factory. `workflow.SUPPORTED`, `prepare-scope`
and `provision` cover the base orchestration only. Before treating any omission as
unavailable, inspect the route and add its separate component/post-import phase.
Do not silently omit From Sheets, typed commentary, variance formatting or charts
when their existing helpers are available. For a true missing branch, state the
specific gap and continue independent authorized work without weakening required
controls or inventing financial values.

| Business area | Module routes |
|---|---|
| Grid, totals and presentation | F01 Layout, F02 Aggregation, F03 Quick Format, F04 Insert Row, F14 Formatting, F16 Column Style, F26 Themes, F28 Header/Footer |
| Inputs, formulas and controls | F05 Typed Inputs, F11 Row Model, F12 Measure Model, F13 Approval, F20 Anchor, F29 OnChange, F30 Formula Eligibility; FORMULAS, RULES, CUBE |
| Time, views and selections | F06 Pivot, F07 Visual Filter, F08 Context, F09 Forecast/Time Extension, F10 Fiscal Year, F21 Data Pane, F22 Side Panel Filter, F23 Bookmark; SCENARIOS, NAVIGATOR |
| Connected planning and maintenance | F17 Writeback, F18 InfoBridge, F19 From Sheets; POWERTABLE, LOOKUP, DIMENSION-ID |
| Application and delivery | F15 Conditional Formatting, F24 Home, F25 Security, F27 Embedding; INTELLIGENCE, LIFECYCLE |

The latest corrections below remain authoritative: Forecast actuals/defaults and
registration, dynamic time-extension grain, reference/UTC dates, filter cards and
casing, query/output identities, complete PowerTable parts and deferred setup,
readable Home geometry, comparison charts and owner-preserving embeds. Earlier
release coverage notes in preserved references do not remove newer listed helpers.
Application-service commands require an external approved profile and are
labeled separately from public Fabric REST.

## Authoring contract

Users describe business outcomes. The agent selects features, resolves real model identities, constructs and saves the native application, and verifies the requested behavior. Delivering a blueprint alone does not complete a creation request. Preserve existing inputs and unrelated configuration on updates. Do not require users to supply module names, enum values, previous report JSON or manual JSON fixes.

The current business request determines functionality; current model metadata determines fields/relationships; the bundled design and feature guides determine styling and supported feature behavior. Historical examples are evidence, not fixed business defaults. Keep the user's detailed feature/use-case/property knowledge and its distinctions intact.

Use bundled API constructors and authenticated API adapters only. There is no native UI authoring fallback. Read `references/api-contract-gaps.json` as a feature-level coverage inventory. Follow `references/verified-authoring-flow.md`: use documented construction and native phases, preserve requested components, and continue independent supported work. Do not auto-deploy a reduced substitute or choose a simpler business flow to bypass a missing capability. Report the exact gap. Do not copy an old report, require a source checkout, manufacture payload fields or ask the user to hand-edit JSON. `references/connected-construction.md` retains component recipes; its older partial-deployment policy is superseded by v29.

**Verification boundary:** bundled typed-column/rule factories, InfoBridge
adapters, PowerTable initialization/save adapters, bookmark persistence,
Navigator registration and Home asset upload have offline contract tests. Full
capture/restore, some advanced factories, environment compatibility and execution
acceptance remain incomplete; see `references/builder-integration.md`. Never
equate saved state with working calculation, input edits, propagation or rendering.

**Reference integration:** adds ID/Skip descriptor construction, typed PowerTable
lookup presentation, normalized contributions, equality filters, linked-measure
companions and owner-preserving embed references. Constructors and deployment
boundaries are tested offline; no tenant report is a runtime dependency.

**Context/Intelligence:** external Context has a model-driven constructor and
mirrored selection/input binding; Scenario stays off the visible axes. The
builder supports labeled slicers, numeric period ranges, KPI cards, styled text
and a lower Planning embed. Offline and mocked-API tests do not prove destination
rendering or propagation. Read `references/context-intelligence.md`.

**InfoBridge:** treat it as a general sheet-data transformation and delivery
utility; connected P&L is one example. Both Add Measure and Add Dimension accept
conditional SQL, and a measure operation can return text. Read
`references/infobridge-construction.md` for synthetic contracts and identity
reconciliation. Graph import and automatic propagation remain unverified.

## Source-aware assignments (v10)

Resolve every measure by its actual origin before assigning it. A correct caption
with the wrong sourceType or ID is invalid. Native Planning registry companions
for DAX measures are not From Sheets outputs. Retain the original PowerBI field
ID/type; link only actual sheet-produced Input/Forecast/Formula outputs; resolve
InfoBridge against the current query's selected output catalog. AC/PY buckets do
not change source identity. Never derive IDs or source types from display names.

Read [measure-source-bindings.md](references/measure-source-bindings.md) and use
`resolve-measure-binding` / `registered_measure`. The direct sheet-link helper now
rejects Native companions. Reconcile assignments, ordinary filter cards, sort
references and DAX flags together; preserve formulas, storage IDs and selections
whose source identity survives. These are construction requirements even when
the user asks to skip runtime validation.

## Required Planning presentation defaults (v9)

Every Planning application must include an Intelligence dashboard with a rich-text
business header, relevant slicers and charts, and the embedded Planning sheet
underneath. Default to one workspace per Planning owner; retain standalone sheets.
Do not deliver only grids unless the user explicitly requests that alternative.
Read [planning-presentation.md](references/planning-presentation.md). `plan.py build`
and `provision` now compose these defaults; Python application callers use
`build_application`. Run `check-application-presentation` for offline coverage.

Every Planning sheet also needs its own meaningful rich-text description and
legend, replacing the native DEFAULT_TITLE / [fields] element. Use
`present-planning` with actual typed records. Default colors are amber for inputs,
purple for formulas and blue for Power BI measures; teal distinguishes From Sheets.
Match the legend to these roles and preserve Forecast open/closed fills, lock
rules, conditional indicators and explicit user styling. The complete TEXT writer
and layout contract replace the old incomplete optional-header snippet.

## Executable formatting and naming checks (v8)

Read [planning-integrity.md](references/planning-integrity.md) before constructing
or repairing a Planning grid. Use the complete known GlobalStyles defaults;
fill missing properties while preserving explicit valid settings and extensions.
`build` and `format-matrix` complete defaults; `check-planning-properties` checks
them; `repair-planning-properties` produces an explicit local repair and change log.
The bundled encode/validate and Plan/property-batch write paths reject incomplete
defaults or inconsistent semantic grouping names before sending them.

Use current model field IDs and **canonical physical grouping names** consistently
in assignments, row/column labels, filters, sort/DTO metadata and dimension lookup
descriptors. Country must not become Market in only some places. Business captions
belong in headings until a complete alias contract is implemented; measure labels
and From Sheets identities remain untouched. Never do a late label-only rename.
Repairs preserve IDs, saved-value keys, formulas, members, grain and all unrelated
state. These executable offline checks are required even when runtime validation
is skipped. API saves are not evidence of rendered or calculated results.

## Supported Matrix formatting and leaf storage defaults

For business styling requests, read [matrix-formatting.md](references/matrix-formatting.md)
and use `plan.py format-matrix`. Resolve the actual Planning/Matrix owner and IDs;
use property-specific types, explicit point-to-pixel conversion, scoped paired
header text/fill, independent Column Style read/edit modes, ordered formatting
operations and complete selected conditional rules. Preserve unrelated state.
Global body fontSize is a numeric pixel **string**; scoped/Column Style font sizes
are **numbers**. Row heights belong to row_height_config. Direct Forecast fill can
hide open/closed styling; the new constructor no longer adds that blanket fill.
Rule targets and condition sources are independent. Sign rules need appropriate
row/period totals scope; leaf comment flags need their own row/column scope. Use
jet_cfProps for the investigated version; do not universally mirror compatibility
stores. Report unsupported styling and approximations; no invented CSS properties,
selection colors, hover guarantees or financial-validation prerequisites.

For **new** planning storage, default to the stable leaf ID per entity table and
exclude its confirmed descriptive ancestors from the key while keeping them visible.
For Brand -> Category -> Subcategory -> SKU, map SKU to the unique ProductKey and
use Skip for those ancestors. Derive this from real key/grain metadata, not merely
column order or the fact that fields share a table. Keep independent dimensions,
composite-key discriminators, calendar/scenario grain and explicit user choices.
Read [dimension-leaf-keys.md](references/dimension-leaf-keys.md); use
`dimensionKeyGroups` in build/provision or `plan.py leaf-key-mapping`. Existing saved
values must not be silently re-keyed: preserve their mapping until a supported
value migration is explicitly requested. Stable IDs avoid mutable parent labels
in new coordinates; cross-key/version migration is not automatic.

This offline update keeps all prior Forecast/time-extension, From Sheets, filters,
PowerTable, Home-fit and discovery resources. The contract snapshot records the
supplied source investigation revisions and the older full native CF seed separately.
No live rendering, storage migration or data-flow verification is implied.

## Model and workspace intake

If a semantic model ID or URL is missing from both the request and unambiguous current task context, ask the user for it before model-dependent creation. Never default to a historical model or the fixtures. Resolve the model's hosting workspace through authorized metadata and default Plan creation to that same workspace, unless the user specifies another destination. If the hosting workspace cannot be resolved or cannot host the Plan, ask which accessible workspace they want. Keep useful model-independent preparation moving while waiting.

## Working-reference Forecast defaults and agent-independent execution

When the user supplies a working reference sheet, inspect its current Forecast
record and date-axis settings before authoring. Reuse relevant configuration,
remapping dependencies to the target; preserve target identities, existing inputs,
layout and unrelated properties. A reference is evidence for settings, not a
template to clone wholesale or a requirement for routine new construction.

Do not ask for a timezone. Reuse saved `periodUtc` bounds for the identical horizon;
otherwise use an explicitly configured reference/report timezone, or **UTC** when
none is available. An offset does not identify an IANA timezone. Do not use the
machine locale or extrapolate captured bounds to another horizon.

The working Forecast save uses `closed_period_till:null`,
`auto_close_forecast_settings:null`, `forecast_allowed_user_permissions:true`,
`disable_write_access:false`, and `edit_config.aggregate_total:null` (the UI shows
All Periods). Do not synthesize `closed_period_till` from the day before the open
range or force the string `AllPeriods` for this default profile. Closed periods
still link to actuals. Forecast numeric metadata defaults
`distribute_parent_value_to_children:true`; preserve an explicit user choice.
The exact requested open-period formula remains editable Data Input, not on-change.

Forecast requires a supported ordered date hierarchy in Columns. Default new
monthly requests to **Year -> Quarter -> Month**; keep business/non-date dimensions
in Rows. Preserve valid Year-only/Year-Quarter or other supported requested grains;
time-extension metadata is derived dynamically from the actual column levels.

Read **[forecast-review-execution.md](references/forecast-review-execution.md)**
for the Forecast extension implementation. `forecast-repair` is a shipped local
candidate command. `runtime.forecast_review` supplies the direct From Sheets
SUM, quarterly text commentary, formula variance, negative formatting and
comparison-chart phase, but the workload mutation has no current CLI command.
Use the Python callable only
through an explicitly approved external adapter profile; otherwise record the
phase as unavailable and return `mutation: none` for an unchanged request that
requires it. `provision` does not run the phase automatically. No new asset
upload capability is required.

Respect explicit requests to skip report validation. Required baseline/identity/
ETag reads and async-operation completion are still needed for safe mutation;
omit post-save exports, rendering checks and runtime tests when asked.

## Forecast requests use native Forecast

Read `references/forecast-authoring.md` together with F09 in `references/feature-contracts.md`. Treat a business request for forecasting as a request for the native Forecast module. Resolve the relevant actuals measure, including its DAX meaning when available, and link Closed Periods to it. Use the requested forecast horizon and real Year -> Quarter -> Month hierarchy in Columns; business dimensions belong in Rows. Do not infer the business cutoff from the machine clock.

For Open Periods, apply the requested formula or measure under editable Data Input defaults unless a read-only outcome was explicitly requested. If no open-period behavior is supplied, use None (`{"DataInput":"Blank"}`). Never invent a growth assumption or seed missing actuals as zero. `COLUMN.ADDMONTH(-1) * 1.1` anchors the first open month to the previous closed actual and compounds 10% month over month thereafter; it is not a fixed-base uplift for every future month.

The composed Planning constructor supports `kind:"Forecast"`, `actuals`, `start`, `end`, optional `timezone` (UTC fallback), saved `periodUtc` or a `referenceForecast` profile and optional `openDefault`. It builds the complete Forecast record, source dependencies, measure registration, aggregation, formatting and context binding. Use `runtime.forecast.forecast_config` through `runtime.construct.planning`/`build`; no old report or manual JSON repair is needed. Preserve the user's requested formula exactly. If actuals or horizon cannot be resolved, ask only for the missing business input and continue independent work.

Native Forecast registration and saved settings are distinct from calculated
results. Check open periods, future-calendar expansion and edit restrictions when
the model is available; report a failover error without fabricating values.
Offline regressions verify construction, not calculation or rendered appearance.

## Forecast period and time-extension fixes

Use full ISO date labels plus `forecast_period.start_utc` and `end_utc` in epoch
seconds. Reuse the reference/report timezone or default to UTC without asking;
use captured `periodUtc` bounds for the exact same horizon when available. UTC bounds represent local-day
start and inclusive end, including DST; never infer them from the nominal ISO labels
or hard-code the sample timezone. Read `references/forecast-authoring.md`.

Under **Forecast -> Time extension**, register the real column calendar levels
with `isTimeDimension:true` and `timeIntervalUnit:Year/Quarter/Month`.
`runtime.construct.planning` applies this through `forecast_time_axis`.
Derive these roles dynamically from the actual assigned hierarchy: Year-only
emits Year only; Year/Quarter emits those two levels. Preserve existing or explicitly
chosen supported granularities, using `columnTimeLevels` for custom names/native
units. The three-level example is not a universal template. Read F09's complete
supported-pattern table and the dynamic-granularity section of forecast-authoring.
The date-axis before/after comparison is time-extension metadata, separate from
the measure's period bounds. Keep measure identities and requested formulas intact.
These two corrections came from a UI-saved comparison. Registration/visible flags
alone did not establish grid or Show Columns availability. Runtime acceptance of
the correction remains separate from successful API submission.

## Native Home content must fit

For new Home content, use `runtime.home_fit.readable_home_layout` with `surfaces.home_item`; the provisioning workflow uses it automatically. Read `references/home-layout-fit.md`. Home row widths are **pixels**, not percentages or Intelligence grid spans: never use `[60,40]` for a percentage split. Prefer flexible null widths and content-driven heights for text and cards. When content width is unknown, stack prose in full-width rows. Do not shrink text or force line breaks to fit narrow blocks. Keep headings aligned, descriptions concise and the Home focused on business guidance and navigation.

Run `runtime.home_fit.audit_home_fit` before saving and after readback. The constructor and native writer reject clearly narrow text widths and invalid dimensions; the audit flags manual text-height/clipping risks. Existing layouts require scoped edits that preserve identities, text, assets and sheet-card settings. The new constructor prevents the observed sizing mistake; API/static checks do not certify rendered fit at every viewport. Report rendered acceptance separately.

## Filter, KPI and connection construction corrections

Read `references/consumer-repair.md` for the 2026-11-13 reference-derived corrections and their evidence boundaries. The bundled constructors now emit uppercase `filterPanePosition:RIGHT`, preserve lowercase `controlPanePosition:right`, and register ordinary Planning grouping filters separately from external Context. KPI construction emits outer CARD mode and complete active KPI/number-format store slices, including variance styling even when variance is disabled.

After import, resolve InfoBridge consumers using the destination's query registry and final selected-field catalog via `runtime/consumer_bindings.py`. A source input-record row ID is not an output-column ID. Preserve large decimal/string IDs exactly; resolve query GUID, native numeric prefix, output field ID and internal consumer measureGuid in their distinct domains. New consumers hash the actual native-qualified field key. Preserve existing Planning input/formula identities during a repair unless a complete supported dependency migration is performed. Failed/pending materialization remains unverified even when the saved field selection matches.

A ShareableCloud OAuth2 connection with type/path `FabricSql` is generic and can be used with a separately resolved Fabric SQL artifact/host/database. Do not reject it for lacking a database-specific path or create repeated duplicate connections. Existing-table initialization uses mode 2; mode 3 on the reference FX table records file-import provenance. Existing-source schema success and new-source credential-resolution failure are separate evidence. Continue independent modules on an isolated maintenance failure.

The prior correction suite contained 209 passing tests, including output-ID/row-ID confusion, transformed final selections, Context preservation, filter casing and incomplete KPI state. Live repair status belongs in the task's delivery evidence; these tests do not certify native rendering or financial propagation.

## Intelligence chart field filters

Every dimension and measure assigned to a chart, including KPI and comparison measures, needs an ordinary visible registration at `properties.superFilterAssignments[]`. Hidden scenario/slicer scope in `visualState.embeddedSuperFilter`, page filters and Planning external Context do not populate those Visual level cards. Use `runtime.chart_filters.ensure_chart_filters` and `audit_chart_filters` after chart construction and after resolving imported field identities. The KPI constructor applies these helpers before the public create.

Read `references/chart-visual-filters.md` for complete numeric/FACET
registrations, DAX flags, category evaluation grain, comparison buckets and
preservation. A dimension inside a measure's filter is evaluation grain, not its
own card. Offline tests cover construction cases; saved registrations do not
prove rendering or query execution.

## Complete PowerTable construction

PowerTable requests dispatch by their current source state. Select exactly one
mode, announce it, and read every linked reference end to end before issuing a
command:

| Mode | Use when | Required references |
|---|---|---|
| `powertable-existing` | One to five existing Fabric SQL Database tables are connected to a new Plan | [Connect existing tables](references/powertable/connect-existing-tables.md), [column mappings](references/powertable/column-mappings.md) |
| `powertable-from-scratch` | New SQL tables must be designed and created before the Plan | [Modeling](references/powertable/modeling.md), [create from scratch](references/powertable/create-from-scratch.md), [column mappings](references/powertable/column-mappings.md) |
| `powertable-analysis` | A natural-language question targets one existing PowerTable sheet | [Analyze PowerTable data](references/powertable/analyze-data.md) |
| `powertable-cross-analysis` | Two or three PowerTable sheets must be compared or reconciled | [Analyze across sheets](references/powertable/analyze-across-sheets.md), [single-sheet analysis](references/powertable/analyze-data.md) |

Use the [PowerTable reference index](references/powertable/index.md) to keep
the mode, source state and required follow-on references together. The
[`sqldb-cli` companion skill](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli)
is an external dependency, not bundled runtime. Its
[authoring guide](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli/references/authoring.md)
supports DDL/discovery and its
[consumption guide](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli/references/consumption.md)
supports read-only T-SQL. Resolve and install that companion separately when a
PowerTable mode needs it; never manufacture a local `sqldb-cli` path.

Apply these rules in all creation and analysis modes:

- Create at most five PowerTable sheets in one run. In `powertable-from-scratch`,
  the approved model is limited to five SQL tables per run.
- In from-scratch mode, offer no sample data, reference-only sample rows, or
  inserted synthetic rows. Ask for a row count only after insertion is selected;
  accept only 1-100 rows per newly created table.
- Use only the SQL type allowlist in
  [PowerTable modeling](references/powertable/modeling.md). Set every Currency
  column's `columnMeta.currency` to US Dollar.
- For existing tables, search every user schema. If requested tables are absent,
  offer create-through-from-scratch, another database, or cancellation.
- After SQL Database selection in either creation mode, list user schemas,
  mark `dbo` as the default and obtain explicit schema selection.
- In from-scratch mode, show proposed tables in readable table layouts and offer
  approve, fine-tune, custom tables or cancel. Do not discover a connection or
  stage writes until the model is approved; repeat the complete preview after
  every change.
- In analysis mode, read the complete saved Plan definition, show the selected
  sheet's database/schema/table/column mappings, and obtain explicit source
  confirmation before the first data query.
- Cross-sheet analysis compares at most three source sheets. Profile and confirm
  every relationship before answer queries, aggregate each sheet before
  combining, and scope discovery to the compared source tables, their Plans and
  their databases. Name sources use the key sheet's own database.
- Resolve Plan, workspace, database, table and connection identities by listing
  and exact filtering. Never guess IDs, overwrite collisions or retry a possibly
  successful write without readback.
- Terminal write by mode: existing mode creates the Plan then verifies it;
  from-scratch mode commits the approved transactional SQL DDL/DML, creates the
  Plan, and verifies both; both analysis modes are strictly read-only.

### PowerTable creation destination

Confirm the target workspace and choose workspace root or an existing folder.
Create the Plan in the confirmed workspace first; move it only after creation
has completed and its Plan ID is resolved. Verify top-level `folderId` through
Get Plan independently of definition readback before reporting placement.
A destination change requires a refreshed review and approval.

For the actual definition, use `runtime.powertable_factory.configured_table` and
`references/powertable-alm-construction.md` when the authorized SQL table and
connection are resolved. Bundle all five parts: the sheet companion and the
visual's properties, source, column configurations and source settings. The
visual properties require the double schema/properties wrapper. Use the real SQL
schema, a fresh source GUID, creation mode consistent with the documented
generator, a real SQLDbNative artifact binding, and source settings linked to
that same GUID. The embedded presentation defaults contain no old report IDs.

An empty POWERTABLE sheet only shows setup/welcome; it is not a configured
table. A direct-initialization error is not proof that a generic Fabric SQL
connection was deleted. Keep connection, artifact, source, visual and column
identities separate. Preserve non-identity integer primary keys and construct
lookups only against verified unique remote keys.

Verify owned type-30 visuals, non-null dataSourceId, the schema in the resolved visual context, intended columns/settings and the final exported definition. Acknowledge runtime/rendering or row-save limits separately. The connection-deferred fallback below remains available only when a source cannot be initialized; it must be labelled honestly.

## PowerTable connection fallback

When the user accepts deferred maintenance initialization, retain native visible POWERTABLE sheets even if the SQL connection is unavailable. An empty sheet is a navigation entry displaying the welcome/setup screen, not a configured table awaiting credentials. Mark it sheet-only-uninitialized and maintenance incomplete. When configured tables are requested, earlier acceptance of a sheet-only fallback does not establish configured-table completion. The complete ALM constructor or the supported native initializer must create the real visual/source/column records; do not fabricate them or clear a working PowerTable. Use runtime.powertable_readiness.inspect_native before reporting configured-table completion, and compare item-bound connections separately from the account connection catalog. Continue independent Plan modules when maintenance is incomplete.

Read `references/maintenance-deferred-connection.md`; use `runtime.maintenance_shells` or `plan.py prepare-maintenance` for the same-item addition. Export a fresh baseline, preserve unrelated part bytes and verify the new native sheet catalog after publication. Preserve and audit the existing chart Visual level field filters, external Context and slicers after every import. Validate query field IDs against current output metadata even when chart and filter agree: ALM can remap both to incorrect input-row IDs. Use `consumer_bindings.audit_visual_consumers` and the scoped `restore_import_bindings` recovery from this deployment's intended properties, then save with fresh ETags and re-export. The updated bundle retains the chart filter constructors and their regression tests.

### PowerTable completion summary

End a creation run without waiting to be asked:

| Field | Value |
|---|---|
| Workspace name | Display name of the workspace that holds the Plan |
| Artifact name | Plan display name (`Plan`) |
| Report URL | `https://app.powerbi.com/groups/{workspaceId}/plans/{planId}` |

When verification fails, report the artifact as unverified but retain the
summary. After a SQL commit without a Plan, report the persisted SQL tables and
omit the URL; never represent the partial state as complete.

## Execute from the installed skill directory

Resolve this file's parent as the skill root. Execute plan.py there or by absolute
path. Keep task data, operation ledgers and API journals in a separate directory.
Credentials belong only in the named process environment, never in the package.

```text
python plan.py discover --list
python plan.py discover "rich header measure colors embedded dashboard"
python plan.py --help
```

## Read the relevant bundled material

From the installed runtime, first use `plan.py discover` and `references/module-routing.md` to select guides and execution phases, then read the applicable sections of `references/runtime-guide.md`. Its full workflow covers model resolution, construction, native routes, connected propagation, Home, maintenance, placement, navigation, deployment, recovery and acceptance.

| Need | Bundled reference or tool |
|---|---|
| Intelligence mode guides, design topics and feature-level references | [Intelligence index](references/intelligence/index.md), [feature master list](references/intelligence/feature-master-list.md), `plan.py discover --module INTELLIGENCE` |
| Every module: business request, guide, command, inputs and limits | `references/module-routing.md`, `references/module-routing.json`, `plan.py discover`, `references/routing-examples.md` |
| External adapter compatibility and acceptance guide | `references/builder-integration.md` |
| PowerTable request modes and source-state routing | [PowerTable index](references/powertable/index.md), [existing tables](references/powertable/connect-existing-tables.md), [from scratch](references/powertable/create-from-scratch.md), [analysis](references/powertable/analyze-data.md), [cross-analysis](references/powertable/analyze-across-sheets.md) |
| External SQL Database authoring and consumption companion | [`sqldb-cli`](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli) |
| Typed-column/rule factories and local construction | `runtime/input_factories.py`, `runtime/rule_factories.py`, `plan.py construct-native`; workload writes are callable-only through an approved external adapter profile |
| PowerTable encoding, new Navigator host and Home assets | `runtime/powertable_factory.py`, `runtime/navigator_api.py`, `runtime/assets_api.py` |
| Native Forecast intent, complete records and defaults | `references/forecast-authoring.md`, `runtime/forecast.py`, `tests/test_forecast.py` |
| Complete configured PowerTable ALM construction | `references/powertable-alm-construction.md`, `runtime/powertable_factory.py`, `tests/test_powertable_alm.py` |
| Business-to-feature decisions and exact properties | `references/feature-contracts.md` |
| Layout, typography, colors, illustrations and quality | `references/design-standards.md` |
| Property validation and known conflicts | `references/planning-integrity.md` |
| Complete Navigator state, appearance and recipes | `references/navigators.md`, `fixtures/navigator-spec-*.json` |
| Runtime/coverage/dependency boundaries | `references/runtime-guide.md`, `references/implementation-status.json` |
| External Context, rich Intelligence construction and API layout | `references/context-intelligence.md`, `runtime/filters.py`, `runtime/intelligence.py`, `runtime/intelligence_api.py` |
| Inputs/formulas/registrations and model-driven Planning parts | `runtime/construct.py`, `runtime/identity.py` |
| Complete native scalar/weighted aggregation validation | `runtime/aggregation.py` |
| Current Cube request validation and saved binding fields | `runtime/cube_contract.py`, `plan.py construct-native cube-settings` |
| InfoBridge operator factories, contribution recipe, stage checks and identity reconciliation | `references/infobridge-construction.md`, `runtime/bridge.py`, `runtime/bridge_operations.py`, `plan.py construct-bridge` |
| Connected constructors, dimension ID descriptors, lookup columns and fallback policy | `references/connected-construction.md`, `runtime/dimension_mapping.py`, `runtime/table_columns.py`, `runtime/connected_components.py`, `runtime/scope.py` |
| Saved definition owner/query/mapping audit | `runtime/definition_audit.py`, `plan.py audit-definition` |
| Saved Pivots, native auth and definition readback | `runtime/pivots.py`, `runtime/session.py`, `runtime/readback.py` |
| Public-definition provisioning with complete-scope coverage | `runtime/workflow.py`, `plan.py provision` |
| Compressed Home metadata, priority and visibility | `runtime/home_api.py`, `vendor/lzutf8/` |
| Home, bookmarks, maintenance source and SQL metadata | `runtime/surfaces.py`, `runtime/native.py` |
| Embedded geometry, ETags, preservation and readback | `runtime/layout.py`, `tools/visual-placement.cjs` |
| Export/decode/update/create and resumable LROs | `runtime/codec.py`, `runtime/transport.py`, `plan.py` |
| Pinned schemas and their transitive refs | `schemas/manifest.json`, `runtime/validate.py` |
| Offline behavioral/negative cases | `tests/test_runtime.py`, `fixtures/` |
| Native query consumer, filter and KPI repairs | `references/consumer-repair.md`, `runtime/consumer_bindings.py`, `fixtures/card-defaults.json` |
| Every chart assignment in Visual level filters | `references/chart-visual-filters.md`, `runtime/chart_filters.py` |
| Maintenance sheets awaiting a connection | `references/maintenance-deferred-connection.md`, `runtime/maintenance_shells.py`, `plan.py prepare-maintenance` |
| Source guide integrity | `references/preservation-manifest.json` |

Source-repository links and historical paths inside retained references are **optional provenance**, not ordinary-authoring dependencies. This runtime guide supersedes old instructions to stop and find those checkouts. Do not carry forward stale counts, nonexistent `--coverage` switches, historical credentials, or prior application IDs.

Use `python plan.py reference feature-contracts.md --list` to find headings and `--heading "..."` to read one section. Read the selected feature's business use, shape, context, constraints and acceptance together; matching a keyword is insufficient.

## End-to-end execution sequence

1. Select the application profile, then route every requested outcome through
   `plan.py discover`/`references/module-routing.json`, including separate
   phases. Apply model/workspace intake, then translate the request into grain,
   columns/values, business inputs, formulas, time/scenario context, policy,
   dependencies and expected outcomes. Resolve current model/source metadata and
   actual endpoint/auth context.
2. Build requested Planning sheets and source owners using the bundled public
   constructors. A missing module does not stop independent **local**
   preparation: record the gap, construct other safe components and produce the
   coverage ledger. It does stop mutation for the unchanged request.
   `prepare-scope` is diagnostic and `provision` returns `mutation: none` for
   incomplete original scope. Continue live only after a verified separate phase
   closes the gap or the user explicitly approves revised scope. Keep complete
   measure/format/aggregation/context registrations and stable input identities;
   never fabricate values or retain unsafe edits.
3. Compose direct links/lookups or InfoBridge at the right grain. For finance, aggregate source detail, retain/add the needed classifications, construct common contribution metrics and Append; do not recreate classifications already present. Normalize grain/names/types/context; use optional-measure union only by explicit policy. Track Year/date fields after each transform. Register output fields, measure selectors and execution-query references separately and resolve actual post-import identities.
4. Use the bundled Home content/priority/visibility APIs. Use the new source-contract maintenance and multipart image adapters with explicit destination profiles and staged readback; never substitute UI steps or fake uploads. Keep roles/security, Home content, priority and visibility separate.
5. Use `context` for external version selection and `dashboards` for rich native Intelligence composition. Include relevant labeled slicers, meaningful KPI cards, a banner and a broad lower Planning workbench; do not silently produce a grid-only page. Read `references/context-intelligence.md`. Compose from a fresh complete inventory with separate non-overlapping sections. Save actual embedded IDs in page-local overrides; preserve source owners. Construct saved Pivots through the bundled factory. Use the new Navigator host registration and public bookmark persistence adapters. Full snapshot capture and restore still require the missing contracts; do not call the dashboard complete without them.
6. Validate exact parts and explicitly record native/public schema discrepancies. Create once or update a fresh baseline; poll Location/Retry-After to terminal status and result. Journal without secrets; reconcile uncertain submissions instead of duplicating items.
7. Read imported grid configuration through the public definition. For dashboard geometry, navigation, Home and requested connected features, use their scoped operations. A separate request to exercise calculations, locks or propagation can use authorized test values.
8. Return the native artifact link, decoded/transport JSON where requested,
   credential-free scripts, execution evidence and the coverage ledger. State
   supported results, alternatives, omitted features and unverified behavior
   separately. A live partial delivery is permitted only under an explicitly
   approved revised scope. An unchanged incomplete request returns
   `mutation: none`; independent local work can still be handed off.

## Readback normalization

Sheet visual declarations can be returned with embedded references first, so
compare declarations by unique visual identity while retaining layer order in
properties. Normalize Decimal geometry before collision checks without changing
saved coordinates. The bundled validators implement both rules; they do not
establish rendered appearance or interaction propagation.

The native column-list projection omits the outer `boundToFilterContext` enum. Verify its inner `bound_to_filter_context` Boolean in native records and the outer enum in the ALM definition; do not synthesize a missing response field or reject an otherwise matched native projection.

Do not assume an empty-catalog Planning source can be enriched on import. Require
a complete supported source/query contract or omit only the connected module and
label dependent totals unavailable. After any failed update, reconcile each module
from fresh state; neither assume rollback nor resubmit the full import blindly.

Treat `PT_WB_9013` as a binding/credential-resolution failure, not proof that a
connection was deleted. Preserve existing SQL data, report the binding gap and
continue independent modules.

## Essential invariants

- Native u64 identities remain decimal strings; allocate custom IDs without
  collision and hash only the exact contracted external key. The generated
  declaration sequence may allocate fresh-build placement origin IDs as described
  in the v50 public contract; never infer persisted, native, imported or existing
  destination IDs from sheet/visual/column order.
- Forecast requests use native Forecast: closed actuals, explicitly requested open defaults or None, and a supported date hierarchy.
- A complete input/formula record needs companions and registrations. Missing activation is not repaired by fake cache/lease/success fields.
- External Context uses `isContextDimension: true`, mirrored `visualState.embeddedSuperFilter` registrations and `visualState.filterContextSettings.filterContextStatus: true`. Keep Context off Rows/Columns, bind scoped inputs, and never seed old context hashes.
- Scenario storage context is distinct from ordinary filters, native scenario selections, edit policy and security. Preserve explicit valid selected members and input keys.
- Before financial append, dimension contracts, aliases, roles, types, grain, period, version, currency, signs and metric meanings agree; classification members can differ. Removing detail columns is not aggregation. Unknown is not zero. General optional-measure union is explicit, not an excuse to omit a required contribution. Preview-only total rows do not imply a consolidation defect.
- An embedded sheet's saved page-local rectangle is authoritative. No origin fallback, silent shrinking, source-owner movement or overlap; validate every existing/new visual and reserved area.
- Public bookmarks and their owner snapshots are real records; a Navigator alone is incomplete. Save/reopen and switching require separate evidence.
- Preserve unknown fields, untouched part bytes and unrelated existing state. Selective automated transformations are allowed; blind recursive ID replacement and user hand repair are not.
- Do not invent inaccessible routes/contracts. For remaining boundaries, report the exact missing API request/factory. UI steps, source repos and prior reports are not runtime fallbacks.

## Quick local checks

```text
python plan.py test
python plan.py build --model fixtures/model.json --spec fixtures/finance-spec.json --out trial/finance
python plan.py build --model fixtures/model.json --spec fixtures/capacity-spec.json --out trial/capacity
python plan.py build --model fixtures/context-dashboard-model.json --spec fixtures/context-dashboard-spec.json --out trial/context-dashboard
node tools/visual-placement.cjs --self-test
python tools/audit_report_definitions.py --self-test
```

These are synthetic offline checks. The fixture model uses reserved dummy identities and an `.invalid` URL; never deploy it or replace actual business data with it. The original audit helper has seven self-tests and no `--coverage` option. Run commands from the extracted runtime, or use absolute paths. Set TEMP/TMP to a writable task directory if a sandbox blocks the system temp directory.
