---
id: CV-LAYOUT-01
name: Canvas size, background, and grid
area: canvas
category: Canvas
status: IS-Confirmed
encoding: verified
visual: Sheet
sources:
  - https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/Intelligence/Properties/1.0.0/schema.json
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-a-dashboard
---

# Canvas size, background, and grid

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Canvas dimension, background/wallpaper, border, grid lines, snap to grid,
smart guides, mobile canvas. Dimension-type presets size the board for its
display medium (such as A4, desktop, TV, tablet or mobile), or set a custom
width and height. Corner radius is uniform or per corner. Grid lines divide
the canvas into even sections, smart guides show alignment lines while moving
elements, and Lock elements fixes existing elements' size and position.

## When to use

- Every new sheet.
- Sizing a dashboard for its target screen or print page.
- Aligning many elements consistently with grid lines and smart guides.
- Protecting a finished layout while still adding elements (Lock elements).

## UI path

Canvas settings: Intelligence ribbon › Canvas (editing mode) › General for
dimension type and size, background or wallpaper, border, corner radius and
grid lines; smart guides and Lock elements are canvas options too.

## Definition encoding

```text
Path: sheet.json → canvasStyle (dimension, background, wallpaper, gridLineSettings, mobileCanvas)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

Native Custom sizing was captured through Intelligence > Canvas > Type >
Custom on a reporting sheet:

```json
{"elementScalingUnit":"percentage","height":900,"type":"CUSTOM","width":1600}
```

This is the `canvasStyle.dimension` group; width/height are native pixels,
while visual placement is normalized. Copy matching native state. Changing
only width/height while retaining `type: "DEFAULT_16_9"` allowed the UI to
normalize the canvas back to its preset size. A report built on this Custom
1600x900 canvas with normalized placement rendered as designed across several
published revisions (user-confirmed), with `isAutoLayoutDisabled: true`.

## Constraints

- The public Intelligence contract locates canvas settings at
  `properties.properties.canvasStyle` inside its page wrapper; a native
  `sheet.json` wraps page settings under `properties`. Preserve the source
  part's actual shape. See [container contracts](../../core/definition-structure.md).
  Schema coverage does not verify custom-size behavior or upgrade this encoding.

- Canvas settings are available only in editing mode.
- Lock elements prevents resizing or moving existing elements; new elements
  can still be inserted and customised.
- Match the dimension type to the intended display medium (print, desktop,
  TV, tablet or mobile) before arranging elements.
- A custom theme's page settings can also set canvas and wallpaper
  backgrounds, grid lines and page dimensions; keep them consistent with the
  canvas settings.
- Plan visual rectangles in pixels, then divide x/width by canvas width and
  y/height by canvas height. Check margins, gutters, bounds and overlap after
  conversion; size the canvas and reflow all affected visuals together.
- Investigate bottom whitespace as both placement and viewport/aspect-ratio
  behavior. Verify persisted Custom dimensions and render at the target
  viewport/fit mode; do not stretch visuals just to fill space outside the board.
- Include filter controls, selected labels and expanded dropdowns in the
  rendered layout check, not just outer rectangle geometry.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: sheet.json /properties/canvasStyle (object)
Values seen: dimension.type CUSTOM | DEFAULT_16_9 | RESPONSIVE; isAutoLayoutDisabled
  true and false; background {isEnabled, type "color" | "image", color, value,
  imageUrl, fillMode "cover", opacity}; wallpaper {isEnabled, fillMode, opacity,
  value {type, color, imageUrl}}; border {isEnabled, color, side, width};
  cornerRadius {isEnabled, isCustomCornerRadius, radius per corner}; shadow
  {isEnabled, angle, blur, color, distance, opacity, placement, side, width};
  gridLineSettings {showGridLines, snapToGrid, gridLayoutType "auto", gridRows null,
  gridColumns null}; mobileCanvas {editModeDimension, runtimeDimension} each
  {width, height}; isLocked; scrollToZoom; showSmartGuide; showVisualGuide;
  verticalAlign "top"
Evidence: [saved] element-gallery and dashboard sheets
```

- [saved] `background` stores `color` and `value` side by side, while `wallpaper`
  nests its colour or image under `value`; keep each group's own shape.
- For a wallpaper-only color request, change
  `canvasStyle.wallpaper.value.color`, retaining its native color type,
  enabled state and opacity. A one-leaf change was published and visually
  confirmed to distinguish the area outside the board from its unchanged
  canvas [confirmed]. Leave `background.color`/`background.value`, dimensions
  and visuals untouched. Use contrasting session-approved surface colors;
  no particular gray is mandatory. Verify in a fitted view with visible
  outside margins, not only from the JSON.
- [saved] An image canvas background saved `type: "image"`, `fillMode: "cover"`,
  `isEnabled: true`, `opacity: 1` and an `imageUrl` holding an encoded workload
  resource locator (canvas-page-background resource path), not image bytes. Upload
  the asset in the target plan instead of copying the locator. [open] Retrieval,
  portability and appearance are untested; a raster background is not native
  element framing.
- [saved] A global theme's page defaults (`DEFAULT_16_9`) coexisted with an
  explicit taller custom sheet canvas; theme defaults did not replace the sheet's
  own `canvasStyle`.
- [saved] A hidden empty sheet exported no `canvasStyle`; preserve it as is and
  never use it as a canvas donor.
- [open] `isAutoLayoutDisabled` saved both `true` and `false`; its effect is not
  isolated. Preserve the observed value unless a native comparison requires a change.
- [open] The companion library saw sheets whose `dimension.elementScalingUnit` was
  `"pixel"`, with pixel-valued owner positions and sizes. This differs from the
  normalized-placement rule in this skill, which wins for authoring; read the unit
  of an existing sheet before interpreting its geometry and capture before writing
  pixel mode.
- [confirmed] A new visual placed below the last row at `position.y` > 1 (outside
  the canvas) was a user-reported defect. When no free in-bounds rectangle fits,
  shrink the new visual while its content stays usable, compact other visuals only
  with approval, or ask which sheet or area to use; never place beyond the canvas
  or silently extend it.
- Retained hidden visuals and background elements are not free slots. Check
  responsive and mobile copies for stale placements, and inspect the read-back page
  at 100% zoom with editor side panels open as well as in viewing mode.
- [open] When cloning a standalone native sheet, keep optional page keys absent
  where the source omits them; an empty `reactiveVisualProperties` added by an
  author was later removed in a repair, and its link to a blank-canvas report is
  unresolved.
- Keep placement defects separate from data or query errors: a geometry repair
  does not resolve a missing-query or other data message, and such errors do not
  widen the repair's scope. Besides the 100% zoom check, also inspect a narrower
  presentation viewport.

## Related features

- `CV-LAYER-01`
