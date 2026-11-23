---
name: fabric-plan-skill
description: Build, validate and update Microsoft Fabric Plan applications from business requirements and a semantic model. Use for Planning sheets, forecasts, connected planning, PowerTables and embedded Plan dashboards, not standalone Power BI reports.
---

# Fabric Plan

Use the Python CLI from this skill's directory. Use a separate task directory for inputs, generated definitions and readbacks. Python 3.11+ and Node.js 24+ are required for the full offline workflow.

## Choose the scope before building

- **New Plan:** translate the requested business grain, time horizon, inputs, measures and calculations into sheets. Include the Home definition, dashboard coverage, Arial and Page Navigators for a complete application.
- **Extension or repair:** start from a fresh export. Preserve unknown fields, unrelated part bytes, existing identities, input values, formulas, conditional formatting and Forecast settings. Change only the requested surfaces and their dependencies.
- **Inspection or design:** do not mutate the workspace. Distinguish a proposed change from a saved or verified one.

## Execution

1. Identify the target model and workspace. Use current model metadata for field names, types, hierarchy levels and aggregation. Do not deploy the synthetic fixtures. If a required source, identity or field cannot be resolved, identify the missing input rather than inventing one.
2. Use `python plan.py discover "business request"` to narrow the choice of topic, or select a guide below. Read only the topic needed. `python plan.py --help` is the inventory of executable commands; use a subcommand's `--help` for its arguments.
3. Construct and validate a local candidate. For example, `python plan.py build --model fixtures/model.json --spec fixtures/finance-spec.json --out /path/to/trial` exercises a synthetic build without credentials. Check required input registrations, formula references, sheet bindings, dashboard geometry and scope coverage before any write.
4. Use only the documented **public Fabric APIs** for live operations. Require the user's explicit destination and write authorization. If a feature has no supported public route (for example, saving a role-specific Home layout), report it as unavailable. Do not call workload endpoints, attempt a token exchange, or substitute UI automation. A local constructor or example is not a live write capability.
5. Export the result from the destination and compare it with the intended changes. Preserve native numeric identities as decimal strings. For existing Plans use saved placement identities, not sheet order. An embedded grid may hide its source sheet in Explorer, but its owner identity must remain usable for formulas and bindings.
6. Report what was built, validated locally, persisted, and verified interactively as separate outcomes. A saved definition does not prove that navigation, input or rendered layout works. After a failed write, read back current state before retrying; do not assume rollback.

## Packaging and publication boundary

Distribute only tracked, reviewed planning instructions, runtime, schemas, references, reusable examples, fixtures, tools and their licences. Never package the whole working folder. Keep task briefs, handoff notes, model exports, report samples, credentials and generated output outside the distribution. To publish a Plan, send only its validated public definition and required report resources, not this skill.

## Planning references

Choose a reference directly; the list is a menu, not a reading sequence.

| Task | Guides |
|---|---|
| Build, validate or update a definition | [Runtime guide](references/runtime-guide.md) |
| Configure sheet measures and embedded dashboards | [Planning measures](references/planning-measures.md), [presentation](references/planning-presentation.md) |
| Plan over time | [Forecast](references/forecast-authoring.md), [roll-forward balances](references/roll-forward-authoring.md), [roll-forward formula patterns](references/roll-forward-formula-patterns.md), [formula equality](references/formula-equality.md) |
| Connect sources | [InfoBridge](references/infobridge-construction.md), [PowerTable](references/powertable.md) |
| Design input and allocations | [Editability](references/input-editability.md), [numeric constraints](references/numeric-input-constraints.md), [anchor measures](references/anchor-measures.md), [measure-weighted distribution](references/measure-weighted-distribution.md) |
| Bind and aggregate measures | [Measure sources](references/measure-source-bindings.md), [numeric Values](references/numeric-column-values.md), [dimension leaf keys](references/dimension-leaf-keys.md), [storage context](references/storage-context.md), [totals](references/planning-totals-defaults.md) |
| Review forecasts | [Actuals versus forecast](references/actual-forecast-review.md), [forecast time intelligence](references/forecast-time-intelligence.md) |
| Format a grid or chart | [Column presentation](references/planning-column-presentation.md), [measure display](references/measure-display-defaults.md), [conditional formatting](references/conditional-formatting.md), [integrated variance](references/integrated-variance.md), [chart filters](references/chart-visual-filters.md) |

Machine-readable resources (not required reading): [discovery catalog](references/module-routing.json), [header metrics](references/arial-header-metrics.json), [preservation manifest](references/preservation-manifest.json).
