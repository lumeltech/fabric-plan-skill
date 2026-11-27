# Reproduce the five business applications in a fresh session

## Contents

- [Reproducibility contract](#reproducibility-contract)
- [Business request -> complete recipe](#business-request---complete-recipe)
- [Fresh-session commands](#fresh-session-commands)
- [Phases that must not be omitted](#phases-that-must-not-be-omitted)
- [Feature-to-guide-to-command map](#feature-to-guide-to-command-map)
- [Evidence and completion](#evidence-and-completion)

## Reproducibility contract

Use this guide when a request matches sales targets, workforce merit, expense
budget, rolling forecast/quarterly review or connected currency/risk outlook.
The package contains each functional prompt, its complete symbolic business
spec, post-import dependency graph and styling defaults. No chat history, old
report export, local task folder or source checkout is required.

Read the adaptive business authoring guide before choosing features. The five
cases are worked examples: interpret business meaning, compose patterns and record
parameters and dependencies with `plan-intent`. `usecase --recipe` accepts
supported adaptations. Literal search does not choose the business design, and no
example rate, date, currency or grain is a default. The mandatory baseline in the
application defaults guide applies to every case. For external Context and storage
grain, read the storage context guide; for artifacts whose metadata is stored in
OneLake, read the onelake linked values guide.

The intended repeatable output is the same sheets, measures, formulas, grain,
filters, controls, chart comparisons, colors, headers, Home and layout. It is not
byte-identical JSON: new Plan IDs, visual IDs, input IDs and timestamps must
be newly created/resolved. Current semantic-model data and the installed native
renderer determine values and final rendering. Do not promise pixel-identical
runtime behavior without checking that environment. User-added reference sheets,
manual input values and unrelated later edits are not part of these creation recipes.

Fractional limits use hidden formula bounds at the same fractional units rather
than decimal static bounds, and AverageLeaf inputs default to distribution on. The
recipe JSON `normalizationNotes` records these intentional choices.

## Business request -> complete recipe

| Business request | Case ID | Final structure | Features beyond the common baseline |
|---|---|---|---|
| Start monthly regional sales targets from prior-year sales and flag shortfalls | `01-sales-targets` | 1 Planning sheet, 1 dashboard, 2 comparison charts | Measure-based input default; actual minus target; negative-variance formatting |
| Plan employee merit from 0% to 15% and show salary cost impact | `02-workforce-merit` | 1 Planning sheet, 1 dashboard, 2 comparison charts | AverageLeaf/distribution; fractional percentage formatting; hidden 0.15 limit; salary times employee FX; proposed/base comparison |
| Budget expenses with 3% inflation, adjustments and monthly explanations | `03-expense-budget` | 1 Planning sheet, 1 dashboard, 2 comparison charts | Editable inflation, hidden fractional limit, budget and remaining-budget formulas; LongText explanation; overspend formatting |
| Roll monthly sales forecast into quarterly review and commentary | `04-rolling-review` | 2 Planning sheets, 2 dashboards, 4 comparison charts | Jan-Dec 2026 open period in UTC; `COLUMN.ADDMONTH(-1) * 1.1`; native Forecast; same/subset-grain From Sheets; quarterly variance and LongText commentary |
| Connect local estimates, risk/FX adjustments and a quarterly executive outlook | `05-currency-risk` | 3 Planning sheets, 3 dashboards, 6 comparison charts | Ordered multi-sheet links and dependent formulas; FX multiplier; risk/opportunity inputs; quarterly baseline comparison and commentary |

All five include visible native Home, rich Planning descriptions/legends,
source-role colors, semantic slicers, integrated variance charts, owner-preserving
Planning embeds, current source identities, leaf-ID storage, full grid formatting,
dynamic column expansion, saved hierarchy expansion, column-total handling,
layout sizing and native-measure filter cards.

## Fresh-session commands

Run from the installed `fabric-plan-skill` directory. Requirements are Python 3.11+ and
Node 24+ for the bundled compressed-payload/HTTPS adapters. Use `python` or your
platform's equivalent; set `FABRIC_PLAN_NODE` and, when needed on managed Windows,
`FABRIC_PLAN_HTTP_NODE` to your Node executable. These paths are local prerequisites,
not paths copied from the original author's computer. The HTTP adapter uses
system trusted roots; credentials are environment variables and never files.

Start by running the discovery step in the skill instructions on the business
phrase, for example "workforce merit salary cost".

```text
python scripts/plan.py usecase list
python scripts/plan.py usecase show --case 02-workforce-merit
```

For an authorized destination, copy
`assets/examples/five-usecases/destination.example.json` to `destination.json` and
replace every synthetic identity with current metadata.
It holds synthetic environment, workspace, model and connection identities, and
no token or Plan IDs. Check that it is the user's intended destination. Set `FABRIC_TOKEN` securely in the process
environment. A config Boolean is not a substitute for the user's deployment request.
For another destination, resolve its actual endpoints, workspace, model URL and
PowerBIDatasets connection; do not change hostnames by string substitution.

```text
python scripts/plan.py usecase model --config destination.json --run runs/model
python scripts/plan.py usecase build --case 02-workforce-merit --model runs/model/current-model.json --run runs/merit

```

`model` reads metadata through the public semantic-model API, not model values.
Its selected parser supports normal tab-indented TMDL. These five recipes use
numeric measures; omitted measure return types are represented as Double. For
other return types or TMDL/TMSL branches, supply the complete current catalog in
the format described in the runtime guide. The actual connection identity is a
separate required input; it is not inferred from a model's source SQL connection.

`build` compiles the base application locally and records the remaining phases in
`phase-ledger.json`: create/import, the recipe's linked, formula, commentary and
comparison extensions, and role-specific Home publication. No `usecase`
subcommand writes to a workspace. Author the pending extensions into the
definition, then publish the reviewed definition with `api create`, as the runtime
guide describes, under the user's deployment authorization. The default name is
the business title plus Unix seconds; `--name` chooses a different explicit name.
Reuse a run directory only to resume the same build: a changed recipe, model or
name is rejected rather than rebuilt.

To build all five, run `usecase build` once per case with separate run directories:
`runs/sales`, `runs/merit`, `runs/expense`, `runs/rolling`, and `runs/currency`.
The original short prompts are in `assets/examples/five-usecases/business-prompts.txt`.
Do not require a customer to paste a technical specification when these recipes
match the requested outcome. A changed requirement should be reflected in an
explicit adapted spec/graph using the same helpers, not hidden agent assumptions.

## Phases that must not be omitted

1. Resolve model fields, numeric units, keys and calendar grain. Compile the base
   definition with Planning owners, registered numeric inputs/formulas/Forecast,
   enabled Home and visible dashboard declarations.
2. Apply the recipe's Planning year filters, percentage formatting and base
   negative-variance rules. Forecast source retains 2025 and 2026 for the previous
   month's actual; the review and other cases select 2026.
3. Author the quarterly or ordered links, formulas and commentary in dependency
   order, resolving every source owner and column identity from this build. Never
   reuse IDs from another report or invent a completion or chart data.
4. Apply rich headers, source-role colors and all five column-presentation defaults
   after the complete measure catalog exists.
5. Resolve each chart's current and baseline from that catalog. Native DAX measures
   keep PowerBI identity; only produced measures are From Sheets. Select integrated
   variance and reconcile filter cards. Keep business comparison direction.
6. Publish once through the public create route, with page-local embedded geometry,
   dashboard visibility and Home visibility in the definition. Keep the receipt and
   wait for the operation to finish. Role-specific Home content stays local.
7. Export the new Plan and compare it with the intended definition.

`usecase build` performs phases 1 and 2 and lists the rest as pending. It does not
open a UI, calculate values or run post-save validation. On an uncertain write
response or an unresolved operation, keep the run and reconcile it against a fresh
export before continuing. Do not blindly replay a whole deployment.

## Feature-to-guide-to-command map

| Feature | Guide | Execution used by the recipe |
|---|---|---|
| Complete business flow | This guide | `usecase show/build`; `runtime.usecases`; `api create` to publish |
| Exact model and source binding | the measure source bindings guide | `resolve-measure-binding`; `registered_measure` |
| Inputs, AverageLeaf and whole static bounds | the numeric input constraints guide | Numeric/Forecast constructors, hidden bound formulas |
| Forecast and time-axis grain | the forecast authoring guide | `construct.planning`; native Forecast records |
| From Sheets, commentary, variance | no bundled guide; `forecast-repair` | `resolve-measure-binding`; `runtime.forecast_review` library; formula/input factories |
| Percentage and matrix styles | `scripts/plan.py format-matrix` | `format-matrix`; `compile_formatting` |
| Negative variance | `scripts/plan.py integrated-variance` | `apply_negative_variance` |
| Leaf identity storage | the dimension leaf keys guide | `leaf-key-mapping`; constructor key groups |
| Home, headers, source colors and embeds | the application defaults guide; the planning presentation guide; the context intelligence guide | `build_application`; `apply_presentation`; public sheet geometry; public Home visibility |
| Visible columns and native measure cards | the planning column presentation guide | `planning-column-presentation` |
| Integrated variance | the integrated variance guide | `comparison_chart`; `integrated-variance` |

## Evidence and completion

`recipe-contract.json` records symbolic dependency and output-shape checks;
`phase-ledger.json` separates the constructed local base from pending phases.
These are construction records, not proof of rendered behavior or calculated
values. The offline tests exercise the five base builds and symbolic graphs; they
do not publish the recipes. Keep that limitation explicit.
