# Sales Performance - Leadership Overview

## Final state: test page cancelled, finalized report restored

The user cancelled the Top N test page. It never persisted. Edits made between
the color finalization and that request had reset Executive Overview and Info
to white default canvases. They also made Help and Info visible, added an empty
Intelligence 1 page, and stored an East selection on the Detailed Breakdown
slicer. Two restore updates were applied, and both API operations reported
failure. A full readback, `restore-readback2`, nevertheless matches the
finalized `surface-color-readback`. It has 8 pages: canvas `#F5F5F4`, wallpaper
`#f3f5f7`, Help and Info hidden, with no stored East selection. The only
retained difference is native default-key normalization on the Detailed
Breakdown Matrix. Everything below this section is historical.

## (Cancelled) isolated Top N error reproduction

Append exactly one page, `Top N Filter - Repro`, to the original Northsar
report. Clone the saved Product Details layout and preserve its failing
Top 10 ranking configuration. Keep all existing nine pages, including the
user-created Intelligence 1, in their current order. Do not modify the
separate user-created Top N test report or repair the original charts.

The fresh `topn-repro-preflight` export contains 467 parts. Compared with the
earlier reproduction baseline, seven Executive Overview chart owners have
native editor-state updates; preserve this newer snapshot byte-for-byte.
The original editor tab was closed only after Save was observed disabled.

The leading-products chart ranks `DimProduct[ProductName]` with
`filterBy: "_Measures[Net Sales]"`, Top 10 enabled. A read-only equivalent
DAX TOPN query returned ten products with nonblank current/prior-year sales.
This proves the model query succeeds, not that the chart emits a valid ranking
request. The reported `RankByColumnType` error and a possible ranking-handle
translation issue remain distinct from the known Matrix initialization failure.
No outgoing failed ranking request or controlled repair has established the
upstream cause. The append-only candidate has 528 parts, including 61 new
parts and 29 cloned owners. The existing 466 non-root parts are byte-preserved.
Validation reports the same 23 pre-existing errors as the fresh baseline and
no new errors; no unrelated fixes were made.

The update was submitted once and accepted as operation
`f0000000-0000-4000-8000-0000000000a4`, request
`f0000000-0000-4000-8000-000000000095`. The new page ID is
`f0000000-0000-4000-8000-0000000000a5`, and its leading-products owner is
`f0000000-0000-4000-8000-0000000000b3`. Persistence and runtime verification
remain pending. Do not submit a duplicate update while this operation is
unresolved. Local `topn-reproduction-diagnostics.json` records evidence,
uncertainties, the sanitized receipt and team revalidation steps.

## Current request: distinct canvas and wallpaper surfaces

Match the remaining seven pages, including hidden Help and Info, to Executive
Overview: canvas `#F5F5F4`, wallpaper `#F3F5F7`. Preserve all images, visual
properties, page dimensions, bindings and reference-page formatting.

The fresh saved `surface-color-baseline` contains 463 parts. All canvases already
match; only the other seven `canvasStyle.wallpaper.value.color` leaves differ.
`surface-color-candidate` changes exactly these seven leaves and byte-preserves
the other 456 files. Native inspection confirmed the reference wallpaper
`#f3f5f7`, but editor automation did not reliably dismiss its color picker.
No native color values were changed. The complete color-only payload is
saved and verified. Update operation
`f0000000-0000-4000-8000-000000000083` reported a non-retriable `UnknownError`
at poll 81. A fresh complete export, operation
`f0000000-0000-4000-8000-0000000000e9`, succeeded and was unpacked as
`surface-color-readback`. All 463 saved parts exactly match the color-only
candidate: all eight pages have the requested distinct surfaces, exactly seven
wallpaper leaves changed, and the other 456 original parts are byte-preserved.
Executive Overview is unchanged, as are all visual properties, images, geometry,
dimensions and model references. Do not resubmit the update. The existing native
editing session was not reloaded; a new fitted-view visual check was not
performed. Matrix and broader report-finalization issues remain paused.

## Revision 6: page finalization and Matrix investigation

The latest saved report was exported on 2026-11-19 as
`page-finalization-baseline` (463 parts, eight sheets). It contains substantial
new user edits: 15 added and 15 removed parts, and 122 changed retained parts
relative to the earlier partial update. Preserve this snapshot rather than
reapplying the older formatting candidate.

Help and Info are already hidden and have no registered slicer owners. Their
six-page navigators exclude utility destinations; the Help/Info icon buttons
retain ordinal destinations 7/8. Opening hidden pages through those buttons
still requires Reading-mode runtime verification. Help's self-navigation
button is intentionally disabled; its Info button remains enabled.

### Matrix findings before any memory or skill update

- Both the original Product hierarchy Matrix and the user's newly created
  Matrix display `Failed to initialize application: unreachable`.
- The new Matrix has a distinct native owner ID and binds only
  `DimRegion[RegionName]`, `DimCustomer[State]` and `_Measures[Total Orders]`.
  This reproduces the failure without the older Matrix's authored measure
  configuration or currency/percentage formatting.
- Fresh live metadata returned seven tables, 51 columns, 36 measures and five
  relationships. Read-only queries using both hierarchies and Net Sales,
  Gross Margin % and Total Orders succeeded: 24 product rows and 21 geography
  rows, with nonblank margins/orders throughout. Each hierarchy reconciles
  to 2025 Net Sales 9,955,994.58.
- Native browser Console diagnostics identify a Rust/WebAssembly
  initialization-request deserialization failure:
  ``packages/jetstream_wasm/src/lib.rs:62: Failed to parse app request: missing field `url` ``.
  The subsequent panic at line 63 produces the visible `unreachable` symptom.
  This reproduces in both the original and newly added native Matrix, build
  20261111.26. It occurs before a usable Matrix can initialize.
- The saved root `semanticModelReference` has no `url`; native sibling
  references do contain a canonical Power BI dataset URL. The original
  generator inherited a donor reference without this field. Restoring the
  field with the existing workspace/model IDs is a controlled candidate
  repair, not yet proof that this saved field supplies the missing runtime
  request field. No model or connection rebinding is involved.
- The user restored Edge. The report was verified in Reading mode before
  submitting the candidate. The earlier minimized-window blocker is resolved.
  Direct query success still does not prove the workload's separate
  connection path.

### Page-by-page acceptance

| Page | Saved-definition findings | Remaining runtime acceptance |
|---|---|---|
| Executive Overview | Four KPIs, three charts, one business-filter owner, native navigator and two utility buttons | Preserve user reference; check values/filter behavior after refresh |
| Performance Drivers | Four charts, one business-filter owner, native navigator and utility buttons | Rendered titles, ranking, filtering and labels |
| Detailed Breakdown | Original product Matrix plus newly created native geographic Matrix | Both observed initialization failures; resolve before accepting |
| KPI Monitoring | Ten KPI cards, one business-filter owner, native navigator and utility buttons | Card fit, blank years, comparisons and rate-versus-pp semantics |
| Product Details | Two charts and product-detail Matrix | Matrix startup, hierarchy totals and chart interaction |
| Geographical Analysis | Two charts and state-detail Matrix | Matrix startup, geography totals and chart interaction |
| Help | Hidden; no slicer; two overlapping pairs of branding images | Utility access/return, final reading fit |
| Info | Hidden; no slicer; user replaced the earlier missing images | Utility access/return, definitions and currency disclosure |

A utility-only local candidate, `utility-finalization-candidate`, retires the
two older overlapping Help images while preserving the user's newer pair,
normalizes copied utility image origin IDs, removes padding, fits short text
and updates educational/context copy. It does not recreate filters or images.
All 348 analytical-sheet files, including the new native Matrix, remain byte
identical to the latest saved baseline. Utility navigation states are retained.
Both utility pages have two visible images, no visible slicers and zero
unexpected visible-content overlaps.

Latest saved-state validation found two copied-image origin-ID conflicts.
The utility candidate fixes both: zero validation errors, 191 geometric
warnings, 34 model fields checked, and six focused tests passing. Warnings and
native interaction acceptance remain separate from structural validity.
The fresh `matrix-url-repair-baseline` export is structurally identical to the
saved page-finalization baseline. The utility cleanup was rebased onto it and
the missing model-reference URL added to `matrix-url-repair-candidate`.
All 463 parts and sheet registrations are retained; all 348 analytical-sheet
files are byte-preserved. Validation passes with zero errors and 191 warnings;
six formatting tests and 17 definition tests pass.

One full-definition update was submitted for this evidence-based repair:
operation `f0000000-0000-4000-8000-0000000000bb`, request
`f0000000-0000-4000-8000-00000000007d`. It terminated **Failed** with
non-retriable `UnknownError`. Polling resumed the same accepted operation
after the helper timeout; no duplicate update was submitted.

The successful `matrix-url-repair-readback` export has all 463 parts:

- The root definition is unchanged. **The candidate URL did not persist.**
  Therefore the proposed runtime-field mapping has not been tested; this is
  not evidence that a successfully deployed URL restoration failed to help.
- Every analytical visual's property document is unchanged.
- All 26 Help property documents match the cleanup candidate. The duplicated
  older artwork is retired in saved state, preserving the newer user uploads.
- All 27 Info property documents remain unchanged; its cleanup did not persist.
- Seventeen writeback companions gained only `version: 1`.
- Both utilities remain hidden and slicer-free. Reading-mode icon access is
  still unverified: the Info click did not navigate from Executive Overview.
- Saved-state validation now reports one remaining copied-image origin
  conflict on Info, zero lost parts, and 191 geometric warnings. The image
  conflict has not been established as the cause of the Matrix or save failure.

Reading-mode visual checks confirmed the Overview, four Performance Drivers
charts and all ten KPI cards render. Monetary/count/rate headlines on KPI
Monitoring use the expected USD display/plain integer/percentage forms.
These observations do not constitute full filter/year/interaction acceptance.
The report remains incomplete while Matrix initialization, Info persistence
and hidden utility navigation are unresolved. No semantic-model changes or
new memory/skill guidance were made. Preserve the newest readback and avoid
another unchanged full-definition update.

## Revision 5 history

**Revision 5, 2026-11-19. User-corrected first page is the finishing reference.**
This revision supersedes the older ten-slicer and separate-chart-caption
composition below. The user requested autonomous application of their saved
Executive Overview standard to the remaining pages:

- USD display formatting on explicitly monetary KPI values; counts remain
  plain integers. Do not invent a currency when none is assigned. This is a
  presentation override, not FX conversion; the source model's INR format
  metadata is unchanged and the Info disclosure must make this explicit.
- True percentage formatting for rate headlines and comparisons, not raw
  fractions. Keep relative variance formatting separate from value formats.
- Transparent internal KPI backgrounds; preserve native sparklines and
  actual/PY/budget role bindings.
- Two-line title/subtitle inside each chart, without duplicate text owners or
  space-consuming endpoint deviation lines. Matrix titles use a different,
  uncaptured native layout and retain fitted external captions for now.
- One native vertical six-page navigator, retaining the user's default,
  selected, hover and pressed styles; separate icon-enabled Help/Info buttons.
- Five filters exactly as saved on the first page: Year, RegionName, State,
  Category and Subcategory. Year remains 2025 by default.
- Reuse this item's uploaded logo and header image. Remove text padding and
  increase short text heights minimally to prevent scrollbars.

**Current evidence and deployment status:** Executive Overview rendered with
the user's corrections on 2026-11-19. A fresh export contains 435 parts and
preserves those corrections. Its canvas uses native pixel units; the other
seven sheets use percentage units. The validator now honors each sheet's
declared unit, with four focused geometry regression tests.

The local candidate
`_build/northsar-leadership-18nov/retry-formatting-candidate` applies the
reference to seven remaining sheets and preserves all first-page owner bytes,
all existing parts, the semantic-model reference, and unrelated service state.
Validation: zero errors, 190 geometric warnings (including retained hidden
owners and intentional background overlaps); a separate visible-owner audit
finds zero unexpected content overlaps, checks 79 background/content layer
pairs, 24 KPI value/comparison formats, and eight internal chart titles.
Four focused formatting tests also pass. This is local evidence, not native
runtime acceptance. Cross-sheet filter synchronization remains uncaptured.

**Retry partially persisted; not complete:** desktop access returned and
the report was observed in Reading mode without a pending Save dialog. The
fresh `retry-formatting-baseline` contains 435 parts and is structurally
identical to the preserved user reference. A new candidate was generated from
that complete snapshot and passed the same exact-output audit and all 21
focused tests. Detailed Breakdown still showed a loading spinner; no explicit
visual error was observed.

One update was submitted through the documented Core Items updateDefinition
route, operation `f0000000-0000-4000-8000-000000000094`, request
`f0000000-0000-4000-8000-000000000092`. It terminally Failed after about
30 minutes with non-retriable `UnknownError`. No mutation remains pending.

A subsequent successful export, `retry-post-update-readback`, contains 463
parts and demonstrates partial persistence despite that failure:

- All five remaining analytical pages and Help have owner properties matching
  the validated candidate.
- All 22 Executive Overview property parts retain their original bytes.
  Four of its writeback companions gained only the service's `version: 1`.
- Info has 14 owner-property differences from the candidate. Two newly
  registered image owners have null properties; its formatting is incomplete.
- The service added 14 image writeback companions. No original part was lost.

Detailed Breakdown eventually exposed both Matrices as **Initialization
Failed**. Opening the native details showed **Failed to initialize
application: unreachable**. One native geographical Matrix data reload did
not resolve it. This establishes a runtime initialization failure, not its
underlying cause; do not diagnose it as a proven field-binding defect.
After a same-tab report reload, native runtime acceptance is still unverified.

Do not blindly repeat the full save, assume rollback, or mark the report
complete. Preserve the fresh partial live state and use a verified targeted
repair path for Info before further deployment. The earlier native save still
has no formal terminal receipt; Reading mode is an observation, not one.

## Earlier approval and deployment history

The following is retained as historical context; revision 5 controls finishing.
The user approved the preview's styling and requested two additional pages,
short explanatory visual subtitles, and all ten base KPIs. This consolidated
spec replaces the earlier one-, three- and four-page proposals.
The user explicitly approved the blueprint and authorized a new Fabric Plan
named **Northsar Leadership 6 Page-AI Created Report 18_Nov**, in the semantic
model's workspace and folder. The 2026-11-18 live listing confirms folder
`f0000000-0000-4000-8000-000000000081` and no name collision.
The [new Fabric Plan](https://msit.powerbi.com/groups/f0000000-0000-4000-8000-0000000000af/plans/f0000000-0000-4000-8000-0000000000bf?experience=fabric-developer)
has been created and moved into the verified semantic model folder.
Initial readback contains all eight submitted sheets (six analytical and two
utilities), all 214 registered native owners and every submitted owner part.
The source semantic model and existing reports are unchanged.

**Build in progress, not final acceptance:** the user can see each page but
reports visual placeholders instead of rendered visuals. Desktop inspection
reaches the native Reading shell and eight-page explorer. After loading, the Help
page exposes a confirmed layout defect: background panels obscure their content.
The native convention is larger layer order = further back, but the original
builder assigned increasing order to later content. The local definition and
builder are corrected; all 142 overlapping background/content checks pass.
The earlier full binding update (operation
`f0000000-0000-4000-8000-0000000000b4`) has Failed with a non-retriable
`UnknownError`. A fresh 444-part baseline was exported afterward. The layer-only
correction changes 213 owner order values, preserves every other setting, and
passes all 142 background/content overlap checks. It was submitted once as
operation `f0000000-0000-4000-8000-0000000000b5`. That operation also Failed
after approximately 30 minutes with non-retriable `UnknownError`; do not repeat
the same full-definition save. Native Editing mode and the Layers pane are now
accessible, but attempted layer dragging did not produce a verified reorder.
The automation engine subsequently rejected drag delivery because the target
was not the visible hit target along its path; keyboard dispatch to the visual
options also failed. No focus or input-safety workaround was attempted.
The editor remains open with unsaved state. Some navigation/labels are visible,
but Executive Overview chart backgrounds still obscure the plots.
The layer correction is not verified as deployed; do not claim completion.
Logo resource upload, shared-filter sync capture, visual variance columns, rate
pp comparisons and final rendering/interaction checks are still outstanding.
Do not equate API acceptance or persistence with runtime rendering or exact
blueprint fidelity. Layering explains the obscured content; chart data rendering
still requires verification after the correction is deployed.

## Deployment capacity risk - 2026-11-18

The current [Microsoft Learn Plan limitations](https://learn.microsoft.com/en-us/fabric/iq/plan/overview-limitations)
state **50 visuals per Plan item** and 25 sheets per item. The six-sheet count
is valid, but the approved native visual composition exceeds the visual limit.
Count all registered elements, not only analytical charts.

Conservative blueprint count (even treating all six page buttons as one
navigation owner, all ten filter fields as one Super Filter owner, and card
subtitles/sparklines as part of each card):

- 29 analytical visual owners across six pages.
- 10 shared-shell owners per page x 6 = 60: rail shape, logo, page navigation,
  filter panel, Help, Info, page title, page subtitle, selection summary, footer.
- 1 additional KPI caveat text owner.
- **90 owners before Help/Info utility content**, versus documented maximum 50.

The preview was a design mockup and did not establish native capacity.
The user was informed of the documentation and explicitly instructed:
"there is no limilataion please proces with report creataion and pleae and use exact blueprint we build together please start report builidng".
Proceed with the single-item blueprint as requested. The documentation remains
a recorded risk, not a claim that the tenant is verified to support more than
50 visuals. API acceptance, complete persistence and native runtime behavior
must be checked separately. Do not silently simplify or split the item.

Alternatives were presented but the user did not approve either:

1. Split into three linked Plan items (two analytical pages per item), preserving
   styling/content. Recount each item including utility elements before build.
   Cross-item filter synchronization is not promised; sharing a semantic model
   does not share report selection state.
2. Keep one six-page item but simplify/consolidate the native layout/content
   enough to meet 50 owners. Supply an updated preview/count for approval before
   implementing any change to the exact approved blueprint.

The latest instruction authorizes continuing the original blueprint, not a
change in scope. Any actual service rejection or missing content must be
reported rather than worked around or represented as a successful build.

## 1. Identity, binding and delivery

- Approved new Fabric Plan name: **Northsar Leadership 6 Page-AI Created Report 18_Nov**.
- Audience: executives, senior managers and team leads.
- Journey: quick executive view -> business drivers -> exact-number summary
  -> KPI exploration -> dedicated product and geographical investigations.
- Six analytical pages, plus two Help/Info utility sheets if native overlays
  cannot preserve the design and filters. Utility pages are not analytical scope.
- Environment MSIT; Planning-Demos workspace
  `f0000000-0000-4000-8000-0000000000af`.
- Semantic model **SM Sales Performance Dashboard-AI Test**,
  `f0000000-0000-4000-8000-000000000099`.
- Entry: live connected model. Proposed portable binding must be confirmed
  against a coherent native Plan example before definition authoring.
- Intended destination: Planning-Demos > Working folder > Saddam >
  00_AI Skill Test and Report Build,
  folder `f0000000-0000-4000-8000-000000000081` (verified 2026-11-16).
- Create a separate Plan. Never overwrite, rename or restyle an existing report.
- `model_measure_permission: none`. Existing model objects remain read-only.
  No new semantic-model measure is needed or proposed.
- Build and creation in the same model folder are authorized for the approved
  blueprint. Material layout changes, split items or changed filter behavior
  still require the user's decision.

## 2. Evidence and limits

[Field registry](field-registry.md): initial full metadata capture 2026-11-16
14:25 UTC, 7 tables / 51 columns / 36 measures / 5 active relationships.
Measures and expanded data samples refreshed 2026-11-18 09:29 UTC:

- [Current measures](../../_build/executive-summary-design-refresh-18nov/measures.json)
- [All ten annual KPIs and baselines](../../_build/executive-summary-design-refresh-18nov/base-kpis.json)
- [Monthly KPI series](../../_build/executive-summary-design-refresh-18nov/monthly-kpis.json)
- [Product evidence](../../_build/executive-summary-design-refresh-18nov/products.json)
- [State and region evidence](../../_build/executive-summary-design-refresh-18nov/geography.json)

Confirmed: 24 products and 21 states in each of 2024 and 2025; source sales
coverage 2024-01-01 to 2025-12-31. Calendar includes 2026 with no actuals.
All ten 2025 annual PY values match 2024 actuals within 1e-7.
Monthly/product/state sales, gross profit, gross sales, discount and budget
sales reconcile to their annual totals within INR 0.01.
Discount % matches Discount / Gross Sales across all sampled annual, monthly,
product and state contexts within 1e-10. This verifies sampled behavior,
not the unavailable DAX expression.

Measure descriptions exist for 7/36 measures; table/column descriptions are
missing. DAX expressions, model native hierarchies, fiscal-year convention,
business ownership and refresh timestamp are not exposed/verified. No forecast
measure is present. Region filters FactSales through DimCustomer, not directly
through FactSales[RegionKey]. Use existing measures and active relationships.

2025 leadership story: sales INR 9.956M, +8.62% YoY, -3.88% versus budget,
-8.46% versus target; gross margin 29.54%, -0.026 percentage points YoY.
Growth does not imply meeting budget. These signals do not prove root causes.

## 3. Approved visual identity

[Clickable six-page preview](design-preview.html) is the user-selected visual
baseline. Preserve its logo, left rectangular rail, active navigation, panel
treatment, teal/slate palette, typography, spacing and overall 16:9 composition.
Do not introduce a new theme, gradients, decorative icons or IBCS notation.

The KPI grid adapts from nine cards to ten: four budget-comparable KPIs across
the first row, then two rows of three. Styling is retained; compact padding
and chart heights accommodate subtitles without shrinking text or adding
whole-report scrolling. Tables and the slicer area may scroll internally.

Native visuals are mandatory. HTML/SVG in the preview are mockup illustrations,
not components to embed in the final Fabric report. Exact native feature
encoding and rendered fidelity require verification. If a capability cannot
match the approved design, explain the specific difference and obtain approval
instead of silently substituting a different design.

## 4. Six-page plan and visual subtitles

Every visual gets one short title and a plain-language subtitle explaining
what to read, plus units/comparison where needed. No long narrative blocks,
duplicate titles or context-insensitive numerical claims.

| Page | Contents | Example explanatory subtitle |
|---|---|---|
| 1 Executive Overview | Four KPIs; monthly Sales/PY; monthly Sales/Budget/Target; regional Sales/Budget | See how each month compares with last year. |
| 2 Performance Drivers | Category, Region, Customer Segment and Channel Sales/PY comparisons | See which customer segments drive sales versus PY. |
| 3 Detailed Breakdown | Side-by-side product hierarchy and geographic hierarchy Matrices, collapsed initially | Find category budget gaps and profitability. |
| 4 KPI Monitoring | Ten base KPI cards with actual/PY and available budget baselines, native monthly mini-trends | Revenue after discounts. |
| 5 Product Details | Top 10 product Sales/PY; all-category gross margin; all-product detail Matrix | Review all products, budget gaps, profit and units sold. |
| 6 Geographical Analysis | Top 10 state Sales/PY; all-region Sales/Budget; all-state detail Matrix | Review all states, growth, budget gaps and profitability. |

Page 3 is the compact cross-business exact-number view. Pages 5-6 add dedicated
ranked comparisons, volume/order context and full product/state investigation;
they are not copies of Page 3.

### Exact analytical bindings

All measures below have home table `_Measures`.

- Overview cards: Net Sales / BUD Net Sales; Gross Profit / PY Gross Margin;
  Gross Margin % / PY Gross Margin %; Total Orders / PY Total Orders.
  Mini-trend axis DimDate[Month]; order by DimDate[MonthNumber].
- Growth line: DimDate[Month], Net Sales, PY Net Sales.
- Commitment line: DimDate[Month], Net Sales, BUD Net Sales, Target Net Sales.
- Region budget comparisons: DimRegion[RegionName], Net Sales, BUD Net Sales.
- Drivers: each of DimProduct[Category], DimRegion[RegionName],
  DimCustomer[CustomerSegment], DimChannel[ChannelName], with Net Sales and
  PY Net Sales; Gross Margin % in native basic tooltip.
- Summary product Matrix rows: DimProduct[Category] >
  DimProduct[Subcategory] > DimProduct[ProductName].
  Values: Net Sales, BUD Net Sales, visual Budget gap %, Gross Profit,
  Gross Margin %.
- Summary geography Matrix rows: DimRegion[RegionName] > DimCustomer[State].
  Values: Net Sales, PY Net Sales, visual YoY growth %, Gross Margin %.
- Product ranking: DimProduct[ProductName], Net Sales, PY Net Sales.
- Category profitability: DimProduct[Category], Gross Margin %.
- Full product Matrix: Category > Subcategory > ProductName using the exact
  DimProduct fields above; Net Sales, BUD Net Sales, visual Budget gap %,
  Gross Profit, Gross Margin %, Quantity Sold.
- State ranking: DimCustomer[State], Net Sales, PY Net Sales.
- Full geographic Matrix: RegionName > State using the exact fields above;
  Net Sales, PY Net Sales, visual YoY growth %, visual Budget gap %
  (BUD Net Sales is a calculation input), Gross Margin %, Total Orders.

## 5. All ten actual/base KPIs

Base here means actual business measures, excluding separate PY/BUD/Target
scenario copies. It does not imply every measure is a raw SUM.

| Actual measure | Prior-year measure | Budget measure | Short card explanation |
|---|---|---|---|
| Net Sales | PY Net Sales | BUD Net Sales | Revenue after discounts. |
| Gross Profit | PY Gross Margin | BUD Profit Margin | Net sales less product costs. |
| Gross Margin % | PY Gross Margin % | BUD Profit Margin % | Gross profit / net sales. |
| Total COGS | PY Total COGS | BUD COGS | Cost of goods sold. |
| Total Orders | PY Total Orders | None | Distinct completed orders. |
| Quantity Sold | PY Quantity Sold | None | Total units sold. |
| Average Order Value | PY Average Order Value | None | Net sales per distinct order. |
| Gross Sales | PY Gross Sales | None | Sales before discounts. |
| Discount | PY Discount | None | Total discount amount. |
| Discount % | PY Discount % | None | Discount / gross sales. |

Use the existing model measures, including AOV, COGS and Discount %, not
reimplemented model definitions. Gross Profit's PY/budget names misleadingly
say Margin, but sampled values and currency formats identify amounts.
Where budget is absent, show **Not available**, not zero or a fabricated plan.
Do not create a budget by allocating sales targets or copying prior-year data.

Card comparisons: explicit PY/budget values and native signed variances where
legible. Rate changes use percentage points, not relative percentage growth.
COGS, Discount and Discount % changes remain neutral: a higher/lower amount
alone does not establish favorable performance. Other growth cues use the
proposed higher-is-better policy, with direction always visible.

## 6. Shared filters, period and interaction contracts

- Same left rail on all six analytical pages: unchanged logo, six labeled
  navigation buttons with active state, grouped slicers, Help/Info.
- Slicers: DimDate[Year]; DimRegion[RegionName]; DimCustomer[State];
  DimProduct[Category], DimProduct[Subcategory], DimProduct[ProductName],
  DimProduct[Brand]; DimChannel[ChannelName];
  DimCustomer[CustomerSegment], DimCustomer[CustomerName].
- **All selections synchronize across all six pages.** Advanced filters are
  not page-local. Show selected-value summaries even for collapsed groups.
- Year single-select, saved default numeric 2025. All other fields default
  All, allow multi-selection and clearing; long lists use search.
- **Year is the only time slicer**: no Quarter, Month, date range or relative
  date. Headlines cover the full selected year; monthly histories show its
  January-December in calendar order. PY refers to the corresponding previous
  year/months. Budget and target use the same selected year/non-date context.
- Preserve a valid Year when clearing other filters. Native clear semantics
  and optional parent/child filter cascading need capture, not invented keys.
- Year 2024: PY unavailable, not zero. Year 2026: no actuals, explicit no-data
  presentation and no invented decline/growth despite existing PY.
- Navigation and return from Help/Info preserve filters. Chart clicks do not
  silently cross-filter other visuals. Use slicers for shared scope and
  Matrix expand/collapse for local detail. Automatic drill-through is deferred.
- Rank current-year Net Sales descending, label ascending for ties, after all
  selected filters. Top 10 products/states explicitly show subset counts;
  fewer than ten valid members means show fewer, no padding/fake members.
  PY aligns to the same ranked members; blank PY does not remove valid actuals.
- Category, region, segment and channel charts show all members. Full Matrices
  retain all members and full-context totals, not Top-10 subtotals.
- Native basic tooltips with exact values; full product/state labels in detail.
- INR throughout; no exchange conversion or USD relabeling.

### Visual-only calculations

- Budget gap amount = Net Sales - BUD Net Sales.
- Budget gap % = (Net Sales - BUD Net Sales) / BUD Net Sales.
- YoY growth % = (Net Sales - PY Net Sales) / PY Net Sales.
- Rate change pp = 100 * (actual rate - comparison rate).
- Blank/zero denominator -> N/A. No silent infinity or success-shaped zero.
- Ratios recompute from underlying totals, never average member percentages.
  Total Orders is distinct count; do not sum arbitrary displayed subtotals.
- The final native inserted calculations require saved evidence and testing.

## 7. Canonical Design Brief

This YAML is design metadata, not Plan definition JSON. Rectangles are
[x, y, width, height] in design pixels. Named templates expand identically
across analytical sheets; each instantiated element gets a unique visual ID.
Shared title/subtitle placements use each sheet's specified text.

```yaml
Design Brief:
  generated_by: fabric-plan-intelligence
  contract_version: 1
  revision: 4
  mode: greenfield
  phase: implementation_in_progress
  design_identity: {tone: calm executive clarity, signature: branded left rail with progressive analytical depth, ibcs: false}
  session_theme:
    profile_id: f0000000-0000-4000-8000-0000000000a9
    revision: 4
    origin: user_selected
    approval_state: approved_build
    design_source: design-preview.html
    palette: {canvas: "#F5F5F4", surface: "#FFFFFF", text: "#172E3C", muted: "#57534E", actual: "#0F766E", prior_year: "#64748B", budget: "#B45309", target: "#7E22CE", border: "#D6D3D1", favorable: "#166534", adverse: "#B91C1C"}
    typography: {family: Arial, title_px: 27, panel_px: 16, body_px: 14, comparison_px: 12, headline_px: 30}
    components:
      panels: {fill: "#FFFFFF", border_px: 1, radius_px: 5, shadow: none}
      navigation: {normal_fill: "#FFFFFF", normal_text: "#334155", active_fill: "#E5F2F0", active_text: "#115E59", active_left_rule_px: 3}
      buttons: {shape: outlined rectangle, normal_fill: "#FFFFFF", normal_text: "#0F766E", hover_fill: "#E7E5E4", selected_fill: "#0F766E", selected_text: "#FFFFFF", disabled_fill: "#E7E5E4", disabled_text: "#57534E"}
      kpis: native card, single title, short explanation, actual and labeled comparisons, native mini-line
    branding: supplied NORTHSTAR CONSUMER logo unchanged, preserve aspect ratio, white rail
    navigation: six fixed labeled page buttons in left rail; Help/Info below filter area
    page_layouts: shared shell with overview, driver grid, summary matrices, ten-KPI grid, specialist detail
    help_info: native overlays if verified; otherwise same-style utility sheets with return and preserved filters
    inspiration: user-selected preview; no new visual theme
    ibcs: false
    freshness: user explicitly requested exact reuse of this session preview styling
  canvas: {width: 1600, height: 900, units: pixels}
  shared_regions:
    rail: [0, 0, 280, 900]
    header: [308, 28, 1264, 77]
    selection: [308, 121, 1264, 45]
    body: [308, 182, 1264, 656]
    footer: [308, 854, 1264, 28]
  shared_placements:
    - {id: rail_background, region: rail, kind: element:shape, rect: [0, 0, 280, 900], features: [CV-ELEM-01]}
    - {id: logo, region: rail, kind: element:image, rect: [20, 24, 240, 80], features: [CV-ELEM-01]}
    - {id: page_navigation, region: rail, kind: element:navigation, rect: [16, 130, 248, 290], destinations: [Executive Overview, Performance Drivers, Detailed Breakdown, KPI Monitoring, Product Details, Geographical Analysis], features: [CV-ELEM-02]}
    - {id: shared_filters, region: rail, kind: slicer:super-filter-panel, rect: [20, 438, 240, 378], source: section 6 exact field list, features: [SF-FACET-01, SF-FEAT-02, CV-INT-02]}
    - {id: help, region: rail, kind: element:button, rect: [20, 842, 100, 36], text: Help, target: Help content, action: native overlay or utility page navigation, features: [CV-ELEM-02]}
    - {id: info, region: rail, kind: element:button, rect: [132, 842, 100, 36], text: Info, target: Info content, action: native overlay or utility page navigation, features: [CV-ELEM-02]}
    - {id: page_title, region: header, kind: element:text, rect: [308, 43, 1120, 34], text_source: sheet name, features: [CV-ELEM-01]}
    - {id: page_subtitle, region: header, kind: element:text, rect: [308, 83, 1264, 22], text_source: sheet purpose, features: [CV-ELEM-01]}
    - {id: active_filters, region: selection, kind: element:text, rect: [308, 121, 1264, 45], purpose: disclose all restrictions including collapsed slicers, features: [CV-ELEM-01]}
    - {id: source_footer, region: footer, kind: element:text, rect: [308, 854, 1264, 28], text: "Source model | Sales coverage 2024-2025 | Refresh timestamp unverified", features: [CV-ELEM-01]}
  super_filter_layout:
    position: left_rail
    region_ids: [rail]
    order: logo, navigation, slicer groups, Help and Info
    expansion: native verified equivalent of preview groups; independently scroll filters
    shared_selection: all six analytical pages, all listed fields
    default: Year 2025; all other fields All
  sheets:
    - name: Executive Overview
      archetype: Custom
      purpose: Growth, profitability and performance against commitments.
      shared_shell: all shared placements and regions
      layout_contract:
        placements:
          - {id: executive_cards, region: body, kind: four-native-kpis, rect: [308, 182, 1264, 202], gap_px: 14, bindings: section 4 overview cards, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: growth_line, region: body, kind: chart:line, rect: [308, 400, 728, 238], bindings: section 4 growth line, features: [CH-LIB-03]}
          - {id: commitment_line, region: body, kind: chart:line, rect: [1052, 400, 520, 238], bindings: section 4 commitment line, features: [CH-LIB-03]}
          - {id: region_budget, region: body, kind: chart:bar, rect: [308, 654, 1264, 184], bindings: section 4 region budget comparisons, features: [CH-LIB-01]}
      space_audit: {unplaced_regions: [], reason: four KPIs and three comparisons, 16px row gaps}
    - name: Performance Drivers
      archetype: Custom
      purpose: Compare the business areas contributing to the selected-year result.
      shared_shell: all shared placements and regions
      layout_contract:
        placements:
          - {id: category_driver, region: body, kind: chart:bar, rect: [308, 182, 624, 320], axis: "DimProduct[Category]", values: ["_Measures[Net Sales]", "_Measures[PY Net Sales]"], features: [CH-LIB-01, CH-SORT-01, CH-TIP-01]}
          - {id: region_driver, region: body, kind: chart:bar, rect: [948, 182, 624, 320], axis: "DimRegion[RegionName]", values: ["_Measures[Net Sales]", "_Measures[PY Net Sales]"], features: [CH-LIB-01, CH-SORT-01, CH-TIP-01]}
          - {id: segment_driver, region: body, kind: chart:bar, rect: [308, 518, 624, 320], axis: "DimCustomer[CustomerSegment]", values: ["_Measures[Net Sales]", "_Measures[PY Net Sales]"], features: [CH-LIB-01, CH-SORT-01, CH-TIP-01]}
          - {id: channel_driver, region: body, kind: chart:bar, rect: [948, 518, 624, 320], axis: "DimChannel[ChannelName]", values: ["_Measures[Net Sales]", "_Measures[PY Net Sales]"], features: [CH-LIB-01, CH-SORT-01, CH-TIP-01]}
      space_audit: {unplaced_regions: [], reason: equal 2x2 comparisons with 16px gutters}
    - name: Detailed Breakdown
      archetype: Custom
      purpose: Compare category and regional performance in one exact-number view.
      shared_shell: all shared placements and regions
      layout_contract:
        placements:
          - {id: product_summary, region: body, kind: matrix, rect: [308, 182, 717, 656], bindings: section 4 summary product Matrix, features: [MX-VIS-01, MX-LAY-01, MX-HIER-01, MX-VAR-01]}
          - {id: geography_summary, region: body, kind: matrix, rect: [1041, 182, 531, 656], bindings: section 4 summary geography Matrix, features: [MX-VIS-01, MX-LAY-01, MX-HIER-01, MX-VAR-01]}
      space_audit: {unplaced_regions: [], reason: more width for product comparison columns; internal Matrix overflow only}
    - name: KPI Monitoring
      archetype: Custom
      purpose: Track all ten base KPIs against prior year and available budgets.
      shared_shell: all shared placements and regions
      layout_contract:
        placements:
          - {id: budget_comparable_cards, region: body, kind: four-native-kpis, rect: [308, 182, 1264, 198], gap_px: 14, measures: [Net Sales, Gross Profit, Gross Margin %, Total COGS], bindings: section 5, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: demand_cards, region: body, kind: three-native-kpis, rect: [308, 394, 1264, 198], gap_px: 14, measures: [Total Orders, Quantity Sold, Average Order Value], bindings: section 5, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: gross_discount_cards, region: body, kind: three-native-kpis, rect: [308, 606, 1264, 198], gap_px: 14, measures: [Gross Sales, Discount, Discount %], bindings: section 5, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: comparison_caveat, region: body, kind: element:text, rect: [308, 815, 1264, 23], text: "Budget exists for Sales, Profit, Margin and COGS only. Rate changes use pp; cost/discount changes are neutral.", features: [CV-ELEM-01]}
      space_audit: {unplaced_regions: [], reason: ten native cards arranged 4+3+3, no report scrolling}
    - name: Product Details
      archetype: Custom
      purpose: Explore product sales, volume, budget gaps and profitability.
      shared_shell: all shared placements and regions
      layout_contract:
        placements:
          - {id: leading_products, region: body, kind: chart:bar, rect: [308, 182, 728, 340], bindings: section 4 product ranking, top_n: 10, features: [CH-LIB-01, CH-SORT-01]}
          - {id: category_margin, region: body, kind: chart:bar, rect: [1052, 182, 520, 340], bindings: section 4 category profitability, features: [CH-LIB-01]}
          - {id: full_product_detail, region: body, kind: matrix, rect: [308, 538, 1264, 300], bindings: section 4 full product Matrix, features: [MX-VIS-01, MX-LAY-01, MX-HIER-01, MX-VAR-01]}
      space_audit: {unplaced_regions: [], reason: two ranked/context charts above a full-width internally scrolling detail Matrix}
    - name: Geographical Analysis
      archetype: Custom
      purpose: Compare regions and states to identify growth and plan shortfalls.
      shared_shell: all shared placements and regions
      layout_contract:
        placements:
          - {id: leading_states, region: body, kind: chart:bar, rect: [308, 182, 728, 340], bindings: section 4 state ranking, top_n: 10, features: [CH-LIB-01, CH-SORT-01]}
          - {id: regional_budget, region: body, kind: chart:bar, rect: [1052, 182, 520, 340], bindings: section 4 region budget comparisons, features: [CH-LIB-01]}
          - {id: full_geographic_detail, region: body, kind: matrix, rect: [308, 538, 1264, 300], bindings: section 4 full geographic Matrix, features: [MX-VIS-01, MX-LAY-01, MX-HIER-01, MX-VAR-01]}
      space_audit: {unplaced_regions: [], reason: region/state analysis with full state detail, not an unverified map visual}
  accessibility: {contrast: WCAG_AA, color_independent_cues: true, plain_language_titles: true, keyboard_access: required}
  help_info_contract:
    Help: {content: "Navigation, shared slicers, clear selections, tooltips, Matrix expansion", return: preserve source page and filters}
    Info: {content: "Metric definitions, INR, full-year scope, model source, coverage, missing refresh timestamp", return: preserve source page and filters}
    utility_layout: same canvas and visual tokens; title at [308, 43, 1120, 34], text body at [308, 182, 1264, 580], visible return at [308, 790, 240, 36]
```

## 8. Acceptance and implementation gates

The preview passed six-page navigation, logo loading, ten KPI card count,
valid displayed numbers, panel containment and full footer containment inside
the 1600x900 canvas. Product/state tables scroll internally, not the report.
These are mockup checks, not Fabric native-feature acceptance.

Before native authoring, capture coherent saved examples for:
multi-baseline KPI cards; native mini-lines; rate pp comparisons; two-/three-
series lines/bars; short visual subtitles; Matrix layout/hierarchy/variance
columns; search/group expansion/scrolling in the left filter rail; active
selection summaries; all-field sync across six pages; Help/Info return behavior.
Use only verified encodings or complete matching native owners, never guessed
properties. Preserve model fields, no missing-field fallback.

After explicit build approval:

1. Persist the approved session theme and refresh all live metadata/field closure.
2. Author a new local native Intelligence definition matching this contract.
3. Validate with the repository's existing Plan tools and current raw registry.
   Check every field in slicers, sorting, Top N, comparisons and tooltips.
4. Reconcile all ten base KPIs, baselines, full Matrix totals and Top-10 members
   under default and representative combined filter selections. Check actual/PY/
   budget/target connectivity, distinct orders and weighted ratios.
5. Test 2024 missing PY, 2026 empty actuals, zero/blank denominators, chronological
   months, filter clearing, all-field sync and navigation/Help/Info preservation.
6. Visually compare against the chosen preview at matching scale: logo, colors,
   geometry, typography, subtitles, cards, chart legends, readable full labels,
   fixed navigation, expanded filter controls and internal-only scrolling.
7. Publish only after publication authorization, to the verified folder.
   Verify item identity, model binding, folder, API readback, native validation
   and Reading-mode rendering separately. Do not equate static validity with
   runtime acceptance or call native fidelity complete before visual review.

Deferred: forecast, writeback, transaction browsing, automatic drill-through,
rich report-page tooltips, customer-level detail page, unverified map visuals,
metric-switch controls and scheduled distribution. No new external sources.
