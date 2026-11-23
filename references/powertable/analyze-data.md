# Analyze PowerTable Data

Use this internal `fabric-plan-skill` mode when the user asks a natural-language
question about data shown in an existing PowerTable sheet. This mode is
strictly read-only. Read
[external `sqldb-cli` consumption guide](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli/references/consumption.md) end to end
before executing the first T-SQL query.

## Supported source

This workflow supports a PowerTable visual backed by a Fabric SQL Database
table. The saved Plan definition and the connected SQL Database are the two
sources of truth:

- the Plan definition identifies the sheet, visual, SQL source, display-to-SQL
  column mappings, lookups, filters, grouping, sorting, and other PowerTable
  behavior
- the confirmed SQL Database supplies the actual values

Never answer a data question from metadata, sample rows, prior answers, or
model knowledge. Never use the undocumented
`/CoreAPI/v2/powertable/sources/config/data/` route. Use the documented Plan
item APIs and the saved definition.

## Discovery and confirmation flow

Follow this sequence without skipping a selection or confirmation.

### 1. Select a workspace

List every workspace available to the current identity using the documented
Fabric workspace API. Show a numbered table:

| # | Workspace | ID |
|---:|---|---|
| 1 | `<display name>` | `<workspace id>` |

Ask the user to select one workspace. Even when exactly one is returned, show
it and obtain confirmation rather than silently selecting it.

If the user supplied a workspace name, still list and exact-filter the
available workspaces. Do not guess an ID or treat a partial match as selection.

### 2. Select a Plan

List Plans in the confirmed workspace:

```http
GET /v1/workspaces/{workspaceId}/plans
```

Handle pagination. Show a numbered table containing Plan display name and ID,
then wait for an explicit selection. If no Plan exists, report that no
PowerTable analysis source is available in that workspace and make no SQL call.

### 3. Read the complete Plan definition and select a sheet

Call:

```http
POST /v1/workspaces/{workspaceId}/plans/{planId}/getDefinition
```

Send `{}` when a body is required. Accept inline `200`, or for `202` poll the
returned `Location` or `Operation-Location` until terminal and then GET its
`/result`. Include `x-ms-fabric-skill: fabric-plan-skill` on the initial call, every
poll, and the result request.

Decode every `InlineBase64` part before interpreting the Plan. Read
`definition.json` first and list only sheets whose `sheetType` is
`POWERTABLE`. For each sheet, retain its:

- `displayName`
- sheet `recordGuid`
- PowerTable visual `visualId`
- hidden state

Show a numbered table and ask the user to select one sheet. Do not choose a
sheet because its name resembles the question.

### 4. Inspect the complete selected-sheet definition

For the selected sheet and PowerTable visual, decode and inspect all matching
parts, including:

```text
sheets/{sheetId}/sheet.json
sheets/{sheetId}/visuals/{visualId}/columnConfigs.json
sheets/{sheetId}/visuals/{visualId}/properties.json
sheets/{sheetId}/visuals/{visualId}/source.json
sheets/{sheetId}/visuals/{visualId}/sourceSettings.json
```

Also retain Plan-level filters, variables, and configuration from
`planProperties.json`, `definition.json`, and other decoded parts when they can
affect the selected sheet.

From `source.json`, resolve:

- `source.meta.workspaceName` and `workspaceId`
- `source.meta.dbDisplayName` and `databaseId`
- `source.dbHost` and physical `dbName`
- `source.schemaName`
- `source.tableName`
- `source.connectionId` and connection name

Do not display the physical host, physical database name, connection secret, or
other infrastructure details unless troubleshooting requires them.

From `columnConfigs.json`, build a mapping table:

| PowerTable column | SQL source column | SQL type | PowerTable type | Behavior |
|---|---|---|---|---|
| `<displayName>` | `<columnName>` | `<columnMeta.dbMeta.type>` | `<columnType>` | `<lookup, formula, hidden, read-only, or direct>` |

For a lookup, retain the `optionLinking.lookupConfig` schema, table, ID,
linking column, and label. A lookup table is part of the sheet model, but
disclose it before any query that joins it.

For a formula, calculated, rollup, reference, or other derived column:

1. use a source column when the definition identifies one
2. translate it to T-SQL only when the complete deterministic expression is
   available
3. otherwise calculate it after a bounded source query only when that is safe
   and efficient
4. if neither is possible, explain that the selected source cannot answer the
   question

Never assume `displayName` equals `columnName`.

### 5. Confirm the source

Before the first data query, show:

```text
Workspace : <workspace>
Plan      : <Plan display name>
Sheet     : <PowerTable sheet>
Database  : <database display name>
Schema    : <schema>
Table     : <table>
Columns   : <count and concise display-to-source summary>
Lookups   : <referenced lookup tables, or none>
```

State that the complete definition, source settings, and column mappings were
reviewed. End with:

`Use this PowerTable source for analysis? (yes / choose another sheet / cancel)`

Do not execute the user's pending data question until the user explicitly
confirms this source. A request to analyze data is not source approval.

## Active analysis context

After confirmation, retain the selected workspace, Plan, sheet, source, and
column mappings as the active context. Natural follow-up questions reuse it
without repeating discovery or confirmation.

Restart the complete selection and source-confirmation flow when:

- the user asks to use another sheet, Plan, workspace, or source
- the selected source becomes unavailable
- the question needs data outside the confirmed table and disclosed lookup
  model
- conversation state no longer contains the confirmed mapping

## Translate questions to T-SQL

Before executing a query:

1. identify the requested metric, dimensions, filters, grouping, ordering,
   ranking, limit, comparison, and time period
2. map every PowerTable display column to its SQL source column
3. verify every source column still exists in the confirmed schema and table
4. resolve ambiguity before querying
5. construct a read-only T-SQL statement
6. execute it through the external `sqldb-cli` consumption workflow against the live SQL Database
   endpoint so database security policies remain authoritative

Ask for clarification when:

- "top" does not identify a metric or entity
- several display columns match the same business term
- several date columns could define a period
- a unit such as lakh, million, percentage, or currency is unclear
- the requested relationship is not present in the confirmed source model

Use the current date for relative periods such as "this year", and state the
resolved period in the result.

## Query safety and efficiency

- Execute only `SELECT` statements or read-only CTEs ending in `SELECT`.
- Refuse `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `TRUNCATE`, `EXEC`, and all
  DDL, even if the current identity has permission.
- Use schema, table, and column identifiers only from the confirmed definition
  and live catalog; delimit them as T-SQL identifiers.
- Treat user-provided filter values as values, never identifiers or executable
  SQL.
- Respect RLS, column permissions, connection permissions, and all database
  errors. Never switch identity or source to bypass them.
- Push filters, joins, grouping, aggregation, sorting, and ranking to SQL.
- Select only required columns; never use `SELECT *`.
- Apply `TOP` to detail queries. Default to at most 100 rows unless the user
  requests a smaller limit; summarize when a larger result would be unwieldy.
- Use window functions for top-N-per-group and ranking.
- Use explicit null handling when it changes the result.
- Prefer aggregate results over transferring raw rows to the assistant.

Do not silently join an unrelated table. A lookup target declared by the
selected sheet may be joined after it is disclosed; any other table requires
an explanation and explicit user confirmation of the expanded source.

## Results

Present tabular results as a Markdown table and single values as a concise
metric. State the mapped PowerTable column, filters, and resolved date period
when useful. Do not expose SQL unless the user asks for it.

If no rows match, say so and identify the applied filter. If the query fails,
report:

- failed stage
- database error without secrets
- whether no result was returned
- whether the active source remains valid
- safe corrective actions

Never estimate, infer, or fabricate a database result.

## Must

- Discover and explicitly confirm workspace, Plan, sheet, and SQL source.
- Decode the complete saved definition before confirming the source.
- Map PowerTable display columns to SQL columns before query generation.
- Query the confirmed database for every factual data answer.
- Keep all SQL read-only and preserve the confirmed source for follow-ups.
- Restart confirmation when the source changes.

## Prefer

- SQL-side aggregation, filtering, sorting, and ranking.
- Concise result tables with a short explanation of the calculation.
- Live OLTP reads when security policy enforcement or freshest values matter.

## Avoid

- Undocumented PowerTable CoreAPI routes or browser-session APIs.
- Selecting a source from the wording of the analytical question.
- Answering from metadata, cached values, examples, or prior outputs.
- Querying undisclosed tables or exposing internal connection configuration.

## Examples

| Request | Required behavior |
|---|---|
| "Analyze employee salaries in my PowerTable." | List workspaces, Plans, and PowerTable sheets; inspect the selected definition; show the source and mappings; wait for confirmation. |
| "Show the top 3 highest-paid employees in each department." | After source confirmation, map employee, salary, and department columns and execute a read-only `ROW_NUMBER()` query partitioned by department. |
| "How many orders are in each status?" | Map the displayed status column to SQL, execute `COUNT(*)` grouped by that source column, and present the result. |
| "Show sales this year." | Clarify which sales metric and date column when either is ambiguous; otherwise state the resolved year and query it. |
| "Use another sheet." | Discard the active source and restart sheet selection and confirmation. |
