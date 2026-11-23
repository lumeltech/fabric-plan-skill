# Report spec - Pharma Executive Overview

## 1. Report identity

- Plan name: Pharma Executive Overview.
- New Plan item, not a Power BI report or an update to an existing item.
- Audience: Executives / leadership.
- Purpose: track commercial performance against plan and prior year, identify
  regional gaps and understand brand contribution.
- Delivery: create and publish in Planning-Demos after approval of this spec.

## 2. Semantic model binding

- Entry mode: Live Connected Model.
- Workspace: Planning-Demos (`f0000000-0000-4000-8000-0000000000af`).
- Model: Pharma_Industry_Intelligence_Demo
  (`f0000000-0000-4000-8000-0000000000da`).
- Binding form: portable, preserving native binding encoding.

## 3. Field registry

- [Current field registry](field-registry.md), captured 2026-11-07.
- Complete raw columns and measures responses are referenced there.
- Refresh live metadata before implementation and validation.

## 4. User decisions and constraints

- One Intelligence Sheet: Executive Overview.
- Field-force and clinical sheets are deferred.
- User requested creation in the same workspace; publishing target is explicit.
- Proposed design default: clean corporate, white panels, navy typography,
  blue actuals and grey plan. IBCS is off unless requested.
- Model-measure permission: ask-per-measure. No new measure is needed here.
- Data is a demo with actuals through December 2027. Display that caveat.
- Default period: January-December 2027, the latest complete demo year.
  Users can change the range; do not use today's date to hide demo data.
- Geography and therapeutic area default to all members.
- Do not use a scenario slicer: compare explicit Actual and Plan measures.
- No currency symbol until the model's reporting currency is verified.

## 5. Narrative

Are we on plan, how is performance changing, and which regions and brands
explain the gap?

Reading order: headline KPIs, monthly trend and regional variance, brand detail.

## 6. Design identity

Professional, restrained and decision-oriented. Consistent actual/plan colours
and clear signed variance labels; colour is never the only indication of a gap.

## 7. Sheet plan

- Six KPI cards: Actual Revenue, Plan Revenue, Revenue Variance %,
  Revenue YoY %, Actual Units and Actual ASP (`KPI-CARD-01`).
- Monthly line chart: Year Month, Actual Revenue and Plan Revenue
  (`CH-LIB-03`).
- Horizontal regional chart: Sub Region and Revenue Variance, with context
  identifying Actual Revenue minus Plan Revenue (`CH-LIB-01`).
- Brand Matrix: Brand Name with Actual Revenue, Plan Revenue,
  Revenue Variance, Revenue Variance %, Revenue YoY %, Actual Units and
  Actual ASP (`MX-LAY-01`). Show all 11 brands; no invented Top N settings.
- Super Filter date range on Date (`SF-DATE-01`).
- Facet dropdowns on Region Group and Therapeutic Area (`SF-FACET-01`).
- All three slicers filter all data visuals. Charts and Matrix cross-filter
  each other, using native interaction encoding (`CV-INT-01`).
- A sheet title and demo-data subtitle are required (`CV-ELEM-01`).

## 8. Measures

- All measures already exist in home table `Measure`.
- No visual calculations or model measures are proposed.
- Variance is the existing actual-minus-plan measure; no native variance
  calculation encoding is needed.
- Evaluate ratios and weighted ASP in each context, never sum displayed ratios.
- Forecast, margin and cost are outside scope; no such measures were identified.

## 9. Canonical design contract

```yaml
Design Brief:
  generated_by: fabric-plan-intelligence
  contract_version: 1
  mode: greenfield
  design_system: design/design-system.md
  report:
    name: Pharma Executive Overview
    workspace_id: f0000000-0000-4000-8000-0000000000af
    semantic_model_id: f0000000-0000-4000-8000-0000000000da
    delivery: new_plan_in_same_workspace
    approval_status: approved
    model_measure_permission: ask-per-measure
  design_identity:
    tone: professional and restrained
    signature: consistent actual-versus-plan colours and signed variance labels
    ibcs: false
    ibcs_theme: null
  color_map:
    strategy: measure_match
    measures:
      "Measure[Actual Revenue]": "#1D4ED8"
      "Measure[Plan Revenue]": "#475569"
      "Measure[Revenue Variance]": "#1E293B"
      "Measure[Revenue Variance %]": "#1E293B"
      "Measure[Revenue YoY %]": "#1E293B"
      "Measure[Actual Units]": "#1E293B"
      "Measure[Actual ASP]": "#1E293B"
  navigation_model: sheet_tabs
  sync_slicers: []
  sheets:
    - name: Executive Overview
      role: landing
      archetype: Executive Summary
      layout_variant: A
      variant_rationale: six commercial KPIs above trends, regional gaps and brand detail
      canvas_background: "#FFFFFF"
      layout_contract:
        canvas: {type: keep-existing, width: 1920, height: 1080, units: normalized, margin_px: 32, gutter_px: 16}
        grid:
          columns: 12
          rows: 12
          regions:
            header: [1, 1, 13, 2]
            filters: [1, 2, 13, 3]
            kpis: [1, 3, 13, 5]
            trend: [1, 5, 9, 9]
            regional: [9, 5, 13, 9]
            detail: [1, 9, 13, 13]
        placements:
          - {id: sheet_title, region: header, slot: 1, of: 2, kind: "element:text", text: "Pharma Executive Overview", features: [CV-ELEM-01]}
          - {id: demo_subtitle, region: header, slot: 2, of: 2, kind: "element:text", text: "Demo data through Dec 2027 | Actual versus Plan", features: [CV-ELEM-01]}
          - id: slicer_period
            region: filters
            slot: 1
            of: 3
            kind: slicer:date-range
            purpose: choose the reporting period
            field_bindings: {category: ["[Dim] Date[Date]"]}
            default_range: {start: "2027-01-01", end: "2027-12-01"}
            features: [SF-DATE-01]
          - id: slicer_geography
            region: filters
            slot: 2
            of: 3
            kind: slicer:dropdown
            purpose: focus on a geographic group
            field_bindings: {category: ["[Dim] Sub Region[Region Group]"]}
            default_selection: all
            features: [SF-FACET-01]
          - id: slicer_therapeutic_area
            region: filters
            slot: 3
            of: 3
            kind: slicer:dropdown
            purpose: focus on a therapeutic area
            field_bindings: {category: ["[Dim] Product[Therapeutic Area]"]}
            default_selection: all
            features: [SF-FACET-01]
          - {id: kpi_actual_revenue, region: kpis, slot: 1, of: 6, kind: kpi, purpose: actual revenue, field_bindings: {values: ["Measure[Actual Revenue]"]}, features: [KPI-CARD-01]}
          - {id: kpi_plan_revenue, region: kpis, slot: 2, of: 6, kind: kpi, purpose: planned revenue, field_bindings: {values: ["Measure[Plan Revenue]"]}, features: [KPI-CARD-01]}
          - {id: kpi_variance, region: kpis, slot: 3, of: 6, kind: kpi, purpose: revenue gap as a percentage of plan, field_bindings: {values: ["Measure[Revenue Variance %]"]}, features: [KPI-CARD-01]}
          - {id: kpi_yoy, region: kpis, slot: 4, of: 6, kind: kpi, purpose: revenue growth versus prior year, field_bindings: {values: ["Measure[Revenue YoY %]"]}, features: [KPI-CARD-01]}
          - {id: kpi_units, region: kpis, slot: 5, of: 6, kind: kpi, purpose: actual units sold, field_bindings: {values: ["Measure[Actual Units]"]}, features: [KPI-CARD-01]}
          - {id: kpi_asp, region: kpis, slot: 6, of: 6, kind: kpi, purpose: weighted actual selling price, field_bindings: {values: ["Measure[Actual ASP]"]}, features: [KPI-CARD-01]}
          - id: revenue_trend
            region: trend
            kind: chart:line
            purpose: compare monthly actual revenue with plan
            field_bindings:
              category: ["[Dim] Date[Year Month]"]
              values: ["Measure[Actual Revenue]", "Measure[Plan Revenue]"]
            features: [CH-LIB-03]
          - id: regional_variance
            region: regional
            kind: chart:bar
            purpose: identify regional revenue gaps - actual minus plan
            field_bindings:
              category: ["[Dim] Sub Region[Sub Region]"]
              values: ["Measure[Revenue Variance]"]
            comparison_measures: ["Measure[Actual Revenue]", "Measure[Plan Revenue]"]
            features: [CH-LIB-01]
          - id: brand_matrix
            region: detail
            kind: matrix
            purpose: compare all brands and identify contributors to the plan gap
            field_bindings:
              rows: ["[Dim] Product[Brand Name]"]
              values: ["Measure[Actual Revenue]", "Measure[Plan Revenue]", "Measure[Revenue Variance]", "Measure[Revenue Variance %]", "Measure[Revenue YoY %]", "Measure[Actual Units]", "Measure[Actual ASP]"]
            features: [MX-LAY-01]
      space_audit:
        content_cell_count: 144
        placed_cell_count: 144
        empty_cell_pct: 0
        unplaced_regions: []
        largest_region: {name: detail, pct_of_content: 33.3333}
        balance_rationale: brand detail occupies the full lower third; trend and regional gap share the middle band
  interaction_pattern: cross_filter
  accessibility:
    contrast: WCAG_AA
    color_independent_cues: true
    titles_plain_language: true
    alt_text: required for each chart and KPI
```

## 10. Implementation notes

- Native starting definition: not yet selected. After approval, resolve existing
  Plan items and capture suitable working visuals or use native UI creation.
- Unverified encodings: KPI cards, line/bar charts and text elements.
- Observed, not isolated: Matrix layout, date/facet slicers and interactions.
- Capture plan: read saved native visual definitions for each required feature.
  Copy complete working settings groups; never invent JSON keys or enum values.
- If samples cannot be obtained, stop and request native samples rather than
  publish an incomplete or speculative definition.
- Before implementation, query selected-period measures to check nonblank
  results, ratio semantics and reporting currency. Report blockers explicitly.
- Validate every assigned field against refreshed live raw metadata, then run
  definition validation. Check feature IDs, layout coverage and contrast.
- Confirm create permission at publish time; approval does not prove permission.
- Create only a new Plan. If the name already exists, ask before replacing it.
- Spec approved by the user on 2026-11-07. Implementation resumes after
  this discovery approval turn; poll any long-running
  operation and read back the definition, binding, sheet and visual inventory.
- API acceptance and readback are separate from actual UI rendering. Verify
  rendering in the browser when available; otherwise report that layer as unverified.
