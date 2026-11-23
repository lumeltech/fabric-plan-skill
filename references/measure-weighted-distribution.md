# Planning distribution using another measure

Choose a measure-weighted rule when a planner distributes an amount in proportion to a separate measure, not equally or using the target’s own values. The local constructor supports Column and Row/CurrentYear profiles.

The Planning sheet's `visualState.data_input_rules` contains
`rule_type.Distribute.operation.Row`, `apply_to_dimensions: "All"`, and:

```json
{"MeasureIdWithReference":{"measure":{"Measure":"<weight measure ID>"},"weights_from":{"Period":"CurrentYear"}}}
```

The selected target remains `measures.SelectedMeasures`. Outer `rows` and
`columns` are `"All"` in this capture. CurrentYear selects the **weight basis**;
it does not express the destination period, eligibility, locks or scenario.

Resolve the target and weighting measure on the same Planning owner. Use `measure_weighted_rule(..., axis="Row", weights_period="CurrentYear")` for the row profile.

## Column distribution: confirmed UI-to-JSON mapping

| UI choice | Persisted member |
|---|---|
| Rule Type: Distribution Rule | `rule_type.Distribute` |
| Apply Distribution Rule to: Columns | `operation.Column` |
| Apply to Dimensions: All Dimensions | `apply_to_dimensions: "All"` |
| Use Reference From: Measure | `reference.MeasureIdWithReference` |
| Choose Measure: the budget measure | `measure: {"Measure": "<current weight measure ID>"}` |
| Weights from Row: Use Self | No source-row member in this configuration |
| Apply to Measures: selected input measure | `measures.SelectedMeasures` with target IDs |
| Unrestricted outer row/column selectors | `rows: "All"`, `columns: "All"` |

`Use Self` here concerns the source **row**. It does not replace the selected
weighting measure with `SelfMeasure` or change the reference to `SelfWeight`.

Choose Column or Row according to the requested behavior, not the layout.

```python
from runtime.rule_factories import measure_weighted_rule
payload = measure_weighted_rule(
    logical_id=logical_rule_id, name="Allocate using budget weights",
    target_measures=["target"], weight_measure="budget", measure_ids=owner_ids,
    axis="Column", rows="All", columns="All")
```

The lower-level helper is `distribute_columns_by_measure(measure_id)`, accepted
by `new_rule` and the existing `construct-native rule` command. The new `weighted-rule`
command resolves symbolic references. Native IDs stay decimal strings, including
values beyond JavaScript's safe integer range. The request supplies logical
`rule_id`; it does not fabricate persisted `id`, timestamps or user audit fields.

Define zero/missing-weight behavior and check that allocated children reconcile to the amount. Local construction does not execute an allocation.
