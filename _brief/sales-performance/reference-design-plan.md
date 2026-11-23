# Sales Performance - Executive Summary: reference-matched plan

Status: **published and visually checked for 2025; interaction acceptance incomplete**.
Approved report name: **Sales Performance - Executive Summary-AI Report 16Nov**.
Approved delivery: new Fabric Plan in the previously specified Planning-Demos destination folder.
Latest canvas requirement: **16:9**, overriding the reference-image aspect ratio.
Prepared 2026-11-16 from the user's attached 736 x 454 reference and the live
[field registry](field-registry.md). This replaces the earlier generic overview proposal.
Revised to the user's year-only, existing-measures, clean-ranking and original-title requirements.
Metric-switching buttons/tabs are excluded at the user's request; comparison charts are fixed to Net Sales versus PY Net Sales. No Matrix view or chart/Matrix toggle is included.
A local native definition and [canonical 1600 x 900 contract](design-contract.json) have now been authored. The concrete contract supersedes the older approximate coordinate table below. No semantic-model objects are changed. Publishing and runtime verification are tracked separately.

### Published delivery and remaining acceptance

**Wallpaper distinction (published and visually verified):** changed only the sheet's outside
wallpaper to a neutral gray (#D6D8DD). The pale-blue-gray canvas remains #ECEFF6,
with its existing 1600x900 size, borders, panels and visuals untouched. All 61
parts match live readback and validation returned zero errors. After automatic
refresh, Reading-mode rendering at 83% Fit to Canvas confirms distinct gray
wallpaper around the unchanged lighter canvas.

**Final background-panel cleanup (published and visually verified):** removed
both padding layers from all three analysis background rectangles: outer visual
padding was 8px horizontally/5px vertically, and native shape drawing padding was
5px on every side. Both are now disabled with all stored side values zero.
White fills and thin gray borders now occupy the complete existing shape bounds,
so foreground charts no longer mask inset panel edges or produce stepped seams.
All 12 visible foreground elements remain at least 8px inside their panel bounds.
No chart, text, layer order, dimensions, data, KPI styling or small-multiples
formatting changed. All 61 parts match live readback; validation returned zero
errors. The refreshed report was visually checked in Reading mode at 83% Fit to
Canvas: three continuous white panels with uninterrupted aligned right borders.
The requested visual refinements are finalized; unrelated acceptance gaps below
remain explicitly documented.

**Small-multiples line styling (published and visually verified):** the Top 3
Segment Trends and Top 3 Category Trends charts now use medium-gray (#969696)
prior-year lines at 1.5px. PY was already enabled but had no explicit line color
or stroke settings. Both actual and prior-year point data labels are disabled;
axis ticks, panel titles, legends, tooltips and pale-blue actual lines remain.
All 61 submitted parts match live readback, with zero validation errors and only
the two intended chart parts changed. Reading-mode rendering at 83% Fit to Canvas
confirms visible gray PY lines across all six panels and no point data labels.
KPI cards, dollar formatting, filters, bindings and layout are unchanged.

**Latest KPI styling and spacing override (published):** each of the four native
KPI cards has vertically centered, left-aligned title/value/prior-year text over a pale-purple (#F1F2FB)
number-side background, with a white (#FFFFFF) sparkline container. The native
smallMultipleAppearance panel background fills behind the existing text and badge
containers, extending the purple fill through the full left section without
overlapping those containers. Variance text is centered inside its existing badge;
the mint shape, colours, dimensions and exact position remain unchanged. The visual background stays white with outer padding
disabled. No visuals or groups are added.

Gutters are now 8px between KPI cards, 16px between the KPI and analysis columns,
and 12px between analysis rows/charts, with 8px analysis-panel insets. KPI cards are
448x162px; analysis panels are 1056x216px. Existing IDs and layer order are retained.
All rectangles are updated in both design-contract placement lists and the ID
registry. Text-box heights and zero-padding fixes are preserved. KPI content,
mint badges, dollar/percentage formats, model bindings and the 1600x900 canvas
are unchanged. All 61 parts match live readback; validation returned zero errors.
The alignment-only follow-up is published and all 61 parts match live readback,
with zero validation errors. Final rendering was verified after the user's
refresh in Reading mode at 83% Fit to Canvas: all four main text blocks are
vertically centered and left-aligned, variance text is centered in its existing badge,
pale purple fills the full left section behind the unchanged visible mint badges,
and the sparkline sections remain white. Compact spacing and readable text are
retained, with no text-box scrollbars.
Variance badges remain +8.6%, +8.5%, +11.0% and +7.9%, with their complete saved
container geometry and non-alignment styling unchanged. KPI values, dollar formatting and all layout rectangles
remain unchanged.

**Latest currency override:** the user requested USD presentation using only
the **$** sign. Replace INR/rupee display markers, money-chart prefixes and
currency-card mentions with $. This is report formatting only: numeric values
are unchanged, no exchange-rate conversion is performed, and the semantic model
is not edited. This overrides earlier INR display instructions below; those
earlier references describe the source model, not the current report currency.

Published and verified: all nine monetary visuals use the dollar prefix, including
current/PY KPI mentions and chart formatting. Count KPIs and percentage badges are
unchanged. All 61 submitted parts match the live readback; validation returned zero
errors. Numeric values, model bindings, geometry and text-box fit are unchanged.
After the user's refresh, accessibility confirms the dollar footer. A rendered
chart/card screenshot remains unverified because the browser window is minimized.

Clarified follow-up: append **Top 3 Segment Trends** and **Top 3 Category Trends**
to the existing segment/category section-heading text. These are short titles,
not explanatory paragraphs or a separate right-hand column. Restore the original
306px comparison bars and 660px small multiples; retain the 1600 x 900 canvas.
The earlier two side-note elements are cleared, hidden and retired behind the
panel, because omitting native visual registrations does not delete them.
This correction is published. Exact heading text, restored chart geometry,
hidden/cleared side notes and all other submitted parts were verified in the
live readback; validation returned zero errors.

Text-overflow follow-up (published and visually verified): all ten visible
native text boxes already had padding disabled. Stored inset values were cleared
to zero, padding remains disabled, and heights increased by 8-14px (38px title,
32px other text). Only the two footer boxes moved upward to y834/y868 to fit
within 900px. Chart placements, typography, colours and text are unchanged.
Live readback matched all submitted parts. In the refreshed Reading-mode report
at 93% Fit to Canvas, all ten visible text boxes were readable without scrollbars.

[Open the published report](https://msit.powerbi.com/groups/f0000000-0000-4000-8000-0000000000af/plans/f0000000-0000-4000-8000-000000000087?experience=fabric-developer).
The item is in the approved destination folder. Live readback verified the model
binding, 1600 x 900 canvas, numeric Year default 2025 and the original 25 visual registrations
(27 after the explanatory-note follow-up).
Rendered 2025 KPI totals, comparative-bullet styling and Top N membership were checked.
No new semantic measures were created.

Not yet accepted: Region-to-States cross-filtering and reset; runtime Year
single-select/dropdown behavior and 2024 no-PY presentation. Rich Top-5 hover
panels are not implemented; charts use native basic tooltips. Help/Info is
readable footer guidance rather than clickable actions. Compact month ticks
remain; text-box scrollbar artifacts were resolved in the overflow follow-up.
Native UI automation did not
reliably apply the remaining interaction controls; no ranking changes were
applied or saved during those attempts. These gaps must not be marked complete.

## 1. Design commitment

Reproduce the supplied reference's visual language, not a new theme:

- Pale blue-grey canvas, flat white/off-white panels, fine light-grey borders.
- Dense executive composition: approximately 30% width for four stacked KPI
  panels, 64% for the comparison grid, with the original margins and gaps.
- Small uppercase headings, dark neutral typography, italic comparison subtitle.
- KPI number/comparison/change badge on the left of each card; twelve monthly
  mini-columns on its right.
- Pale blue horizontal comparison bars, thin dark reference ticks, pale
  blue/grey mini-lines, grey monthly columns, coral-red adverse columns/dots,
  and mint change badges. Omit the reference's metric-tab strip.
- Square corners, no heavy shadows, no new gradients or decorative icons.
- Do not copy the European title, currencies, data values or designer credit.
  Use this dataset's labels, INR and actual values.
- Do not impose an IBCS theme: the user requested the image's appearance,
  not strict IBCS notation.

### Palette evidence

These are actual source-image pixel samples, not inferred brand colours.
The image includes several close background shades; a sample does not prove a
single original theme token.

| Role | Sample / proposed token | Evidence |
|---|---|---|
| Main canvas | #ECEFF6 | Sampled at (725,300) |
| Analysis panel | #FFFFFF, with off-white #FAFAFA | White is dominant; #FAFAFA at (690,100) |
| KPI panel | #F1F2FB | Sampled at (25,150) |
| Comparison bar | #CADAFD | Sampled at (355,125) |
| Prior-period column | #C5C7C6 | Sampled at (115,120) |
| Adverse column | #E15759 | Sampled at (183,119) |
| Change badge background | #BEE9DE | Sampled at (40,143) |
| Heading/text and reference tick | #303030 proposed | Visual estimate; verify against rendered reference |
| Fine panel border | #D4D4D4 proposed | Present among dominant image colours |

Use Arial as the proposed close visual match; the source font cannot be
identified conclusively from the raster image. At a 1472 x 908 working canvas,
start with title 20px bold, panel titles 14px, labels 12px and KPI values 28px.
Tune to match proportional sizing, not enlarged typography that changes layout.
Small text must meet AA contrast; retain mint fills and use sufficiently dark
teal/neutral foreground. Flag any needed departure rather than silently
substituting a brighter or unrelated palette.

## 2. Dataset-to-reference mapping

| Reference element | Proposed equivalent in this dataset | Source / status |
|---|---|---|
| European Superstore executive title | COMMERCIAL PERFORMANCE - EXECUTIVE OVERVIEW | Original title; same placement/treatment; no unverified geographic claim |
| Period year/month selectors | One Year dropdown, single-select | DimDate[Year]; default 2025; no Month slicer |
| Sales KPI | Net Sales | _Measures[Net Sales] versus [PY Net Sales], INR |
| Profit KPI | Gross Profit | _Measures[Gross Profit] versus [PY Gross Margin], INR; PY name is misleading but sampled as an amount |
| Orders KPI | Total Orders | _Measures[Total Orders] versus [PY Total Orders] |
| Customers KPI | Units Sold | _Measures[Quantity Sold] versus [PY Quantity Sold]; existing model measures |
| Segment comparison | CustomerSegment comparison | DimCustomer[CustomerSegment], four members |
| Category comparison | Top 5 Product Categories | DimProduct[Category], five of six members, ranked by selected-year Net Sales |
| Regional bars | Region comparison | DimRegion[RegionName], four members |
| Region-dependent state detail | State comparison | DimCustomer[State]; top five within selected region, or top five overall before selection |
| Ship Mode comparison | Sales Channel comparison | DimChannel[ChannelName], four members; Ship Mode is absent |
| Reference metric-tab strip | Omitted | No metric-switching controls or chart/Matrix toggle; four KPI cards remain fixed |

**Required dataset adaptations:** no Ship Mode field exists, so propose Channel
in the same bottom-right visual footprint. Geography uses this model's real
regions/states, not the reference's European members. The user authorized a
different existing KPI and a low-cardinality replacement for Ship Mode.

**Units metric contract:** total units sold, using the existing Quantity Sold
measure and its existing PY counterpart. Units complement revenue, profit and
order count and support the reference's AC/PY monthly mini-charts. This avoids
introducing a customer-count measure. No new semantic-model measure is proposed.

### Original report copy

- Title: **COMMERCIAL PERFORMANCE - EXECUTIVE OVERVIEW**.
- Subtitle: **Full-year 2025 performance compared with 2024**, dynamically
  updated from the selected year; not labelled MTD or YTD.
- KPI labels: **NET SALES**, **GROSS PROFIT**, **TOTAL ORDERS**, **UNITS SOLD**.
- Panel headers: **CUSTOMER SEGMENT PERFORMANCE**, **TOP 5 PRODUCT CATEGORIES**,
  **REGIONAL CONTRIBUTION**, **TOP 5 STATES**, **CHANNEL PERFORMANCE**.
- Trellis captions: **Top 3 segments by Net Sales** and
  **Top 3 categories by Net Sales**.
- All right-hand chart subtitles identify **Net Sales vs. Prior Year (INR)**;
  neither the charts nor their rankings switch to another metric.
- Footer: **Data coverage: 2024-2025 | Selected year: 2025**, plus discreet
  Help/Info links. Do not imply verified worldwide coverage or change INR
  because the intended audience is global.

## 3. Proposed single-sheet composition

Use **1600 x 900 (16:9)**, adapting the reference's relative composition to
the user's latest aspect-ratio requirement. Preserve the left KPI/right
comparison arrangement, palette, typography hierarchy and visual formatting.
These are design coordinates, not Plan JSON or verified native properties.
No scrolling at the intended desktop viewport; scale the whole canvas to fit.

| Region | Approximate x,y,width,height | Contents |
|---|---|---|
| Header | 46,36,950,44 | Title and dynamic comparison-period subtitle |
| Period controls | 1270,36,160,36 | One compact Year dropdown; single-select, 2025 default |
| Legend | 36,120,680,20 | Adverse marker, current period, previous period |
| Left KPI column | 36,148,428,732 | Four cards, roughly 164px high, 24px vertical gaps |
| Segment panel | 508,168,904,210 | Compact segment bars left; three trend panels right |
| Category panel | 508,402,904,210 | Category bars left; three trend panels right |
| Bottom analysis band | 508,648,904,210 | Region, state detail and channel comparison |
| Footer | 36,882,1394,18 | Subtle data-period/Info/Help text; no copied designer signature |

Inside each analysis band, retain thin dividers, small headings and whitespace.
Use all four segment bars and the top five category bars; show three mini-line
panels on the right, explicitly labelled **Top 3 by selected-year Net Sales**.
Do not silently drop members or pretend the reference's three-member segment
dimension matches this model's four. Trellis panels use the selected year's
12-month AC/PY history. Preserve stable, labelled per-panel scales where they
differ, as the reference does.

Proposed data-visual budget: four composite KPI cards, two comparison bar
charts, two trellis chart owners, and three bottom-band charts = 11 data visuals,
plus one small Super Filter and text/Help/Info elements. This count assumes
native trellis/card composition; capture structure before authoring.
There are no alternate metric states, hidden chart copies for switching,
metric navigation buttons or Matrix views. Leave the removed tab strip as
clean background space; retain the chart-panel geometry and reference balance.
Help and Info are proposed as discreet footer links, not new prominent panels.

## 4. Period, comparison and clean-ranking behaviour

- Exactly one slicer: DimDate[Year], single-select with 2025 saved as the
  default. Disable Select All/multi-selection; keep a valid single selection
  when resetting. No month, region, channel or extra page slicers.
- All four headlines show their respective full selected-year KPI values.
  Every comparison chart uses full selected-year Net Sales versus PY Net Sales.
  The native mini-charts show January-December of the same selected year.
- Observed 2025 headlines and PY values:

| KPI | 2025 | 2024 comparison |
|---|---|---|
| Net Sales | INR 9,955,994.58 | INR 9,166,241.99 |
| Gross Profit | INR 2,941,211.34 | INR 2,710,300.94 |
| Total Orders | 3,745 | 3,375 |
| Units Sold | 8,987 | 8,327 |

- Display full selected-year values in headlines, previous-year values below,
  and (AC - PY) / PY in the change badge; no invented value when PY is zero
  or blank. Compact K/M display may be used, with full values in tooltips.
- Each card's monthly chart compares the selected year's months with the same
  calendar months one year earlier. Do not add a selected-month highlight or
  let the monthly axis turn the annual headline into the last month's value.
- Reference tick / previous-period series means PY, not budget or target.
  Existing BUD/Target measures are intentionally outside the initial design;
  adding them would change the reference composition.
- A month is adverse when AC < the same month's PY for these higher-is-better
  metrics. Use signed values and marker/legend cues, not colour alone.
- Total Orders remains evaluated at the full-year context; do not assume that
  arbitrary member-level distinct counts can be added. Units Sold is additive.
- Month labels follow MonthNumber. Keep Year context to avoid merging years.
- Subtitle is dynamic: Full-year <Year> performance compared with <Year-1>.
  2026 must not be the default because it has no actual sales. If a user selects
  2026, show an explicit no-actual-data state, not misleading PY-only growth.
  Selecting 2024 retains actuals but shows comparison unavailable where 2023
  is absent, never fabricated zero-growth values.

### Ranking contract

- Segments: show all four. Regions: show all four. Channels: show all four;
  no Top N is needed for these low-cardinality fields.
- Categories: show Top 5 of six, explicitly labelled; no automatic Others
  row, to keep the reference's compact footprint.
- Trend panels: show Top 3 segments and Top 3 categories, selected once using
  full selected-year Net Sales totals, not re-ranked separately each month.
- State detail: Top 5 overall, or Top 5 within the clicked region.
- Optional segment-hover customer breakdown: Top 5 by Net Sales;
  this ranks customers, it does not introduce a customer-count KPI.
- Rank descending by current-year Net Sales after year and applicable
  region/hover filters; use label ascending as deterministic tie-break. Exclude
  blank labels/blank metric values; show fewer than N when insufficient members
  exist. A blank PY comparison does not remove a valid current-year member.
- Keep current/PY bars and trends aligned to the same ranked members.
  Changing the year or applicable region/hover context recalculates membership. Header KPIs remain full
  population totals, not Top-N subtotals; disclose that ranked charts show
  subsets. Any share denominator is the full applicable population.
- Top 10 is unnecessary in this compact layout; do not add it by default.

## 5. Interactions

- No metric selector, switching buttons, metric tabs, bookmark-based metric
  states, Matrix visual or chart/Matrix toggle. Left KPI cards retain their
  Net Sales/Gross Profit/Total Orders/Units Sold identities; right-hand charts
  stay bound to _Measures[Net Sales] and _Measures[PY Net Sales].
- Segment hover intent from the image: top five customers by Net Sales
  within that segment and selected year, aggregated at customer level.
- Category hover intent: subcategory breakdown for the hovered category.
- Clicking a region should filter the adjacent top-five-state detail. Reset
  returns it to overall top five. Other sections stay unchanged unless the
  final interaction contract explicitly says otherwise.
- Match source captions only after the promised hover/click behaviour works.
  The screenshot proves appearance and intended captions, not native
  tooltip-report wiring or hover-triggered cross-visual filtering.
- The single Year selection applies consistently to annual headlines, annual
  comparison bars and monthly histories. Prior-year measures retain the
  corresponding previous-year context.
- Keep dropdown expansion unclipped; reserve overlay space below the controls.
  Do not replace dropdowns with large filter tiles.
- Help/Info links and region-detail reset are informational/reset controls
  only, not metric or visual-type switching.

## 6. Fabric Plan feature routes and implementation gates

Only native Fabric Plan Intelligence Sheet visuals, not Power BI native visuals,
SVG-rendered KPI charts or a static screenshot background replacing live charts.

| Requirement | Feature routes | Evidence / next verification |
|---|---|---|
| KPI headline and PY change badge | KPI-CARD-01, KPI-VAR-01 | Verified family; validate this layout and date scope |
| Native monthly mini-columns inside KPI | KPI-CHART-01 | Native charts supported; exact comparative column/tick/red-dot preset needs saved sample and runtime validation |
| Horizontal bars and PY reference markers | CH-LIB-01 | Observed; isolate baseline-marker settings |
| Mini-lines / three-panel trellis | CH-LIB-03, CH-MULT-01 | Observed; verify facet context, top-three order, domains and no scrolling |
| Rich hover breakdowns | CH-TIP-01 | Ordinary hover observed; exact top-five/subcategory composition not verified |
| Region-to-state filtering | CV-INT-01 | Observed; verify target and reset behaviour |
| Year dropdown | SF-FACET-01 | Verified; single selection, saved 2025 default, reset and open-list clipping checks required |
| Clean Top 5 / Top 3 subsets | CH-SORT-01 | Observed; capture active ranking and trellis settings, validate membership/ties |
| Background, borders and headings | CV-LAYOUT-01, CV-ELEM-01 | Layout verified; copy native text/shape owners for styling |

Before any implementation, resolve active Top-N
configuration, annual-headline/monthly-chart aggregation and the exact mini-column preset.
Capture additional native samples for each unresolved encoding. If a capability
cannot match the reference, present the specific visual/interaction difference
for approval; do not claim pixel-perfect equivalence in advance.

Metadata limitations remain as documented in the registry: no exposed measure
DAX, no retrieved native hierarchies, limited object descriptions and no
verified refresh timestamp. Do not label the report as live current-year data.

## 7. Approved build sequence

1. Review the revised layout and original report copy, Year-only 2025 default,
   Units Sold replacement, Channel adaptation, fixed Net Sales comparisons,
   omission of switching controls and Top-N definitions.
   Resolve required native capability gates above.
2. Save the complete session theme and canonical Design Brief with exact
   field bindings, placements, filter scopes, accessibility and space audit.
   The palette/layout in this document is the proposed design source, not a
   fabricated native encoding or an already approved theme.
3. Lock the consolidated specification and obtain explicit build approval
   in a later reply. Any model measures need their own approval separately.
4. Build one Intelligence Sheet from coherent UI-saved native examples.
5. Validate live-model field closure, annual and monthly AC/PY values for all
   four existing KPIs, Top-N membership, single-Year scope/default/reset,
   absence of switching controls, fixed chart bindings, dropdown expansion,
   hover, region reset and card mini-charts.
6. Compare the rendered result side by side with the reference at matching
   aspect ratio; check colours, alignment, density, font hierarchy, bars,
   ticks, badges, borders and unclipped labels. Fix visual mismatches before
   claiming fidelity; passing JSON validation is insufficient.
7. Publish only with explicit authorization in Planning-Demos > Working folder >
   Saddam > 00_AI Skill Test and Report Build
   (folder `f0000000-0000-4000-8000-000000000081`), then read back and validate.

**Current outcome:** image inspected, core palette sampled, dataset mapping
revised to the user's latest instructions. Annual values for all four selected
KPI pairs are present in [yearly.json](../../_build/sales-performance-5a5327d4/yearly.json).
Earlier customer-count profiling is historical evidence only, not current
report scope. Monthly Units Sold/PY Units must join the other KPI series in
pre-build validation.
No build, model write, publishing or runtime visual verification has occurred.
