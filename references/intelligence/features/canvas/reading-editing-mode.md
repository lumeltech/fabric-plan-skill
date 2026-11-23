---
id: CV-MODE-01
name: Reading and editing modes
area: canvas
category: Modes
status: IS-Confirmed
encoding: observed
visual: Sheet
sources:
  - https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/PlanProperties/1.0.0/schema.json
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes
---

# Reading and editing modes

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Controls panes and actions available to readers vs authors. Editing mode
holds the authoring ribbons and design options; reading mode is for analysis
and collaboration. For each visual the author chooses the reader controls:
toolbar, pivot data, annotations, export, element and setting toggles, chart
types, trellis focus, table reorder/resize/rename, summary table, selection
modes, axis break and chart/card/table tabs.

## When to use

- Lock down reader experience.
- Letting analyst readers re-pivot or change chart types while others only view.
- Read-only visuals where readers should only select data.

## UI path

Mode toggle; settings. Select Reading › Editing to switch modes; in each
visual's settings, choose the allowed reader controls.

## Definition encoding

```text
Path: planProperties.json → workloadModeConfig (EDIT, READ)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- `planProperties.json` wraps `workloadModeConfig` inside `properties`.
  EDIT and READ have different pane contracts; `showLumelAIPane` is optional
  in both. Check the versioned schema rather than copying all EDIT keys into
  READ. Pane configuration is not an authorization or permission grant.
- The toolbar control can make a visual read-only, leaving readers only
  viewing and data selection.
- Editing-only actions, such as inserting rows or columns or Canvas settings,
  are disabled in reading mode.
- Reading-mode export gives image or PDF snapshots; raw Excel/CSV export needs
  edit permission in editing mode.
- Readers cannot change unchecked elements, settings or chart types, and see
  only the chart/card/table tabs the author leaves enabled.
- Selection modes (single click, lasso, reverse lasso, data point) and axis
  breaks reach readers only when their icons are enabled.
- Configure interactions in editing mode, then test selections in reading mode.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- [saved] One inspected plan saved `showBookmarksPane: false` in both EDIT and
  READ, and its READ mode hid the Data pane while keeping the Filter pane visible.
  Pane flags hide panes; they do not delete the bookmarks or filters behind them.

## Related features

- `MX-TB-01`
