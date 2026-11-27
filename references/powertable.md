# PowerTable modes, SQL ownership and Plan definition

Choose the source state before planning. `fabric-plan-skill` owns the PowerTable
definition (`source.json`, `columnConfigs.json`, `sourceSettings.json`,
`properties.json`, `forms.json`, `automations.json`) and the Fabric Plan
lifecycle. The external `sqldb-cli` companion owns SQL catalog inspection, DDL,
DML and read-only T-SQL:
<https://github.com/microsoft/skills-for-fabric/tree/main/skills/sqldb-cli>.
Install or attach it separately. A Plan-definition request alone never
authorizes a database write.

| UI creation mode | Route in this skill | `creation_mode` |
|---|---|---|
| Import existing table | Read the catalog with `sqldb-cli`, then `powertable-table` | 2 |
| Create from scratch | Approved DDL through `sqldb-cli`, re-read the catalog, then `powertable-table` | 1 |
| Import from file (CSV/XLSX) | No public route. Prepare SQL tables explicitly through approved `sqldb-cli` DDL/DML, then use the from-scratch Plan route and label the result accordingly. | 1 |
| Create from template | No workload route. Design and create the template's tables explicitly through approved `sqldb-cli` DDL, then use the from-scratch Plan route. | 1 |
| Import from semantic model | No public live-sync route. A separately approved snapshot-to-SQL flow may create a from-scratch table, but must not claim native semantic-model synchronization. | 1 |
| Existing-sheet analysis | Decode the Plan definition, confirm database/schema/table and column mappings, then query read-only with `sqldb-cli` | n/a |

Tables built through the file, template or snapshot routes record
`creation_mode` 1 because the table is created by DDL. The product's 3/4/5 origins
depend on upload tasks, sync records and templates owned by the workload service.
Do not call private service routes for table creation or other workload routes to
imitate them, and do not present them as Fabric REST APIs.

## Contents

- [Column defaults](#column-defaults)
- [Build the table definition](#build-the-table-definition)
- [Row access](#row-access)
- [Forms and Automations](#forms-and-automations)
- [Approvals](#approvals)
- [Existing tables: keys, lookups and analysis](#existing-tables-keys-lookups-and-analysis)

## Column defaults

`powertable-table` and `table_column_configs` give every physical column the
type the product assigns when a table is added:

| SQL type | PowerTable column | Notes |
|---|---|---|
| `int`, `bigint`, `smallint`, `tinyint` | Number (6) | |
| `decimal`, `numeric`, `money`, `smallmoney`, `float`, `real` | Decimal (13) | `float` shows 1 decimal, the others 2, unless overridden |
| `date` | Date (4) | |
| `datetime`, `datetime2`, `smalldatetime`, `datetimeoffset` | Date time (12) | Locale date-time format with no time zone, as the product sets it. Set `time_zone` to `timezone-independent` to keep stored values unshifted, or `user-local` to treat them as UTC |
| `bit` | Checkbox (11) | Checked `1`, unchecked `0` |
| Any other type, including the text types, `uniqueidentifier`, `xml`, `varbinary` and `time` | Text (1) | Plain text. The skill never picks Single select by default; with schema inference on, the product itself can make a foreign-key column a database lookup |

SQL Server `timestamp` and `rowversion` have no default; choose a compatible kind
explicitly or report the column.

Every column, including the primary key, is displayed (`hideColumn: 0`). As in
the product's create-table flow, a `NOT NULL` or primary-key column is mandatory.
Identity and computed columns are also read-only. Change presentation only on
request, per column:

```json
{"columns": {
  "Status": {"kind": "text-options"},
  "DepartmentID": {"kind": "database-lookup",
                   "lookup": {"schema": "dbo", "table": "Department", "key": "DepartmentID", "label": "DepartmentName"}},
  "Salary": {"decimals": 0, "hide": true},
  "LastLogin": {"time_zone": "user-local"},
  "Code": {"display_name": "Employee code"}
}}
```

`text-options` is Single select with distinct values; `database-lookup` needs
`lookup_catalog` from the current SQL catalog. `date` may be chosen for a
datetime column to hide the time; `datetime` is never valid on a `date` column.

## Build the table definition

1. Resolve the destination workspace, Fabric SQL Database, connection and one
   explicit schema. List user schemas; `dbo` is the default but needs
   confirmation.
2. Run `surfaces.PHYSICAL_METADATA_SQL` and `surfaces.UNIQUE_METADATA_SQL` with
   `@schema`/`@table` through `sqldb-cli`. Both are read-only. An empty unique
   result is valid; a missing one is not.
3. For from scratch, file, template or snapshot, first preview the complete
   table layout and obtain explicit DDL approval. Model at most five tables with
   stable primary keys and required foreign keys. Use a date-only `DATE` for
   dates and `DATETIME2(0)` for date and time. Execute the approved
   transactional DDL with `sqldb-cli` and roll back on failure. Load rows only
   with separate approval (synthetic rows: 1-100 per table). Then run step 2 on
   the committed table: DDL success is not proof of the schema.
4. Write the request and construct the candidate on a fresh export:

```json
{
  "name": "Employees",
  "creation_mode": 2,
  "connection": {"connectionId": "...", "dbHost": "...", "dbName": "...", "artifactId": "...",
                 "workspaceId": "...", "connectionName": "...", "workspaceName": "...", "dbDisplayName": "..."},
  "catalog": {"schema": "dbo", "table": "Employee", "rows": [], "unique_rows": []},
  "columns": {},
  "allow_add": true, "allow_update": true, "allow_delete": false
}
```

```sh
python scripts/plan.py powertable-table --input table.request.json --baseline current-definition.json --out candidate
```

`rows`/`unique_rows` are the two query results (objects keyed by the selected
column names). `table` may replace `catalog` when the physical metadata came
from `sql_definition.physical_table`. Without `--baseline` the command writes
only the new sheet and parts. `changes.json` lists each column's type code;
compare it with the request before `api update`.

5. Create or update the Plan through the public Fabric Plan API, then read back
   the complete definition and confirm source identity, column configs, row
   actions, forms and automations.
6. Report partial state if SQL committed but the Plan update failed. Never rerun
   DDL or row loads merely to resume Plan creation.

## Row access

Row actions carry their audience. New tables get the product default:
`ROW_ADD` and `ROW_UPDATE` enabled for **All users** (`all_users`,
`filterType: 1`, `filter: {}`), `ROW_DELETE` disabled. Enabling delete adds the
same All users selection. Validation rejects an enabled row action with no
selection.

PowerTables saved without a selection show nothing on the Row access tab.
Repair them on a fresh export; only enabled actions without a selection change:

```sh
python scripts/plan.py repair-powertable-row-access --baseline current-definition.json --out candidate
```

Pass `--input` with `{"sheet_guids": ["<sheet GUID>"]}` to limit the repair.

## Forms and Automations

Forms and Automations are Plan definition parts in the PowerTable visual folder.
The Plan import creates and updates them, so author them on a fresh export and
publish through the public API:

```json
{
  "sheet_guid": "<PowerTable sheet GUID>",
  "forms": [{
    "title": "New employee",
    "description": "",
    "fields": [{"column": "Code"}, {"column": "FullName"}, {"column": "JoinDate"},
               {"column": "Active", "defaultValue": true}, {"column": "Department", "mandatory": 0}],
    "config": {"showTitle": true, "submissionMessage": "Thanks", "fieldLabel": "stacked"}
  }],
  "automations": [{
    "name": "Notify HR",
    "trigger": "ROW_UPDATED",
    "watch_columns": ["Active"],
    "conditions": {"combinator": "and", "rules": [{"field": "Active", "operator": "equals", "value": true}]},
    "actions": [{"type": "SEND_MAIL", "config": {"subject": "Status changed", "body": "...", "to": ["hr@example.com"]}}]
  }]
}
```

```sh
python scripts/plan.py powertable-features --baseline current-definition.json --input features.request.json --out candidate
```

Forms:

- Fields name configured columns. Every mandatory column must be on the form
  (the product blocks submission otherwise) and stays mandatory there.
  Read-only columns (identity, computed, read-only lookups) cannot be fields.
- Each field and layout node references the column's `recordGuid`; the import
  maps it to the runtime column. Do not use runtime column IDs or display names.
- Submissions need `ROW_ADD` access; the command warns when adding is disabled.
- Titles are unique per table; the default layout lists the fields in order.

Automations:

- Triggers: `ROW_CREATED`, `ROW_UPDATED` (optional `watch_columns`),
  `ROW_DELETED`. Actions run in order in one action block: `SEND_MAIL`
  (subject, body, to, optional cc/bcc), `MS_TEAMS` (message, channelDetails),
  `CREATE_RECORD` and `UPDATE_RECORD` (connectionId, schema, table, fields;
  update also needs a conditions group).
- Trigger conditions use one `{combinator, rules}` group on Text, Number,
  Decimal or Checkbox columns. The engine evaluates this group shape; the public
  schema lists conditions as an array, so validation reports it as a native
  extension.
- `{{...}}` value references pass through unevaluated. Copy their syntax from an
  exported automation of the same tenant. Scheduled, form-submitted, button,
  conditional-branch and sync automations are not authored here.

An update that omits an existing `forms.json`, `automations.json` or
`approvals.json` deletes those records on import. Always patch a fresh export; never rebuild a
PowerTable folder from scratch for an existing Plan.

Product exports omit each automation's `recordGuid`, so the import cannot match
exported automations: any update that carries them may recreate or overwrite
them and lose their run history. `powertable-features` and
`repair-powertable-row-access` warn when this applies; tell the user and verify
every automation after publishing.

## Approvals

`approvals.json` holds the approval workflow (rule type, levels, filters) and
travels with the definition: preserve it. When a PowerTable has none,
`powertable-features` can add one from an `approvals` request with the rule
type (`DEFAULT`, `MANUAL` or `LOOKUP`), persist flag (`SAVE_AFTER_REVIEW` or
`SAVE_BEFORE_REVIEW`), ordered levels (name and description) and routing filters
(name, filter object and order). An optional `multi_level_enabled` sets whether
multi-level approval is on; when the request omits it, the flag is not written.
It refuses to replace an existing workflow.
Approver users are not definition content. Assigning approver users has no
supported public route. Do not use a workload endpoint, a private token exchange,
a browser session or any other private service route.
Report the workflow as partially configured: the definition can carry approval
structure, but user assignment remains a manual product operation until a
supported public API exists.

## Existing tables: keys, lookups and analysis

Start from the physical schema: database, schema, base table, columns, types,
nullability, primary key, identity/computed columns and approved connection
identity. A display name does not prove any of those identities. Keep generated
keys read-only. Decide row insertion separately from editability of an existing
column.

**New table grain.** For an employee master, decide whether a row denotes an
employee or an employee assignment; choose the stable key accordingly. Specify
required/default values and unique constraints.

**Lookup.** For `Employee.DepartmentID` referencing `Department.DepartmentID`,
store the key and display the requested label, e.g. `DepartmentName`. Require
compatible types and a unique target key. Repeated labels do not uniquely
identify rows. A lookup configuration is not a join and must not overwrite the
stored key. In each `lookupConfig` hop, `id` is the key column in the lookup
table and `linkingColumn` is the preceding table's column that holds it.
Preserve unrelated column metadata, editing and row actions.

```sh
python scripts/plan.py repair-powertable-config --baseline current-definition.json --input repair-request.json --out candidate
```

This produces a local candidate using supplied metadata. Compare the complete
candidate to the baseline and verify the change is confined to the intended
source/columns. A syntactically present connection ID does not prove access.

**Analyze across sheets.** Match facts to the unique master key at the fact
grain before aggregation. Count unmatched keys, nulls and duplicate masters;
a many-to-many match can multiply totals. Qualify currency and effective date
when comparing snapshots. If all you have is schema, report which joins and
checks are possible, not counts or conclusions about actual data.
