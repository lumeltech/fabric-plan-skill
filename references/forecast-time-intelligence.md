# Forecast hierarchies, one-time columns and dynamic as-of controls

## 1. Preserve a valid calendar hierarchy

Resolve actual model fields, calendar relationships, sort order, date formats and
fiscal definitions first. Prefer individual date attributes, in this order:

| Grain | Preferred Columns |
|---|---|
| Monthly | Year, Quarter, Month (MonthName is a valid field label) |
| Quarterly | Year, Quarter |
| Yearly | Year |
| Weekly | Year, Quarter, Month, Week only when those are valid parents |

For weeks crossing month/quarter boundaries, use the model's valid Year/Week
hierarchy; do not invent month parentage. A model without Quarter can use
Year/Month. Do not add synthetic calendar fields just to satisfy an example.
Custom fiscal names require explicit role mappings, not guesses from labels.

Avoid YearMonth, YearQuarter and YearWeek in Columns when equivalent separate
attributes exist. A composite is allowed when explicitly required or when no
suitable individual hierarchy exists; record the reason and establish the native
time role, member ordering and extension behavior. A YearMonth filter or slicer
may remain useful for a date window; the rule concerns the planning axis.

Forecasts extending into future periods require **only valid date hierarchy
attributes in Columns**. Move unrelated product/scenario dimensions only within
authorized scope; do not silently remove them. Calendar member completeness,
chronological sorting and the applicable time unit must be resolved separately.

`build` normalizes a recognized composite Forecast axis to available individual
fields. `calendarRoleFields` maps Year/Quarter/Month/Week to actual model field
keys. `weekParentageValidated:true` is an evidence assertion by the author, not a
check of the calendar's data. An intentional composite requires
`allowCompositeTimeAxis:true`, `compositeTimeAxisReason` and `columnTimeLevels`.
No suitable fields means resolve the model or deliberate exception; do not guess.

For existing reports, use `planning-time-axis` with properties, current model,
columns and optional `time_levels`. It prepares properties only. Preserve existing
date-window filters (including a removed composite's scope filter), measure IDs,
Forecast bounds, locks, input values and storage key mappings. A changed visible
calendar axis does not authorize a writeback key migration.

## 2. Choose the correct one-time column

When the request adds information beside a finer-grain planning grid, evaluate a
Visual Column first. Leave the existing Columns hierarchy intact.

| Request in the existing grid | Preferred additional column |
|---|---|
| Quarterly/annual management commentary beside monthly values | Visual Input Column, LongText |
| Monthly/quarterly notes beside weekly values | Visual Input Column, LongText |
| One-time forecast adjustment | Visual Input Column, Number |
| QTD, MTD, YTD or selected-date summary | Formula Visual Column |

Append once at the end of the grid, once per row context, not once under every
month. Visual input and visual formula are distinct native types:

```json
{"VisualColumn":{"DataInput":{"id":"<configuration-id>","title":"Commentary","column_type":{"LongText":"<resolved metadata>"},"allow_input":"ReadAndEdit","bound_to_filter_context":true}}}
```

```json
{"VisualColumn":{"Formula":{"formula":"<resolved native formula>"}}}
```

These illustrate the `measure_type` tags, not complete deployment payloads.

`input_create(..., visual_column=True)` and `formula_create(..., visual_column=True)` construct typed candidates locally. Forecast and Native are not VisualColumn tags.

One-time presentation does not imply one global saved comment. Resolve row,
quarter/year, scenario/version and filter context for persistence. If separate
comments for every quarter are needed, retain those distinct storage contexts or
use an appropriate period-grain commentary sheet. Do not overwrite one comment
while presenting it as multiple quarter-specific entries. Define subtotal entry
and roll-up explicitly. Do not create a new calendar axis merely for the comment.

## Cutoff and period calculation

Resolve one cutoff date at the requested scope. A selected month without a year is ambiguous. Distinguish an exact date cutoff from month end. For a dataset-backed date list, use `date_parameter_bundle` with actual date members; expressions use `VR_CALC_VARIABLE_<id>`, not the displayed label.

Exact native date-list patterns (replace symbolic IDs with current IDs):

```text
SUM(QTD(M_<forecast-id>, 0, DATE(VR_CALC_VARIABLE_<id>)))
SUM(MTD(M_<forecast-id>, 0, DATE(VR_CALC_VARIABLE_<id>)))
SUM(YTD(M_<forecast-id>, 0, DATE(VR_CALC_VARIABLE_<id>)))
```

The first argument is the source measure, second is relative period offset
(normally zero, unless requested), and third is the cutoff. `SUM` is the
aggregation wrapper for an additive amount.

Use the aggregation that matches the business measure. For example:

Keep the main monthly/weekly grain. Resolve time windows, loaded history and
future-month availability; a truncated visible interval can make a QTD/YTD total
incomplete. Keep missing distinct from zero. The helper can guard an aligned
missing-cell measure with the **same** period and cutoff:

```text
IF(SUM(QTD(M_<missing-id>, 0, <cutoff>)) > 0, BLANK, SUM(QTD(M_<forecast-id>, 0, <cutoff>)))
```

Choose row aggregation per business semantics. Sum only compatible additive
values; currencies must be converted at the correct leaf grain before summing.
Rates and mixed local currencies do not become additive just because a visual
column is appended. Preserve existing missing/FX guards and balance aggregation.
The helper defaults row aggregation to None and column aggregation to None.

```sh
python plan.py planning-time-column --baseline definition.json --input time-column.request.json --out candidate
```
