---
id: SF-DATE-07
name: Date filter settings (week, fiscal, default, holidays)
area: slicers
category: Date filters
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/add-date-filters
---

# Date filter settings (week, fiscal, default, holidays)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Week mode, default selection, start date and start day, single select, days off, fiscal months, measure values, today navigation, holidays, invalid dates, month total bar.

## When to use

- Fiscal calendars; bounded default period.

## UI path

Date › Format pane settings.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.dateSettings (defaultDate, defaultDateRangeSelection, daysOff, dateSingleSelectType …)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Weekday-only columns, week numbers and month-total bars are presentation,
  not proof of their settings. Define first day, week-year/month allocation,
  locale and missing-day policy.
- First-party docs describe fiscal relative-date configuration. Screenshots do
  not establish default-date rules, holiday setup or other format switches.
  Availability is user-confirmed; capture those settings before use.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Date sliders saved `defaultDateRangeSelection: "user_defined"` [saved]; other
  values and their effect are uncaptured [open].
- Fiscal and day-number enum values in `dateSettings` have unresolved meanings;
  do not infer them from labels [open].

## Related features

- `SF-DATE-02`
