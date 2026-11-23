---
id: SF-FEAT-03
name: Mass filter (paste lists)
area: slicers
category: Features
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
---

# Mass filter (paste lists)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Paste or type a list of members with custom delimiters.

## When to use

- Filter by a list of IDs from email or Excel.

## UI path

Toolbar › Bulk copy-paste.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.toolbarSettings (enableBulkCopyPaste, massFilter*), filterHiddenSettings.bulkCopyPasteDelimiter
Observed: enableBulkCopyPaste:true with enableSearch:true on a native checkbox facet
  that also uses the pop-up (min mode); bulkCopyPastePlaceHolderText,
  bulkCopyPasteTag* colours and massFilterPopupHeight/Width are companion keys.
Evidence: native facet sample; applied in a report build (rendering awaits confirmation).
```

Copy the whole native toolbar group and change only the switches you need.

## Constraints

- Clipboard controls and selected-count/member lists do not show an open paste
  dialog or executed paste. Capture delimiter, whitespace, duplicate/unmatched
  handling, append/replace and clear behavior.
- Report unmatched values explicitly; pasted lists select existing semantic
  members, not import data or authorize model writes.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Bulk paste is enabled on few saved owners [saved]. Text-area state
  (`facetTextArea`), delimiter and hidden settings are stored apart from the
  toolbar `enableBulkCopyPaste` flag [saved]; keep them with the registration
  context instead of copying only toolbar flags.

## Related features

- `SF-FEAT-02`
