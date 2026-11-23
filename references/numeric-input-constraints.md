# Numeric input and Forecast bounds and distribution

## Average Leaf and parent distribution

An editable Data Input or Forecast measure can use `AverageLeaf` aggregation and
`distribute_parent_value_to_children:true` together. Do not restrict distribution
to Sum or automatically turn it off for rates/percentages. In the business spec,
default distribution on when either aggregation axis is AverageLeaf, unless the
user explicitly asks to disable it. An explicit `distribute:false` stays false.

For Data Input, write `measure_type.DataInput.column_type.Number` (also underneath
VisualColumn when applicable). For Forecast, write
`measure_type.Forecast.edit_config.number_column_metadata`. Keep both aggregation
axes, input eligibility, locks, bound context and identities intact. Distribution
is not a weighted allocation rule or a guarantee of any tested spread result.
Low-level `input_create` has no aggregation context: pass the selected Boolean
explicitly there. `distribution_default` is available to higher-level callers.

## Static min/max values are whole numbers

Do not author fractional static minimum or maximum values.

`max_value:{"Static":0.15}` is not a whole-number static bound. Do not round it or silently change the units. This restriction applies only to static min/max values, not to decimal defaults or formula results.

Choose a representation consistent with the business unit:

- For an existing fractional percentage input (0.03 means 3%), retain its IDs,
  stored data, percentage formatting and formulas. A hidden Formula measure
  returning `0.15` can supply `max_value:{"Measure":"<resolved native ID>"}`.
  Register that helper and its dependency; do not use its label as the ID.
- For a new input stored as percentage points, whole bounds 0 and 15 are possible.
  Formula consumers must divide by 100 and formatting must display 3 as 3%, not
  300%. Do not impose this representation on existing fractional stored values.

Example business spec fragments (actual IDs are resolved by the constructor):

```json
[
  {"key":"meritLimit","kind":"Formula","label":"Merit Maximum","formula":"0.15","visible":false,"aggregation":"Formula"},
  {"key":"merit","kind":"DataInput","label":"Merit Increase","aggregation":"AverageLeaf","distribute":true,"default_value":{"Static":0},"min_value":{"Static":0},"max_value":{"Measure":"meritLimit"}}
]
```
