---
id: SF-HIER-01
name: Hierarchy filter
area: slicers
category: Category filters
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/add-a-hierarchy-filter
---

# Hierarchy filter

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Tree slicer over multiple levels with indent, default expand level, leaf single-select, child counts.

## When to use

- Region › Country › City; org trees.

## UI path

Add dimensions to Category in top-down order, then Filter ribbon › Quick Mode ›
Hierarchy. Properties › Global › Select Type sets checkbox, radio or list;
Expand to Level, Parent Child Indent, Child Count (leaf or immediate child),
Select All and Soft Selection are hierarchy settings.

## Definition encoding

```text
Registration: SUPER_FILTER; /properties/visualType = 60
Mode: /properties/visualState/facetSettings/enableFacetMode = false
  (configuration.visualType stays "FACET"; Quick Mode › Hierarchy saves this switch)
Levels: /properties/pivotAssignments = one bucketId "category" item per level,
  order 0..n top-down (first field = root)
Per level: /properties/superFilterAssignments[i] = {bucketId:"category",
  configuration:{name:<level>, sort:[<level asc/desc>], selectAll, singleSelect,
  visualType:"FACET", …}, filter:[], filterLevel:"visual", id, isDefault:true,
  isDaxMeasure:false, isDefaultMeasure:false, position:"RIGHT",
  pivotAssignments:[<that level only, same order>]}
Tree settings: /properties/visualState/hierarchySettings
  hierarchyViewType:"tree"; hierarchyTreeViewType:"checkbox" | "list";
  enableDropdown:false (inline tree) | true (dropdown); hierarchyLevel (expand-to
  level); displayChildCount; leafCountOrChildCount:"leafCount"; leafSingleSelect;
  softSelection; indent; root/parent/childNode font and colour keys
Companion: facetSettings.showCount:true and showFacetHeader:true in multi-level saves
Selection: visualState.slicerFilterAssignments VALUES filter whose columnIds list
  every level and whose valuesFilter ids are tuples, e.g. {id:["Q2","Jun"]}
Evidence: eight UI-saved multi-level filters (checkbox tree, list dropdown, checkbox
  dropdown) and single-level list variants in native Plan exports; applied in a
  report build with two and three levels and read back. Rendering of the three-level
  build awaits confirmation.
```

A single field with facet mode off renders the hierarchy view types (list,
checkbox tree) for one level; a single-level list with a stored default was
also observed. Clone a UI-saved hierarchy filter, rebuild the per-level
pivots and assignments for the target fields, and reset stored selections.

## Constraints

- An inline tree needs height for its rows (about 30px each plus the toolbar);
  in a short filter band use the dropdown variant or a side filter pane; a
  pop-up (SF-FEAT-05) only with the user's approval.
  The dropdown variant (`enableDropdown: true`) is common in native reports;
  check that its open list is not cropped at the target viewport.
- A radio select type is documented but not captured; do not invent its enum.
- When a parent and its child can be selected together, define selection
  semantics so totals are not double counted.
- Checkbox/radio/list trees, partial parent states, level-specific node styles
  and child counts are presentation. Capture expansion, global versus
  branch/leaf selection, selected-state styling and whether counts mean
  children or descendant leaves.
- Define total/filtered/selected count scope; Others may be generated or a
  source member. Use stable keys for duplicate names and preserve model RLS.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Radio tree (partial): /properties/visualState/hierarchySettings =
  {hierarchyViewType:"tree", hierarchyTreeViewType:"radio", singleSelect:true,
   leafSingleSelect:false, softSelection:false} [saved]
hierarchyViewType values in saved owners: "tree", "list", "map" (map: SF-TREE-01) [saved]
styleby:"canvastheme" in every owner of one inspected sheet [saved]
  Its meaning and alternative values are unresolved [open]
Evidence: saved owners only (radio not captured); copy the whole group from a same-kind
  readback rather than writing these values by hand.
```

- `hierarchySettings.singleSelect` is its own key, separate from
  `facetSettings.singleSelect` and the registration's; a tree/list owner saved
  it false while the radio tree saved true [saved]. Do not force the three to
  match because their names overlap.
- Facet-mode owners, including a facet dropdown, kept `enableDropdown: false`
  [saved]; how it relates to `facetViewType: "dropdown"` is unresolved [open].
- A user finishing save switched `enableDropdown` on for a compact control and
  separately cleared its stored selection [saved]. Dropdown presentation and
  selection scope are separate changes; never clear an approved selection to
  copy the styling.

## Related features

- `SF-TREE-01`
- `SF-FACET-01`
- `SF-FEAT-05`
- `SF-QUICK-01`
