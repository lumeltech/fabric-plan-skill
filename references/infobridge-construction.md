> v39: Rows/Columns already define storage grain. External Context is only for additional stored selections, never ordinary page/global filtering. Connected Planning owners must match Context; query outputs must retain it. Read [storage-context.md](storage-context.md) for the bundled guards and build-time query evidence.

# InfoBridge: construction and consumption contracts

This supplement is limited to InfoBridge. It supersedes incomplete InfoBridge
construction advice in earlier bundled references; all other feature guides
remain applicable. The constructors and synthetic regression tests are bundled;
no reference report, tenant IDs, source checkout or recording is needed.

Definition fixtures and mocked metadata responses establish the bundled payload
contracts. They are distinct from calculation and refresh evidence. New constructor
payloads have offline tests; a successful read is not proof of an input-triggered
refresh.

## Start with the business flow and row grain

Treat InfoBridge as a **general sheet-data transformation and delivery utility**, not a fixed workforce-to-P&L feature. Given a source and a receiving sheet, reason about the required destination grain, fields, classifications, calculations and scope; compose the transformations that bridge the difference. Connected P&L is one worked example. The same principles apply to demand feeding capacity, quantities feeding cost, FX-enriched plans, conditional classifications, exception flags, regional rollups and combined forecast streams. These are application patterns using the operators, not claims that every imaginable transformation or API branch has been validated.

Use direct From Sheets/From Queries consumption when the existing output already fits. Use InfoBridge when data needs shaping, aggregation, enrichment, conditional calculation or combination before another sheet consumes it. Keep the transformation in InfoBridge when that satisfies the request; an external SQL table or writeback cycle is not inherently required.

Separate source storage, connection route, transformation and consumer. An employee-level salary plan can feed a region-level finance view without SQL writeback: Planning sheet -> InfoBridge source -> Pivot to Region x Month -> add account classification -> normalized contribution -> Append -> receiving Planning values. Editable FX/reference data can remain in PowerTable and enter InfoBridge as an EDITABLE source, then Join to the planning output. A PowerTable database lookup column is a different feature from this InfoBridge Join.

Choose the operation by intended result:

| Need | Operation | Meaning |
|---|---|---|
| Reduce Employee/Department detail to Region x Month | Pivot Table, step 50 | Select row/column roles and explicit measure aggregations; removing a dimension alone is not aggregation. |
| Calculate an amount, conditional label or other expression result | Add Measure, 130 | SQL-expression result, such as `"Adjusted Pay" - "Base Pay"` or CASE returning high/low text; the operation name does not force a numeric type. |
| Derive a classification or grouping | Add Dimension, 170 | SQL expression, including a constant or conditional CASE; single quotes are string literals. |
| Limit source rows to a region, scenario or slice | Filter Rows, 180 | Array of predicates with `Where`, subsequent `And` or `OR`. |
| Change a member value | Find/Replace, 200 | Change values in named columns; does not rename the column. |
| Align a column with a consumer dimension | Rename Column, 60 | Change the output field name/identity, such as Account -> AccountName. |
| Stack normalized workforce, expense, sales and cost contributions | APPEND source, step 140 | Stack rows. A later consumer may aggregate them; Append is not a lookup or automatic de-duplication. |
| Add corresponding quantities from multiple queries at the same grain | MERGE source, step 150 | Select matching measure names and sum their values at the matching grain. This is not a SQL Join. |
| Bring a region's FX rate alongside a planning amount | JOIN source, step 230 | Join on explicit keys. The demonstrated profile is LEFT_OUTER. |
| Express a more complex query over existing InfoBridge results | SQL_SOURCE, load step 10 | SQL text with `{{query_id:...}}` references; this is the InfoBridge query engine, not Fabric SQL DDL/writeback. |
| Drop unused measures/columns after normalization | Remove Columns, 310 | Projection only; does not perform a rollup. |

The sample Merge uses `finalsalary = "salary adj" * 2` and `* 4`. The video shows UK North values 10.98M + 21.96M = 32.94M. This is demonstration data, not a compensation policy. The sample Rename/Find-Replace maps Salary Expenses to Professional Services solely because that member exists in the demonstration model. Never adopt that account mapping as a real finance default.

## Portable graph envelope and complete query records

`connectedPlanning/infobridge.json` contains `$schema`, `sources`, `linkedQueries`, and `queryGroups`. A source owns its queries. The source's `sourceGuid` equals each owned query's `sourceId`. Each transformation has its owning `queryId`, ordered one-based `stepIndex`, `notes` (null when unused), and `meta:{type,name,description,value}`.

Keep these fields even when unused:

```json
{
  "queryId":"<fresh-query-identity>",
  "sourceId":"<owning-source-guid>",
  "name":"Workforce contribution",
  "type":"PLANNING",
  "visualId":"<owning-planning-visual-guid>",
  "meta":{},
  "transformationSteps":[],
  "writebackDestinations":[],
  "writebackSettings":null
}
```

This illustrates the envelope only; the constructor supplies real catalogs and steps. Both exports consistently contain an empty `writebackDestinations` array and null `writebackSettings` for queries without writeback. Do not replace null with `{}`. Missing arrays are a possible explanation for array-method import errors, not a proven root cause of an earlier `flatMap` failure. A new import/readback test is still needed to prove compatibility.

Source/query `meta` carries base arrays (`dimensions`, `columns`, `measures`, `dateColumns`, `hierarchyColumns`) and selected arrays (`selectedDimensions`, etc.). Base/source catalogs and final selected outputs are not interchangeable. Preserve existing metadata exactly on updates; do not copy cached row counts, parquet paths, status, job IDs, timestamps or user-specific outputs into a new graph.

Field IDs occupy several domains. Planning input measures can have string unsigned-64 `measureGuid` values; native source selectors can use small numeric IDs as strings; derived fields can have opaque hash IDs; consumer assignment IDs are qualified query-field references. Do not infer one from another. Date/hierarchy helper descriptors may omit `id` or `type`; do not manufacture identities to make every helper look like a measure. Constructors use explicitly typed, identified business fields; preserve auxiliary descriptors from the selected writer separately when required.

## Planning source and independent query branches

Use `planning_source` with the actual owner visual, model/workspace reference, explicit selected measure and scenario arrays, `honorSourceFilter`, and `isSkipTotals`. For generated Planning sources, supply current `owner_columns` or a complete typed catalog. The constructor enriches `includeMeasures` and all source measures with explicit `measureGuid`, `columnType` and `isHierarchyColumn:false`. Portable IDs and native source-selector IDs remain separate; see [Planning-source identity](infobridge-planning-identity.md) for the constructor contract and post-import reconciliation. Empty scenario selection is distinct from inventing a scenario default.

The video duplicates a base query to demonstrate separate transformations. Ordinary generation can construct multiple fresh query records sharing one Planning source. Replay the chosen steps with new query identity and current field IDs; copying the original report or transient jobs is unnecessary. Reusing the existing **source** does not mean referencing a sibling query's output. Add dependency edges only when a derived source really consumes another query.

The user clarified that the total rows shown in this recording are **preview-only**. Ignore them when learning the transferable query flow. Do not infer a consolidation defect, impose total-row removal, or change `isSkipTotals` from preview row counts or null-period display rows. Preserve the relevant source configuration; assess actual query grain and consumption separately from preview presentation.

## Transformation value contracts

### Pivot, Add and Filter

Pivot step 50 has `value:{sourceDimensions:[...],sourceColumns:[...],sourceMeasures:[...],removeColumns:[...],isValid:true}`. Select full field descriptors from the **preceding stage**. A measure descriptor carries its chosen `aggregationType` (the demonstrated branch uses `sum`). Keep order deliberate. Use one canonical dimension order before combining business contributions.

Add Measure 130 and Add Dimension 170 use `value:{columnName,formulaQuery,isValid:true}`. Quote column references with double quotes and literal members with single quotes. Examples:

```sql
"salary adj" - "Grid Salary Monthly Base Salary"
'Compensation'
CASE WHEN "PNLGroup" = 'Other Opex' THEN "Expense USD" ELSE 0 END
```

Filter Rows 180 uses an array, not an object:

```json
[
  {"condition":"Where","isValid":true,"operator":{"name":"is","value":"="},
   "sourceColumn":{"id":"Region[Name]","name":"RegionName","alias":"RegionName","type":"VARCHAR"},
   "value":"West"}
]
```

Some exported transform descriptors omit `dataType`; others contain `TEXT_COLUMN`, `NUMERIC`, `INTEGER` or even `string`. Compare the actual SQL `type`/logical family without erasing original metadata. Never assume a label implies a numeric field.

### General conditional SQL, not just arithmetic or constants

Both Add Measure and Add Dimension accept SQL expressions in `formulaQuery`, including conditional `CASE WHEN ... THEN ... ELSE ... END`. Compose conditions and expressions according to the business request; do not restrict Add Dimension to a literal account name or Add Measure to multiplication. The user's follow-up screenshots demonstrate **Add Measure returning text** with this formula and show the resulting `high` values:

```sql
CASE
  WHEN "salary adj" > 1000000 THEN 'high'
  ELSE 'low'
END
```

The example is synthetic business logic, not a copied tenant definition. The
million-unit threshold and labels are illustrative. This remains a type-130
operation even though its result is text. `Query.add(...,kind='measure',output_type='VARCHAR')`
constructs a provisional text-result catalog without a numeric SUM default.
Numeric expressions can use `output_type='DOUBLE'`. Reconcile execution types and
field IDs before consumption.

For a conditional dimension, a reusable example is:

```sql
CASE
  WHEN "RegionName" IN ('Canada East', 'Canada West') THEN 'Canada'
  ELSE 'Other markets'
END
```

For a numeric measure, use a CASE that returns compatible numeric branches and preserves missingness deliberately, for example `CASE WHEN "Amount" IS NULL THEN NULL WHEN "Amount" > 0 THEN "Amount" * 1.05 ELSE 0 END`. These are SQL expressions, not Planning-cell formula syntax or DAX. Use double quotes for field identifiers and single quotes for text values; escape literal quotes. Functions, casts, NULL handling and compound conditions should follow the actual query engine's supported syntax and be validated through query execution/output readback. Do not claim an arbitrary function works from its name alone.

Place the expression at the intended evaluation grain. Classifying each employee before aggregation and classifying total regional pay after Pivot answer different business questions. Likewise, applying a threshold or computing a ratio before versus after summation can change the outcome. Preserve condition dependencies through preceding steps; `requires` validates that referenced fields are available, but is not a SQL parser or engine-execution test. Chain Add, Filter, Rename, Find/Replace, Pivot, Append, Merge, Join and SQL source as needed, then deliver the resolved query output to the receiving sheet.

### Member replacement versus column rename

Find/Replace 200:

```json
{"columns":["RegionName"],"find":"West","replace":"West Combined",
 "flags":{"fullMatch":true,"matchCase":false,"useRegex":false},"isValid":true}
```

Rename 60:

```json
{"columnName":"AccountName","isValid":true,
 "sourceColumn":{"id":"<preceding-field-id>","name":"Account","alias":"Account","sourceType":"dimensions"}}
```

The observed renamed field has a different final output ID. The skill must reconcile the final catalog; changing the displayed alias while retaining every old downstream reference is insufficient. `Query.rename` requires a supplied construction identity and records the preceding field descriptor. Actual destination IDs still come from readback.

## Append: general union and strict P&L normalization

APPEND source and owned query metadata use `queries:["<upstream-Q-id>", ...]`. Initial step type is 140 with `{}` value. Create one `linkedQueries` edge per upstream, with its query ID, the **new dependent source GUID**, and upstream visual ID (null for sources without a visual). Keep graph references and metadata lists consistent.

An append can combine inputs with the same Account/Region/YearMonth dimensions
when only one has `variance`. Missing optional measures remain null. Use
`append_queries(...,allow_measure_union=True)` only when missing measures are
intentionally optional, and do not change them to zero silently.

For a finance consolidation, use the stricter `financial=True` path and
`contribution` factory. Normalize all branches to a deliberate common set of
dimensions, roles/order, types, period, scenario, currency and sign conventions.
Add missing business classifications, rename mismatched columns, aggregate away
excess detail with Pivot, then project the same additive metrics. Cast numeric
contributions consistently; do not treat a sample literal as a complete template.

A synthetic P&L pattern uses RegionName, ScenarioName, PNLGroup, AccountName and
YearMonth, with seven additive metrics: Plan Gross Revenue, Plan Net Revenue, Plan
COGS, Plan Compensation, Plan Other Opex, Plan Depreciation and Plan Units. Align
the requested dimension order explicitly.

Gross sales contribute Gross Revenue to both gross and net columns; a separate Discounts branch contributes `Net revenue USD - Gross revenue USD` to net only. Summing both yields net revenue without double-counting discounts. Additive consolidation formulas then calculate gross profit, total opex, EBITDA, operating income and signed amount. Adapt the metrics to the current business request; this is a recipe, not required field names for every application.

### Applying transformation building blocks to a finance flow

Compose the operators into a finance application in this order: load the relevant
Planning output, apply the business-scope filter, Pivot to the reporting grain,
add missing classifications, construct the common measure set, and remove
superseded source measures. Consolidation stacks contributions with Append and
adds financial formulas.

| Contribution | Detailed source grain | Pivot retained grain | P&L classifications | Nonzero contribution measures |
|---|---|---|---|---|
| Workforce | Region x Department x Employee x Scenario x Month | Region x Scenario x Month; SUM Compensation USD | Add PNLGroup = Compensation and AccountName = Compensation | Plan Compensation = Compensation USD |
| Operating expense | Region x PNLGroup x Account x Department x Scenario x Month | PNLGroup x Account x Region x Scenario x Month; SUM Expense USD | Already present: retain PNLGroup and AccountName; filter to Other Opex OR Depreciation | Plan Other Opex and Plan Depreciation use CASE on PNLGroup |
| Revenue | Region x Channel x Category x Product x Month, plus resolved Scenario context | Region x Scenario x Month; SUM quantity, gross and net amounts | Add Revenue / Gross Revenue | Plan Gross Revenue = Gross; Plan Net Revenue = Gross; Plan Units = Quantity |
| Supply cost | Region x Channel x Category x Product x Scenario x Month | Region x Scenario x Month; SUM Forecast COGS USD | Add Direct Cost / Cost of Goods Sold | Plan COGS = Forecast COGS USD |
| Revenue discounts | Same revenue source, independent branch | Region x Scenario x Month; SUM quantity, gross and net amounts | Add Revenue / Discounts | Plan Net Revenue = Net minus Gross |

Every branch emits all seven common measures; unrelated measures are intentional numeric zero contributions. Employee, Department, Product and Channel detail are absent from the final common grain. Account/PNLGroup **members can differ** across branches: Compensation and Cost of Goods Sold must remain different rows. What agrees is the dimension contract, type, reporting level, period/scenario interpretation and metric meaning, not identical member values or identical source field IDs. Expense already has finance classifications, so adding duplicate dimensions there would be wrong. Reorder its existing dimensions to the chosen canonical order when constructing a new normalized graph.

The consumer can group the stacked rows by semantic AccountName/PNLGroup and sum their measures. Append itself does not erase account rows. The consolidation's five additional measures are additive expressions over the common columns: gross profit, total opex, EBITDA, operating income and signed amount. Do not sum rates or percentages as financial contributions; calculate them at the appropriate business grain or from aggregated numerator/denominator.

Use this pattern as a compiler recipe, not as a fixed seven-column requirement: derive a contribution matrix from the requested financial lines, identify which branch supplies each metric, supply valid classification mappings, and explicitly decide each zero versus unknown. Build the full common catalog from that matrix before Append. `connected_components.contribution` provides an equivalent construction for additive expressions with explicit DOUBLE casts and a final common-grain Pivot; `Query` supports the recorded Pivot-first sequence. Nonlinear formulas must remain at their specified evaluation grain rather than being moved across aggregation mechanically.

## Merge: structured measure selection

MERGE metadata uses **objects**, unlike Append:

```json
{"queries":[
  {"id":"<first-query>","sourceMeasures":[{"id":"<actual-selector-id>","alias":"Pay","name":"Pay","aggregationType":"sum"}]},
  {"id":"<second-query>","sourceMeasures":[{"id":"<actual-selector-id>","alias":"Pay","name":"Pay","aggregationType":"sum"}]}
]}
```

Initial step 150 has `{}` value. Resolve each selection from that upstream query's current catalog; do not reuse one query's derived-field hash for another. Matching names do not make IDs identical. Runtime selectors and portable
Planning measure IDs occupy different identity domains. `merge_queries` preserves
supplied selector descriptors and checks names, order, numeric types and grain.

## Join and PowerTable reference data

JOIN metadata:

```json
{"joinType":"LEFT_OUTER","queries":[
  {"sourceId":"<base-query>","sourceName":"Amounts","joinColumnName":["RegionName"],"isBaseQuery":true},
  {"sourceId":"<lookup-query>","sourceName":"Rates","joinColumnName":["RegionName"]}
]}
```

Here `sourceId` means the referenced **query identity**, not the graph source GUID. Initial step 230 has `{}` value. Check key types and lookup uniqueness before joining; multiple lookup matches multiply rows and can inflate totals. LEFT_OUTER retains base rows; an unmatched rate should remain missing and be reported, not silently become 1 or 0. The demonstrated Join outputs both RegionName and RegionName_1; a subsequent Pivot removes the redundant lookup key. Confirm the complete grain before summing FX rates in a Pivot: rates are not additive business amounts. If there are several rows per region/date/currency, include those keys rather than joining only by region.

PowerTable source type is `EDITABLE`, not `PLANNING`, with source metadata:

```json
{"source":{"infoBridgeSourceType":220,"editable":{
  "mdeDestinationId":"<resolved-destination>","mdeSourceId":"<resolved-powertable-source>",
  "mdeSuperfilter":null,"mdeTableName":"Rates","mdeVisualId":"<resolved-powertable-visual>"
}}}
```

Its initial query uses load step 10. `editable_source` constructs this branch using real existing PowerTable identities; it does not initialize SQL storage or configure database lookup columns. Do not default its source/destination IDs equal merely because the sample uses the same value. Use prior bundled PowerTable initialization contracts if creation is needed.

Keep transient demonstrations distinct from persisted definitions. Do not invent
a saved calculation or file-source API contract that is not present in the current
authorized graph.

## SQL references, date inference and identity translation

SQL_SOURCE metadata contains `sql` and `queries`. Portable query tokens and
runtime query records occupy different identity domains. Build an explicit mapping
with `execution_map`, not array position or a guessed ID algorithm.

The same translation applies to scalar Append lists, Merge `queries[*].id`, and Join `queries[*].sourceId`. Update both source and query metadata when preparing the corresponding writer payload. `reconcile_meta`/`reconcile_graph_execution` touch only known reference slots and SQL tokens; they do not globally substitute GUIDs, change business literals, or rewrite labels. A native-execution view is not an ALM graph: structural owner/query/edge IDs must remain in their own domains. Re-export after import and rebuild consumer bindings from the actual final catalog.

SQL can infer YearMonth as DATE and expose generated Year, Quarter Name and Month Name columns. The source Planning query may have only text YearMonth. Never add `Year` to every Planning extraction because it appears in one SQL result. After every step, track exact field names, roles and types. `audit_step_columns` flags references unavailable in the current source snapshot; `Query.pivot` rejects unavailable columns during construction. Treat missing context in a snapshot as a readback question, not permission to invent a value.

A mixed-domain graph can contain portable query IDs and a different runtime token.
Treat it as a reconciliation task, not a universal SQL template. Resolve the
current external Context and source output before reconstructing branches, and
inherit only the requested business scope.

## Receiving Planning sheet and refresh acceptance

Use actual semantic master dimensions in the receiving sheet's Rows/Columns and query measures in Values. Match the output dimension names, members, data types and period/scenario context to the consumer. Rename Account -> AccountName when that is the actual consumer column, and map the account **member** separately. A field label match alone cannot prove a valid member mapping. Stable dimension-ID mapping, where configured, is separate from query GUID/field-ID reconciliation.

A saved query measure assignment uses `sourceType:"InfoBridge"`, `queryId`, `tableName`, `columnName`, qualified `id`/`sourceId`, `customSource:true`, and a destination `measureGuid`. Use `bridge_consumer` to create its Native input companion and registrations from the **resolved output catalog**. Do not assign InfoBridge output dimensions as substitutes for semantic master dimensions. Check that old field IDs are removed from all consumer assignments after a rename/reimport.

Build topologically. Save source Planning inputs, refresh/materialize sources and
dependent queries through the authorized external adapter, inspect job completion,
and verify final catalogs and values. Include cross-sheet Planning dependencies
that are not represented by an InfoBridge linked-edge graph.

Use existing bundled API adapters for inventory, metadata, transformations, query reload, targeted notification polling and source Parquet. Successful ALM LRO completion is not connected-worker completion. Verify actual output grain, duplicate business keys, unmatched lookup keys, period/scenario scope, missing-value policy and arithmetic. Ignore preview-only total rows. For a salary delta, compare source compensation, its finance contribution and operating-income delta at the same scope; restore authorized test inputs. A manual reload test does not prove automatic propagation. If the tenant cannot initialize one graph module, report that module and retain independent supported application work.

Read current inventory, query metadata and transformations only through the
organization-approved external service profile. Route templates and credentials
are intentionally not bundled. For public Plan exports, use the documented
`getDefinition` transport and its bounded polling contract. Metadata reads do not
reload queries or modify planning values.

## Bundled callable path

1. Resolve current source model/owner/input identities and select real fields. Construct a source with `planning_source` or `editable_source`.
2. Construct each query with `Query` or `construct_query`. For multiple branches use fresh query identities against the same source. Use `requires` for formula dependencies and exact stage fields for Pivot/filter/rename.
3. Construct the derived source with `append_queries`, `merge_queries`, `join_queries` or `sql_source`, supplying the planned complete output catalog. Output construction IDs are not assumed to be native execution/consumer identities.
4. Add returned dependency edges, assemble with `portable`, and validate references/cycles. Apply financial normalization or explicit optional-measure-union policy as appropriate.
5. Use the existing codec/ALM API deployment path with a fresh complete baseline, preserving unrelated part bytes. Run source/query initialization/readback and reconcile actual identities/catalogs. No unsupported native source-create endpoint is fabricated by these factories.
6. Bind consumers using actual readback fields, verify refresh/data behavior and record any unverified stage.

CLI: `python plan.py construct-bridge {query|planning-source|append|merge|join|sql|editable-source} --input agent-built-spec.json --out constructed.json`. The agent builds these specs from the business request and discovered metadata; the user does not hand-edit payloads. The Python constructors are the same functions used by the CLI. These adapters are callable component phases; the general `provision` convenience command is not a universal compiler for every graph.

Run `python plan.py test`. The new tests cover optional-measure Append, strict financial append, structured Merge selection, left Join keys/fanout, PowerTable source type, SQL token parity, native/portable identities, Rename versus replacement, optional descriptor dataType, writeback defaults, dependency cycles, and per-stage Year availability. Missing unrelated features remain feature-level coverage entries, not application-wide vetoes.
