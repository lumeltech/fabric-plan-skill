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
python plan.py build --model current-model.json --spec application.json --out draft
python plan.py check-import-contract --spec application.json --construction draft/construction.json --out coverage.json
```

Keep the original request with the candidate. Check that requested measures,
inputs, formulas and conditional rules survived construction together. When
editing a definition, start from a fresh complete export, keep unknown parts
and existing identities, and inspect the scoped diff. Do not silently rebuild
a smaller report when a requirement cannot be represented.

**Public Fabric operations.** `api export` calls `getDefinition` for the
selected workspace and Plan. `api create` takes a new name and complete
definition; `api update` targets an existing Plan with `updateDefinition`.
Use an authorized identity and explicit destination config. For example:

```sh
python plan.py api export --config destination.json --run run --label baseline
```

Export is a read; create and update are writes. For asynchronous operations,
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
