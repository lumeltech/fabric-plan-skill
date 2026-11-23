## Contents

- [What-can-be-built proposal](#what-can-be-built-proposal)
- [Design Contract Gate](#design-contract-gate)
- [Locked Report Spec Output](#locked-report-spec-output)
- [Required acceptance checks](#required-acceptance-checks)
- [Approval Gate](#approval-gate)
- [Implementation After Approval](#implementation-after-approval)
- [Anti-Patterns](#anti-patterns)
- [Additional details](#additional-details)

<!-- Mode reference for the `fabric-plan-skill` skill. Continuation of discovery.md. Open this file directly from the skill reference index. -->

# Discovery mode - Part 2

Continuation of `discovery.md`.

## What-can-be-built proposal

Present this after Round 2 inspection. Keep it to one screen; link feature IDs
so authoring can load the right files later.

```markdown
## What you can build from <Model>

### Sheet ideas
1. **Executive overview** — KPI cards (Revenue AC vs PL, Margin %, Headcount),
   trend chart by month, variance by region. Features: KPI-CARD-01, CH-LIB-01, MX-VAR-01
2. **Regional performance Matrix** — rows Region › Country, columns Year › Month,
   values AC, PL, ΔPL, ΔPL%; data bars on ΔPL. Features: MX-LAY-01, MX-CF-02, MX-VAR-01
3. **Product mix** — Top 10 + Others by revenue, contribution %. Features: MX-SRT-03, CH-LIB-01

### Slicers
- Date: `[Dim] Date[Month]` → date slider / month-range calendar (SF-DATE-01/02)
- Region hierarchy: Region › Country → hierarchy slicer (SF-HIER-01)
- Product category (12 members) → facet tiles (SF-FACET-01)
- Customer (8,400 members) → searchable dropdown only (SF-FACET-01, SF-FEAT-02)

### Measures ready to use
- AC: Revenue, Cost, Margin · PL: Revenue Budget · PY: Revenue PY · Ratios: Margin %

### Measures built in Fabric Plan (no model change)
- Margin % = Margin / Revenue → calculated column (MX-CALC-02)
- ΔPL, ΔPL% → variance columns (MX-VAR-01)

### Model measures needed (only if you allow model edits; each asked separately)
- Revenue YTD — only if Matrix reporting time functions cannot cover the
  required date context → permission-gated model measure

### Gaps this skill will not fix
- No forecast data → FC comparisons unavailable
- No sort column for Account → needs a model column (columns are never created)

### Optional
- IBCS report template/theme is available because AC/PL/PY measures exist (offered as a report shape).
```

Rules: only list features that exist in the index; classify each measure as
ready / Fabric Plan measure / model measure needed; propose a model measure
only when Fabric Plan cannot compute it; never create columns, tables, or
relationships, and never change existing model objects.
For proposed Matrix calculations, consult
[Matrix formula syntax](features/matrix/formula-syntax.md) before classifying
time intelligence as a model gap. Exclude Planning-only formula contexts.

## Design Contract Gate

Before writing the spec, the design contract must exist:

- If the user supplied enough design input (sheets, visuals, layout intent),
  use the **fast path**: read `design/session-theme.md` and
  `design/design-brief.md`, follow the supplied design and fill the contract.
- Otherwise run `design` mode for each sheet and capture its `Design Brief:`
  YAML.

Required in the contract:

Report type does not determine theme or layout. `archetype` may be `Custom`;
reference screenshots are not supplied design instructions unless the user
explicitly asks to reproduce them.

- `generated_by: fabric-plan-intelligence`, `contract_version: 1`
- `design_identity` (tone, signature, `ibcs: true|false`)
- `session_theme` (resolved shared profile); Help and Info actions/placements
  or explicit user opt-out
- one `sheets[]` entry per sheet with archetype, `layout_contract` (canvas,
  grid regions, placements), and `space_audit`
- every visual placed in a named region; Super Filter position, chosen regions
  and overflow behavior recorded in `super_filter_layout` (or `none` with reason)
- a sheet title element; no placeholder text

## Locked Report Spec Output

Persist one file, `./_brief/report-spec.md`. Markdown sections for humans plus
one fenced YAML block, which is authoritative. Template:
`assets/report-spec-template.md`.

Sections:

1. **Report identity** — plan name, new vs existing plan, audience, purpose, delivery.
2. **Semantic model binding** — entry mode, workspace name/ID, model name/ID,
   binding form (`legacy` copied from an existing plan, or `portable`).
3. **Field registry** — path to `_brief/field-registry.md`, capture timestamp.
4. **User decisions and constraints** — scope, sheet count, interactivity,
   design direction, IBCS yes/no, publishing, data caveats,
   `model_measure_permission` (none / ask-per-measure).
5. **Narrative** — core story, key questions answered.
6. **Design identity** — tone, signature, IBCS flag.
7. **Sheet plan** — per sheet: archetype, purpose, visuals (kind, fields,
   measures, feature IDs), slicers and interactions.
8. **Measures** — Fabric Plan visual measures to build; model measures
   proposed (name, home table, DAX, why not in Fabric Plan), each still needing
   its own approval; gaps the skill will not fix.
9. **Canonical design contract** — the YAML block.
10. **Implementation notes** — template/native sample to start from,
    feature encodings still unverified, validation plan, publishing boundary, risks.

## Required acceptance checks

Before asking for approval, confirm:

1. Every field and measure in the sheet plan resolves in the field registry.
2. Every feature ID exists in `references/intelligence/feature-master-list.md`.
3. Every sheet has an archetype, a layout contract, and a title element.
4. Slicer types match cardinality (no tile slicer over 50 members).
5. Variance visuals name both comparison measures.
6. IBCS flag is `false` unless the user chose IBCS.
7. Unverified feature encodings are listed with a capture plan.
8. Delivery target and publishing permission are explicit.
9. Model gaps are listed, not silently dropped.
10. Every proposed model measure states why Fabric Plan cannot compute it, and
    none is proposed when `model_measure_permission` is `none`.

## Approval Gate

When the user wants to see the design first, build the mockup described in the
[dashboard build playbook](design/dashboard-playbook.md#3-mock-up-and-approve)
before asking; the approval then covers both the spec and the mockup.

Ask exactly one question:

> **Approve this report spec so I can start building?**

1. Approve
2. Revise audience/purpose
3. Revise scope/sheet plan
4. Revise design/delivery

Do not enter `authoring` or `management` until the user approves in a later reply.

## Implementation After Approval

1. Re-read `_brief/report-spec.md` and `_brief/field-registry.md`.
2. Refresh the registry if the model changed since capture.
3. If `model_measure_permission` is `ask-per-measure` and the spec lists model
   measures, switch to `model-measures` and create them **one at a time, each
   with its own approval**. Skipped measures stay gaps; adjust the visuals.
4. Switch to `design` only if the contract is incomplete.
5. Switch to `authoring`: start from the native template, add sheets and
   visuals, apply features, run `plan_def.py validate`. For a multi-page
   report, publish a pilot page first and clone the rest from its user-saved
   readback ([dashboard build playbook](design/dashboard-playbook.md)).
6. Capture native samples for any unverified encoding the spec needs.
7. If delivery includes publishing, switch to `management`: create or update the
   Plan item, poll the LRO, read back, and re-validate.
8. Report exactly which layers passed: static validation, API acceptance,
   readback, and (user-confirmed) UI rendering.

## Anti-Patterns

| Anti-pattern | Instead |
|---|---|
| Proposing a "Forecast" chart when no FC measure exists | List as a model gap |
| Creating a model measure for Margin % | Build it in Fabric Plan (calculated column) |
| Creating several model measures under one approval | Ask for each measure separately |
| Tile slicer on a 5,000-member field | Searchable dropdown or hierarchy slicer |
| One sheet with 20 visuals | ≤ 12 data visuals per sheet; split into sheets |
| IBCS applied because the data "looks financial" | Offer IBCS; apply only on request |
| Summing ratio measures in totals | Mark ratios; use measure aggregation settings |
| Re-asking the audience the prompt already gave | Record it in working notes |

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Optional Model Brief

Summarize the Round 2 inventory for the user and the spec. Keep these tables
in the report spec or a separate brief file, **not** in
`_brief/field-registry.md`, whose Markdown reader treats table rows as fields.

```markdown
## Model Brief - <model name>
Source: <what was read>; confidence: high | medium | low

### Facts
| Table | Grain | Key dimensions | Notes |

### Measures
| Measure | Table | Unit | Additivity | Polarity | Scenario | Time intel | Role | Format |

### Dimensions and hierarchies
| Table | Key columns | Hierarchy | Cardinality | Notes |

### Connectivity
| Measure group | <dimension> | <dimension> | ... |

### Domain signals detected
### Gaps and risks
### Assumptions to verify
```

For very large models, list only what the report will use plus a count of
the rest. Classification and connectivity rules are in
model inspection.

### Domain signals

Signals suggest sheet ideas; they never mandate theme or layout.

| Signal | Typical evidence |
|---|---|
| Scenario/version | Scenario or version members (actual, plan, forecast) or separate AC/PL/FC measures |
| Chart of accounts | Account hierarchy, account type, sign or reverse-sign flag |
| Organisation | Entity, company, business unit, cost center, department |
| Commercial | Product, customer, channel, region, price and volume measures |
| Workforce | Employee, position, grade, FTE, headcount, hires, leavers |
| Cash and balance sheet | Balance measures, receivables, payables, inventory, DSO/DPO/DIO |
| Supply chain | Demand, supply, stock, lead time, fill rate, item, location |
| Projects/capex | Project, WBS, capex budget, commitments, spend |
| Currency | Currency dimension, FX rates, reporting-currency selector |

Planning-writeback signals are module dependencies; see
module boundaries.

### Sheet-plan extensions

Optionally record per sheet: the business decision it supports, its
navigation position, a question-to-visual mapping (question → exact fields
and measures → visual family → feature IDs), grain, units and favorable
direction per visual, date and scenario scope, and acceptance checks with
evidence gaps. Move unsupported questions to model gaps instead of proposing
visuals for them.

### Additional acceptance checks

- Sheet and registered-visual counts fit the documented per-item limits
  (validation layers).
- Every measure–dimension pair on a visual is connected, or the exception is
  stated.
- Semi-additive measures are shown at period end, not summed across time.
- Period labels (MTD, YTD, full year) name real period calculations
  (metric contract).
- Business-critical metrics have a metric contract and acceptance cases, or
  are listed as pending.

After implementation, report each layer with the statuses in
validation layers.

### Additional anti-patterns

| Anti-pattern | Instead |
|---|---|
| A different measure renamed MTD or YTD | A real period calculation over the same metric |
| Scenario page slicer that removes the plan comparison | Keep comparison visuals out of its scope |
| A measure sliced by an unconnected dimension | Check the connectivity matrix; drop or fix the pair |
| Treating a reference-learning request as build approval | Ask for explicit approval of the locked spec |
| Carrying every feature from earlier reports into a new one | A small, coherent report for the workflow; reuse principles and tested configurations, not a whole old report |
