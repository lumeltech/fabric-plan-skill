---
id: SF-DISP-01
name: Slicer display settings
area: slicers
category: Display
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
---

# Slicer display settings

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Show details, default selection by Boolean measure, forced selection, tooltips, localisation, hover/selected state, no-data text, scale, select-all, hide blanks, keyboard accessibility, RTL.

## When to use

- Bounded default selection; accessibility.

## UI path

Display settings.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.displaySettings, interactionStateSettings
Forced single choice: displaySettings.forcedSelection:true with displaySelectAll:false,
  configuration.singleSelect:true and a default in visualState.slicerFilterAssignments
  (see SF-FACET-01). Runtime: user-confirmed (one year always selected, newest default).
Pop-up switch: minModeSettings.enableMinModeFilter (SF-FEAT-05);
  displaySettings.displaydialogbox stayed false in the working pop-up.
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export; only the forced-selection
values above are isolated. Copy the whole group from a working visual or run
`core/native-samples.md` before writing other display settings.

## Constraints

- Allocate room for selected chips/counts, scrolling and member/measure/
  variance labels independently of the filter position. Test long labels and
  no-data states.
- Date filters also need room for inputs, calendars and presets; a shallow
  container can clip them even when its outer rectangle fits. Resize and
  reflow neighboring visuals, then check in Reading mode at the target viewport.
- Use a native dropdown for a facet that would otherwise consume excessive
  space, and give it room for the open list: in a 76px band the open list
  rendered cropped. Pop-up mode (SF-FEAT-05) needs the user's approval first.
  Captured facet state uses `facetSettings.facetViewType: "dropdown"`;
  preserve its matching assignment/registration/selection state. Test the open
  dropdown, search, clear/reset and long selections, not just the collapsed face.
- Do not impose a universal pixel height: measure the rendered controls under
  the chosen canvas scale and font size, and confirm none are cropped.
- Screenshots do not show forced selection, Boolean-measure defaults,
  RTL/localization or keyboard behavior. Forced single selection with a stored
  default is captured (above); Boolean-measure defaults still need capture; do
  not infer them from a selected chip or radio-style appearance.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Budget effective fit, not the rectangle: header, selected-value and member
  area, search/clear/dropdown affordances, active padding and border together.
  An outer box height is not member space; check at 100% zoom.
- In a user finishing save, compact controls changed all four
  `visualStyles.padding` values (`topPadding`, `rightPadding`, `bottomPadding`,
  `leftPadding`) from 12 to 0, avoiding a double inset around native control
  chrome [saved]. This is component-specific; it does not justify removing
  chart padding.
- Stored padding numbers with padding disabled are not an active inset;
  user-corrected controls kept outer padding disabled [saved]. Saved radius
  values with the radius switch off are not active rounded corners [saved].
- Optional companion preference: no scrollbars in collapsed or expanded
  controls. Enlarge or reflow, or use a fitting native view (a pop-up only
  with the user's approval), and check the open results list; search alone
  does not remove scrolling.
- A stored default selection does not replace registration: a styled control
  whose targets are not registered is incomplete. Verify that the default
  reaches each intended Matrix, card and chart.

## Related features

- `SF-TB-01`
