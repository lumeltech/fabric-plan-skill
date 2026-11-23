> Direct numeric-column Values (v28): use [numeric-column-values.md](numeric-column-values.md). Planning, KPI cards and charts default semantic Columns to source Sum when no explicit aggregation is supplied. Planning `sourceAggregation` is independent of grid total settings; saved measure IDs are preserved.

> v15: For the five end-to-end business examples, read [five-usecase-recipes.md](five-usecase-recipes.md). `usecase` packages every local and native phase; basic build/provision alone does not execute these complete linked workflows.

Current authoring rules: read [forecast-time-intelligence.md](forecast-time-intelligence.md)
for non-composite calendar axes, one-time Visual Columns and shared versus local
as-of controls. Read [formula-equality.md](formula-equality.md): native comparisons
use `==`; single `=` is reserved for variable declarations. These rules supersede
older comparison examples; original supplied documents remain preserved.


# Forecast, From Sheets and variance execution

## Route this request before considering omissions

For a monthly forecast consumed by a quarterly review, use the normal constructor
for the base Planning sheets and Intelligence charts, then run the callable
`runtime.forecast_review.quarterly_review` only through an explicitly approved
external service-adapter profile.
The convenience `provision` command does not compose this phase automatically.
Do not silently drop requested features. The post-import implementation is
shipped in `runtime/forecast_review.py`, but the current CLI intentionally does
not expose it. If no approved adapter profile is available, record the phase as
unavailable and keep the unchanged request at `mutation: none`.

This release includes the direct sheet link, conditional-format rule and
comparison-chart implementation as parameterized constructors. No old-report
path or agent-session dependency is required.

## Dependencies and API boundary

Python 3.11+, Node.js 24+ where needed by the existing compression/HTTPS adapter,
ordinary file/terminal tools, authorized network access and a current token are
required. There is no MCP server, agent-specific tool registration or proprietary
local checkout requirement. Keep the entire skill directory and its fixtures.

Public Plan export/update use the configured Fabric REST endpoint. The native
post-import phase uses the authenticated **workload application API**, not a
documented public Fabric REST contract. These routes remain tenant/build dependent;
packaging them does not grant access or turn them into public APIs. If your target
does not permit workload APIs, report that specific dependency; do not invent a
public equivalent or omit a feature because the package supposedly lacks code.
Home asset upload remains a separate capability and is not needed by this recipe.

`runtime.session.native_session` exchanges the authorized token for an artifact-
scoped workload token, follows the returned capacity host and scopes all calls to
the selected Plan. Resolve `powerbiApiBase` from the actual environment. Never
replace hostnames heuristically, persist tokens, or use a previous Plan's IDs.

## Configuration and callable-only execution

Example config (replace placeholders using current metadata; set the token only
in the named process environment variable):

```json
{
  "powerbiApiBase":"https://<resolved-powerbi-api-host>",
  "tokenEnvironment":"FABRIC_PLAN_TOKEN",
  "workspaceId":"<current-workspace-guid>",
  "planId":"<created-plan-guid>",
  "authorizedMutation":true
}
```

`authorizedMutation` records the user's existing authorization; it is not a
request to ask them again. Example request is bundled at
`examples/forecast-review.request.json`. Set names to the actual created sheets,
source Forecast, target native Actuals and chart layer names:

Invoke `runtime.forecast_review.quarterly_review` through the approved external
adapter with the resolved configuration and request. The callable resolves
names against the current Plan, reads only the source/target
catalogs and required ETags, creates missing companions and saves scoped properties.
It does no post-save readback or runtime test. Stable generated IDs and responses
are retained in the run directory. Reuse that directory when resuming. A changed
existing column causes a reconciliation error instead of overwriting user edits.
An asynchronous column response returns `pending-column-jobs` with the actual job
IDs and stops dependent writes; that branch requires the destination's provisioning
job completion contract. Do not claim it succeeded or blindly repeat creation.

## Exact operations and identity domains

1. Use `session.entities` then `session.page` with the externally supplied SQL
   or OneLake route profile. Resolve current owners and visuals. Embedded grids
   retain their owner; dashboard placement belongs in page-local
   `reactiveVisualProperties`.
2. Use `session.columns` with the resolved numeric source visual. It scopes the
   catalog and selects the documented SQL/OneLake column-read profile.
3. `from_sheet_assignment` uses `sheet_column_id`: the SQL source record id, or
   the registered source measureGuid for OneLake records without id. This key
   supplies both `id/sourceId`; use numeric source `visualId`, `sourceType:"Visual"`,
   `aggregationType:"sum"`, and destination `measureGuid = XXH3_64("SUM__" + key)`.
   Read [onelake-linked-values.md](onelake-linked-values.md). A missing SQL id is
   not a reason to substitute an InfoBridge pipeline or construct a fake row id.
   Do not substitute an ALM GUID or guess column ordinals. The selected route
   supports numeric SUM at the same/subset dimension grain. Target quarter fields
   must be the matching prefix of the source Year/Quarter/Month hierarchy.
4. The external `column-create` operation creates the companion, LongText
   DataInput measure (`visual_column=False`) and Formula measure. Commentary is
   repeated at the target's quarterly grain; it is not an outside-axis VisualColumn.
5. Variance formula uses native target IDs: `M_<forecastId> - M_<actualId>` through
   `formula_create`. Aggregations are Forecast Sum/Sum, Variance Formula/Formula,
   Commentary None/None. Each has a visible `manage_measures` entry and formatting.
6. `apply_negative_variance` installs the parameterized static `< 0` rule in both
   `cfProps` and `jet_cfProps`. Existing unrelated rules survive. The fixture has no
   reference-report IDs. The rule uses red font/fill on the requested variance.
7. `comparison_chart` takes a base type-50 column chart, preserves its grouping
   and layout, and assigns Forecast to AC and actuals to PY. It now selects native
   integrated variance by default: `COLUMN_INTEGRATED_VERTICAL`, aligned serialized
   template and `integratedVariance` measure config. Keep the PY assignment even
   though it is not a separate grouped-bar config entry. Read integrated-variance.md.
   Labels identify Actuals as baseline: the result is Forecast minus Actuals, not a
   previous-year claim. Ordinary filter cards are reconciled to the assigned fields.
8. Save through the external `properties-batch` operation with current
   visual/entity ETags. A successful response establishes persistence only.

These factories can also be imported individually by another Python orchestrator:
`from_sheet_assignment`, `negative_variance_rule`, `apply_negative_variance`,
`comparison_chart`, `save_properties`, and `quarterly_review`.
For new charts use `runtime.intelligence`/`construct.build` to create the base
chart, then this phase; this module is not a replacement for the chart base state.

## Repair an existing forecast from a working sheet

Read the user-designated reference before mutation. A working reference determines
configuration shape; IDs, input values and unrelated layout belong to their owners.
Use `plan.py api export` for a fresh full definition. Then:

```powershell
python plan.py forecast-repair --baseline C:/task/before.json --input C:/task/repair.json --out C:/task/updated.json
python plan.py api update --config C:/task/fabric-config.json --payload C:/task/updated.json --run C:/task/update-run --label forecast-repair
```

Repair request keys are `target_sheet`, `reference_sheet`, `target_forecast`,
`reference_forecast` (example in `examples/forecast-repair.request.json`). The repair
keeps target record IDs, label, actuals link and open formula. It copies the selected
saved Forecast defaults and same-horizon bounds, derives time-axis metadata from
actual assigned fields, and preserves all unrelated ALM bytes. References with
unmapped edit formulas/measure defaults or a different horizon require explicit
remapping/reconstruction; they are not copied blindly. Preserve the reference sheet.

## Evidence boundary

The module packages these execution paths behind an external service adapter; its
presence does not prove authentication or that calculations and formatting
render correctly. Forecast defaults derive from the current requested working
sheet. Honor a request to skip report validation; necessary identity/ETag reads
and operation polling are not post-save validation. Do not claim runtime checks
passed when they were skipped.


## Measure source binding (v10)

Read [measure-source-bindings.md](measure-source-bindings.md) before assigning or
replacing measures. Use `resolve-measure-binding` for exact PowerBI/Visual/InfoBridge
identities and typed metadata. Native companion records are not sheet outputs.
Reconcile ordinary filter cards with changed chart assignments; captions alone
do not identify a source. Preserve the prior formatting, forecasting and layout fixes.
