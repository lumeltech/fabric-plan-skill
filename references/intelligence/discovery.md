## Contents

- [Must/Prefer/Avoid](#mustpreferavoid)
- [Examples of When to Use](#examples-of-when-to-use)
- [Required Operating Rules](#required-operating-rules)
- [Dependency Checklist](#dependency-checklist)
- [Round Structure](#round-structure)
  - [Round 0 — Setup and Model Resolution](#round-0--setup-and-model-resolution)
  - [Round 1 — Audience and Job](#round-1--audience-and-job)
  - [Round 2 — Model Inventory and What Can Be Built](#round-2--model-inventory-and-what-can-be-built)
  - [Round 3 — Narrative and Sheet Plan](#round-3--narrative-and-sheet-plan)
  - [Round 4 — Design Identity, Accessibility, and Delivery](#round-4--design-identity-accessibility-and-delivery)
- [Additional details](#additional-details)

<!-- Mode reference for the `fabric-plan-skill` skill. Loaded on demand from `SKILL.md` when the request matches the `discovery` mode. Structure adapted from microsoft/skills-for-fabric powerbi-report-cli (MIT). -->

# fabric-plan-skill discovery mode — Intelligence Sheet report discovery

> **Required continuation.** After this file, open
> [discovery-part-02.md](discovery-part-02.md) before producing
> `_brief/report-spec.md`.

This mode orchestrates the start of a new Intelligence Sheet report on an
**existing** semantic model:

**Define -> Inspect -> Propose -> Spec -> Approve -> (design -> authoring -> management)**

## Must/Prefer/Avoid

### MUST

- Read [module boundaries](core/module-boundaries.md). Propose only
  semantic-model-backed data in this release; mark cross-module requests
  blocked until integration, not as unsupported by the Fabric Plan product.
- Inspect the live semantic model (read-only) and persist
  `_brief/field-registry.md` before scoping visuals.
- Inventory all tables, columns and measures, read their available descriptions,
  and use documented business meaning to guide report scope and bindings.
- Give the user a concrete **"what can be built"** proposal from the model:
  candidate sheets, Matrix layouts, KPI cards, charts, and slicers, each linked
  to feature IDs.
- Ask focused clarification questions one at a time.
- Lock `_brief/report-spec.md` and get explicit approval before implementation.
- Route design decisions through `design` mode and definition mechanics through
  `authoring` mode.
- Load [session design](design/session-theme.md) before proposing layouts.
  Reuse one theme, button/navigation style and page-layout system for all reports
  in this session; supplied user design takes precedence.

### PREFER

- Infer obvious answers from the prompt, the model, an existing plan, or
  earlier rounds instead of re-asking.
- Propose only features whose files exist in the reference index.
- Treat user-supplied screenshots, report links and examples as feature
  references only. Map each visible element to a feature file through the
  [reference index](index.md); never reuse their names, figures, theme or
  layout. Missing fields and uncaptured encodings remain explicit gaps.
- Before proposing visuals, resolve grain, units, scenario and period
  definitions, denominators, favorability and status rules from model
  descriptions.
- For Super Filter requirements, open the [slicer index](features/slicers/_index.md).
  Propose only relevant calendar, facet, hierarchy, search or analytical
  controls; resolve data grain and selection semantics before promising
  interactions.
- Offer the IBCS report template among report shapes (it needs scenario
  measures); apply IBCS only if the user chooses it.
- Treat publishing as optional and only proceed when approved.
- Never assign a theme or layout from report type, industry or audience; use
  the user/session design choice, with custom options available.

### AVOID

- Writing to the semantic model in this mode, or proposing a model measure for
  something Fabric Plan can compute.
- Proposing visuals that need fields absent from the registry, unless flagged
  as "needs model change" for a semantic-model skill.
- Using this mode for a small edit to an existing Intelligence sheet (use
  `authoring`).
- Building before the user approves the locked spec.

## Examples of When to Use

- "Create a Fabric Plan Intelligence report from the HR Analytics model."
- "What can I build from this semantic model?"
- "Plan an executive dashboard sheet, then build and publish it."
- "Walk me through creating an Intelligence sheet."

Not for: adding one slicer to an existing sheet (`authoring`), a design
critique only (`design`), or publishing an existing definition (`management`).

## Required Operating Rules

1. **Ask one question at a time.** Each round has one primary question and at
   most one follow-up.
2. **Run 3–5 clarification rounds maximum.**
3. **Inventory the model before locking the spec.** Inspect every table, column
   and measure and its available description. A supplied schema is provisional
   context, not proof of complete live metadata or current field closure.
4. **Check dependencies explicitly** (table below). Do not assume `az` access,
   `executeQueries` permission, or a target workspace.
5. **Produce one locked `_brief/report-spec.md` before building.**
6. **Ask for approval before implementation.** If the request also says build
   or publish, persist the spec, ask for approval, and stop. Do not load
   `authoring`/`management`, write definition files, or call Fabric write APIs
   until a later reply approves.
7. **When approved, continue end to end:** design brief (if not locked) →
   authoring → validation → optional publish (only if delivery says so).
8. **Local stays local unless publishing is approved.**
9. **Do not re-ask known answers.** Capture them in working notes and move on.

## Dependency Checklist

| Dependency | Purpose | Required when |
|---|---|---|
| `az` CLI signed in | All REST calls | Always |
| Read/Build on the semantic model + `executeQueries` enabled | Model inspection | Always (discovery) |
| Contributor on the target workspace | Create/update the Plan item | Publishing only |
| Python 3 | `scripts/plan_def.py`, `scripts/build_index.py` | Authoring and validation |
| Native sample definition (template plan or readback) | Starting point and feature encodings | Authoring |
| Write permission on the semantic model | Create new measures (only if the user allows it) | `model-measures` only |
| Other module skills (integration pending) | Planning, InfoBridge, PowerTable, blend measures | Not enabled; record dependency rather than creating or binding their data |

If a dependency is missing, continue discovery and mark the affected phase as
blocked or manual. Do not pretend it is available.

## Round Structure

### Round 0 — Setup and Model Resolution

Goal: identify the semantic model and the target plan.

| Entry mode | The user is starting from |
|---|---|
| `Live Connected Model` | A semantic model in a Fabric/Power BI workspace (link, ID, or name) |
| `Existing Plan` | An existing Fabric Plan item whose binding gives the model |
| `No Model` | Raw data or an idea only |

If unclear, ask: *"Which semantic model should this Intelligence report use?"*

**`Live Connected Model`** — resolve to `{workspaceName, workspaceId,
modelName, modelId}` using `core/model-inspection.md` § Resolve the model.
Ask the user when a name or GUID is ambiguous (kind unknown, zero matches,
several matches).

**`Existing Plan`** — resolve the plan by list + JMESPath, run `getDefinition`
(management mode, read-only), read `definition.json →
semanticModelReference`, and resolve the model tuple from it. Record existing
sheet names so new sheets do not collide. Run the Data pane field check on
the existing definition (`plan_def.py fields … --registry …`) and report any
field the plan uses that the model no longer has.

**`No Model`** — out of scope for this release. This skill currently needs a
semantic model; the product also supports other sources. Record the dependency
and resume when a model exists or module integration has been implemented.

**Model-measure permission (ask once, in this round).** Ask exactly:

> Some measures may not exist in the semantic model. If a measure cannot be
> built inside Fabric Plan, may I create it in the semantic model
> **<model name>**? I will still ask you before creating each one.

1. No — keep the model read-only (default)
2. Yes — ask me for each measure

Record the answer as `model_measure_permission: none | ask-per-measure`. Never
assume yes. See `model-measures.md`.

Working notes:

```markdown
Dependency status:
- Model-measure permission: none | ask-per-measure
- az login / tenant:
- Semantic model: <name> (<id>) in <workspace> (<id>)
- executeQueries:
- Target plan: new | existing <name/id>
- Publishing requested:
- Native sample available:
```

### Round 1 — Audience and Job

Summarize when already clear; otherwise ask, one at a time.

> Who is this report primarily for?

1. Executives / leadership — concise KPIs, trends, risks, decisions
2. Finance / FP&A — statements, variance to plan, drill to detail
3. Analysts — exploration, comparisons, Top N, tables
4. Operators — monitoring, exceptions, status
5. Planners — reporting on model-backed plan/budget measures (live input deferred)

> What should the report help them do?

1. Understand the overall story
2. Track performance against plan / prior year
3. Find outliers or opportunities
4. Compare entities or segments
5. Prepare a recurring business review (paginated / export)
6. Produce financial statements (income statement, balance sheet, cash flow)
7. Analyze plan versus actual using model measures (live scenarios require integration)

For financial statements, resolve the account hierarchy and line roles, sign
conventions, period flows versus balance snapshots and per-share units. Candidate
features: financial templates (`MX-TPL-02`), calculated rows (`MX-CALC-01`),
invert sign (`MX-SIGN-01`), totals (`MX-TOT-01`) and header/footer (`MX-HF-01`).

Capture:

```markdown
Audience:
Primary purpose:
Tone:
Success criteria:
```

### Round 2 — Model Inventory and What Can Be Built

Goal: inspect, then **propose**. This is the core of discovery mode.

1. Run the INFO queries from `core/model-inspection.md` and write
   `_brief/field-registry.md` (all tables/columns/measures and descriptions,
   scenario tags, relationships, cardinality for slicer candidates).
   Record description coverage and retrieval gaps; distinguish original
   descriptions from inferred grain, roles and business rules.
2. Summarize for the user:

```markdown
Facts:        table, grain, keys, key measures
Dimensions:   date, geography, org, product, customer, account …
Measures:     <count> total — AC: …, PL: …, PY: …, FC: …, ratios: …
Hierarchies:  Region › Country › City; Year › Quarter › Month …
Context:      description coverage; documented KPI definitions, units, grain,
              exclusions and time basis; conflicts or missing metadata
Risks:        high-cardinality fields, inactive relationships, measures that
              should not be summed, missing date table, blank members
```

3. Present the **What can be built** proposal (template in
   [discovery-part-02.md](discovery-part-02.md) § What-can-be-built proposal):
   sheet ideas, Matrix layouts, KPI cards, chart picks, slicers, and gaps.
   Mark each item with its feature IDs and one of: **ready**, **Fabric Plan
   measure** (built as a visual measure), or **model measure needed** (only
   when Fabric Plan cannot compute it; created later only with permission).
4. Infer the first-build scope from the prompt and answers. Ask a scope
   question only when the boundary is unclear or too broad, using options
   built from the proposal:

> The model supports revenue, margin, and headcount with plan and prior year.
> For the first build, should we focus on the executive overview, or also
> include the regional variance Matrix sheet?

```markdown
First-build scope:
- inferred from: <prompt | answer | model>
- included now:
- deferred:
```

### Round 3 — Narrative and Sheet Plan

Consult `design` mode for analytical purpose and reuse the session's page-role
layouts. Only when establishing the session profile, present 2–3 layout options,
**IBCS report template** and **Other**, marking one `(Recommended)`. Do not
reselect layouts for each report or iteration in the same session.

> Which report shape should we use?

**IBCS report template** builds pages from the IBCS chart templates C01–C13
(`CH-IBCS-01`) and table templates T01–T05 (`MX-TPL-04`) with the strict IBCS
theme (flexible only if the user accepts deviations). Choosing it is the user's
IBCS opt-in: load `ibcs/ibcs-rules.md` and set `ibcs: true`. It needs an actual
measure plus a plan, prior-year or forecast measure; if the model lacks them,
say so in the option rather than hiding it.

Then draft the sheet list:

```markdown
Proposed sheets:
1. <Sheet> — archetype — purpose — visuals (Matrix / chart / KPI / slicer) — fields/measures — feature IDs
```

Capture interactions:

- Global slicers (sync across sheets via `syncSlicerConfig`) vs sheet slicers
- Slicer type per field (date slider, calendar, facet, hierarchy, search)
- Cross-filter vs highlight between visuals (edit interactions)
- Drill-down / drill-through, bookmarks, navigation buttons
- Cross-module/embedding requests as deferred dependencies, not build placements

### Round 4 — Design Identity, Accessibility, and Delivery

Consult [session design](design/session-theme.md). Follow supplied design
details or reuse the session profile. If neither exists, use the question tool
for a few design/layout/color bundles, **Use my design file** and **Other**,
including button and navigation treatments, and persist the choice. Use my
design file asks for the location of a design Markdown (`.md`) file and follows
it as the supplied design. Include Help and Info controls. When the model has
scenario measures and IBCS was not already chosen as the report shape, offer
**IBCS theme** separately; it is used only if the user picks it. Do not repeat
resolved design questions.

> What should this report feel like?

Ask delivery only if unclear:

> Where should the finished report end up?

1. Validated local definition only (no publish)
2. New Plan item in an existing workspace
3. Add sheets to an existing Plan item
4. Build locally first, decide publishing later

Defaults applied unless overridden:

- WCAG AA contrast on every text/background pair; colour is never the only cue.
- Searchable dropdown slicers for high-cardinality fields; tiles only for short lists.
- Bounded default date range and one top-level member for large grids.
- Detail Matrix below summary visuals; consistent interactions on every sheet.
- Alt text / descriptive titles on every chart and KPI card.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- **Prompt reading.** Before Round 1, note the audience, business decision,
  required pages, comparison basis, time horizon and deployment scope; keep
  mandatory requirements apart from suggested aesthetics.
- **Scope size.** With no sheet count in the prompt, two to five sheets is a
  reasonable start; reproducing one reference page may need only one.
- **Conflicts.** Current requests and explicit corrections outrank historical
  examples; surface equally current conflicting instructions and ask.
- **Learning is not approval.** Explaining a feature or learning from a
  reference, screenshot or export is read-only work answered with its
  evidence limits; it never approves a build, a publish or a model change.
- **Round 2 depth.** Add measure classification, the connectivity matrix and
  sampling checks (model inspection);
  summarize them in the optional Model Brief
  (part 2).
- **Round 3 interactions.** A page slicer on a scenario or version field must
  not remove the comparison a visual depends on (for example actual versus
  plan); keep those visuals out of its scope.
