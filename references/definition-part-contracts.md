# Plan definition part contracts

Use this guide to read or review the feature parts of a PlanV1 definition:
Planning writeback, inserted rows, scenarios and row templates; PowerTable
columns, source, settings, approvals, automations and forms; Intelligence
properties; InfoBridge; and cube configuration. Requirements come from the
published part schemas, codes from the Plan definition article, and export
behavior from the published structure manifest.

These parts configure behavior. Saving them does not run a writeback, approve a
row, submit a form, run an automation or execute a query.

## Contents

- [What this package builds and what it only preserves](#what-this-package-builds-and-what-it-only-preserves)
- [Planning parts](#planning-parts)
- [PowerTable parts](#powertable-parts)
- [Intelligence properties](#intelligence-properties)
- [InfoBridge](#infobridge)
- [Cube](#cube)
- [Published schemas and the structure manifest](#published-schemas-and-the-structure-manifest)
- [Primary sources](#primary-sources)

## What this package builds and what it only preserves

The bundled runtime constructs Planning inputs and properties, PowerTable
columns, source, settings, forms and automations, and InfoBridge sources. It
validates native cube settings and keeps saved cube bindings on inputs. Three
commands add new feature records to a fresh export and keep every other part
byte for byte:

```bash
python scripts/plan.py planning-features --baseline current-definition.json --input planning-features.request.json --out candidate
python scripts/plan.py powertable-features --baseline current-definition.json --input features.request.json --out candidate
python scripts/plan.py cube-part --baseline current-definition.json --input cube.request.json --out candidate
```

`planning-features` adds `writeback.json`, inserted rows, scenarios and row
templates to one Planning visual; `powertable-features` adds an approval
workflow beside forms and automations; `cube-part` appends to `cube/cube.json`.
Product values have no defaults, so each request states them all: the writeback
layout, scenario status and first order, approval rule type, persist flag and
filter orders, cube measure type, and the five row-template flags. Adding a
default is a product decision for the user, not an inference from the schemas.

`planning-features` takes `sheet_guid`, an optional `visual_id`, and any of:

- `writeback`: `writeback_type`, `destinations` (each as Fabric exports it), and
  optional `column_mapping` (measure GUID to column name), `excluded_measures`,
  `skipped_dimensions` and `number_precision`. Fabric exports a `writeback.json`
  for every Planning visual, and the constructor refuses an existing one, so it
  applies only to a definition without one, such as a newly built Planning sheet.
- `insert_rows`: a list with `name`, `dimension_id` (a row dimension of the
  visual), `row_type` (`StaticRow` or `CalculatedRow`), a `formula` for each
  calculated row, and optional `description`, `include_in_total` and
  `column_aggregation`.
- `scenarios`: a list with `name`, `measure_ids` (measure GUIDs of the visual),
  `status` and `order`. Once the part has scenarios, an omitted `order` becomes
  the highest order plus one. The current Fabric Plan import neither reads nor
  exports `scenarios.json`, so the command warns that these scenarios have no
  effect after publishing.
- `row_templates`: a list with `title`, `no_row_id` (the text written for a
  missing parent or previous row) and ordered `rows`, each with `title`,
  `include_in_total`, `disabled`, `distribute_parent_value_to_child`,
  `default_value` and `row_edit_mode`.

`powertable-features` takes `sheet_guid` and `approvals` with `rule_type`,
`persist_flag`, `levels` (`name`, `description`), and optional
`multi_level_enabled` (Boolean) and `filters` (`name`, `filter`, `order`). A
`LOOKUP` rule also needs `lookup_config` (`tableName`, `approverColumn` and a
`conditionalColumn` list of `columnName`/`lookupColumnName` pairs), copied as
given. `cube-part` takes any of `partitions` (`name`, `dimensions`,
`time_dimensions`, `measures`), `measures` (`name`, `type`, `config`),
`measure_mappings` (`partition`, `measure`) and `input_mappings` (`measure`,
`sheet_guid`, `measure_guid`, optional `visual_id` and `partition`). Names link
new records to new or exported ones.

The constructors append and never rebuild. They refuse an existing
`writeback.json` or `approvals.json`, and records already in `insertRows.json`,
`scenarios.json`, `modelTemplate.json` or `cube/cube.json` keep their content and
`$schema` value. Any other change to an exported feature part is a scoped patch
of that part, reviewed against the contract below, never a rebuild from a
smaller hand-written object.

The constructors do not compute a writeback `settingsHash`, a scenario
`dimensionHash`, simulations or numeric cube service IDs. The approval record's
`approvalLevel` is the number of levels, which is how Fabric's own workflow API
stores it: multi-level approval finishes only at that level. They do not position
inserted rows, nest template rows, author `ForecastRow` or
`PercentContributionRow` rows, or assign approver users.

## Planning parts

**Writeback (`writeback.json`).** The article requires `writebackType` and
`destinations`; the published schema requires only `$schema` and
`writebackType`. Layout codes are `PIVOT_LONG` 2, `PIVOT_WIDE` 3, `DELTA_ONLY` 4
and `DELTA_WIDE` 5. Fabric exports each destination with `tableName`, a
`settings` object and `connectionId` or `connectionIdVariable`; `settingsHash`
can be empty. The import never reads the schema's portable `connection`, and a
destination without `settings` (the article's `connectionId`/`databaseId`
example) fails import on Fabric SQL-backed Plans. On those Plans the import keeps
`tableName` only when `settings.database` is set; otherwise it keeps the existing
table name or creates one. The constructor accepts only the exported form,
copied as given, and reports `schema-conflict` when `settingsHash` or
`connectionId` is absent. Keep measure-to-column mappings, exclusions, filters,
auto and snapshot writeback, scenario IDs, debounce, precision, string length and
skipped dimensions.

**Inserted rows (`insertRows.json`).** The part wraps `rows`. Each row requires
`id`, `visualId`, `rowMeta`, `name` and `dimensionId`; `rowMeta` requires `id`,
`row_type` and `title`. Row types are `StaticRow`, `CalculatedRow`,
`ForecastRow` and `PercentContributionRow`. Keep hierarchy, order, totals,
formulas and bindings.

**Scenarios (`scenarios.json`).** The part wraps `scenarios`. Each scenario
requires `name`, `status` (`ACTIVE` or `LOCK`) and `meta` with `measureIds`,
`scenarioGuid` and `order`. `autoWritebackEnabled` is `ACTIVE` or `INACTIVE`.
Keep simulation payloads and dimension hashes. The current import ignores this
part, and export doesn't write it.

**Row templates (`modelTemplate.json`).** The part wraps
`properties.dynamicRowTemplates`. Each template requires `id`, `title` and
`rows`. Each template row requires `id`, `title`, `row_type`,
`include_in_total`, `parent_id`, `level`, `previous_row_id` and `disabled`, and
its `row_type.StaticRow` requires `distribute_parent_value_to_child`,
`default_value.Static` and `row_edit_mode`. Template rows are not inserted-row
records; do not move one into the other.

## PowerTable parts

**Columns (`columnConfigs.json`).** The article describes a root array. The
published schema defines an object with a `columnConfigs` array, which is the
shape this package writes. Keep the shape of the export in hand. Each entry
requires `columnGuid`, `columnName`, `columnType`, `columnMeta` and
`displayName`; edit, mandatory and hidden flags are `0` or `1`. `columnType`
codes are `TEXT` 1, `SINGLE_SELECT` 2, `MULTI_SELECT` 3, `DATE` 4, `NUMBER` 6,
`PERSON` 7, `TIME` 8, `LAST_UPDATED_BY` 9, `LAST_UPDATED_AT` 10, `CHECKBOX` 11,
`DATETIME` 12, `DECIMAL` 13, `IMAGE` 14, `URL` 15, `EMAIL` 16, `FORMULA` 17,
`BUTTON_COLUMN` 18, `CURRENCY` 19, `PHONE_NUMBER` 20, `RATING` 21, `ATTACHMENT`
22, `PERCENT_SLIDER` 23, `PERCENT` 24, `JSON_KEYS_ONLY` 26 and
`JSON_STRICT_SCHEMA` 27. The visual column type is a separate code set: `BASE` 1,
`DISPLAY` 2, `SINGLE_SELECT` 3, `MULTI_SELECT` 4, `REFERENCE_COLUMN` 5, `FORMULA`
6, `ALTER_TABLE` 7, `RELATION_COLUMN` 8, `BUTTON_COLUMN` 9, `ATTACHMENT` 10 and
`ROLLUP` 11. Column and table names may use Unicode letters, digits, spaces,
underscores, brackets and hyphens, start with a letter, and stay within 128
characters.

**Source (`source.json`).** The article lists `connection`, `database`,
database `schema` and `tableName`. The published schema requires only `$schema`
and also defines a `source` object; this package reads the source record
identity from `source.recordGuid`. Keep whichever members the export has.

**Settings (`sourceSettings.json`).** The article wraps a `settings` array; the
published schema also defines `sourceSettings`. Fabric's import reads
`sourceSettings` or a bare array: a `settings` wrapper imports nothing and raises
no error, so this package writes and reads `sourceSettings`. Setting names are
`ROW_ADD`, `ROW_UPDATE`, `ROW_DELETE`, `ROW_IDENTIFIER`, `VISUAL_LAYOUT`,
`COMMENT_SETTINGS` and `SCD`. Row access is all users, specific users or rule
based, stored as `filterType` 1, 2 or 3. Never broaden row access by default.

**Approvals (`approvals.json`).** The article requires `ruleType`: `DEFAULT` 10,
`MANUAL` 20 or `LOOKUP` 30. `persistFlag` is `SAVE_AFTER_REVIEW` 10 or
`SAVE_BEFORE_REVIEW` 20. Approval levels require `name`, `description` and
`level`; routing filters require `name`, `filter` and `order`. Assigning
approver users has no public route. The article lists these members at the top
level. Fabric's import reads them from one nested `approvals` record or from the
top level, and its export writes the nested record, which the constructor
follows: `ruleType`, `persistFlag`, `approvalLevel` (the number of levels),
optional `multiLevelEnabled`, both lists and, for `LOOKUP`,
`settings.lookupConfig`. No public source shows the nesting, so the command
warns about it; confirm the workflow in the product after publishing.
`multiLevelEnabled` is written only when the request states
`multi_level_enabled`; it is never inferred from the number of levels. The
PowerTable UI offers only `SAVE_AFTER_REVIEW`; the backend also accepts 20.

**Automations (`automations.json`).** An object with an `automations` array.
Each automation requires `name`, `triggerType` and `config`. Trigger codes are
`ROW_CREATED` 1, `ROW_UPDATED` 2, `ROW_DELETED` 3, `RECORD_MATCHES_CONDITION` 4,
`SCHEDULED` 5, `FORM_SUBMITTED` 6 and `BUTTON_CLICKED` 7. `config` requires
`name`, `trigger`, `entryGroupId` and `groups`; each group requires `groupId`,
`groupType`, `entryActionId` and `actions`, and each action requires
`actionId`, `actionType` and `config`. Keep the links between groups and actions.
Current Fabric also has a webhook action (`TRIGGER_WEBHOOK` 15); this package
builds only create-record, update-record, mail and Teams actions.

**Forms (`forms.json`).** The article describes a root array; the published
schema wraps a `forms` array, which is the shape this package writes. Each form
requires `title` and `layoutMeta` with `children` and `type: "form"`. The
product's layouts are `default` and `tabs`, and its layout elements are `form`,
`field`, `group`, `tabItem` and `rowGroup`. The article's `sections` layout and
`section`/`tab` elements don't appear in the product. New forms show the logo
and allow multiple entries, as the product does.

## Intelligence properties

Intelligence `properties.json` requires `$schema`, a page `properties` object
(`schema` plus the page settings in `properties`) and a `visuals` array. Each
visual requires `id`, `visualType` and `properties`, which hold `schema` and the
visual configuration in `properties`. Entity variables require `id`, `label`,
`type` (`action`, `number`, `text`, `dropdown`, `date` or `slider`), `scope`
(`entity`, `visual` or `page`) and `technicalName`. Some exported values hold a
JSON object as a string; keep wrappers and strings as exported. The structure
manifest notes that exported visual `properties.json` files match none of the
public properties schemas, so schema conformance is not a repair target.

## InfoBridge

`connectedPlanning/infobridge.json` requires a `sources` array. The article and
the published schema require at least one source, but the structure manifest
records exports with an empty array, so keep an exported empty array rather
than inventing a source. Each source requires `name` and `type`. Source codes are
`PLANNING` 10, `APPEND` 20, `MERGE` 30, `CSV` 40, `JSON` 50, `XLSX` 60,
`PARQUET` 70, `JOIN` 80, `ENCRYPTED_PARQUET` 170, `EDITABLE` 220 and
`SQL_SOURCE` 230. Join queries use Inner 10, Left Outer 20, Right Outer 30 and
Full Outer 40.

A query requires `name`. A join reference requires `sourceName` and a non-empty
`joinColumnName` list, plus `queryId` or `sourceId`. A transformation step
requires `stepIndex` and `meta` with `type` and `name`; do not invent
transformation type codes. A query group requires `name` and `queryIds`. A
writeback destination requires `tableName` and one connection form: `connection`
with `database`, `connectionId` with `databaseId`, or `dmtsConnectionId` with
`databaseId`.

## Cube

`cube/cube.json` requires four arrays: `cubePartitions`,
`cubePartitionMeasures`, `cubePartitionMeasureMappings` and
`cubePartitionMeasureDataInputColumnMappings`. A partition requires
`recordGuid`, `name`, `dimensions`, `timeDimensions`, `measures` and `rowCount`.
Its dimensions require `id`, `label`, `type` and `dataType`, and its measures
add `isNative` and `aggregationType`. A partition measure requires `recordGuid`,
`name`, `config` and `type` (`FORECAST`, `NUMBER` or `FORMULA`). Both mapping
kinds require `recordGuid`. Keep the reference form an export uses, and never
invent numeric service IDs; new records reference partitions and measures by
`recordGuid` in the `_RefId` members. The published schema types a measure
config's `data_type` and `dataType` as a `oneOf` of the enum `Number` or `Text`
and any text, so both documented values match twice and fail. The schema
report marks that as a reviewed deviation rather than a conflict.

## Published schemas and the structure manifest

Schemas are published under
https://github.com/microsoft/json-schemas/tree/main/fabric/item/plan/definition.
The `$schema` URI inside each part is its version marker. GitHub paths are
case-sensitive and differ in casing from several `$schema` URIs, so treat a
path and a URI as two spellings of one schema, not as two versions.

| Contract | Path under the schema folder |
|---|---|
| Root definition | `Definition/1.0.0/schema.json` |
| Plan properties | `PlanProperties/1.0.0/schema.json` |
| Sheet | `Sheets/Sheet/1.0.0/schema.json` |
| Sheet comments | `Sheets/CommentSettings/1.0.0/schema.json` |
| Planning inputs | `Planning/DataInput/1.0.0/schema.json` |
| Planning properties | `Planning/Properties/1.0.0/schema.json` |
| Writeback | `Planning/Writeback/1.0.0/schema.json` |
| Inserted rows | `Planning/InsertRows/1.0.0/schema.json` |
| Scenarios | `Planning/Scenarios/1.0.0/schema.json` |
| Row templates | `Planning/modelTemplate/1.0.0/schema.json` |
| PowerTable columns | `PowerTable/ColumnConfigs/1.0.0/schema.json` |
| PowerTable properties | `PowerTable/Properties/1.0.0/schema.json` |
| PowerTable source | `PowerTable/Source/1.0.0/schema.json` |
| PowerTable settings | `PowerTable/Settings/1.0.0/schema.json` |
| PowerTable approvals | `PowerTable/Approvals/1.0.0/schema.json` |
| PowerTable automations | `PowerTable/Automations/1.0.0/schema.json` |
| PowerTable forms | `PowerTable/Forms/1.0.0/schema.json` |
| Intelligence properties | `Intelligence/Properties/1.0.0/schema.json` |
| InfoBridge | `ConnectedPlanning/Infobridge/1.0.0/schema.json` |
| Cube | `cube/1.0.0/schema.json` |
| Structure manifest | `definitionStructure/1.0.0/definitionStructure.json` |

The structure manifest describes one exported structure and records where
exports differ from the public schemas: root, Plan-properties and data-input
parts carry extra fields; sheet parts omit some notes members; visual
properties match no public properties schema; writeback parts lack a required
destination member; and InfoBridge exports can have no sources. Read those
differences as reasons to preserve exported content, not as defects to repair.

This package checks candidates against its pinned copies in the `schemas`
folder, recorded by URL and SHA-256 in that folder's manifest. Refreshing them is
a separate, reviewed change. The Scenarios and ModelTemplate schemas are not
pinned, so new records in those parts pass only the constructors' own checks and
the schema report marks the parts `schema-gap`. The Scenarios `$schema` value is
all lower case (`planning/scenarios`), unlike its GitHub path.

## Primary sources

- Plan definition article:
  https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/plan-definition
- Published schemas and the structure manifest:
  https://github.com/microsoft/json-schemas/tree/main/fabric/item/plan/definition
