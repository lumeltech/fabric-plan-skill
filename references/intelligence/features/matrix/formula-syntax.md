---
id: MX-FML-01
name: Matrix formula syntax and reporting functions
area: matrix
category: Calculations
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/planning-sheets/reference/formula-syntax
---

# Matrix formula syntax and reporting functions

## What it does

Provides the reporting subset of Fabric Plan's Excel-like formula language
for Intelligence Matrix calculated columns and rows. The source is published
under Planning sheets; the user confirms that most formulas also apply to
Intelligence Matrix. This is not a blanket guarantee for every function,
editor option, or saved JSON representation.

## When to use

- Ratios, variance, business classifications, text labels and date calculations.
- Hierarchy-aware calculations and time analysis supported by the Matrix.
- A calculated flag used as the basis for conditional formatting.
- Checking whether a missing measure can be computed without changing the model.

## UI path

Open the Matrix calculated column or row formula editor. Use its formula menu,
autocomplete and reference picker to confirm available functions and operands.
Do not assume Planning's Copy to Column or action-parameter UI exists here.
For Insert Row and row Quick Formula options, first select an actual Matrix
row; selecting only the visual leaves the commands disabled.

In the row editor, explicitly choose References when partial names collide
with functions. Pick an unambiguous partial name and then the exact suggestion;
for hierarchy references select the parent, type `.` and select the child.
An exact-text automation match can hit the formula editor instead of the
suggestion, so verify the inserted reference.

## Formula authoring rules

1. Reuse existing model measures where suitable. Resolve operands against the
   live field registry and the actual visual's inserted-measure IDs.
2. Choose a row or column calculation with the required evaluation context.
   Use references offered by that Matrix editor, not guessed labels or IDs.
3. Use straight quotes for string literals, commas for function arguments,
   parentheses for grouping, and square brackets where the function expects
   a list. The operators page documents `+`, `-`, `*`, `/`, `=`, `!=`, `>`,
   `>=`, `<`, `<=`; some examples use `==`. Confirm editor acceptance rather
   than translating formulas from DAX, JavaScript or Excel unchanged.
4. Select the output type supported by the Matrix: Number, Text, Boolean or
   Date. Keep ratios numeric and apply percentage formatting separately.
5. Define blank, zero-denominator and no-match behavior explicitly. A fallback
   of zero can hide missing data; use it only when the report contract requires
   it. Do not mask unresolved references with `IFNA` or `ISREFEXIST`.
6. Check detail rows, parents, grand totals, filters and column ordering.
   A total ratio normally needs a ratio of totals, not a sum of row ratios.
7. Documentation establishes syntax, not stored formula tokens or properties.
   Validate the formula in the Matrix and capture its native encoding.

## Reporting function families

Read the linked category and, where available, its individual function page
for exact arguments. This catalog selects reporting candidates, not verified
Intelligence Matrix encodings.

| Family | Functions and reporting use | Fabric Plan reference |
|---|---|---|
| Conditions | `IF`, `SWITCH`, `IFNA`; `AVERAGEIF`, `COUNTIF`, `SUMIF`, `FILTERIF` for conditional aggregation | [Conditional statements](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/conditional-statements) |
| Logic | `AND`, `OR`, `NOT`, `XOR`, `IN`, `ISBLANK`/`ISEMPTY`, `ISNUMBER`, `ISREFEXIST` | [Logical functions](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/logical-functions) |
| Arithmetic and aggregation | `ABS`, `DIVIDE`, `SUM`, `COUNT`, `AVERAGE`, `MIN`, `MAX`, `AVERAGEEXNEG`, `AVERAGEEXZERO`, `AVERAGEEXZERONEG` | [Math functions](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/math-functions) |
| Rounding and numeric analysis | `ROUND`, `ROUNDUP`, `ROUNDDOWN`, `CEILING`, `FLOOR`, `MROUND`, `EVEN`, `ODD`, `EXP`, `LOG`, `SQRT`, `INDEXOF`; inspect the individual power-function page because the catalog uses `POWER` but shows `POW` syntax | [Math functions](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/math-functions) |
| Specialist numeric functions | `NORMDIST`, `NORMSDIST`, `NORMINV`, `NORMSINV`, `PCT`, `PMT` when a reporting requirement calls for them; not inherently Planning-only. `RAND`/`RANDBETWEEN` are not suitable for reproducible performance measures | [Math functions](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/math-functions) |
| Text | `CONCATENATE`, `LEFT`, `RIGHT`, `MID`, `LOWER`, `UPPER`, `PROPER`, `REPLACE`, `REPT`, `TEXT`, `TRIM`, `VALUE`; `HYPERLINK` requires a rendering/navigation check | [Text formatting](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/text-formatting-functions) |
| Dates | `DATEADD`, `DATEDIFF`, `DAY`, `MONTH`, `YEAR`, `EOMONTH`, `NOW`, `PERIOD_RANGE`; confirm date types and serial-conversion direction from the individual `FROMEXCELDATE`/`TOEXCELDATE` pages | [Date functions](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/date-functions) |
| Operators | Arithmetic, comparison and grouping on measures/node references | [Other operators](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/other-operators) |

`FILTERIF` returns an array: aggregate it when a scalar column is needed.
Do not infer Excel-compatible argument order, indexing or error behavior from
function names. For example, use the Plan-specific
[DIVIDE signature](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/math-functions/divide).

### Hierarchy and relative references

The [identifiers catalog](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/identifiers)
includes reporting-oriented `COLUMN.DATE`, `COLUMN.PARENT`, `COLUMNS`,
`CURRENT_PERIOD`, `GROUP_INDEX`, `LEVEL`, `DESCENDANTS`, `MEMBERS`,
`ROW.LABEL`, `ROW.PARENT`, `RELATIVE`, `RELATIVE_COLUMN`, `MINDATE`,
`MAXDATE`, `HAS`, `HAS_ALL`, `HAS_SOME` and `MATCH`.

Select identifiers appropriate to a row or column formula. Parent/child
references depend on hierarchy and aggregation; relative references depend on
visible column order and boundary handling. Several catalog links are broken,
and some examples are incomplete: confirm syntax in the Matrix editor rather
than copying malformed examples or inventing signatures.

### Time intelligence

The [time-intelligence catalog](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/time-intelligence-functions)
lists `AGGREGATE`, `COLUMN_PERIOD`, `FILTER`, `LASTNDAY`, `LASTNMONTH`,
`LASTNQTR`, `LASTNYEAR`, `NEXTNDAY`, `NEXTNMONTH`, `NEXTNQTR`, `NEXTNYEAR`,
`MONTHPERIOD`, `QTRPERIOD`, `YEARPERIOD`, `MOVINGAVERAGE`, `MOVINGSUM`,
`MTD`, `QTD`, `YTD`, `TOTALMTD`, `TOTALQTD`, `TOTALYTD`, `SHIFT`, `VALUEAT`.

These are reporting candidates, not excluded just because the source is under
Planning. Confirm availability, arguments, date bindings, fiscal boundaries
and access to the required periods in the Intelligence Matrix. The catalog's
broken detail links do not establish callable signatures. Do not use DAX
signatures for identically named functions. A visible-axis running total is
not automatically equivalent to a model-level YTD or rolling measure.
When a date preset or slicer narrows the visible range, confirm moving,
prior-period and YTD functions can still read earlier periods; otherwise the
first periods are partial or blank.

### Same-grid conditional lookup

[XLOOKUP](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/lookup-functions/lookup-functions-xlookup)
describes condition-based measure lookup, not the advanced cross-sheet
`LOOKUP` configuration. Consider it only if the Intelligence Matrix exposes
it and the data/context is available. Its four arguments are conditions,
return measure, fallback and output mode: `1` selects the first match; `0`
returns all matches as an array. Aggregate arrays for scalar output. Use
`THIS` only for dimensions that should follow current evaluation context;
confirm uniqueness before choosing first-match behavior.

## Reporting examples

These are formula-editor patterns using illustrative references `AC`, `PL`
and `PY`, not serialized formulas or actual model field names.

```text
Absolute variance: AC - PL
Variance ratio:    DIVIDE(AC - PL, PL, 0)
Achievement ratio: DIVIDE(AC, PL, 0)
YoY ratio:         DIVIDE(AC - PY, PY, 0)
Magnitude:         ABS(AC - PL)
Reporting flag:    IF(AC < PL, "Below plan", "At or above plan")
Threshold flag:    IF(AND(AC < PL, PL > 0), 1, 0)
```

The examples' zero fallbacks are illustrative; agree on missing/zero behavior
before use. Revenue and expense favorability can be opposite. For conditional
formatting, compare the numeric result or calculated flag through a supported
Matrix rule; do not assume the rule editor accepts arbitrary formula strings.

## Excluded Planning-only scope

- Forecast lifecycle identifiers `CLOSEDPERIOD`, `FORECAST.CLOSED_START`,
  `FORECAST.CLOSED_END`, `FORECAST.OPEN_START`, `FORECAST.OPEN_END`.
- On-change input identifiers `LOGGEDIN_EMAIL` and `LOGGEDIN_NAME`, input
  mutation, writeback, allocation, spreading and connected-planning automation.
- [Advanced LOOKUP](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/lookup-functions/lookup):
  configured From Sheets/Queries lookups and planning assumptions.
- [Scripting functions](https://docs.fabricplan.com/planning-sheets/reference/formula-syntax/scripting-functions):
  initialization/data-change/button actions are not Matrix calculation formulas.
  Some headings and syntax on that page disagree; do not transplant them.

Actual Planning-only requests await the owning module's integration. Independent
Intelligence canvas interactions remain separate features requiring their own
native evidence, not a reason to import Planning scripts.

## Definition encoding

```text
Calculated row path: sheets/{sheetId}/visuals/{visualId}/insertRows.json
rows[].rowMeta.row_type.CalculatedRow.formula: native R_<row ID> expression
Example pattern only: R_<revenue row ID> - R_<cost row ID>
Evidence: native saved reporting-Matrix subtotal/profit rows.
Calculated-column and function-specific encodings: still require their own capture.
```

Follow [native sample capture](../../core/native-samples.md) and the calculated
row/column feature's encoding gate. Preserve captured IDs and token syntax:
`R_<id>` for the observed row operands, `M_<id>` only where the native Matrix
uses measure references. These IDs are model/visual-specific, never portable
constants. Do not derive a
formula JSON schema from the documentation or from an embedded Planning grid.

## Constraints

- This reference does not authorize semantic-model edits or Planning writes.
- Formula runtime support and stored encoding must be checked separately.
- Test ordinary values, blanks, zero denominators, first/last periods,
  hierarchy totals and changed filters before accepting a calculation.

## Related features

- `MX-CALC-02`
- `MX-CALC-01`
- `MX-QF-01`
- `MX-VAR-01`
- `MX-CF-01`
