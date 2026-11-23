---
id: CV-VAR-01
name: Entity-level variables
area: canvas
category: Variables
status: IS-Confirmed
encoding: unverified
visual: Sheet
sources:
  - https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/Intelligence/Properties/1.0.0/schema.json
  - https://github.com/tmdaidevs/fabric-planning-skill/blob/ce129e8bce4663f3f6f8fff154df3c253c3fc377/references/definition-authoring.md#intelligence-contracts
---

# Entity-level variables

## What it does

Declares typed variables in Intelligence page settings. The public contract
supports action, number, text, dropdown, date and slider types with entity,
visual or page scope. This describes the declared configuration, not verified
action execution or a Matrix formula-variable encoding.

## When to use

- Preserve existing page controls and defaults while editing a report.
- Assess a requested parameter/control against the documented contract, then
  capture a same-kind native example before adding it.

## UI path

Variables pane when enabled by the Plan's mode settings. Capture the precise
creation/configuration path in the current Fabric Plan UI before instructing
the user or authoring a new control.

## Definition encoding

```text
Public Intelligence container: properties.properties.entityLevelVariables[]
Required per variable: id, label, type, scope, technicalName
Types: action | number | text | dropdown | date | slider
Scopes: entity | visual | page
Optional groups: value/defaultValue, options, interfaceType, min/max/interval
Evidence: published schema; no isolated native capture or runtime test
```

Preserve the actual source part and its wrapper; see
[definition structure](../../core/definition-structure.md). Optional fields
also cover display/reader settings and data-backed options. Use the exact
schema version and a native example rather than assuming every option applies
to every type.

Run the [native-sample workflow](../../core/native-samples.md) before writing
new controls or behavior. Do not mark the encoding verified from schema coverage.

## Constraints

- Entity variables are not variable-library connection/item references, model
  measures, or Matrix-local formula variables.
- Do not infer action scripts, private endpoints, writeback permissions or
  external-source bindings from an action type or configuration flag.
- Test defaults, selection/reset, value types, ranges, reader visibility and
  the consuming visual's response. Preserve unrelated variable definitions.
- The semantic-model-only and module-integration gates still apply.

## Related features

- `CV-MODE-01` - pane visibility in reading and editing modes.
- `CV-FILT-01` - distinguish variable values from filter state.
