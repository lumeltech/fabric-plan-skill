# PowerTable Application Modeling

## Contents

- [Design sequence](#design-sequence)
- [Entity and relationship rules](#entity-and-relationship-rules)
- [Database column choices](#database-column-choices)
- [PowerTable column choices](#powertable-column-choices)
- [Advanced visual columns](#advanced-visual-columns)
- [Defaults, constraints, and audit fields](#defaults-constraints-and-audit-fields)
- [Preview contract](#preview-contract)

## Design sequence

1. Extract nouns with independent lifecycle or multiple records as candidate
   entities.
2. Remove candidates that are only fixed choices, labels, or duplicated
   attributes.
3. Identify ownership and cardinality: one-to-one, one-to-many, or many-to-many.
4. Choose stable keys, required fields, validation rules, and delete behavior.
5. Add derived PowerTable behavior only after the physical model is sound.
6. Keep the model within five application tables. If more are genuinely needed,
   split the use case into releases and preview the first boundary.

For an ambiguous detail, make the least-destructive reasonable assumption and
show it in the preview. Ask only when different answers would materially change
the tables, security, or destructive behavior.

## Entity and relationship rules

- Create a table when the concept has its own lifecycle, attributes,
  relationships, or multiple records.
- Keep simple statuses and categories as constrained values unless users must
  manage them as records with their own metadata.
- Put the foreign key on the child for one-to-many relationships.
- Use a junction table for many-to-many relationships. It must have its own
  identity primary key plus foreign keys to both parent tables, and normally a
  unique constraint over the two foreign keys.
- Use a self-referencing foreign key for hierarchies such as employee-manager or
  task-parent relationships.
- Prefer `NO ACTION` for deletes. Use `CASCADE` only when the child cannot exist
  independently and the preview calls out the consequence.
- Add an index for each frequently filtered foreign key.

## Database column choices

For every table created from scratch, use only these PowerTable-supported Fabric
SQL Database types:

| PowerTable storage category | Allowed SQL types |
|---|---|
| Text | `VARCHAR(n)`, `NVARCHAR(n)`, `CHAR(n)`, `TEXT`, `VARCHAR(MAX)`, `NVARCHAR(MAX)` |
| Number | `INT`, `BIGINT` |
| Decimal | `DECIMAL(p,s)`, `FLOAT` |
| Date/time | `DATE`, `DATETIME`, `DATETIME2`, `TIMESTAMP` |
| Boolean | `BIT` |

Do not choose aliases or adjacent SQL types such as `TINYINT`, `SMALLINT`,
`NUMERIC`, `REAL`, `MONEY`, `SMALLMONEY`, `TIME`, `NCHAR`,
`SMALLDATETIME`, `DATETIMEOFFSET`, or `UNIQUEIDENTIFIER` for a new PowerTable
source. In Fabric SQL Database, prefer `DATETIME2` for business timestamps;
SQL Server `TIMESTAMP` is a row-version value, not a business date/time.

| Business intent | SQL design | PowerTable input intent |
|---|---|---|
| Stable identifier | `INT` or `BIGINT IDENTITY` primary key | Number; usually hidden/read-only |
| Short text | `NVARCHAR(n)` sized to the domain | Text |
| Long text, notes, description | `NVARCHAR(MAX)` | Text displayed as long-form content |
| Whole quantity | `INT` or `BIGINT` | Number |
| Precise quantity | `DECIMAL(p,s)` | Decimal |
| Money | `DECIMAL(19,4)`, another justified `DECIMAL(p,s)`, or whole-unit `INT`/`BIGINT` | Currency with US Dollar selected |
| Ratio stored as fraction | `DECIMAL(p,s)` with `CHECK (value BETWEEN 0 AND 1)` | Percentage |
| Progress stored as whole percent | `INT` with `CHECK (value BETWEEN 0 AND 100)` | Percent complete |
| Date only | `DATE` | Date |
| Timestamp | `DATETIME2` | DateTime |
| True/false | `BIT` | Checkbox |
| Fixed single choice | `NVARCHAR(n)` plus `CHECK`, or a real lookup entity | Select |
| Email | `NVARCHAR(320)` | Email |
| URL | `NVARCHAR(2048)` | URL |
| Phone number | `NVARCHAR(32)` | Phone |
| File association | No guessed SQL binary column | Attachment visual column |

Do not use `FLOAT` for money. Every Currency column configuration must set
`columnMeta.currency` to `{"displayName":"US Dollar ($ - USD)","value":"USD"}`.
Do not store formatted currency symbols,
percent signs, comma-separated multi-select values, or duplicated lookup labels.

## PowerTable column choices

For every proposed column, record:

- physical SQL column and type, if any
- user-facing display name and description
- required or optional
- editable or read-only
- default value
- PowerTable type
- select options or checkbox values
- relationship, lookup, rollup, or formula source
- automation status: `automated` or `post-create`

Use these decisions:

| Need | PowerTable choice |
|---|---|
| Editable database value | Database column with the most specific supported input type |
| One related record selected by key | Single-select loaded from the referenced table |
| Read-only value displayed from a related record | Reference/lookup visual column |
| Multiple related records | Multi-select relationship plus junction table |
| Aggregate over child records | Rollup |
| Derivation from columns in the same record | Formula |
| One or more files | Attachment |

The current repository generator automatically persists database-backed
columns, checkbox mappings, dates, datetimes, time, number, decimal, currency,
rating, and scalar foreign-key selectors. Static select metadata is documented
by the Plan definition schema and may be added only with a schema-valid payload
and readback verification.

## Advanced visual columns

PowerTable supports Formula, Reference, Rollup, Multi-select relationship, and
Attachment columns. The public column-config schema allows extensible metadata
but does not define the complete metadata contract for every advanced type.

Therefore:

1. Always design these columns when the business requirement calls for them.
2. Show their exact semantic definition in the preview.
3. Mark them `automated` only when a verified payload pattern exists in the
   current repository or has been obtained from a saved definition.
4. Otherwise mark them `post-create`, create the underlying tables and base
   sheets, and report the remaining configuration plainly.
5. Never invent property names or claim readback success for configuration that
   was not present in the saved definition.

### Reference and lookup

- Store only the foreign key in the child table.
- Use the related table's stable key as the value and a concise human-readable
  column as the label.
- Display additional related attributes through read-only reference/lookup
  columns rather than copying them into the child table.

### Multi-select

- Use only for a real many-to-many relationship.
- Create a junction table with an identity column, both foreign keys, and a
  unique pair constraint.
- Define the primary table, lookup table, lookup key/label, relation table,
  relation-table reference key, and primary-table identifier in the preview.

### Rollup

Specify:

- current table and matching key
- linked table and matching key
- value column
- aggregation (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, earliest, or latest)
- optional filter
- behavior when no child record exists

### Formula

Specify:

- expression in business-readable form
- source columns
- output type and formatting
- null and divide-by-zero behavior
- whether it is visual-only or intentionally persisted

Prefer a visual formula for presentation calculations. Use a SQL computed
column only when the database must expose the value to other consumers and the
expression is valid and deterministic for the target SQL surface. The payload
generator marks computed columns read-only in the PowerTable.

## Defaults, constraints, and audit fields

- Use `SYSUTCDATETIME()` for UTC creation/update timestamps.
- Use explicit defaults only when the business meaning is stable, such as
  `IsActive = 1` or `Status = 'New'`.
- Pair fixed-choice defaults with a matching `CHECK` constraint.
- Apply `UNIQUE` to natural business identifiers such as employee number,
  product SKU, project code, or customer code when duplicates are invalid.
- Use positive/range checks for quantities, percentages, ratings, and monetary
  values where negative values are not meaningful.
- Include `CreatedAt` and `UpdatedAt` when auditability is useful. If
  `UpdatedAt` must track every update, include the update trigger in the preview.
- Do not add soft-delete, row-version, owner, or audit columns without a stated
  business or concurrency need.

## Preview contract

The preview must include:

1. Target workspace, database, schema, Plan name, and approved connection.
2. Assumptions and scope boundary.
3. One table section per entity:
   - description
   - columns with SQL type, nullability, default, and identity/computed status
   - primary key, unique constraints, checks, foreign keys, indexes, and delete
     behavior
4. Relationship summary with cardinality.
5. One sheet section per table:
   - unique sheet name and source table
   - each PowerTable column's type, display name, description, requiredness,
     options/default, source/expression, and automation status
6. Creation order and rollback/partial-failure behavior.
7. A single explicit question authorizing the exact staged SQL and Plan writes.
