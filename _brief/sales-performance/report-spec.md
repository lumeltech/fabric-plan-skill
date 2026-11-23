# Sales Performance - Executive Summary: discovery plan

> **Build authorized, 2026-11-16:** the user approved proceeding with the
> reference-matched plan, requested a 16:9 canvas and named the new Fabric Plan
> **Sales Performance - Executive Summary-AI Report 16Nov**. These latest
> instructions supersede the historical approval_pending statements below.
> Delivery is the previously specified Planning-Demos target folder.

> **Reference-image revision, 2026-11-16:** the user has now supplied the image
> and explicitly requested its formatting, styling, background and chart colours.
> [Reference-matched report plan](reference-design-plan.md) supersedes sections
> 3-8 below for proposed scope, period, design and interactions. Sections 1-2
> retain the verified source/destination and inventory. The older full-year,
> six-KPI proposal below is historical discovery context, not the build target.
> Status remains approval_pending: no report creation or publishing is authorized.
> Latest revision: Year is the only slicer (single-select, default 2025);
> headlines use full-year totals. Units Sold replaces Customers; Channel uses
> all four members. Original commercial-performance copy and explicit Top 5 /
> Top 3 rules are in the reference-matched plan. No customer-count measure is needed.
> Metric/visual-switching buttons and tabs are excluded. The four KPI cards
> remain fixed; right-hand charts and Top-N rankings use Net Sales versus PY
> Net Sales. No Matrix visual or chart/Matrix toggle is in scope.

## Status and boundaries

**Draft discovery plan, not an approved or locked build specification.**
Phase: `approval_pending`; active mode: discovery only.
The user requested model exploration and a plan first, then will provide a reference image to reproduce in a Fabric Plan Intelligence Sheet.
No Plan item, sheet, report definition, model object or folder has been created or changed.
Existing briefs for other semantic models are preserved.

Design is deliberately not locked: inventing a palette, canvas or layout before the promised reference would conflict with the requested workflow. A complete canonical design contract and build-approval request follow screenshot mapping, not this preliminary plan.

## 1. Identity, binding and future destination

- Proposed Plan name: Sales Performance - Executive Summary.
- Audience: executives / leadership; proposed first-build scope: one Intelligence Sheet.
- Source environment: MSIT, authenticated tenant verified for the current read-only calls.
- Workspace: Planning-Demos (`f0000000-0000-4000-8000-0000000000af`), verified by workspace listing.
- Semantic model: SM Sales Performance Dashboard-AI Test (`f0000000-0000-4000-8000-000000000099`), verified by semantic-model listing.
- [Live semantic model](https://msit.powerbi.com/groups/f0000000-0000-4000-8000-0000000000af/datasets/f0000000-0000-4000-8000-000000000099/details?experience=fabric-developer&subfolderId=330275).
- Future destination: Planning-Demos > Working folder > Saddam > 00_AI Skill Test and Report Build.
- Folder chain verified read-only: Working folder `f0000000-0000-4000-8000-0000000000ab` > Saddam `f0000000-0000-4000-8000-00000000008a` > target `f0000000-0000-4000-8000-000000000081`.
- Target folder is not the semantic-model URL's `subfolderId=330275`; use the verified Fabric folder ID above.
- No permission to build or publish yet; destination is recorded for the later approved operation. Contributor/write capability has not been tested.
- Model-measure permission: `ask-per-measure`, explicitly granted during this task. Each new measure still needs its own DAX/home-table/format approval and a reason it cannot be computed in Fabric Plan. No new measure is currently proposed or needed.

## 2. What the model contains

[Complete field registry](field-registry.md), captured live on 2026-11-16.

- Seven Import tables, 51 columns including technical/hidden fields, 36 measures and five active one-way relationships.
- FactSales: 13,698 sales lines, 7,120 distinct orders; inferred sales-line grain checked through unique SalesLineKey.
- Five dimensions: Date, Product, Customer, Region and Channel; one measure-home table.
- Actual sales cover January 2024 through December 2025. Calendar covers January 2024 through December 2026.
- Currency: INR, evidenced by source columns and model formats.
- Comparisons available: actual, prior year, budget and target. Budget and target are separate baselines. No explicit forecast measure was found.
- Product scope: 24 products, six categories, 15 subcategories, 10 brands.
- Customer scope: 250 customer names, four segments; four regions and four channels.
- All table and column descriptions are missing; seven measure descriptions are populated. Available descriptions and all returned metadata are preserved in the registry/raw evidence.

## 3. Executive story supported by the observed data

Proposed default: January-December 2025 versus the corresponding 2024 period.
This is the latest full year with actual data, not a claim about current operational performance or refresh freshness.

| Metric | Observed 2025 value | Interpretation |
|---|---|---|
| Net Sales | INR 9,955,994.58 | +8.62% versus 2024 |
| Budget Net Sales | INR 10,358,000.36 | Actual shortfall INR 402,005.78, or -3.88% |
| Target Net Sales | INR 10,875,900.24 | Actual -8.46% versus target |
| Gross Profit | INR 2,941,211.34 | Amount, not margin percentage |
| Gross Margin % | 29.54% | Approximately -0.03 percentage points versus 2024 |
| Total Orders | 3,745 | Distinct orders in selected context |
| Quantity Sold | 8,987 | Units |
| Average Order Value | INR 2,658.48 | Evaluate as a ratio, never sum member averages |

Narrative: sales grew year over year, but did not meet budget or target. Explain the shortfall by region and product category, while monitoring profitability.
The sampled 2025 region breakdown shows North above budget; East, South and West below. Category results include positive budget variances in Home & Kitchen and Office Supplies. These observations are context, not hardcoded report text that would ignore filters.

## 4. What can be built - proposed first sheet

Visual counts, arrangement and final selection will follow the reference image. Keep the final page within 12 data visuals; reduce or combine candidates rather than overcrowd it.
All candidates below use exact live-model fields; readiness means data availability, not verified runtime encoding.

| Candidate | Question | Exact fields/measures | Feature IDs | Readiness |
|---|---|---|---|---|
| Headline KPI cards, up to six | How large, profitable and active is the business? | _Measures[Net Sales], [Gross Profit], [Gross Margin %], [Total Orders], [Quantity Sold], [Average Order Value] | KPI-CARD-01 | Ready |
| Net Sales comparisons on KPI | Are we growing and on plan? | _Measures[Net Sales], [PY Net Sales], [BUD Net Sales], [Target Net Sales] | KPI-VAR-01 | Ready input pairs; variance configured in Fabric Plan |
| Monthly sales trend | When did the performance gap develop? | DimDate[Year], DimDate[Month]; _Measures[Net Sales], [PY Net Sales], [BUD Net Sales] | CH-LIB-03 | Ready; single selected year, months sorted by MonthNumber |
| Regional comparison | Where is the shortfall? | DimRegion[RegionName]; _Measures[Net Sales], [BUD Net Sales] | CH-LIB-01 | Ready; native comparison encoding still needs sample verification |
| Category contribution | Which categories drive sales and profit? | DimProduct[Category]; _Measures[Net Sales], [Gross Profit] | CH-LIB-01 | Ready; final choice or omission follows screenshot |
| Optional detail Matrix instead of category chart | What should leadership drill into? | DimProduct[Category], [Subcategory], [ProductName]; _Measures[Net Sales], [BUD Net Sales], [Gross Profit], [Gross Margin %] | MX-LAY-01, MX-VAR-01 | Ready inputs; Matrix/variance encoding requires native evidence |

No separate detail sheet is included initially. Regional, product and customer-detail sheets are optional later scope, not automatic additions.
IBCS report template/theme is an available alternative because actual/PY/budget pairs exist, but is off unless explicitly selected; the reference image takes priority for requested appearance.

## 5. Filters and interaction proposal

- Year: DimDate[Year], proposed single selection 2025. Year/month controls must not default to empty 2026 actuals merely because it is the current year.
- Region: DimRegion[RegionName], four members.
- Product category: DimProduct[Category], six members.
- Channel: DimChannel[ChannelName], four members.
- Optional customer segment: DimCustomer[CustomerSegment], four members.
- Optional customer selector only if present in the reference: DimCustomer[CustomerName], 250 members, searchable dropdown, never a large tile set.
- Features: SF-FACET-01; SF-FEAT-02 only for optional search. A date-range control (SF-DATE-01/02) can replace Year if the reference requires it; do not add redundant controls automatically.
- Super Filter position, dimensions, expansion state and overflow: pending the reference image. Do not lock top/side placement yet.
- Same selected business/date context should filter the sheet; preserve comparison measures. There is no Scenario column and no scenario slicer is proposed.
- Region uses DimRegion -> DimCustomer -> FactSales. Never bind a region label to the unconnected FactSales[RegionKey].
- Date drill proposal: Year > Quarter > Month; product drill proposal: Category > Subcategory > ProductName. Native hierarchies were not retrievable; runtime drill behavior must be verified before promising it.
- Chart cross-filter/highlight, reset control, Help/Info, tooltips and navigation remain subject to screenshot mapping and native capability validation. Do not invent unsupported interaction encodings.

## 6. Metric contracts and calculations

Use the existing model measures; do not redefine them in the semantic model.
Available descriptions establish Net Sales as after-discount revenue, Gross Profit as sales less COGS, Gross Margin % as profit / sales, Total Orders as distinct completed orders, and AOV as sales / distinct orders.

Proposed Fabric Plan visual calculations, only where needed:

- Sales YoY % = (Net Sales - PY Net Sales) / PY Net Sales.
- Sales versus budget amount = Net Sales - BUD Net Sales.
- Sales versus budget % = (Net Sales - BUD Net Sales) / BUD Net Sales.
- Sales versus target % = (Net Sales - Target Net Sales) / Target Net Sales.
- Margin change in percentage points = 100 * (Gross Margin % - PY Gross Margin %).
- Zero/blank comparison denominators show no comparison / not available, never an invented zero-growth result.
- Higher sales/profit/margin is provisionally favorable; use signs and labels as well as color. No arbitrary red/amber/green thresholds.
- Ratios, distinct orders and AOV are evaluated in total context, not summed across categories. Percent growth is relative change; margin change is percentage points.
- Label the view full-year 2025. Do not label ordinary totals MTD/YTD without a real period calculation.

Feature routes: KPI-VAR-01 for KPI comparisons; MX-VAR-01 for an approved Matrix variance; CH-CALC-01 only if a required chart calculation is evidenced. Model-measure creation is unnecessary for the current proposal.

## 7. Evidence, caveats and unresolved gaps

- All proposed source fields resolve in the live registry.
- Twelve 2025 months contain actual and PY/budget/target sales values.
- Monthly sales/budget/target/profit/orders reconcile to annual totals within INR 0.01.
- Region/category/channel/segment sales breakdowns reconcile to annual sales within INR 0.01.
- Annual 2025 PY Net Sales agrees with 2024 Net Sales within INR 0.01.
- Tested source sums, profit, discount, AOV and margin arithmetic pass monetary tolerance INR 0.01 and ratio tolerance 1e-10.
- Tested fact-key blanks, dimension orphans and fact/customer region disagreement returned no matching exceptions.
- DAX measure definitions were not exposed: INFO.VIEW.MEASURES returned null expressions and supplementary INFO.MEASURES failed. Aggregate checks establish observed consistency, not full formula verification.
- Supplementary native hierarchy metadata retrieval also failed. An authorized model metadata export can resolve these gaps if the screenshot requires more complex measures/drill paths.
- PY Gross Margin, BUD Profit Margin and Target Profit Margin are currency amounts despite their names; percentage variants are separate.
- Discount % denominator is not established, so it is excluded from first-build KPIs.
- No verified forecast, order-status exclusion logic, fiscal calendar, refresh timestamp, KPI thresholds or brand assets. Do not invent them.
- Native visual JSON and rendered fidelity are not established by data inspection or the pending screenshot. Observed/unverified encodings need native saved samples before authoring; KPI-CARD-01 and KPI-VAR-01 are catalogued verified.

## 8. Next steps and approval gates

1. User reviews this data-backed plan and shares the reference image.
2. Map each visible reference element to an Intelligence Sheet feature and exact model fields; identify unsupported/missing elements, while using this model's real labels and data.
3. Resolve the design identity, precise canvas/grid/placements, filter layout/overflow, font/number formats, branding and Help/Info. Persist the session theme and canonical design contract only after those choices are known.
4. Finalize the one-sheet locked specification and ask for explicit approval in a later reply. The reference image alone is not build/publish approval.
5. After approval only: author from a native sample, validate against a freshly captured live registry, and implement visual calculations without changing the model.
6. Publish only after explicit authorization, into the verified destination folder; poll completion, read back and validate bindings, then verify rendered visuals, slicers, comparisons and screenshot fidelity.

Discovery checks passed as listed; design, authoring, API acceptance, readback and UI rendering are **not performed**. No report has been built.
