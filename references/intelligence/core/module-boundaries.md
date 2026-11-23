# Intelligence ownership and data-source scope

## Reference namespace and integrated ownership

Everything under `references/intelligence/` applies to **Intelligence Sheets**:
mode guides, property references, design rules,
formula guidance, feature indexes and source evidence. A documentation URL
under Planning does not make the consuming Intelligence guidance a Planning
instruction; each reference explicitly limits what is applicable.

This library is bundled in [fabric-plan-skill](../../../SKILL.md), which also
provides Planning, PowerTable and InfoBridge construction. Route those operations
through [module routing](../../module-routing.md) and their owning guides;
do not apply Intelligence property schemas or formula subsets to other modules.
The latest skill contract supersedes standalone semantic-model-only release
gates retained in older Intelligence guides. Integration is not permission to
invent a missing factory, binding or runtime guarantee.

| Surface | Intelligence ownership |
|---|---|
| `REPORTING` sheets | Report layout, Matrix, charts, KPI, slicers, navigation and native reporting formulas |
| Planning sheets | Own inputs, forecasts, storage Context and formulas through the Planning routes; Intelligence consumes supported outputs and embeds without moving the owner |
| PowerTable | Own table/source/column configuration through PowerTable routes; preserve its native parts during Intelligence edits |
| InfoBridge | Own queries, transformations and output lineage through InfoBridge routes; Intelligence consumes resolved current output fields |
| Shared Plan definition | Transport the complete definition; preserve other modules' parts and unrelated shared settings |
| Semantic model | Read-only except explicitly approved measures under the existing ownership/permission rules |

Reference paths such as `core/...`, `design/...` and `features/...` in these
guides are relative to the Intelligence reference root. Bundled `assets/` paths
are skill-root resources. Keep task `_brief/` and `_build/` directories outside
the installed skill. Historical `scripts/` commands are not shipped here; use
the [runtime guide](../../runtime-guide.md) and `plan.py discover` for actual
commands. Do not move other modules' artifacts into this namespace.

Feature IDs are local to Intelligence. In a merged dispatcher identify a
feature by module plus ID (for example `intelligence:KPI-VAR-01`); preserve the
existing ID inside Intelligence briefs. Keep the
[reference index](../index.md), [feature master list](../feature-master-list.md)
and module-routing entries consistent. The standalone `build_index.py` generator
is not bundled and is not required for ordinary authoring.

## Product capability versus current release

Source: [Blend measures | Plan](https://docs.fabricplan.com/planning-sheets/concepts/connected-planning/blend-measures).
The [reviewed upstream contracts](upstream-references.md) add public API and
container/reference guidance, not proof of tested blend behavior. Construction
coverage comes from the current bundled source-aware contracts.

Intelligence Sheets are **not inherently restricted to semantic-model
measures**. The product supports a single visual combining baseline model
dimensions/measures with live measures from other modules:

- Model actuals and baselines can be compared with Planning inputs, formulas,
  simulations and forecasts exposed under **From Sheets**.
- The documentation describes blending semantic models, external files,
  Planning and PowerTable data in Intelligence analysis, with InfoBridge
  providing blending across sources.
- Planning-backed values can respond to source-sheet changes. Do not promise
  that behavior without verifying the actual bindings and runtime.

Use supported semantic, From Sheets and From Queries bindings through
[source-aware assignments](../../measure-source-bindings.md),
[Context/Intelligence construction](../../context-intelligence.md) and the
applicable [OneLake consumer contracts](../../onelake-linked-values.md).
Planning embeds are part of the application baseline, not blocked on a future
module merge. Product support for another source does not establish a bundled
factory for it; check the exact route before promising construction.

1. Resolve actual source owners, current measure/query/output identities and
   compatible grain, units and storage Context. Never match sources by caption.
2. Keep semantic-model field closure separate from sheet/query lineage checks.
   Do not relabel connected outputs as model fields or invent DAX substitutes.
3. Preserve other modules' parts, embeddings, input identities and unrelated
   settings. Use a fresh baseline and scoped updates; never delete valid parts
   to pass a model-only validation check.
4. Report a precise remaining contract gap, not "module integration pending".
   Preserve the original request and continue independent authorized work without
   silently deploying a reduced substitute.

## Cross-module construction and evidence requirements

Observed encodings in [cross-module blend](cross-module-blend.md) are evidence,
not an execution recipe. Use the current bundled helpers with:

- Explicit ownership/routing to the integrated modules; no unrelated Intelligence
  edits to inputs, queries, cube, writeback or source-sheet definitions.
- Native evidence for each binding and a provenance-aware field registry:
  source module, source object/measure identity, lineage, grain, relationships,
  aggregation, units, scenario/period, refresh behavior and permissions.
- Source-aware closure/validation and permission checks, including combinations
  in the **same visual**. Do not bypass bundled checks or use display-name matches
  across sources as a substitute.
- End-to-end tests for blending, source changes, filters, security, readback
  and preservation of other module parts; user approval of the report scope.

Do not invent property keys or infer runtime acceptance from a reference file's
presence or a feature's encoding status.

## Production reporting

Use business report titles and production-oriented instructions. Sample
definitions are evidence for native encoding, not verified business data.
Keep truthful source, as-of, freshness and quality caveats; do not remove them
to make an illustrative dataset appear operational. Exact external model/item
names and serialized identifiers must remain unchanged when needed for binding.
Do not publish without approval or claim runtime verification that did not occur.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- **Sheet hosting.** In the product a Planning sheet holds one planning matrix
  and a PowerTable sheet one table; to show either beside charts, it is
  embedded on an Intelligence sheet [confirmed]. Use the integrated skill's
  current embed constructor and destination placement contract.
- **Legacy source types.** The official legacy
  `semanticModelReference.sourceType` list also includes `POWERTABLE` and
  `INFOBRIDGE`, while native Intelligence exports here carry `WORKLOAD` [open].
  Preserve any other value unchanged and report it as module scope.
- **Model signals.** Input columns, or tables fed from Planning sheets, signal
  planning writeback; record them as a module dependency, not Intelligence
  scope.
- **Validation layer.** Planning input/save/reopen and downstream refresh are
  separate acceptance checks when the application uses those modules. Record
  unperformed checks as pending or skipped with a reason, never as passed.
- **Procedure ownership.** Use the bundled Planning, InfoBridge and PowerTable
  guides for their authoring procedures; this Intelligence library does not
  replace their execution contracts.
