---
id: SF-TB-01
name: Slicer toolbar and title
area: slicers
category: Display
status: IS-Confirmed
encoding: verified
visual: Super Filter
sources:
---

# Slicer toolbar and title

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Title, clear, apply, saved filter, search, progress bar, and toolbar colours.

## When to use

- Every slicer needs a readable title.

## UI path

Toolbar settings.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.toolbarSettings
Title: showTitle:true, customTitleText:"<label>", titleFontSize, titleFontBold,
  titleFontItalic (templates may default to true), titleFontColor, headerHeight
Actions: enableClearButton, enableSearch, enableBulkCopyPaste, showSavedFilter,
  enableRenameButton, showProgressBar, applyAllFilter, toolbarIconColor
Placement: toolbarType "fixed" | "float" | "hide" (all three in UI saves);
  floatingToolbar
Evidence: native facets; customTitleText titles user-confirmed at runtime in a
  published report (labels missing until set). Pop-up launchers do not show the title.
```

Set `customTitleText` explicitly: an empty value left controls without field
labels in review. Use `fixed` where toolbar actions such as saved filters must
stay visible; native date sliders use `float`.

## Constraints

- Titles, eraser/clear affordances, search/info controls and clipboard menus
  are presentation. Capture each action's scope; clearing a search term may
  differ from clearing selection.
- Text-entry apply prompts do not prove global Apply All behavior. Test
  reading/editing-mode visibility, keyboard access and selected-count updates.
  Screenshots do not establish progress-bar behavior; capture it separately.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- A user correction switched compact controls from `toolbarType: "float"` to
  `"fixed"`, removed the separate caption text boxes beside them and enlarged
  the frames to fit header and body [confirmed]. Those headers kept
  `showTitle: true` and `headerHeight: 30` [saved].
- Where a control shows its native header, do not repeat the field name in an
  adjacent text box; pop-up launchers still need a label (SF-FEAT-05).
- The corrected fixed headers saved no `customTitleText` [saved]. This differs
  from the finding above (labels missing until set); whether a fixed header
  shows a default field title is unresolved, and the guidance above wins, so
  keep setting `customTitleText` [open].
- Menu opening, propagation and list scrolling under a fixed header were not
  runtime-tested [open].

## Related features

- `SF-DISP-01`
