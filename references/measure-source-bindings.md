# Measure source identity and typed assignment

Resolve the intended source from supplied model, sheet or query metadata before constructing a Planning assignment. A model measure on a Planning sheet is still a model measure.

## Business request to source contract

| Intended source | Required identity and type | Constructor |
| --- | --- | --- |
| Original Power BI DAX measure | Current model plus exact table-qualified field ID; sourceType PowerBI, columnType Measure; matching sourceId, tableName, columnName, dataType and semantic measureGuid | semantic_measure / resolve-measure-binding |
| Direct numeric Power BI column | Exact current field; sourceType PowerBI, columnType Column, dataRoleType Measure; source aggregation defaults to sum | semantic_value / semantic_measure / resolve-measure-binding |
| Input, Forecast or formula produced by a sheet | Current owner visual ID + source measureGuid; external key is SQL column record id or, for OneLake without id, measureGuid; source record type DataInput, Forecast or Formula, including VisualColumn wrapper; match visualState.manage_measures | resolve-measure-binding / registered_measure |
| From Queries / InfoBridge output | Current query registry ID (SQL sqlPk or opaque OneLake id) and selected post-transform output ID, alias and data type; sourceType InfoBridge and query-qualified id/sourceId | resolve-measure-binding with consumer_bindings |

Power BI display folders (for example a business folder called Mid-Market
Estimate) are not physical table identities. Read the actual model catalog and
preserve the table-qualified measure ID. Do not create a new ID from folder or
caption text. AC/PY/ameasure identify destination roles, not the source namespace.

For a comparison, resolve both sides independently. An estimate Forecast may be
From Sheets while the current forecast comparator is a DAX measure. Do not send
both through the same linking helper because they appear on the same source grid.
Conversely, a calculated USD estimate/forecast created as a sheet Formula remains
a sheet output; it must not be replaced by an unrelated DAX amount with a similar
name. Honor currency, period and grain in addition to identity.

## Executable construction

```text
python plan.py resolve-measure-binding --input binding-request.json --out assignment.json
```

The input is an object with `request` and optional `model`, `sheets`, `queries`.
PowerBI request: `{ "sourceType":"PowerBI", "fieldId":"Finance[Current Forecast]", "bucket":"PY" }`.
Use the current model metadata as `model`, not an invented field dictionary.
When this field is a numeric Column, the binding defaults to `aggregationType:
"sum"`. Supply request `aggregation` only for an explicit source override. This
does not change an explicit DAX Measure or the grid total settings.

Visual request: sourceType `Visual`, string `visualId`, `sourceMeasureGuid`,
optional `columnId`, and destination `bucket`. `sheets` contains the matching
owner's `name`, `visualId`, current `properties` and current `columns` records.
The helper requires the selected column's native type and source measureGuid to
match its owner registration. The returned destination measureGuid is distinct
from the source measureGuid; use `sheet_column_id` for the external column key.
Fabric SQL uses the current row id; OneLake uses measureGuid when id is absent/null.
Current owner-scoped OneLake records may also omit visualId. When present, it
must agree. Keep the runtime visual ID distinct from the portable definition GUID.

InfoBridge request: sourceType `InfoBridge`, `queryId`, `outputId`, a typed
`assignment` from the current query metadata, and destination `bucket`. `queries`
contains the current native records and selected output metadata. Use sqlPk only
when returned; OneLake records without it use their opaque id. The bundled
`find_query` resolves this exact domain without requiring a SQL property.
It reuses the query resolver and numeric type family contract. Input row IDs,
source-record IDs, old query IDs and output ordinals cannot replace output IDs.
Unknown source types or missing metadata are explicit construction dependencies.

Python callers selecting a registered Planning measure use
`registered_measure(properties, record, visual_id, sheet_name, model=...)`.
It follows a Native companion's exact upstream pivot assignment. For a local
Formula/Input/Forecast it builds a sheet link from the current source records.
`from_sheet_assignment` now rejects Native companions instead of silently making
an invalid link. Never bypass this guard by changing a measure's label or tag.

These constructors preserve lossless string IDs. In an existing Planning
consumer, changing its internal measureGuid can break formulas, formatting or
stored inputs: preserve it or perform an explicitly scoped migration. Rebinding
a chart does not authorize changes to Planning formulas or stored values.
