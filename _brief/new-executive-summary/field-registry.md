# Live field registry - new executive summary

Captured 2026-11-16 14:25 UTC through read-only Power BI executeQueries.
Model: SM Sales Performance Dashboard-AI Test.
Workspace: Planning-Demos (`f0000000-0000-4000-8000-0000000000af`).
Semantic model: `f0000000-0000-4000-8000-000000000099`.

This is a fresh capture for this task, not a reuse of the earlier report registry.
Raw responses are authoritative, including original formats, descriptions,
hidden flags, sort columns and all technical objects:

- [Tables](../../_build/executive-summary-discovery-16nov-1953/tables.json)
- [Columns](../../_build/executive-summary-discovery-16nov-1953/columns.json)
- [Measures](../../_build/executive-summary-discovery-16nov-1953/measures.json)
- [Relationships](../../_build/executive-summary-discovery-16nov-1953/relationships.json)

## Coverage and limitations

- 7 tables, 51 columns (including 7 internal row-number columns), 36 measures.
- Descriptions populated: tables 0/7, columns 0/51, measures 7/36.
- All four metadata queries succeeded without returned errors; counts match
  their complete returned row sets. No reported truncation.
- All tables use Import storage. All 36 measures are visible.
- All measure expressions returned null: definitions are unavailable through
  this capture, not proven absent. Native hierarchy objects were not retrieved.
- No calculation-group table is indicated by the returned table inventory.
- Currency is INR, evidenced by source names and existing measure formats.
- Refresh timestamp, fiscal-year convention and business ownership are unverified.
- This is scoped report discovery, not a complete data-quality or security audit.

## 2026-11-18 measure and data refresh

Live INFO.VIEW.MEASURES() at 09:29 UTC returned the same 36 measure names,
including exactly ten actual/base measures after excluding PY, BUD and Target
scenario copies. This refresh did not recapture columns/tables/relationships;
their complete inventory below remains dated 2026-11-16 and must be refreshed
again before native authoring/validation.

- [Refreshed measures](../../_build/executive-summary-design-refresh-18nov/measures.json):
  still 7 populated descriptions; all expressions unavailable.
- [Annual base KPIs](../../_build/executive-summary-design-refresh-18nov/base-kpis.json):
  all ten actual measures and their PY measures queried directly. All ten
  2025 PY values match 2024 actuals within 1e-7.
- [Monthly base KPIs](../../_build/executive-summary-design-refresh-18nov/monthly-kpis.json):
  24 month rows for 2024-2025, including Gross Sales, Discount, Discount %,
  Average Order Value and Total COGS directly from existing model measures.
- [Product samples](../../_build/executive-summary-design-refresh-18nov/products.json):
  24 products per year, Category/Subcategory/ProductName and financial/volume
  measures. [Geography samples](../../_build/executive-summary-design-refresh-18nov/geography.json):
  21 states per year with RegionName and financial/order measures.
- Monthly/product/state sales, gross profit, gross sales, discount and budget
  sales reconcile to annual measures within INR 0.01 for each sampled year.
- **Discount % is now selected:** it matches Discount / Gross Sales across
  all returned nonblank annual, monthly, product and state contexts within
  1e-10. Gross Sales - Discount matches Net Sales within INR 0.01.
  The denominator is behaviorally verified in these contexts; DAX remains
  unavailable. PY Discount % matches the previous year's observed rate.
- Rate KPIs are weighted ratios, not additive. Changes use percentage points.
  Cost and discount movements have neutral comparison direction until a
  business favorability rule is approved. No budget counterpart is exposed
  for Orders, Quantity, AOV, Gross Sales, Discount or Discount %.

## Table context

Roles/grain below are inferred from metadata and profiled data; descriptions
are missing for every table.

- FactSales: sales-line fact; 13,698 rows and 13,698 distinct SalesLineKey values.
- DimDate: time dimension, 1,096 calendar days, 2024-01-01 to 2026-12-31.
- DimCustomer: customer/segment/state dimension.
- DimProduct: product/category/subcategory/brand dimension.
- DimChannel: channel dimension.
- DimRegion: region dimension; reaches sales through DimCustomer.
- _Measures: measure home/helper table; hidden Column1 is not a report field.

## Columns

All descriptions are missing. Hidden technical fields remain inventoried but
are not proposed as display fields. Every table also has the hidden Integer
column `RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61`; these seven columns
are present in the raw inventory and account for the difference from 44 below.

| Table | Column | Type | Hidden | Context |
|---|---|---|---|---|
| DimChannel | ChannelKey | Integer | true | Relationship key |
| DimChannel | ChannelName | Text | false | 4 distinct |
| DimCustomer | CustomerKey | Integer | true | Relationship key |
| DimCustomer | CustomerName | Text | false | 250 distinct; no tile selector |
| DimCustomer | CustomerSegment | Text | false | 4 distinct |
| DimCustomer | City | Text | false | Not selected |
| DimCustomer | State | Text | false | 21 distinct; optional later detail |
| DimCustomer | RegionKey | Integer | true | Region relationship |
| DimCustomer | CustomerStatus | Text | true | Do not invent order-status rules |
| DimDate | DateKey | Integer | true | Relationship key |
| DimDate | Date | Date | false | Calendar date |
| DimDate | MonthNumber | Integer | true | Chronological sort helper |
| DimDate | Year | Integer | false | 2024, 2025, 2026 |
| DimDate | Quarter | Text | false | Retain Year context |
| DimDate | Month | Text | false | SortByColumn = MonthNumber |
| DimProduct | ProductKey | Integer | true | Relationship key |
| DimProduct | ProductName | Text | false | 24 distinct |
| DimProduct | Category | Text | false | 6 distinct |
| DimProduct | Subcategory | Text | false | Not selected |
| DimProduct | Brand | Text | false | Not selected |
| DimProduct | ListPriceINR | Integer | true | Attribute, not revenue |
| DimProduct | StandardCostRatio | Number | true | Attribute, not aggregate margin |
| DimRegion | RegionKey | Integer | true | Relationship key |
| DimRegion | RegionName | Text | false | 4 distinct |
| FactSales | SalesLineKey | Integer | false | Unique observed line identifier |
| FactSales | OrderID | Text | true | 7,120 distinct across both years |
| FactSales | OrderDateKey | Integer | true | Active date key |
| FactSales | CustomerKey | Integer | true | Active customer key |
| FactSales | ProductKey | Integer | true | Active product key |
| FactSales | RegionKey | Integer | true | No direct region relationship |
| FactSales | ChannelKey | Integer | true | Active channel key |
| FactSales | Quantity | Integer | false | Prefer existing Quantity Sold |
| FactSales | UnitPriceINR | Number | false | Not additive |
| FactSales | NetRevenueINR | Number | false | Source sales amount |
| FactSales | COGSINR | Number | false | Source cost amount |
| FactSales | GrossSalesINR | Number | false | Source gross sales |
| FactSales | DiscountAmountINR | Number | false | Source discount |
| FactSales | BudgetNetRevenueINR | Number | false | Source budget sales |
| FactSales | BudgetCOGSINR | Number | false | Source budget cost |
| FactSales | BudgetGrossProfitINR | Number | false | Source budget profit |
| FactSales | TargetNetRevenueINR | Number | false | Source target sales |
| FactSales | TargetCOGSINR | Number | false | Source target cost |
| FactSales | TargetGrossProfitINR | Number | false | Source target profit |
| _Measures | Column1 | Text | true | Helper only |

## Measures

All measures belong to _Measures. Unit/scenario classifications are inferred
from names, formats, descriptions and sampled behavior, not retrieved DAX.
AC = actual, PY = prior year, BUD = budget; target is separate from budget.

| Home table | Measure | Unit / scenario | Original description or qualification |
|---|---|---|---|
| _Measures | Net Sales | INR / AC | Net revenue after discounts. |
| _Measures | Quantity Sold | Units / AC | Total units sold. |
| _Measures | Total Orders | Count / AC | Distinct completed orders. |
| _Measures | Average Order Value | INR/order / AC | Net sales divided by distinct orders. |
| _Measures | Total COGS | INR / AC | Cost of goods sold. |
| _Measures | Gross Profit | INR / AC | Net revenue less COGS. |
| _Measures | Gross Margin % | Percent / AC | Gross profit divided by net sales. |
| _Measures | PY Net Sales | INR / PY | Description missing; annual/monthly behavior checked |
| _Measures | PY Total Orders | Count / PY | Description missing; annual/monthly behavior checked |
| _Measures | PY Quantity Sold | Units / PY | Description missing; annual/monthly behavior checked |
| _Measures | PY Average Order Value | INR/order / PY | Description missing |
| _Measures | PY Total COGS | INR / PY | Description missing |
| _Measures | PY Gross Margin | INR / PY | Description missing; sampled as prior-year Gross Profit, not a rate |
| _Measures | PY Gross Margin % | Percent / PY | Description missing; sampled as prior-year margin rate |
| _Measures | Gross Sales | INR / AC | Description missing |
| _Measures | Discount | INR / AC | Description missing |
| _Measures | PY Discount | INR / PY | Description missing |
| _Measures | PY Gross Sales | INR / PY | Description missing |
| _Measures | BUD Net Sales | INR / BUD | Description missing; annual source sum checked |
| _Measures | BUD COGS | INR / BUD | Description missing |
| _Measures | BUD Profit Margin | INR / BUD | Description missing; amount format, not a rate |
| _Measures | BUD Profit Margin % | Percent / BUD | Description missing |
| _Measures | Target Net Sales | INR / Target | Description missing; annual source sum checked |
| _Measures | Target COGS | INR / Target | Description missing |
| _Measures | Target Profit Margin | INR / Target | Description missing; amount format, not a rate |
| _Measures | Target Profit Margin % | Percent / Target | Description missing |
| _Measures | PY BUD COGS | INR / PY BUD | Description missing |
| _Measures | PY BUD Net Sales | INR / PY BUD | Description missing |
| _Measures | PY BUD Profit Margin | INR / PY BUD | Description missing |
| _Measures | PY BUD Profit Margin % | Percent / PY BUD | Description missing |
| _Measures | PY Target Net Sales | INR / PY Target | Description missing |
| _Measures | PY Target COGS | INR / PY Target | Description missing |
| _Measures | PY Target Profit Margin | INR / PY Target | Description missing |
| _Measures | PY Target Profit Margin % | Percent / PY Target | Description missing |
| _Measures | Discount % | Percent / AC | Description missing; sampled Discount / Gross Sales, selected |
| _Measures | PY Discount % | Percent / PY | Description missing; sampled prior-year discount rate, selected |

## Relationships

All five are active, many-to-one, single-direction from dimension to fact side.

| From | To | Direction |
|---|---|---|
| DimCustomer[RegionKey] | DimRegion[RegionKey] | DimRegion to DimCustomer |
| FactSales[ChannelKey] | DimChannel[ChannelKey] | DimChannel to FactSales |
| FactSales[CustomerKey] | DimCustomer[CustomerKey] | DimCustomer to FactSales |
| FactSales[ProductKey] | DimProduct[ProductKey] | DimProduct to FactSales |
| FactSales[OrderDateKey] | DimDate[DateKey] | DimDate to FactSales |

## Data verification

- [Profile](../../_build/executive-summary-discovery-16nov-1953/profile.json):
  sales dates 2024-01-01 to 2025-12-31. Calendar includes 2026 without actuals.
- [Yearly](../../_build/executive-summary-discovery-16nov-1953/yearly.json)
  and [monthly](../../_build/executive-summary-discovery-16nov-1953/monthly.json):
  both years' monthly sales, profit, orders, units, budget and target reconcile
  to annual measures within 0.01; 2025 annual and monthly PY sales/profit/orders/
  units match the corresponding 2024 actuals within 0.01.
- Sales/profit/budget/target source identities reconcile within INR 0.01.
- [Breakdowns](../../_build/executive-summary-discovery-16nov-1953/breakdowns.json):
  all four region, four segment, four channel and six category sales amounts
  independently reconcile to annual Net Sales within INR 0.01.
- [Quality](../../_build/executive-summary-discovery-16nov-1953/quality.json):
  no matching exceptions for tested unmatched dimension keys, mismatched
  fact/customer region, negative revenue or blank order IDs. DAX COUNTROWS on
  these empty exception sets returned null, meaning zero matching exceptions.
- Orders are distinct counts, not arbitrary additive category subtotals.
  The documented completed-order exclusion cannot be independently checked
  without the measure expression; use the existing measure unchanged.
- Margin must be evaluated in total context, never summed/averaged from
  displayed percentages. Fiscal or current-year YTD claims are not justified.
