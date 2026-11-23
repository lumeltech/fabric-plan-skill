# Field registry - Pharma_Industry_Intelligence_Demo

Workspace: Planning-Demos (`f0000000-0000-4000-8000-0000000000af`)
Semantic model: `f0000000-0000-4000-8000-0000000000da`
Captured: 2026-11-07 via live executeQueries INFO.VIEW queries.
Classification: Internal Only. Keep raw metadata and this brief local.

## Authoritative live metadata

The complete inventory contains 194 columns, 75 measures, 29 relationships,
and 14 visible tables (including the Measure table). Hidden automatic date
tables are excluded from the report-facing inventory below.

Raw responses captured in the current session:

- Tables: `c:\Users\v-sivakumarl\.copilot\session-state\f0000000-0000-4000-8000-0000000000c4\files\info-tables.json`
- Columns: `c:\Users\v-sivakumarl\.copilot\session-state\f0000000-0000-4000-8000-0000000000c4\files\info-columns.json`
- Measures: `c:\Users\v-sivakumarl\.copilot\session-state\f0000000-0000-4000-8000-0000000000c4\files\info-measures.json`
- Relationships: `c:\Users\v-sivakumarl\.copilot\session-state\f0000000-0000-4000-8000-0000000000c4\files\info-relationships.json`

Use the raw columns and measures responses as validation registries; this
human-readable summary does not replace their exact field inventory.

## Dimensions and slicer candidates

All listed report-facing columns are visible. Names include literal table prefixes.
Cardinalities were queried live; unprofiled attributes are marked unknown.

| Table | Columns | Type | Cardinality / notes |
|---|---|---|---|
| [Dim] Date | Date | Date | Monthly calendar; Jan 2023 to Dec 2027 |
| [Dim] Date | Year, Quarter, Month, Year Month, Year Quarter | Text | 60 Year Month members; Quarter sorts by Quarter Num; Month by Month Num |
| [Dim] Sub Region | Region Group, Sub Region, Country, Currency | Text | 5 groups, 15 sub-regions, 12 countries; currency count unknown |
| [Dim] Product | Therapeutic Area, Brand Name, SKU | Text | 5 areas, 11 brands, 28 SKUs; candidate area > brand > SKU hierarchy |
| [Dim] Product | Launch Year, Patent Expiry Year | Integer | Cardinality unknown |
| [Dim] Scenario | Scenario Name | Text | Actual and Plan documented; member count not queried |
| [Dim] Account Tier | Account Name, Account Tier, Account Type, Country | Text | 103 accounts; use searchable dropdown for account names |
| [Dim] Territory | Territory Code, Territory Name | Text | 37 territory names |
| [Dim] Rep | Rep Key, Rep Name, Rep Title, Is Active | Text | Cardinality not queried; avoid personal-level executive detail by default |
| [Dim] Rep | Hire Date | Date | Do not use as the reporting calendar |
| [Dim] Brand | Brand Name, Therapeutic Area, Launch Year, Patent Expiry Year | Text | Shared brand dimension for sales and clinical facts |
| [Dim] Study | Study ID, Therapeutic Area, Phase, Drug Name, Study Status | Text | 15 studies |

## Facts

| Table | Grain / fields | Notes |
|---|---|---|
| [Fact] Sales Performance | Monthly product x sub-region x account x scenario; Revenue, Units, Avg Selling Price | Revenue and ASP are Number; Units is Integer |
| [Fact] Field Force | Monthly rep x territory x scenario; Calls, Visits, Conversions, Effectiveness Score, Coverage Percent | Integer fields; prefer existing ratio measures over summing percentages |
| [Fact] Call Log | Individual call records; Call Date, Call Type, Call Outcome, Call Duration Minutes | Transaction detail, deferred for executive first-build scope |
| [Fact] Clinical Timeline | Tasks/subtasks per study; Study ID, Therapeutic Area, Phase, Drug Name, Study Status, Task Name, Sub Task Name, Start Date, End Date, Planned Start Date, Planned End Date, Milestone Date, Milestone Name, Assigned To, Depends On, Progress, Status, Enrollment Target, Enrollment Actual, Budget Allocated, Delay Days | Clinical fact has no direct active reporting-date relationship in the captured metadata |

## Measures

Home table for all 75 measures: `Measure`. Expressions and format strings
were returned null by the API; do not infer their DAX or formatting.
Tags below are inferred from names and descriptions, not inspected expressions.

| Group | Exact measure names | Scenario / semantics |
|---|---|---|
| Base | Actual Revenue; Plan Revenue; Actual Units; Plan Units | AC / PL |
| Revenue and pricing | Total Revenue; Actual ASP; Plan ASP; Revenue per Account; Brand Count; Active SKU Count | Total Revenue includes all scenarios unless filtered; ASP is weighted, not additive |
| Variance | Revenue Variance; Revenue Variance %; Revenue Variance Abs; Units Variance; Units Variance %; ASP Variance %; Variance Direction | Delta / ratios / text flag; actual versus plan |
| Period trends | Revenue PY; Revenue YoY %; Revenue PM; Revenue MoM %; Revenue 3M Rolling; Revenue 12M Rolling; Revenue YTD; Revenue YTD vs Plan | PY / ratios / rolling / YTD |
| Field force | Actual Calls; Plan Calls; Actual Visits; Plan Visits; Total Conversions; Avg Effectiveness Score; Avg Coverage %; Conversion Rate | AC / PL / averages / ratios |
| Field variance | Call Attainment %; Visit Attainment %; Call Variance; Visit Variance | Ratios / delta |
| Call analytics | Total Calls (Log); Avg Call Duration; Call Completion Rate; In-Person Call %; Virtual Call % | Counts / averages / ratios |
| Clinical | Active Studies; Avg Progress %; Delayed Tasks; On Track Tasks; Enrollment %; Total Budget Allocated; Avg Delay Days | Counts / ratios / budget / average delay |
| Ranking | Revenue Rank; Revenue Cumulative %; Is Top 20% | Context-dependent ranking / ratio / flag |
| Labels | Report Refreshed; Selected Period; Selected Scenario; Selected Geography; Latest Data Month | Labels, not additive numeric KPIs |
| Additional field force | Effectiveness Score Target; Effectiveness Score Var; Active Rep Count; Total Rep Count; Active Rep % | Descriptions unavailable; validate semantics before use |
| Additional commercial | Total Accounts; Bottom Brand by Revenue; Top Brand by Revenue; Plan Revenue per SKU; Actual Revenue per SKU; Leading Market by Revenue; Underperforming Market by Revenue; Total Sub Region; Revenue\Sub Region Actual; Top Account Tier by AC Revenue; Bottom Account Tier by AC Revenue; Top Acct Tier % of AC Revenue; Bottom Acct Tier % of AC Revenue | Descriptions unavailable; validate semantics before use |

## Relationship paths and risks

- Active, one-direction many-to-one: Sales Performance to Date, Product,
  Sub Region, Account Tier and Scenario.
- Active: Product to Brand; Territory to Sub Region; Rep to Territory.
- Active: Field Force to Date, Rep and Scenario; geography filters reach
  Field Force through Sub Region > Territory > Rep.
- Active: Call Log to Date, Rep and Account Tier.
- Active: Clinical Timeline to Study and Brand.
- Inactive: Account Tier to Sub Region; Field Force to Territory and Sub
  Region; Call Log to Territory; Study to Brand through Drug Name.
- Do not assume Product slicers filter clinical facts: the shared Brand
  dimension is the appropriate common brand filter.
- Do not assume the sales date slicer filters clinical tasks. Clinical
  date behavior requires separate scope and explicit interaction design.
- Latest Data Month returned `Dec 2027`, beyond the current date. Treat
  this as demo data, not proof of current real-world performance.
- No forecast measure or margin/cost measure was identified in this inventory.
- Ratios, averages, rankings and labels must not be summed across entities.
- Blank members and measure results in chosen reporting contexts remain
  to be checked once first-build scope is selected.

## Current discovery decisions

- Audience: Executives / leadership - KPIs, trends, risks and decisions.
- Model-measure permission: ask-per-measure; never create without separate approval.
- Phase: spec_approved; discovery finished. No definition files or Fabric writes yet.
- First-build scope: Executive overview only.
- Proposed content: existing commercial KPI measures, monthly actual/plan
  revenue trend, regional variance and brand performance Matrix.
- Field-force and clinical sheets: deferred.
- Delivery: new Plan item in Planning-Demos, as requested by the user.
- Design: proposed clean corporate default, IBCS off.
- Locked report spec: report-spec.md; approved on 2026-11-07 for building and
  publishing a new Plan in Planning-Demos.
