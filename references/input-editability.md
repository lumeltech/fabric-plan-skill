# Allow Input defaults and conditional editing

For **new editable Data Input and Forecast measures**, explicitly emit
`"allow_input": "ReadAndEdit"`, corresponding to **In both Read and Edit mode**.
This applies to **every Data Input type**: Number, Simulate, Text (short and long),
Checkbox, Person, List (single and multi select), and Date. It also applies to
commentary and supported visual-column placement of these inputs.

Forecast uses the same explicit default in its edit configuration. Choose `Edit` only when edit-only entry was requested.

When the business asks for conditional lock/unlock, approval/status gating,
eligibility or another expression-controlled edit rule, use **Allow Input based
on formula**, with a real expression:

```json
{"allow_input": {"BasedOnFormula": "${eligible} > 0"}}
```

`eligible` must resolve to an actual policy measure for the current cell grain.
If multiple conditions apply, resolve the business eligibility logic at that
grain and write the corresponding expression using supported formula functions.
The example above is a symbolic spec, not a deployed expression. Constructors resolve these
symbols to current native `M_<id>` references. Use the installed formula contract
for operators/types; never deploy placeholders, labels as IDs, copied old IDs or
an invented policy field. If a required business condition cannot be resolved,
keep it unresolved rather than replacing it with unrestricted ReadAndEdit. A
predicate states when input is permitted: true allows input, false prevents it.
The input rule does not grant access, override independent permissions or reopen
Forecast closed periods. Defaults, on-change actions and conditional formatting
serve different purposes and do not replace this gate.

## Correct property owner and construction route

| Owner | Native path | Authoring route |
|---|---|---|
| Ordinary input | `columnMeta.measure_type.DataInput.allow_input` | `construct.planning` numeric spec or `input_create(..., allow_input=...)` |
| Visual-column input | `columnMeta.measure_type.VisualColumn.DataInput.allow_input` | `input_create(..., visual_column=True, allow_input=...)` |
| Forecast | `columnMeta.measure_type.Forecast.edit_config.allow_input` | Forecast spec `allow_input`, resolved by `forecast_config` |

The reusable `runtime.input_policy.allow_input` enforces the union, nonempty
formula and resolvable symbolic/native references. Forecast eligibility symbols
also join the construction dependency graph. These offline checks do not compile
or evaluate the expression in the native engine.

For a new Forecast derived from a reference, do not inherit the reference's
incidental Edit mode. Set the requested policy explicitly, otherwise ReadAndEdit.
A reference with formula gating requires an explicit remapped policy; do not copy
its old IDs or silently erase the condition. For a repair of an existing report,
preserve its intentional mode/formula and other locks unless that change is
authorized. This default update is not a blanket unlock or data migration.
