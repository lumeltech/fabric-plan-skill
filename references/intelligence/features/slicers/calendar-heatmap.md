---
id: SF-DATE-06
name: Calendar heatmap
area: slicers
category: Date filters
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/add-date-filters
---

# Calendar heatmap

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Colours calendar days or months by a measure (including annual heatmap).

## When to use

- Daily patterns.
- Monthly activity grid for one year with year navigation.

## UI path

Date › Heatmap.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.dateSettings.contextualHeatMap
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- A month grid with year arrows, a clear icon, cell values and empty months is
  presentation only. Capture the measure binding, color scale and selection
  behavior before reuse.
- Bind color to a measure that varies by period, such as monthly activity; a
  cumulative YTD measure only increases and cannot show higher/lower activity.
  Make the labeled value and color measure consistent or caption both.
- Day, week, month and multi-year heatmaps may add selection summaries and
  month-total bars. Capture value versus selection color precedence.
- Boundary weeks can occur in adjacent month rows; verify aggregation rather
  than adding repeated labels. Hidden weekdays and blank cells are not proof
  of zero activity.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Partial: {"dateSettings":{"enableDateRange":true,"dateViewType":"dateCalendar",
  "calendarViewType":"monthCalendar","heatMapEnable":true,"contextualHeatMap":true}} [saved]
Measure: contextual heatmaps bind one numeric measure (lowercase "measure" bucket) [saved]
```

- `heatMapEnable: true` also occurs without `contextualHeatMap` [saved]; alone
  it does not show a measure-colored heatmap [open].
- The UI switch behind `contextualHeatMap` is not isolated; a one-setting
  capture was deferred [open].
- Calendars with date variance saved `heatMapEnable: false` (SF-DATE-05) [saved].

## Related features

- `SF-DATE-05`
