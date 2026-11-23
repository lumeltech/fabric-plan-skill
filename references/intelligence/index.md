# Intelligence reference index

Intelligence Sheet references only. Files named `part-XX` continue the named topic. Other Fabric Plan modules own separate namespaces; feature IDs here are Intelligence-local.

## Using this library in fabric-plan-skill

Start with the current [skill contract](../../SKILL.md) and
[module routing](../module-routing.md), or run
`python plan.py discover --module INTELLIGENCE` from the skill root.
Use the mode guide for the requested phase, then the
[feature master list](feature-master-list.md) and relevant area index below.
Read linked `part-02` continuations when required; do not load every feature.

These references are integrated guidance, not a separate installed skill.
The latest application defaults, supported connected bindings and public
deployment contract take precedence over retained standalone release notes.
Use the shipped [runtime](../runtime-guide.md), not historical `scripts/`
commands, and keep `_brief/` and `_build/` task data outside the skill root.
See [module boundaries](core/module-boundaries.md) for ownership and current
execution routes. Qualify feature IDs as `intelligence:<ID>` in cross-module
records without changing their local IDs or evidence tags.

### Mode Guides

- [`authoring-part-02`](authoring-part-02.md)
- [`authoring`](authoring.md)
- [`design`](design.md)
- [`discovery-part-02`](discovery-part-02.md)
- [`discovery`](discovery.md)
- [`management-part-02`](management-part-02.md)
- [`management`](management.md)
- [`model-measures`](model-measures.md)

### Core

- [`core/cross-module-blend`](core/cross-module-blend.md)
- [`core/definition-structure`](core/definition-structure.md)
- [`core/invariants`](core/invariants.md)
- [`core/metric-contract`](core/metric-contract.md)
- [`core/model-inspection`](core/model-inspection.md)
- [`core/module-boundaries`](core/module-boundaries.md)
- [`core/native-samples`](core/native-samples.md)
- [`core/product-architecture`](core/product-architecture.md)
- [`core/rest-and-lro`](core/rest-and-lro.md)
- [`core/upstream-references`](core/upstream-references.md)
- [`core/validation-layers`](core/validation-layers.md)

### Design

- [`design/accessibility`](design/accessibility.md)
- [`design/anti-patterns`](design/anti-patterns.md)
- [`design/archetypes/analytical-canvas`](design/archetypes/analytical-canvas.md)
- [`design/archetypes/comparative-benchmark`](design/archetypes/comparative-benchmark.md)
- [`design/archetypes/executive-summary`](design/archetypes/executive-summary.md)
- [`design/archetypes/narrative-story`](design/archetypes/narrative-story.md)
- [`design/archetypes/operational-monitor`](design/archetypes/operational-monitor.md)
- [`design/chart-selection`](design/chart-selection.md)
- [`design/color`](design/color.md)
- [`design/dashboard-playbook`](design/dashboard-playbook.md)
- [`design/dashboard-standards`](design/dashboard-standards.md)
- [`design/design-brief`](design/design-brief.md)
- [`design/design-families`](design/design-families.md)
- [`design/design-system-part-02`](design/design-system-part-02.md)
- [`design/design-system`](design/design-system.md)
- [`design/domain-playbooks`](design/domain-playbooks.md)
- [`design/interactivity`](design/interactivity.md)
- [`design/layout`](design/layout.md)
- [`design/pre-flight-checklist`](design/pre-flight-checklist.md)
- [`design/report-inspiration`](design/report-inspiration.md)
- [`design/session-theme`](design/session-theme.md)
- [`design/typography`](design/typography.md)
- [`design/visual-craft`](design/visual-craft.md)

### IBCS (opt-in only — load when the user asks for IBCS)

- [`ibcs/ibcs-rules-part-02`](ibcs/ibcs-rules-part-02.md)
- [`ibcs/ibcs-rules`](ibcs/ibcs-rules.md)

### Features (one file per feature)

Open the area index, then only the feature files the report needs. Human review list: [`feature-master-list`](feature-master-list.md) (also `.csv`). Template for new features: [`features/_template`](features/_template.md).

- [`features/matrix`](features/matrix/_index.md) — Matrix (55 features)
- [`features/slicers`](features/slicers/_index.md) — Slicers (Super Filter) (25 features)
- [`features/charts`](features/charts/_index.md) — Charts (Intelligence chart library) (47 features)
- [`features/kpi`](features/kpi/_index.md) — KPI cards (7 features)
- [`features/table`](features/table/_index.md) — Table (4 features)
- [`features/canvas`](features/canvas/_index.md) — Canvas, sheet, and interactions (20 features)
