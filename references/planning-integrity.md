# Planning formatting and field-name integrity

Use when a generated Planning grid fails while reading default formatting, or
when renamed attributes disagree across assignments, filters and pivot metadata.
These are offline definition checks. They do not execute the report or prove that
the native renderer, calculations or writeback work.

## Business request to command

| Request | Action |
| --- | --- |
| Avoid incomplete formatting objects in a new plan | `build` completes known defaults; `format-matrix` completes them before applying typed formatting |
| Check a saved Planning visual before updating it | `check-planning-properties` with the current physical model catalog |
| Repair missing defaults and inconsistent grouping names | `repair-planning-properties`, review its changes, then publish only the returned `properties` |
| Use business wording such as Market for Country | Keep the physical grouping identity and canonical grouping name throughout this authoring path; put business wording in headings or explanatory text |

```text
python scripts/plan.py check-planning-properties --input properties.json --model current-model.json --out check.json
python scripts/plan.py repair-planning-properties --input properties.json --model current-model.json --out repair.json
```

Input is one plain Planning properties object, including `pivotAssignments` and
`visualState`, not an ALM part envelope. Output of repair includes `properties`,
`changes`, `check` and `runtime: not-run`. Never save the repair wrapper as native
properties. Keep it in the task audit directory. A repeat repair is idempotent.
The synthetic `assets/examples/planning-integrity.properties.json` can be repaired without
`--model`; real authoring should pass a current catalog with exact field IDs.

## Complete defaults, preserve intentional formatting

The complete known `GlobalStyles` initializer is captured in
`assets/fixtures/matrix-global-defaults.json`, from the bundled feature contracts'
GlobalStyles default profile. It includes body/header typography, hierarchy and
subtotal typography, header controls, variable color, variance/KPI sizes and chart
scale. It is a versioned baseline, not a claim to contain every future property.
Fill only absent defaults; preserve explicit valid values and unknown extensions.
Present nulls or incompatible types fail with a path instead of silently replacing
user formatting. Body fontSize is a positive numeric string; headerFontSize is a
positive pixel string; Column Style fontSize is a number. Both boolean and numeric
types are checked. Do not substitute CSS properties or write row heights here.

For each present supported Column Style category, complete each present `read`
or `edit` mode independently from the bundled preset. Preserve each mode's
explicit values, including borderSides null and borderWidth zero. A missing mode
stays missing and a null mode stays null: the product renders either with no
Column Style, and its Reset saves null. Never copy one mode's colors into the
other. The product's Column Style editor offers border sides 1-3 and 7-12. Conditional rules, ordered formatting, Forecast open/closed
styles and all earlier type/scope checks remain in effect.

## One physical grouping identity across every reference

Resolve the actual model field by ID, for example `DimRegion[Country]`. Never
invent `DimRegion[Market]` from a business caption. In this selected authoring path,
use `Country` consistently in semantic grouping assignment name/columnName, native
dimension labels, filter assignment/caption/sort/DTO metadata and dimension lookup
pivot descriptors. The check catches stale aliases even when the field ID is valid.
Do not run a late label-only rename after filters and mapping have been generated.
Native UI rename support is not an assertion that this package implements its full
rename contract; a future alias writer needs its own complete synchronized contract.

The repair derives table and column from the exact semantic field ID, checks them
against the supplied model catalog and refuses unresolved identities. It never
changes assignment IDs/source IDs, dimension IDs, storage mappings (ID/Skip),
selected filter members, measure labels, formulas, From Sheets source names/IDs,
periods, input locks, data records or sheet grain. An existing storage-key change
remains a separate migration concern under the dimension leaf keys guide.

## Executable enforcement and save boundary

The constructor normalizes and checks newly generated Planning properties.
The formatting compiler completes and checks styles. `validate`, `encode` and
the bundled HTTP Client's Plan create and updateDefinition requests reject
incomplete defaults or noncanonical grouping references before the network
adapter is called. The write guard does not silently repair payloads.
Use the repair command explicitly on an older saved definition first. Non-Planning
visuals and read requests are outside this guard. Direct HTTP outside the bundled
Client is outside this enforcement boundary.

For an authorized existing-report patch, start from a fresh export, apply
`repair-planning-properties` to the owner's properties, preserve unrelated records
and publish with `api update`. No browser or post-save readback is needed when the
user asks to skip runtime validation. A successful API receipt establishes saving
only. Offline regressions cover missing defaults/types, independent style modes,
all named reference surfaces, idempotence, preservation and the guarded create and
update routes.
