# Leaf-level storage identity

## Business rule

Default new planning storage to the stable leaf entity ID when multiple visible
columns describe one entity from the same semantic table. Keep descriptive ancestors
in Rows/Columns for grouping and display, but turn their **In key** setting off.
This prevents a rename or movement between parents from adding those mutable labels
to the stored coordinate. This is a default the user can override.

For `Brand -> Category -> Subcategory -> SKU`, where the assigned SKU resolves to a
unique `ProductKey`, retain SKU with the ID strategy and exclude Brand, Category and
Subcategory from storage identity. Do not remove them from the visible hierarchy.
The native observed representation is:

```json
{
  "mappings": {
    "Product[Brand]": {"Skip": {}},
    "Product[Category]": {"Skip": {}},
    "Product[Subcategory]": {"Skip": {}},
    "Product[SKU]": {"ID": "Product[ProductKey]"}
  }
}
```

These are synthetic external field identities. Resolve the real fields and construct
the companion `pivot` lookup descriptors with `runtime.dimension_mapping`; this
fragment alone is not complete mapping state. A key descriptor is lookup metadata,
not an additional visible row level. UI disabled-toggle styling in a screenshot
does not establish whether a leaf is excluded: follow its saved mapping contract.

Apply independently to each entity table: for example a region ID and a product ID
can both remain in the coordinate, along with the required time and scenario grain.
“Leaf-only” does not mean retaining just the last column in the whole visual.

## Preconditions and exceptions

- The retained ID must uniquely identify the planned entity at the intended grain
  and determine the excluded attributes. Use existing key/relationship metadata,
  a model contract or explicit business knowledge; do not invent an ID or require
  unnecessary live queries merely to restate established metadata.
- Same table alone is insufficient. Keep independent planning dimensions, multiple
  entity leaves, role-playing fields, user-selected key components and composite-key
  discriminators. A SKU unique only within company must retain company or use an
  established unique composite/surrogate key.
- For a leaf with a versioned/surrogate key, values follow that exact key. A new key
  after a slowly changing dimension transition is not automatically a rename or
  parent move. Do not promise cross-key value migration.
- Parent/child hierarchies, non-unique labels and lookups need their own identity
  contract. Never toggle ancestors off solely because they appear above another row.
- Time mappings are separate. A month label without year is not unique, nor is Q1
  across years. Preserve the actual supported calendar grain, time interval mapping
  and forecast/time-extension metadata. The leaf helper does not auto-skip calendars.
- Existing stored inputs must not be silently re-keyed. Preserve their current
  mappings unless an explicitly requested, supported migration carries those values
  to the new coordinates. A style change is not a migration.

The policy avoids including mutable parents in new coordinates; it is not a claim
that a particular report's reparenting, data refresh or persistence was tested.

## Guide to command

```text
python scripts/plan.py leaf-key-mapping --input assets/examples/leaf-key-mapping.request.json --out mapping.json
```

Input: current `model`, actual semantic `assignments`, and resolved `groups`:

```json
{
  "leaf": "Product[SKU]",
  "key": "Product[ProductKey]",
  "ancestors": ["Product[Brand]", "Product[Category]", "Product[Subcategory]"],
  "unique": true,
  "determinesAncestors": true,
  "evidence": "Model key contract: ProductKey identifies one product and determines its current attributes"
}
```

The agent derives the group from the business grain and model metadata. Users need
not know this syntax. An unresolved key dependency keeps its current mapping and is
reported; it must not become an invented assertion of uniqueness.

For new sheets, put those groups in `dimensionKeyGroups`; both `build` and the base
provisioner's scope preparation preserve them. Use `dimensionKeyOverrides` for
explicit choices: an entry `"Product[Brand]": null` retains its native label/default
key strategy. Explicit ID/Skip strategies are also accepted where their dependencies
remain valid. Do not combine `dimensionKeyGroups` with `dimensionIdMappings`.
The existing explicit `dimensionIdMappings` + `dimensionSkipSupport` route remains
available for previously resolved profiles, including context-only descriptors.

The helper validates field ownership, descriptors, axis scope and evidence, then
returns native `mappings` plus complete `pivot` descriptors. It never changes visible
assignments, permissions, formulas, input records or model data. For existing state,
pass `existing`; a different storage mapping is rejected pending a separate migration.
