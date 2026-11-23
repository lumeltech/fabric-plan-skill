---
id: CH-NOTE-01
name: Notes on charts
area: charts
category: Chart formatting
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Notes on charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Attaches notes to a chart: canvas notes placed anywhere for overall context
and data-point notes anchored to a selected point; both can be dragged. Text
supports rich-text formatting, # references that show a data point's value
(category + measure) and Use data point color. Global settings set the
indicator type (All, Marker only, Text + Arrow, Floating text), border, arrow
style/color and marker letters, numbers or symbols and size.

## When to use

- Explain spikes.
- Add context to a specific data point or a summary for the whole chart.
- Quote a data point's value or color inside commentary.

## UI path

Chart › Notes. On the chart ribbon select Annotation (Story group), then click
the chart for a canvas note or a data point for a data-point note. Select note
text for the rich-text menu. Hover a note for edit, delete and note-level
Settings; use the settings icon for global indicator settings and Hide All to
hide every note.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Notes are available for charts and tables only, not cards.
- Data-point notes and # value references need a category and a measure of
  the chart; canvas notes are not tied to a data point.
- Global indicator settings apply to every note in the visual; note-level
  settings override them for that note only.
- Hide All hides every note; delete individual notes from the hover menu.
- Documented UI behavior is not encoding evidence; capture a native note
  sample before writing notes into a definition.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_annotation (JSON string)
Decoded: chart note settings plus annotations[]; records save creationType "notes"
Pointer: /properties/visualState/commentsNotes (object): globalNoteSettings,
  note counters, creation/editor state, an ID map and commentsMap
Pointer: /properties/visualState/hiddenProperties_!!!_annotationSettings (JSON
  string): editor/dialog state such as isOpen and showEditor
Pointer: /properties/visualState/hiddenProperties_!!!_filterContextSetting (JSON string)
Sheet: sheet.json -> properties.commentary.notes (page defaults, visibility,
  counter, marker state)
Record keys: id, index, timestamps; type "dataPoint" or "point" (canvas note
  with empty target and dataKey); target, dataRowId, dataKey {instanceId, id,
  measureName, group, color}; text, unFormattedText, comment, formattedText;
  displayStyle "card" | "float" per note; displayAnnotationAs "floatingText"
  (per-note override; settings default "markerText"); coord, relativeCoord,
  position, relativePosition, scale, size, ratio; filterContextHash,
  filterContextValue; rollupTargets, rollupTarget, tableAnnotationDataProps
Evidence: [saved] saved chart notes; not isolated one change at a time.
```

```text
Settings in hiddenProperties_!!!_annotation: show, displayAnnotations,
  showTimestamp, showUsername, enableReply, showFootnote, rollupNotes;
  indicatorType ("number", "Arrow"; case matters), indicatorPosition,
  indicatorSize, indicatorColor, indicatorIcon, iconColor; floating shape,
  stroke, end, arrowColor, arrowWidth, borderColor, borderWidth, borderStyle,
  dragLineType, textAlignment, verticalAlignment
commentsNotes.globalNoteSettings.floatSettings: arrowStyle, arrowEnd,
  displayNoteAs, horizontalAlign, verticalAlign (other names; map, never copy)
Fetch with "#": span class "hash-mention", title "[<member> > <measure>]",
  key "#[NO_GROUP~**~R0-%-<member>__#__<bucket>]", HTML-escaped JSON in
  data-value {title, key, value, color, text, image, avatar}
Filter-aware: filterContextProperties (dimensions, current hash, hash map,
  current JSON); filterContextSetting {enableFilterContext, filterContextKey
  "<table>.<column>", hash, filterContextJson, feature.showFilterContextNotes}
Evidence: [saved]
```

- A UI-created data-point card note left `text` and `comment` empty, stored
  rich HTML in `unFormattedText` and processed text in `formattedText`; do
  not fill every text-like field [saved]. Note HTML is plain HTML, never a
  Lexical tree; escape inserted text and keep the companion fields aligned.
- Attachment, presentation and fetched content are independent: a data-point
  note can float and fetch values, and can attach to a derived variance
  series (target and `dataKey.measureName` end in `ΔPL`; `group` and `color`
  null) [saved]. Keep explicit nulls and derived identities, and never invent
  `"canvas"` or `"visual"` type values [saved].
- `displayAnnotations: "create"` is editor state, not a floating-view
  selector; note `scale` is not the visual rectangle, and negative offsets
  occur [saved].
- Counters: sheet `commentary.notes.counter` and each annotation
  `noteCreateIndex` keep the last-used index, `commentsNotes.noteCreateIndex`
  the next one; counters are not live-note counts [saved]. A UI save advanced
  the sheet's owners together, while an import advanced only the edited
  owner; preserve owner-local values and never restart them per visual
  [saved]. Some chart owners, such as a waterfall, carry no note groups
  [saved].
- Use the `#` picker for fetched values; never build mention delimiters from
  labels [saved]. The fetched item can differ from the note's attachment, so
  reconcile each with the surrounding prose (measure, sign, unit, period and
  scope).
- A cached `value` or `text` does not prove refresh after a member or data
  change [open]. Never replace a token with a typed figure while calling it
  dynamic.
- Each note keeps its own `filterContextHash`, and other contexts' hashes
  need not appear in the current map [saved]. Null note hashes mean unscoped
  notes even when the visual has a context; never invent a hash [saved].
  Sheet `filterContextUserConfig` can hold active settings apart from cached
  pop-up state [saved].
- Card view saves `displayStyle: "card"` and Floating view `"float"` in saved
  donors [saved]. A user-reported Floating save was absent from a fresh
  export [open]. Report instructions also name highlight, selected-text links
  and double-click editing of floating text [open].
- Companion exports show note records on KPI card owners, unlike the
  charts-and-tables constraint above, which stands until a native capture
  resolves it [open].
- Cross-visual stories use separate notes on separate visuals; no shared
  multi-visual record was seen [saved]. Clone a matching note-bearing owner
  and bind it to new runtime targets, never to source IDs.
- Validate: note records and companions intact; IDs unique per owner; target
  row, measure and context correct; card or float per record without clipped
  text, hidden data or off-canvas callouts; HTML and mention JSON parse; each
  filter member shows its notes. Save, reopen and export to confirm
  persistence, then test hover, View All Notes, hide/show, edit and delete in
  EDIT and READ modes on a test copy. A navigation test does not cover notes.
- Pane flags that hide the Comments pane do not show whether the Notes panel
  is available [open].
- Find a user-created note's saved owner (sheet and visual) by readback
  before editing it; one such note was saved on a different sheet than
  assumed [saved].

## Related features

- `CV-ANN-01`
