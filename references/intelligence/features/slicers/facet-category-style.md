---
id: SF-FACET-02
name: Facet category style
area: slicers
category: Category filters
status: IS-Confirmed
encoding: verified
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/create-a-filter-panel
---

# Facet category style

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Fonts, colours, header, select-all, label icons, height for facet items.

## When to use

- Match the design system.

## UI path

Filter ribbon › Properties › Style › Category Styling (first-party filter-panel guide).

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/visualState/facetSettings/displaySelectAll = true
Pointer: /properties/visualState/displaySettings/displaySelectAll = true
Pointer: /properties/visualState/displaySettings/selectAllLabel = "Select All"
Tile styling (facetSettings): tileWidth, tileHeight, tileGap, tileRadius,
  isTileResponsive, tileBackgroundColor
Item text (categoryCustomizeSettings): commonFontSize, commonFontColor,
  commonTagBackgroundColor, commonHeader* keys
Selected and hover state (interactionStateSettings): selectedBackgroundColor,
  selectedTileFontColor, hoverBackgroundColor, hoverTextColor, selectedValueColor
Evidence: native tile facet; tileGap value from a UI save in the report editor.
  Runtime: a one-row tile control with isTileResponsive:true, tileHeight:28 and a
  ~104px frame on a 1600x900 canvas was user-confirmed; a 76px frame cropped the tiles.
```

Screenshots show toggle/select-all presentation only. Copy complete
facet/display groups; font/color/height controls are not isolated by these
pointers. Do not assume all category customization lives in a single generic
group.

## Constraints

- Size the frame for title plus controls: a one-row tile filter needs about
  104px at a 1600x900 canvas. Fixed-width tiles overflowed into a scrollbar;
  `isTileResponsive: true` fits tiles to the slot. Users may prefer a tight
  `tileGap` (1) for chip rows.
- Templates may carry `toolbarSettings.titleFontItalic: true`; set the title
  style explicitly.
- Checkbox colors, list sections, scrollbars, tile shapes and active-state
  fills are presentation. Capture selected-state, item, corner and font
  settings rather than inferring them from select-all pointers.
- Keep selection styling distinct from KPI status/warning colors. Use friendly
  field labels and preserve keyboard access and selection visibility.
- One panel can mix control styles and label/image tiles. Configure
  per-category styles separately from panel position; reserve room for
  selected chips, measure/variance columns, long labels and scrolling.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Saved single-select tile rows hid the facet header (`showFacetHeader: false`)
  while saved dropdown facets showed it [saved].
- Tile width, height, gap, radius and column counts in saved owners are
  source styles, not universal dimensions; reuse the session design instead.

## Related features

- `SF-DISP-01`
