---
id: MX-TPL-03
name: Matrix themes and enterprise themes
area: matrix
category: Templates and themes
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
---

# Matrix themes and enterprise themes

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Sets gridlines, row highlight, toolbar and canvas themes; applies
organisation-wide themes. Toolbar and canvas switch between Light and Dark,
with custom text, header-text and background colours; Column Style formats
cells and text by column type for reading and editing views. Enterprise
themes save a report's display settings (visual, general, hierarchy, number,
header/footer, layout) as a named theme that others can preview and apply.

## When to use

- Match the report design system.
- Reuse a company theme.
- Use a dark toolbar or canvas to reduce eye strain.
- Set native (visual-level) measure columns apart from model columns.

## UI path

Display settings › General; Enterprise themes. Design tab: Display
(gridlines, outline, row highlight) and Theme (Toolbar, Canvas, Column Style)
options; Design › Enterprise themes › View themes (Preview › Apply theme) or
Add new theme.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.themeColors (themeType, tableThemeType, rowEvenColor, rowOddColor, rowHoverColor …), gridStyles
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Defaults: light toolbar and canvas, black font and alternate-row banding
  without fills or borders; gridlines are grey until recoloured in Display
  settings › General.
- Column Style also styles locked, data-input and forecast open/closed-period
  columns; those are Planning concepts and not authored in this release.
- Applying an enterprise theme replaces the report's display settings; Undo
  in the confirmation message restores the previous settings.
- A new theme stores a report screenshot as its preview (replaceable) and stays
  private unless Share publicly makes it available to everyone in the workspace.
- Only a theme's creator can update it (Preview › Update › Save, optionally
  renaming or changing access); Cancel resets the applied formatting.
- The themes panel searches by name, filters by All/Public/My themes, author
  or date range, and deletes themes individually.

## Related features

- `CV-THEME-01`
