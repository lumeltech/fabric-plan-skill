---
id: SF-FEAT-01
name: Saved filters
area: slicers
category: Features
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
---

# Saved filters

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Users save and reapply filter selections.

## When to use

- Recurring selections.

## UI path

Toolbar › Saved filters.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.filterHiddenSettings.savedFilters, toolbarSettings.showSavedFilter
Default: savedFilters = {"none": {id:"none", isActive:true, isSaved:true, label:"None", mode:"all"}};
  showSavedFilter:false in every UI-saved filter inspected (100+ Plans in one workspace)
Report build: showSavedFilter:true on hierarchy trees and pop-ups with a fixed toolbar;
  rendering of the toolbar entry awaits confirmation.
```

No UI-saved `true` sample exists yet. Keep the default `savedFilters` object;
do not author saved selections. Capture one saved filter from the UI before
relying on persisted entries.

## Constraints

- Named threshold or Top N buttons in a saved-filter panel do not establish
  saved member lists versus reevaluated rules, or persistence.
- Capture creation/reapply/clear, user/report scope, reopen/refresh behavior
  and handling of deleted/new members. Do not equate saved filters with report
  bookmarks or promise cross-session persistence without a runtime test.

## Related features

- `SF-FEAT-04`
