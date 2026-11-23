# Field registry - SM Sales Performance Dashboard-AI Test


## Metadata coverage

- Tables: 7 total; descriptions populated 0; missing 7.
- Columns: 51 total, including 7 internal row-number columns; descriptions populated 0; missing 51.
- Measures: 36 total; descriptions populated 7; missing 29.
- Relationships: 5, all active, many-to-one, single-direction. 
- Raw responses are authoritative for exact formats, folders, flags, source columns and lineage.
- Measure expressions were null for all 36 measures. Their DAX is unavailable through this capture, not proven absent.
- Supplementary INFO.MEASURES() and INFO.HIERARCHIES() requests failed with DatasetExecuteQueriesError / AnalysisServicesErrorCode 3239575574. Do not interpret these failures as empty metadata.
- Native hierarchy definitions remain unavailable. Candidate drill paths below are inferred from columns, not verified native hierarchies.
- No calculation-group table was indicated in the returned table inventory (all calculation-group precedence values null).

## Table context

All tables use Import storage and are visible. All table descriptions are missing.
Roles and grain below are explicitly inferred and checked against sampled results:

- DimChannel: channel dimension.
- DimCustomer: customer dimension, including customer segment and geographic attributes.
- DimDate: calendar dimension; DataCategory Time, Date is a unique key; calendar 2024-01-01 through 2026-12-31, 1,096 rows. Fiscal-year convention not documented.
- DimProduct: product dimension with Category, Subcategory and Brand.
- DimRegion: region dimension; filters sales through DimCustomer, not directly through FactSales[RegionKey].
- FactSales: one sales line per SalesLineKey in the observed data; 13,698 rows and 13,698 distinct line keys, 7,120 distinct orders. Actual dates 2024-01-01 through 2025-12-31.
- _Measures: measure home/helper table. Hidden Column1 is not a report field.

## Columns

Description is missing for every column. Distinct counts shown are observed in live profiling; "-" means not sampled. Hidden keys and row numbers are inventoried, not proposed as display fields.

| Table | Column | Type | Hidden | Distinct | Notes |
|---|---|---|---|---|---|
| DimChannel | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | true | - | Internal RowNumber |
| DimChannel | ChannelKey | Integer | true | - | Unique dimension key |
| DimChannel | ChannelName | Text | false | 4 | Direct Sales, Distributor, Online, Retail Partner |
| DimCustomer | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | true | - | Internal RowNumber |
| DimCustomer | CustomerKey | Integer | true | - | Unique dimension key |
| DimCustomer | CustomerName | Text | false | 250 | Searchable selector if requested |
| DimCustomer | CustomerSegment | Text | false | 4 | Enterprise, Mid-Market, Retail Consumer, SMB |
| DimCustomer | City | Text | false | - | Geographic attribute |
| DimCustomer | State | Text | false | - | Geographic attribute |
| DimCustomer | RegionKey | Integer | true | - | Relationship to DimRegion |
| DimCustomer | CustomerStatus | Text | true | - | Hidden; do not expose by default |
| DimDate | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | true | - | Internal RowNumber |
| DimDate | DateKey | Integer | true | - | Unique relationship key |
| DimDate | Date | Date | false | - | Unique key, calendar range above |
| DimDate | MonthNumber | Integer | true | - | Sort helper; not a display field |
| DimDate | Year | Integer | false | 3 | 2024, 2025, 2026 |
| DimDate | Quarter | Text | false | - | Preserve Year context |
| DimDate | Month | Text | false | - | SortByColumn MonthNumber; preserve Year context |
| DimProduct | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | true | - | Internal RowNumber |
| DimProduct | ProductKey | Integer | true | - | Unique dimension key |
| DimProduct | ProductName | Text | false | 24 | Product detail candidate |
| DimProduct | Category | Text | false | 6 | Executive breakdown candidate |
| DimProduct | Subcategory | Text | false | 15 | Detail candidate |
| DimProduct | Brand | Text | false | 10 | Optional selector |
| DimProduct | ListPriceINR | Integer | true | - | Hidden price attribute; not a sales measure |
| DimProduct | StandardCostRatio | Number | true | - | Hidden ratio attribute |
| DimRegion | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | true | - | Internal RowNumber |
| DimRegion | RegionKey | Integer | true | - | Unique dimension key |
| DimRegion | RegionName | Text | false | 4 | East, North, South, West |
| FactSales | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | true | - | Internal RowNumber |
| FactSales | SalesLineKey | Integer | false | 13698 | Observed unique line identifier; do not sum |
| FactSales | OrderID | Text | true | 7120 | Use Total Orders measure |
| FactSales | OrderDateKey | Integer | true | - | Active date relationship |
| FactSales | CustomerKey | Integer | true | - | Active customer relationship |
| FactSales | ProductKey | Integer | true | - | Active product relationship |
| FactSales | RegionKey | Integer | true | - | No direct relationship; matched customer region in tested data |
| FactSales | ChannelKey | Integer | true | - | Active channel relationship |
| FactSales | Quantity | Integer | false | - | Prefer Quantity Sold measure |
| FactSales | UnitPriceINR | Number | false | - | Unit price; not additive |
| FactSales | NetRevenueINR | Number | false | - | Net sales source |
| FactSales | COGSINR | Number | false | - | Cost source |
| FactSales | GrossSalesINR | Number | false | - | Gross sales source |
| FactSales | DiscountAmountINR | Number | false | - | Discount source |
| FactSales | BudgetNetRevenueINR | Number | false | - | Budget sales source |
| FactSales | BudgetCOGSINR | Number | false | - | Budget cost source |
| FactSales | BudgetGrossProfitINR | Number | false | - | Budget gross profit source |
| FactSales | TargetNetRevenueINR | Number | false | - | Target sales source |
| FactSales | TargetCOGSINR | Number | false | - | Target cost source |
| FactSales | TargetGrossProfitINR | Number | false | - | Target gross profit source |
| _Measures | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | true | - | Internal RowNumber |
| _Measures | Column1 | Text | true | - | Helper, not a visual field |

## Measures

All 36 measures are visible and State Valid. Exact formats/folders remain in the raw measures response linked above; DAX expressions are unavailable there. Unit/scenario classifications are inferred from names, formats, descriptions and sampled behavior. INR is evidenced by source-column names and currency formats.

| Home table | Measure | Unit | Scenario tag | Description | Aggregation / interpretation |
|---|---|---|---|---|---|
| _Measures | Net Sales | INR | AC | Net revenue after discounts. | Additive; reconciled to source sum |
| _Measures | Quantity Sold | Units | AC | Total units sold. | Additive units |
| _Measures | Total Orders | Count | AC | Distinct completed orders. | Distinct count; do not sum across arbitrary slices |
| _Measures | Average Order Value | INR/order | AC | Net sales divided by distinct orders. | Non-additive; evaluate at total context |
| _Measures | Total COGS | INR | AC | Cost of goods sold. | Additive; positive in sampled data |
| _Measures | Gross Profit | INR | AC | Net revenue less COGS. | Amount, not percentage |
| _Measures | Gross Margin % | Percent | AC, % | Gross profit divided by net sales. | Non-additive weighted ratio |
| _Measures | PY Net Sales | INR | PY | missing | Prior-year behavior checked at annual and monthly grains |
| _Measures | PY Total Orders | Count | PY | missing | Non-additive distinct count |
| _Measures | PY Quantity Sold | Units | PY | missing | Prior-year units |
| _Measures | PY Average Order Value | INR/order | PY | missing | Non-additive ratio |
| _Measures | PY Total COGS | INR | PY | missing | Prior-year cost |
| _Measures | PY Gross Margin | INR | PY | missing | Amount; 2025 value matches 2024 Gross Profit |
| _Measures | PY Gross Margin % | Percent | PY, % | missing | Non-additive percentage |
| _Measures | Gross Sales | INR | AC | missing | Gross Sales minus Discount reconciles to Net Sales |
| _Measures | Discount | INR | AC | missing | Discount amount |
| _Measures | PY Discount | INR | PY | missing | Prior-year discount amount |
| _Measures | PY Gross Sales | INR | PY | missing | Prior-year gross sales |
| _Measures | BUD Net Sales | INR | PL | missing | Budget sales; source sum reconciled |
| _Measures | BUD COGS | INR | PL | missing | Budget cost |
| _Measures | BUD Profit Margin | INR | PL | missing | Amount; reconciled to BudgetGrossProfitINR |
| _Measures | BUD Profit Margin % | Percent | PL, % | missing | Non-additive ratio; reconciled to budget profit / budget sales |
| _Measures | Target Net Sales | INR | Target | missing | Target sales; source sum reconciled; distinct from budget |
| _Measures | Target COGS | INR | Target | missing | Target cost |
| _Measures | Target Profit Margin | INR | Target | missing | Amount; reconciled to TargetGrossProfitINR |
| _Measures | Target Profit Margin % | Percent | Target, % | missing | Non-additive ratio; reconciled to target profit / target sales |
| _Measures | PY BUD COGS | INR | PY, PL | missing | Prior-year budget cost; definition not retrieved |
| _Measures | PY BUD Net Sales | INR | PY, PL | missing | Prior-year budget sales; definition not retrieved |
| _Measures | PY BUD Profit Margin | INR | PY, PL | missing | Prior-year budget profit amount; definition not retrieved |
| _Measures | PY BUD Profit Margin % | Percent | PY, PL, % | missing | Non-additive; definition not retrieved |
| _Measures | PY Target Net Sales | INR | PY, Target | missing | Prior-year target sales; definition not retrieved |
| _Measures | PY Target COGS | INR | PY, Target | missing | Prior-year target cost; definition not retrieved |
| _Measures | PY Target Profit Margin | INR | PY, Target | missing | Prior-year target profit amount; definition not retrieved |
| _Measures | PY Target Profit Margin % | Percent | PY, Target, % | missing | Non-additive; definition not retrieved |
| _Measures | Discount % | Percent | AC, % | missing | Denominator not verified; not selected for first-build KPIs |
| _Measures | PY Discount % | Percent | PY, % | missing | Denominator not verified; not selected for first-build KPIs |

## Relationships

| From | To | Cardinality | Direction | Active |
|---|---|---|---|---|
| DimCustomer[RegionKey] | DimRegion[RegionKey] | Many to one | DimRegion to DimCustomer | true |
| FactSales[ChannelKey] | DimChannel[ChannelKey] | Many to one | DimChannel to FactSales | true |
| FactSales[CustomerKey] | DimCustomer[CustomerKey] | Many to one | DimCustomer to FactSales | true |
| FactSales[ProductKey] | DimProduct[ProductKey] | Many to one | DimProduct to FactSales | true |
| FactSales[OrderDateKey] | DimDate[DateKey] | Many to one | DimDate to FactSales | true |

## Connectivity and profiling notes

- Sales-source base measures have active dimension paths from Date, Channel, Product and Customer; Region travels through Customer. Sampled comparisons also varied by region/category/channel/segment and reconciled to total sales.
- Calendar extends into an empty actual year: 2026 has PY values but no actual/budget/target values. Proposed default year is 2025, not the current year.
- Proposed drill paths: Year > Quarter > Month; Category > Subcategory > ProductName. These are column-based proposals, not confirmed native hierarchy objects.
- Counts: channels 4, regions 4, segments 4, categories 6, subcategories 15, brands 10, products 24, customer names 250. Do not use customer-name tiles.
- Tested fact keys had no blank line/order identifiers, no unmatched date/customer/product/channel/customer-region paths, and no disagreement between fact and customer RegionKey. Empty COUNTROWS results serialize as null; this means zero matching exceptions for these explicit count queries, not a failed query.
- No negative net revenue or COGS rows in the scoped tests. This is not a full data-quality audit.
- Monetary identities passed within INR 0.01; tested ratio identities passed within 1e-10. Twelve 2025 monthly totals reconciled for sales/budget/target/profit/orders; all four sampled dimension sales totals reconciled; 2025 PY Net Sales matched 2024 Net Sales.
- Descriptions say Total Orders counts completed orders, but no order-status column or DAX definition was exposed to independently establish the exclusion rule. Use the existing measure without inventing a new status filter.
- Data source refresh timestamp, business ownership, fiscal basis, detailed DAX, and native hierarchies were not verified.
- Evidence: [profile](../../_build/sales-performance-5a5327d4/profile.json), [yearly](../../_build/sales-performance-5a5327d4/yearly.json), [monthly](../../_build/sales-performance-5a5327d4/monthly.json), [breakdowns](../../_build/sales-performance-5a5327d4/breakdowns.json), [quality](../../_build/sales-performance-5a5327d4/quality.json).
