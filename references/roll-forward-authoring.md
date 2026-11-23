# Carry a balance between periods

Choose a continuous ordered calendar, entity grain, unit and sign convention.
Resolve the prior actual that seeds the first open period. Closing is opening
plus signed movements; next period opens at the prior close. If the first
visible period lacks history, identify a governed seed rather than using zero.

For example, 100 opening units + 25 received − 40 consumed = 85 closing units.
The next period opens at 85. Preserve a negative close if it represents a real
shortage. Hires, receipts and collections can sum across time; closing stock
generally cannot. For cohort collections, apply lag rates to the original
invoice cohort, not this month's sales.

Distinguish a backwards time reference from a same-period cycle. A cumulative
sum can replace recurrence only when movements are independent of the opening
balance. If exits depend on opening headcount, that shortcut changes the
business result. The local build rejects cyclic measure dependencies; surface
the gap rather than emitting an invalid graph.

Use `ReadAndEdit` only for decisions the planner can change; leave seed and
derived closing measures non-editable. Record zero/blank and prefill policy.
For a Measures-in-Rows layout group opening, drivers, closing and diagnostics;
the hierarchy should not change arithmetic, measure IDs or storage.

```sh
python plan.py roll-forward-presentation --input presentation.json --out candidate.json
```

This applies a resolved presentation locally. Check opening/closing continuity,
seed visibility and totals against illustrative amounts before treating a
definition as ready. Local construction does not establish calculated results.
