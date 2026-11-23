---
id: SF-DATE-02
name: Calendar modes (year, month range, month, week, day)
area: slicers
category: Date filters
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/add-date-filters
---

# Calendar modes (year, month range, month, week, day)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Calendar pickers for year/multi-year, month range (single, multiple, predefined, fiscal presets), month, month only, week, day.

## When to use

- Executive month or quarter selection.

## UI path

Add Super Filter, bind a date Category (not Date Hierarchy), then Filter ribbon
› Quick Mode › Date Picker. Properties › Calendar Customization › Calendar
View selects the view, as described in the first-party date-filter guide.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.dateSettings (calendarViewType, calendarDateRangeType …)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- A collapsed date-range control with a clear icon shows only its visible
  range, which does not establish the calendar enum. Capture the expanded
  picker and apply behavior.
- Specify inclusive dates, timezone, partial days and any separate fixed-day
  comparison window rather than silently making it an equal-length prior range.
- Month, year, multi-year, week and paired range calendars are distinct views.
  Disjoint selected days/months differ from a contiguous range; capture the
  required mode and state.
- Define week-year convention, boundary-week allocation and hidden weekdays.
  Similar selections across visuals or sheets do not establish synchronization.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Calendar picker: /properties/visualState/dateSettings/dateViewType = "dateCalendar" [saved]
calendarViewType in saved date owners: "monthCalendar", "yearCalendar",
  "multiYearCalendar", "weekCalendar", "monthRangeCalendar" [saved]
Partial: {"dateSettings":{"enableDateRange":true,"dateViewType":"dateCalendar",
  "calendarViewType":"monthCalendar"}} [saved]
False on every inspected owner: periodSingleSelect, multiDateRangeEnable [saved]
```

- Enabled single-period or multiple-range calendars are uncaptured [open].
- `calendarDateRangeType: "user-defined"` and `defaultDateRangeSelection:
  "user_defined"` coexist in different keys; never normalize one spelling to
  the other [saved].
- Fiscal and day-number enum meanings in `dateSettings` are unresolved [open].
- A calendar needs a DateTime field and a DATE registration; a `dateSettings`
  branch on a String-bound owner is dormant [saved].

## Related features

- `SF-DATE-04`
- `SF-DATE-07`
