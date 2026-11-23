---
id: MX-VARB-01
name: Variables
area: matrix
category: Calculations
status: Inforiver-only
encoding: unverified
visual: Matrix
sources:
  - https://docs.inforiver.com/working-with-inforiver/18.-variables
  - https://docs.inforiver.com/working-with-inforiver/18.-variables/variable-types
  - https://docs.inforiver.com/working-with-inforiver/18.-variables/variable-bookmarks
---

# Variables

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

User-adjustable values (number, select, text, date, date range, boolean, button) used in formulas and titles.

## When to use

- Thresholds, dynamic titles.

## UI path

Insert › Variables.

## Definition encoding

```text
Path: sheet.json → entityLevelVariables; planProperties.json → workloadLevelVariables (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- A card captioned "variable" with highlighted narrative values is not
  evidence of Matrix input variables, variable bookmarks or the storage paths
  above. Route card text to [card formatting](../kpi/card-customization.md);
  keep this feature Inforiver-only until matching Fabric Plan evidence is
  captured.
- Check whether Fabric Plan 'Parameters' is the same feature.

## Related features

- `MX-CALC-02`
