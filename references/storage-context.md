# Storage Context versus page and global filters

Rows and Columns already define the planning input coordinate. **Do not also
add an assigned row or column dimension to Context.** For example, Year and
Quarter on the time axis do not need additional Context selectors.

Use **Context** only for a field outside those axes when the selected member
must also identify the saved input. Typical cases are Scenario Name/ID or
Version Name/Number/ID. Select the actual business storage dimensions; do not
automatically add every scenario/version attribute, duplicate a key and label,
or manufacture a Context when the requirement does not need one.

| Setting | Scope | Changes the input storage coordinate? |
|---|---|---|
| Rows / Columns | Planning visual grain | Yes |
| Context | External, single selected storage member | Yes, for bound inputs |
| Page-level filter / dashboard slicer | View on that page | No |
| Global-level filter | View across pages | No |

Ordinary filters can restrict which row/column members are visible and therefore
which existing cells a user can edit. Their selections do not become extra
storage dimensions. Single select by itself does not turn a normal slicer into
Context. Context is not security, RLS or an authorization rule.
The current UI's `filterContextBar.height` is transient rendered-layout state,
not a saved storage-Context property. Do not author it into `visualState` or use
it as evidence that Context is configured.

## Connected source and destination owners

For **From Sheets and From Queries**, keep the same storage Context across
the contributing and consuming Planning owners: same semantic fields, same
ID mapping policy, and the same intended selected scenario/version. A source
Version cannot become destination Year/Quarter, and a page filter cannot replace
either owner's Context. Do not copy registration UUIDs or runtime context hashes.

- `runtime.storage_context.signature(owner)` for symbolic specs or current
  native owner properties. Presentation labels and registration order are ignored.
- `require_same(source, destination)` checks identity, key mapping and typed
  initial selection. Both owners with no external storage context are valid.

### From Queries lineage

Verify that each query retains the source storage fields as output dimensions
through transforms, grouping and append. Resolve actual output IDs from current
metadata. An opaque OneLake query ID and a Fabric SQL numeric binding ID remain
different supported identity profiles; context semantics do not change by mode.

```python
from runtime.storage_context import query_contract, require_query
from runtime.consumer_bindings import numeric_output_fields

# Fresh owner properties and selected output metadata, not previous report IDs.
proof = query_contract(current_query, current_source_owner_properties,
                       {"Version[Number]": actual_version_output_id})
fields = numeric_output_fields(current_query, storage_context=proof)
# Supply fields as application_spec['queryFields'] for Planning construction.
# The builder compares the proof with the constructed destination context.
```

The map must include every Context field, each mapped to a distinct selected
query dimension. Multi-source queries require matching source context. This
evidence is a **build-time sidecar**; it is not a native API property and is not
serialized into visual assignments. The Planning constructor refuses query
Values without this evidence. For a source with no external Context, explicitly
verify that fact and use an empty map; never infer absence from a missing catalog.
Custom field remapping or combining different versions requires its own reviewed
business/storage contract, not bypassing the guard.

## Existing reports and validation

Inspect current saved Context before changing it. Adding, removing or remapping
a field can change which existing inputs are found. Do not silently migrate or
re-key populated inputs as a presentation fix. Preserve existing values and
require a supported retention/migration plan for a storage-key change.

These local checks compare metadata. They do not test recalculation or isolation when a user switches versions.
