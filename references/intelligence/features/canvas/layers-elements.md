---
id: CV-LAYER-01
name: Layers, element styling, and grouping
area: canvas
category: Canvas
status: IS-Confirmed
encoding: observed
visual: Canvas
sources:
  - https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/Intelligence/Properties/1.0.0/schema.json
---

# Layers, element styling, and grouping

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Z-order, layer names, visibility, grouping, and container style (background,
border, radius, padding, shadow). The Layers pane shows or hides elements,
brings them to front or back or one step forward or backward, and groups,
renames, duplicates, deletes or ungroups them. Element settings set type,
width/height and X/Y position, border width and colour, corner radius,
padding, margin, fill and shadow (blur and size).

## When to use

- Clean z-order; consistent containers.
- Dense dashboards where overlapping elements need explicit stacking.
- Moving, duplicating or deleting related elements together.
- Tabbed dashboards, where a tab navigator creates one tab per group.

## UI path

Layers pane; element format. Intelligence ribbon › Canvas › Layers: use an
element's context menu for Show/Hide, Bring Front/Back, Bring
Forward/Backward, Group and UnGroup Selection. Select an element › Layout ›
General for size, position, border and shadow; element settings also cover
type, corner radius, padding, margin and fill.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.layerProperties, visualStyles; sheet.json → visualGroupMap
Layer state: layerProperties = {layerProperties:{groupIds:[], isHidden:<bool>, name:"<layer>"},
  order:<int>}; a higher order sits further back (the background element gets the
  highest value). Runtime: user-confirmed (a rail shape stopped covering its buttons
  after the order was reversed).
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

Grouping values are not isolated. Copy the whole group from a working visual or
run `core/native-samples.md` before writing groups. `isHidden: true` keeps a
visual in the Layers pane and off the canvas; reports use it to retire visuals
that `updateDefinition` will not delete, and to keep re-emitting visuals a user
deleted in the editor (see `core/invariants.md`). An editor
save that deleted two visuals renumbered every order on that page to 0…n in
the same relative order [saved]; authored gaps (such as 951 for a band) are
not preserved, so compare relative order, not values, after a user save.

## Constraints

- Public Intelligence page settings expose `visualGroupMap`; visual config
  includes styles, position, dimensions and mobile settings. Preserve the
  [documented wrappers](../../core/definition-structure.md) or observed native
  flat shape as appropriate. Schema coverage does not establish exact layer
  ordering values or verify grouping behavior.
- Reset on an element removes all its configuration and customisation; its
  type must be chosen and configured again.
- Grouped elements act as one entity for moving, duplicating and deleting;
  use UnGroup Selection to release them.
- Hidden elements remain listed, greyed out, in the Layers pane.
- Bring Front/Back jump to the top or bottom of the stack; Bring
  Forward/Backward move one position.
- Padding is the space inside the border; margin is the space between the
  element and its container. Corner radius 0 gives square corners.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualStyles (object) — same key set on BI_TEXT, BI_SHAPE,
  BI_IMAGE, BOX, INFORIVER and ANALYTICS_PLUS owners
Keys: background {isEnabled, backgroundColor}; border {isEnabled, color, side "all",
  width}; cornerRadius {isEnabled, isCustomCornerRadius, radiusTopLeft, radiusTopRight,
  radiusBottomLeft, radiusBottomRight}; padding {isEnabled, isCustomPaddingSize,
  topPadding, rightPadding, bottomPadding, leftPadding}; rotation {isEnabled, transform};
  shadow {isEnabled, angle, blur, color, distance, opacity, placement "outer",
  side "bottom", width}; isTooltipEnabled; tooltipType "default"; tooltipPageId "auto";
  tooltipStyle {backgroundColor, labelColor, valueColor, fontFamily, fontSize, bold,
  italic, underline}
Copies: a UI duplicate saves layer name "<name> copy" and
  layerProperties.layerProperties.shallowDelete: false
Evidence: [saved] element gallery and dashboard exports
```

- [saved] Default layer names follow the element kind (such as `Text`,
  `Rectangle`, `Hbox`, `Page Navigator`, `Image`); rename layers to their role.
- [saved] Each effect is gated by its own flag: stored padding values with
  `padding.isEnabled: false`, or radius values with `cornerRadius.isEnabled: false`,
  are not an active inset or rounded corners.
- [saved] Some owners keep a `visualState.visualStyles` mirror of the outer
  styles; when it exists, keep it consistent with the owner `visualStyles`.
- [saved] A horizontal container's members carry the container's local
  `preVisualId` in `layerProperties.layerProperties.groupIds` while
  `visualGroupMap` stays empty; members can hold further group identifiers, so
  preserve the whole array. See horizontal container.
- A container or header band must sit behind everything it frames. Declare each
  intended decoration/content overlap and test clickability; an allowed overlap
  does not make a covered control usable.
- Audit the placements actually saved in the definition; copying one intended
  rectangle into every representation only proves internal consistency.

## Related features

- `CV-LAYOUT-01`
