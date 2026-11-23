<!-- Read-only `fabric-plan-skill` mode: powertable-cross-analysis. -->

# Analyze Across PowerTable Sheets

Use this internal mode for questions requiring two or three PowerTable sheets:
comparisons, ratios, reconciliations, gaps, combined rankings, and aligned
trends. Sheets may belong to the same Plan or different Plans or workspaces.
Plan boundaries do not determine database boundaries. This mode is strictly
read-only: no SQL or Plan writes and no runtime files anywhere, including
temporary files. Keep definitions, query results, and relationship context in memory.

Read [single-sheet analysis](analyze-data.md),
[column mappings](column-mappings.md), and
[external `sqldb-cli` consumption guide](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli/references/consumption.md) end to end.
Inherit their mapping and query-safety rules, but this mode's narrower source,
endpoint, and no-file restrictions take precedence over broader SQL exploration
or script-export guidance. Every Fabric request, including definition polls
and result retrieval, carries `x-ms-fabric-skill: fabric-plan-skill`.

## Contents

- [Workflow](#workflow)
- [Failure reporting](#failure-reporting)
- [Must](#must)
- [Prefer](#prefer)
- [Avoid](#avoid)
- [Examples](#examples)

## Workflow

### 1. Bound the compared set

Collect the requested compared sheets before decoding definitions. At most
three compared sheets are allowed. If four or more are requested, stop before
decoding any definition and show the requested set in a numbered Markdown
table; ask the user to narrow it to two or three. Do not silently drop a sheet.
Sheets used only for display-name substitution do not count toward this limit.

`Which two or three PowerTable sheets should be compared? (select sheets / cancel)`

A single-sheet request belongs to `powertable-analysis`; announce that route
and follow [single-sheet analysis](analyze-data.md) instead.

### 2. Select and decode every compared sheet

For each sheet, follow [steps 1-4 of single-sheet analysis](analyze-data.md#discovery-and-confirmation-flow):
[workspace](analyze-data.md#1-select-a-workspace),
[Plan](analyze-data.md#2-select-a-plan),
[complete definition and sheet selection](analyze-data.md#3-read-the-complete-plan-definition-and-select-a-sheet),
and [selected-sheet inspection](analyze-data.md#4-inspect-the-complete-selected-sheet-definition).
Reuse a complete decoded Plan already obtained in this selection flow when
several selected sheets belong to it. Do not skip any sheet's inspection.
Use only documented Plan APIs and saved definition parts, never browser-session
or undocumented PowerTable CoreAPI routes.

Retain workspace and Plan names and IDs; sheet name and `recordGuid`;
`visualId`; `source.connectionId`, `source.dbHost`, `source.dbName`,
`source.meta.databaseId`, `source.meta.dbDisplayName`, source workspace,
`source.schemaName`, and `source.tableName`. Retain each sheet's full
display-to-SQL column mapping from `columnConfigs.json`, lookup configurations,
and filters or other saved behavior that may affect the question. Never assume
that a displayed column name is its SQL name. Preserve saved filters where
applicable and disclose any requested departure before approval.

Show all selected sheets in one numbered table, with each sheet's column
mapping in a Markdown table. Use database display names in user-facing tables;
keep physical hosts, physical database names, and connection details private
unless troubleshooting requires them.

| # | Workspace | Plan | Sheet | Database | Schema | Source table |
|---:|---|---|---|---|---|---|
| 1 | `<workspace>` | `<Plan>` | `<sheet>` | `<database display name>` | `<schema>` | `<table>` |

### 3. Determine source topology

Group sheets by physical database identity, `dbHost` plus `dbName`, not by Plan,
workspace, connection ID, or database display name alone. Confirm that these
saved coordinates identify the live Fabric SQL Database item before querying;
if inconsistent or unresolved, stop and clarify rather than guess.

| Case | Execution strategy |
|---|---|
| All compared sheets use one physical database, even across Plans or workspaces | Aggregate each source first, then combine in a single read-only SQL statement |
| Compared sheets use two or three physical databases | Query each database separately at the confirmed grain, then combine the small aggregated results in the session |

Show the selected strategy and sheet-to-database grouping as Markdown tables.
Never execute cross-database SQL, three-part source references, or queries
through a SQL analytics endpoint or another database as a workaround. Use each
confirmed Fabric SQL Database's own live endpoint and existing permissions.

### 4. Capture the analytical question

Before proposing relationships, collect the metrics, dimensions, filters,
period, and comparison the user needs. Reuse an already clear question rather
than asking again. Apply the [single-sheet clarification rules](analyze-data.md#translate-questions-to-t-sql)
when a metric, entity, column, date, unit, or relationship is ambiguous.
Resolve relative dates such as "this year" using the current date and state the
resolved period. The question determines which keys and time alignment matter.

Show unresolved alternatives in a numbered Markdown table, then ask:

`Which metric, dimensions, filters, and period should this comparison use? (specify / cancel)`

### 5. Propose candidate relationships

Compare only columns belonging to the selected sheets' own source tables.
Read declared constraints on those tables, but do not search other tables or
databases for candidate links. Propose relationships in descending trust:

| Priority | Candidate evidence | Required treatment |
|---:|---|---|
| 1 | Declared SQL foreign key between compared source tables in one physical database | Preserve declared column pairs and profile them |
| 2 | Shared PowerTable `optionLinking.lookupConfig` target | Compare configured schema, table, and key column, scoped to the target physical database |
| 3 | Same SQL column name and compatible SQL types | Suggest only; names do not prove a shared key domain |
| 4 | Same PowerTable display name | Resolve each SQL mapping and suggest only |
| 5 | User-specified column pairing | Validate it like any other candidate |

Matching lookup schema/table/key names in different databases do not establish
one shared lookup target. Every candidate, including declared foreign keys,
requires explicit confirmation. Support composite relationships only when the
user confirms every column pair; profile tuples, not each component in
isolation. For time alignment, propose the date column for each sheet and a
common day, month, quarter, or year grain. Time alignment is a relationship too.
Show all proposed pairs and their evidence in a Markdown table. If no suitable
candidate exists, ask for a pairing among the selected source columns or stop.

### 6. Profile proposed relationships

Before an analytical answer, use read-only aggregate profiling of the proposed
keys. Profiling may precede the combined confirmation gate; it does not
authorize executing the user's analytical question. Present counts and
diagnostics, not source detail rows.

| Check | Required evidence |
|---|---|
| Type and format | Live SQL types and lengths; counts exposing leading zeros, surrounding whitespace, case differences, or failed conversions |
| Cardinality | Total rows, distinct key or tuple counts, and duplicate-key counts per side; classify 1:1, 1:N, N:1, or N:M |
| Nulls | Null-key counts per side; for composites count a tuple as incomplete when any component is null |
| Overlap | Distinct normalized keys matched, only in A, and only in B; profile every proposed pair for three sheets |

If normalization is needed, show the exact proposed expressions in a table,
such as `TRY_CAST`, `LTRIM(RTRIM(...))`, or `UPPER(...)`, and ask before applying
them even in profiling. Check for conversion failures, meaningful leading-zero
loss, and multiple original keys collapsing to one normalized key. Do not
silently equate case-sensitive keys or discard failed conversions as nulls.

`Apply these normalization expressions for relationship profiling? (yes / adjust / cancel)`

Within one database, compute overlap using SQL set operations over distinct
keys. Across databases, the sole exception to aggregate-only profiling is
retrieving distinct approved normalized key values or composite tuples, with
no other source columns, for session-side comparison. Count first and retrieve
at most 10,000 distinct values or tuples per side. Exclude null or incomplete
keys from matched-key sets and report their counts separately.

If either side exceeds the cap, do not report overlap from truncated sets as
complete. Show the counts that were verified and label overlap unverified;
offer narrower filters or ask whether to proceed with that limitation:

`Overlap exceeds the 10,000-key limit. Continue with overlap unverified? (yes / narrow filters / cancel)`

Never bypass the cap with paging or raw-row exports. Carry any approved
limitation into the combined review and every affected join report.

| Verdict | Next step |
|---|---|
| Compatible | Show profiling results and request combined confirmation |
| Compatible with normalization | Show approved expressions and resulting profiling, then request combined confirmation |
| Not comparable | Stop that relationship, explain the reason, and ask for another pairing or cancellation |

Low overlap alone is not incompatibility. Show it and let the user decide.
Inability to read or profile a source is unresolved, not evidence of zero rows
or unmatched keys. Do not continue through an unvalidated relationship except
for the explicitly approved overlap-cap limitation.

### 7. Confirm sheets and relationships together

Show one combined review using the selected-sheet table from step 2 and these
Markdown tables; include all column mappings and profiling limitations.

| Setting | Reviewed value |
|---|---|
| Compared sheets | `<two or three confirmed selections>` |
| Question | `<metrics, dimensions, filters, and resolved period>` |
| Strategy | `<single-database statement or per-database aggregation combined in session>` |
| Grain | `<relationship keys and time grain; detail-preserving unique key if applicable>` |
| Time alignment | `<date column per sheet and day/month/quarter/year, or none>` |
| Join behavior | `<full outer by default for comparisons; otherwise stated inner or left>` |
| Unmatched keys | `<how missing sides and null keys will be reported>` |

| Relationship / column pairs | Evidence | SQL types | Approved normalization | Matched / only A / only B | Cardinality | Verdict / limitations |
|---|---|---|---|---|---|---|
| `<Sheet A.SQL column = Sheet B.SQL column; every composite pair>` | `<FK / shared lookup / SQL name / display name / user>` | `<types per side>` | `<expressions or none>` | `<counts or explicitly unverified>` | `<1:1 / 1:N / N:1 / N:M>` | `<compatible / compatible with normalization; limitations>` |

`Use these sheets and relationships for analysis? (yes / adjust relationships / choose other sheets / cancel)`

Do not run the analytical answer query without explicit approval. The original
comparison request, prior single-sheet source confirmation, normalization
approval, or approval of incomplete overlap is not this combined approval.
Adjustments return to the relevant selection, question, or profiling step and
require a refreshed review.

### 8. Offer display names after confirmation

Only after the question and relationships are confirmed, offer optional name
substitution when the result is keyed by IDs. If a key-only result has already
been shown, the same offer may follow it; never block analysis on optional
names or ask about them during initial selection.

`Replace these result keys with display names? (yes / keep keys)`

If requested, search in this order and stop widening once suitable candidates
are found. Every candidate must use the same physical database as the key's
sheet, even if a different Plan or workspace owns the candidate sheet.

| Order | Allowed name-source search |
|---:|---|
| 1 | Lookups configured on compared sheets: declared `lookupConfig` table, key, and `label` |
| 2 | Other PowerTable sheets within any of the compared sheets' Plans, with the key as the source table's primary key and a text column; inspect their saved definitions read-only |
| 3 | Catalog of the key sheet's physical database, same schema first; only if none is suitable, announce a widened search to its other schemas; prefer declared FK relationships to the key |

Do not visit other Plans, other databases, or Fabric-wide search. The catalog
expansion here is only for names, never for relationship discovery. Name-only
sheets are not compared sheets and do not consume the three-sheet allowance.

Validate key uniqueness and reject duplicate keys in a candidate name source.
Profile coverage over result keys under the same permissions and approved
normalization. A name source is not an implicit new analytical source: using
its metrics requires selecting it as a compared sheet within the cap and
repeating the relationship profiling and combined confirmation.

| # | Plan / configured lookup / catalog | Database | Schema.Table | Key | Text label | Unique key | Coverage |
|---:|---|---|---|---|---|---|---|
| 1 | `<source>` | `<database display name>` | `<schema.table>` | `<key>` | `<label>` | `<yes / rejected: duplicates>` | `<x of y keys have a non-null name>` |

`Use this display-name source? (select number / keep keys / cancel)`

Use only a confirmed, unique name source. Retain the original key alongside
names when needed to distinguish duplicate labels. Keys lacking a name remain
visible as unnamed; do not drop them with an inner join. If names are unavailable,
report that and continue with keys when the user chooses to do so.

### 9. Build and execute the analysis

Aggregate every sheet independently to the confirmed relationship and time
grain before combining. Within one database use read-only CTEs or derived
tables for the per-sheet aggregates, then combine those in one statement.
Across databases, query each source separately and combine only the small,
already-aggregated results in memory. Do not truncate per-database aggregates
or top-N lists before combining if doing so could change the answer; narrow the
question with the user if the required intermediate result is too large.

This mode also supports detail-level reconciliation when a confirmed unique
relationship grain preserves the requested details. Verify that uniqueness;
if it is not established, ask for a suitable grain rather than collapsing
detail rows arbitrarily. Never join detail rows across 1:N or N:M relationships
before aggregation. Non-additive metrics must use sufficient aggregates, such
as sum and count for a weighted average, not an average of averages.

Default comparisons to full outer combination so missing keys remain visible.
Use another join type only when the question clearly requires it; state and
confirm that behavior in the combined review. For three sheets, build a union
of confirmed keys/grains or an equivalent full-outer combination that preserves
unmatched keys from every side. Do not join the third sheet only to the first
sheet's key, losing keys present only in the second sheet. Do not invent a
shared key or align incomplete composite keys as matches.

Apply only approved normalization. Handle division by zero and nulls explicitly
in ratios, and distinguish missing data from a genuine zero. Push filtering,
grouping, aggregation, sorting, and ranking to SQL where semantically safe.
After combination, compute cross-source ratios and global rankings from the
complete approved intermediate results.

Inherit every [single-sheet query-safety rule](analyze-data.md#query-safety-and-efficiency):
only `SELECT` or read-only CTEs ending in `SELECT`; identifiers from confirmed
definitions and the live catalog; user filter values treated as values, never
SQL; respect RLS, column and connection permissions; required columns only,
never `SELECT *`; `TOP` for detail queries, default at most 100 returned rows.
Do not switch identity, endpoint, or database to bypass security or errors.
Execute queries without creating SQL scripts, temporary tables, exports, or
relationship files. Never fabricate a value from metadata or cached examples.

### 10. Present results and a join report

Return a Markdown result table or a concise metric for a single value. Include
filters and the resolved period where useful. Do not expose SQL unless asked;
approved normalization expressions in review tables are the exception.
If no rows match, identify the applied filters rather than inventing a result.

After every result, add a short join report in a Markdown table:

| Report | Value |
|---|---|
| Relationships | `<column pairs and approved normalization used>` |
| Matched / unmatched | `<distinct key counts per side, pairwise for three sheets; nulls and explicitly unverified overlap stated separately>` |
| Missing sides | `<how unmatched keys appear, including intentional exclusions for inner/left joins>` |
| Execution | `<one database statement or separate database aggregations combined in session>` |
| Display names | `<confirmed source and x of y coverage, or not used>` |

Across databases, disclose that the source queries ran separately and may
reflect different times; do not imply a shared snapshot. If changes during
execution prevent a reliable reconciliation, report that limitation rather
than claiming consistency.

Counts describe the filtered, normalized key sets used for this answer. Refresh
profiling counts when follow-up filters or periods change them; never reuse
stale overlap numbers or label capped overlap as exact.

### 11. Retain context and reuse safely

Keep confirmed sheets, mappings, relationships, normalization, time alignment,
join behavior, and name source as the active cross-analysis context. Natural
follow-ups reuse it without repeating discovery when these remain valid.
Adding, removing, or swapping a sheet, changing a relationship or normalization,
or requesting a key not yet validated restarts the relevant profiling and
confirmation gates. Changed metrics or periods that require different keys or
time alignment also require a refreshed review. One remaining compared sheet
routes back to `powertable-analysis` and its source-confirmation flow.

On request or at session end, print a compact relationship summary as a
Markdown table, never as a saved file. Include sheet workspace/Plan IDs,
`recordGuid` and `visualId`, database item IDs, schema/table mappings, every
column pair, normalization, time alignment, join behavior, and any name source
and profiling limitations. Omit secrets and physical infrastructure details.
A pasted summary is a proposed context, not proof: re-read current definitions
and catalog mappings, rerun step 6 profiling, and obtain step 7 confirmation
before using it. Revalidate and reconfirm a retained name source as well.

## Failure reporting

Follow the [single-sheet results and failure pattern](analyze-data.md#results).
Do not present a partial combination as a complete answer.

| Field | Required report |
|---|---|
| Failed stage | Selection, definition decode, topology, profiling, name-source lookup, query, or combination |
| Reason | Exact service/database error or observed mismatch, without secrets |
| Result state | Whether any result was returned; which source results are incomplete; no SQL or Plan writes occurred |
| Active context | Whether it remains valid and which gate must be repeated |
| Corrective actions | Safe read-only retry, narrower filters, corrected pairing/source, permissions correction, or cancellation |

An inaccessible source is not an empty source. Never combine only the successful
databases and silently omit a failed one. Name lookup failure may leave the
confirmed key-only analysis valid; disclose it and offer to keep the keys.

## Must

- Limit comparison to two or three sheets before definition decoding; exclude
  name-only sheets from the count and route one-sheet work to single analysis.
- Inspect every compared sheet's complete saved definition and source mapping.
- Capture the question before relationship discovery; restrict candidates to
  the compared source tables' own columns.
- Profile types, formats, overlap, cardinality, and nulls; require approval of
  exact normalization expressions and every composite or time-alignment pair.
- Confirm the combined sheet/source/relationship review before answer queries;
  profiling is permitted earlier only under step 6's read-only limits.
- Aggregate each sheet at the confirmed grain before combining; report
  unmatched keys and explicitly unverified overlap with every answer.
- Restrict name-source searches to the compared Plans and each key's own
  physical database, validate uniqueness and coverage, and confirm the choice.
- Preserve database security, telemetry, active context, and no-file behavior.

## Prefer

- Declared relationships over name similarities, without skipping profiling.
- One database statement when physical sources match, regardless of Plan owner.
- Full outer comparisons and concise result/join-report tables.
- Minimal, already-aggregated transfers when physical databases differ.

## Avoid

- SQL or Plan writes, undocumented CoreAPI calls, and local working-directory files.
- Cross-database SQL, SQL analytics endpoint workarounds, or permission bypasses.
- Assuming identically named keys or lookups share a domain across databases.
- Detail joins before aggregation, double counting, and averaging averages.
- Fabric-wide or other-database searches for linking columns or display names.
- Treating a comparison request, old source approval, or pasted summary as
  confirmed cross-sheet relationships.
- Dropping unnamed keys, hiding unmatched sides, or claiming complete overlap
  from capped key sets.

## Examples

| Request | Required behavior |
|---|---|
| "Compare returns and sales by territory." | Select both sheets, decode, show topology, propose TerritoryKey pairs, profile format/overlap/cardinality, confirm, aggregate each source per territory, and combine full outer. Only after confirmation, offer territory names from a configured lookup, a same-database sheet in either compared Plan, or the scoped catalog. |
| "Return rate by customer for this year." | Confirm customer pairs and date columns/grain, resolve the year, aggregate each source per customer for that period, and compute returns divided by sales with explicit zero/null handling. |
| "Which customers have returns but no sales?" | Validate and confirm the customer relationship, then return keys present only in returns, with matched/unmatched counts. |
| "Compare these four sheets." | Reject the four-sheet set before decoding any definition and ask the user to choose two or three. |
| "Analyze my Sales sheet." | Announce the single-sheet route and use powertable-analysis. |
| "Compare Sales in Plan A with Returns in Plan B." | Resolve both definitions independently; if their dbHost and dbName match, aggregate each source and combine in one read-only database statement. Different Plans do not require separate database queries. |