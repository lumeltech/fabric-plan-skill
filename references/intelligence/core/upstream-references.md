# Upstream references and public-contract coverage

## Provenance and precedence

Reviewed source: [tmdaidevs/fabric-planning-skill](https://github.com/tmdaidevs/fabric-planning-skill),
revision `ce129e8bce4663f3f6f8fff154df3c253c3fc377`.
Its [README](https://github.com/tmdaidevs/fabric-planning-skill/blob/ce129e8bce4663f3f6f8fff154df3c253c3fc377/README.md)
identifies it as a community project, not an official Microsoft product.
Treat it as a secondary reference to the Microsoft documentation and schemas
it cites, not as Microsoft product certification.

This integration covers core definition contracts, API behavior, blend
preservation, and Intelligence only. It retains this skill's existing modes,
folder structure, tools, native evidence, approval gates, and semantic-model-only
authoring scope. Planning, PowerTable and InfoBridge references are not imported.

Use the exact schema version embedded in a part and the public API contract.
When documentation, schemas and fresh native readbacks differ, record the
discrepancy and preserve unknown service fields; do not strip them or invent a
conversion to make validation pass. A documented wrapper is not a verified
encoding for the settings inside it.

## Source-to-local mapping

| Area | Upstream reference | Local guidance |
|---|---|---|
| Snapshot, reconcile, apply and verify | [Shared workflow](https://github.com/tmdaidevs/fabric-planning-skill/blob/ce129e8bce4663f3f6f8fff154df3c253c3fc377/SKILL.md#one-workflow) | [Management](../management.md), [verification](../management-part-02.md) |
| Seven Plan APIs, scopes, pagination, telemetry and LROs | [API reference](https://github.com/tmdaidevs/fabric-planning-skill/blob/ce129e8bce4663f3f6f8fff154df3c253c3fc377/references/api-reference.md) | [REST and LRO](rest-and-lro.md) |
| Root, sheet, platform and Intelligence contracts | [Definition authoring](https://github.com/tmdaidevs/fabric-planning-skill/blob/ce129e8bce4663f3f6f8fff154df3c253c3fc377/references/definition-authoring.md) | [Definition structure](definition-structure.md) |
| Portable and variable-library references | [Root/reference contracts](https://github.com/tmdaidevs/fabric-planning-skill/blob/ce129e8bce4663f3f6f8fff154df3c253c3fc377/references/definition-authoring.md#root-reference-and-sheet-contracts) | [Definition structure](definition-structure.md#definitionjson) |
| Intelligence page variables, canvas, filters and visual wrappers | [Intelligence contracts](https://github.com/tmdaidevs/fabric-planning-skill/blob/ce129e8bce4663f3f6f8fff154df3c253c3fc377/references/definition-authoring.md#intelligence-contracts) | [Canvas features](../features/canvas/_index.md), [definition structure](definition-structure.md) |
| Blend and embedded-source preservation | Shared root/visual references, not a new blend API | [Cross-module blend](cross-module-blend.md), [module boundaries](module-boundaries.md) |

The upstream helper is not bundled here. Continue using `az rest` for transport
and `scripts/plan_def.py` for local work; upstream CLI flags are not commands
supported by this skill's helper.

## Official sources

- [Plan REST operation group](https://learn.microsoft.com/en-us/rest/api/fabric/plan/items)
- [Plan definition specification](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/plan-definition)
- [Core Update Item Definition](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/update-item-definition)
- [Long-running operations](https://learn.microsoft.com/en-us/rest/api/fabric/articles/long-running-operation)
- [Pagination](https://learn.microsoft.com/en-us/rest/api/fabric/articles/pagination)
- [Variable-library definition](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/variable-library-definition)
- [Fabric platform metadata](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format)

Schema paths below are relative to the
[official Plan schema directory](https://github.com/microsoft/json-schemas/tree/main/fabric/item/plan/definition).
They locate published files; they are not replacement `$schema` values.
Preserve the case-sensitive URI embedded in each part.

| In-scope contract | Published schema path |
|---|---|
| Root | `Definition/1.0.0/schema.json` |
| Plan properties | `PlanProperties/1.0.0/schema.json` |
| Sheet | `Sheets/Sheet/1.0.0/schema.json` |
| Intelligence properties | `Intelligence/Properties/1.0.0/schema.json` |
| Structure manifest | `definitionStructure/1.0.0/definitionStructure.json` |

Shared reference schemas:
[connection](https://github.com/microsoft/json-schemas/blob/main/fabric/common/connectionReference/1.0.0/schema.json),
[item](https://github.com/microsoft/json-schemas/blob/main/fabric/common/itemReference/1.0.0/schema.json),
[variable](https://github.com/microsoft/json-schemas/blob/main/fabric/common/variableReference/1.0.0/schema.json).

## Evidence limits

The upstream documents Intelligence containers, not isolated Matrix, chart,
Super Filter or KPI setting encodings. Do not blanket-upgrade feature
`encoding` confidence or replace observed native objects with generic examples.
Source links added to features establish contract coverage only.

It does not establish a tested `From Sheets`/`From Queries` binding recipe or
source-aware closure for this skill. Cross-module blend remains preservation-only.
Matrix's within-cell Blend measures is a separate presentation feature.

`plan_def.py validate` checks local structure, field closure and existing
preservation rules; it is not complete JSON Schema validation or a runtime test.
Check the applicable versioned schema contracts separately and report the
verification layers accurately.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Companion-library coverage

The companion Intelligence authoring library was merged additively. Its
topics map to these local sections:

| Companion topic | Local section |
|---|---|
| Validation layers and completion claims | Validation layers |
| Model study, measure classification, metric contract | Model inspection, metric contract, discovery part 2 |
| Sheet structure, identities, cloning and geometry | Invariants, definition structure |
| Visual identity and observed families | Product architecture |
| Transport, readback and copies | REST and LRO, management, management part 2 |
| Donor comparison and capture refinements | Native samples |
| Module parts and embedded sources (preservation only) | Cross-module blend, module boundaries |

### Schema URL case

The official article's examples show lowercase `definition/1.0.0` and
`planProperties/1.0.0` schema paths, while native exports embed
`Definition/1.0.0`; the companion work found the lowercase root-schema path
unavailable when fetched [open]. Keep the URI embedded in each part and fetch
published schemas by that case-sensitive path.
