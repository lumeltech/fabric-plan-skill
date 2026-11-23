---
id: CV-INT-03
name: Drill-through between sheets
area: canvas
category: Interactions
status: IS-Confirmed
encoding: observed
visual: Sheet
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes
---

# Drill-through between sheets

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Opens a detail sheet filtered to the selected member.

## When to use

- Profile/detail pages.

## UI path

Drill-through settings.

## Definition encoding

```text
Part: planProperties.json
Pointer: /properties/drillThroughConfig/<destination sheet id>
Observed keys: filters[], filterConfig[] (hide, locked), keepAllFilters
Filter keys: columnIds, columnNames, columnType, dataType, dateTimeFilter,
  filterType, isDefaultFilter, isDefaultMeasureFilter, rangeFilter,
  sourceType, tableNames, valuesFilter
Destination sheet: back navigator with isNavigationBackForDrillThu:true
Evidence: live export of a UI-created test Plan with one configured
          drill-through; runtime propagation not tested.
```

Fabric Plan's saved destination configuration supersedes generic root-level
guidance (`drillThroughConfig` is under `properties`). Copy full native
destination/filter structures and resolve every field through the registry.
A drill-through menu or return control in screenshots does not prove runtime
filter propagation or return state.

## Constraints

- Remap destination IDs and preserve filter/filterConfig alignment.
- A detail page, drill tip or back arrow is not an executed transition.
  Confirm source keys, destination predicates (member, date and other context)
  and return state before calling a page a verified drill-through destination.
- If a destination promises one member but shows several members or
  out-of-scope dates without an incoming action, label it as an unfiltered
  detail log rather than claiming verified drill-through.
- Test that drill filters reach every measure and update any selected-member
  breadcrumb; visible context text does not prove dynamic bindings or filter
  propagation.
- Enforce detail permissions independently of navigation: an aggregate
  selection does not approve record-level access. Expose only authorized,
  minimum-necessary detail fields.
- Validate source selection, destination context and return navigation in a
  permitted test plan, using authorized synthetic records, before calling the
  behavior verified.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- [confirmed] User correction: destination registrations and independently
  reconciled DAX checks were wrongly accepted as drill coverage without inspecting
  the source's field wells. Before any pass, inspect each destination's native
  drill-through field registration (exact semantic table and column identity); a
  slicer, axis field, label or incoming-context cache is not a substitute. A
  negative control (remove a required registration, expect the route to disappear,
  restore and retest) must fail when the field is absent.
- [saved] Adding a child level to a chart source saved
  `properties.drilldown.drillFields.axis[]` entries with `dataRole: "axis"`,
  `drillType: "DOWN"` and the child field's `queryName`. That is drill-down
  configuration, not a drill-through registration or navigation; do not prescribe
  it for every source.
- [confirmed] Eligibility fields and carried context are separate: corrected
  destinations differed, one registering two fields with `keepAllFilters: true`,
  another one field with `false`. Do not register every slicer field or force Keep
  all filters on; define and test each destination's scope.
- [saved] A destination sheet's `drillThroughConfig` entry kept `filters` and
  `filterConfig` arrays of equal length, each `filterConfig` entry saving
  `hide: false` and `locked: false`.
- [confirmed] A destination's filter panel listed the same field twice, once from
  a slicer and once from the clicked axis point. Record each predicate's field
  identity, origin, values, operator and scope, then test slicer only, axis point
  only, both identical, a broad slicer narrowed by a click, and clear/back/re-drill.
- [open] Whether the repeated entry is expected display. Identical include-value
  restrictions on one field should act as their intersection and must not multiply
  rows or totals; different fields with the same label must not be merged.
- Do not hide or deduplicate filter cards, discard valid restrictions or switch
  Keep all filters off globally to tidy the panel; capture a functional
  reproduction when stale restrictions survive clear/back or totals are wrong.
- [confirmed] After user edits, recheck the destination's record grain: a
  raw-record destination became grouped detail. Retire old raw-grain assertions and
  keep the user's edits instead of reverting them.
- Without UI access the drill test is blocked, not passed.

## Related features

- `CV-ELEM-02`
