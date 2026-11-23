---
id: MX-COMM-01
name: Comments and collaboration
area: matrix
category: Notes and comments
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/collaborate-on-reports-with-comments
---

# Comments and collaboration

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Data-level and report-level comments, tagging, task assignment, resolve and lock threads.
Comments attach to a cell, row or column, or to the whole report, with rich
text, hyperlinks, replies, stars, @mentions with email notifications and
assignees (status Open or Resolved). A comments column, roll-up indicators on
collapsed parents and a Hide all comments toggle are optional.

## When to use

- Review cycles on report numbers.
- Assign follow-ups on specific values and track them to resolution.
- Overall report commentary for reviewers (report-level comments).
- Exception notes that stay visible on collapsed hierarchies (roll-up).

## UI path

Comments pane. Select a cell, row or column › Comment › Add New Comment.
Comments drop-down: View All Comments, Report Level Comments, Comments column,
Rollup indicator and Settings (General, Digest, Permissions).

## Definition encoding

```text
Path: sheets/{sheetId}/commentSettings.json; planProperties workloadModeConfig.showCommentsPane
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Only the comments column is exported to Excel or PDF; cell-level threads are
  not included in exports.
- Without filter context for comments (`MX-CTX-01`), a comment stays visible
  after slicer selections change.
- Locked threads accept no edits or replies until unlocked; replying to a
  resolved thread, or undoing the resolve, reopens it.
- Report authors can edit or delete other users' comments; Settings › Delete
  all comments clears every comment in the report.
- Settings › General toggles commenting, the panel on open, starred comments
  on load, indicator style/size/position and email notifications; Digest
  schedules periodic comment summaries; Reset all settings restores defaults.
- Comment writeback to an external destination belongs to other modules and
  is not enabled in this release.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Reporting sheets can export `commentSettings.json`; a later UI save added
  it to existing Intelligence sheets without any visual-property or
  sheet-definition change [saved]. Its presence proves neither comments,
  embedding nor an editable visual.
- Inspected settings saved a `user` comment indicator on reporting sheets
  and an `arrow` indicator on Planning sheets, with comments and
  notifications allowed and the Comments and Status columns, rollup,
  starred-only filtering and keep-panel-open off [saved]. They are separate
  from manual notes and prove no thread CRUD or permissions.
- Core guidance records this part on every sheet, while the companion saw it
  absent until a save added it; the core guidance wins, so preserve the part
  where present and never delete it [open].
- Comment filter context is saved apart from note context as
  `visualState.filterContextSettings.isCommentFilterContext` (`MX-CTX-01`)
  [saved].

## Related features

- `MX-NOTE-01`
