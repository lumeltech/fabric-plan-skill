---
id: MX-TPL-01
name: Grid templates
area: matrix
category: Templates and themes
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-financial-reports
---

# Grid templates

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Applies default or spreadsheet-style grid templates. Grid templates suit
typical tabular reports: Default grid, or Spreadsheet grid for a familiar
spreadsheet look. The same Templates gallery holds financial and IBCS
performance templates, which are separate features.

## When to use

- Quick professional starting look.
- Plain tabular or detail reports before custom formatting.
- Audiences used to spreadsheet-style grids.

## UI path

Home › Templates. In the gallery: Grid templates › Default grid or Spreadsheet
grid.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.themeColors.tableThemeType (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Templates can be switched at any time, but switching may discard
  customizations made under the current template; apply one before formatting.
- A template is only a starting point; formatting can be customized afterwards.
- Financial templates are `MX-TPL-02`; IBCS performance templates are
  `MX-TPL-04` and remain opt-in.

## Related features

- `MX-TPL-02`
