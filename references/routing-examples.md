> v25 CF: discover CONDITIONAL-FORMATTING or F15; read [conditional-formatting.md](conditional-formatting.md). New report specs support sheet.conditionalFormatting directly.

> v16: Read [adaptive-business-authoring.md](adaptive-business-authoring.md)
> before choosing features. Interpret business meaning, compose patterns and
> record parameters and dependencies with `plan-intent`. The five cases are examples;
> `usecase --recipe` accepts supported adaptations. Literal search does not choose
> the business design, and no example rate, date, currency or grain is a default.

> v15: For the five end-to-end business examples, read [five-usecase-recipes.md](five-usecase-recipes.md). `usecase` packages every local and native phase; basic build/provision alone does not execute these complete linked workflows.

# Composing business requests into execution phases

Use these as parameterized business patterns. Field names, horizons, source and
destination IDs come from the current request/model. These are not fixed templates
or additional authorization. For every requested outcome, select a route from
[module-routing.md](module-routing.md) or `python plan.py discover --module <ID>`.

## Intelligence discovery, design and focused edits

For a new Intelligence report or a visual-only change, start with
`python plan.py discover --module INTELLIGENCE` and the
[Intelligence index](intelligence/index.md). Select
[discovery](intelligence/discovery.md) for requirements and field inventory,
[design](intelligence/design.md) for visual decisions,
[authoring](intelligence/authoring.md) for native parts, and
[management](intelligence/management.md) for transport considerations.
The [feature master list](intelligence/feature-master-list.md) routes to the
specific Matrix, chart, KPI, slicer, table or canvas feature.

Use [context-intelligence.md](context-intelligence.md) and the current
[skill contract](../SKILL.md) for executable construction, mandatory application
defaults, supported connected sources and deployment. Loading a feature guide
does not establish an executable factory or authorize a live write.

## Rolling forecast and quarterly review dashboard

Request: Region/Product rows, Year/Quarter/Month columns, sales actuals, rolling
Forecast for January-December 2026, open defaults `COLUMN.ADDMONTH(-1) * 1.1`.
Reuse the Forecast in a Year/Quarter review sheet through From Sheets; add Quarterly
commentary, Forecast-minus-Actuals variance, red negative variance and comparison
charts. Embed both workbenches in Intelligence dashboards.

| Business clause | Guide/module | Execution and dependency |
|---|---|---|
| Monthly Forecast | F09 forecast-authoring | Build Native actuals plus Forecast; closed actuals, exact editable open formula; supported actual date hierarchy. |
| Quarterly review grid | F01/F02 | Build the second owner with Region/Product rows and Year/Quarter columns and its actuals. Do not create a second independent Forecast. |
| Charts and embeds | INTELLIGENCE/F27 | Build prepared column charts, both source owners and dashboards. Import/provision base application before resolving native source/target identities. |
| From Sheets Forecast | F19 forecast-review-execution | Approved external-adapter phase calls `runtime.forecast_review.quarterly_review` to resolve the source column and register its numeric SUM consumer at compatible subset grain. |
| Quarterly commentary | F05 | Same review phase creates a LongText visual measure, `visual_column=false`, with the quarter grain. |
| Variance and negative color | FORMULAS/F15 | Same phase creates Forecast-minus-Actuals and applies the specific negative-variance rule. |
| Variance charts versus actuals | INTELLIGENCE | Same phase binds prepared comparison charts; ordinary visual filters include all assignments. |
| Readable Home | F24 | Provision supported text/cards, or `native home` using `readable_home_layout`; full-width prose when width is unknown. |

```text
python plan.py discover --module F09
python plan.py discover --module F19
python plan.py reference forecast-review-execution.md
python plan.py provision --config destination.json --model current-model.json --spec application.json --run base-run
# Invoke runtime.forecast_review.quarterly_review only through an approved external adapter.
```

Adapt `examples/forecast-review.request.json` for review.request.json; retain the
entire original request in a phase ledger. Never conclude that From Sheets,
commentary or comparison charts are unavailable merely because the base
provisioner does not compose them. Required identity/ETag reads and asynchronous
completion precede dependent writes. Respect the user's requested validation scope.

Time extension belongs under F09. Derive dateAxisBefore/dateAxisAfter-related
metadata from actual supported column levels; retain Year-only or Year/Quarter
grains when requested. Do not apply monthly metadata to every sheet. Forecast
defaults follow the latest reference/UTC policy, nullable closure/aggregate fields,
permissions and distribution-to-children settings. No supplied open default means
None, not an assumed 10% growth rate.

## Quantity to cost: direct reuse or transformation

Request: use sales quantities from Region/Product/Channel in Region/Product cost
planning. Choose F19 direct From Sheets if source/destination dimensions and SUM
semantics are compatible. Query `discover --module F19` and inspect
`runtime.forecast_review.from_sheet_assignment`; the named forecast-review command
is intentionally not a CLI route. The callable is a specific composed workflow,
not a universal direct-link factory.

If workforce needs a cost-center mapping, choose F18 Join then aggregation, or
LOOKUP for a scalar rate retrieval only. Use `construct-bridge planning-source`,
`construct-bridge join` and `construct-bridge query` with current catalogs. For
consolidation, use `construct-native contribution` then `construct-bridge append`.
Import complete graph parts, reconcile runtime identities, reload/poll upstream
jobs, then construct output consumers with `construct-native bridge-consumer`.
Do not pretend a saved graph proves materialization or automatic refresh.

## Maintain master data before planning

Request: onboard products and employees before actual transactions exist. Route to
POWERTABLE, then typed SQL column configuration and LOOKUP where appropriate.
`runtime.powertable_factory.configured_table` returns complete declaration/ALM
parts; it is a Python callable, not a missing feature because there is no top-level
`configure-table` CLI. See powertable-alm-construction.md for assembly and publishing.

Resolve actual connection, SQL artifact, schema, source and key identities. Build
all five parts with the double properties wrapper. If connection is unavailable
and deferred setup is accepted, `prepare-maintenance` retains a visible
uninitialized sheet. Label this state accurately; do not drop requested sheets or
claim that a welcome screen is a working grid. Row insert/update uses separate
explicitly authorized operations.

## Editable controls, allocation and commentary

Request: users set targets and finance allocates them by headcount, while notes and
eligibility remain at their intended grain. Use F05 typed inputs, RULES allocation,
F30 formula eligibility and FORMULAS calculated outputs.

1. `construct-native input` builds each selected input's complete native payload.
2. An approved external adapter resolves the created record and completes its
   async job; the current CLI does not expose this workload route.
3. The same approved adapter supplies visibility/aggregation/format companions.
4. `construct-native rule` builds the supported rule branch and selectors.
5. The rule callable requires the verified engine mount/profile. Do not
   confuse this with application column routes or treat submission as execution.

Weighted allocation is distinct from Forecast's numeric distribute-parent toggle.
Use the allocation guide to choose weights, missing/zero behavior and conservation.

## Named views, approvals and access controls

Request: provide named review views, submit/approve a budget and restrict regions.
Treat this as separate F06/F23/NAVIGATOR, F13 and F25 outcomes. Saved Pivot
construction and Navigator creation are executable; bookmark persistence accepts a
complete capture but universal capture/restore is incomplete. Approval and security
have detailed business/property guides but no complete constructor in this package.
Do not replace them with colored status, slicers or Home role layouts. Report the
specific gap, keep independent work moving and avoid deploying editable/protected
areas whose required controls cannot be established.
