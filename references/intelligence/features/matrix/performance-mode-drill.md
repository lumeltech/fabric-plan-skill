---
id: MX-LAY-03
name: Performance mode drill down and roll up
area: matrix
category: Layout and hierarchies
status: Inforiver-only
encoding: unverified
visual: Matrix
sources:
  - https://docs.inforiver.com/advanced-topics/drill-down-and-roll-up-in-performance-mode
  - https://docs.inforiver.com/performance-optimization-options-in-inforiver
---

# Performance mode drill down and roll up

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Loads one hierarchy level at a time and drills down or rolls up on demand for large data.

## When to use

- Large hierarchies near the cell limit.
- Analyst sheets with deep drill paths.

## UI path

Home › Layout › Performance mode.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.layout (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- About 1.2 million cells is the practical grid budget.

## Related features

- `MX-LAY-01`
