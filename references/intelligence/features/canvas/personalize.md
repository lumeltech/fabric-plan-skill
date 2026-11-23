---
id: CV-PERS-01
name: Personalise visuals
area: canvas
category: Modes
status: IS-Confirmed
encoding: unverified
visual: Sheet
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes
---

# Personalise visuals

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Readers personalise visuals without changing the published report. Within the
controls the author allows, readers can switch the visual type (chart, card,
table), browse chart types, re-assign measures and dimensions for ad-hoc
views, toggle elements such as title, KPI or axis, apply sorting and ranking,
customise or focus trellis panels and, in tables, reorder categories, resize
fields and rename headers.

## When to use

- Analyst readers.
- Readers who need another chart type or field assignment without edit access.
- Trellis views where readers focus on or customise a single panel.

## UI path

Personalise pane. In reading mode, turn on Settings › Personalize, select the
visual's Edit icon and change the visual type or its dimensions and measures.
Authors set per visual which reader controls (pivot data, chart types, tabs,
elements, sorting) are allowed.

## Definition encoding

```text
Path: planProperties.json → workloadModeConfig.READ.showPersonalizePane
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Readers change only what the author allows; unchecked elements or settings
  and hidden chart/card/table tabs stay fixed.
- Trellis panel customisation and focus panel are separate reader permissions.
- Re-assignment is limited to fields of the bound semantic model; it adds no
  sources, writeback or planning inputs.
- Personalised changes are session changes: Reset to Default restores the
  published view and clears them with session filters and notes.

## Related features

- `CV-MODE-01`
