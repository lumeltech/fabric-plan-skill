# Forecast boundaries and calendar calculations

Resolve the authoritative actuals measure, last closed period, first open
period, horizon, timezone and planner edit policy before building a forecast.
A `Forecast` measure names its actuals by key and uses explicit `start` and
`end` dates. Do not infer a growth assumption from the word “forecast”.
For example, with an existing `actual` key in the same sheet:

```json
{"key":"outlook","kind":"Forecast","label":"Outlook","actuals":"actual",
 "start":"2026-01-01","end":"2026-12-31"}
```

Use ordered calendar fields, not alphabetical month captions. If fields such
as `Calendar[FY]` and `Calendar[FQ]` are not self-describing, set sheet
`columnTimeLevels` to map those exact IDs to `Year` and `Quarter`. Verify the
requested grain and fiscal/weekly parentage; don't introduce a month axis
where weeks cross calendar months.

For quarter-to-date review, combine closed-period actuals and the open-period
plan at monthly grain **before** aggregating to quarter. Forecast-only drivers
may be blank in history. A missing required actual is not a zero variance.
Keep the as-of cutoff distinct from quarter-end. Preserve the historical
periods needed by prior-year or prior-cohort formulas. A one-time as-of control
is not a new time dimension or a repeated input for every month.

Local construction can establish axis order, references and forecast settings.
It does not evaluate formulas, fill stored inputs or establish that subsequent
edits, closure or changes in the as-of date recalculate correctly.
