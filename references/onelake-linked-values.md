# OneLake storage mode: From Sheets and From Queries

This contract is for **Fabric Plan artifacts whose metadata is stored in
OneLake**, whether newly created in that mode or migrated from Fabric SQL.
The current native records determine the identity domain. It is not a change
to the semantic model's Direct Lake connection, SQL database, or input data.
Do not switch storage modes or request a SQL reader/token to resolve these links.
Connected owners must match the storage Context, and query outputs must retain it;
the storage context guide holds the bundled guards.

## Contents

- [Two storage profiles, two valid link routes](#two-storage-profiles-two-valid-link-routes)
- [Normal new-application construction](#normal-new-application-construction)
- [Package-only verification and evidence limits](#package-only-verification-and-evidence-limits)

## Two storage profiles, two valid link routes

| Route | Fabric SQL metadata | OneLake metadata |
| --- | --- | --- |
| From Sheets local Input, Forecast or Formula | Source column record `id` supplies `id/sourceId` | When `id` is absent/null, a record migrated from Fabric SQL supplies its `sqlPk`; otherwise its registered `measureGuid` supplies `id/sourceId` |
| From Queries selected output | Query registry `sqlPk` supplies the qualifier | When `sqlPk` is absent/null, the exact opaque registry `id` supplies the qualifier |

An explicitly malformed ID is an error; do not silently replace it. Keep IDs as
lossless strings, including numeric measure IDs above JavaScript's safe-integer
range and UUID/Q-prefixed query IDs. Do not infer IDs from captions or ordinals.
Absence of a SQL row ID is expected in OneLake and does **not** require replacing
a valid direct From Sheets link with an InfoBridge query.

## Normal new-application construction

1. Discover the actual model and build/import the supported complete owner sheets
   using the bundled builder. Preserve inputs, formulas, Forecast and CF. Resolve
   the new owners' identities and current column catalogs from this build or a
   fresh export of the Plan; reading native runtime catalogs through a metadata
   session has no public route here. Do not clone a reference report or copy its
   visual IDs.
2. For compatible same/subset-grain direct links, call `resolve_measure` with
   `sourceType: Visual`, current runtime `visualId`, `sourceMeasureGuid`, optional
   `columnId`, and the current owner's columns/properties. `sheet_column_id`
   selects the correct external key; do not pre-index `record['id']` in a caller.
   `registered_measure` and `from_sheet_assignment` use the same contract.
   The forecast-review library and the usecase recipe checks already call them.
3. For a query route, read the current query registry and selected post-transform
   output catalog. Use `binding_query_id`, `output_catalog`, `numeric_output_fields`
   and `resolve_measure`, not `query['sqlPk']`. Put these descriptors in build
   `queryFields`; use their exact qualified IDs for Planning Values, cards and
   chart measures. Keep semantic model dimensions in Rows/Columns/slicers.
4. Register the destination Native companion, measure metadata, formulas and
   chart/filter assignments together through the documented bundled phase.
   For an already-registered Native companion, follow its original source
   assignment; do not treat the companion itself as a new sheet output.
5. Check saved owner/source/output identities, types and context mappings.
   Initial InfoBridge refresh is optional: the user may refresh manually.
   Record materialization, rendering and edit-to-P&L propagation separately.

Native direct-link shape (partial illustration):

```json
{
  "id": "<current-source-measureGuid-if-no-row-id>",
  "sourceId": "<same-external-key>",
  "visualId": "<current-source-runtime-visual-id>",
  "sourceType": "Visual",
  "columnType": "Column",
  "aggregationType": "sum",
  "dataRoleType": "Measure"
}
```

For a new direct Sum assignment the destination internal `measureGuid` is the
decimal XXH3-64 hash of `SUM__<external-key>`. The source's `columnMeta.id` must
match its `measureGuid`, and the owner's `manage_measures` must register it once.
An owner-scoped OneLake column record may also omit `visualId`; if present, it
must match the requested owner. Never pass an unscoped/mixed catalog to the helper.
The native link uses a numeric runtime visual ID. ALM export uses the source
visual GUID for that same reference: let the normal import/export mapping handle
that separate domain; never replace one with the other by guesswork.

For From Queries, `id/sourceId` are `<qualifier>[<selected-output-id>]`,
`queryId` is the qualifier and `sourceType` is `InfoBridge`. New additive Values
hash `SUM__<qualifier>[<selected-output-id>]`. Existing registered internal IDs
must remain stable when their external assignments are reused. A source-record
ID or the source owner's measure ID is not a substitute for a query output ID.
Read the onelake query consumers guide for the typed contract.

## Package-only verification and evidence limits

First run the discovery step in the skill instructions on the phrase "OneLake
From Sheets".

```text
python scripts/plan.py resolve-measure-binding --input binding-request.json --out assignment.json
python assets/examples/onelake-linked-values/build.py <new-output-directory>
python -m unittest discover -s tests -p "test_onelake*.py"
```

The offline example uses only this package, creates new IDs and a new application
definition, and emits the direct-link native-phase payload. It uses synthetic
current-catalog responses; it is not a live deployment or a refresh test.
`assets/fixtures/onelake-linked-values.json` contains a sanitized golden binding shape
from a saved OneLake artifact, with consumer identities matched to the source
column and query metadata. Its identifiers are test evidence only, never
templates for a new application's identities.
Tests exercise resolver, registered-companion, recipe, query and cold-build paths
and preserve the SQL profile. No chat state, external repair script or earlier
report export is needed to run the shipped constructors.
