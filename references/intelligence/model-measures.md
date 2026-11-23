## Contents

- [Rules (non-negotiable)](#rules-non-negotiable)
- [Two permission levels](#two-permission-levels)
- [Decision: Fabric Plan first](#decision-fabric-plan-first)
- [Ownership: which measures the skill may edit](#ownership-which-measures-the-skill-may-edit)
- [Workflow: create one measure](#workflow-create-one-measure)
- [Workflow: edit or remove a measure the skill created](#workflow-edit-or-remove-a-measure-the-skill-created)
- [Ledger](#ledger)
- [Troubleshooting](#troubleshooting)
- [Additional details](#additional-details)

<!-- Mode reference for the `fabric-plan-skill` skill. Loaded on demand from `SKILL.md` when a needed measure is missing from the semantic model. -->

# fabric-plan-skill model-measures mode — permission-gated semantic model measures

First check [source scope](core/module-boundaries.md). A measure owned by
Planning, PowerTable or InfoBridge is an integration dependency, not a missing
model measure to synthesize. This release uses only model-backed data.

This mode creates **new** measures in the bound semantic model, and only when
both permission levels are granted and the measure **cannot** be built in
Fabric Plan. Everything else about the semantic model stays read-only.

## Rules (non-negotiable)

1. **Model edit permission first.** Never write to the semantic model unless
   the user has said yes to the model-edit question in this task
   (`model_measure_permission: ask-per-measure`). Default is `none`.
2. **Fabric Plan first.** If the measure can be built in Fabric Plan (see
   [Decision](#decision-fabric-plan-first)), build it there and do **not**
   create it in the semantic model.
3. **Per-measure approval.** Ask for approval of **each** measure separately,
   showing its full definition. One question, one measure. Approval of one
   measure never covers another, and approval from an earlier task does not
   carry over.
4. **Create only.** Never edit, rename, move, reformat, hide, or delete an
   existing model measure, column, table, relationship, or any other object.
5. **Edit only skill-created measures.** The skill may edit or remove a measure
   only if it carries the skill's ownership annotation (below), and only with a
   fresh per-measure approval.
6. **Never overwrite by name.** If a measure with the same name exists anywhere
   in the model, do not create it; propose a different name or use the
   existing measure.
7. **Prove nothing else changed.** Before uploading, `scripts/model_measure.py
   check` must confirm the only differences are skill-owned measures.
8. **Descriptions are required.** Every new measure must have a meaningful,
   nonblank description explaining its business purpose, calculation, units,
   time/filter scope and relevant blank/zero behavior. Base it on inspected
   source-object descriptions and the approved formula, not just an ownership
   label. Include it in approval, persisted model metadata and the ledger.
   Updates must retain a nonblank description and revise it when semantics change.

## Two permission levels

| Level | When asked | Question (one at a time) | Recorded as |
|---|---|---|---|
| 1. Model edit | Discovery Round 0, or the first time a model gap appears in any mode | "Some measures may not exist in the semantic model. If a measure cannot be built inside Fabric Plan, may I create it in the semantic model **<model name>**? I will still ask you before creating each one." Options: **No — keep the model read-only (default)** / **Yes — ask me for each measure** | `model_measure_permission: none \| ask-per-measure` in `_brief/report-spec.md` and the run-state |
| 2. Each measure | Before writing each measure | "Create this measure in **<model name>**?" followed by the measure card (below). Options: **Create it** / **Change it** / **Skip — leave as a model gap** | One ledger entry per measure with `approved: true` and the UTC time |

If level 1 is `none`, list missing measures as **model gaps** and stop there.

**Measure card** shown for level 2:

```markdown
Measure:        Revenue YTD
Home table:     [Fact] Sales           (must already exist)
DAX:            TOTALYTD ( [Revenue], '[Dim] Date'[Date] )
Format string:  #,0
Display folder: Fabric Plan Intelligence
Description:    Cumulative Revenue from calendar-year start through the current date context, retaining non-date filters and Revenue currency and blank semantics.
Why not in Fabric Plan: needs year-to-date accumulation across dates that are not on the visual's axis.
Test result:    DEFINE MEASURE … EVALUATE ROW(...) returned 12,345,678 (query-scoped, nothing written)
```

## Decision: Fabric Plan first

KPI variance icons and sparklines are built-in presentation features
(`KPI-VAR-01`, `KPI-CHART-01`). Never propose or create SVG/image-data measures
to render them. Missing native settings require capture, not a model change.
Evaluate genuinely missing numeric business measures separately under the
normal Fabric Plan-first, description and permission rules.

For Matrix calculations, consult
[the reporting formula reference](features/matrix/formula-syntax.md), including
time intelligence. Its Planning publication location does not make all formulas
Planning-only. Confirm Matrix availability and data context before declaring a
model gap; documentation alone does not prove runtime support or JSON encoding.

Build it in Fabric Plan when any of these cover the need:

| Need | Fabric Plan feature |
|---|---|
| Arithmetic between measures already on the visual (difference, ratio, margin %) | Calculated column `MX-CALC-02`, chart calculated measure `CH-CALC-01`, KPI formula `KPI-FMT-01` |
| Statement lines (Gross Margin = Revenue − COGS) | Calculated row `MX-CALC-01` |
| Running total, % of parent/total, growth, rank, lead/lag | Quick formula `MX-QF-01` |
| AC vs PL/PY/FC difference and % | Variance columns `MX-VAR-01`, chart deviation `CH-DEV-01`, KPI variance `KPI-VAR-01` |
| Different total behaviour (average, last value) | Aggregation `MX-AGG-01` |
| Sign flip, scaling, formatting, renaming | `MX-SIGN-01`, `MX-NUM-*`, `MX-HEAD-01` |

Create it in the semantic model **only** when none of those can produce it,
typically when the calculation:

- needs rows or columns that are not bound to the visual (e.g. distinct counts,
  `CALCULATE` with filters on other dimensions, iterators such as `SUMX` over
  fact columns);
- needs time intelligence across dates the visual does not show (YTD, same
  period last year, rolling 12 months) and neither a supported Matrix reporting
  time function nor a quick formula can access the required context;
- needs semi-additive logic (closing balance, last non-blank);
- is required where visual formulas are not available (e.g. a Super Filter
  measure filter or default-selection Boolean measure).

Write the reason in the measure card ("Why not in Fabric Plan"). If unsure,
build it in Fabric Plan.

## Ownership: which measures the skill may edit

Every measure the skill creates carries this annotation in the model:

```json
{ "name": "fabricPlanIntelligence.createdBy", "value": "fabric-plan-intelligence" }
```

plus `fabricPlanIntelligence.createdOn` (UTC date). Only measures with the
`createdBy` annotation are skill-owned. Everything else is read-only, even if
the user created it the same day.

## Workflow: create one measure

Prerequisites: level 1 = `ask-per-measure`; approved report spec; Contributor
on the workspace and write permission on the semantic model.

1. **Check the name.** Look it up in `_brief/field-registry.md` (all tables). If it
   exists, stop and propose another name or reuse.
2. **Check the home table** exists (prefer the main fact table of the measure).
   Read the home-table and all referenced column/measure descriptions. Resolve
   conflicting definitions and draft the new measure's description before approval.
3. **Test the DAX without writing** (Power BI `executeQueries`, see
   `core/model-inspection.md`):

   ```text
   DEFINE MEASURE '<Home table>'[<Name>] = <expression>
   EVALUATE ROW("value", '<Home table>'[<Name>])
   ```

   It must return without error. Fix and re-test before asking.
4. **Ask level 2 approval** with the measure card. Wait for **Create it**.
5. **Download the model definition as TMSL** (LRO, `core/rest-and-lro.md`):

   ```bash
   az rest --method post --resource "https://api.fabric.microsoft.com" \
     --headers "x-ms-fabric-skill=fabric-planning-api" \
     --url "https://api.fabric.microsoft.com/v1/workspaces/$WS_ID/semanticModels/$MODEL_ID/getDefinition?format=TMSL" \
     --verbose 2>&1 | tee _build/op-model-getdef.log
   # poll → GET /v1/operations/$OP_ID/result --output-file _build/model-source.json
   python -I scripts/plan_def.py unpack _build/model-source.json _build/model-before
   cp -r _build/model-before _build/model-after
   ```

6. **Add the measure** (refuses duplicates, missing tables and blank descriptions):

   ```bash
   python -I scripts/model_measure.py add _build/model-after/model.bim \
     --table "[Fact] Sales" --name "Revenue YTD" \
     --expression "TOTALYTD ( [Revenue], '[Dim] Date'[Date] )" \
     --format "#,0" --folder "Fabric Plan Intelligence" \
     --description "Cumulative Revenue from calendar-year start through the current date context, using the model Date column. Retains non-date filters and Revenue currency and blank semantics."
   ```

7. **Prove only skill-owned measures changed:**

   ```bash
   python -I scripts/model_measure.py check _build/model-before/model.bim _build/model-after/model.bim
   ```

   Any other difference stops the workflow. New or modified skill-owned
   measures without a nonblank text description also fail this check.
8. **Upload** all parts (LRO). `updateDefinition` replaces the whole model
   definition, so pack the full folder:

   ```bash
   python -I scripts/plan_def.py pack _build/model-after _build/model-payload.json
   az rest --method post --resource "https://api.fabric.microsoft.com" \
     --headers "x-ms-fabric-skill=fabric-planning-api" \
     --url "https://api.fabric.microsoft.com/v1/workspaces/$WS_ID/semanticModels/$MODEL_ID/updateDefinition" \
     --body @_build/model-payload.json --verbose 2>&1 | tee _build/op-model-update.log
   # poll until Succeeded; never re-POST after a 202
   ```

9. **Verify:** re-run `INFO.VIEW.MEASURES()` and confirm the measure exists with
   the expected expression and approved description; refresh
   `_brief/field-registry.md`, including description coverage. If description
   readback is unavailable, use authorized metadata readback or report verification
   as incomplete; do not silently mark the measure verified.
10. **Record** the ledger entry, then continue with the next measure (back to step 1).

Measures need no data refresh. If the service reports the model needs
recalculation, tell the user; do not trigger a data refresh without permission.

## Workflow: edit or remove a measure the skill created

1. Confirm the measure has the `fabricPlanIntelligence.createdBy` annotation in the
   downloaded `model.bim`. If not, **refuse** and explain it is not skill-owned.
2. Show the current and proposed definitions, including descriptions; ask level 2
   approval for this change. Update the description when purpose or logic changes.
3. `python -I scripts/model_measure.py update …` (or `remove …`). The script
   refuses any measure without the annotation.
4. `check`, upload, verify, and update the ledger exactly as in creation.
5. Before removing, search the Plan definition for references to the measure
   (`Measure[<name>]` in `pivotAssignments`); remove or replace those bindings first.

## Ledger

Keep `_brief/model-measure-ledger.json` (template `assets/model-measure-ledger.json`):

```json
{ "model": { "workspaceId": "<id>", "modelId": "<id>", "modelName": "<name>" },
  "permission": { "model_measure_permission": "ask-per-measure", "grantedOn": "<UTC>" },
  "measures": [
    { "name": "Revenue YTD", "table": "[Fact] Sales", "action": "created",
      "expression": "TOTALYTD ( [Revenue], '[Dim] Date'[Date] )",
      "description": "Cumulative Revenue from calendar-year start through the current date context, retaining non-date filters and Revenue currency and blank semantics.",
      "whyNotFabricPlan": "YTD across dates not on the axis",
      "approved": true, "approvedOn": "<UTC>", "operationId": "<id>", "verified": true } ] }
```

Never record user names or emails in the ledger.

## Troubleshooting

| Symptom | Fix |
|---|---|
| 403 on `updateDefinition` | No write permission on the model; report it and keep the gap |
| `getDefinition?format=TMSL` rejected | Stop; report that the model cannot be exported as TMSL. Do not hand-edit other formats |
| `check` reports other differences | Do not upload; the download or edit changed something else; start again from a fresh download |
| Measure name already exists | Use the existing measure or propose a new name; never overwrite |
| Description missing or blank | Supply the approved business description; do not upload until the check and description readback pass |
| DAX test fails | Fix the expression; never upload an untested measure |
| Plan shows "fields no longer available" | A bound measure was renamed/removed; restore or rebind |

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

These notes refine the steps above. They never relax the permission levels,
per-measure approval, Fabric Plan-first decision or skill-ownership rules.

- **TMSL `formatString`:** omit the key when no format is needed. Setting it
  to `null` or `""` broke the model import with a conversion error for a
  required string [confirmed]. `model_measure.py add` already omits it when
  `--format` is absent; never pass an empty `--format` to `update`.
- **TMSL `expression`:** native model exports store multi-line DAX as an array
  of line strings [saved]. Keep the convention of the downloaded model for
  measures the skill writes; never reformat measures it does not own.
- **Step 3 test context:** a bare `EVALUATE ROW` has no ambient filter
  context, which is what a KPI card without a date filter sees. Date-dependent
  measures (year-to-date, period shifts) can return blank there, and an
  unanchored prior-year shift can return nearly the unshifted value, showing a
  meaningless near-zero variance [confirmed]. Treat a blank or near-identical
  result as a finding: explain it in the measure card, re-test under the
  report's intended date and scenario context, and name the sheet filter the
  measure depends on.
- **Scenario leakage:** in models with a scenario dimension, a measure that
  does not filter the scenario explicitly can mix actual, plan and forecast
  rows; this was the most frequent reconciliation failure [confirmed]. Put the
  scenario filter in the DAX or document the required sheet filter, and
  reconcile a known total before asking for approval.
- **Reuse before creating:** when a requested measure is absent, first look for
  an existing measure that genuinely satisfies the
  metric contract (same scenario and period scope,
  unit and sign). Prefer it over a new date-restricted measure, never relabel a
  different calculation, and never bind a placeholder.
