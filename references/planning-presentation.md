# Planning matrix presentation

Start with the decision the reader must make. Show units, period and source
role in the header; distinguish actuals, editable assumptions and calculated
results without relying on color alone. Size headers to the content. Preserve
existing row/column order and deliberate user selections during a scoped edit.

For a negative-variance rule, resolve target and test measures independently.
Set favorable direction from business meaning (lower expense can be favorable),
and decide whether row/column totals should be evaluated. Test zero and missing
separately. A rule that colors every total red can conceal a correct leaf rule.

```sh
python plan.py format-matrix --input formatting-request.json --out candidate.json
python plan.py planning-totals --input totals-request.json --out totals.json
```

These commands construct local candidates. For formatting, use current state
and exact IDs; do not replace unrelated rules or treat a serialized color as
evidence that a UI rendered it. For totals, distinguish **placement** (e.g.
column total on the left) from **calculation** (e.g. closing balance at last
period, not a sum over time). Preserve units, source bindings and storage keys
when changing expansion, widths, scale, hierarchy icons or header height.
