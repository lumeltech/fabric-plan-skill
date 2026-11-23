# PowerTable SQL Column Mappings

Use this reference with the Plan PowerTable authoring workflow. Create one PowerTable column configuration per source SQL column in ordinal order.

## Contents

- [Mapping table](#mapping-table)
- [New-table SQL type allowlist](#new-table-sql-type-allowlist)
- [Foreign-key lookups](#foreign-key-lookups)
- [Single-select values](#single-select-values)
- [Checkbox values](#checkbox-values)
- [Shared column rules](#shared-column-rules)
- [Must](#must)
- [Prefer](#prefer)
- [Avoid](#avoid)

## Mapping table

| SQL category | `columnType` | `visualColumnType` | Required metadata |
|---|---:|---:|---|
| scalar foreign key | `2` | `3` | `selectionMethod: LOAD_FROM_DATABASE` and one `optionLinking.lookupConfig` entry |
| `date` | `4` (`DATE`) | `1` | `format: DEFAULT_LOCALE`, empty `min` and `max` |
| `datetime`, `datetime2`, `datetimeoffset`, `smalldatetime` | `12` (`DATETIME`) | `1` | `format: DEFAULT_LOCALE_TIME`, empty `min` and `max` |
| `time` | `8` (`TIME`) | `1` | `format: DEFAULT_LOCALE`, empty `min` and `max` |
| explicit closed character category | `2` (`SINGLE_SELECT`) | `3` | `selectionMethod: DISTINCT_VALUES`, empty `options`; declare the column in `singleSelectColumns` |
| populated non-FK `bit`/boolean, integer-family, or character-family column with one recognized boolean value or a recognized boolean pair | `11` (`CHECKBOX`) | `1` | source-typed `checkedValue` and `unCheckedValue`; infer the missing counterpart only for a recognized single value |
| empty-table `bit` or boolean alias | `11` (`CHECKBOX`) | `1` | `checkedValue: 1`, `unCheckedValue: 0` |
| `decimal`, `numeric`, `float`, `real`, double alias without monetary intent | `13` (`DECIMAL`) | `1` | SQL `precision` and `scale` in `dbMeta`, `noOfDecimals` from SQL scale, empty bounds/prefix/suffix |
| `money`, `smallmoney` from an existing source | `19` (`CURRENCY`) | `1` | SQL precision/scale, `noOfDecimals`, and `currency: {"displayName":"US Dollar ($ - USD)","value":"USD"}` |
| integer or decimal-family column with strong monetary intent in its name | `19` (`CURRENCY`) | `1` | normalized names ending in a token such as `amount`, `price`, `cost`, `salary`, `fee`, `budget`, or `balance`; SQL precision/scale and US Dollar `currency` metadata |
| integer with strong rating intent in its name | `21` (`RATING`) | `1` | normalized names ending in `rating`, `star`, or `stars`, plus explicit forms such as `rating_value`; SQL precision/scale preserved without inventing a rating range |
| other `tinyint`, `smallint`, `int`, `bigint` | `6` (`NUMBER`) | `1` | SQL precision/scale preserved; empty bounds/prefix/suffix |
| other/string | `1` | `1` | text metadata, no inferred choices |

## New-table SQL type allowlist

When `fabric-plan-skill` designs tables from scratch, choose only:

```text
TEXT:     varchar, nvarchar, char, text, varchar(max), nvarchar(max)
NUMBER:   int, bigint
DECIMAL:  decimal, float
DATETIME: date, datetime, datetime2, timestamp
BIT:      bit
```

This is a DDL restriction for newly designed PowerTable sources. Do not create
new columns with `money`, `smallmoney`, `numeric`, `real`, `tinyint`,
`smallint`, `time`, `nchar`, `smalldatetime`, `datetimeoffset`, or other SQL
types. Use the closest allowed storage type and then choose the best PowerTable
input. For example, store Salary as `INT`, `BIGINT`, or `DECIMAL(p,s)` and map
it to Currency.

Every Currency column must include:

```json
{
  "currency": {
    "displayName": "US Dollar ($ - USD)",
    "value": "USD"
  }
}
```

The object belongs directly in `columnMeta`.

## Foreign-key lookups

Foreign-key mapping takes precedence over the underlying SQL type. For a scalar foreign key, set:

```json
{
  "columnType": 2,
  "visualColumnType": 3,
  "columnMeta": {
    "selectionMethod": "LOAD_FROM_DATABASE",
    "options": [],
    "optionLinking": {
      "filters": [],
      "lookupConfig": [
        {
          "schema": "<referenced schema>",
          "table": "<referenced table>",
          "id": "<referenced key column>",
          "label": "<chosen display column>",
          "linkingColumn": "<referenced key column>",
          "order": 0
        }
      ]
    }
  }
}
```

The local PowerTable column remains the source foreign-key column. `id` and `linkingColumn` name the referenced key column. Use a human-readable display name without a trailing `_key`.

## Single-select values

Use `DISTINCT_VALUES` single-select only when a declared constraint or explicit
user choice establishes a closed character category. Add the exact column name
to its table selection:

```json
{
  "schemaName": "dbo",
  "tableName": "CustomerOrder",
  "singleSelectColumns": ["OrderType"]
}
```

The generated column uses `columnType: 2`, `visualColumnType: 3`, empty
`options`, and `selectionMethod: DISTINCT_VALUES`. Do not infer single-select
from the current row values alone.

Keep the shared dropdown metadata even when no lookup is configured:

```json
{
  "selectionMethod": "DISTINCT_VALUES",
  "options": [],
  "optionLinking": {
    "filters": [],
    "lookupConfig": []
  }
}
```

These fields belong in `columnMeta`. Do not omit `optionLinking` or replace
its arrays with `null`. Successful creation alone does not prove dropdown
usability; open the saved sheet and expand the dropdown during validation.

`DISTINCT_VALUES` builds its dropdown only from values already stored in the
column; it does not read CHECK-constraint domains. Declare a column in
`singleSelectColumns` only when the existing rows already contain every
allowed value. For a CHECK-constrained category on a newly created table, or
any table where allowed values are missing from the data, keep the column as
editable text and report manual (`STATIC`) options as `post-create` work; do
not invent option objects. The generator keeps a declared column as text and
lists it in `postCreateSingleSelectColumns` when the table is empty.

## Checkbox values

For a populated table, inspect every non-foreign-key `bit`/boolean,
integer-family, and character-family column. A column is a checkbox candidate
only when it has one recognized boolean value or a recognized boolean pair.
Character discovery must use binary collation so values such as `Y` and `y`
remain separate.

For two observed values, automatically resolve these semantic pairs while preserving each exact source value and its type:

| Checked semantic | Unchecked semantic | Example preserved mapping |
|---|---|---|
| `true` | `false` | `True` / `FALSE` |
| `yes` | `no` | `YES` / `No` |
| `y` | `n` | `y` / `N` |
| `1` | `0` | numeric `1` / `0`, or string `"1"` / `"0"` for character columns |

Pair recognition is case-insensitive only for deciding which value is positive. Distinct-value detection, source validation, and emitted strings are case-sensitive. Never normalize the values written to `checkedValue` or `unCheckedValue`.

When only one recognized value is present, infer the missing member of its pair. Preserve numeric versus string type. For text, mirror a standard observed casing style: `true` produces `false`, `True` produces `False`, and `TRUE` produces `FALSE`; the same rule applies to `yes/no` and `y/n`. If a single text value uses irregular mixed casing or is not a recognized boolean token, retain its normal non-checkbox mapping rather than inventing a counterpart. A single populated `bit`/boolean value must resolve to `1/0`.

Any other exact two-value pair remains its normal text or numeric mapping. If
it is a declared closed category such as `DineIn`/`Takeaway`, configure it with
`singleSelectColumns`; never turn it into a checkbox.

For an empty table, map only SQL `bit`/boolean columns to checkbox and use numeric checked `1` and unchecked `0`. Do not infer checkbox intent for empty integer or character columns.

`unCheckedValue` is case-sensitive in the canonical saved definition. `NULL`
cannot be a checkbox value. A populated `bit`/boolean column must have one
recognized value or a recognized pair; otherwise stop for source correction.
A non-bit candidate with unrecognized values retains its normal mapping.

## Shared column rules

- Identity columns are read-only.
- SQL computed columns, generated-always (temporal period) columns, and `TIMESTAMP`/`rowversion` columns are read-only (`allowEdit: 0`) and never mandatory, because SQL Server generates their values and rejects explicit writes.
- Other non-nullable columns are mandatory.
- Primary-key columns are marked as primary keys.
- Preserve SQL metadata in `dbMeta` where the canonical column shape supports it.
- Set Date `columnMeta.format` to `DEFAULT_LOCALE` and DateTime
  `columnMeta.format` to `DEFAULT_LOCALE_TIME`.
- Set `columnMeta.currency` to US Dollar for every `CURRENCY` column.
- Apply mapping precedence in this order: scalar foreign key, explicit distinct-values single-select, populated recognized boolean checkbox, then integer currency/rating/number intent or text fallback.
- Normalize snake_case, camelCase, PascalCase, spaces, and punctuation before evaluating integer column-name intent. Require a complete intent token; do not match arbitrary substrings.
- Do not infer distinct-value selectors from names or current row values. Use `DISTINCT_VALUES` only when a declared constraint or explicit user choice establishes a closed category.
- Do not infer semantic string types such as email, URL, phone, person, image, attachment, or rating from a column name. SQL string storage does not establish those PowerTable semantics, so keep such columns as text unless the user explicitly supplies a mapping.

## Must

- Preserve source column order and SQL precision and scale.
- Use only the documented SQL type allowlist when designing a new source table.
- Persist `{"displayName":"US Dollar ($ - USD)","value":"USD"}` in
  `columnMeta.currency` for every Currency input.
- Give scalar foreign-key mappings precedence over checkbox and numeric mappings; give a valid populated checkbox precedence over integer intent and text fallback.
- Require one recognized boolean value or a recognized case-sensitive non-null source pair for every populated checkbox.
- Preserve numeric-versus-string type, exact casing for observed values, and the documented matching casing for an inferred counterpart.
- Keep unrecognized two-value pairs as text/number, or use explicit `singleSelectColumns` for a declared closed category.
- Infer a missing counterpart only from a recognized single boolean value, preserving source type and standard text casing.
- For empty tables, use checkbox only for bit/boolean columns with numeric checked `1` and unchecked `0`.

## Prefer

- Conservative full-token matching for integer currency and rating intent.
- Empty bounds, prefixes, and suffixes when no explicit source constraint establishes them.

## Avoid

- Inventing validation ranges, defaults, enum choices, lookup labels, or composite-lookup behavior.
- Treating `NULL` as an unchecked value.
- Converting an unrecognized two-value pair into a checkbox.
- Treating empty integer or character columns as checkboxes.
