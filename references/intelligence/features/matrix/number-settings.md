---
id: MX-NUM-02
name: Number display settings
area: matrix
category: Number formatting
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-financial-reports
---

# Number display settings

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Formats signed numbers, including parenthesized negatives and separators.
Additional legacy number-display options are not all confirmed in Intelligence.

## When to use

- Financial statement tables with accounting-style negative values.

## UI path

Format ribbon > Appearance > Numbers > Semantic Formatting for positive/
negative colors and formats. Matrix > Prefix/Suffix for selected rows/cells.
Other number-display controls require an Intelligence UI capture.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.numberFormatting (customNullText, customZeroText, decimalSeperator, negativeValueFormat …)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Grouping separators and parentheses do not determine arithmetic sign, and
  blank cells do not prove zero suppression. Preserve numeric measures and
  confirm currency/locale and row-specific format scope.
- Fabric Plan replaces the legacy reference for signed presentation.
  [Legacy number settings](https://docs.inforiver.com/display-settings/number-settings)
  remains only for uncovered Indian numbering, error suppression, custom
  blank labels and null/zero replacement controls. These subfeatures are not
  established by the first-party guide; capture before use.
  Do not suppress errors or replace missing financial values to force totals.
- IS-Confirmed applies to the documented signed-display capability, not all
  legacy options. The prior observed settings group does not isolate a
  reporting Matrix switch; screenshot evidence does not upgrade encoding.

## Related features

- `MX-NUM-01`
