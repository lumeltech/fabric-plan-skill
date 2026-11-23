---
id: MX-FMT-04
name: General display settings
area: matrix
category: Formatting
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
---

# General display settings

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Toolbar, canvas theme, background, header text, outline, row hover, gridlines,
table padding, custom date format, localization. Toolbar and canvas switch
Light/Dark; text, header-text, background and outline colours are custom.
Row highlight offers hover, alternate, alternate contrast or flashy bands, or
off; gridlines cover major parent-row, minor horizontal, header and vertical
lines. Canvas rendering speeds up very large grids.

## When to use

- Fine-tune the grid look.
- Match the report palette or use a dark canvas.
- Speed up scrolling in grids with many row and column categories.
- Show translated labels to a multilingual audience.

## UI path

Display settings › General (Home › Settings › Display settings opens the
Display side panel). Gridlines, outline, row highlight and toolbar/canvas
themes are also on the Design tab.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.gridStyles, themeColors, locale
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Row alternate is the default highlight; Off removes banding and Measure Only
  Highlight bands the measures but not the row categories.
- Major gridlines (parent rows) default to Off; Single or Double take a custom
  colour. Vertical lines are Solid or Off.
- Minor horizontal lines are Solid, Dashed or Off with Skip lines 1–10; the
  header gridline shares their colour, and recolouring it recolours them.
- Table padding (top, bottom, left, right) accepts 0–100 and carries into PDF
  exports.
- Custom date format sets separate year, quarter, month and day formats for
  date dimensions on rows or columns (plain date fields, flat or model date
  hierarchies).
- Canvas rendering disables Freeze Total in the single-page view.
- Localization: add translation keys under Localization Settings, then use
  GETLOCALELABEL in calculated row/column or column-group titles (confirm it
  in the Matrix editor); labels switch when the report language changes.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/gridStyles (object, partial)
Fragment: {"gridBorderLinePosition": null, "gridBorderLineWidth": 0}
Evidence: saved reporting Matrix owner [saved]
```

- `gridBorderLinePosition` saved as `null` beside a numeric
  `gridBorderLineWidth` [saved]. A null position identifies no UI enum, and
  zero width alone does not prove that every grid line is hidden [open].
- The border-position control and its null-state behaviour are unmapped;
  capture one border change before writing these keys [open].

## Related features

- `MX-TPL-03`
