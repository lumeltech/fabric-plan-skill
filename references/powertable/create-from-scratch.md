# Create a PowerTable Application from Scratch

Use this internal `fabric-plan-skill` mode when the business requirement needs new
Fabric SQL Database tables before PowerTable sheets can be created. Apply
[modeling.md](modeling.md) to the database design,
[column-mappings.md](column-mappings.md) to database-backed PowerTable columns,
and the confirmed payload generator in
[`resources/New-PowerTablePayload.ps1`](resources/New-PowerTablePayload.ps1).
For SQL catalog discovery and transactional DDL/DML, use the external
[`sqldb-cli` authoring guide](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli/references/authoring.md);
the companion is not bundled in this repository.

## Contents

- [Input collection](#input-collection)
- [Schema selection](#schema-selection)
- [Proposed-table review gate](#proposed-table-review-gate)
- [Discovery and collision checks](#discovery-and-collision-checks)
- [Connection confirmation](#connection-confirmation)
- [Model and preview](#model-and-preview)
- [Optional sample data](#optional-sample-data)
- [Final approval](#final-approval)
- [Create and verify SQL tables and sample data](#create-and-verify-sql-tables-and-sample-data)
- [Create and verify the Plan](#create-and-verify-the-plan)
- [Completion summary](#completion-summary)
- [Failure handling](#failure-handling)

## Input collection

Collect:

- business use case
- target workspace
- existing Fabric SQL Database
- Plan display name
- destination: workspace root (no folder) or an existing target-workspace folder

Do not ask the user to design the tables. Infer the model and disclose
assumptions. The user may replace the proposal with custom tables or ask to
fine-tune it through the review gate below.

If the user gives only a short request such as "Build a CRM PowerTable", ask for
the target coordinates and enough business scope to distinguish a minimal CRM
from a larger sales application. Do not ask about details that can be represented
as disclosed assumptions.

## Schema selection

Immediately after the SQL Database is selected, query all user schemas and
present them before modeling tables. Use a readable table:

| # | Schema | Existing tables | Default |
|---:|---|---:|---|
| 1 | dbo | `<count>` | Yes |
| 2 | `<schema>` | `<count>` | No |

Ask the user to select one target schema by name or serial number. Mark `dbo` as
the default and preselect it in the question, but do not treat silence, omission,
or the default marker as confirmation. If `dbo` does not exist, show the
available schemas without inventing it and ask for an explicit selection.

Use the confirmed schema for every newly designed table in this run. If the
user changes the database, list its schemas again and reconfirm.

## Proposed-table review gate

After schema selection, infer the smallest normalized model and present the
complete proposed table design before connection discovery, sample-data
planning, collision resolution, payload staging, or any write.

Start with a compact overview:

| # | Proposed table | Purpose | Primary key | Relationships |
|---:|---|---|---|---|
| 1 | `<schema>.<table>` | `<purpose>` | `<key>` | `<summary or none>` |

Then show one readable column table per proposed SQL table:

| Column | SQL type | Required | Default | Key / constraint | PowerTable behavior |
|---|---|:---:|---|---|---|
| `<column>` | `<type>` | Yes / No | `<value or —>` | `<details>` | `<input / lookup>` |

End with these explicit choices:

1. **Approve these tables** -- freeze the current tables, columns, relationships,
   and creation order and continue.
2. **Fine-tune the proposal** -- collect requested additions, removals, renames,
   type changes, constraints, or relationships.
3. **Provide custom tables** -- collect the user's table names, columns, keys,
   and relationships, then normalize and validate them.
4. **Cancel** -- make no changes.

Only **Approve these tables** passes this gate. A connection choice, sample-data
choice, general "continue", question, or partial acceptance is not table-model
approval. For fine-tuning or custom tables, regenerate and show the complete
overview and every complete column table again, then offer the same four
choices. Repeat without a retry limit until the user approves or cancels.

## Discovery and collision checks

1. List workspaces and resolve the exact workspace by name.
   Follow [creation destination](../../SKILL.md#powertable-creation-destination) to select
   workspace root or resolve an existing folder, including nested or ambiguous names.
2. List SQL Database items in that workspace and resolve the exact existing
   database.
3. Complete schema selection and the proposed-table review gate.
4. List existing tables and constraints through read-only catalog queries.
5. List Plan items and reject a colliding Plan display name.
6. Compare approved table names case-insensitively with existing tables.

If a proposed table already exists:

- do not alter or replace it
- show the collision
- offer a unique name or route the user to the existing-table `powertable-existing` flow

## Connection confirmation

List accessible connections, filter to `connectionDetails.type == FabricSql`,
and show the proposed connection details. Obtain explicit confirmation even
when exactly one candidate exists.

Connection confirmation authorizes only use of that connection. It does not
authorize table creation or Plan creation.

## Model and preview

After the proposed tables are approved, apply the modeling reference and
generate the exact staged implementation:

1. ordered `CREATE TABLE` design
2. key, constraint, index, trigger, and relationship design
3. sheet-to-table design
4. PowerTable column configuration blueprint
5. automation-status classification for advanced visual columns

Before showing the preview, verify that every proposed SQL column uses the
from-scratch allowlist in [modeling.md](modeling.md): text uses
`VARCHAR`/`NVARCHAR`/`CHAR`/`TEXT`, numbers use `INT`/`BIGINT`, precise values
use `DECIMAL`/`FLOAT`, date-time values use `DATE`/`DATETIME`/`DATETIME2`/
`TIMESTAMP`, and booleans use `BIT`. Replace unsupported aliases with the
closest allowed type rather than carrying them into the DDL. For example, use
`DECIMAL(19,4)` instead of `MONEY`, and still configure that column as Currency.

The complete preview must show the exact staged result, not a summary. Preserve
the approved table layouts and use a compact table per entity:

| Column | SQL type | Required | Default | Key/constraint | PowerTable type | Display/behavior | Automation |
|---|---|---|---|---|---|---|---|

Then show:

- target Plan workspace and workspace root or full destination folder path and ID
- primary, unique, check, and foreign-key constraints
- relationship cardinality and delete behavior
- indexes and update triggers
- sheet names and source tables
- reference/lookup mappings
- multi-select junction mappings
- rollup definitions and aggregations
- formula expressions and output formatting
- attachment behavior
- object creation order

Use collision-safe sheet names. Default each sheet to the singular table name
and suffix duplicates case-insensitively with ` (2)`, ` (3)`, and so on.

## Optional sample data

After the model is stable and before the final preview, offer one optional
sample-data choice unless the user already supplied it:

1. no sample data
2. show synthetic sample rows for reference only
3. insert synthetic sample rows with the new tables

Reference-only rows are preview content and never authorize DML. Show up to
five representative rows per table in a Markdown-style table and label them
clearly as examples that will not be inserted. Never present sample rows as a
comma-separated sentence or dense prose list.

When insertion is selected, ask:

> How many sample rows should be inserted per newly created table? Enter a whole
> number from 1 through 100.

- Accept only an integer from `1` through `100`; reject and re-ask for zero,
  negatives, decimals, non-numeric input, or values above `100`.
- Apply the approved count to every newly created table. Do not silently use a
  different count for parent, child, or junction tables.
- Generate synthetic, non-sensitive values that satisfy every unique, check,
  required-field, and foreign-key constraint.
- Insert parent rows before child and junction rows. Capture generated identity
  values rather than guessing them.
- Do not insert into pre-existing tables unless the user separately requests,
  previews, and approves that additional write.
- Include the exact per-table row counts and generated values in the final
  review. Show inline values in a separate readable table for each SQL table.
  For more than ten rows per table, show the first five inline and provide the
  complete generated row set as a reviewable artifact before approval.

## Final approval

After the table model is approved, the connection is approved, and the complete
tabular preview is visible, ask one unambiguous question:

> Create these SQL tables and then create this Plan with the listed PowerTable
> sheets?

When sample insertion was selected, include it in the same question:

> Create these SQL tables, insert the approved sample rows, and then create this
> Plan with the listed PowerTable sheets?

For a folder destination, add "and move it to <full folder path>" to the
approval question. A destination change requires a refreshed preview and approval.

Only an explicit affirmative answer authorizes the previewed writes, including
the folder move when selected. A correction,
question, silence, or connection approval is not final approval.

If the user changes the model, return to the proposed-table review gate,
regenerate every table layout, and require explicit table approval again before
connection or write approval.

## Create and verify SQL tables and sample data

1. Recheck that none of the proposed tables now exists.
2. Generate the DDL in dependency order.
3. Start one SQL transaction.
4. Create parent tables, child tables, junction tables, constraints, indexes,
   defaults, and approved triggers.
5. If sample insertion was approved, insert the exact previewed synthetic rows
   in dependency order within the same transaction.
6. Commit only when every DDL and approved DML statement succeeds; otherwise
   roll back.
7. Verify through read-only catalog queries:
   - tables and schemas
   - column names, SQL types, lengths, precision/scale, nullability, identity,
     defaults, and computed status
   - primary keys and unique constraints
   - check constraints
   - foreign keys and delete actions
   - expected indexes and triggers
   - exact per-table sample row counts when insertion was approved

Do not continue when verification differs from the approved preview.

## Create and verify the Plan

Use the verified created tables as inputs to the existing Plan payload
generator. Do not rediscover arbitrary tables or ask the user to select them:
the final preview already fixed the exact table set and order.

1. Generate one sheet per created table.
2. Apply database-backed input types and foreign-key selector mappings.
3. Set every Currency column's `columnMeta.currency` to US Dollar
   (`US Dollar ($ - USD)`, `USD`).
4. Apply only schema-valid advanced column overrides with a verified payload
   pattern.
5. Include every `post-create` column in the completion report; do not insert
   guessed metadata into the definition.
6. Create through `POST /v1/workspaces/{workspaceId}/plans`.
7. Accept `201`, or poll a `202` operation to completion.
8. After creation completes and the Plan ID is resolved, use
   [Move Item](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/move-item):
   `POST /v1/workspaces/{workspaceId}/items/{planId}/move` with body
   `{"targetFolderId":"<confirmed folder ID>"}`. Expect `200 OK`; honor
   `Retry-After` on `429`. Skip this call for workspace root.
9. Call [Get Plan](https://learn.microsoft.com/en-us/rest/api/fabric/plan/items/get-plan)
   at `GET /v1/workspaces/{workspaceId}/plans/{planId}` and verify top-level
   `folderId` equals the confirmed `targetFolderId`; for workspace root it must
   be absent or null. A failed read or mismatch means placement is unverified.
   This is an item property, not a definition part.
10. Call Get Plan Definition and verify:
   - Plan display name
   - sheet count and unique names
   - source database, schema, and table per sheet
   - required database-backed column types
   - `DEFAULT_LOCALE` on Date columns and `DEFAULT_LOCALE_TIME` on DateTime columns
   - US Dollar metadata on every Currency column
   - connection ID
   - saved advanced columns that were classified as automated

Every Fabric request, including polling and definition readback, uses the
`fabric-plan-skill` telemetry value.

### Completion summary

End the final reply with the completion summary defined in
[SKILL.md](../../SKILL.md#powertable-completion-summary), without waiting to be asked:

| Field | Value |
|---|---|
| Workspace name | Display name of the workspace that holds the Plan |
| Artifact name | Plan display name (`Plan`) |
| Report URL | `https://app.powerbi.com/groups/{workspaceId}/plans/{planId}` |

If readback differs or fails, label the artifact unverified but keep the
summary. After a SQL commit with no Plan, omit the URL and report the partial
state instead.

## Failure handling

Every failure response must identify the failed stage, exact known reason or
service error, current persisted/rolled-back state, corrective actions, and the
approval required before another write.

| Failure point | State to report | Corrective actions |
|---|---|---|
| Before final approval | No writes occurred | Correct the model, connection, sample-data choice, or preview and ask for approval again |
| SQL statement fails | The transaction rolled back; no approved tables or sample rows from this run remain | Name the failing statement/object and SQL error; correct collisions, types, constraints, permissions, or syntax, regenerate the full preview when behavior changes, and obtain fresh write approval |
| Sample-data insert fails before commit | DDL and DML rolled back together; no Plan was created | Report the violated constraint or insert error; correct the generated rows and obtain fresh write approval |
| SQL catalog or sample row-count verification fails after commit | **Partial state:** tables and committed sample rows exist but are not verified; no Plan should be created | Report exact catalog or count mismatches, perform read-only checks, and ask before any corrective DML, destructive cleanup, or ALTER; changed rows or schema need a new preview and approval |
| Plan create fails after SQL commit | **Partial state:** verified SQL tables and approved sample rows exist, but the Plan does not | Report created table names and the Plan error; offer Plan-only retry after correcting connection, permissions, folder/name collision, or payload, with read-only state checks and fresh Plan write approval |
| Plan create returns `202` but local polling/output fails | SQL is committed and Plan state is uncertain | List/read back the exact Plan before retrying; do not rerun DDL or issue a duplicate Plan create |
| Plan created but move failed or outcome is uncertain | **Partial state:** SQL tables and approved sample rows remain committed, and the Plan exists; requested placement is incomplete or unverified | Report Plan ID, URL, exact move error, intended folder, and actual `folderId` if known; retain SQL and the Plan, refresh folders and read properties, then obtain fresh approval for a move-only retry; never rerun DDL, recreate the Plan, or automatically clean up |
| Plan properties or definition readback differs or fails | SQL exists and the Plan exists but is unverified | Report Plan ID plus missing/different sheets, mappings, connection, formats, or expected versus actual `folderId`; retry read-only retrieval or obtain approval before corrective writes |
| Advanced visual column lacks verified payload metadata | Base tables and sheets may exist; the named advanced configuration remains incomplete | Report each `post-create` Formula, Rollup, Reference, Multi-select, Attachment, or manual-option Single Select and the manual configuration needed |

Never automatically drop committed tables after a Plan failure. Cleanup is a
new destructive operation and requires separate explicit approval. Never say
only "table creation failed" or "Plan creation failed"; include the reason,
state, and recovery choices.
