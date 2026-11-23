# Planning fields, inputs and storage grain

For a model value, resolve the qualified field in the supplied catalog.
Bind a DAX measure as a Measure. Bind a numeric column intended for Values as
a Column with a Measure role; do not turn an integer key into a metric just
because it is numeric. `sourceAggregation` selects how the model aggregates
the column (Sum by default). Grid `aggregation` and `columnAggregation` are
separate: a monthly rate can have no time total without changing its source.

For a sheet-produced input, forecast or formula use the **source owner's**
identity and registered measure, not a matching caption. A model measure on a
sheet remains a model measure. For a transformed query use its query and output
IDs, not input column IDs or ordinals. If those facts aren't in the supplied
metadata, stop rather than invent a binding.

```sh
python plan.py resolve-measure-binding --input binding-request.json --out assignment.json
```

For example, a model binding request contains `model` plus
`"request":{"sourceType":"PowerBI","fieldId":"Metrics[BasePay]","bucket":"ameasure"}`.
Construction only resolves the supplied records; it does not fetch data.

Define each input's unit, type, default, storage key and eligibility. Preserve
the difference between blank and a deliberate zero. For percentages agree on
the stored fraction versus displayed percentage before setting bounds. A
positive eligibility expression controls whether a cell allows input, not who
has access. Repeated per-period commentary needs a period key; a one-time note
at entity grain should not acquire a different identity for each visible month.

For a shared assumption, anchor it at the dimensions where it is decided.
Do not copy an amount pool into every child; an allocation needs an explicit
weight and a rule for zero or missing total weight. Do not sum rates as if
they were amounts. An anchor can hide repeated display at lower levels without
removing the value from leaf formulas. The dimension hash uses **all** ordered
pivot dimensions; selected anchor dimensions describe only the decision grain.
Prefer stable leaf keys over display labels. Skipping an ancestor in storage
requires evidence that the leaf determines it; changing keys is a migration,
not a presentation change.
