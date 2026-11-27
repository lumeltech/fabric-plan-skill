# Intelligence dashboard visual type coverage

An Intelligence dashboard can hold more visual types than this package constructs. Use this guide for three things:

- to build a decomposition or organization tree;
- to say precisely which type an existing visual is and what this package may change;
- to say what must be reported instead of improvised.

Classification reads current exported or locally built properties. It never contacts a service and never rewrites a visual.

## Contents

- [Coverage ledger](#coverage-ledger)
- [Build a tree](#build-a-tree)
- [The tree family](#the-tree-family)
- [Rules that keep a tree intact](#rules-that-keep-a-tree-intact)
- [Evidence](#evidence)

## Coverage ledger

| Dashboard content | What this package does | How |
| --- | --- | --- |
| KPI card, column chart, IBCS recipe chart | Constructs it from the current model or query catalog and completes the field registrations. | `intelligence`, `integrated-variance` |
| Semantic slicer, text block, Page Navigator | Constructs it with placement and navigation rules, for a new or an existing dashboard. | `intelligence`, `navigator` |
| Embedded Planning workbench, Matrix table | Constructs the page-local reference to the directly owned visual, or a Matrix in its place. | `embed`, `intelligence` |
| PowerTable | Constructs a visible sheet. When no connection resolves, the source binding is deferred. | `powertable`, `maintenance-shell` |
| Decomposition and organization trees | Constructs the tree from model dimensions and values. | `intelligence` |
| Row and measure trees | **Names and preserves only.** Fabric's editor does not offer them. | `visual-type-coverage` |
| Gantt, Map, Shape, Image, Box, Adhoc Matrix, buttons, bookmark tabs and other Analytics+ chart families | **Not named or constructed.** Keep them unchanged and report them as unclassified. | — |
| In-table micro-charts | Not a dashboard visual type: they are a column feature of a grid. | — |

## Build a tree

Add the tree to a dashboard's `charts` list, so it takes a chart slot. A spec with `tree` is built by `scripts/runtime/tree_visuals.py`:

```json
{"label": "Revenue drivers", "tree": "decomposition",
 "levels": ["Geo[Region]", "Product[Category]"], "measure": "Facts[Revenue]"}
```

```json
{"label": "Organization", "tree": "organization", "levels": ["Staff[EmployeeId]"],
 "parent": "Staff[ManagerId]", "fields": ["Staff[Name]", "Staff[Title]"],
 "sparkline": ["Period[Month]"], "measure": {"field": "Facts[Hours]", "label": "Hours"}}
```

| Spec key | Tree role (`bucketId`) | Tree type | Rule |
| --- | --- | --- | --- |
| `levels` | `rows` | both | One or more model dimensions, in drill order. |
| `measure` | `ameasure` | both | A field ID, `{field, aggregation, label}`, or a list. Required for a decomposition tree, which breaks this value down. |
| `parent` | `parentid` | organization | One identifier dimension for parent-child data. |
| `fields` | `fieldid` | organization | Detail dimensions shown on each node. |
| `sparkline` | `columns` | organization | Dimensions for the node sparkline; needs a measure. |

Fields come from the current model or a registered query output, never from labels. A dimension appears once across all roles. Unknown keys are refused, including layout and styling keys.

**The definition carries what Fabric saves when a tree is added from the Elements pane:**

- the visual declared as `TREE`, which is visual type 25 in its properties;
- `DECOMPOSITION_TREE` or `ORGANIZATION_TREE` in both the top-level `chartType` and `visualState.chartType`;
- the pivot assignments above.

The tree derives its orientation, layout, node view and node templates when it loads, so none are written. No filter cards are written, and slicer selections are not saved into a tree's state; that state has not been observed for trees.

**Availability is a tenant setting.**

- Fabric loads a decomposition or organization tree only when the tenant's switch for that tree type is on. Otherwise the page drops the tree as it loads.
- The parent identifier role also needs the tenant's organization-tree parent-data mapping. Without it, Fabric removes the parent identifier when the tree first renders, and saves that change.

The dashboard identity lists these switches per tree visual under `treeRequirements`, with what Fabric does when each is off; `runtime.tree_visuals.tree_requirements(properties)` returns the same list for one tree. Report them with the build. If a tree doesn't appear after import, these switches are the likely cause. A readback proves the tree was saved, not that the destination shows it.

## The tree family

The tree types share one discriminator field. `runtime.intelligence.tree_visual_types` returns the four values and their display names. `runtime.intelligence.classify_visual` reads either position of that field, the same field a card writes as `CARD`:

```python
from runtime.intelligence import classify_visual, tree_visual_types
props = exported_visual_properties            # one dashboard visual
kind = classify_visual(props)
# {'family': 'tree', 'chartType': 'ORGANIZATION_TREE', 'visual_type': 'Organizational tree', 'engine': 'native tree'}
```

The `engine` key tells two trees apart when the properties carry their visual type:

- `native tree` means type 25, the tree built here.
- `Analytics+ chart` means type 50. Analytics+ has its own decomposition tree chart.
- `None` means the visual type is absent.

`classify_visual` returns `None` when the value is absent or belongs to a type this package does not name. `None` is an answer, not a license to guess: keep the properties unchanged, then report the type as unclassified.

Each tree also carries its own configuration family in the visual state. It covers:

- orientation (left-to-right or top-to-bottom);
- layout (the decomposition tree is restricted to the normal layout);
- node view (full or minimal);
- node components (variance, variance percentage, sparkline, child count);
- node template shape (simple, card, metric summary);
- connector line and arrow, and the legend;
- per-node conditional formatting, the header key-performance measure and sparkline colors.

The tree derives these on load. None of them has a bundled writer, default table or formatter here.

## Rules that keep a tree intact

1. **Never retype a tree.** A card-state writer fills the store slices a KPI needs and sets the discriminator to card. That would flatten a tree into a single number. The bundled card writer refuses when `classify_visual` reports the tree family; pass tree properties through untouched and say so.
2. **Keep the type domains apart.**
   - A native tree is `TREE` in the definition and visual type 25 in its properties. Fabric's import and export map those two to each other.
   - An Analytics+ decomposition tree is a type 50 chart with the same chart type value. Do not convert one into the other.
3. **Availability varies by destination.** The tenant switches above gate the decomposition and organization trees. Fabric's editor offers no row or measure tree, and the measure tree depends on a tenant switch in the Planning grid. When a type isn't available, report that visual type as unavailable. Don't substitute a card, chart or Planning grid the user did not ask for.
4. **Tree field roles are not Planning pivot roles.** Chart and card audits, pivot layout hashes and column presentation checks do not classify a tree. Don't use them as readiness tests for one.
5. **Keep the gap independent.** When an unavailable tree is one requested element among several, continue the supported modules and record the tree as an incomplete item. Record it the same way as an unbound PowerTable sheet. An unconstructed element is never evidence that the whole request failed, and never a reason to drop it silently.

## Evidence

The type names, roles, chart type selectors, availability switches and configuration families come from the product implementation of these trees. The saved shape built here is the one Fabric writes when a tree is added. No export containing a tree ships with this package. Classification, construction and the card-writer refusal are covered offline by tests. Rendering and tenant availability remain unverified until an export of the actual destination is inspected.
