# Integrated variance in a comparison chart

Use a vertical integrated variance column when comparing actual or planned values with one baseline at a shared category grain. Keep single-series charts unchanged and honor an explicit request for a different comparison style.

Examples: sales actuals versus targets, forecast versus actuals, proposed salary
versus base salary, expense budget versus spend, and risk-adjusted outlook versus
baseline. Choose the comparison direction from the business meaning. AC and PY
are chart roles: PY need not mean previous year. Preserve meaningful business
captions, units, category grain, filters and source-specific field identities.
An increase in cost is not automatically favorable; preserve configured sign and
color polarity, or explicitly select it from the business requirement for new work.

## Build a local presentation candidate

For an existing resolved AC/PY chart, create a presentation-only candidate:

```text
python plan.py integrated-variance --input chart-properties.json --out chart-candidate.json
```

The input is the inner native properties object. `apply_integrated_variance`
requires type 50, one numeric AC and one numeric PY, and category grouping. It
preserves assignments, source IDs, measure GUIDs, filter cards, titles and geometry.

Keep the top-level type, template, visible AC configuration and chart mode consistent. The integrated view still needs the PY assignment even though its renderer configuration has only one visible AC entry. Do not substitute an unverified horizontal enum. The candidate is not a rendered chart or evidence of calculated variance.
