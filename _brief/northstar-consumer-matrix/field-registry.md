# Field registry - SM Sales Performance Dashboard-AI Test (f0000000-0000-4000-8000-000000000099) in Planning-Demos (f0000000-0000-4000-8000-0000000000af)
Captured: 2026-11-19T10:43Z via executeQueries INFO.VIEW.* (live, this task); measure DAX via read-only semanticModels getDefinition (TMDL), because INFO.VIEW.MEASURES returned null expressions.

## Metadata coverage
- Tables: 7 / descriptions populated 0 / missing 7 / unavailable 0
- Columns: 51 / descriptions populated 0 / missing 51 / unavailable 0
- Measures: 36 / descriptions populated 7 / missing 29 / unavailable 0
- Relationships: 5. Raw: _build/northstar-consumer-matrix-19nov/info-tables.json, info-columns.json, info-measures.json, info-relationships.json; DAX: _build/northstar-consumer-matrix-19nov/model-tmdl/

## Table context
- DimChannel: description: missing; hidden: False; grain/role (inferred): sales channel dimension (4).
- DimCustomer: description: missing; hidden: False; grain/role (inferred): customer dimension, 250 customers; carries State/City and RegionKey.
- DimDate: description: missing; hidden: False; grain/role (inferred): calendar dimension, marked date table.
- DimProduct: description: missing; hidden: False; grain/role (inferred): product dimension, 24 products.
- DimRegion: description: missing; hidden: False; grain/role (inferred): region dimension (4), reaches FactSales only via DimCustomer.
- FactSales: description: missing; hidden: False; grain/role (inferred): fact; one row per sales line (SalesLineKey); 13,698 rows; 2024-01-01..2025-12-31; holds AC, Budget and Target amounts at line grain.
- _Measures: description: missing; hidden: False; grain/role (inferred): measure table (hidden placeholder column).

## Dimensions
| Table | Column | Type | Hidden | Distinct | Description | Notes (hierarchy, sort-by) |
|---|---|---|---|---|---|---|
| DimChannel | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | True |  | missing | technical/key |
| DimChannel | ChannelKey | Integer | True |  | missing | technical/key |
| DimChannel | ChannelName | Text | False | 4 | missing |  |
| DimCustomer | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | True |  | missing | technical/key |
| DimCustomer | CustomerKey | Integer | True |  | missing | technical/key |
| DimCustomer | CustomerName | Text | False | 250 | missing | Geo L4 / customer; search/dropdown only |
| DimCustomer | CustomerSegment | Text | False | 4 | missing |  |
| DimCustomer | City | Text | False | 32 | missing | Geo L3 (each city in one state) |
| DimCustomer | State | Text | False | 21 | missing | Geo L2 (each state in one region) |
| DimCustomer | RegionKey | Integer | True |  | missing | technical/key |
| DimCustomer | CustomerStatus | Text | True |  | missing | technical/key |
| DimDate | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | True |  | missing | technical/key |
| DimDate | DateKey | Integer | True |  | missing | technical/key |
| DimDate | Date | Date | False |  | missing | Marked date table (dataCategory Time); 2024-01-01..2026-12-31 |
| DimDate | MonthNumber | Integer | True |  | missing | technical/key |
| DimDate | Year | Integer | False | 3 | missing | 2024-2026 in calendar; facts 2024-2025 only |
| DimDate | Quarter | Text | False | 4 | missing |  |
| DimDate | Month | Text | False | 12 | missing | sortBy MonthNumber; hierarchy 'Date Hierarchy' Year>Quarter>Month>Date |
| DimProduct | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | True |  | missing | technical/key |
| DimProduct | ProductKey | Integer | True |  | missing | technical/key |
| DimProduct | ProductName | Text | False | 24 | missing | Product hierarchy L3 |
| DimProduct | Category | Text | False | 6 | missing | Product hierarchy L1 |
| DimProduct | Subcategory | Text | False | 15 | missing | Product hierarchy L2 (unique parent) |
| DimProduct | Brand | Text | False | 10 | missing | Alt attribute; each brand in one category |
| DimProduct | ListPriceINR | Integer | True |  | missing | technical/key |
| DimProduct | StandardCostRatio | Number | True |  | missing | technical/key |
| DimRegion | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | True |  | missing | technical/key |
| DimRegion | RegionKey | Integer | True |  | missing | technical/key |
| DimRegion | RegionName | Text | False | 4 | missing | Geo L1; filters sales via DimCustomer only |

## Facts
| Table | Column | Type | Hidden | Description | Notes (grain, keys) |
|---|---|---|---|---|---|
| FactSales | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | True | missing | key/technical |
| FactSales | SalesLineKey | Integer | False | missing |  |
| FactSales | OrderID | Text | True | missing | key/technical |
| FactSales | OrderDateKey | Integer | True | missing | key/technical |
| FactSales | CustomerKey | Integer | True | missing | key/technical |
| FactSales | ProductKey | Integer | True | missing | key/technical |
| FactSales | RegionKey | Integer | True | missing | key/technical |
| FactSales | ChannelKey | Integer | True | missing | key/technical |
| FactSales | Quantity | Integer | False | missing |  |
| FactSales | UnitPriceINR | Number | False | missing | INR amount |
| FactSales | NetRevenueINR | Number | False | missing | INR amount |
| FactSales | COGSINR | Number | False | missing | INR amount |
| FactSales | GrossSalesINR | Number | False | missing | INR amount |
| FactSales | DiscountAmountINR | Number | False | missing | INR amount |
| FactSales | BudgetNetRevenueINR | Number | False | missing | INR amount |
| FactSales | BudgetCOGSINR | Number | False | missing | INR amount |
| FactSales | BudgetGrossProfitINR | Number | False | missing | INR amount |
| FactSales | TargetNetRevenueINR | Number | False | missing | INR amount |
| FactSales | TargetCOGSINR | Number | False | missing | INR amount |
| FactSales | TargetGrossProfitINR | Number | False | missing | INR amount |
| _Measures | RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61 | Integer | True | missing | key/technical |
| _Measures | Column1 | Text | True | missing | key/technical |

## Measures
| Home table | Measure | Format string | Folder | Scenario tag | Description | Expression / raw source |
|---|---|---|---|---|---|---|
| _Measures | Net Sales | `₹#,##0;[Red](₹#,##0)` | 01 Base Measures | AC | Net revenue after discounts. | `SUM ( FactSales[NetRevenueINR] )` |
| _Measures | Quantity Sold | `#,##0` | 01 Base Measures | AC | Total units sold. | `SUM ( FactSales[Quantity] )` |
| _Measures | Total Orders | `#,##0` | 01 Base Measures | AC | Distinct completed orders. | `DISTINCTCOUNT ( FactSales[OrderID] )` |
| _Measures | Average Order Value | `₹#,##0.00` | 01 Base Measures | AC % | Net sales divided by distinct orders. | `DIVIDE ( [Net Sales], [Total Orders] )` |
| _Measures | Total COGS | `₹#,##0;[Red](₹#,##0)` | 01 Base Measures | AC | Cost of goods sold. | `SUM ( FactSales[COGSINR] )` |
| _Measures | Gross Profit | `₹#,##0;[Red](₹#,##0)` | 01 Base Measures | AC | Net revenue less COGS. | `[Net Sales] - [Total COGS]` |
| _Measures | Gross Margin % | `0.0%;[Red](0.0%)` | 01 Base Measures | AC % | Gross profit divided by net sales. | `DIVIDE ( [Gross Profit], [Net Sales] )` |
| _Measures | PY Net Sales | `"₹"\ #,0;#,0\ -"₹";"₹"\ #,0` | 02 PY Measures | PY | missing | `CALCULATE( [Net Sales], SAMEPERIODLASTYEAR(DimDate[Date]))` |
| _Measures | PY Total Orders | `#,##0` | 02 PY Measures | PY | missing | `CALCULATE([Total Orders], SAMEPERIODLASTYEAR(DimDate[Date]))` |
| _Measures | PY Quantity Sold | `#,##0` | 02 PY Measures | PY | missing | `CALCULATE([Quantity Sold], SAMEPERIODLASTYEAR(DimDate[Date]))` |
| _Measures | PY Average Order Value | `₹#,##0;[Red](₹#,##0)` | 02 PY Measures | PY % | missing | `CALCULATE( [Average Order Value], SAMEPERIODLASTYEAR(DimDate[Date]))` |
| _Measures | PY Total COGS | `₹#,##0;[Red](₹#,##0)` | 02 PY Measures | PY | missing | `CALCULATE( [Total COGS], SAMEPERIODLASTYEAR(DimDate[Date]))` |
| _Measures | PY Gross Margin | `₹#,##0;[Red](₹#,##0)` | 02 PY Measures | PY | missing | `CALCULATE( [Gross Profit] , SAMEPERIODLASTYEAR(DimDate[Date]))` |
| _Measures | PY Gross Margin % | `0.00%;-0.00%;0.00%` | 02 PY Measures | PY % | missing | `CALCULATE([Gross Margin %], SAMEPERIODLASTYEAR( DimDate[Date]))` |
| _Measures | Gross Sales | `₹#,##0;[Red](₹#,##0)` | 01 Base Measures | AC | missing | `SUM( FactSales[GrossSalesINR])` |
| _Measures | Discount | `₹#,##0;[Red](₹#,##0)` | 01 Base Measures | AC | missing | `SUM(FactSales[DiscountAmountINR])` |
| _Measures | PY Discount | `₹#,##0;[Red](₹#,##0)` | 02 PY Measures | PY | missing | `CALCULATE([Discount], SAMEPERIODLASTYEAR(DimDate[Date]))` |
| _Measures | PY Gross Sales | `₹#,##0;[Red](₹#,##0)` | 02 PY Measures | PY | missing | `CALCULATE( [Gross Sales] , SAMEPERIODLASTYEAR(DimDate[Date]))` |
| _Measures | BUD Net Sales | `₹#,##0;[Red](₹#,##0)` | 03 BUD Measures\_AC | PL | missing | `SUM(FactSales[BudgetNetRevenueINR])` |
| _Measures | BUD COGS | `₹#,##0;[Red](₹#,##0)` | 03 BUD Measures\_AC | PL | missing | `SUM(FactSales[BudgetCOGSINR])` |
| _Measures | BUD Profit Margin | `₹#,##0;[Red](₹#,##0)` | 03 BUD Measures\_AC | PL | missing | `[BUD Net Sales] - [BUD COGS]` |
| _Measures | BUD Profit Margin % | `0.00%;-0.00%;0.00%` | 03 BUD Measures\_AC | PL % | missing | `DIVIDE( [BUD Profit Margin], [BUD Net Sales])` |
| _Measures | Target Net Sales | `₹#,##0;[Red](₹#,##0)` | 04 Target Measures\_AC | PL-TGT | missing | `SUM( FactSales[TargetNetRevenueINR])` |
| _Measures | Target COGS | `₹#,##0;[Red](₹#,##0)` | 04 Target Measures\_AC | PL-TGT | missing | `SUM( FactSales[TargetCOGSINR])` |
| _Measures | Target Profit Margin | `₹#,##0;[Red](₹#,##0)` | 04 Target Measures\_AC | PL-TGT | missing | `[Target Net Sales] - [Target COGS]` |
| _Measures | Target Profit Margin % | `0.00%;-0.00%;0.00%` | 04 Target Measures\_AC | PL-TGT % | missing | `DIVIDE( [Target Profit Margin] , [Target Net Sales])` |
| _Measures | PY BUD COGS | `₹#,##0;[Red](₹#,##0)` | 03 BUD Measures\_PY | PY | missing | `CALCULATE( [BUD COGS], SAMEPERIODLASTYEAR(DimDate[Date]))` |
| _Measures | PY BUD Net Sales | `₹#,##0;[Red](₹#,##0)` | 03 BUD Measures\_PY | PY | missing | `CALCULATE( [BUD Net Sales], SAMEPERIODLASTYEAR(DimDate[Date]))` |
| _Measures | PY BUD Profit Margin | `₹#,##0;[Red](₹#,##0)` | 03 BUD Measures\_PY | PY | missing | `CALCULATE( [BUD Profit Margin] , SAMEPERIODLASTYEAR( DimDate[Date]))` |
| _Measures | PY BUD Profit Margin % | `0.00%;-0.00%;0.00%` | 03 BUD Measures\_PY | PY % | missing | `CALCULATE( [BUD Profit Margin %], SAMEPERIODLASTYEAR(DimDate[Date]))` |
| _Measures | PY Target Net Sales | `₹#,##0;[Red](₹#,##0)` | 04 Target Measures\_PY | PY | missing | `CALCULATE( [Target Net Sales] , SAMEPERIODLASTYEAR( DimDate[Date] ))` |
| _Measures | PY Target COGS | `₹#,##0;[Red](₹#,##0)` | 04 Target Measures\_PY | PY | missing | `CALCULATE( [Target COGS] , SAMEPERIODLASTYEAR( DimDate[Date]))` |
| _Measures | PY Target Profit Margin | `₹#,##0;[Red](₹#,##0)` | 04 Target Measures\_PY | PY | missing | `CALCULATE( [Target Profit Margin] , SAMEPERIODLASTYEAR( DimDate[Date]))` |
| _Measures | PY Target Profit Margin % | `0.00%;-0.00%;0.00%` | 04 Target Measures\_PY | PY % | missing | `CALCULATE( [Target Profit Margin %] ,  SAMEPERIODLASTYEAR( DimDate[Date] ))` |
| _Measures | Discount % | `0.00%;-0.00%;0.00%` | 01 Base Measures | AC % | missing | `DIVIDE( [Discount], [Gross Sales])` |
| _Measures | PY Discount % | `0.00%;-0.00%;0.00%` | 02 PY Measures | PY % | missing | `CALCULATE( [Discount %], SAMEPERIODLASTYEAR(DimDate[Date]))` |

## Relationships
| From | To | Cardinality | Direction | Active |
|---|---|---|---|---|
| DimCustomer[RegionKey] | DimRegion[RegionKey] | Many:One | OneDirection | True |
| FactSales[ChannelKey] | DimChannel[ChannelKey] | Many:One | OneDirection | True |
| FactSales[CustomerKey] | DimCustomer[CustomerKey] | Many:One | OneDirection | True |
| FactSales[ProductKey] | DimProduct[ProductKey] | Many:One | OneDirection | True |
| FactSales[OrderDateKey] | DimDate[DateKey] | Many:One | OneDirection | True |

## Notes
- Table names carry no prefixes; names are exact IDs (e.g. `DimProduct`, `_Measures`).
- Hidden keys/RowNumber columns are inventoried but excluded from visuals.
- No relationship from `FactSales[RegionKey]` to `DimRegion`; Region filters sales through `DimCustomer[RegionKey]` (customer's region). Sampled: fact RegionKey equals customer RegionKey on every row, so totals reconcile.
- Hierarchies: model has only `DimDate` 'Date Hierarchy' (Year > Quarter > Month > Date). Product (Category > Subcategory > ProductName) and Geography (RegionName > State > City > CustomerName) are clean parent-child paths (sampled: no child under two parents) and can be built as Matrix row hierarchies.
- Scenario tags inferred from names, folders and DAX: AC = actual; PL = `BUD *` (budget); PL-TGT = `Target *` (stretch target, second plan scenario); PY = `SAMEPERIODLASTYEAR` over the AC/BUD/Target measures.
- `PY Gross Margin` is actually PY Gross Profit (amount, DAX `CALCULATE([Gross Profit], ...)`); `BUD/Target Profit Margin` are amounts (gross profit), `... %` are ratios.
- Non-additive: Total Orders (distinct count), Average Order Value, all % measures - totals use the measure, never sums.
- Currency: all amounts are INR; format strings use the rupee symbol. `PY Net Sales` has an inconsistent format string versus the other amount measures.
- Data coverage: AC/BUD/Target exist for 2024 and 2025 only. PY is blank for 2024; calendar year 2026 has only PY values (2025 shifted). Default report scope should be Year = 2025 and the year list restricted to 2024-2025.
- Sampled quality: no negative net revenue, no blank budget lines, no customers without sales.
