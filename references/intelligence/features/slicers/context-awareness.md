---
id: SF-CTX-01
name: Slicer context awareness
area: slicers
category: Display
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/create-a-filter-panel
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/context-awareness
---

# Slicer context awareness

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Slicer behaviour that follows the filter context.

## When to use

- Scenario-aware slicers.

## UI path

Context settings.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.filterContextProperties
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- `filterContextProperties`, chart `hiddenProperties_!!!_filterContextSetting`
  (`hash`, `filterContextKey`, `filterContextJson`), Matrix `filterContextHashMap`
  and slicer `embeddedSuperFilter` are caches the editor fills on load (for
  example with the page's year and data-status context). Reset them when
  cloning from another report; never author their contents.
- Repeated totals across slices, stack segments or facets do not prove cascade.
  Test field binding, model relationships, filter-removing measures and visual
  context separately; never divide repeated values to force reconciliation.
- Give facts with different grains or sources a distinct, explicit scope.
- First-party panel docs describe cascading panels that update available
  choices across categories. A static screenshot does not show the
  transition; test it at runtime.
- Treat within-panel cascade, cross-visual interactions and cross-sheet sync
  as separate settings. Test invalidated selections, parent/child context,
  measure/rank recalculation and reset behavior; matching chips are not proof.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Received context: /properties/visualState/embeddedSuperFilter/superFilterAssignments
  holds compact {"filter":[...]} entries carrying other controls' selections
  (semantic column ids and valuesFilter members; no registration id, bucketId or
  pivotAssignments) [saved]
  A control can also receive a complete locked single-select page registration there [saved]
Consumers: filterContextProperties.filterContextJson recorded the page period and a
  control's member in one native save [saved]
```

- Received context is not a swapped binding: resolve owner registration, own
  selection (`slicerFilterAssignments`), received context, page scope and
  consumer copies separately; do not require them to be equal [saved]. In an
  existing report keep received context; the reset above applies to clones.
- Recorded consumer context does not prove propagation, clear behavior or
  cross-page sync, and a named synced-slicer group does not prove sync is
  enabled (CV-INT-02) [open].
- Updating only `embeddedSuperFilter` and `filterContextProperties` left an old
  selection in a consumer's JSON-string `hiddenProperties_!!!_filterContextSetting`
  [saved]; handle every copy in its native serialization. The companion rewrote
  all copies to the new scope; the reset rule above wins [open].
- A selected control does not make commentary filter-aware; notes key on the
  consumer's filter-context hash (CH-NOTE-01, MX-NOTE-01) [saved]. Preserve
  filter-dependent note keys, hashes and bookmark snapshots when changing a
  control's field or default.
- Planning scenario selectors stay single-select for input persistence and
  separate from analytical comparison filters that must keep baselines
  [confirmed]; Planning persistence is not enabled in this release.

## Related features

- `MX-CTX-01`
