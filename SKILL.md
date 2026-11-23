---
name: fabric-plan-skill
description: Build, validate and update Microsoft Fabric Plan applications from business requirements and a semantic model. Use for Planning sheets, forecasts, connected planning, PowerTables and embedded Plan dashboards, not standalone Power BI reports.
---

# Fabric Plan

Use the Python CLI from this skill's directory. Use a separate task directory for inputs, generated definitions and readbacks. Python 3.11+ and Node.js 24+ are required for the full offline workflow.

## Choose the scope before building

- **New Plan:** build from the current model and business spec. Enable public Home visibility; role-specific cards, layout and priority can be prepared locally but not published. For a complete application, check each requested sheet against the spec, each Planning grid's dashboard coverage, Arial on authored text, and a Page Navigator with resolved destinations on every dashboard.
- **Extension or repair:** patch a fresh, complete export of the named Plan; do not rebuild it from the model. Preserve unknown fields, unrelated part bytes, identities, formulas and settings outside the requested change and its dependencies. If storage keys or grain must change, establish a supported migration and authorized before/after checks of planner values at the same entity, period and scenario. Stop if required retention cannot be verified.
- **Inspection or design:** do not mutate the workspace. Distinguish a proposed change from a saved or verified one.

## Execution

1. Identify the target model and workspace. Use current model metadata for field names, types, hierarchy levels and aggregation. Do not deploy the synthetic fixtures. If a required source, identity or field cannot be resolved, identify the missing input rather than inventing one.
2. Use `python plan.py discover "business request"` to narrow the choice of topic, or select a guide below. Read only the topic needed. `python plan.py --help` is the inventory of executable commands; use a subcommand's `--help` for its arguments.
3. Construct and validate a local candidate. For example, `python plan.py build --model fixtures/model.json --spec fixtures/finance-spec.json --out /path/to/trial` writes local files without credentials. Before a workspace create or update, check required input registrations, formula references, sheet bindings, dashboard geometry and coverage against the request.
4. Use only the documented **public Fabric APIs**. Export is a live read; create and update require explicit write authorization for the named destination. A new update rechecks the reviewed baseline. Stop on drift. This check is not atomic: coordinate exclusive editing if a concurrent overwrite is unacceptable. If a feature lacks a public route, report it as unavailable; do not substitute workload endpoints, token exchanges or UI automation.
5. Export the result from the destination and compare it with the intended changes. Preserve native numeric identities as decimal strings. Placement identifies where a grid appears; its source owner and measure identify what formulas and bindings consume. Check both using saved identities, not sheet order. Neither check proves stored values survived.
6. Report what was built, validated locally, persisted, and verified interactively as separate outcomes. A saved definition does not prove that navigation, input or rendered layout works. After a failed write, read back current state before retrying; do not assume rollback.

## Packaging and publication boundary

Distribute only tracked, reviewed planning instructions, runtime, schemas, references, reusable examples, fixtures, tools and their licences. Never package the whole working folder. Keep task briefs, handoff notes, model exports, report samples, credentials and generated output outside the distribution. To publish a Plan, send only its validated public definition and required report resources, not this skill.

## Planning references

Choose a reference directly; the list is a menu, not a reading sequence.

| Task | Guides |
|---|---|
| Build, validate or update a definition | [Runtime guide](references/runtime-guide.md) |
| Configure sheet measures and embedded dashboards | [Planning measures](references/planning-measures.md), [presentation](references/planning-presentation.md) |
| Plan over time | [Forecast](references/forecast-authoring.md), [roll-forward balances (short default)](references/roll-forward-authoring.md), [formula equality](references/formula-equality.md). Only for full worked cases: [roll-forward formula patterns](references/roll-forward-formula-patterns.md). |
| Connect sources | [InfoBridge](references/infobridge-construction.md), [PowerTable](references/powertable.md) |
| Design input and allocations | [Editability](references/input-editability.md), [numeric constraints](references/numeric-input-constraints.md), [anchor measures](references/anchor-measures.md), [measure-weighted distribution](references/measure-weighted-distribution.md) |
| Bind and aggregate measures | [Measure sources](references/measure-source-bindings.md), [numeric Values](references/numeric-column-values.md), [dimension leaf keys](references/dimension-leaf-keys.md), [storage context](references/storage-context.md), [totals](references/planning-totals-defaults.md) |
| Review forecasts | [Actuals versus forecast](references/actual-forecast-review.md), [forecast time intelligence](references/forecast-time-intelligence.md) |
| Format a grid or chart | [Column presentation](references/planning-column-presentation.md), [measure display](references/measure-display-defaults.md), [conditional formatting](references/conditional-formatting.md), [integrated variance](references/integrated-variance.md), [chart filters](references/chart-visual-filters.md) |

Machine-readable resources (not required reading): [discovery catalog](references/module-routing.json), [header metrics](references/arial-header-metrics.json), [preservation manifest](references/preservation-manifest.json).
