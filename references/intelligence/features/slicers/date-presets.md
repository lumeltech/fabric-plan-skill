---
id: SF-DATE-04
name: Dynamic date presets
area: slicers
category: Date filters
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/add-date-filters
---

# Dynamic date presets

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Preset buttons such as YTD, MTD, QTD, last 12 months.

## When to use

- Executive sheets.

## UI path

Filter type › Date › Presets.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/superFilterAssignments/0/configuration/visualType = "DATE"
Pointer: /properties/visualState/presetSettings/enablePreset = true
Pointer: /properties/visualState/filterHiddenSettings/customPresets
Observed date keys: date-MTD, date-QTD, date-YTD,
                   date-last-1-CALENDER_YEARS, date-last-1-CALENDER_MONTHS,
                   date-last-1-QUARTERS
```

These are exact saved Fabric Plan preset keys (including `CALENDER`).
Copy the complete native preset/filter-state groups; do not derive enum names
from button captions or assume fixed dates. Preset buttons in screenshots show
presentation only; selection behavior remains unverified.

```text
Preselected preset: /properties/visualState/filterHiddenSettings/selectedDatePreset
  (native sample: ["date-last-1-CALENDER_YEARS"]; set [] for no default preset)
Hide one preset: customPresets[i].isHidden = true (key observed false by default)
Preset styling: presetSettings (presetSelectedBackgroundColor, presetSelectedTextColor,
  presetsFontSize, presetButtonColor, presetButtonBorderColor)
Fiscal settings exist in dateSettings (fiscalStartMonth, fiscalYearMode); their effect
  on YTD/QTD presets is not captured.
```

## Constraints

- Presets are relative to today and calendar-based unless fiscal settings are
  captured. A calendar "Last Year" preset beside a fiscal-year default
  intersects to no data; hide it or clear the preselection. With an April
  fiscal year, quarter presets cover the same months as fiscal quarters, but
  YTD is calendar YTD intersected with the selected fiscal year.
- A filled preset pill above a date-range input or slider does not prove the
  visible absolute range came from that preset. Define the period anchor and
  calendar; test boundaries, fiscal starts and cross-year ranges.
- Capture distinct fact/date roles. Detail or history views outside the preset
  range may be intentional but must be explicit; a selected preset does not
  prove propagation to every fact table or detail page.
- Presets restrict visible dates; rolling, MoM, QoQ and PY measures may need
  earlier periods. Confirm those measures still compute at the range start.

## Related features

- `SF-DATE-02`
