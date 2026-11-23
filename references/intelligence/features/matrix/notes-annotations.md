---
id: MX-NOTE-01
name: Notes and annotations
area: matrix
category: Notes and comments
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes
---

# Notes and annotations

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Cell, header, and report notes; footnotes; notes column; marker mode.

## When to use

- Explain variances; narrative sheets.

## UI path

Notes tab / reading mode › Notes.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/visualState/notes
Observed keys: show:true, notes:[], footNote, indicator, markerSettings, persistProperties
Pointer: /properties/visualState/annotationBox (group observed)
```

Copy the saved reporting Matrix groups or isolate an active note. Empty
`notes:[]` does not prove an authored note. A visible Notes column is not
proof of cell annotation storage, collaboration or writeback.

## Constraints

- A numbered marker in a label or cell may be literal text, an anchored note
  or a CF status icon. Verify which; capture annotation storage, anchor and
  disclosure text, and test destinations/export placement. Never invent
  footnote text.
- Instructional text such as a right-click drill-through tip is not an enabled
  action, verified navigation or permission to expose sensitive records.
  Capture the note anchor and destination separately.
- Notes, assignee or action columns are presentation evidence only, not proof
  of input editing, assignment workflow, collaboration threads or writeback.
- Check that commentary periods match the displayed KPI period; verify
  filter-aware text and stable row anchors. Static commentary does not
  establish dynamic-note encoding.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Owners and serialization

```text
Pointer: /properties/visualState/notes/notes[]          (note records)
Pointer: /properties/visualState/notes/indicator        (indicator defaults)
Pointer: /properties/visualState/notes/footNote         (footNoteColumn, footNoteHeight, optional showFootNote)
Pointer: /properties/visualState/notes/showNotesColumn  (Notes column flag)
Pointer: /properties/visualState/commentsNotes/globalNoteSettings (shared presentation)
Evidence: saved native Table and Matrix owners [saved]
```

- `notes`, `commentsNotes`, `filterContextHashMap`, `filterContextSettings`
  and `annotationBox` are objects, not JSON strings, and are separate from
  chart notes [saved]. Preserve absent `show` or `showNotesColumn` fields
  rather than inventing defaults.
- `persistProperties` holds floating/editor appearance (colours, icon,
  display options); `commentsNotes.globalNoteSettings` mirrors shared
  presentation under partly different names and enums [saved].
- Indicator enums differ between the groups: `notes.indicator` saves
  `indicatorType:"numbered"`, `size`, `color` and
  `indicatorPositions:["left","center"]`, while the shared indicator saves
  `type:"number"` and `position:"LEFT"` [saved]. Never normalize one enum
  set to the other.
- A `customIcon:"CIRCLE_FILL"` value is saved with the note-indicator
  defaults; its exact parent object is not isolated [open].
- Footnote and Notes-column flags were mirrored in the shared settings
  [saved]; units of the numeric `footNoteColumn` and `footNoteHeight` are
  not established [open].

### Selection identity

- `selectionIds`: a cell note saves one `{rowId, colId, type:1}`, a column
  note `{rowId:null, colId, type:3}`, a multi-cell note several `type:1`
  entries; Notes-column records can save an empty array [saved]. Keep their
  full metadata; empty does not mean a canvas note.
- Record keys: `id`, `index`, `rowId`, `colId`, `measureGuid`,
  `filterContextHash`, `coord`, `indicator`, `unformattedText` (lowercase f;
  chart notes use `unFormattedText`) and optional audit/runtime fields
  [saved].
- IDs are engine identities, not display labels; a record's top-level
  `colId` can differ from its selected cell's `colId` [saved]. Never
  "repair" them to equality.
- No row-only selection enum was isolated; never guess `type:2` [open].
- Note counters can differ between owners and from the record count, and a
  save can normalize a Matrix counter [saved]. Retain notes and counters.

### Model-bound annotations

- Saved INFORIVER/10 owners can bind a semantic-model text column to an
  optional `annotation` bucket (the Annotation field well), saved with First
  aggregation [saved]. First can hide several distinct comments; validate
  cardinality and grain.
- `annotationBox` presents those bound annotations and is not the manual
  Notes column or footnote; an enabled empty box creates no commentary
  [saved]. InfoBridge- or Planning-sourced annotation columns are not
  enabled in this release.

### Workflow and checks

- Notes attach to a Matrix cell or total and can follow filter context
  (`MX-CTX-01`); markers can be lettered, text is rich, `#` fetches a report
  value into the note, and display is Card or Floating [confirmed].
- Report-described route, not a tested sequence: select a cell, column or
  several cells › Intelligence › Notes › Add Notes; enable Footnote and/or
  Notes column; review by indicator hover or View All Notes; set footnote
  height, columns and border and indicator style, size and colour; use card
  mode or floating-note settings for long commentary [open].
- Keep cell attachment: do not replace attached notes with a free-floating
  text visual.
- Clone records only into the same scope with known target IDs; create new
  notes through a verified method so identities and audit fields regenerate.
- Verify anchors survive sorting, hierarchy expansion, filters and layout
  changes, and that footnotes and the Notes column leave required grid width
  and height.
- Re-export to confirm record count, HTML and attachment, then test hover
  and filter switching in the native runtime.
- Shared-note CRUD, permissions, threaded replies and cross-report IDs are
  not established by saved examples [open].

## Related features

- `MX-COMM-01`
- `CV-ANN-01`
