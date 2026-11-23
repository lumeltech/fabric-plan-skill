---
id: SF-FEAT-06
name: Conditional formatting, sort, rank, variance in slicers
area: slicers
category: Features
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
---

# Conditional formatting, sort, rank, variance in slicers

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Colours, sorts, ranks, and shows variance or measure values next to slicer members.

## When to use

- Slicers that also inform (e.g. sales per region).

## UI path

Features tab.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.rankSettings, displaySettings (measureTooltip, varianceTooltip) (capture sample)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Measure/delta values, direction icons, rule fills, continuous tile colors
  and ranked children with Others can appear across categorical styles.
  Capture CF and selected-state precedence rather than conflating them.
- Define comparison/CF/ranking measures independently, including units,
  favorability, denominator and current context.
- Top N needs explicit global versus per-parent scope, ties, total/filtered
  count semantics and Others aggregation/selection behavior; a caption does
  not establish active rules.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
CF group: /properties/visualState/cfSettings (object; rule list in cfSettings.rules) [saved]
  Rules (partial): {cfFormatBy:"rules", cfRuleFor:"valueOnly", cfApplyTo:"allMeasures",
    isEnabled:true, isIconEnabled:false, logicalOperator:"or"}; numeric conditions
    isGreaterThan / isLessThan [saved]
  Scale (partial): {cfFormatBy:"colorScheme", cfColorScaleType:"continuous",
    cfImpactsOn:"bgColor", classificationType:"percentage", isEnabled:true,
    isAutoFontColor:true, isReverseColor:false} with category/measure references [saved]
Variance: /properties/visualState/varianceSettings/enableVarianceMeasure [saved]
Registration Top N: superFilterAssignments[].configuration.topN = {displayOthers,
  otherLabel, rankMeasure, rankMeasureLabel, rankMode:"TOP", rankType:"value",
  rankValue} [saved]
Registration sort item: {columnId, columnName, direction:"ASC" | "DESC", id} [saved]
```

- Super Filter `cfSettings` is not the Matrix `cfProps`/`jet_cfProps` encoding;
  never import one as the other [saved]. The fragments omit identity, condition
  and format fields; adapt a complete owner.
- Many owners save `enableVarianceMeasure: true` with only the first measure
  reference populated [saved]; resolve both references and a common context
  before relying on a comparison.
- `rankSettings` is enabled on a minority of owners and absent on some [saved].
  Rank dimension/measure resolution, CF precedence and whether registration
  `topN` acts on a control are unresolved [open].

## Related features

- `SF-FACET-01`
