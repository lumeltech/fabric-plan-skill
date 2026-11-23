---
id: MX-TB-01
name: Toolbar and reading-mode controls
area: matrix
category: Toolbar and UX
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
---

# Toolbar and reading-mode controls

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Full, minimal, or tabbed toolbar; floating toolbar; which actions readers see.
Full (default) shows the Home, Insert, Design and Export tabs; Minimal keeps
core actions such as Layout, Top N, Auto fit, Row height, Notes and Export.
The toolbar can be unpinned for full-screen viewing and previewed as readers
see it. Quick access (Ctrl+F) finds and opens features; Rails add rulers to
resize and select columns and rows.

## When to use

- Clean reading view for executives.
- Small visuals or screens (Minimal toolbar).
- Limit what readers can change, sort or export.

## UI path

Display settings › Toolbar. Toolbar options dropdown: Full, Minimal, Minimal
with tabs, Reading view preview (Show edit mode returns), Unpin toolbar,
Allowed user controls, Quick access. Rails: Home › Rails (Actions); numbering
via Display settings › General › Show Ruler Numbering.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.toolbar, readModeToolbar, readViewConfig
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Allowed user controls set the reading-view toolbar (Auto, Full, Minimal,
  Minimal with tabs or Off) and which tab items, gripper, reorder, sort on
  click, search, zoom, notes, pagination and conditional formatting readers get.
- Show search works only when the reading-view Toolbar is Off; tab reordering
  applies only to Full and Minimal with tabs.
- Show Expand Collapse Only limits the readers' row gripper to expanding and
  collapsing hierarchies.
- Turning off Configure Toolbar Settings stops readers switching toolbar
  modes; turning off Show Excel Export Settings locks export settings.
- Rows or columns readers insert in reading view can be exported but are not
  saved; they are lost on refresh or page switch.
- With the main toolbar unpinned, the floating toolbar still offers cell
  formatting, show/hide values and comments.
- Rails are on by default except in the Hierarchy, Drilldown and Measures
  (Pivot) layouts.
- Scenario, Writeback, data-input, simulation and forecast items are Planning
  features: keep them hidden from readers and do not author them here.

## Related features

- `CV-MODE-01`
