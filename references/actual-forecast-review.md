# Actual-to-forecast boundary in QTD reviews

A forecast-only supply or driver series can be blank before the first open month.
Do not feed it directly into a QTD completeness check that also includes closed
actual months. First construct a hidden monthly review series with the bundled
`formula_create`: `IF(${open} > 0, ${plan}, ${actual})`, resolving all references at
the same business grain. Use model actual revenue, cost, investment or
compensation for the closed branch. Then use `time_expression` on that series
and its missing-value indicator. Missing required actuals and FX remain missing.

For a specifically forecast-only change, such as an incremental planned volume
bridge or future risk adjustment, closed months can be zero only when the
business definition explicitly holds actuals fixed. Do not apply that zero rule
to financial actuals. Keep the as-of QTD cutoff separate from the quarter-end
cutoff for a full-quarter estimate. Retain all required historical months.
A comparison baseline must likewise combine actuals-to-date with the selected
open forecast if that is the requested outlook comparison.

When correcting a formula, preserve the existing measure identity, storage and unrelated records. Check a synthetic closed/open boundary with known amounts before relying on the definition; a local candidate does not prove evaluation.
