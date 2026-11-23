# Report spec — North Star Consumer Matrix Demo Report AI 19 Nov Test

Status: **approval_pending** (discovery). Nothing has been built or published.

## 1. Report identity
- Plan name: `North Star Consumer Matrix Demo Report AI 19 Nov Test`
  (from the user's "North Star Consumer Matrix demo report AI nineteen November test").
- New plan or existing plan: **new** Plan item.
- Target: workspace **Planning-Demos** › Working folder › Saddam ›
  `00_AI Skill Test and Report Build` (folder ID `f0000000-0000-4000-8000-000000000081`).
- Audience: demo / showcase viewers (not end-user operational reporting).
- Primary purpose: show Matrix capabilities across 5 pages, including
  hierarchies, PY / Budget / Target comparisons and variances, conditional
  formatting (rules, icons, semantic colours), data bars, colour-scale
  gradients, Top N, totals, Super Filter slicers and KPI cards.
- Delivery: new Plan item in the folder above, published only after this spec is approved.

## 2. Semantic model binding
- Module: Intelligence. Source scope: semantic-model-only.
- Entry mode: Live Connected Model.
- Workspace: Planning-Demos (`f0000000-0000-4000-8000-0000000000af`), MSIT tenant.
- Semantic model: SM Sales Performance Dashboard-AI Test (`f0000000-0000-4000-8000-000000000099`).
- Binding form: portable, **including the canonical dataset `url`** in
  `semanticModelReference` (see Risks: the earlier Matrix initialization failure).

## 3. Field registry
- Path: [field-registry.md](field-registry.md). Raw: `_build/northstar-consumer-matrix-19nov/`.
- Captured on 2026-11-19 (UTC) from live INFO.VIEW.* (7 tables, 51 columns,
  36 measures, 5 relationships). DAX came from read-only TMDL `getDefinition`.
- Descriptions: tables 0/7, columns 0/51, measures 7/36 populated. Business
  meaning is mostly inferred from names, folders and DAX.
- Inferred definitions:
  - AC = `Net Sales` etc.
  - Budget = `BUD *`; Target = `Target *`, a second plan scenario.
  - PY = `SAMEPERIODLASTYEAR` of each measure.
  - `BUD/Target Profit Margin` and `PY Gross Margin` are gross-profit **amounts**; the `%` measures are ratios.
- Grain: sales line. Facts cover 2024-01-01 to 2025-12-31. The calendar runs to 2026-12-31.
- Region reaches sales only through `DimCustomer` (customer region). Sampled:
  the totals reconcile.

## 4. User decisions and constraints
- Scope: 5 analysis pages + hidden Help and Info utility pages.
- Interactivity:
  - Top-band Super Filter on every page.
  - Year is synced across pages.
  - Visuals cross-filter each other on each page.
  - Matrix expand/collapse is available.
- Design direction: **Navy/ice, top header with underlined tabs, top-band
  Super Filter** (user-selected). Session profile `st-7f3c91a2` rev 1.
- IBCS: no.
- Number display: **`$` sign** by user choice, even though the source amounts
  are INR. Use K/M scaling with 1 decimal. The Info page discloses the source currency.
- Publishing permission: publish a new Plan item after approval.
- Model-measure permission: **none**. No model measures are needed.
- Data caveats:
  - PY is blank for 2024, so PY variances show only for 2025.
  - Year 2026 has PY values only. Year slicer members are limited to 2024 and 2025, with 2025 as the default.
  - Measure descriptions are mostly missing.

## 5. Narrative
- Core story: 2025 Net Sales of $9.96M grew **+8.6% vs PY**, but came in **−3.9% vs
  Budget** and **−8.5% vs Target**. Gross margin of 29.5% trails Budget (30.4%) and Target (31.6%).
- Key questions:
  1. Where do we stand overall, and in which months and categories? (Overview)
  2. Which products grew or declined versus last year? (Product vs PY)
  3. Where are we missing Budget and Target, and by how much? (Budget & Target)
  4. Which regions, states and cities drive the gaps? (Geography)
  5. Which segments and customers matter, and how do they buy? (Customers)

## 6. Design identity
- Profile `st-7f3c91a2` rev 1 (session file `fabric-plan-intelligence-session-theme.json`).
  Source: user-selected bundle. It differs from the previous NORTHSTAR leadership
  design, which used teal/stone colours and a left rail.
- Palette: navy header `#0B2545`, ice canvas `#F4F7FB`, white panels.
  - Measure colours: AC navy, PY grey `#94A3B8`, Budget teal `#0E7490`, Target amber `#B45309`.
  - Favourable `#15803D`, adverse `#B91C1C`.
- Font: Segoe UI.
- Navigation: underlined tab buttons in the header. The active tab has a light-blue underline.
- Help and Info: outlined buttons at the right end of the header. Each navigates
  to a hidden utility page that has a "Back to report" button.
- Tone: crisp, analytical showcase. Signature: navy header band and gradient Matrix heatmaps.
- All five pages share one layout template:
  - header (row 1)
  - Super Filter band (row 2)
  - KPI strip (rows 3–4)
  - main Matrix (cols 1–8)
  - side Matrix (cols 9–12)

## 7. Sheet plan

Global slicer: `DimDate[Year]` as tiles, limited to 2024 and 2025, default 2025, synced to all pages.

### Sheet 1 — Overview
- Layout: shared analysis template. Purpose: answer "Where do we stand?"
- KPI cards (5):
  - Net Sales vs PY and vs BUD
  - Gross Profit vs PY Gross Margin and vs BUD Profit Margin
  - Gross Margin % vs BUD Profit Margin % (pp)
  - Total Orders vs PY
  - Average Order Value vs PY
  - Each card has a monthly sparkline. Features: KPI-CARD-01, KPI-VAR-01, KPI-CHART-01.
- Main Matrix: **Category × Month heatmap**.
  - Rows `DimProduct[Category]`; columns `DimDate[Month]`; value `Net Sales`.
  - Table-wise sequential **colour-scale gradient**, with row and column totals.
  - Features: MX-VIS-01, MX-CF-02, MX-TOT-01, MX-NUM-01.
- Side Matrix: **Channel vs Budget**.
  - Rows `DimChannel[ChannelName]`.
  - Values `Net Sales`, `BUD Net Sales`, ΔBUD, ΔBUD %.
  - **Data bars** on Net Sales; semantic red/green on the Δ columns.
  - Features: MX-VAR-01, MX-CALC-02, MX-CF-02, MX-NUM-03.
- Slicers: Year (tiles), `DimRegion[RegionName]` (tiles, 4), `DimChannel[ChannelName]` (tiles, 4).
  Features: SF-FACET-01, SF-TB-01, CV-INT-02.

### Sheet 2 — Product vs Prior Year (PY comparison only)
- KPIs (3): Net Sales vs PY, Quantity Sold vs PY, Gross Margin % vs PY (pp).
- Main Matrix: **Product hierarchy**.
  - Rows `Category › Subcategory › ProductName`, expanded to Category by default.
  - Values: `Net Sales`, `PY Net Sales`, ΔPY, ΔPY %, `Quantity Sold`, `PY Quantity Sold`,
    `Gross Margin %`, `PY Gross Margin %`, ΔGM pp.
  - **Data bars** on Net Sales; **in-cell variance bars** on ΔPY;
    **arrow icons** on ΔPY %; semantic colours on Δ. Totals and subtotals are shown.
  - Features: MX-HIER-01, MX-VAR-01, MX-CALC-02, MX-CF-02, MX-CHART-01, MX-CF-03, MX-NUM-03, MX-TOT-01.
- Side Matrix: **Brand ranking**.
  - Rows `DimProduct[Brand]`; values `Net Sales`, ΔPY %; sorted by ΔPY % descending.
  - **Diverging colour scale** on ΔPY %. Features: MX-SRT-01, MX-CF-02.
- Slicers: Year; Month range (`DimDate[Month]` via the Date hierarchy, SF-DATE-02);
  Product hierarchy filter Category › Subcategory (SF-HIER-01); Brand dropdown (SF-FACET-01).

### Sheet 3 — Budget & Target Attainment (BUD + Target + PY)
- KPIs (4): Net Sales vs BUD, Net Sales vs Target, GM % vs BUD %, GM % vs Target %.
- Main Matrix: **Scenario comparison**.
  - Rows `Category › Subcategory`.
  - Column groups:
    - Net Sales: AC, BUD, ΔBUD, ΔBUD %, Target, ΔTGT, ΔTGT %, PY, ΔPY %
    - Gross profit: `Gross Profit`, `BUD Profit Margin`, `Target Profit Margin`
    - Margin: `Gross Margin %`, `BUD Profit Margin %`, `Target Profit Margin %`, Δ pp
  - **CF rules** on ΔBUD % and ΔTGT %: red below −5%, amber from −5% to 0%, green at 0% or above (background plus icon).
  - **In-cell variance bars** on ΔTGT.
  - Features: MX-LAY-02, MX-VAR-01, MX-CALC-02, MX-CF-01, MX-CF-03, MX-CHART-01, MX-NUM-03.
- Side Matrix: **Monthly attainment**.
  - Rows `Quarter › Month`; values AC, BUD, TGT, ΔBUD %, ΔTGT %.
  - **Diverging gradient** on ΔBUD %. Features: MX-HIER-01, MX-CF-02.
- Slicers: Year, Region (tiles), Channel (tiles), Brand (dropdown).

### Sheet 4 — Geography
- KPIs (3): Net Sales vs BUD, Discount %, Gross Margin %.
- Main Matrix: **Region › State › City**.
  - Values: `Net Sales`, `PY Net Sales`, ΔPY %, `BUD Net Sales`, ΔBUD %, `Gross Margin %`, `Discount %`.
  - Data bars on Net Sales, **sequential gradient** on Gross Margin %, icons on ΔBUD %.
  - Features: MX-HIER-01, MX-CF-02, MX-CF-03, MX-CALC-02, MX-TOT-01.
- Side Matrix: **Region × Quarter**. Values: Net Sales ΔPY % with a diverging heatmap. Features: MX-CF-02.
- Slicers: Year; Geography hierarchy filter Region › State › City (SF-HIER-01); Channel tiles.

### Sheet 5 — Customers
- KPIs (4): Net Sales vs PY, Total Orders vs PY, Average Order Value vs PY, Discount % vs PY.
- Main Matrix: **Segment › Customer, Top 10 + Others** per segment.
  - Values: `Net Sales`, `PY Net Sales`, ΔPY %, `Total Orders`, `Average Order Value`, `Gross Margin %`, `Discount %`.
  - Data bars on Net Sales, colour scale on AOV, icons on Discount %.
  - Features: MX-SRT-03, MX-HIER-01, MX-CF-02, MX-CF-03.
- Side Matrix: **Segment × Channel cross-tab**.
  - Value: `Net Sales`, with a table-wise gradient and row and column totals.
  - Features: MX-CF-02, MX-TOT-01.
- Slicers: Year; Segment tiles (4); Region tiles; Customer searchable dropdown
  (250 members; SF-FACET-01 + SF-FEAT-02).

### Utility pages (hidden) — Help and Info
- **Help**: covers tabs, slicers and clearing them, Matrix expand/collapse, colour and icon meaning, and cross-filtering.
- **Info**: covers measure definitions (AC / BUD / Target / PY and variance direction),
  the INR source shown with a `$` sign, data coverage from 2024 to 2025, the absence of PY for 2024, and how Region links to sales.
- Features: CV-ELEM-01, CV-ELEM-02.

## 8. Measures
- Ready in the model:
  - All AC, BUD, Target and PY measures listed above.
  - Non-additive measures: `Total Orders`, `Average Order Value` and all `%` measures.
- Built in Fabric Plan (calculated columns or native variance; no model change):
  - ΔPY = Net Sales − PY Net Sales; ΔPY % = ΔPY / PY Net Sales (blank when PY is blank or 0).
  - ΔBUD, ΔBUD % (against BUD Net Sales); ΔTGT, ΔTGT % (against Target Net Sales).
  - ΔGM pp = Gross Margin % − (PY / BUD / Target) margin %.
  - Polarity: positive is favourable for sales, profit and margin. **Discount % is
    lower-is-better.**
- Model measures proposed: none (permission: none).
- Gaps:
  - The model has no descriptions.
  - No Forecast scenario exists.
  - There are no Product or Geography model hierarchies. They are built as Matrix row hierarchies instead.

## 9. Canonical design contract
```yaml
Design Brief:
  generated_by: fabric-plan-intelligence
  contract_version: 1
  mode: greenfield
  design_system: design/design-system.md
  session_theme:
    profile_id: st-7f3c91a2
    revision: 1
    origin: user_selected
    approval_state: proposed
    palette: {canvas: "#F4F7FB", wallpaper: "#EAF0F7", surface: "#FFFFFF", header: "#0B2545", header_text: "#FFFFFF", header_muted: "#C7D6EA", text: "#0F1B2D", muted: "#475569", border: "#D5DEEA", accent: "#1D4ED8", tab_active_underline: "#7DD3FC", actual: "#0B2545", prior_year: "#94A3B8", budget: "#0E7490", target: "#B45309", favorable: "#15803D", adverse: "#B91C1C", neutral_band: "#D97706"}
    heat_sequential: ["#EFF6FF", "#BFDBFE", "#60A5FA", "#1D4ED8", "#0B2545"]
    heat_diverging: ["#B91C1C", "#FCA5A5", "#F8FAFC", "#86EFAC", "#15803D"]
    typography: {family: "Segoe UI", title_px: 26, tab_px: 15, panel_title_px: 16, body_px: 13, kpi_value_px: 28, kpi_comparison_px: 12}
    numbers: {currency_prefix: "$", source_currency: INR, scaling: "K/M", decimals: 1, pct_decimals: 1, margin_delta_unit: pp}
    components: {container: "white, 1px #D5DEEA border, 6px radius", kpi: "4px left accent in measure colour; value + vs PY / vs BUD signed deltas + sparkline", buttons: "outlined rectangular 4px radius 32px; hover #13315C; selected white text + 3px #7DD3FC underline"}
    navigation: {model: buttons, style: underlined header tabs, order: [Overview, Product vs PY, Budget & Target, Geography, Customers]}
    branding: {logo: omitted, footer: "source/as-of in Info"}
    inspiration: none
    help_info: {placement: "header right", action: "navigate to hidden Help / Info page", return: "Back to report button"}
    ibcs: false
  design_identity: {tone: "crisp analytical showcase", signature: "navy header band + gradient Matrix heatmaps", ibcs: false, ibcs_theme: null}
  color_map:
    strategy: measure_match
    measures:
      "_Measures[Net Sales]": "#0B2545"
      "_Measures[PY Net Sales]": "#94A3B8"
      "_Measures[BUD Net Sales]": "#0E7490"
      "_Measures[Target Net Sales]": "#B45309"
  navigation_model: buttons
  sync_slicers: [{field: "DimDate[Year]", sheets: [all], default: 2025, members: [2024, 2025]}]
  shared_layout: &analysis
    canvas: {type: keep-existing, width: 1920, height: 1080, units: normalized, margin_px: 32, gutter_px: 16}
    grid:
      columns: 12
      rows: 12
      regions: {header: [1,1,13,2], filters: [1,2,13,3], kpis: [1,3,13,5], main: [1,5,9,13], side: [9,5,13,13]}
    shell_placements:
      - {id: sheet_title, region: header, slot: 1, of: 3, kind: element:text}
      - {id: page_nav, region: header, slot: 2, of: 3, kind: element:navigation, destinations: [Overview, Product vs PY, Budget & Target, Geography, Customers], features: [CV-ELEM-02]}
      - {id: help_btn, region: header, slot: 3, of: 3, kind: element:button, text: Help, action: "page navigation to hidden Help", features: [CV-ELEM-02]}
      - {id: info_btn, region: header, slot: 3, of: 3, kind: element:button, text: Info, action: "page navigation to hidden Info", features: [CV-ELEM-02]}
    space_audit: {content_cell_count: 144, placed_cell_count: 144, empty_cell_pct: 0, unplaced_regions: [], largest_region: {name: main, pct_of_content: 44}, balance_rationale: "Main Matrix answers the page question; side Matrix gives a second CF technique"}
  sheets:
    - name: Overview
      role: landing
      archetype: Custom
      layout_variant: navy-top-analysis
      variant_rationale: "User-selected bundle; wide main region suits month columns"
      canvas_background: "#F4F7FB"
      super_filter_layout: {position: top_band, region_ids: [filters], rationale: "3 low-cardinality filters fit one row", overflow_behavior: "single row; tiles wrap none"}
      layout_contract:
        <<: *analysis
        placements:
          - {id: title_overview, region: header, kind: element:text, text: "Overview — where do we stand?"}
          - {id: sf_overview, region: filters, kind: slicer:super-filter, field_bindings: {category: ["DimDate[Year]", "DimRegion[RegionName]", "DimChannel[ChannelName]"]}, features: [SF-FACET-01, SF-TB-01, CV-INT-02]}
          - {id: kpi_ns, region: kpis, slot: 1, of: 5, kind: kpi, purpose: "Are sales ahead of PY and Budget?", field_bindings: {values: ["_Measures[Net Sales]"], comparison: ["_Measures[PY Net Sales]", "_Measures[BUD Net Sales]"]}, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: kpi_gp, region: kpis, slot: 2, of: 5, kind: kpi, purpose: "Is gross profit ahead?", field_bindings: {values: ["_Measures[Gross Profit]"], comparison: ["_Measures[PY Gross Margin]", "_Measures[BUD Profit Margin]"]}, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: kpi_gm, region: kpis, slot: 3, of: 5, kind: kpi, purpose: "Is margin on budget?", field_bindings: {values: ["_Measures[Gross Margin %]"], comparison: ["_Measures[BUD Profit Margin %]"]}, aggregation: ratio, features: [KPI-CARD-01, KPI-VAR-01]}
          - {id: kpi_orders, region: kpis, slot: 4, of: 5, kind: kpi, purpose: "Are orders growing?", field_bindings: {values: ["_Measures[Total Orders]"], comparison: ["_Measures[PY Total Orders]"]}, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: kpi_aov, region: kpis, slot: 5, of: 5, kind: kpi, purpose: "Is order value growing?", field_bindings: {values: ["_Measures[Average Order Value]"], comparison: ["_Measures[PY Average Order Value]"]}, aggregation: ratio, features: [KPI-CARD-01, KPI-VAR-01]}
          - {id: mx_cat_month, region: main, kind: matrix, purpose: "Which categories and months drive sales?", field_bindings: {rows: ["DimProduct[Category]"], columns: ["DimDate[Month]"], values: ["_Measures[Net Sales]"]}, cf: "table-wise sequential colour scale heat_sequential", sort_policy: chronological, features: [MX-VIS-01, MX-CF-02, MX-TOT-01, MX-NUM-01]}
          - {id: mx_channel_bud, region: side, kind: matrix, purpose: "Which channels miss budget?", field_bindings: {rows: ["DimChannel[ChannelName]"], values: ["_Measures[Net Sales]", "_Measures[BUD Net Sales]"]}, calculated: [ΔBUD, ΔBUD %], cf: "data bars on Net Sales; semantic colours on deltas", features: [MX-VAR-01, MX-CALC-02, MX-CF-02, MX-NUM-03]}
    - name: Product vs PY
      role: detail
      archetype: Custom
      layout_variant: navy-top-analysis
      variant_rationale: "Shared template; PY-only comparison page"
      canvas_background: "#F4F7FB"
      super_filter_layout: {position: top_band, region_ids: [filters], rationale: "4 filters incl. hierarchy and month range", overflow_behavior: "hierarchy and dropdown expand downward over KPI strip"}
      layout_contract:
        <<: *analysis
        placements:
          - {id: title_prod, region: header, kind: element:text, text: "Product performance vs prior year"}
          - {id: sf_prod, region: filters, kind: slicer:super-filter, field_bindings: {category: ["DimDate[Year]", "DimDate[Month]", "DimProduct[Category]", "DimProduct[Subcategory]", "DimProduct[Brand]"]}, features: [SF-FACET-01, SF-DATE-02, SF-HIER-01, SF-TB-01]}
          - {id: kpi_p1, region: kpis, slot: 1, of: 3, kind: kpi, purpose: "Sales vs PY?", field_bindings: {values: ["_Measures[Net Sales]"], comparison: ["_Measures[PY Net Sales]"]}, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: kpi_p2, region: kpis, slot: 2, of: 3, kind: kpi, purpose: "Units vs PY?", field_bindings: {values: ["_Measures[Quantity Sold]"], comparison: ["_Measures[PY Quantity Sold]"]}, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: kpi_p3, region: kpis, slot: 3, of: 3, kind: kpi, purpose: "Margin vs PY?", field_bindings: {values: ["_Measures[Gross Margin %]"], comparison: ["_Measures[PY Gross Margin %]"]}, aggregation: ratio, features: [KPI-CARD-01, KPI-VAR-01]}
          - {id: mx_prod_hier, region: main, kind: matrix, purpose: "Which products grew or declined vs PY?", field_bindings: {rows: ["DimProduct[Category]", "DimProduct[Subcategory]", "DimProduct[ProductName]"], values: ["_Measures[Net Sales]", "_Measures[PY Net Sales]", "_Measures[Quantity Sold]", "_Measures[PY Quantity Sold]", "_Measures[Gross Margin %]", "_Measures[PY Gross Margin %]"]}, calculated: [ΔPY, ΔPY %, ΔGM pp], cf: "data bars Net Sales; in-cell variance bars ΔPY; arrow icons ΔPY %; semantic colours", features: [MX-HIER-01, MX-VAR-01, MX-CALC-02, MX-CF-02, MX-CHART-01, MX-CF-03, MX-NUM-03, MX-TOT-01]}
          - {id: mx_brand_rank, region: side, kind: matrix, purpose: "Which brands grew fastest?", field_bindings: {rows: ["DimProduct[Brand]"], values: ["_Measures[Net Sales]", "_Measures[PY Net Sales]"]}, calculated: [ΔPY %], sort_policy: "ΔPY % desc", cf: "diverging colour scale on ΔPY %", features: [MX-SRT-01, MX-CALC-02, MX-CF-02]}
    - name: Budget & Target
      role: detail
      archetype: Custom
      layout_variant: navy-top-analysis
      variant_rationale: "Shared template; multi-scenario variance page"
      canvas_background: "#F4F7FB"
      super_filter_layout: {position: top_band, region_ids: [filters], rationale: "4 filters", overflow_behavior: "dropdown expands downward"}
      layout_contract:
        <<: *analysis
        placements:
          - {id: title_bt, region: header, kind: element:text, text: "Budget & target attainment"}
          - {id: sf_bt, region: filters, kind: slicer:super-filter, field_bindings: {category: ["DimDate[Year]", "DimRegion[RegionName]", "DimChannel[ChannelName]", "DimProduct[Brand]"]}, features: [SF-FACET-01, SF-TB-01]}
          - {id: kpi_b1, region: kpis, slot: 1, of: 4, kind: kpi, purpose: "Sales vs budget?", field_bindings: {values: ["_Measures[Net Sales]"], comparison: ["_Measures[BUD Net Sales]"]}, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: kpi_b2, region: kpis, slot: 2, of: 4, kind: kpi, purpose: "Sales vs target?", field_bindings: {values: ["_Measures[Net Sales]"], comparison: ["_Measures[Target Net Sales]"]}, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: kpi_b3, region: kpis, slot: 3, of: 4, kind: kpi, purpose: "Margin vs budget?", field_bindings: {values: ["_Measures[Gross Margin %]"], comparison: ["_Measures[BUD Profit Margin %]"]}, aggregation: ratio, features: [KPI-CARD-01, KPI-VAR-01]}
          - {id: kpi_b4, region: kpis, slot: 4, of: 4, kind: kpi, purpose: "Margin vs target?", field_bindings: {values: ["_Measures[Gross Margin %]"], comparison: ["_Measures[Target Profit Margin %]"]}, aggregation: ratio, features: [KPI-CARD-01, KPI-VAR-01]}
          - {id: mx_scenarios, region: main, kind: matrix, purpose: "Where are we missing budget and target?", field_bindings: {rows: ["DimProduct[Category]", "DimProduct[Subcategory]"], values: ["_Measures[Net Sales]", "_Measures[BUD Net Sales]", "_Measures[Target Net Sales]", "_Measures[PY Net Sales]", "_Measures[Gross Profit]", "_Measures[BUD Profit Margin]", "_Measures[Target Profit Margin]", "_Measures[Gross Margin %]", "_Measures[BUD Profit Margin %]", "_Measures[Target Profit Margin %]"]}, calculated: [ΔBUD, ΔBUD %, ΔTGT, ΔTGT %, ΔPY %, ΔGM pp vs BUD], cf: "rules on ΔBUD %/ΔTGT %: < -5% red, -5..0 amber, >= 0 green (background + icon); in-cell variance bars on ΔTGT", features: [MX-LAY-02, MX-VAR-01, MX-CALC-02, MX-CF-01, MX-CF-03, MX-CHART-01, MX-NUM-03]}
          - {id: mx_month_attain, region: side, kind: matrix, purpose: "Which months missed plan?", field_bindings: {rows: ["DimDate[Quarter]", "DimDate[Month]"], values: ["_Measures[Net Sales]", "_Measures[BUD Net Sales]", "_Measures[Target Net Sales]"]}, calculated: [ΔBUD %, ΔTGT %], sort_policy: chronological, cf: "diverging gradient on ΔBUD %", features: [MX-HIER-01, MX-CALC-02, MX-CF-02]}
    - name: Geography
      role: detail
      archetype: Custom
      layout_variant: navy-top-analysis
      variant_rationale: "Shared template"
      canvas_background: "#F4F7FB"
      super_filter_layout: {position: top_band, region_ids: [filters], rationale: "Year + geo hierarchy + channel", overflow_behavior: "hierarchy expands downward"}
      layout_contract:
        <<: *analysis
        placements:
          - {id: title_geo, region: header, kind: element:text, text: "Geographic performance"}
          - {id: sf_geo, region: filters, kind: slicer:super-filter, field_bindings: {category: ["DimDate[Year]", "DimRegion[RegionName]", "DimCustomer[State]", "DimCustomer[City]", "DimChannel[ChannelName]"]}, features: [SF-FACET-01, SF-HIER-01, SF-TB-01]}
          - {id: kpi_g1, region: kpis, slot: 1, of: 3, kind: kpi, purpose: "Sales vs budget?", field_bindings: {values: ["_Measures[Net Sales]"], comparison: ["_Measures[BUD Net Sales]"]}, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: kpi_g2, region: kpis, slot: 2, of: 3, kind: kpi, purpose: "Discount vs PY (lower is better)?", field_bindings: {values: ["_Measures[Discount %]"], comparison: ["_Measures[PY Discount %]"]}, polarity: lower_is_better, aggregation: ratio, features: [KPI-CARD-01, KPI-VAR-01]}
          - {id: kpi_g3, region: kpis, slot: 3, of: 3, kind: kpi, purpose: "Margin vs PY?", field_bindings: {values: ["_Measures[Gross Margin %]"], comparison: ["_Measures[PY Gross Margin %]"]}, aggregation: ratio, features: [KPI-CARD-01, KPI-VAR-01]}
          - {id: mx_geo_hier, region: main, kind: matrix, purpose: "Which regions, states and cities drive the gap?", field_bindings: {rows: ["DimRegion[RegionName]", "DimCustomer[State]", "DimCustomer[City]"], values: ["_Measures[Net Sales]", "_Measures[PY Net Sales]", "_Measures[BUD Net Sales]", "_Measures[Gross Margin %]", "_Measures[Discount %]"]}, calculated: [ΔPY %, ΔBUD %], cf: "data bars Net Sales; sequential gradient GM %; icons ΔBUD %", features: [MX-HIER-01, MX-CALC-02, MX-CF-02, MX-CF-03, MX-TOT-01]}
          - {id: mx_region_qtr, region: side, kind: matrix, purpose: "Which region-quarters grew?", field_bindings: {rows: ["DimRegion[RegionName]"], columns: ["DimDate[Quarter]"], values: ["_Measures[Net Sales]", "_Measures[PY Net Sales]"]}, calculated: [ΔPY %], cf: "diverging heatmap on ΔPY %", features: [MX-CALC-02, MX-CF-02]}
    - name: Customers
      role: detail
      archetype: Custom
      layout_variant: navy-top-analysis
      variant_rationale: "Shared template"
      canvas_background: "#F4F7FB"
      super_filter_layout: {position: top_band, region_ids: [filters], rationale: "Customer has 250 members: searchable dropdown", overflow_behavior: "dropdown with search expands downward"}
      layout_contract:
        <<: *analysis
        placements:
          - {id: title_cust, region: header, kind: element:text, text: "Customer insights"}
          - {id: sf_cust, region: filters, kind: slicer:super-filter, field_bindings: {category: ["DimDate[Year]", "DimCustomer[CustomerSegment]", "DimRegion[RegionName]", "DimCustomer[CustomerName]"]}, features: [SF-FACET-01, SF-FEAT-02, SF-TB-01]}
          - {id: kpi_c1, region: kpis, slot: 1, of: 4, kind: kpi, purpose: "Sales vs PY?", field_bindings: {values: ["_Measures[Net Sales]"], comparison: ["_Measures[PY Net Sales]"]}, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: kpi_c2, region: kpis, slot: 2, of: 4, kind: kpi, purpose: "Orders vs PY?", field_bindings: {values: ["_Measures[Total Orders]"], comparison: ["_Measures[PY Total Orders]"]}, features: [KPI-CARD-01, KPI-VAR-01, KPI-CHART-01]}
          - {id: kpi_c3, region: kpis, slot: 3, of: 4, kind: kpi, purpose: "AOV vs PY?", field_bindings: {values: ["_Measures[Average Order Value]"], comparison: ["_Measures[PY Average Order Value]"]}, aggregation: ratio, features: [KPI-CARD-01, KPI-VAR-01]}
          - {id: kpi_c4, region: kpis, slot: 4, of: 4, kind: kpi, purpose: "Discount vs PY (lower is better)?", field_bindings: {values: ["_Measures[Discount %]"], comparison: ["_Measures[PY Discount %]"]}, polarity: lower_is_better, aggregation: ratio, features: [KPI-CARD-01, KPI-VAR-01]}
          - {id: mx_cust_topn, region: main, kind: matrix, purpose: "Who are the top customers per segment?", field_bindings: {rows: ["DimCustomer[CustomerSegment]", "DimCustomer[CustomerName]"], values: ["_Measures[Net Sales]", "_Measures[PY Net Sales]", "_Measures[Total Orders]", "_Measures[Average Order Value]", "_Measures[Gross Margin %]", "_Measures[Discount %]"]}, calculated: [ΔPY %], sort_policy: "Net Sales desc; Top 10 + Others per segment", cf: "data bars Net Sales; colour scale AOV; icons Discount % (lower better)", features: [MX-SRT-03, MX-HIER-01, MX-CALC-02, MX-CF-02, MX-CF-03]}
          - {id: mx_seg_channel, region: side, kind: matrix, purpose: "Which segment buys through which channel?", field_bindings: {rows: ["DimCustomer[CustomerSegment]"], columns: ["DimChannel[ChannelName]"], values: ["_Measures[Net Sales]"]}, cf: "table-wise sequential gradient; row and column totals", features: [MX-CF-02, MX-TOT-01]}
    - name: Help
      role: drill
      hidden: true
      archetype: Custom
      layout_variant: navy-top-utility
      super_filter_layout: {position: none, region_ids: [], rationale: "utility page"}
      layout_contract:
        canvas: {type: keep-existing, width: 1920, height: 1080, units: normalized, margin_px: 32, gutter_px: 16}
        grid: {columns: 12, rows: 12, regions: {header: [1,1,13,2], body: [1,2,13,13]}}
        placements:
          - {id: title_help, region: header, kind: element:text, text: "How to use this report"}
          - {id: help_body, region: body, kind: element:text, content: "tabs, slicers and clear, Matrix expand/collapse, colour/icon legend, cross-filtering", features: [CV-ELEM-01]}
          - {id: help_back, region: header, kind: element:button, text: "Back to report", action: "navigate to Overview", features: [CV-ELEM-02]}
    - name: Info
      role: drill
      hidden: true
      archetype: Custom
      layout_variant: navy-top-utility
      super_filter_layout: {position: none, region_ids: [], rationale: "utility page"}
      layout_contract:
        canvas: {type: keep-existing, width: 1920, height: 1080, units: normalized, margin_px: 32, gutter_px: 16}
        grid: {columns: 12, rows: 12, regions: {header: [1,1,13,2], body: [1,2,13,13]}}
        placements:
          - {id: title_info, region: header, kind: element:text, text: "Definitions and data notes"}
          - {id: info_body, region: body, kind: element:text, content: "AC/BUD/Target/PY definitions, variance = AC − comparison, INR source displayed with $, coverage 2024–2025, no PY for 2024, region via customer", features: [CV-ELEM-01]}
          - {id: info_back, region: header, kind: element:button, text: "Back to report", action: "navigate to Overview", features: [CV-ELEM-02]}
  interaction_pattern: cross_filter
  accessibility: {contrast: WCAG_AA, color_independent_cues: true, titles_plain_language: true, notes: "icons accompany red/green; white on #0B2545 header passes AA"}
```

## 10. Implementation notes
- Starting point:
  - Native template or readback for the Plan shell.
  - `_samples/pharma-native` provides the saved Matrix scenario buckets
    (`ameasure`/`plmeasure`/`pymeasure`), variance properties and colour-scale rules.
- Encoding status of the features used:

  | Feature | IDs | Status |
  |---|---|---|
  | CF rules, KPI cards, KPI variance, KPI sparklines, facet slicer, navigation, semantic formatting | MX-CF-01, KPI-CARD-01, KPI-VAR-01, KPI-CHART-01, SF-FACET-01, CV-ELEM-02, MX-NUM-03 | verified |
  | Colour scales, icons, hierarchy, totals, calculated columns, Top N, hierarchy/date slicers | MX-CF-02, MX-CF-03, MX-HIER-01, MX-TOT-01, MX-CALC-02, MX-SRT-03, SF-HIER-01, SF-DATE-02 | observed; copy from native samples |
  | Variance columns, in-cell variance bars, sort | MX-VAR-01, MX-CHART-01, MX-SRT-01 | **unverified** |
  | Data bars (part of MX-CF-02) | MX-CF-02 | **no native evidence** |

  Capture plan for the unverified items:
  1. Publish the smoke-test plan (below).
  2. Ask the user to add one data bar, one in-cell variance bar and one variance column in the editor.
  3. Read the plan back and record each encoding in the ledger.
  4. If a capture fails, fall back to calculated-column variances with semantic
     colours, or a colour scale, so that page stays truthful.
- Build order (de-risking):
  1. **Smoke test.** Publish a one-page plan with a single Matrix. Include the dataset
     `url` in `semanticModelReference`, and confirm the Matrix initializes in the browser.
  2. Capture the unverified encodings on that plan.
  3. Author all pages locally.
  4. Run `plan_def.py validate --registry` for field closure.
  5. Publish, poll the operation, read back and re-validate.
  6. Run rendered acceptance with the pre-flight checklist.
- Publishing boundary: create a new Plan item only, in folder `1806eea4-…`.
  The semantic model is not modified.
- Risks:
  - **Matrix initialization.** The prior report on this model showed
    `Failed to initialize application: unreachable`. The cause was a missing `url` in the
    saved `semanticModelReference`, and a later fix did not persist. The smoke test gates the full build.
  - Long-running update operations have previously failed with `UnknownError`.
    The definition will be kept compact, and readback is authoritative.
  - Data has PY only for 2025 and a 2026 calendar year with PY only. The Year slicer is restricted.
  - Displaying a `$` sign over INR data is a user display choice. It is disclosed on the Info page.
