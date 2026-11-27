# Build and inspect a Planning definition

Start with the business grain, not a template. For each sheet record who enters
which value, at what entity and period, in which units, and how a reviewer
should total it. Keep approval, access policy and scenario lifecycle as explicit
unresolved requirements unless the destination supplies those controls. A
filter, input field or color does not implement them.

The local builder takes a model catalog (`reference` and `fields`) and a spec
(`name` and `sheets`). Rows and columns use exact table-qualified model field
IDs. Use unique measure keys within each sheet. For example, a sheet may bind
a `Native` measure with `{"key":"base","kind":"Native","label":"Base pay",
"source":"Metrics[BasePay]"}`. The caption is not a substitute for the source.

```sh
python scripts/plan.py build --model current-model.json --spec application.json --out draft
python scripts/plan.py check-import-contract --spec application.json --construction draft/construction.json --out coverage.json
```

`validation.json` can report `passed-native-extension` for the reviewed native
dashboard visual types, object-form Home layout, and target-input values that
the pinned historical public schemas do not describe. These rows are
normalized only for schema checking; the authored native payload is unchanged.
Treat `schema-conflict` or `schema-gap` as a deployment blocker. A passing
schema report is still static evidence, not backend or UI acceptance.

Keep the original request with the candidate. Check that requested measures,
inputs, formulas and conditional rules survived construction together. When
editing a definition, start from a fresh complete export, keep unknown parts
and existing identities, and inspect the scoped diff. Do not silently rebuild
a smaller report when a requirement cannot be represented.

**Public Fabric operations.** `api export` calls `getDefinition` for the
selected workspace and Plan. `api create` takes a new name and complete
definition; `api update` targets an existing Plan with `updateDefinition`.
`api list` and `api get` read Plan metadata, `api rename` changes a Plan's
display name or description, and `api delete` removes a Plan only after
confirming its ID and current display name.
Use an authorized identity and explicit destination config. For example:

```sh
python scripts/plan.py api export --config destination.json --run run --label baseline
```

Export, list and get are reads; create, update, rename and delete are writes. For asynchronous operations,
retain the operation receipt and resume with the same journal rather than
submitting a second create. A completed operation establishes API acceptance,
not formula evaluation, persisted cell values or permission to edit a cell.

For a repair, use a new run or export label to obtain a fresh baseline rather
than replaying a receipt. Patch the `body` of `result.json`; copy its top-level
`baselineSha256` into the update config. Review the changed parts and authorize
the update for that same Plan. A new update re-exports and compares the baseline;
if it differs, reconcile and review a new candidate. This is not a server-side
lock. Coordinate an exclusive edit window when loss of concurrent edits is
unacceptable. Afterward, use a new export label for readback.

Only `https://api.fabric.microsoft.com/v1` is a supported base. The transport's
64 MiB response limit is local, not a Fabric capacity guarantee. Check available
disk space and applicable destination limits before publishing large definitions.
Report unknown limits or rejected payloads; do not silently drop parts.
