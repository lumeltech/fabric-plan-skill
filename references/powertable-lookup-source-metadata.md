# PowerTable database lookups and source metadata

Use this guide when a policy/master table stores IDs but should display lookup
labels, when a saved PowerTable lacks its lookup configuration, or when its
source metadata lacks workspace/database/connection display names. Discover
`POWERTABLE-CONFIG`, `POWERTABLE` or `LOOKUP`. These are PowerTable column
properties, not Planning Advanced Lookup, semantic relationships or InfoBridge
field mappings.

## Contents

- [Choose the stored key and visible label](#choose-the-stored-key-and-visible-label)
- [Native properties and bundled constructor](#native-properties-and-bundled-constructor)
- [Source metadata belongs to the destination](#source-metadata-belongs-to-the-destination)
- [Scoped repair of an existing report](#scoped-repair-of-an-existing-report)
- [Portable example and evidence boundary](#portable-example-and-evidence-boundary)

## Choose the stored key and visible label

Use the current physical SQL catalog and the business relationship to map each
foreign key to its lookup table's unique key and requested display column. Do not
convert every integer or every name ending in ID to a lookup. Identity PKs remain
numeric and read-only. A key can remain read-only while its display uses a lookup;
lookup presentation does not grant editing rights or replace stored IDs.

The Supply Policy example captured these mappings:

| Stored column | Lookup table | Linking key | Display column |
|---|---|---|---|
| PH_ProductID | dbo.PH_Product | PH_ProductID | ProductCode |
| RegionID | dbo.DimRegion | RegionID | RegionCode |
| MonthID | dbo.DimMonth | MonthID | MonthName |
| ScenarioID | dbo.DimScenario | ScenarioID | ScenarioCode |

These names illustrate a confirmed saved configuration, not universal defaults.
Resolve the analogous relationship in another model. The reference Region lookup
also follows DimRegion.CurrencyID into DimCurrency.CurrencyID and displays
CurrencyCode. Preserve that ordered chain when requested; do not invent it for
unrelated tables.

## Native properties and bundled constructor

`runtime.table_columns.column_config` accepts `kind="database-lookup"`, an explicit
`lookup` and current `lookup_catalog`. Pass `allow_edit=False` for keys the business
requires read-only; use `configured_table(..., allow_add=False)` when inserts must
be disabled. These choices are separate from lookup configuration.

```json
{
  "columnName": "RegionID",
  "displayName": "RegionCode",
  "allowEdit": 0,
  "columnType": 2,
  "visualColumnType": 3,
  "columnMeta": {
    "selectionMethod": "LOAD_FROM_DATABASE",
    "allowAddingNewOptions": false,
    "isFilterBasedOnAnotherValue": false,
    "options": [],
    "optionLinking": {
      "lookupConfig": [
        {"id":"RegionID","label":"RegionCode","linkingColumn":"RegionID","order":0,"schema":"dbo","table":"DimRegion"},
        {"id":"CurrencyID","label":"CurrencyCode","linkingColumn":"CurrencyID","order":1,"schema":"dbo","table":"DimCurrency"}
      ]
    }
  }
}
```

This is an excerpt: keep the complete column's physical `dbMeta`, `columnGuid`,
`recordGuid`, mandatory/visibility settings and other unrelated metadata.
`id` names the unique key in the lookup table. `linkingColumn` names the column
in the preceding table that holds it: this column for the first hop, the previous
lookup table's column for later hops. They need not have the same name.
The helper checks compatible key types, uniqueness, key/label existence and the
availability of each chained FK. Use only a catalog resolved for this source's
database. It does not inspect row data or prove business validity.

Constructor input for the ordered relationship:

```json
{
  "schema":"dbo", "table":"DimRegion", "key":"RegionID", "label":"RegionCode",
  "chain":[{"column":"CurrencyID","schema":"dbo","table":"DimCurrency","key":"CurrencyID","label":"CurrencyCode"}]
}
```

Keep `options:[]` so runtime loads choices from the current database. Do not copy
cached option rows or allow free-form additions to a database-backed key picker.

## Source metadata belongs to the destination

A complete configured `source.json` needs `source.meta` in addition to its source
binding. Fill these values from the destination records:

| Property under source.meta | Current authoritative value |
|---|---|
| connectionName | GET /v1/connections/{source.connectionId} → displayName |
| workspaceId | source.sqlTargetArtifact.workspaceId |
| workspaceName | GET /v1/workspaces/{workspaceId} → displayName |
| databaseId | source.sqlTargetArtifact.artifactId |
| dbDisplayName | GET /v1/workspaces/{workspaceId}/items/{artifactId} → displayName |

Use the authenticated Fabric endpoint resolved for the destination. Keep its
connectionId, source recordGuid, SQL host/database/schema/table and artifact
binding. Never copy the reference report's connectionId or labels: a working
reference can use a different authorized connection to the same database.
Preserve existing meta fields such as totalRows. A totalRows-only object is not
complete source metadata. An observed `workspaceName` null error is a symptom,
not proof that this is the only possible cause.

For new ALM construction, provide `connectionName`, `workspaceName` and
`dbDisplayName` on the resolved connection input, alongside connectionId, dbHost,
dbName, artifactId and workspaceId. `configured_table` includes these in its
source part and rejects missing labels. `existing_source` creates only a smaller
source request; that request alone is not a complete configured grid.

`runtime.powertable_config.enrich_source(source, connection, workspace, database)`
accepts current API record objects (`id`, `displayName`) and rejects identity
mismatches before filling metadata.

## Scoped repair of an existing report

1. Export the current definition and resolve the exact sheet GUID. Read its current
   source and lookup catalog; obtain the three metadata records above.
2. Create a request containing `sheet_guid`, `lookups` keyed by physical column
   name, `lookup_catalog`, and `source_metadata` with connection/workspace/database
   records. No token belongs in that file.
3. Run the bundled local command:

```text
python scripts/plan.py repair-powertable-config --baseline current-definition.json --input repair.request.json --out candidate
```

It produces candidate/definition.json and candidate/changes.json. It changes only
the selected sheet's columnConfigs.json and source.json when needed. All column
editability, sourceSettings (including ROW_ADD), source bindings, unrelated fields,
Planning sheets, InfoBridge, inputs, formulas and storage mappings are preserved.
Untouched definition parts retain their original encoded bytes. The helper is
idempotent and is not a deployment command.

Use the normal authorized update workflow separately. Do not bypass an unrelated
whole-report guard or rewrite InfoBridge lineage as an implicit part of this fix.
If existing native lineage is rejected, report that specific blocker and preserve
the candidate. Reconcile it through the appropriate supported workflow and scope.
HTTP 202 or `Running` is pending, not saved. Poll only the save operation when the
user asks for status only. Do not resubmit a pending write without an explicit
retry request, and do not equate stopping local polling with cancelling the server.
Respect a request to skip report/runtime validation; state that limit explicitly.

## Portable example and evidence boundary

```text
python assets/examples/powertable-lookups/build.py draft
python scripts/plan.py repair-powertable-config --baseline draft/baseline.json --input draft/repair.request.json --out repaired
```

The example builds its own illustrative schema and creates both a new configured
PowerTable and an existing-definition repair. It needs no chat, local repair
script, cached report, production IDs or credential. Replace illustrative records
with current destination metadata before any authorized deployment.

The lookup and source properties above come from a working report compared with
an incomplete definition. Offline helper and package checks are separate evidence:
they do not confirm a pending save or the target UI behavior.
