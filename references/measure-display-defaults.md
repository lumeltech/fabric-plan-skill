# Measure cards at All and Auto number formatting

## Assigned measure cards stay visible, with no preset restriction

Show assigned Values measures in the side filter panel. Initialize each ordinary
measure card with `filter: []`, no selected values/presets, and null numeric
min/max/equal bounds. The intended UI is **is (All)**. A range slider's available
extent or the editor's `between` operator alone does not mean a range is applied.
Do not hide/delete the card to achieve an unrestricted view. Preserve complete
typed field IDs and source, query, visual, aggregation and bucket identities.

This applies to semantic DAX and aggregated numeric columns, native query /
InfoBridge values, and supported From Sheets assignments. Custom inputs/formulas
are numeric measures too, but do not invent a source assignment just to create a
filter card: use their actual supported registration contract.

Dimension defaults may select an explicitly requested year, region or scenario.
Apply the selection only to that dimension's **own** card. A measure card can
contain Year/Region/etc. assignments as its evaluation grain: those are not the
card's selected field. Never match `any(pivotAssignment.id == year)` when applying
a dimension selection. `runtime.filters.select_axis_filter()` requires a single
Grouping assignment and excludes measure and Context cards.

Existing intentional measure restrictions remain during unrelated repairs. The
user may set them manually, or explicitly request a business threshold. No
measure restriction is introduced merely because a field is assigned to Values.
Use `clear_measure_filter_selections(properties)` only for an authorized reset to
All; it keeps the cards, dimension selections, hidden Context, formulas and values.

Default constructors: `ensure_chart_filters()` for charts/KPIs and
`ensure_assigned_measure_filters()` for Planning. Both create unrestricted cards;
they preserve existing selections. `ensure_native_measure_filters()` remains a
compatible alias. Registration and filtering are separate operations.

## Numeric Planning measures use per-measure Auto

The sanitized numeric fixture contains this operation for all four
measures (two DAX, one input and one formula):

```json
{"format":{"13":"auto"},"order":8}
```

The owner is `properties.visualState.formatConfig.measure[resolvedMeasureId][]`.
Property `13` is scaling. **`auto` is different from `autoFixed`.** In that same
export, global `numberFormatting` remains `formatType: "default"` and
`scalingFactor: "autoFixed"`; the per-measure operations implement the selected
menu option. Do not change the global mode, use the display label `Auto` as a
wire value, or set a fixed `1000000` divisor by default.

Use `runtime.display_defaults.auto_number_formatting(state, numeric_ids)` after
numeric measure registration. It assigns monotonically increasing format orders,
is idempotent, and preserves colors, percentage flag `10`, decimal precision `11`,
currency prefixes/suffixes and every unrelated format property. Native source
types or custom `columnMeta.data_type: "Number"` identify numeric measures;
captions and source family do not. Text commentary, dates and checkboxes are
excluded. Never rescale stored values, inputs, bounds, formulas or aggregation.

New numeric Data Inputs, Simulation, Forecast, Formula, semantic, From Sheets and
query measures receive Auto. Explicit business formatting (for example fixed
millions or an intentionally unscaled FX rate) wins. Percentage formatting remains
percentage formatting; Auto does not turn a ratio into an amount. Default calls
preserve existing per-measure scaling; `overwrite=True` is an explicit scoped
reset. Existing cell/row/column overrides remain; inspect operation order if they
override the requested display. Do not clear all formatConfig or replace a full
globalStyles object with a fragment.

```sh
python plan.py planning-display-defaults --input display-request.json --out candidate.json
```
