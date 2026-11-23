---
id: SF-DATE-01
name: Date slider
area: slicers
category: Date filters
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/date-filter-date-slider
---

# Date slider

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Range slider over dates with label, scale, fixed interval, max default date, and date format.

## When to use

- Analyst date ranges.

## UI path

Filter type › Date › Slider.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/superFilterAssignments/0/configuration/visualType = "DATE"
Pointer: /properties/visualState/dateSettings
Observed keys: dateViewType:"dateSlider", dateSliderType:"Between",
               showDateRangeSlider:true, calendarViewType:"monthRangeCalendar",
               fiscalStartMonth:0, fiscalYearMode, defaultDate:"max_date",
               heatMapEnable:true, sliderColor, dragHandleColor
Stored state: /properties/visualState/filterHiddenSettings/selectedDatePreset
Evidence: native date slider with presets, reused in a report build and read back;
  rendering in that report awaits confirmation.
```

Copy the full Fabric Plan date/filter-state groups, not only these observed
keys. Bind the date field via the registry and preserve the filter-state trio.
A visible date range/slider does not isolate fixed-interval or default-date
behavior. The native sample ships with `selectedDatePreset:
["date-last-1-CALENDER_YEARS"]` (Last Year) preselected; clear it to `[]`
unless that default is intended, or the page opens filtered to the previous
calendar year and conflicts with other period filters. With no stored range,
the slider follows the other filters on the page.

## Constraints

- Dual handles, date inputs and tick labels are presentation. Capture date
  locale, inclusive bounds, handle movement, date entry and clear behavior.
- An interval toggle and day count, shown on or off, are not verified
  fixed-interval settings; capture them before assuming activation.
- Test months of different lengths; do not equate a fixed-day window with a
  previous-calendar-month comparison.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Slider signature (partial): facetSettings.enableFacetMode:false;
  dateSettings {enableDateRange:true, dateViewType:"dateSlider",
  dateSliderType:"Between", showDateRangeSlider:true,
  defaultDateRangeSelection:"user_defined", enableSliderFixedInterval:false} [saved]
Binding: one lowercase "category" field with dataType "DateTime";
  registration configuration.visualType "DATE" [saved]
Evidence: complete saved date owners; this excerpt is not an insertion payload.
```

- `enableSliderFixedInterval` was false on every inspected owner; an enabled
  fixed interval is uncaptured [open].
- `showDateRangeSlider: true` in the date branch of a non-date owner is not an
  active slider [saved].
- Keep `dateSliderType: "Between"` capitalized; the measure filter saves
  lowercase `numericSliderType: "between"` [saved].

## Related features

- `SF-DATE-02`
