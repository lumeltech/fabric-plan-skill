---
id: CV-EMBED-01
name: Embed a Planning or PowerTable sheet
area: canvas
category: Embedding
status: IS-Confirmed
encoding: observed
visual: Sheet
sources:
  - https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/Definition/1.0.0/schema.json
  - https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/Intelligence/Properties/1.0.0/schema.json
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/get-started-with-reporting
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/visualize-simulations-budgets-and-forecasts
---

# Embed a Planning or PowerTable sheet

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Places a Planning (or PowerTable) visual on the Intelligence sheet so users plan from the dashboard.

## When to use

- Product context for Planning front-door sheets. New embedding is **blocked
  until module integration** in this skill; preserve existing embeddings.
  See [module boundaries](../../core/module-boundaries.md).

## UI path

Visualizations pane › **Planning**, then choose the sheet in **Select an
Existing Planning Sheet** (first-party guide). PowerTable sheets use the
**PowerTable** tile and its sheet selection (first-party guide); the tile
appeared disabled in the captured pane.

## Definition encoding

```text
Path: definition.json → sheets[i].workloadItemEntityVisuals {visualType: "PLANNING" | "POWERTABLE", isEmbedded: true}
Host sheet.json → reactiveVisualProperties[] {visualId, properties{position, dimension, lockAspectRatio, originEntityId, visualInteractions, visualStyles}}
Embedded PowerTable → host sheet.json assignmentColumnMap (column label → columnId, parentPath, source, sourceId)
Evidence: decoded native readbacks (embedded Planning grid; embedded Planning and PowerTable visuals with From Sheets consumers)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Public root/Intelligence schemas document registration and embedded/origin
  references, not an end-to-end embedding recipe. Upstream contract coverage
  does not remove the module-integration gate or verify source behavior.
- Placement copies must agree; bounded default scope. Source sheets belong to
  their owning module skills, which are not integrated in this release.
- A Planning grid whose inputs feed Intelligence visuals is product context
  only; building it is blocked in this release.
- Embedded measures reach consumers as `"sourceType": "Visual"` bindings that
  validation lists but cannot check against the model. Preserve them and the host
  `assignmentColumnMap` unchanged; see [cross-module blend](../../core/cross-module-blend.md).

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

Intelligence-hosting side only; new embedding stays not enabled in this release.

```text
Chain: the source Planning sheet and the host sheet register the same root visual
  GUID; owner properties.json, dataInput.json and writeback.json exist only under
  the source sheet, never under the host
Host: sheet.json /properties/reactiveVisualProperties[] {visualId: <owner's local
  preVisualId string>, properties {position, dimension, originEntityId,
  lockAspectRatio, visualInteractions, visualStyles}}
Evidence: [saved] embedded Planning references in several saved exports; rendering,
  editing and writeback not tested
```

- [saved] In the usual pattern the placement `visualId` equals the owner's
  `preVisualId`, not the root GUID. Exceptions seen: an owner with no `preVisualId`
  key (absent, not null) and an `originEntityId` that differed from a matching
  `visualId`. Never substitute `originEntityId` or geometry equality for the join or
  synthesize a missing ID; record that placement as unresolved.
- [saved] One owner can back several placements, including repeated placements on
  different host sheets. Count the owner once for property frequencies, but
  inventory each placement's geometry, styles and interactions. For a scoped move,
  edit only that placement (and mirrors proven to belong to it); never move the
  shared owner to reposition one placement.
- [open] Owner and placement rectangles differed in some saved embeddings, and the
  companion library advises against forcing distinct placements to be equal; this
  differs from "Placement copies must agree" above, which wins until a native
  capture resolves it.
- [saved] An embedded PowerTable reference whose owner parts (`properties.json`,
  `columnConfigs.json`, `source.json`, `sourceSettings.json`) were absent is an
  incomplete association, not a donor. [open] PowerTable owner parts and local-ID
  mapping.
- [saved] A `commentSettings.json` companion or a local `preVisualId` on an owner
  does not establish embedding; require the source-sheet, owner and placement chain.
  References with no owner properties stay unresolved; never infer their fields or
  geometry from a `writeback.json` companion.
- [saved] One export held a sheet entry with literal `sheetType: "BI_REPORTING"` and
  an `UNKNOWN` visual but no sheet or visual parts. Keep the literal type, do not
  relabel it PowerTable or build companions, and keep the root-reference inventory
  separate from the parts actually present.
- Hide a source sheet from navigation only after its embedding works; never delete
  hidden sheets that support embedded visuals.
- Match each placement in `reactiveVisualProperties[]` by its identity join, never
  by array position. [open] Numeric visual IDs can change during import; re-read
  the owner `preVisualId` and the placement `visualId` from the post-import readback
  before treating the join as intact.
- [saved] Beside the origin placement in
  geometry invariants, one review of several
  host sheets found other states: a correct host override while the owner kept an
  older rectangle, and a host with no override still on a preset 16:9 canvas.
  Inspect owner geometry, host override and host canvas for every placement;
  fixing one host does not fix the others. [open] Which copy wins when they differ
  was not isolated.
- Keep an existing embedded grid's toolbar, header, rows and footer unobscured,
  with host slicers and cards outside its rectangle; check them in the rendered page
  at presentation size, not only in the saved rectangles.
- [open] A registration audit of a host's own visuals does not cover embedded
  placements (the companion's audit counted only non-embedded visuals); test
  separately that host slicers filter each existing embedded placement and its
  dependent content.
- [open] A message that one or more visuals are deleted or invalid points to the
  referenced source visual and its import or runtime identity mapping, not to a
  broken formula token.
- Never synthesize a PowerTable embed from a standalone PowerTable sheet; future
  work needs a complete embedded donor or a controlled before/after export of a
  disposable copy.

## Related features

- `CV-LAYOUT-01`
