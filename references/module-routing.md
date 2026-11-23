> v37: Discover **NATIVE-COLUMN-READBACK** for OneLake `dataInputType` / `columnType` readback compatibility and duplicate-safe resumes. See [native-column-readback.md](native-column-readback.md). Reusable repairs must be promoted to the main skill, shared builder, tests and regenerated Copilot package; see [verified-authoring-flow.md](verified-authoring-flow.md).

> v36: Discover ONELAKE-CONSUMERS for **OneLake storage mode**, both From Sheets and From Queries. Read [onelake-linked-values.md](onelake-linked-values.md). Current-catalog resolution is bundled in construction, recipe and comparison phases; missing SQL id/sqlPk does not require a local repair.

> v34: Discover SAVED-VIEW-REFERENCE for native/export bookmark identity, parameter capture gaps, separate Home content and independent PowerTable readers. Read [saved-view-reference.md](saved-view-reference.md).

> v33: discover ONELAKE-CONSUMERS for storage-aware From Queries Values in Planning and Intelligence. See onelake-query-consumers.md. All v32 business-navigation/manual-refresh defaults remain.

> **BUSINESS-NAVIGATION** / **INITIAL-REFRESH** covers duplicate Explorer pages, hiding a Planning sheet embedded in an Intelligence dashboard, Home card destinations, standalone sheet visibility and optional initial InfoBridge refresh. Read [business-navigation.md](business-navigation.md).

> v31: [Backend-aware metadata recovery](metadata-backend-routing.md). Discover METADATA-BACKEND for feature-specific Fabric SQL/OneLake operations. Resolve only the collection consumed by the operation; no mutation replay or storage migration. Preserve the same artifact and all prior fixes.

> v30: [Measure-weighted distribution](measure-weighted-distribution.md) is now constructible for the captured Column / All dimensions / another Measure / source Row Use Self profile. Discover RULES or weights from another measure; use `construct-native weighted-rule`. Saved configuration is confirmed, not allocation execution. Other reference profiles and bookmark restore remain separate gaps. All prior fixes remain.

> Discover **VERIFIED-AUTHORING-FLOW** for reference-only imports, incomplete imports, planning grid validation, or storage-specific repository errors.

> v29 execution rule: follow [verified-authoring-flow.md](verified-authoring-flow.md). Import supported inputs, formulas, Forecast and CF together. Use documented native phases only; no reference-only staging shortcut or automatic reduced-scope deployment. The original request and import-contract checks remain authoritative. This supersedes older partial-deployment fallback wording.

> v28: For direct numeric columns, implicit measures, missing explicit DAX or default Sum, discover `NUMERIC-COLUMN-VALUES` and read [numeric-column-values.md](numeric-column-values.md). This integrated path covers Planning, cards, comparison charts and automatic dashboards.

> v27 mandatory navigation: every Intelligence dashboard includes a visible native Page Navigator, even when omitted from the prompt. The standard builder reserves space and the public Plan definition carries its complete state. The completion gate rejects missing controls. Read [the navigation contract](navigators.md#mandatory-dashboard-page-navigation-v27). All v26 padding and earlier fixes remain.

> v26 Navigator: discover NAVIGATOR for complete new-dashboard defaults, disabled icon padding and topPadding white-screen errors. Read [the current contract](navigators.md#current-construction-contract-v26).

> v25 CF: discover CONDITIONAL-FORMATTING or F15; read [conditional-formatting.md](conditional-formatting.md). New report specs support sheet.conditionalFormatting directly.

> v21: Planning-source InfoBridge identity is enforced by the bundled builders and pre-write guard. Discover INFOBRIDGE-MAPPING; read [infobridge-planning-identity.md](infobridge-planning-identity.md) for source/query catalogs, transformation lineage and native consumer bindings.

PowerTable lookup/source fixes: discover `POWERTABLE-CONFIG`. Read [powertable-lookup-source-metadata.md](powertable-lookup-source-metadata.md) for key/label chains, destination metadata, read-only columns and scoped repair.

> v20: All reports use content-sized rich-text headers plus a small buffer and
> native row/column hierarchy icons `gmate`, independent of business use case.
> Read [report-presentation-defaults.md](report-presentation-defaults.md) and
> discover REPORT-PRESENTATION. Preserve intentional user overrides.

> v19: Every new Planning grid uses explicit row GT Top, row subtotal Top,
> column GT Left, column subtotal null/OFF. Preserve intentional overrides.
> Read [planning-totals-defaults.md](planning-totals-defaults.md). Measure-based
> roll-forwards recommend Measures in Rows + native Measure Model; discover
> ROLL-FORWARD and read [roll-forward-authoring.md](roll-forward-authoring.md)
> plus the complete supplied [formula reference](roll-forward-formula-patterns.md).

> v18: [measure-display-defaults.md](measure-display-defaults.md) is the default: assigned measure cards stay visible at **All**, with no selected values/ranges. Numeric Planning measures use per-measure Auto (`13: "auto"`). Apply dimension selections only to the dimension card itself; preserve all source bindings and intentional existing filters.

> v17: New editable inputs explicitly default to ReadAndEdit. Business-dependent
> locking uses BasedOnFormula with a real, resolved expression. See
> [input-editability.md](input-editability.md); preserve intentional existing locks.

> v16: Read [adaptive-business-authoring.md](adaptive-business-authoring.md)
> before choosing features. Interpret business meaning, compose patterns and
> record parameters and dependencies with `plan-intent`. The five cases are examples;
> `usecase --recipe` accepts supported adaptations. Literal search does not choose
> the business design, and no example rate, date, currency or grain is a default.

> v15: For the five end-to-end business examples, read [five-usecase-recipes.md](five-usecase-recipes.md). `usecase` packages every local and native phase; basic build/provision alone does not execute these complete linked workflows.

> v14 required default: use native integrated variance for bar/column baseline comparisons. Read [integrated-variance.md](integrated-variance.md) for exact selectors, source-preserving commands and business examples. Ordinary single-series bars are unchanged.

> v13: Read [planning-column-presentation.md](planning-column-presentation.md) for dynamic column expansion, selected sizing/default-total rules and native-measure filter cards. Expansion recovery was user-confirmed; the other defaults were subsequently requested. Preserve all existing input and formula identities.

> 2026-11-14 numeric-input correction: [numeric-input-constraints.md](numeric-input-constraints.md) is authoritative for whole-number static min/max bounds and AverageLeaf parent distribution. Decimal defaults/formulas are separate; preserve existing percentage units and IDs.

# Business request to guide to command routing

This directory covers every F01-F30 module plus cross-cutting workflows. It links
the existing detailed business guides to actual shipped CLI commands and Python
helpers. It does not turn a documented property into a complete creation factory.

Run from the installed skill directory (or use an absolute path to plan.py):

```text
python plan.py discover --list
python plan.py discover "rolling forecast quarterly commentary variance"
python plan.py discover --module F09
python plan.py discover --module POWERTABLE --json
```

Discovery is local and read-only: no credentials, network, report changes or
Codex-specific tools. Search matches business phrases/aliases; it is a lookup aid,
not a semantic classifier. Read the business distinctions before selecting modules.
Use the complete list and related modules when a phrase does not match.

## How to route a request

1. Extract each business outcome, row grain, column grain, editable values, time
   horizon, context and constraints. Read **Interpret the Prompt Before Choosing
   Modules**, **Select Features by Business Distinction** and **Request-Scoped
   Reading Map** in feature-contracts.md when selection is ambiguous.
2. Look up each outcome here, then read only its selected business guide and
   implementation reference. Use the guide to decide whether the feature is needed.
3. Record `request clause -> module/guide -> command or callable -> inputs and
   dependencies -> execution phase -> result`. All requested clauses stay in the
   ledger, including separate helpers and genuine gaps.
4. Compose base build/provision, ALM component construction and post-import native
   phases in dependency order. `workflow.SUPPORTED` describes only the convenience
   provisioner. A prepare-scope omission is not final application coverage when a
   separate helper is listed here. Include that phase before reporting an omission.
5. For a guide-only or unsupported branch, report the precise missing constructor
   and affected outputs; continue independent authorized work. Do not invent flags,
   undocumented API payloads, fake financial values or weaken required security.

Coverage labels identify construction paths, not live/runtime verification.
Commands with current-model.json or request.json placeholders need real resolved
inputs. Do not deploy fixture data. A route without a CLI command is callable-only
and requires an explicitly approved external service-adapter profile; its Python
symbol is shown by `plan.py discover --json`. These workload routes are not public
REST guarantees. Do not add internal asset upload as a public capability. Existing
asset helpers remain implementation evidence outside the recommended public route. Honor explicit no-validation instructions for the report while
still obtaining identities/ETags and completing asynchronous writes.

The latest Forecast, time-extension, filter, PowerTable, Home-fit, identity and
embedding corrections in SKILL.md and their targeted references take precedence
over older general wording in preserved guides. This index does not replace them.

## Module directory

### BUSINESS-INTENT: adaptive business decisions

For different wording, changed requirements or a mixed workflow, first read
[adaptive-business-authoring.md](adaptive-business-authoring.md). Interpret the
business clauses and run `plan-intent` on the resulting brief. It returns relevant
guides, commands, dependency order and unresolved decisions. Use
`python plan.py discover --module BUSINESS-INTENT` for the full command metadata.
This is local routing; it does not infer intent from prose or execute live writes.

`USECASES` and `CASE01` through `CASE05` remain discoverable as worked patterns.
Use `usecase show --out` to export a recipe, or `usecase build/deploy --recipe` for
an adaptation within the supported pipeline. Other modules compose separately;
do not silently discard clauses that do not fit a case.

| Module | Business request example | Execution coverage |
|---|---|---|
| [F01 Layout](#f01-layout) | Show metrics down rows instead of across columns. | partial |
| [F02 Aggregation Settings](#f02-aggregation-settings) | Sum sales but recalculate margin percentages at totals. | integrated |
| [F03 Quick Format](#f03-quick-format) | Show sales in millions and margins as percentages. | partial |
| [F04 Insert Row](#f04-insert-row) | Add a presentation subtotal or custom row to this grid. | guide-only |
| [F05 Insert Column and Typed Inputs](#f05-insert-column-and-typed-inputs) | Add quarterly commentary that repeats by quarter. | separate-phase |
| [F06 Pivot](#f06-pivot) | Switch between region and product planning views while keeping the same inputs. | integrated |
| [F07 Visual Filter](#f07-visual-filter) | Filter only this chart by product. | integrated |
| [F08 Filter Context](#f08-filter-context) | Store independent Budget and Upside inputs using a version selector. | integrated |
| [F09 Forecast including Time Extension](#f09-forecast-including-time-extension) | Create a rolling sales forecast with closed actuals and editable future periods. | integrated |
| [F10 Fiscal Year](#f10-fiscal-year) | Plan an April-to-March fiscal year. | guide-only |
| [F11 Row Model](#f11-row-model) | Author Overtime Hours and Rate rows with distinct business formulas under Salaries. | guide-only |
| [F12 Measure Model](#f12-measure-model) | Organize many measures into expandable Revenue, Cost and Margin groups. | partial |
| [F13 Approval](#f13-approval) | Let department owners submit a plan for finance approval. | guide-only |
| [F14 Formatting](#f14-formatting) | Align the dashboard and make labels and grid text legible. | partial |
| [F15 Conditional Formatting](#f15-conditional-formatting) | Highlight negative Forecast-minus-Actuals variance in red. | separate-phase |
| [F16 Column Style](#f16-column-style) | Use a different supported display style for a planning column. | partial |
| [F17 Writeback](#f17-writeback) | Publish approved planning results to an operational database. | guide-only |
| [F18 InfoBridge](#f18-infobridge) | Join workforce to cost centers and consolidate departmental costs. | separate-phase |
| [F19 Blend / From Sheets](#f19-blend--from-sheets) | Use the monthly Forecast from another sheet in a quarterly review. | separate-phase |
| [F20 Anchor Measures](#f20-anchor-measures) | Business-grain assumptions, hidden repetition with leaf-formula availability, native dimension hashing and first-anchor creation. | partial |
| [F21 Data Pane](#f21-data-pane) | Make the right model fields and linked outputs available for assignments. | partial |
| [F22 Side Panel Filter](#f22-side-panel-filter) | Offer page and global filters while keeping chart filters separate. | partial |
| [F23 Bookmark](#f23-bookmark) | Save named dashboard views and switch back to them. | partial |
| [F24 Home Layout](#f24-home-layout) | Create a legible introduction, forecast instructions and sheet navigation. | separate-phase |
| [F25 Security](#f25-security) | Allow each region to see only its own data and assign author/reviewer roles. | guide-only |
| [F26 Themes](#f26-themes) | Apply a consistent corporate theme across the application. | guide-only |
| [F27 Embedding](#f27-embedding) | Place monthly planning and quarterly review workbenches inside Intelligence dashboards. | integrated |
| [F28 Header Footer](#f28-header-footer) | Add a planning sheet title and explanatory header. | partial |
| [F29 OnChangeFormula](#f29-onchangeformula) | Update a dependent field when a user changes a planning input. | integrated |
| [F30 Allow Input Based on Formula](#f30-allow-input-based-on-formula) | Allow editing only eligible future periods and active products. | integrated |
| [LIFECYCLE Plan lifecycle and deployment](#lifecycle-plan-lifecycle-and-deployment) | Create a new Plan or update an existing report without losing unrelated settings. | integrated |
| [INTELLIGENCE Intelligence charts and dashboards](#intelligence-intelligence-charts-and-dashboards) | Package a forecast in a dashboard with KPIs, slicers and Actuals comparison charts. | integrated |
| [POWERTABLE PowerTable maintenance](#powertable-powertable-maintenance) | Maintain products, employees or valid business combinations before transactions exist. | separate-phase |
| [LOOKUP Advanced Lookup and key/label selection](#lookup-advanced-lookup-and-keylabel-selection) | Retrieve the benefit rate for a department. | partial |
| [RULES Input rules, allocation and distribution](#rules-input-rules-allocation-and-distribution) | Allocate a departmental target to employees using weights. | separate-phase |
| [DIMENSION-ID Dimension ID Mapping](#dimension-id-dimension-id-mapping) | Keep employee inputs stable when employee display names change. | integrated |
| [FORMULAS Formula measures and variance](#formulas-formula-measures-and-variance) | Calculate revenue from volume times price. | integrated |
| [CUBE Cube planning](#cube-cube-planning) | Calculate or enter a measure at an explicit cube breakdown. | partial |
| [NAVIGATOR Page and bookmark navigation](#navigator-page-and-bookmark-navigation) | Mandatory Page Navigator on every Intelligence dashboard; additional buttons/bookmark tabs. | integrated |
| [SCENARIOS Scenarios and sensitivity](#scenarios-scenarios-and-sensitivity) | Explore a downside without changing the saved budget. | partial |

## F01 Layout

**Invoke for:** Show metrics down rows instead of across columns. Make a region/product planning grid readable.

**Read:** [Layout and Measure Placement Authoring](feature-contracts.md), [design-standards.md](design-standards.md).

**Execution:** partial. `python plan.py build --model current-model.json --spec application.json --out draft`

**Inputs/dependencies:** Resolve row/column grain and requested measure orientation.

**Boundaries:** Basic grid and canvas constructors exist; advanced measures-in-rows/tree branches require their exact property contract, not an invented build option.


Related: F14, F27.

## F02 Aggregation Settings

**Invoke for:** Sum sales but recalculate margin percentages at totals. Use different row and column aggregation.

**Read:** [Totals and Aggregation Authoring](feature-contracts.md).

**Execution:** integrated. `python plan.py build --model current-model.json --spec application.json --out draft`

**Inputs/dependencies:** Establish additive, semi-additive or formula semantics per measure.

**Boundaries:** Set aggregation and columnAggregation per measure; nonadditive calculations need their own formula. Advanced total labels remain property-level guidance.


Related: FORMULAS.

## F03 Quick Format

**Invoke for:** Show sales in millions and margins as percentages.

**Read:** [matrix-formatting.md](matrix-formatting.md), [Number Format Authoring](feature-contracts.md), [Number Format Property Inventory](feature-contracts.md).

**Execution:** partial. `python plan.py format-matrix --input examples/matrix-formatting.request.json --out candidate.json`; `python plan.py build --model current-model.json --spec application.json --out draft`

**Inputs/dependencies:** Measure data types, units, currency and exact native format entries.

**Boundaries:** Selected Matrix typography/header/Column Style/ordered-format/size and numeric single-condition CF constructors are shipped. General rule families, Shell/Charts/PowerTable styling and exact hover/selection demands require their own contracts. Native defaults provenance and rendering limits are explicit in matrix-formatting.md.

Example: Make open inputs yellow in read/edit modes and use text-only negative indicators without hiding closed-period colors: format-matrix, resolved scopes and independent target/test IDs.

Related: F14, INTELLIGENCE.

## F04 Insert Row

**Invoke for:** Add a presentation subtotal or custom row to this grid. Add products before actual transactions exist.

**Read:** [Local Insert Rows Versus Business Members](feature-contracts.md).

**Execution:** guide-only. Guide only; no complete creation command is shipped.

**Inputs/dependencies:** Decide local authored row versus persistent business member.

**Boundaries:** No complete standalone Insert Row factory is shipped. Persistent product/employee maintenance routes to PowerTable; authored calculations route to Row Model.


Related: F11, POWERTABLE.

## F05 Insert Column and Typed Inputs

**Invoke for:** Add quarterly commentary that repeats by quarter. Add a checkbox, date or selectable planning assumption.

**Read:** [Input Type and Placement Workflows](feature-contracts.md), [Input and Formula Measure Authoring](feature-contracts.md), [builder-integration.md](builder-integration.md).

**Execution:** separate-phase. `python plan.py construct-native input --input input.request.json --out input.payload.json`

**Inputs/dependencies:** Resolve input type, storage/context grain, native IDs and visual measure versus visual column.

**Boundaries:** Number inputs are composed by build/provision. Other typed inputs are explicit construct/create/register phases. Async creation requires terminal completion before dependent writes.

Example: Quarterly commentary: kind LongText and visual_column=false on a Year/Quarter sheet; a VisualColumn is a different placement.

Related: F29, F30, F08.

## F06 Pivot

**Invoke for:** Switch between region and product planning views while keeping the same inputs.

**Read:** [Pivot View Authoring](feature-contracts.md), [Pivot Business Reconciliation](feature-contracts.md).

**Execution:** integrated. `python plan.py build --model current-model.json --spec application.json --out draft`

**Inputs/dependencies:** Current dimension/measure registry and saved-view scope.

**Boundaries:** Saved Pivot construction/activation exists. It is not complete bookmark capture/restore or data-coordinate migration.


Related: F23, NAVIGATOR.

## F07 Visual Filter

**Invoke for:** Filter only this chart by product. Show every assigned field in the Visual level filter pane.

**Read:** [F07 Visual Filter](feature-contracts.md), [chart-visual-filters.md](chart-visual-filters.md), [consumer-repair.md](consumer-repair.md).

**Execution:** integrated. `python plan.py build --model current-model.json --spec application.json --out draft`; `python plan.py build --model current-model.json --spec dashboard.json --out draft`

**Inputs/dependencies:** Resolve actual semantic dimension or measure assignments and intended filter level.

**Boundaries:** Ordinary visible registrations are separate from hidden evaluation context; preserve selections and nested ID domains.


Related: F08, F22.

## F08 Filter Context

**Invoke for:** Store independent Budget and Upside inputs using a version selector.

**Read:** [Planning Input Context Authoring](feature-contracts.md), [context-intelligence.md](context-intelligence.md).

**Execution:** integrated. `python plan.py build --model current-model.json --spec application.json --out draft`; `python plan.py build --model current-model.json --spec application.json --out draft`

**Inputs/dependencies:** A real context dimension/member catalog and input binding policy.

**Boundaries:** External storage Context stays off Rows/Columns and mirrors input bindings. An ordinary slicer is not version storage or row-level security.


Related: F07, SCENARIOS, F25.

## F09 Forecast including Time Extension

**Invoke for:** Create a rolling sales forecast with closed actuals and editable future periods. Extend the forecast calendar at Year, Year/Quarter or Year/Quarter/Month grain.

**Read:** [forecast-authoring.md](forecast-authoring.md), [Rolling Forecast Authoring](feature-contracts.md), [Forecast Business Examples](feature-contracts.md), [Time extension under Forecast](feature-contracts.md), [forecast-review-execution.md](forecast-review-execution.md).

**Execution:** integrated. `python plan.py build --model current-model.json --spec forecast.json --out draft`; `python plan.py provision --config destination.json --model current-model.json --spec application.json --run run`; `python plan.py forecast-repair --baseline definition.json --input examples/forecast-repair.request.json --out candidate.json`

**Inputs/dependencies:** Resolved actuals semantics, horizon, supported ordered column date levels and any requested open defaults.

**Boundaries:** Use native Forecast. Closed actuals, nullable closure/aggregate defaults, true distribution and UTC/reference policy are retained. Unspecified open defaults are None; requested formula defaults remain editable. dateAxisBefore/dateAxisAfter describe time extension derived from actual hierarchy, not fixed Y/Q/M metadata.

Example: Jan-Dec 2026 open periods: openDefault={"Formula":"COLUMN.ADDMONTH(-1) * 1.1"}; first open month uses preceding closed actuals, then compounds monthly. Do not use on-change or a fixed baseline uplift.

Example: For Year-only or Year/Quarter columns preserve that supported grain; do not inject months or silently reinterpret a requested monthly formula. Consult the hierarchy/formula contract.

Related: F19, F15, INTELLIGENCE.

## F10 Fiscal Year

**Invoke for:** Plan an April-to-March fiscal year.

**Read:** [F10 Fiscal Year](feature-contracts.md), [Supported Date Hierarchies and Labels](feature-contracts.md).

**Execution:** guide-only. Guide only; no complete creation command is shipped.

**Inputs/dependencies:** Model fiscal calendar, year boundary and supported time intelligence mapping.

**Boundaries:** No complete Fiscal Year constructor is shipped. Calendar display labels and native fiscal settings must agree; Forecast date-axis metadata alone is not a fiscal-year configuration.


Related: F09.

## F11 Row Model

**Invoke for:** Author Overtime Hours and Rate rows with distinct business formulas under Salaries.

**Read:** [Row Model Business Authoring](feature-contracts.md), [Authored Row Extension Examples](feature-contracts.md).

**Execution:** guide-only. Guide only; no complete creation command is shipped.

**Inputs/dependencies:** Authored business row hierarchy and row-specific calculation/aggregation semantics.

**Boundaries:** No complete model-template/row factory is shipped. An existing GL hierarchy or measures displayed vertically does not require Row Model.


Related: F04, F12, F01.

## F12 Measure Model

**Invoke for:** Organize many measures into expandable Revenue, Cost and Margin groups.

**Read:** [Measure Hierarchy Authoring](feature-contracts.md), [Measure Hierarchy Evidence and Worked Example](feature-contracts.md).

**Execution:** partial. `python plan.py build --model current-model.json --spec application.json --out draft`

**Inputs/dependencies:** Existing complete measure identities and desired hierarchy/group totals.

**Boundaries:** The low-level Planning constructor can retain an explicit native measureModelConfig; provision does not compose it and there is no business-hierarchy factory. Do not pass invented keys or confuse ordinary input creation with Measure Model.


Related: F01, FORMULAS.

## F13 Approval

**Invoke for:** Let department owners submit a plan for finance approval.

**Read:** [Approval Workflow Authoring](feature-contracts.md), [Worked Functional Patterns](feature-contracts.md), [Editability and Transition Guards](feature-contracts.md).

**Execution:** guide-only. Guide only; no complete creation command is shipped.

**Inputs/dependencies:** Named roles, submission package grain, transitions and effective lock rules.

**Boundaries:** No complete approval lifecycle constructor/transition adapter is shipped. Keep required controls intact; a review page, checkbox or colored status does not implement approval.


Related: F25, F30, RULES.

## F14 Formatting

**Invoke for:** Align the dashboard and make labels and grid text legible.

**Read:** [matrix-formatting.md](matrix-formatting.md), [Grid Appearance Authoring](feature-contracts.md), [design-standards.md](design-standards.md).

**Execution:** partial. `python plan.py format-matrix --input examples/matrix-formatting.request.json --out candidate.json`; `python plan.py build --model current-model.json --spec application.json --out draft`; `python plan.py build --model current-model.json --spec dashboard.json --out draft`

**Inputs/dependencies:** Real canvas/visual dimensions, typography and content volume.

**Boundaries:** Selected Matrix typography/header/Column Style/ordered-format/size and numeric single-condition CF constructors are shipped. General rule families, Shell/Charts/PowerTable styling and exact hover/selection demands require their own contracts. Native defaults provenance and rendering limits are explicit in matrix-formatting.md.

Example: Make open inputs yellow in read/edit modes and use text-only negative indicators without hiding closed-period colors: format-matrix, resolved scopes and independent target/test IDs.

Related: F01, F03, F24.

## F15 Conditional Formatting

**Invoke for:** Highlight negative Forecast-minus-Actuals variance in red. Flag an amount based on commentary or a helper condition.

**Read:** [matrix-formatting.md](matrix-formatting.md), [Conditional Formatting Business Workflow](feature-contracts.md), [forecast-review-execution.md](forecast-review-execution.md).

**Execution:** separate-phase. `python plan.py format-matrix --input examples/matrix-formatting.request.json --out candidate.json`

**Inputs/dependencies:** Target measure, comparison/condition source, detail/total scope and appearance.

**Boundaries:** Selected Matrix typography/header/Column Style/ordered-format/size and numeric single-condition CF constructors are shipped. General rule families, Shell/Charts/PowerTable styling and exact hover/selection demands require their own contracts. Native defaults provenance and rendering limits are explicit in matrix-formatting.md.

Example: Make open inputs yellow in read/edit modes and use text-only negative indicators without hiding closed-period colors: format-matrix, resolved scopes and independent target/test IDs.

Related: F19, F30, FORMULAS.

## F16 Column Style

**Invoke for:** Use a different supported display style for a planning column.

**Read:** [matrix-formatting.md](matrix-formatting.md), [Column Style Authoring](feature-contracts.md).

**Execution:** partial. `python plan.py format-matrix --input examples/matrix-formatting.request.json --out candidate.json`

**Inputs/dependencies:** Native column identity, requested style and compatible type.

**Boundaries:** Selected Matrix typography/header/Column Style/ordered-format/size and numeric single-condition CF constructors are shipped. General rule families, Shell/Charts/PowerTable styling and exact hover/selection demands require their own contracts. Native defaults provenance and rendering limits are explicit in matrix-formatting.md.

Example: Make open inputs yellow in read/edit modes and use text-only negative indicators without hiding closed-period colors: format-matrix, resolved scopes and independent target/test IDs.

Related: F03, F14, POWERTABLE.

## F17 Writeback

**Invoke for:** Publish approved planning results to an operational database.

**Read:** [F17 Writeback](feature-contracts.md).

**Execution:** guide-only. Guide only; no complete creation command is shipped.

**Inputs/dependencies:** Explicit authorized destination, mapping, operation semantics and job completion contract.

**Boundaries:** No general Planning Writeback setup/execution constructor is shipped. PowerTable insert/update adapters cover only that maintenance route. Saving a Plan or refreshing InfoBridge is not external writeback.


Related: POWERTABLE, F18, F13.

## F18 InfoBridge

**Invoke for:** Join workforce to cost centers and consolidate departmental costs. Use transformed sales quantities to calculate supply cost.

**Read:** [infobridge-construction.md](infobridge-construction.md), [Transformation Discovery Inventory](feature-contracts.md), [Connected Planning Design Examples](feature-contracts.md).

**Execution:** separate-phase. `python plan.py construct-bridge planning-source --input source.request.json --out source.json`; `python plan.py construct-bridge query --input bridge.request.json --out bridge.json`; `python plan.py construct-bridge append --input bridge.request.json --out bridge.json`; `python plan.py construct-bridge merge --input bridge.request.json --out bridge.json`; `python plan.py construct-bridge join --input bridge.request.json --out bridge.json`; `python plan.py construct-bridge sql --input bridge.request.json --out bridge.json`; `python plan.py construct-bridge editable-source --input bridge.request.json --out bridge.json`; `python plan.py construct-native contribution --input contribution.request.json --out contribution.json`; `python plan.py construct-native bridge-consumer --input consumer.request.json --out consumer.json`

**Inputs/dependencies:** Source grain/catalogs, transformation order, compatible output types and destination identities.

**Boundaries:** Construct graph/import through supported ALM parts, then resolve IDs and execute dependencies. Saved transformations do not prove materialization or automatic propagation. Direct compatible From Sheets may be sufficient without a pipeline.


Related: F19, LOOKUP, DIMENSION-ID, POWERTABLE.

## F19 Blend / From Sheets

**Invoke for:** Use the monthly Forecast from another sheet in a quarterly review. Sum channel quantities into Region/Product cost planning.

**Read:** [Measures From Sheets Authoring](feature-contracts.md), [Connected Planning Design Examples](feature-contracts.md), [forecast-review-execution.md](forecast-review-execution.md).

**Execution:** separate-phase callable `runtime.forecast_review.quarterly_review`
through an approved external adapter; no current CLI route.

**Inputs/dependencies:** Current source sheet/owner/column catalog, compatible ordered subset dimensions, numeric SUM meaning and time/context compatibility.

**Boundaries:** from_sheet_assignment and quarterly_review provide direct numeric SUM with required companions. Other source kinds/aggregations need their own supported contract. Never invent fine-grain values from a coarse total.


Related: F18, F05, F15, FORMULAS.

## F20 Anchor Measures


Read [anchor-measures.md](anchor-measures.md) for business grain, visibility
without deleting leaf formula values, native keys and executable scope.
[anchor-business-cases.md](anchor-business-cases.md) covers all ten PPT cases and
additional synthetic functional patterns and transfer rules.

Use per-measure `anchor` options in new base reports, `construct-native anchor`
for a scoped local candidate, and the `runtime.anchor_measures.save_anchors`
callable for an authorized
ETag save. [dimension-hashing.md](dimension-hashing.md) defines exact source IDs,
all ordered pivot dimensions and seed-zero XXH3-64. First-anchor construction
needs no donor hash. F20 lists callables, source and examples. Disable/reset and
native runtime behavior remain bounded gaps; no new API is introduced.

## F21 Data Pane

**Invoke for:** Make the right model fields and linked outputs available for assignments.

**Read:** [F21 Data Pane](feature-contracts.md).

**Execution:** partial. `python plan.py build --model current-model.json --spec application.json --out draft`; `python plan.py construct-native bridge-consumer --input consumer.request.json --out consumer.json`

**Inputs/dependencies:** Actual model/source catalogs and correct assignment buckets.

**Boundaries:** Base pane visibility and assignments exist; pane display is not a constructor for missing data sources or arbitrary field metadata.


Related: DIMENSION-ID, F19, F18.

## F22 Side Panel Filter

**Invoke for:** Offer page and global filters while keeping chart filters separate.

**Read:** [F22 Side Panel Filter](feature-contracts.md), [consumer-repair.md](consumer-repair.md), [chart-visual-filters.md](chart-visual-filters.md).

**Execution:** partial. `python plan.py build --model current-model.json --spec application.json --out draft`; `python plan.py build --model current-model.json --spec application.json --out draft`

**Inputs/dependencies:** Explicit visual/page/global scope and current semantic field identities.

**Boundaries:** Base corrected pane casing and ordinary registrations exist. Arbitrary page/global predicates must follow their exact native contracts; do not misuse Context to populate filter cards.


Related: F07, F08.

## F23 Bookmark

**Invoke for:** Save named dashboard views and switch back to them.

**Read:** [Bookmark Business Authoring](feature-contracts.md), [Observed Public Bookmark Snapshots](feature-contracts.md), [builder-integration.md](builder-integration.md).

**Execution:** partial. `python plan.py construct-native navigator --input navigator.request.json --out navigator.json`; the save/placement phase is callable-only through an approved external adapter.

**Inputs/dependencies:** Complete supported capture, current page/visual identities and current ETags.

**Boundaries:** Persistence of a complete capture is executable; universal snapshot construction and restore/application are incomplete. Navigator alone does not create a working saved view.


Related: F06, NAVIGATOR.

## F24 Home Layout

**Invoke for:** Create a legible introduction, forecast instructions and sheet navigation. Show audience-specific Home instructions.

**Read:** [Home Layout Authoring](feature-contracts.md), [home-layout-fit.md](home-layout-fit.md).

**Execution:** separate-phase. `python plan.py provision --config destination.json --model current-model.json --spec application.json --run run`; `python plan.py native home --config destination.json --input home.request.json --run run --label home`

**Inputs/dependencies:** Audience/role IDs, content, navigation targets and known width when available.

**Boundaries:** Text/cards compose automatically; advanced Home phases are separate. Widths are pixels, not percentages: prefer flexible widths and content-driven heights. Asset upload uses a workload application route, not a public API; no new upload command is recommended as a public path.

Example: Stack forecast assumptions and calendar coverage in full-width prose rows when available width is unknown; preserve uploaded image IDs and sheet cards during a scoped edit.

Related: F25, NAVIGATOR.

## F25 Security

**Invoke for:** Allow each region to see only its own data and assign author/reviewer roles.

**Read:** [Security Authoring](feature-contracts.md), [Security Business Patterns](feature-contracts.md), [Separate the Access Layers](feature-contracts.md).

**Execution:** guide-only. Guide only; no complete creation command is shipped.

**Inputs/dependencies:** Explicit identity/role mappings, source RLS, workload access, sheet and feature permissions.

**Boundaries:** No complete security policy constructor/enforcement adapter is shipped. Slicers, Home roles, edit formulas and assignments do not prove RLS. Do not deploy exposed data when a required visibility control is unresolved.


Related: F13, F30, F24.

## F26 Themes

**Invoke for:** Apply a consistent corporate theme across the application.

**Read:** [matrix-formatting.md](matrix-formatting.md), [F26 Themes](feature-contracts.md), [design-standards.md](design-standards.md).

**Execution:** guide-only. `python plan.py format-matrix --input examples/matrix-formatting.request.json --out candidate.json`

**Inputs/dependencies:** Supported native theme scope and user-provided branding.

**Boundaries:** Selected Matrix typography/header/Column Style/ordered-format/size and numeric single-condition CF constructors are shipped. General rule families, Shell/Charts/PowerTable styling and exact hover/selection demands require their own contracts. Native defaults provenance and rendering limits are explicit in matrix-formatting.md.

Example: Make open inputs yellow in read/edit modes and use text-only negative indicators without hiding closed-period colors: format-matrix, resolved scopes and independent target/test IDs.

Related: F14.

## F27 Embedding

**Invoke for:** Place monthly planning and quarterly review workbenches inside Intelligence dashboards.

**Read:** [F27 Embedding](feature-contracts.md), [Observed Embedded Owner and Placement Checks](feature-contracts.md), [context-intelligence.md](context-intelligence.md).

**Execution:** integrated. `python plan.py build --model current-model.json --spec dashboard.json --out draft`; `python plan.py construct-native embedded-planning --input embed.request.json --out embed.json`

**Inputs/dependencies:** One true Planning owner per sheet and current destination runtime IDs/ETags.

**Boundaries:** Preserve source inputs and geometry; the embedding page owns placement overrides. A portable visual GUID is not the runtime visual ID.


Related: INTELLIGENCE, F01.

## F28 Header Footer

**Invoke for:** Add a planning sheet title and explanatory header.

**Read:** [F28 Header Footer](feature-contracts.md).

**Execution:** partial. `python plan.py build --model current-model.json --spec application.json --out draft`

**Inputs/dependencies:** Plain business title/body text and content height.

**Boundaries:** Sheet header text is supported through the header field. General footer and advanced title elements lack a request-level constructor.


Related: F14, F24.

## F29 OnChangeFormula

**Invoke for:** Update a dependent field when a user changes a planning input.

**Read:** [On Change Workflow Authoring](feature-contracts.md), [Cross-Industry Input and Workflow Cases](feature-contracts.md).

**Execution:** integrated. `python plan.py construct-native input --input input.request.json --out input.payload.json`; `python plan.py build --model current-model.json --spec application.json --out draft`

**Inputs/dependencies:** Explicit changed input, target measure identities and supported side-effect formula semantics.

**Boundaries:** Use on_change in build input specs or on_change in input_create; handlers are distinct from forecast open defaults and ordinary formula evaluation. Configuration does not prove event execution.


Related: FORMULAS, F05, F09.

## F30 Allow Input Based on Formula

**Invoke for:** Allow editing only eligible future periods and active products.

**Read:** [Formula-Based Editability Workflow](feature-contracts.md).

**Execution:** integrated. `python plan.py build --model current-model.json --spec application.json --out draft`; `python plan.py construct-native input --input input.request.json --out input.payload.json`

**Inputs/dependencies:** Boolean eligibility formula and its resolved measure dependencies.

**Boundaries:** Use allow_input={BasedOnFormula:...}; this is cell eligibility, not RLS or a submitted/approved lifecycle lock.


Related: RULES, F13, F25.

## LIFECYCLE Plan lifecycle and deployment

**Invoke for:** Create a new Plan or update an existing report without losing unrelated settings. Download and cache a definition for comparison.

**Read:** [Plan Item Lifecycle](feature-contracts.md), [runtime-guide.md](runtime-guide.md).

**Execution:** integrated. `python plan.py api export --config destination.json --run run --label baseline`; `python plan.py decode definition.json --out decoded`; `python plan.py build --model current-model.json --spec application.json --out draft`; `python plan.py provision --config destination.json --model current-model.json --spec application.json --run run`; `python plan.py api update --config destination.json --payload candidate.json --run run --label update`

**Inputs/dependencies:** Current authorized workspace/model/Plan identities, API profile and credentials supplied outside files.

**Boundaries:** Full definitions preserve untouched part bytes. Wait for asynchronous completion; saved response is separate from behavioral validation.


Related: .

## INTELLIGENCE Intelligence charts and dashboards

**Invoke for:** Discover, design, author or maintain Intelligence Sheets; package a forecast in a dashboard with KPIs, slicers and Actuals comparison charts.

**Read:** Start with the [Intelligence index](intelligence/index.md) and select
[discovery](intelligence/discovery.md), [design](intelligence/design.md),
[authoring](intelligence/authoring.md) or
[management](intelligence/management.md) for the requested phase. Use the
[feature master list](intelligence/feature-master-list.md) to reach individual
Matrix, chart, KPI, slicer, table and canvas guides. Read
[Intelligence Dashboard Business Authoring](feature-contracts.md),
[context-intelligence.md](context-intelligence.md),
[chart-visual-filters.md](chart-visual-filters.md) and
[forecast-review-execution.md](forecast-review-execution.md) for the applicable
bundled construction paths.

**Execution:** integrated. `python plan.py build --model current-model.json --spec dashboard.json --out draft`; `python plan.py provision --config destination.json --model current-model.json --spec application.json --run run`

**Inputs/dependencies:** Current semantic/query fields, source owners, meaningful comparisons and complete KPI/chart state.

**Boundaries:** Column charts, KPI cards, slicers, text and embeds are supported. Forecast comparison charts use the separate review phase; advanced chart families are not all compiled. The detailed Intelligence library does not add executable factories or override current application defaults, source identities or API-only deployment. Historical standalone scripts and semantic-model-only release gates are not the integrated skill's execution contract.


Related: F27, F07, F15.

## POWERTABLE PowerTable creation and analysis

**Invoke for:** Maintain products or employees; connect one to five existing
Fabric SQL Database tables; design a PowerTable application from scratch;
analyze one PowerTable sheet; or compare two or three PowerTable sheets.

**Mode map:** Start with the [PowerTable index](powertable/index.md). Select
exactly one mode:

| Mode | Required guides |
|---|---|
| `powertable-existing` | [connect existing tables](powertable/connect-existing-tables.md), [column mappings](powertable/column-mappings.md) |
| `powertable-from-scratch` | [modeling](powertable/modeling.md), [create from scratch](powertable/create-from-scratch.md), [column mappings](powertable/column-mappings.md) |
| `powertable-analysis` | [analyze PowerTable data](powertable/analyze-data.md), [column mappings](powertable/column-mappings.md) |
| `powertable-cross-analysis` | [analyze across sheets](powertable/analyze-across-sheets.md), [analyze PowerTable data](powertable/analyze-data.md), [column mappings](powertable/column-mappings.md) |

Also use [powertable-alm-construction.md](powertable-alm-construction.md),
[maintenance-deferred-connection.md](maintenance-deferred-connection.md) and
[connected-construction.md](connected-construction.md) for the existing
runtime component contracts. The external
[`sqldb-cli`](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli)
companion supplies SQL authoring and consumption; it is not bundled.

**Execution:** separate-phase. `runtime.powertable_factory.configured_table(...)`; `python plan.py construct-native table-column --input column.request.json --out column.json`; `python plan.py construct-native powertable-source --input source.request.json --out source.json`; `python plan.py construct-native powertable-rows --input rows.request.json --out rows.payload.json`; `python plan.py prepare-maintenance --baseline definition.json --requests maintenance.json --out maintenance`; `python plan.py api update --config destination.json --payload candidate.json --run run --label update`

**Inputs/dependencies:** Resolve the mode and source state first. Creation
requires an authorized SQL Database, an explicit schema, physical primary keys,
a confirmed FabricSql connection and the destination approval chain. Analysis
requires a confirmed Plan/PowerTable source and read-only SQL access.

**Boundaries:** At most five created sheets/tables; 1-100 optional synthetic rows
per new table; allowlisted SQL types; US Dollar Currency metadata; all-schema
discovery; explicit schema and source confirmations. Analysis is read-only and
cross-analysis is limited to three source sheets with confirmed relationships
before aggregate answer queries. Configured grids require coherent ALM parts and
source IDs. Deferred sheets are uninitialized. Approved `sqldb-cli` and external
adapter profiles are required for their respective SQL/workload writes.


Related: LOOKUP, F17, F18.

## LOOKUP Advanced Lookup and key/label selection

**Invoke for:** Retrieve the benefit rate for a department. Show product names while storing stable product keys.

**Read:** [Advanced Lookup Authoring](feature-contracts.md), [Choose Lookup, InfoBridge or Both](feature-contracts.md), [connected-construction.md](connected-construction.md).

**Execution:** partial. `python plan.py construct-native table-column --input column.request.json --out column.json`; `python plan.py construct-native dimension-mapping --input mapping.request.json --out mapping.json`; `python plan.py construct-native input --input input.request.json --out input.payload.json`

**Inputs/dependencies:** Lookup grain, matching keys, missing/duplicate policy and labels separate from stored values.

**Boundaries:** SQL PowerTable lookup columns and dimension descriptors are executable. General Planning Advanced Lookup source/loading factory is incomplete; setting options_source=Lookup alone is not sufficient.


Related: F18, DIMENSION-ID, POWERTABLE.

## RULES Input rules, allocation and distribution

**Invoke for:** Allocate a departmental target to employees using weights. Apply row locks or numeric limits.

**Read:** [Input Rule Business Workflows](feature-contracts.md), [Allocation Examples](feature-contracts.md), [Native Rule Serialization](feature-contracts.md), [builder-integration.md](builder-integration.md).

**Execution:** separate-phase. `python plan.py construct-native rule --input rule.request.json --out rule.payload.json`

**Inputs/dependencies:** Target grain, row/column/measure selectors, weights, total conservation and verified engine mount.

**Boundaries:** Lock, basic row-distribution and MinMax payloads are implemented. Captured measure-weight profiles support Row / All dimensions / CurrentYear and Column / All dimensions / source Row Use Self. They are Planning rules. General runtime execution acceptance remains separate. Numeric distribute-to-children is distinct from saved weighted allocation.


Related: F02, F20, F30.

## DIMENSION-ID Dimension ID Mapping

**Invoke for:** Keep employee inputs stable when employee display names change. Keep values associated with the product ID when SKU moves across brand/category; exclude redundant ancestors from the key, keeping them visible.

**Read:** [dimension-leaf-keys.md](dimension-leaf-keys.md), [Dimension ID Mapping](feature-contracts.md), [connected-construction.md](connected-construction.md).

**Execution:** integrated. `python plan.py leaf-key-mapping --input examples/leaf-key-mapping.request.json --out mapping.json`; `python plan.py construct-native dimension-mapping --input mapping.request.json --out mapping.json`; `python plan.py build --model current-model.json --spec application.json --out draft`

**Inputs/dependencies:** Non-null stable keys and complete label/key descriptors from current model metadata.

**Boundaries:** ID/Skip supported branches only; an existing data-coordinate change requires migration planning, not arbitrary ID replacement. Default leaf-key reduction needs unique same-entity evidence; keep composite/independent/time keys and explicit choices. Existing storage changes require a separate value migration.


Related: LOOKUP, F08.

## FORMULAS Formula measures and variance

**Invoke for:** Calculate revenue from volume times price. Add Forecast minus Actuals variance and margin percent.

**Read:** [Native Formula Authoring](feature-contracts.md), [Ordinary Measure-Based Planning Examples](feature-contracts.md), [forecast-review-execution.md](forecast-review-execution.md).

**Execution:** integrated. `python plan.py build --model current-model.json --spec application.json --out draft`; `python plan.py construct-native formula --input formula.request.json --out formula.payload.json`

**Inputs/dependencies:** Resolved dependency graph, correct grain/units and native formula symbols.

**Boundaries:** Formula strings use explicit ${symbol} mappings. Formula measures, default formulas, OnChange side effects and edit eligibility are distinct settings.


Related: F02, F09, F29, F30.

## CUBE Cube planning

**Invoke for:** Calculate or enter a measure at an explicit cube breakdown.

**Read:** [Cube Planning Authoring](feature-contracts.md), [Cube Business Examples and Boundaries](feature-contracts.md).

**Execution:** partial. `python plan.py construct-native cube-settings --input settings.json --out validated-settings.json` validates the current request fields, dynamic model marker and per-key lookup dimensions. Input/Forecast factories preserve returned cube bindings.

**Inputs/dependencies:** Resolved Cube source, breakdown and target coordinates.

**Boundaries:** Request and saved-record shapes are now source-validated, but no complete Cube provisioning, refresh or allocation/evaluation factory is shipped. Do not label a normal formula or aggregate as a native Cube.


Related: FORMULAS, F09.

## NAVIGATOR Page and bookmark navigation

**Invoke for:** Every new Intelligence dashboard must include a Page Navigator automatically. Add other tabs to switch between planning dashboards and saved views. Construct complete Navigator defaults, including disabled icons; investigate a dashboard white screen or topPadding error.

**Read:** [navigators.md](navigators.md), [builder-integration.md](builder-integration.md).

**Execution:** separate-phase. `python plan.py construct-native navigator --input navigator.request.json --out navigator.json`

**Inputs/dependencies:** Current pages/bookmarks, supported host registration and complete placement inventory.

**Boundaries:** All-visible-page tabs are integrated in build/provision, including ALM membership and the native geometry save. Additional targeted tabs/buttons use separate helpers and real destination IDs. A bookmark target must already represent a complete capture; navigation does not implement restore semantics.


Related: F23, F06.

## SCENARIOS Scenarios and sensitivity

**Invoke for:** Explore a downside without changing the saved budget. Maintain separate Budget and Upside versions.

**Read:** [Select Features by Business Distinction](feature-contracts.md), [Planning Input Context Authoring](feature-contracts.md), [context-intelligence.md](context-intelligence.md).

**Execution:** partial. `python plan.py construct-native input --input input.request.json --out input.payload.json`; `python plan.py build --model current-model.json --spec application.json --out draft`; `python plan.py build --model current-model.json --spec application.json --out draft`

**Inputs/dependencies:** Decide transient sensitivity versus persisted versions versus native Scenario lifecycle.

**Boundaries:** Simulation input and external version Context have constructors; general native Scenario creation/copy/compare lifecycle is not supplied by them.


Related: F08, F05, F09.

## Exact input and execution details

`python plan.py discover --module <ID>` expands every operation into its full
command, input contract, callable locations and local/live phase. `--json` returns
the same machine-readable record. The authoritative catalog is module-routing.json;
this guide and CLI are generated from/consume that catalog. Caller keys must match
the real function, not business display names. For **construct-native** and
**construct-bridge**, input JSON is unpacked as keyword arguments to the listed
factory. Approved external-adapter requests use the listed callable's arguments
(the former command
supplies client and label); their API profile is described in builder-integration.md.

Read [routing-examples.md](routing-examples.md) for composed business requests and
phase ordering. Historical implementation-status/api-contract-gaps entries remain
evidence for specific releases; do not read an old broad gap as removing a listed
newer constructor. Runtime/calculation acceptance remains separate.

## Planning integrity checks (v8)

Read [planning-integrity.md](planning-integrity.md). Missing known GlobalStyles
defaults are completed by build/format-matrix, and grouping field references use
canonical model names across assignments, filters and lookup metadata. Run
`check-planning-properties` before saving or `repair-planning-properties` to produce
an explicit candidate. Bundled Plan/property-batch writes reject violations.
These are offline checks; they do not require report runtime validation.

## Required presentation defaults (v9)

Read [planning-presentation.md](planning-presentation.md). Normal application builds
require rich Intelligence dashboards above their embedded Planning grids. The
complete native TEXT header writer and semantic measure palette are executable
through present-planning; build/provision apply new-application defaults. Use
check-application-presentation for offline coverage. These defaults preserve the
v8 integrity checks and all prior Forecast, formatting, From Sheets and storage fixes.
Explicit requests to skip runtime validation still take precedence; use the
verified identity/ETag reads and save-only placement options described there.


## Measure source binding (v10)

Read [measure-source-bindings.md](measure-source-bindings.md) before assigning or
replacing measures. Use `resolve-measure-binding` for exact PowerBI/Visual/InfoBridge
identities and typed metadata. Native companion records are not sheet outputs.
Reconcile ordinary filter cards with changed chart assignments; captions alone
do not identify a source. Preserve the prior formatting, forecasting and layout fixes.


## Required application baseline (v11)

Home is mandatory alongside rich Planning headers, measure colors and embedded
Intelligence dashboards. Read [application-defaults.md](application-defaults.md).
Use `check-application-defaults`; verify Home content, role metadata and workload
visibility separately. Do not silently downgrade a complete application to grids
or dashboards without its native landing page. Retain all source-binding fixes.
