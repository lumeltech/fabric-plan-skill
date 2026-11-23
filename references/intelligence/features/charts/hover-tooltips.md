---
id: CH-TIP-01
name: Hover tooltips and contextual drill menu
area: charts
category: Chart interactions
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes
---

# Hover tooltips and contextual drill menu

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Shows category/measure context on hover; a configured report may also expose
a drill-through menu. Tooltip appearance is not destination wiring.

## When to use

- Compact charts that need exact values without persistent labels.
- Hover context (period, measure and value) with a Drill Through entry where
  detail navigation is configured.

## UI path

Chart tooltip controls; exact Fabric Plan click sequence was not captured.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/visualState/hiddenProperties_!!!_commonSettings (JSON string)
Decoded keys: varianceInTooltip:true, varianceTooltipType:"both",
              enableSharedTooltip:false, showAdvancedTooltip:false
Drill destination: planProperties.json
Pointer: /properties/drillThroughConfig
```

Copy matching whole settings; individual hover/menu activation is not
isolated. Empty `reportPageTooltipEntities` in this sample is not evidence
of a configured report-page tooltip. Capture before adding new tooltip wiring.

## Constraints

- Check tooltip measures against the live registry.
- Validate context and destination filters independently of screenshots.
- A displayed tooltip confirms content only, not hover activation, selection,
  a drill menu/destination or shared-tooltip configuration. Capture bindings;
  verify formatting and units.
- Validate that the tooltip swatch, series identity and context match the
  hovered element and the legend color mapping.
- Captions that promise tooltip content are capture requirements, not
  verified content or proof of configured interactions.
- Tooltips on card mini-charts may be card-owned; verify ownership before
  using chart settings, and align fiscal/period context.
- Keep tooltip content at the authorized aggregate level, without personal or
  protected identifiers.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Line owners bind tooltip fields in a `Tooltip` bucket (capitalized)
  [saved]. A saved tooltip binding does not prove its rendered text resolves
  [open].
- Inspect tooltip number formatting separately from axes, labels and KPI
  values when checking scaling and suffix (`CH-DISP-01`) [confirmed].
- A Drill Through entry depends on the destination's registered drill-through
  fields; slicer or axis fields and incoming context are no substitute, so
  test each source/destination pair (`CV-INT-03`) [confirmed].
- Test hover and click with the real layers and containers; static z-order
  alone does not prove that a chart is reachable.

## Related features

- `CV-INT-03` — destination/filter configuration.
- `CH-LBL-01` — persistent labels instead of hover.
