---
id: SF-NUM-01
name: Numeric and alphanumeric filters
area: slicers
category: Numeric filters
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
---

# Numeric and alphanumeric filters

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Range filter on numeric columns; pattern filter on codes.

## When to use

- Age bands; account code ranges.

## UI path

Filter type › Numeric / Alphanumeric.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.measureFilterSettings (enableNumericCategorySlider, enableAlphaNumericFilter, alphaNumericRegex)
Numeric type: /properties/superFilterAssignments/0/configuration/visualType = "NUMERIC"
  with configuration keys alphaNumericValues {equalValue, maxValue, minValue},
  enableNumericToFacet:false, regex:"", scale:"none", slider:false
  (UI saves on an integer year field rendered as tiles, facetViewType "tile",
  with a stored VALUES selection of numeric ids)
Evidence: decoded native readbacks; the range-slider form (slider:true) is not captured.
```

Copy the whole group from a working visual or run `core/native-samples.md`
before writing range or alphanumeric settings.

## Constraints

- Range endpoints beside a table of mixed codes do not prove which field is
  filtered. Capture the actual bound field, range ordering and downstream
  interaction.
- Do not convert identifiers to numbers, drop prefixes/leading zeros or infer
  regex semantics from the slider. Test lexical versus numeric/extracted-key
  ranges, inclusive endpoints, blanks and nonmatching values.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Int64 year field (user-corrected control): owner and registration bind lowercase
  "category" with dataRoleType "Grouping", Int64 type and formatString "0";
  registration configuration.visualType "NUMERIC", singleSelect:false [saved]
Typed numeric selection (page-level entry, CV-FILT-01): columnDataType ["Int64"],
  dataType ["number"], valuesFilter [{id:[<number>], label:[<number>]}] unquoted [saved]
Alphanumeric (partial): measureFilterSettings {enableAlphaNumericFilter:true,
  alphaNumericRegex:"<pattern>", showSlider, showPreset, numericSliderType:"between"} [saved]
```

- `NUMERIC` on a registration does not imply a range control or measure
  semantics [saved].
- `enableNumericCategorySlider` is saved on many owners; alone it does not
  establish a numeric control [saved].
- Measure filtering (`enableMeasureFilter`) and alphanumeric filtering
  (`enableAlphaNumericFilter`) are independent switches in the same
  `measureFilterSettings` group, and some owners enabled both [saved]. Classify
  each capability from its own flag and bindings.

## Related features

- `SF-MEAS-01`
