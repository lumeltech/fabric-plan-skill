---
id: CV-MARK-01
name: Marker Mode drawings
area: canvas
category: Storytelling
status: IS-Confirmed
encoding: observed
visual: Sheet
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes
---

# Marker Mode drawings

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Marker Mode lets a presenter draw on a sheet to highlight areas of interest:
freehand pencil strokes, text-area labels, rectangles and triangles, each with
a colour, line pattern, stroke size and text size. [saved] Drawings are stored on
the sheet, not on a visual, data point or note. Merged from the companion
Intelligence authoring library; tags follow
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

## When to use

- Live walkthroughs that circle, underline or label an area of a dashboard.
- Preserving markup that already exists on a sheet during unrelated edits.

## UI path

Intelligence ribbon › Notes › Marker Mode. Reset to Default clears session
changes, including drawn marker annotations.

## Definition encoding

```text
Part: sheets/{sheetId}/sheet.json
Pointer: /properties/commentary/notes (object)
Keys: enableMarkerMode (bool); markerData[] records {style, color, pattern, size,
  data[], text (text-area only)}; settings.marker {color, pattern, size, style,
  textSize} = current drawing-tool default
style values seen: "pencil" (variable-length data), "text-area", "rectangle",
  "triangle" (four-number data); pattern "solid" | "dashed"
Evidence: [saved] a marker sheet in a saved export; drawing, persistence and
  reading-mode behaviour not tested
```

Copy complete record families from a same-build export and prefer drawing in
the product over synthesizing coordinates. Run `core/native-samples.md` before
writing markers into a definition.

## Constraints

- [saved] Changing `settings.marker` does not rewrite existing records; each
  record keeps its own colour and size.
- [saved] A chart on the marker sheet kept an empty
  `hiddenProperties_!!!_annotateMarker` (JSON string) while the sheet held the
  drawings; inspect sheet commentary, not only the visuals.
- [open] Four-number `data` arrays are consistent with placement and extent, but
  their order and units are unconfirmed. Do not label them x/y/width/height or
  scale them with visual-placement rules.
- [open] Coordinates are sheet-space, not data-bound: sorting, filtering, resizing
  or moving a chart may leave a marker pointing at the wrong place. Markers from a
  responsive or differently sized canvas are not drop-in donors.
- [open] The documentation calls drawn markers session changes that Reset to
  Default clears, yet `markerData` persisted in a saved export; when drawings
  persist (editing or reading mode, save) is unresolved.
- [saved] A marker rectangle is not a `BI_SHAPE`, a text-area is not Lexical
  `BI_TEXT`, and a marker beside a data point is not a data-bound note. No circle
  or arrow marker style is established.
- [saved] A bookmark targeted the marker sheet; that does not prove the bookmark
  captures or restores the drawings.
- Choose colour, pattern and size for contrast without covering values or
  controls. Preserve sibling notes, annotation settings and every other record;
  never clear a user's markup without explicit authorization.
- Verify record count, types, text, colours and bounds after saving; test resize,
  zoom, hide/show, edit/clear and reading mode separately.

## Related features

- `CV-ANN-01` — the same sheet `commentary` object holds annotation settings.
- `CV-MODE-01` — Reset to Default clears session markup.
