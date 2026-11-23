---
id: KPI-CAT-01
name: Categorical leader, exception and latest-period cards
area: kpi
category: KPI cards
status: IS-Confirmed
encoding: unverified
visual: KPI card
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-a-dashboard
---

# Categorical leader, exception and latest-period cards

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Displays a category label (top/underperforming brand or market, account tier,
latest month) with supporting revenue, contribution or comparison text.

## When to use

- Answers "who?" or "which period?" rather than only "how much?".

## UI path

Visualizations pane › KPIs; exact categorical template selection not captured.

## Definition encoding

```text
Presentation evidence: screenshots only.
Exact category/ranking/latest-period template: not isolated.
Base family only: CARD / ANALYTICS_PLUS / 50 (see KPI-CARD-01).
```

Do not invent `topBrand`, `latestMonth` or ranking expressions. Resolve the
category, ordering measure, support measures, tie rules and date role against
the registry. Capture a native same-kind card before authoring this behavior.

## Constraints

- Define the ranking before generating the card or its narrative: filtered
  scope, selected path, ordering measure and its definition, ties,
  empty-context result and any share denominator. The label must match the
  ordering measure; a "highest severity" label needs a severity measure.
- Define ranking scope and what "underperforming" means (growth, plan variance,
  absolute revenue, etc.); screenshots do not establish the computation.
- Do not copy a screenshot winner or infer dynamic ranking from a title.
  Highlighted tokens establish neither a dynamic categorical template nor
  interactive parameters; capture bindings and reconcile with related visuals.
- Latest month depends on the intended reporting date, not necessarily today.
- Availability does not authorize semantic-model changes.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/pivotAssignments - text measures in bucketId
  "TextCategory" (UI: Tooltip-Text categories) beside an AC assignment:
  {"bucketId":"TextCategory","sourceType":"PowerBI","columnType":"Measure",
   "dataRoleType":"Measure","dataType":"String"}
Pointer: /properties/visualState/hiddenProperties_!!!_kpiControls (JSON string)
  decoded gridLayout[] text item:
  {"type":"text","dataType":4,"measureKey":"AC","isHidden":false}
staticText: hash-mention spans for TXT1..TXT3; HTML-escaped data-value keys
  title, key, value, text, color, image, avatar
Evidence: [saved] saved native context cards
```

- Saved cards bind one or three text measures; three-field cards show TXT3,
  TXT2 and TXT1 in that order [saved]. The ordinal carries no meaning.
- These are `ANALYTICS_PLUS` CARD owners, not `BI_TEXT`; the item's
  `measureKey: "AC"` does not identify the fields in its HTML [saved].
- Keep each mention's identity and runtime key separate from its cached
  text and value, and preserve HTML escaping and single-brace JSON [saved].
  Never copy donor tokens or cached business text.
- Bind an existing text-returning measure rather than a static caption; a
  new measure follows the model-measures permission gate.
- Mention insertion, filter refresh, multi- or empty-selection behaviour and
  reopen persistence are untested; cached text does not prove refresh [open].
- This is the only saved mechanism found for text values in cards; whether a
  dedicated categorical template exists is unresolved [open].
- Check TextCategory-to-token closure, JSON parsing after HTML unescaping and
  the retained AC binding.

## Related features

- `KPI-CARD-01` — native card family.
- `KPI-FMT-01` — text/support formatting.
- `KPI-VAR-01` — supporting comparison.
