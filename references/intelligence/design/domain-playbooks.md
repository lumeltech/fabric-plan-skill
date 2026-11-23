## Contents

- [Use and precedence](#use-and-precedence)
- [Finance playbooks](#finance-playbooks)
- [Operations playbooks](#operations-playbooks)
- [Cross-cutting finance rules](#cross-cutting-finance-rules)

<!-- Design topic for the `fabric-plan-skill` skill. Optional analytical starting points merged from the companion Intelligence authoring library; report type never mandates theme or layout. -->

# Domain playbooks

Merged from the companion Intelligence authoring library. Additive only:
session design, chart selection and
the other design topics take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

## Use and precedence

**Optional (companion default):** finance and operations playbooks (F1–F10,
O1–O3) as starting points for report questions and visual choices; they apply
only when the user or session design selects them and never override the
session theme, supplied designs, report-inspiration guidance or IBCS opt-in.
A playbook describes analytical content only: report type never mandates
theme, palette, navigation or layout, and the session's page-role layouts
place the recipe.

- Use a playbook only when its **Requires** signals exist in the field
  registry; optional items extend it only if present.
- Never fill a recipe slot with a measure the model lacks: drop the slot or
  record a model gap under the model-measures rules.
- Recipes are question maps, not permission to invent measures or filters.
- Scenario shorthand: AC actual, PL plan or budget, FC forecast, PY prior year.

## Finance playbooks

**F1 P&L performance.** Requires an account dimension with hierarchy or
groups, an amount measure and date; optional scenarios, entity, cost centre
and product. Questions: how did the top line, margins and profit land, which
lines moved most against PY or PL, is margin improving? Recipe: a KPI strip of
the top-line measures that exist, each with Δ against the best available
comparison; a statement Matrix with the account hierarchy on rows and AC,
comparison, Δ and Δ% columns (`MX-TPL-02`, `MX-VAR-01`); monthly AC against
PY or PL for the top line; the largest variances by account group or entity
as sorted or variance bars. Watch: subtotals reconcile to their components and
follow the sign convention; margins are non-additive; avoid a sheet of
disconnected cards.

**F2 Plan vs actual and variance.** Requires AC and PL (measures or scenario
members) on the same grain, and date; optional variance measures, entity, cost
centre and account. Questions: are we on plan year to date, where is the
variance and is it favourable, is it timing or real? Recipe: one comparison
KPI card per distinct metric with AC, PL, Δ and Δ% inside it where supported,
not several cards for one metric (`KPI-VAR-01`); a waterfall bridge from PL to
AC by account group or entity (`CH-LIB-02`); sorted variance bars by cost
centre or entity (`CH-LIB-27`); monthly AC against PL columns with variance,
plus a YTD cumulative line only if a YTD measure exists. Watch: plan may cover
every month while actuals stop at the last closed month, so compare like
periods; polarity follows the account type.

**F3 Forecast and rolling forecast.** Requires FC (measure, scenario member or
version) and AC; optional versions, PL and PY. Questions: what is the
full-year outlook against plan, how did the forecast move between versions,
how accurate was the last one? Recipe: a full-year outlook as AC for closed
months plus FC for open months only if a model measure combines them
(otherwise AC and FC side by side, stated as such); outlook against PL and PY
as KPI cards with Δ; FC by version only if versions exist; accuracy only if an
accuracy or error measure exists. Watch: never stitch AC and FC inside a
visual unless a feature file documents it; make forecast periods visually
distinct with the session's forecast style.

**F4 Opex and cost-centre management.** Requires an expense amount, cost
centre or department, and date; optional expense category, PL, headcount and
vendor. Questions: who is over plan, what is the run rate, which categories
drive cost growth? Recipe: plan consumption by cost centre (bar with target or
variance bars); spend trend by category (line, or stacked columns with no more
than five categories); a detail Matrix of cost centre by category with AC, PL
and Δ. Watch: lower is better; many cost centres need Top N with a search
slicer.

**F5 Revenue, sales and margin.** Requires revenue plus product, customer or
region, and date; optional volume, price, cost, margin, discounts, channel, PL
or PY. Questions: where does revenue come from and grow, which products or
customers drive margin, is it price, volume or mix? Recipe: a KPI strip
(revenue, margin %, volume as available) against PY or PL; contribution as a
sorted bar by product or region (treemap only for part-to-whole with at most
20 tiles); monthly revenue against PY; a price-volume-mix bridge only if
separate effect measures exist or a feature file documents the calculation.
Watch: average price is non-additive; customer dimensions are often
high-cardinality.

**F6 Cash flow and working capital.** Requires cash-flow or balance measures
(cash, receivables, payables, inventory) with date; optional days measures,
cash-flow categories and entity. Recipe: a period-end cash position trend; a
cash-flow waterfall by category if categories exist; working-capital days as
KPI cards with trend. Watch: balances are semi-additive; never compute days
metrics in the design.

**F7 Balance sheet.** Requires balance measures and an account hierarchy with
asset, liability and equity types; optional PY or PL balances. Recipe: a
period-end balance-sheet Matrix with Δ against the prior period; key ratios
only if measures exist. Watch: never sum balances across months; confirm that
the selected period shows the closing balance.

**F8 Workforce and headcount.** Requires a headcount or FTE measure, an
organisation dimension and date; optional hires, leavers, attrition, personnel
cost, grade, location and planned headcount. Questions: are we staffed to
plan, where is attrition high, what does headcount cost? Recipe: headcount AC
against PL by department; a period-end headcount trend; hires against leavers
as paired columns; cost per FTE only if a measure exists. Watch: headcount is
period-end; attrition % is non-additive; keep sheets at aggregate level unless
asked, because person-level detail may be sensitive.

**F9 Scenario comparison.** Requires a scenario or version dimension with two
or more members, or scenario measures; optional driver measures (price,
volume, rate). Questions: how do outcomes differ across scenarios, which
drivers matter most? Recipe: clustered columns or small multiples by scenario
on a shared axis; Δ against the base scenario. Watch: a sheet-level
single-select scenario slicer removes cross-scenario visuals, so scope it per
visual or use a comparison selector the model provides. Driver input belongs
to embedded Planning, not enabled in this release.

**F10 Capex and project portfolio.** Requires a project dimension with budget
and spend or commitment measures; optional status, phase, owner and
completion %. Recipe: a portfolio KPI strip (approved, committed, spent); spend
against budget by project as sorted variance bars; a status Matrix with
conditional formatting.

## Operations playbooks

**O1 Demand, supply and S&OP.** Requires demand and supply or inventory
measures, item or product, location and date; optional forecast demand, fill
rate, lead time and safety stock. Recipe: a demand against supply trend;
period-end inventory position by location; an exception Matrix for items below
safety stock only if a threshold measure or column exists.

**O2 Sales pipeline and commercial operations.** Requires a pipeline amount,
stage and date; optional win rate, quota, sales owner and region. Recipe:
pipeline by stage (funnel only for monotone stages, otherwise bars); quota
attainment by owner as bars with a target; a pipeline trend.

**O3 Operational KPI monitoring.** Requires operational measures with target
or threshold measures. Recipe: status tiles with target context; a trend per
KPI; an exception Matrix; data freshness when a refresh or as-of field exists.

## Cross-cutting finance rules

- **Comparison choice.** Use the comparisons the model supports, in this order
  of usefulness for performance review: PL (are we on plan?), FC (where will
  we land?), PY (are we growing?). Show at most two comparisons per visual.
- **Notation.** Use the session's scenario styles; IBCS notation applies only
  when the user asks for IBCS.
- **Period logic.** Compare like with like: YTD to the last closed period;
  full year only with an outlook (AC plus FC) measure.
- **Polarity by account type.** Revenue, profit and cash in: higher is better.
  Costs, expenses, cash out and days sales outstanding: lower is better.
- **Totals.** Take subtotals from model measures, hierarchy levels or approved
  calculated rows (`MX-CALC-01`); never sum ratios.
- **Units.** Use one currency scale per sheet (K or M) and state it in the
  subtitle.
- **Plan input.** Sheets where users enter or revise plans belong to embedded
  Planning, not enabled in this release.
