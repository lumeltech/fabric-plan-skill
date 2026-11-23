# Visual-level filter registration in a chart definition

For local inspection or construction of supplied chart properties, distinguish `pivotAssignments` (fields) from `superFilterAssignments` (ordinary visible field cards). A card set to All has `filter: []` and null numeric bounds. An empty card list is not equivalent. Page/global filters and storage Context have separate purposes.

For each assigned field:

- Set `isDefault: true`, `position: "RIGHT"`, `filterLevel: "visual"`, and `configuration.hide: false`.
- Use the displayed field label (`customName`, then `name`, then `columnName`) for the configuration name.
- Copy the full current field assignment into the registration, including source/query identity, actual bucket, aggregation and type. Preserve large string IDs exactly.
- A numeric measure uses `isDefaultMeasure: true`, an advanced NUMERIC filter, `filterOperator: "between"`, and null min/max/equal defaults. `isDaxMeasure` is true for a PowerBI semantic Measure and false for an aggregated column or InfoBridge column.
- A grouping dimension has its own non-measure card. Text uses basic FACET configuration; a numeric dimension can use NUMERIC configuration while remaining `isDefaultMeasure: false`.
- Include the query ID in sort metadata for InfoBridge fields. The sort column ID must match the assignment ID.

A grouped measure filter contains the chart's grouping assignments followed by that one measure. These dimensions define its evaluation grain. Their presence inside a measure filter **does not** count as their own dimension filter cards, and does not authorize copying dimension selections into that measure filter. The inspected comparison-chart shape uses outer filter `bucketId: "AC"` for measure filters, while the nested measure retains its actual `AC` or comparison bucket such as `PY`. Grouping filters retain their own bucket such as `axis`.

Do not deduplicate only by field name or ID. The same field may be grouped and aggregated, or assigned in comparison buckets using different aggregations. Match source, query, field, bucket, role, column type and aggregation.

## Numeric measure shape

This compact excerpt illustrates the contract; use the complete constructor rather than sending the placeholder strings:

```json
{
  "id": "filter_<new-unique-id>",
  "pivotAssignments": ["<grouping assignments, if any>", "<full assigned measure>"],
  "isDefault": true,
  "isDefaultMeasure": true,
  "isDaxMeasure": false,
  "bucketId": "AC",
  "configuration": {
    "name": "Planned compensation",
    "hide": false,
    "filterMode": "advanced",
    "visualType": "NUMERIC",
    "filterOperator": "between",
    "alphaNumericValues": {"minValue": null, "maxValue": null, "equalValue": null}
  },
  "filter": [],
  "position": "RIGHT",
  "filterLevel": "visual"
}
```

`runtime.chart_filters.ensure_chart_filters(props)` constructs missing ordinary cards locally; `audit_chart_filters(props)` checks identity, role and evaluation grain. Preserve intentional restrictions on existing cards and custom filters. These helpers do not read a workspace or verify the rendered pane.
