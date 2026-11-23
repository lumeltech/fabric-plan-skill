---
id: CV-ANN-01
name: Annotations
area: canvas
category: Storytelling
status: IS-Confirmed
encoding: observed
visual: Canvas
sources:
  - https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/Intelligence/Properties/1.0.0/schema.json
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes
---

# Annotations

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Rich-text annotations on data points and canvas. A note placed on a data
point annotates that point; one placed on an element or the canvas covers the
whole view. Each indicator can have its own colour, and indicator style and
size are configurable. A Comments pane element gathers element- and
dashboard-level comments, can be styled and can present annotations as an
animation.

## When to use

- Narrative sheets.
- Explaining an anomaly or variance at the exact data point.
- Collaborative review where several users add context to one dashboard.
- Guided presentations that zoom to each annotated chart in reading mode.

## UI path

Annotations (Intelligence ribbon › Notes: Add Notes, View all Notes, Hide All
Notes). Select the element or data point before adding a note. Insert a
Comments pane from the element insert menu or from the all-comments view; its
Add link creates dashboard-level comments.

## Definition encoding

```text
Path: sheet.json → commentary.annotation; sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.annotationBox
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- The public Intelligence page contract includes `commentary`; retain its
  wrapper, notes and annotation settings. It is not a new comments-execution
  API, and it does not authorize edits to another module's comment settings.
- Hide All in an element's annotation menu toggles that element's notes;
  hiding does not delete them.
- Present (animated annotations) is enabled in the Comments pane
  configuration and runs in reading mode, zooming to each annotated chart.
- Readers can add visual- and data-point-level notes only when the author
  allows annotations in reading mode.
- The Comments pane marker setting applies one format, size and colour to all
  indicators; enable wrap text there to show long notes in full.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Matrix presentation: /properties/visualState/annotationBox (object; partial)
  {enabled, placement "RIGHT", size, fontSize, color, itemGap, fontFamily, padding,
  border, cornerRadius, shadow, title {showTitle, showValue, showVariance, ...}}
Data binding: properties.pivotAssignments bucket "annotation" (String column,
  sourceType "PowerBI")
Sheet defaults: sheet.json /properties/commentary/annotation/settings (indicator,
  title and text styling, hideAllAnnotations, container effects)
Evidence: [saved] semantic-model and Planning-backed annotation matrices
```

- [saved] An enabled `annotationBox` alone shows no commentary; the `annotation`
  bucket binding supplies it, and manual `notes.notes` stayed empty on the
  semantic-model donor.
- [saved] The donor showed its String column aggregated as First, which can hide
  several distinct comments; check cardinality and grain before binding. Never add
  a text measure to the model outside the permission-gated `model-measures` mode.
- [saved] Donors differ: copy the whole `annotationBox`, including its title
  (responsive value/variance rendering, triangle variance icons), padding, border,
  radius, shadow and font family, not a fragment.
- [saved] Planning-backed annotations bind the same bucket to an InfoBridge output
  (`sourceType: "InfoBridge"`). That source is not enabled in this release; preserve
  existing pipelines unchanged and never paste their IDs into another plan.
- [saved] Every inspected sheet exported a `commentSettings.json` companion
  (comment indicator, comment and notification switches); preserve it per sheet. It
  is separate from notes and annotations and does not prove comment threads work.
- [saved] Sheet-level Marker Mode drawings live in `commentary.notes`, not in
  annotation settings; see Marker Mode.
- Choose the owner before designing commentary: chart/KPI notes, table/matrix
  notes, data-bound annotations, sheet markers and standalone Text are different
  components. Test hierarchy levels, empty and long comments and each period.

## Related features

- `MX-NOTE-01`
- `CH-NOTE-01`
