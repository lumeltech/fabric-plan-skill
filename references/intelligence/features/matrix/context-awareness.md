---
id: MX-CTX-01
name: Context awareness
area: matrix
category: Toolbar and UX
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/context-awareness
---

# Context awareness

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Notes, titles, headers, and formatting that follow the filter context.
Content entered for one filter or slicer selection is shown only for that
selection: notes, comments, header presets, measure headers, titles and
conditional formatting update as the selection changes. Filter Context
Settings turn this on per visual and choose which content types respond.

## When to use

- Per-scenario notes; per-year titles.
- Commentary that differs by the region, period or segment selected.
- Headers or titles that must state the current selection.

## UI path

Context settings. Matrix toolbar: Insert › Filter Context › Filter Context
Settings: turn on Filter Context, toggle Notes and Comments, Save. Charts:
(...) More options › Filter context.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.filterContextProperties (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Without filter context, a note or comment entered for one selection stays
  visible after the selection changes.
- Only dimensions included in the filter context drive it; a slicer on another
  dimension does not switch notes or comments.
- Notes and comments are switched separately; View All Notes lists the notes
  kept for each filter/slicer combination.
- Header presets and measure headers reflect selections only when filter
  context applies; see `MX-HEAD-01` for appending selections to headers.
- With Super Filter, Intelligence visuals become context-aware without extra
  configuration or new model measures.
- Context-aware data inputs, locked input cells and writeback of selections
  belong to other modules and are not enabled in this release.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/filterContextSettings (object)
Keys: filterContextStatus, isNoteFilterContext, isCommentFilterContext (booleans)
Pointer: /properties/visualState/filterContextHashMap (object: note hash → filter field members)
Pointer: /properties/visualState/notes/notes[]/filterContextHash (per note record)
Evidence: saved native Matrix with one note per filter member [saved]
```

- In that owner all three `filterContextSettings` flags were true, every
  note record had a populated `filterContextHash`, and the hash map tied
  each hash to the filter field and member it was written for [saved].
- Its generic `filterContextProperties` stayed empty or null [saved];
  reading only that group wrongly suggests the notes ignore filter context.
  The `filterContextProperties` path in Definition encoding stays a capture
  placeholder.
- `isNoteFilterContext` and `isCommentFilterContext` appear to match the
  Notes and Comments toggles, but that mapping is not isolated [open].
- Hashes and selection IDs are runtime values of the target, not
  transferable labels [saved]; never author or copy them (see the cloning
  rules in invariants).
- The hash map names the filter field the sheet's slicer actually uses; do
  not substitute a similarly named date field from another page [saved].
- Report-described route: Matrix tab › Filter Context Settings › enable
  Filter Context › Save, after selecting each filter member and writing that
  member's note [open]. Then switch members and confirm each note shows only
  for its member.

## Related features

- `MX-HEAD-01`
