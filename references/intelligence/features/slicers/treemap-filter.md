---
id: SF-TREE-01
name: Treemap filter
area: slicers
category: Category filters
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/add-a-treemap-filter
---

# Treemap filter

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Selects members from a treemap sized by a measure.

## When to use

- Visual selection by share.

## UI path

Filter type › Treemap.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.hierarchySettings (treeMapColor, treeMapTileType, treeMapLassoType)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

`hierarchySettings.hierarchyViewType: "map"` appeared on UI-saved tile facets
with a progress bar and no measure binding; it does not prove a treemap
filter. No UI-saved Super Filter with a sizing measure was found, so the
treemap binding remains uncaptured.

## Constraints

- Grouped measure-sized tiles, parent totals and an optional range slider are
  presentation. Capture hierarchy/value bindings, selected states and
  interaction scope. Super Filter treemap evidence does not establish a
  standalone chart's filter behavior.
- Verify parent/leaf aggregation, multi-selection and missing/negative values.
  Capture lasso behavior before relying on it; truncated tile labels require
  accessible full labels.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- A few owners save `hierarchyViewType: "map"`, some with
  `measureFilterSettings.enableMeasureFilter: true` [saved]. Whether that
  measure sizes the tiles is unresolved [open].
- Map owners saved the tile and lasso selectors as `"square"` and
  `"inclusive"` [saved]. Lasso and parent/child selection behavior is
  untested [open].

## Related features

- `SF-HIER-01`
