---
id: CV-THEME-01
name: Dashboard, chart, and KPI themes
area: canvas
category: Canvas
status: IS-Confirmed
encoding: observed
visual: Sheet
sources:
  - https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/PlanProperties/1.0.0/schema.json
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/use-themes-for-consistent-color-schemes
---

# Dashboard, chart, and KPI themes

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Built-in and custom themes; import/export themes. A dashboard theme applies
one colour scheme across all elements, and an individual element can use its
own theme. Custom themes start from an existing theme: name it and change
chart, measure, font and background colours; saved custom themes apply to the
dashboard or to single elements.

## When to use

- Apply the design system palette across the report.
- Accessible palettes (colour-blind light or dark) for wide audiences.
- One element that needs a palette distinct from the rest of the sheet.

## UI path

Themes. Dashboard: Intelligence ribbon › Canvas › Themes. Element: the
chart's theme option, KPI ribbon › Settings › Theme, or a table's display
settings › Canvas › Theme; Customize there creates a custom theme from the
selected one.

## Definition encoding

```text
Path: planProperties.json → theme (type, appliedThemes) (capture sample for custom themes)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- The public Plan properties schema covers the shared theme container, not
  isolated custom chart/KPI theme settings. Preserve unrelated shared settings
  and other modules' styling; the source link does not upgrade encoding status.
- An element-level theme applies to that element only and takes precedence
  over the dashboard theme for it.
- In KPI cards, theme colours drive both the metrics and their charts.
- Auto font colour adjusts text for contrast and overrides a custom font
  colour; turn it off to set one.
- Theme import and export use JSON; keep exported themes with the design
  system so sheets stay consistent.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Part: planProperties.json
Pointer: /properties/theme {type, id, appliedThemes {"<key>": {type, id?, theme?}}}
Registration: appliedThemes["<key>"].theme (object) = {colors {defaultColors[],
  primaryColors[], extraChartColors {measures[], series[]}, semantic {positive,
  negative, neutral}, structuralColors {outline1, outline2, background, icon, accent,
  subtleFill}}, elements {background, border, cornerRadius, padding, shadow,
  header {backgroundColor, borderColor, iconColor}, tooltip {backgroundColor, color}},
  page {canvas {background, border, cornerRadius, shadow, dimension {dimensionType,
  width, height}, showGridLines, showVisualGuide}, wallpaper}, typography
  {fontFamily, fontSize, color, autoFontColor, responsiveFontSize}}
Evidence: [saved] global theme saves; [confirmed] one user-supplied custom preset
```

- [saved] A custom global theme saved active `type: 2` with a 16-character hex
  `id` and a matching applied entry `{type, id, theme}`. Other entries can be stubs
  such as `{type: 3}` or `{type: 5}` added by later saves, and two keys can hold
  identical registrations for one `id`; preserve the complete map, keep duplicates
  and check that they agree.
- [open] The meaning of `appliedThemes` keys and the UI label of each numeric
  `type` are not established.
- [saved] Before and after a user-identified Light choice, the theme changed from
  `{appliedThemes:{}, type:3}` to `{appliedThemes:{"1":{type:0}}, type:0}`; this is
  build-specific evidence, not an enum table.
- [confirmed] A user-supplied custom preset matched every supplied field of the
  saved registration. The native registration added background `value` fields and
  derived 20-entry `extraChartColors.measures` and `.series` arrays from a 40-entry
  `defaultColors`; the preset's `themeType` became native `type`, while preset
  `label` and `clonedFromThemeType` stayed outside the registration. Never paste a
  UI preset envelope into `planProperties.json`.
- [saved] After that global application, visited charts saved
  `appearance.charts.theme: "custom"`, `previousTheme: "custom"`,
  `isDefaultMeta.theme: true` and a derived `hiddenProperties_!!!_customTheme`
  JSON string whose schema differs from the preset. Other charts were unchanged in
  that save, so derived state does not prove every chart was normalized.
- [confirmed] The user presented that state as the correct global update, so
  it is propagated state, not an element-level theme choice: preserve it, do not
  strip it and do not paste a preset into `customTheme`.
- [saved] A cached `appearance.charts.theme: "ibcs"` stayed on visuals after a
  global Light change; a cached per-visual theme string does not establish the
  active global theme. Do not repair a global theme by writing strings into visuals.
- [saved] Explicit owner styling (such as container effects or axis fonts)
  coexisted with an unchanged global profile; global theme values are defaults,
  not proof of each owner's effective styling.
- Optional guidance: the companion library's users applied themes at report level
  only and avoided element-level theme selection. This is a preference, not a
  product limit; element-level themes described above remain available.

## Related features

- `MX-TPL-03`
