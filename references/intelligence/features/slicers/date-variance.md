---
id: SF-DATE-05
name: Variance in the date filter
area: slicers
category: Date filters
status: IS-Confirmed
encoding: unverified
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/add-date-filters
---

# Variance in the date filter

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Shows measure variance between periods inside the calendar.

## When to use

- Spot good/bad months while selecting.

## UI path

Date › Variance.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.dateSettings (capture sample)
Presentation evidence: screenshots only.
Visible: calendar values, comparison rows, variance fills and direction icons.
Exact comparison measures, period alignment and settings: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Comparison rows and direction icons do not reveal their bindings. Identify
  actual/comparison measures, absolute versus percent/pp deltas, time
  alignment and favorable direction; a fiscal label does not prove PY.
- Keep selection highlighting distinct from variance/heatmap colors. A selected
  cell's appearance must not conceal its value or adverse status.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Partial: {"dateSettings":{"enableDateRange":true,"dateViewType":"dateCalendar",
  "enableDateVariance":true,"heatMapEnable":false}} [saved]
Bindings: two measures on the owner [saved]
```

- Which bound measure is actual versus comparison, and the variance math, are
  unresolved [open].
- `varianceSettings` (with `enableVarianceMeasure`) is a separate group
  (SF-FEAT-06) [saved].

## Related features

- `SF-DATE-06`
