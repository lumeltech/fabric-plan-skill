---
id: SF-MEAS-01
name: Measure filter (range slider)
area: slicers
category: Numeric filters
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/measure-filter
---

# Measure filter (range slider)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Filters members by a measure range with step and labels.

## When to use

- Show customers with revenue above X.

## UI path

Filter type › Measure.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.measureFilterSettings (enableMeasureFilter, numericSliderStep …)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Numeric min/max inputs, a slider and an All selector are presentation.
  Capture the member field, comparison measure, aggregation, bounds and
  interaction scope; visible values are not reusable defaults.
- For range controls above hierarchy or treemap views, identify the qualifying
  grain (parent/leaf), displayed versus filtering measure and context.
- Test inclusive endpoints, scaled input parsing, blanks/negative values and
  range updates after other filters; do not copy captured bounds.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Partial: /properties/visualState/measureFilterSettings = {enableMeasureFilter:true,
  enableAlphaNumericFilter, alphaNumericRegex, showSlider:true, showPreset:false,
  numericSliderType:"between"} [saved]
Bucket: numeric measures bind to the lowercase "measure" bucket [saved]
Bounds: measureFilter / alphaNumericFilter bounds exist only on some owners [saved]
```

- Preserve bounds only when present; never copy a donor's business bounds.
- Measure filtering also appears on hierarchy map owners (SF-TREE-01) [saved].

## Related features

- `SF-NUM-01`
