---
id: SF-DATE-03
name: Relative date
area: slicers
category: Date filters
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/add-date-filters
---

# Relative date

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Last/next N days, weeks, months, quarters, years.

## When to use

- Operational monitors.

## UI path

Bind a date Category (not Date Hierarchy), then Filter ribbon › Quick Mode
› Relative Date. Configure the interval and calendar/fiscal type in settings
using the first-party date-filter guide.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.dateSettings
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Relative-date configuration is documented, but screenshots do not show the
  relative-date editor. Preset captions and historic selected dates do not
  prove a relative anchor.
- Verify current-date/time-zone and fiscal boundary behavior independently.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- A stored VALUES year or month selection is a fixed period; automatic rolling
  is not established [open]. Label it as fixed, or use a relative date or preset
  when the period must roll.

## Related features

- `SF-DATE-04`
