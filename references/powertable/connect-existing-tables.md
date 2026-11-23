<!-- Existing-table PowerTable mode for `fabric-plan-skill`. Read end to end before acting. -->

# Connect Existing Tables to PowerTable

Create a new Fabric Plan containing one to five PowerTable sheets. Each sheet is backed by one user-selected Fabric SQL Database table.

## Contents

- [Preconditions](#preconditions)
- [Required user inputs](#required-user-inputs)
- [Authoring workflow](#authoring-workflow)
- Map SQL columns: use [PowerTable column mappings](column-mappings.md)
- [Review and obtain the second confirmation](#8-review-and-obtain-the-second-confirmation)
- [Create and poll](#9-create-and-poll)
- [Verify](#10-verify) and the completion summary
- [Failure reporting](#failure-reporting)
- [Must](#must)
- [Prefer](#prefer)
- [Avoid](#avoid)
- [Troubleshooting](#troubleshooting)

## Preconditions

- The caller has Contributor access to the target Plan workspace and `Item.ReadWrite.All`.
- The source is a Fabric SQL Database item, not its SQL analytics endpoint.
- Every selected source table exists and has at least one primary-key column.
- The target workspace is on a Plan-supported Fabric capacity.
- At least one accessible `FabricSql` connection exists, or the user explicitly chooses to create one through the supported connection workflow.

PowerTable connects directly to Fabric SQL Database for read/write behavior; it does not require the companion SQL analytics endpoint. Do not create or mutate the source table as part of Plan authoring.

## Required user inputs

Collect these values without defaults:

| Target | Source |
|---|---|
| Plan workspace | SQL Database workspace |
| Plan display name | SQL Database display name |
| Workspace root or existing folder | One to five schema and table selections |
|  | Optional custom sheet name for each selected table |

The user may supply fully qualified sources such as `workspace.database.schema.table`. If any workspace or database component is missing, resolve only what is unique and ask for the rest. A sheet name may be omitted; its documented default is the selected table name. Do not infer the target workspace, Plan name, source database, or table selections.

## Authoring workflow

### 1. Resolve the target and source

Follow [SKILL.md model and workspace intake](../../SKILL.md#model-and-workspace-intake)
and the `sqldb-cli` external companion's authoring guidance. List workspaces and
filter by exact display name. Then list SQL Database items in the resolved
source workspace and filter by exact display name. Reject zero or multiple exact matches.

After resolving the target workspace, follow
[creation destination](../../SKILL.md#powertable-creation-destination) to select workspace
root or resolve an existing folder, including nested or ambiguous names.

Read the SQL Database item details and retain:

- item ID
- display name
- `properties.serverFqdn`
- `properties.databaseName` (the physical database name)
- source workspace ID and display name

### 2. Select schemas, then list tables and collect the selection

After resolving the Fabric SQL Database, query its catalog read-only through
`sys.schemas`, `sys.tables`, `sys.columns`, `sys.indexes`, and
`sys.index_columns`. Search every user schema; never add a `dbo` filter unless
the user explicitly selected only `dbo`.

Show the available schemas first in a readable table:

| # | Schema | Table count | Default |
|---:|---|---:|---|
| 1 | dbo | `<count>` | Yes |
| 2 | `<schema>` | `<count>` | No |

Ask the user to select one or more schemas by name or serial number. Mark `dbo`
as the default and preselect it in the question, but do not silently accept the
default. If the user's next response selects qualified tables from a displayed
schema, that response also explicitly confirms that schema.

After schema confirmation, show every user table from the selected schemas in a
readable table. Keep the successful all-schema scan available for resolving
requested-table mismatches. Include at least:

- schema and table name
- whether the table has a primary key
- column count

Use this layout:

| # | Schema | Table | Primary key | Columns | Eligible |
|---:|---|---|:---:|---:|:---:|
| 1 | dbo | Employee | Yes | 8 | Yes |

Do not silently filter away tables without primary keys; mark them ineligible
and explain that PowerTable requires a stable row identity. Display qualified
names such as `hr.Employee`, especially when the same table name exists in
multiple schemas. Number the displayed rows in their exact display order, then
state:

`Select up to five tables. Enter comma-separated table names (for example, dbo.Employee, dbo.Department) or comma-separated serial numbers from this list (for example, 1, 3, 5).`

Accept one to five eligible tables. Even when the initial request named tables,
show the schema choices and table inventory and obtain explicit confirmation of
the qualified selections. Resolve serial numbers only against the exact
displayed list and order. Accept fully qualified selections when duplicate table
names exist across schemas. If the input mixes names and serial numbers or is
otherwise ambiguous, ask the user to restate it; do not guess. Reject a sixth
selection before inspecting any selected table.

For each selection, offer an optional custom sheet name. If the user does not provide one, use the table name. Do not require a custom name merely because the default is available.

#### Requested tables are unavailable

Conclude that a requested table is unavailable only after the all-schema query
succeeds. A permission, authentication, endpoint, or query failure is unresolved
discovery, not evidence that the table does not exist.

If one or more requested tables do not appear in the complete inventory:

1. Show the unavailable qualified names and the schemas/tables that were found.
2. If the same unqualified name exists in another schema, show each exact match
   in a table and ask whether one is the intended source. If needed, return to
   schema selection and let the user add that schema.
3. Offer these explicit choices:
   - **Create the missing tables** -- switch to `powertable-from-scratch`, read
     [modeling](modeling.md), [create from scratch](create-from-scratch.md),
     [column mappings](column-mappings.md),      and the external
     [`sqldb-cli` authoring guide](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli/references/authoring.md), then
     collect any missing business scope and run that mode's complete preview
     and approval flow.
   - **Select another database** -- return to database resolution, scan all of
     its user schemas, and show a fresh numbered inventory.
   - **Cancel** -- make no changes.
4. Stop for the user's choice. Do not silently create tables, choose another
   database, or reinterpret similarly named tables.

When the user chooses create, carry forward only confirmed coordinates and
business requirements. Table names alone are not a complete schema design.
Connection confirmation from the existing-table attempt does not authorize
from-scratch SQL or Plan writes.

### 3. Inspect every selected table read-only

Use the external
[`sqldb-cli` consumption guide](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli/references/consumption.md)
and Go `sqlcmd` with Microsoft Entra authentication. Query `sys.columns`, `sys.types`, `sys.indexes`, `sys.index_columns`, `sys.foreign_keys`, and `sys.foreign_key_columns` for the requested object.

Collect columns in ordinal order:

- name and SQL type
- maximum length, precision, and scale
- nullability
- identity flag
- primary-key membership and key order
- foreign-key constraint, referenced schema/table/column, and constraint column count
- candidate display columns from each referenced table

For populated tables, inspect non-FK bit/boolean, integer, and character columns using case-sensitive distinct values. Only one recognized boolean value or a recognized boolean pair can form a checkbox. Infer a missing `true/false`, `yes/no`, `y/n`, or `1/0` counterpart with the source type and standard casing. Preserve source casing and type. Other two-value pairs, such as `DineIn`/`Takeaway`, retain their text/number mapping; when the user explicitly requests a closed text category, configure `singleSelectColumns` instead. For empty tables, default only bit/boolean columns to checked `1` and unchecked `0`.

If a confirmed object disappears between inventory and inspection, report the
changed source state and return to the unavailable-table choices: create it
through `powertable-from-scratch`, select another database, or cancel. Stop if a
selected object has no columns or no primary key; identify the failing selection
and ask the user to remove it, choose another table, or fix it through
the external `sqldb-cli` authoring workflow. Preserve every primary-key column for a composite key.

For each scalar foreign key, choose a referenced textual display column deterministically:

1. `<referenced-entity>_name`, after removing a conventional source prefix such as `adv_`
2. `name`, `display_name`, `title`, or `label`
3. `first_name`
4. another column ending in `_name`
5. the first non-key textual column by ordinal

If no textual display column exists, stop and ask the user which referenced column should be displayed. The canonical PowerTable definition does not establish a safe shape for composite foreign-key lookups; stop and request an explicit design rather than inventing one.

### 4. Allocate unique sheet names

Before staging any sheet, compare its proposed name case-insensitively with names already allocated in the new Plan definition.

1. Start with the user-supplied sheet name, or the table name when omitted.
2. If unused, allocate it unchanged.
3. If already used, append ` (2)`, ` (3)`, and so on until the name is unique.
4. Preserve selection order so suffix assignment is deterministic.

Treat generated suffixes as proposals, not hidden assumptions. Show every adjusted name in the final review and let the user edit it before creation.

### 5. Discover FabricSql connections

Call `GET /v1/connections`, following `continuationUri` until exhausted. Filter the returned objects to:

```text
connectionDetails.type == FabricSql
```

Do not claim the list is database-specific: List Connections returns connections visible to the caller, and the response does not provide a reliable binding to one SQL Database item.

Behavior by candidate count:

| Count | Required behavior |
|---|---|
| 0 | Stop. Offer to create a FabricSql connection, but do not create one silently. |
| 1 | Show its display name, ID, connectivity type, and credential type. Ask the user to confirm it. |
| 2+ | Show all candidates with those fields and ask the user to select one. |

End this interaction with:

`Use this FabricSql connection? (yes / choose another / cancel)`

Only literal, unambiguous approval selects the proposed connection. A previous request to create a PowerTable is not connection approval.

### 6. Build the PowerTable definition

Generate fresh identifiers and construct four shared `InlineBase64` parts:

1. `.platform`
2. `connectedPlanning/infobridge.json`
3. `definition.json`
4. `planProperties.json`

For each selected table, add five sheet-specific parts:

1. `sheets/{sheetId}/sheet.json`
2. `sheets/{sheetId}/visuals/{visualId}/columnConfigs.json`
3. `sheets/{sheetId}/visuals/{visualId}/properties.json`
4. `sheets/{sheetId}/visuals/{visualId}/source.json`
5. `sheets/{sheetId}/visuals/{visualId}/sourceSettings.json`

The total part count is `4 + (5 * selected table count)`. Use forward slashes in part paths. Every root sheet and visual must use `POWERTABLE`. Each visual source must include:

- confirmed `connectionId`
- SQL server host and physical database name
- SQL Database item ID and display name
- source workspace ID and display name
- schema and table

After the user confirms the connection, generate the staged body with a JSON array in selection order:

```powershell
$tableSelections = @(
  @{ schemaName = "dbo"; tableName = "Employee" }
  @{ schemaName = "dbo"; tableName = "Department"; sheetName = "Departments" }
) | ConvertTo-Json -Compress

pwsh -NoProfile -File references\powertable\resources\New-PowerTablePayload.ps1 `
  -WorkspaceName "<source workspace>" `
  -DatabaseName "<SQL Database item>" `
  -PlanName "<target Plan name>" `
  -ConnectionId "<confirmed FabricSql connection id>" `
  -TableSelectionsJson $tableSelections `
  -OutputPath "<temporary JSON path>"
```

Each selection requires `schemaName` and `tableName`; `sheetName` is optional. The helper performs only Fabric GETs, read-only SQL metadata queries, unique-name allocation, and a local payload write. It does not create the Plan. Use its per-sheet summary and saved payload for the final review.

Use `checkboxMappings` only for recognized boolean values as documented in the directly linked column-mapping reference. It cannot turn an arbitrary category pair into a checkbox. The helper validates source casing and numeric-versus-string type.

The helper rejects zero or more than five selections before resolving the workspace, database, connection, or table metadata.

Use the Plan definition schemas documented by Microsoft. Preserve these proven invariants:

- `definition.json` contains the schema, empty cube partition references, sheets, and `workloadItemName`; do not add `appDBconnection`.
- `source.json` uses `creationMode: 5`.
- `properties.json` uses the PowerTable Properties schema; do not paste fields from an unrelated Plan export.
- `dbMeta.precision` and `dbMeta.scale` preserve values returned by SQL metadata for numeric columns. Do not invent numeric metadata or unsupported members such as `primaryKeyOrdinal`.
- For a PowerTable-only Plan, do not invent a semantic model reference; PowerTable connects directly to Fabric SQL Database.

### 7. Map SQL columns

Apply [PowerTable column mappings](column-mappings.md) to every source column
in ordinal order. Foreign-key mapping takes precedence over the underlying SQL
type. That reference defines the exact checkbox, temporal, decimal,
numeric-intent, text, and lookup metadata contract.

Default source settings may enable row add and row update for all users, disable row delete, and enable comments. Show these choices in the preview; do not conceal them as implementation defaults.

### 8. Review and obtain the second confirmation

After the connection is confirmed and before any write, show the complete configuration:

```text
Target workspace : <workspace>
Destination      : <workspace root, or full folder path and targetFolderId>
Plan             : <plan name>
Connection       : <display name> [<connection id>] (confirmed)
Total sheets     : <count>

1. Sheet         : <unique sheet name> (POWERTABLE)
   Source        : <workspace>.<database>.<schema>.<table>
   Name change   : <requested/default name -> unique name, only when adjusted>
   Columns       : <count>
   Primary key   : <ordered key columns>
   Date inputs   : <date columns, or none>
   Date-time     : <datetime-family columns, or none>
   Time inputs   : <time columns, or none>
   Checkbox      : <column (checked: <exact value>, unchecked: <exact value>), or none>
   Decimal       : <decimal/numeric/float columns, or none>
   Currency      : <money/smallmoney or clear integer monetary intent, or none>
   Number        : <integer fallback columns, or none>
   Rating        : <integer columns with clear rating intent, or none>
   Lookups       : <local column -> referenced table.id shown as label, or none>

2. Sheet         : <next unique sheet name> (POWERTABLE)
   Source        : <workspace>.<database>.<schema>.<table>
   ...

Row add/update   : enabled
Row delete       : disabled
Definition parts : <4 + (5 * total sheets)>
Endpoint         : POST /v1/workspaces/<workspace id>/plans
```

End with:

`Create this Plan with <count> PowerTable sheet(s)? (yes / edit / cancel)`

For a folder destination, add "and move it to <full folder path>" to that
question. Final approval covers creation and that move. A destination change
requires a refreshed review and approval.

Do not write until the user explicitly confirms this review. Connection confirmation alone does not authorize creation. An `edit` response returns to the affected selection, sheet name, mapping, or permission question and requires a refreshed review.

### 9. Create and poll

Send the definition through:

```http
POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/plans
```

The body contains `displayName`, a description of at most 256 characters, and `definition.parts`. Every Fabric call, including every poll and result fetch, must carry
`x-ms-fabric-skill: fabric-plan-skill`.

- `201 Created`: capture the returned Plan ID.
- `202 Accepted`: poll the `Location` operation using `Retry-After` when supplied. Stop on `Failed` and report the service error. On `Succeeded`, resolve the created Plan ID from the operation result or by exact list-and-filter.
- `429`: honor `Retry-After`; do not busy-loop.

One final confirmation authorizes one create attempt. Do not repeat a write merely because command output was empty or headers were not captured. Verify state first; a retry needs a corrected payload and fresh confirmation.

After creation completes and the Plan ID is resolved, use
[Move Item](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/move-item):
`POST /v1/workspaces/{workspaceId}/items/{planId}/move` with body
`{"targetFolderId":"<confirmed folder ID>"}`. Expect `200 OK`; honor
`Retry-After` on `429`. Skip this call for workspace root. If moving fails or
its outcome is uncertain, read current placement before any retry; never issue
another Plan create.

### 10. Verify

Call [Get Plan](https://learn.microsoft.com/en-us/rest/api/fabric/plan/items/get-plan)
at `GET /v1/workspaces/{workspaceId}/plans/{planId}`. Its top-level `folderId`
must equal the confirmed `targetFolderId`; for workspace root it must be absent
or null. A failed read or mismatch means placement is unverified. This check is
separate from definition readback; folder placement is not a definition part.

Call the Plan-specific Get Plan Definition endpoint. It can return inline `200 OK` or `202 Accepted`; for 202, poll `Location` or `Operation-Location` to `Succeeded`, then GET its `/result`.

Decode all `InlineBase64` parts and verify:

- the sheet count equals the reviewed selected-table count
- every reviewed sheet name exists exactly once and every sheet uses `sheetType == POWERTABLE`
- every sheet contains exactly one PowerTable visual
- all `4 + (5 * sheet count)` expected parts exist
- every sheet's source connection, database item, workspace, schema, and table match the review
- every sheet's column count and primary-key flags match its SQL metadata
- every SQL `date` column uses `columnType: 4`, `visualColumnType: 1`, and `columnMeta.format: DEFAULT_LOCALE`
- every SQL `datetime`, `datetime2`, `datetimeoffset`, or `smalldatetime` column uses `columnType: 12`, `visualColumnType: 1`, and `columnMeta.format: DEFAULT_LOCALE_TIME`
- every SQL `time` column uses `columnType: 8` and `visualColumnType: 1`
- every reviewed checkbox candidate uses `columnType: 11`, `visualColumnType: 1`, source-typed values, exact observed casing, and the documented inferred casing for a missing counterpart
- every empty-table SQL `bit`/boolean column uses checked `1` and unchecked `0`; empty integer and character columns retain their normal non-checkbox mappings
- every SQL `decimal`, `numeric`, `float`, `real`, or double-alias column uses `columnType: 13`, `visualColumnType: 1`, preserves SQL precision and scale in `dbMeta`, and preserves SQL scale as `noOfDecimals`
- every SQL `money` or `smallmoney` column uses `columnType: 19`, `visualColumnType: 1`, and preserves SQL scale as `noOfDecimals`
- every non-checkbox integer column with clear monetary intent uses `columnType: 19`; every non-checkbox integer with clear rating intent uses `columnType: 21`; every remaining non-checkbox integer uses `columnType: 6`; all use `visualColumnType: 1` and preserve SQL precision/scale
- every scalar FK uses `columnType: 2`, `visualColumnType: 3`, `LOAD_FROM_DATABASE`, and the previewed lookup target and label

End with the completion summary defined in
[SKILL.md](../../SKILL.md#powertable-completion-summary), without waiting to be asked:

| Field | Value |
|---|---|
| Workspace name | Display name of the workspace that holds the Plan |
| Artifact name | Plan display name (`Plan`) |
| Report URL | `https://app.powerbi.com/groups/{workspaceId}/plans/{planId}` |

If verification fails, report creation as unverified rather than successful, but still include the summary.

## Failure reporting

Every failure response must include:

- **Failed stage** -- discovery, connection validation, payload generation,
  Plan create, LRO polling, folder move, or properties/definition readback
- **Reason** -- exact error code/message or observed mismatch; if unknown, say
  what could not be determined rather than guessing
- **Current state** -- what was not written, what may exist, and what was
  verified
- **Corrective actions** -- specific user actions or safe next operations
- **Approval boundary** -- whether a corrected retry needs refreshed connection
  confirmation, a new final write approval, or only read-only verification

Apply these outcomes:

| Failure point | State to report | Corrective actions |
|---|---|---|
| Schema/table catalog query fails | Availability is unknown; no Plan write occurred | Correct account, permissions, endpoint, or query access, then rerun the complete all-schema scan |
| Requested table is absent | No write occurred | Create through `powertable-from-scratch`, select another database, or cancel |
| Connection is missing, stale, or unauthorized | No Plan write occurred | Create/share/re-authorize a FabricSql connection, refresh the list, directly validate it, and reconfirm |
| Payload generation fails | No Plan write occurred | Correct unsupported metadata, table shape, lookup label, or source values; regenerate and show a refreshed preview |
| Plan create is rejected before acceptance | No Plan is known to exist | Report the service error; correct permissions, folder/name collision, connection, or payload, then obtain fresh approval for a changed retry |
| Create returns `202` but local polling/output fails | Plan state is uncertain | List/read back by exact name and ID before any retry; never issue a duplicate create blindly |
| Plan created but move failed or outcome is uncertain | **Partial state:** the Plan exists, but requested placement is incomplete or unverified | Report Plan ID, URL, exact move error, intended folder, and actual `folderId` if known; retain the Plan, refresh folders and read properties, then obtain fresh approval for a move-only retry; never recreate or delete the Plan |
| Plan properties or definition readback fails or differs | Plan exists but is unverified | Report the Plan ID and mismatches, including expected versus actual `folderId`; retry read-only retrieval, correct access, or ask for approval before corrective writes |

Never reduce a failure to "Plan creation failed." Name the reason, persisted
state, and actionable recovery path.

## Must

- Keep connection confirmation and write confirmation separate.
- Require explicit target and source selections; use only the documented table-name default for omitted sheet names.
- List available tables as numbered choices and wait for one to five comma-separated table names or displayed serial numbers.
- Show available schemas in a numbered table after database selection, mark
  `dbo` as the default, and obtain explicit selection before confirming tables.
- Search and display tables across every user schema, then require explicit
  confirmation of qualified schema/table selections.
- When requested tables are unavailable, offer create through
  `powertable-from-scratch`, select another database, or cancel.
- Reject a sixth table before selected-table inspection, and clarify mixed or ambiguous selection formats.
- Keep sheet names unique within the new Plan and disclose every generated suffix in the review.
- Use the Plan-specific create and definition endpoints.
- Preserve composite primary keys and source column order.
- Configure scalar foreign keys as database-backed lookups. For populated bit, integer, and character columns, configure a checkbox only for one recognized boolean value or a recognized case-sensitive boolean pair; for empty tables, default only bit/boolean columns to `1`/`0`.
- Leave the source table and connection unchanged.

## Prefer

- Generate JSON and base64 programmatically to avoid quoting and encoding errors.
- Save the exact previewed request body before confirmation and submit it unchanged.
- Use exact, case-sensitive matching when duplicate display names would be unsafe.

## Avoid

- Generic item creation for a Plan.
- Selecting a sole connection without asking.
- Hardcoded workspace, item, connection, sheet, visual, or source GUIDs.
- Reusing identifiers copied from another Plan.
- Retrying a potentially successful create before readback.

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| No FabricSql connections | None are visible to the caller | Offer explicit connection creation; do not continue silently. |
| Multiple connections | List Connections is tenant-visible, not reliably database-bound | Ask the user to choose. |
| Duplicate proposed sheet names | Two selections use the same default or custom name | Propose deterministic numeric suffixes, show them in the review, and allow edits before confirmation. |
| More than five selected tables | One Plan request exceeds the supported batch size | Ask the user to choose at most five; do not inspect or stage the excess selection. |
| Requested table is not in the all-schema inventory | The table is absent or the wrong database was selected | Offer create through `powertable-from-scratch`, select another database, or cancel. |
| Populated bit/boolean column has one recognized value | The source currently contains only one checkbox state | Infer the missing recognized counterpart with the same source type and standard casing. |
| Populated bit/boolean column has no recognized value, contains `NULL`, or has more than two values | The source cannot safely establish checkbox states | Show the observed values and ask the user to correct the source or choose another table. |
| Integer or character column has an unrecognized two-value pair | The values are categories, not recognized boolean states | Retain Text/Number, or explicitly configure a closed text category through `singleSelectColumns`; do not use `checkboxMappings`. |
| Character values differ only by case | Database collation may otherwise merge them | Discover them with binary case-sensitive collation and preserve their exact casing in the configuration. |
| Table has no primary key | No stable row identity | Stop and ask the user to choose another table or add a key through `sqldb-cli`. |
| Referenced table has no clear text label | A lookup ID can be resolved but its user-facing label cannot | Show candidate referenced columns and ask the user to choose. |
| Composite foreign key | The canonical definition does not prove a safe generated lookup shape | Stop and request an explicit lookup design. |
| `CorruptedPayload` | Invalid base64, schema, path, or part shape | Correct the staged payload; obtain fresh write confirmation. |
| LRO reports `Failed` | Service rejected provisioning | Report the operation error and do not claim creation. |
| Definition readback is 202 | Get Definition is asynchronous | Poll, then fetch `/result`; do not treat 202 as the definition body. |
