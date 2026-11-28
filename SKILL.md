---
name: fabric-plan-skill
description: Build, validate and update Microsoft Fabric Plan applications from business requirements and a semantic model. Use for Planning sheets, forecasts, connected planning, PowerTables and embedded Plan dashboards, not standalone Power BI reports.
---

> **Telemetry — MANDATORY.** Every `api.fabric.microsoft.com` call must carry
> `x-ms-fabric-skill: fabric-plan-skill` (`az rest`: `--headers "x-ms-fabric-skill=fabric-plan-skill"`),
> including every LRO poll, `fabric_lro` and retry. Snippets omit it — add it anyway.

# Fabric Plan

Run the Python CLI as `python scripts/plan.py` from this skill's root directory; data files live under `assets/`. Use a separate task directory for inputs, generated definitions and readbacks. Python 3.11+ and Node.js 24+ are required for the full offline workflow.

The bundled Python client adds the telemetry header to every request it sends, including operation polls and retries, and preserves it through the optional Node adapter. The value identifies this skill only and must not include tenant, workspace, report, user or credential data.

## Must/Prefer/Avoid

### MUST DO
- Use only documented public Fabric APIs and send the required telemetry header on every request, poll and retry.
- Build and validate a local candidate before any workspace write; require explicit write authorization for the named destination.
- Patch extensions and repairs from a fresh, complete export, preserve unrelated bytes and identities, and stop on baseline drift.
- Report locally built, locally validated, persisted and interactively verified outcomes separately.

### PREFER
- Resolve current model and destination metadata instead of inferring fields, grain or native identities.
- Use saved sheet, visual, source and measure identities rather than list order.
- Keep inputs, generated definitions and readbacks in a separate task directory.

### AVOID
- Do not deploy synthetic fixtures, invent unresolved inputs, or substitute private workload routes, token exchanges or UI automation.
- Do not package maintainer logs, credentials, task output or the whole working folder.
- Do not treat a saved definition as proof of navigation, input, stored values or rendered layout.

## Examples

- **New Plan:** `python scripts/plan.py build --model assets/fixtures/model.json --spec assets/fixtures/finance-spec.json --out /path/to/trial` constructs and validates an offline candidate; workspace creation remains a separate authorized step.
- **Extension or repair:** export the named Plan, patch only the requested parts and dependencies, validate locally, then update only after the reviewed baseline still matches.
- **Unsupported capability:** state that the requested operation has no public Fabric Plan API and identify the missing supported route without proposing a private workaround.

## Choose the scope before building

- **New Plan:** build from the current model and business spec. Enable public Home visibility; role-specific cards, layout and priority can be prepared locally but not published. For a complete application, check each requested sheet against the spec, each Planning grid's dashboard coverage, Arial on authored text, and a Page Navigator with resolved destinations on every dashboard.
- **Extension or repair:** patch a fresh, complete export of the named Plan; do not rebuild it from the model. Preserve unknown fields, unrelated part bytes, identities, formulas and settings outside the requested change and its dependencies. If storage keys or grain must change, establish a supported migration and authorized before/after checks of planner values at the same entity, period and scenario. Stop if required retention cannot be verified.
- **Inspection or design:** do not mutate the workspace. Distinguish a proposed change from a saved or verified one.

## Execution

1. Identify the target model and workspace. Use current model metadata for field names, types, hierarchy levels and aggregation. Do not deploy the synthetic fixtures. If a required source, identity or field cannot be resolved, identify the missing input rather than inventing one.
2. Use `python scripts/plan.py discover "business request"` to narrow the choice of topic, or select a guide below. Read only the topic needed. `python scripts/plan.py --help` is the inventory of executable commands; use a subcommand's `--help` for its arguments.
3. Construct and validate a local candidate. For example, `python scripts/plan.py build --model assets/fixtures/model.json --spec assets/fixtures/finance-spec.json --out /path/to/trial` writes local files without credentials. Before a workspace create or update, check required input registrations, formula references, sheet bindings, dashboard geometry and coverage against the request.
4. Use only the documented **public Fabric APIs**. Export, list and get are live reads; create, update, rename and delete require explicit write authorization for the named destination, and delete also needs a matching confirmation ID and the Plan's current name. Plan item create, rename and delete are also covered by the enterprise `plan-cli` skill: when `plan-cli` is available, route those item operations through it and keep this skill for authoring and validation, so one skill owns each write. A new update rechecks the reviewed baseline. Stop on drift. This check is not atomic: coordinate exclusive editing if a concurrent overwrite is unacceptable. If a feature lacks a public route, report it as unavailable; do not substitute workload endpoints, token exchanges or UI automation.
5. Export the result from the destination and compare it with the intended changes. Preserve native numeric identities as decimal strings. Placement identifies where a grid appears; its source owner and measure identify what formulas and bindings consume. Check both using saved identities, not sheet order. Neither check proves stored values survived.
6. Report what was built, validated locally, persisted, and verified interactively as separate outcomes. A saved definition does not prove that navigation, input or rendered layout works. After a failed write, read back current state before retrying; do not assume rollback.

## Packaging and publication boundary

Distribute only tracked, reviewed planning instructions, runtime, schemas, references, reusable examples, fixtures, tools and their licences. Never package the whole working folder. Keep task briefs, handoff notes, model exports, report samples, credentials and generated output outside the distribution. To publish a Plan, send only its validated public definition and required report resources, not this skill.

## Planning references

Choose a reference directly; the list is a menu, not a reading sequence.

| Task | Guides |
|---|---|
| Build, validate or update a definition | [Runtime guide](references/runtime-guide.md) |
| Check API access, error codes and operation recovery | [Fabric Plan REST operations](references/plan-rest-api.md) |
| Check which parts a definition needs and what each must contain, or add writeback, inserted-row, scenario, row-template, approval or cube records | [Definition part layout](references/definition-part-layout.md), [part contracts](references/definition-part-contracts.md) |
| Route a business request to a worked recipe | [Adaptive business authoring](references/adaptive-business-authoring.md), [five use-case recipes](references/five-usecase-recipes.md) |
| Apply mandatory defaults to a new application | [Application defaults](references/application-defaults.md), [Home layout fit](references/home-layout-fit.md), [report presentation defaults](references/report-presentation-defaults.md), [native typography](references/native-typography.md) |
| Keep an authored definition sound and repair consumers | [Planning integrity](references/planning-integrity.md), [consumer repair](references/consumer-repair.md), [filter context](references/context-intelligence.md) |
| Configure sheet measures and embedded dashboards | [Planning measures](references/planning-measures.md), [presentation](references/planning-presentation.md). Super Filters in a top band use dropdown mode; Super Filters in a left rail use hierarchy mode. |
| Build decomposition and organization trees, or cover every dashboard visual type | [Intelligence visual type coverage](references/intelligence-visual-types.md). A tree shows only where the tenant's tree switch is on. |
| Plot IBCS recipe charts (C01–C13) or stacked charts, or build an IBCS page with a Matrix table, message title, footnotes or the IBCS Plan theme | [IBCS charts and dashboards](references/ibcs-charts.md). Writes chart templates, bindings and the IBCS chart theme with its scenario and variance colors, not the other IBCS chart styling. Set the Plan theme only on explicit request. |
| Reuse a saved view as a reference definition | [Saved view reference](references/saved-view-reference.md) |
| Plan over time | [Forecast](references/forecast-authoring.md), [roll-forward balances (short default)](references/roll-forward-authoring.md), [formula equality](references/formula-equality.md). Only for full worked cases: [formula principles](references/roll-forward-formula-patterns.md) and [worked cases](references/roll-forward-formula-patterns-part-02.md). |
| Connect or author PowerTable data | [PowerTable modes](references/powertable.md), [lookup source metadata](references/powertable-lookup-source-metadata.md), [SQL definition discovery](references/sql-definition-discovery.md), [deferred connections](references/maintenance-deferred-connection.md). `powertable-table` builds verified existing tables and approved `sqldb-cli` from-scratch results with the product column defaults and All users row access. Forms and Automations use public Plan definition parts (`powertable-features`). Approver-user assignment and private file/template/semantic workload routes have no public API and remain unavailable. |
| Connect other sources | [InfoBridge](references/infobridge-construction.md), [planning-source identity](references/infobridge-planning-identity.md), [connected construction](references/connected-construction.md) |
| Read OneLake values and query consumers | [Linked values](references/onelake-linked-values.md), [query consumers](references/onelake-query-consumers.md) |
| Design input and allocations | [Editability](references/input-editability.md), [numeric constraints](references/numeric-input-constraints.md), [anchor measures](references/anchor-measures.md), [anchor business cases](references/anchor-business-cases.md), [measure-weighted distribution](references/measure-weighted-distribution.md) |
| Bind and aggregate measures | [Measure sources](references/measure-source-bindings.md), [numeric Values](references/numeric-column-values.md), [dimension leaf keys](references/dimension-leaf-keys.md), [dimension hashing](references/dimension-hashing.md), [storage context](references/storage-context.md), [totals](references/planning-totals-defaults.md) |
| Review forecasts | [Actuals versus forecast](references/actual-forecast-review.md), [forecast time intelligence](references/forecast-time-intelligence.md) |
| Format a grid or chart | [Column presentation](references/planning-column-presentation.md), [measure display](references/measure-display-defaults.md), [conditional formatting](references/conditional-formatting.md), [integrated variance](references/integrated-variance.md), [chart filters](references/chart-visual-filters.md) |

Machine-readable resources (not required reading): [discovery catalog](assets/catalog/module-routing.json), [capability gaps](assets/catalog/api-contract-gaps.json), [header metrics](assets/fixtures/arial-header-metrics.json), [preservation manifest](assets/preservation-manifest.json).
