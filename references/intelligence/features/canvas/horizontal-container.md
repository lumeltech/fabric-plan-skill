---
id: CV-BOX-01
name: Horizontal container (Hbox)
area: canvas
category: Elements
status: IS-Confirmed
encoding: observed
visual: Canvas
sources:
---

# Horizontal container (Hbox)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

A `BOX` element lays out member visuals, such as a row of KPI cards, in one
horizontal strip with a gap, alignment and overflow handling. [saved] It is its
own layout element, not a decorative rectangle (`BI_SHAPE`) and not a
Layers-pane group. Merged from the companion Intelligence authoring library;
tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

## When to use

- A strip of equal-width KPI cards or tiles that should stay aligned together.
- Preserving an existing grouped row while editing its member cards.

## UI path

Not captured. Other elements are inserted from Intelligence ribbon › Elements
in editing mode; confirm whether the container is inserted there or created
from selected visuals, and capture the steps that add members, before
instructing a user. The saved layer name defaults to `Hbox`.

## Definition encoding

```text
Registration: BOX; /properties/visualType = 206
Pointer: /properties/visualState/boxState (object, not a JSON string)
Keys: boxType "horizontal", initialBoxType, gap, horizontalAlignment "left",
  verticalAlignment "top", wrapContent false, isExpanded true,
  overflow {horizontal "hidden", vertical "hidden"}
Membership: each member's /properties/layerProperties/layerProperties/groupIds
  contains the container's local preVisualId string; sheet.json visualGroupMap
  stayed empty
Companion: writeback.json (empty destinations)
Evidence: [saved] containers holding KPI cards in several saved exports;
  resizing, clipping and selection not tested
```

[saved] Outer `visualStyles` (a `"transparent"` background, border, radius,
padding, shadow) and layer state stay separate from `boxState`. Copy a complete
native container together with its members, and run `core/native-samples.md`
before writing a new one.

## Constraints

- [saved] `boxType` is the active layout: one container kept a historical
  `initialBoxType: "vertical"` while `boxType` was `"horizontal"`. Never
  overwrite the active value from the historical one.
- [saved] The membership token is neither the container GUID nor the sheet
  GUID. Allocate a new local ID through the target's ID registry and set every
  member's `groupIds` together; never globally replace a numeric string.
- [saved] Some members hold additional group identifiers; preserve the whole
  array. Resolve membership from `groupIds`, not from overlap or layer names.
- [saved] One container had no members in the exported arrays; do not reclassify
  a childless `BOX` as a shape. [open] Its intended use and runtime grouping.
- [saved] Members were roughly equal-width rectangles about 1 px inside the
  container, separated by `gap` pixels. Update container and member bounds
  together; `gap` is not an amount to add to normalized coordinates.
- [open] With `wrapContent: false` and hidden overflow, members whose widths plus
  gaps exceed the container may clip rather than wrap; size them to fit.
- [open] Vertical and nested boxes and responsive resizing are untested.
- After read-back, test resizing, clipping, membership, selection and
  clickability, and re-check membership after any UI save, which can renumber
  `preVisualId`.

## Related features

- `CV-LAYER-01` — layers, z-order and grouping; `groupIds` live in `layerProperties`.
- `KPI-CONT-01` — KPI-internal containers and flex groups.
