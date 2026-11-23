---
id: CV-ELEM-01
name: Text boxes, shapes, and images
area: canvas
category: Elements
status: IS-Confirmed
encoding: observed
visual: Canvas
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-a-dashboard
---

# Text boxes, shapes, and images

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Adds titles, text, shapes, and images to the canvas.

## When to use

- Sheet titles, section labels, logos, background panels.

## UI path

Elements pane.

## Definition encoding

```text
Text: /properties/visualType = 202; registration: BI_TEXT;
      /properties/visualState/text (JSON string: Lexical editor state)
      {"root":{"type":"root","children":[{"type":"paragraph","format":"left",
        "children":[{"type":"text","text":"…","format":<1 bold | 2 italic>,
                     "style":"font-size: 13px;line-height: 1.5;color: #…;"}],
        "textFormat":…,"textStyle":"…"}],…}}
      Transparent box: visualStyles.background {backgroundColor:"#ffffff00", isEnabled:true}
Shape: /properties/visualType = 201; registration: BI_SHAPE (earlier saved element);
       visualState.shapeState.fill {fillColor, isEnabled}, cornerRadius, border
Image: registration BI_IMAGE; visualState.imageState {src, scale:"fit", tooltip,
       action {actionType:"NONE", pageDestinationId, bookmarkId, webUrl, isEnabled}}
       src = base64 of the item-scoped upload path
             workloads/<planId>/entities/<n>/image-element/<uploadId>__<file name>
Evidence: live export of a UI-created test Plan (default state); Lexical titles, notes
          and shapes rendered as authored in a published report (user-confirmed);
          image state from user-finalized saved reports [saved].
```

Copy a matching whole Fabric Plan text/shape element with normalized placement.
Typical text elements include question-led headers, refresh text and section
captions; visible logos do not establish image upload/URL encoding.
Do not treat a leftover `chartType:"COLUMN_VERTICAL"` on an element as its
visual identity.

## Constraints

- Text boxes must not show scrollbars [confirmed]. User-finalized reports
  stored `visualStyles.padding` disabled or with all sides 0, a 0 corner
  radius on large page titles, and heights of about twice the font size per
  line [saved]. If a scrollbar remains, add a few pixels of height (for
  example 22 → 25 px) rather than shrinking the font [confirmed]; check in
  Reading mode. With `line-height: 1.35` and padding off, a box needs about
  font × 1.35 + 9 px per line: 13 px text in 24 px and 17 px text in 28 px
  showed scrollbars, 26 px text in 44 px did not.
- Uploaded images belong to their Plan item. A definition copied into a new
  Plan kept the source item's upload path, and the logo and icon did not
  display until the user re-uploaded them on every page [saved][confirmed].
  After copying, re-upload approved assets in the new item or tell the user
  before delivery; never call a copy identical until its images render.
- For [legacy-report branding inspiration](../../design/report-inspiration.md#branding-and-logo-treatment),
  reuse placement and hierarchy, not screenshot logo crops, business names,
  contacts or old findings. Use approved logo assets and preserve their aspect
  ratio and light/dark treatment; capture image encoding before authoring.
- Capture static versus measure-bound text for every narrative or insights
  panel. A narrative does not prove AI generation or filter-aware text;
  regenerate claims for current filters or state the fixed scope and date.
- Narrative periods, values, shares and leaders must match the visuals beside
  them; revalidate claims against current data rather than copying them.
- Rankings or contribution analysis do not prove causes such as pricing,
  demand, equipment, materials or individual performance; mark unsupported
  explanations as hypotheses and avoid unsupported clinical conclusions.
- Bind verified units and context in labels. "Best" claims need an explicit
  scoring rule; the largest histogram bin is not necessarily a majority.
- Refresh or "last checked" text does not verify data freshness or a live
  Today reference; a standards label (such as IBCS) does not prove
  compliance or a native template.
- Capture static text, dynamic binding and image/icon ownership separately;
  descriptive panels and pictograms do not establish tooltips, interactive
  Info controls or native card chart content.
- Keep explanatory rails optional and distinguish status commentary from
  operational approval. A product logo (such as Planning) does not change
  module scope.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Text (`BI_TEXT`/202)

```text
Pointer: /properties/visualState/text (JSON string: Lexical tree); sibling reportMode
Node types: root, paragraph, text, linebreak, heading (tag h1 | h2 | h3), quote,
  list (listType "bullet" + tag "ul" | listType "number" + tag "ol", start), listitem (value)
Common node keys: version 1, direction null, indent 0; leaf detail 0, mode "normal"
Style owners: root/block textStyle (default CSS), leaf style (inline CSS), leaf
  numeric format (bit flags), block format (alignment string), block textFormat
Evidence: [saved] titles plus heading/list/quote specimens in saved exports
```

- [saved] `reportMode` is saved beside `text`; retain it unless the task changes it.
- [saved] Empty CSS declarations (such as `color: ;font-size: ;`) occur natively;
  preserve them on unrelated edits instead of normalizing the tree.
- [saved] Leaf `format` holds bit flags; preserve combined values rather than
  deriving an enum from bold and italic. Block `format: "left"` is a different field.
- Keep hierarchy, list order/value/tag, alignment and direction; never flatten
  structured text into one string or HTML.
- For text-box scrollbars, inspect outer `visualStyles.padding` first. In a
  confirmed fix, padding was already disabled; stored side values were zeroed
  and only then were heights increased minimally. Check Reading-mode fit at
  the intended zoom and keep the footer within the canvas. Do not hide
  overflow, clear content or shrink all typography to conceal the scrollbar.
- To add a line, decode the tree once, deep-copy a compatible `paragraph` donor
  (not a heading or list item) with the intended normal format, replace its leaf
  text, append it and re-serialize with a JSON encoder. Never string-replace inside
  the serialized report. Recheck height and wrapping after appending; a successful
  save does not prove the new line is visible.
- [saved] Text systems differ: chart notes store HTML, table notes `unformattedText`
  HTML, sheet markers plain `text-area` text, shape labels `shapeState.text` and KPI
  cards mention tokens. Do not swap representations because all of them show words.
- [open] Fonts used in saved specimens may be missing on viewer devices; compare
  rendering and fallback before relying on a font family.

### Shape (`BI_SHAPE`/201)

```text
Owner: shapeType "RECTANGLE", copied at visualState.shapeType and
  visualState.shapeState.initialShapeType {isEnabled, type}
visualState.shapeState (object, not a JSON string): fill {isEnabled, fillColor};
  border {isEnabled, color, side "all", style "solid", width}; cornerRadius; padding;
  rotation {isEnabled, type "all", all, shape, text}; shadow; glow {isEnabled, blur,
  color, opacity}; accentBar {isEnabled, value {color, side, width}}; text {isEnabled,
  value, fontColor, fontFamily, fontSize, horizontalAlign, verticalAlign, isBold,
  isItalic, isUnderline, padding, textRotation}; icon; tooltip {isEnabled, content};
  action {isEnabled, actionType "NONE", bookmarkId, pageDestinationId, webUrl}
Dormant per-type groups in rectangle defaults: arrow, chevronArrow, hexagon, line,
  octagon, parallelogram, snip, speechBubble, trapezoid, triangle
Evidence: [saved] rectangles in saved exports; only RECTANGLE was exercised
```

- [saved] Drawing and container styling are separate owners. A rectangle with a
  transparent outer `visualStyles.background` and disabled outer border still drew
  its enabled `shapeState` fill and border. Two rectangles with identical outer
  radii differed only in `shapeState.cornerRadius` (0 versus 6); outer radius alone
  need not round the drawing.
- A background rectangle can have two active padding layers:
  `/properties/visualStyles/padding` and
  `/properties/visualState/shapeState/padding`. Both use `isEnabled` and
  `leftPadding`, `rightPadding`, `topPadding`, `bottomPadding`. Disabling both
  and zeroing the four side values made fill/border occupy the existing
  rectangle bounds [confirmed].
- These insets can place a background border underneath foreground charts,
  producing stepped seams that resemble incorrect layer order. Audit both
  padding owners before moving charts or changing z-order. After correction,
  verify foreground rectangles remain inside the visible border with the
  approved content inset; do not remove intentional dashboard gutters.
- [saved] `isEnabled: true` on a dormant per-type group does not make that type
  active; request an active donor before promising another shape type, an action or
  an effect. Keep every `shapeType` copy consistent.
- [saved] The `line` group is dormant in rectangle defaults; use a matched donor for
  a thin divider instead of guessing line properties.
- [saved] Shape text was disabled in captured headers; a separate Text element
  layered over the filled rectangle carried the title.
- [open] Rendered-page observations: rotation happens inside the element box, so a
  rotated rectangle can lose its corners (use a larger square box); the drawing
  stretches to its box (keep width equal to height for circles); a new rectangle
  showed a thin grey border nobody set (set borders explicitly); shape text keeps its
  colour after fill changes; shapes are keyboard-focusable.
- [open] Whether shape colours follow the theme, minimum shape size, data-driven
  fills and removing decorative shapes from the tab order.
- Do not add a full-page background shape when the canvas background already gives
  the colour.

### Image (`BI_IMAGE`/207)

```text
Registration: BI_IMAGE; /properties/visualType = 207
Pointer: /properties/visualState/imageState (object, not a JSON string)
Keys: src, scale "fit", tooltip "", action {isEnabled false, actionType "NONE",
  bookmarkId null, pageDestinationId null, webUrl null}
Evidence: [saved] uploaded images in saved exports; load, fit and portability not tested
```

- [saved] `src` is a base64-encoded workload resource locator whose decoded form is a
  workload/entity/image-element path. It is not image bytes, a data URI or a public
  URL, and the definition carries no image binary.
- Upload the authorized asset through the product, then capture the resulting `src`.
  For another plan, upload or remap the asset; copying `src` is not asset migration.
  Verify load after reopen, fit or cropping and tooltip.
- [saved] Dormant `action` fields do not establish image buttons; capture an active
  donor first. [open] Image actions, tooltip overlays and SVG, URL or model-column
  image sources are reported product capabilities with no saved evidence here.
- Use an image for a logo or illustration; never rasterize a dashboard instead of
  building its visuals.
- [saved] Every inspected text, shape and image owner also exported a
  `writeback.json` companion; preserve it, but it does not imply writeback.

## Related features

- `CV-LAYER-01`
