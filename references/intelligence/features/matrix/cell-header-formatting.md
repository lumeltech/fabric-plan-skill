---
id: MX-FMT-01
name: Cell, header, and value formatting
area: matrix
category: Formatting
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-financial-reports
---

# Cell, header, and value formatting

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Font, size, style, colours, borders, alignment, header orientation, indent, row size, word wrap, format painter.

## When to use

- Apply the design system typography.
- Emphasise subtotal rows.

## UI path

Format ribbon: Bold, font controls, and Border > Custom for color, thickness
and position (first-party financial-report guide).

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.globalStyles (fontFamily, fontSize, headerFontSize, rowHeight, headerHeight, textColor), row_height_config
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Coloured section/total rules, indented labels, right-aligned amounts and
  bold latest-period values in a screenshot prove appearance only, not
  conditional-format rules, frozen columns or a required palette.
- Capture row/cell/header scope; preserve readable long labels, accounting
  symbols and parentheses.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/globalStyles (object, partial)
Fragment: {"fontSize": "<n>", "headerFontSize": "<n>px", "rowHeight": <n>}
Evidence: saved reporting Matrix owner [saved]
```

- `globalStyles` and `gridStyles` are ordinary objects under `visualState`,
  not chart `hiddenProperties_!!!_*` JSON strings [saved].
- Value types are mixed: `fontSize` saved as a unitless numeric string,
  `headerFontSize` as a px string and `rowHeight` as a number, with
  `fontFamily` holding a Segoe UI fallback stack [saved]. Preserve each
  type; never normalize every size to a number.
- The effective rendered typography of these values is not confirmed [open].
- Do not read style state as evidence that editing, writeback, aggregation
  or security was exercised.
- Matrix differences between consecutive saves can be context or cache
  churn rather than new styling [saved]; learn styling only from isolated
  changes.

## Related features

- `MX-TPL-03`
