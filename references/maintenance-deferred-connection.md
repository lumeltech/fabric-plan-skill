# PowerTable sheets with deferred connections

When a source is resolved, prefer the complete bundled constructors described by the
PowerTable modes and PowerTable lookup source metadata guides; this fallback is only for
genuinely unavailable connections. A generic FabricSql connection path alone does not establish that
the connection is unsuitable for a specific Fabric SQL database.

When maintenance sheets are requested, a missing or unusable connection should defer source binding, not remove the sheets or stop independent Plan deployment. Create native `POWERTABLE` sheets in the same Plan and make them visible. Clearly report **connection required**. Do not promise editing, lookups, saved rows or data access until binding is complete.

**A deferred sheet is only a navigation entry and displays the PowerTable welcome/setup screen.** It is not a table with columns that merely needs credentials. Use this fallback only when the user accepts an uninitialized sheet; the current request takes precedence over an earlier willingness to defer. Preserve the sheet and continue independent modules, but report maintenance as incomplete. Never report an empty `workloadItemEntityVisuals` array as successful table construction.

## Blank sheet contract

`runtime.maintenance_shells.blank_powertable` constructs a new sheet registry entry with a fresh record GUID, a requested name/order, `sheetType: "POWERTABLE"`, `isHidden: false` and `workloadItemEntityVisuals: []`. Add its ordinary `sheets/{recordGuid}/sheet.json` part. A source-less PowerTable does not require an invented visual, fake connection GUID, fake columns or placeholder source settings. A configured table added later supplies the PowerTable visual and its source records.

Keep intended schema/table and outstanding lookups/rules in the deployment manifest. The manifest is a handoff artifact, not a made-up Plan property or a guarantee that the table exists. Do not fabricate missing key, identity or lookup metadata. Do not replace a working PowerTable with a blank sheet.

## Prepare and publish through APIs

1. Export a fresh baseline and retain its exact part bytes.
2. Prepare `requests.json` as an array, for example `[{"name":"Employee Master","table":"dbo.DimEmployee"}]`.
3. Run `python scripts/plan.py prepare-maintenance --baseline baseline.json --requests requests.json --out prepared`. This constructs the patched transport envelope, readable definition and maintenance manifest; it performs no remote mutation or SQL operations.
4. Publish the envelope with `api update`. Poll Location/Retry-After and reconcile failures before any retry. This is a same-item addition, not a new Plan.
5. Export again and verify every requested PowerTable sheet entry: type, name, visibility and the absence of a configured source. For new reports set final visibility in the public create definition. Distinguish API-persisted navigation from a visually observed setup screen.
6. Compare the pre/post existing pages and chart assignments. Keep `properties.superFilterAssignments[]` for every chart grouping/measure using `ensure_chart_filters` and `audit_chart_filters`; retain external Context, page filters, slicers and existing selections. Also call `consumer_bindings.audit_visual_consumers` with current query metadata: chart and filter IDs can both be wrong while agreeing with each other. Apply the scoped `restore_import_bindings` repair from this deployment's intent when import remaps output suffixes to input-row IDs, then export again. See the consumer repair guide.

The helper rejects existing names/GUIDs and leaves every existing non-root part byte-identical in the submitted envelope. If a previous attempt created only some sheets, reconcile the exported sheet list and rebuild requests for only the genuinely absent sheets; never create duplicates or delete existing records to retry.

An accepted same-item publication validates the deferred sheet contract only. It does not prove a rendered setup screen, lookup completion or database write readiness.

## Connect later

Resolve an authorized connection and target SQL artifact. Read the real table, key and column schema from the database definition (the SQL definition discovery guide) or the approved `sqldb-cli` companion. Then build the configured table with `powertable-table` from that verified metadata and add it to a fresh export of the Plan with `--baseline`. Use `creationMode: 2` for an existing table; this does not authorize physical table creation. Finish the requested lookup column configurations and edit policies only after target source metadata is available. Publish with `api update`. Data rendering and row save/reopen remain separate checks that the definition cannot prove.

A Fabric control-plane OAuth token is not itself a persistent SQL connection credential. A listed connection and an imported `connectionId` do not prove that the service can resolve the connection's credential for a PowerTable source or reach SQL. Credential resolution can fail even when the Fabric connection catalog lists that ID.

## Keep connection evidence separate

When learning from an authorized reference, inspect only the PowerTable sheet/visual parts, source records, column configurations and source settings in its export. Do not inherit its other application modules or hardcode its identifiers. Record the distinction among cloud connection ID, PowerTable source ID, visual ID, SQL artifact ID, host, database and schema/table. A connection catalog entry, successful source import, schema read and row save are different evidence stages.

When one read fails and another succeeds, report both outcomes and inspect the returned definition before changing routes or assuming the whole connection is broken. Do not change methods or invent query parameters merely to hide a failed check.

Never treat every primary key as auto-generated or omit a manually supplied key during insert: one table's integer primary key can be identity-generated while another's is not. Read the actual SQL metadata for each table.

## Diagnose a welcome screen before changing properties

1. Export the definition. A PowerTable sheet whose `workloadItemEntityVisuals` is empty has no grid to style. The directly owned PowerTable visual, its source and its column metadata are separate requirements. This package ships no readiness classifier, so report that classification as unavailable rather than substituting one. Claim a configured table only from its own source, column configuration and settings parts, and do not block unrelated Plan modules.
2. In an ALM package, inspect the matching visual declaration and its `properties.json`, `source.json`, `columnConfigs.json` and `sourceSettings.json`. A `sheet.json` alone cannot instantiate the grid. Preserve the PowerTable properties envelope and source-record GUID relationships. Do not copy source or column IDs from an unrelated report.
3. Compare the item's bound connections using `GET /v1/workspaces/{workspaceId}/items/{itemId}/connections` in its resolved Fabric API environment. This is different from listing connections available to the user. A bound semantic-model connection does not establish a SQL source binding. A missing SQL binding is evidence to investigate, not proof of the cause of any given credential error. Do not apply the semantic-model-only `bindConnection` API to a Plan or invent a Plan connection writer.
4. Source initialization has no separate public route in this package. Add a configured table through `powertable-table` and `api update`; when that cannot be done, record `sheet-only-uninitialized`. Do not fill a source ID with a copied reference value or keep creating duplicate connections.
5. Compare the SQL table's physical columns, read from the database definition, with the exported column configuration. Ordinary chart pivot assignments are not a PowerTable readiness test: a working PowerTable can have empty top-level `pivotAssignments`.
6. Record schema, data-render, lookup and save evidence separately; one failed check must not suppress an independent one. When an export does not finish, keep its operation ID and do not claim its source parts were retrieved.

Public connection-inventory contract: https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-item-connections
