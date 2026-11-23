---
id: CH-LIB-26
name: Network graphs
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/visualization-library
---

# Network graphs

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Nodes and links showing relationships: Category dimensions become nodes and
one Value measure weights them. Patterns: inflows/outflows between two
dimensions (Source and target mode shows both around one central node) and
parent–child hierarchies (right-click a parent node to expand or collapse).
Settings cover marker size, layout (force, hierarchical, circular, concentric,
grid, Fruchterman-Reingold), outlines, node format, links and arrows.

## When to use

- Relationship maps.
- Inflows and outflows between locations or entities, such as supply routes.
- Organizational or other parent–child structures.

## UI path

Visualizations pane › Charts 100+ › Network graph (type network in Search
Charts; its category was not captured). Assign the node dimensions to Category
and one measure to Value. Settings › Canvas › Network: Source and target mode,
layout, marker
size and outline, Node format/Color mode, Link (Dynamic or Default; solid,
dotted or dashed; straight, smooth or S-shaped; single, gradient, source or
target color) and Directional arrow (on hover or on display).

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Intelligence chart library only; never a Power BI native visual.
- Documented setups bind exactly one Value measure.
- Source and target mode needs two Category dimensions; when off, one
  member's inflows and outflows render as separate nodes.
- Color mode applies when Node format is All nodes; a legend needs Color mode
  Dynamic, then Legend › Show legend.
- Arrows show source-to-target or parent-to-child direction; confirm which
  dimension is the source before describing flows.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "NETWORK_GRAPH" (matches the decoded template id)
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"bubbleChart"
Pointer: /properties/pivotAssignments (two ordered axis endpoint fields; AC =
         weight; optional two image assignments)
Pointer: /properties/visualState/hiddenProperties_!!!_networkGraph (JSON string)
Decoded keys: sourceAndTargetMode:true; layout:"fruchtermanReingold" | "force";
              isNodePositionLocked:false; nodeSelfLink:true | false;
              linkLineConfig{linkLineMode:"default" | "dynamic",
              dynamicWidthRange{min, max}}; linkLabel{enabled, font size};
              directionalArrow.showArrow; link.directionalArrow; marker;
              cluster; interaction; format; movedShapeCoordinates;
              nodeCollapseState
Partial: {"layout":"force","nodeSelfLink":true,"linkLineConfig":
          {"linkLineMode":"dynamic","dynamicWidthRange":{"min":1,"max":5}}}
Evidence: [saved] companion-library saved owners; not isolated or re-rendered.
```

- A page titled as a network graph saved a `COLUMN_VERTICAL` owner; classify
  by the owner's chartType and template, never by page name [saved].
- Only `"force"` and `"fruchtermanReingold"` layouts were seen; the stored
  values of the other documented layouts are unknown [open].
- Default-mode owners still retain a `dynamicWidthRange`; the range alone does
  not prove dynamic link width is active [saved].
- Top-level `directionalArrow.showArrow` and a separate
  `link.directionalArrow` group coexist [saved]. Which one the renderer obeys
  is unresolved [open].
- Keep `nodeSelfLink: true` examples beside earlier false ones; neither
  replaces the other [confirmed].
- Matching display labels are not necessarily unique node keys. Image
  bindings do not prove that external images load [open].
- Node consolidation, self-link rendering, width scaling, drag, pin and force
  effects, missing endpoints and negative weights are unresolved [open].

## Related features

- `CH-AX-01`
- `CH-LBL-01`
