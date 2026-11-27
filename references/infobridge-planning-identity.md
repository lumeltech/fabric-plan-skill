# Planning-source InfoBridge mappings

Use this guide when building an InfoBridge source from a Planning owner, adding
transformations, importing it into a destination, or repairing unresolved query
fields. Search terms: missing Queries, From Sheets, measureGuid, columnType,
source selector, native sqlPk, integer range, incomplete mappings, field lineage.
Route it with the discovery step in the skill instructions using `--module INFOBRIDGE-MAPPING`, or by F18.

## Contents

- [Why this belongs in construction](#why-this-belongs-in-construction)
- [Source contract: resolve identity before copying descriptors](#source-contract-resolve-identity-before-copying-descriptors)
- [Self-contained construction example](#self-contained-construction-example)
- [Resolve destination outputs after import](#resolve-destination-outputs-after-import)
- [Completion boundaries](#completion-boundaries)

## Why this belongs in construction

A generated graph can omit explicit source-measure lineage in its catalogs
and transformation descriptors. Portable unsigned-64 measure IDs remained in
native selector positions; export failed with a signed-integer-range error marked
non-retriable. Adding the mappings and resolving consumers from current query
outputs restored source/query initialization and export. This is a construction
failure, not a reason to sleep, repeatedly reload, or request a different token.
Other authentication/job failures have separate causes; diagnose their response.

The recorded repair establishes those API outcomes, not universal UI visibility,
correct business values, edit-trigger propagation or RLS. Missing From Sheets or
Queries is a symptom, not proof of this particular cause. Inspect owner
registration and source/query metadata independently. A consumer reference does
not create its source, query, or native input companion.

## Source contract: resolve identity before copying descriptors

For the observed Planning-source writer, each actual owner measure carries:

| Field | Rule |
|---|---|
| `id` | Portable source: the owner's exact `measureGuid` string. Native selector: the current registered selector ID, as a string, in an explicitly selected native workflow. |
| `measureGuid` | The exact owner identity. Never replace it with a small SQL-row ID or a name-derived hash. Keep unsigned-64 IDs as strings. |
| `columnType` | `DI` for registered `DataInput`, `Native`, and `Forecast`; `FORMULA` for registered `Formula`. These are InfoBridge source codes, not consumer `Column`/`Measure` enums. |
| `isHierarchyColumn` | `false` for these measure descriptors. Do not stamp auxiliary date/hierarchy records. |
| `name`, `alias`, `type`, `dataType`, aggregation | Preserve actual names, SQL/logical types, captions and chosen aggregation. Infer neither source kind nor identity from a label. |

Use current owner records from the same generated `dataInput.json.columns` or
the owning visual's native column catalog. Do not use unrelated reports or
previous task scripts. Match by exact identity; if the owner name conflicts,
resolve the mismatch rather than matching by name. Unknown measure variants
need their own source contract; the builder rejects them instead of guessing DI.

`runtime.bridge_identity.planning_catalog(catalog, owner_columns,
identity_mode='portable')` returns a copy with complete source descriptors.
`planning_source`, Planning `Query`, `construct_query`, and `contribution` accept
the same optional `owner_columns`/`identity_mode` arguments. Without owner records,
the supplied measure catalog must already contain explicit lineage and type.

The normalized descriptor must survive in source/query base `measures`,
`selectedMeasures`, `includeMeasures`, and every transformation copy that refers
to that owner field, including Pivot `sourceMeasures` and `removeColumns`, Filter
`sourceColumn`, and Rename's input descriptor. Use the enriched source catalog
for every branch. Query-derived or renamed output IDs have their own identity;
do not tag them as owner inputs or turn their SQL expressions into Planning formulas.
PowerTable/EDITABLE, SQL, Append, Join and Merge sources retain their own contracts.

## Self-contained construction example

From the installed/extracted skill directory:

```text
python scripts/plan.py construct-bridge planning-source --input assets/examples/infobridge-lineage/planning-source.request.json --out source.json
python assets/examples/infobridge-lineage/build.py draft
python scripts/plan.py check-bridge-mappings --input draft/infobridge.json --out mappings.json
```

The example uses clearly illustrative owner records and builds fresh source/query
identities. It includes a Forecast and Formula with large IDs, a pivot, and an
illustrative post-import query catalog with different native IDs. It makes no
network calls and is not deployable production data. Replace its owner/catalog
inputs with the current application's records for real work.

```python
from runtime.bridge import planning_source, Query, portable

source = planning_source(
    name, owner_visual_id, catalog, selected_measures, selected_scenarios,
    owner_columns=owner_records, model_reference=current_model_reference)
query = Query(query_name, source['sourceGuid'], source['meta'],
              visual_id=owner_visual_id).load_planning()
query.pivot(row_names, period_names, measure_aggregations)
source['queries'] = [query.record]
graph = portable([source], [])
```

`portable` checks lineage. The normal Plan create/update transport also checks
`connectedPlanning/infobridge.json` before sending a write, so assembling the
JSON manually does not bypass the check. Checks reject incomplete or conflicting
copies and do not silently rewrite source identities. This local structural guard
does not require UI or business validation.

## Resolve destination outputs after import

Import and finish the supported operation, then export the definition and take the
exact destination query metadata from its InfoBridge part. If the export lacks the
native identities a binding needs, report that binding as unresolved: reading
native query metadata through a workload route is outside this package. Keep the
portable query GUID distinct from its native `sqlPk` and selected output IDs.
Neither array position, a matching label, nor the old input-record ID proves the
query output identity.

```python
from runtime.bridge_identity import resolve_planning_output
from runtime.connected_components import bridge_consumer

field = resolve_planning_output(
    current_query, source_measure_guid, expected_name=expected_output_caption)
bundle = bridge_consumer(field, destination_visual_id,
                         destination_internal_measure_guid, display_label)
```

The resolver matches explicit `measureGuid` lineage in this query's current
`selectedMeasures`, then resolves that output through `output_catalog`. It fails
on absent/ambiguous lineage or a mismatched expected caption; it does not fall
back to label matching. An explicit empty selection stays empty. Its result has
the native qualified ID, query ID and consumer types required by `bridge_consumer`.
Derived/renamed outputs require their own explicit current output-ID mapping;
use the existing `consumer_bindings` helpers for that case.

The packaged CLI demonstrates this phase without live calls:

```text
python scripts/plan.py resolve-bridge-output --input assets/examples/infobridge-lineage/resolve-output.request.json --out field.json
```

For a new consumer, register all four objects returned by `bridge_consumer` through
the bundled column/property writers: assignment, Native companion, manage measure,
and aggregation. For an existing consumer, keep its internal `measureGuid` because
formulas, storage and measure models can depend on it. `bind-bridge-outputs` accepts:

```json
{
  "properties": {"pivotAssignments": [], "superFilterAssignments": []},
  "owner_columns": [],
  "queries": {"<portable-query-guid>": "<current complete query metadata object>"},
  "bindings": [{
    "measure_guid": "<existing destination Native measureGuid>",
    "query_guid": "<portable-query-guid>",
    "source_measure_guid": "<original owner measureGuid>",
    "expected_name": "<expected selected output caption>"
  }]
}
```

Replace every placeholder with the current records; include current metadata for
all InfoBridge queries referenced by this visual. The command returns a scoped
`properties` candidate and resolved mappings. It requires existing InfoBridge
assignments and Native companions, updates their matching filter/sort references,
and preserves internal aliases, formulas, inputs, locks, formatting and storage.
It performs no API writes. Apply the candidate to the visual in a fresh export and
publish it with `api update`. Never overwrite the entire report from an old
construction snapshot to make a binding repair.

The Planning integrity guard understands query sort IDs such as `77[12]`:
`12` is an opaque output key, not the physical field name. It compares the sort
caption with the assigned query output, while retaining semantic-field checks.
No task-local guard monkeypatch is required.

## Completion boundaries

Treat graph save/import, source/query initialization, output identity binding,
definition export, From Sheets/Queries UI visibility, and business behavior as
separate milestones. Report only observed results. Honor a request to skip runtime
validation; do not execute query reloads or business edits just to claim success.
Source/query refresh and downstream propagation follow the existing connected
workflow when authorized, not fabricated cached statuses or materialized paths.
