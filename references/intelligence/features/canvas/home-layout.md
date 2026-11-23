---
id: CV-HOME-01
name: Plan home layout
area: canvas
category: Canvas
status: IS-Confirmed
encoding: observed
visual: Sheet
sources:
  - https://docs.fabricplan.com/resources/create-and-manage-home-layouts
---

# Plan home layout

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

A home layout is the item's role-based landing page, shown when a user selects
Home in the Explorer. A layout can hold a hero banner, sections with titles and
descriptions, images and an available-sheets card block. Layouts are configured
per role: the Item Baseline role serves users without a specific role, and users
with several roles see the highest-priority visible layout. [saved] It is stored
as plan-level state shared by every module, not as Intelligence sheet canvas
state. Merged from the companion Intelligence authoring library; tags follow
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

## When to use

- Preserve an existing landing page whenever this skill updates a definition.
- Point role-specific audiences to the Intelligence sheets they need, only when
  the user explicitly asks to change the landing page.

## UI path

Home tab › Home Layout › Create Layout (choose a role), then the layout
toolbar: Hero Banner, New section, List of Available Sheets, Image, Undo/Redo,
Preview and Save. The Layouts pane holds each layout's Show toggle, Add Layout
and drag-to-reorder priority. An image block's settings choose Fit or Fill.

## Definition encoding

```text
Part: planProperties.json
Pointer: /properties/homeLayout (object)
Keys: show (bool); roles[] (opaque role objects) → layouting.rows[] {height (px),
  isHeightManual (true or absent), defaultHeightRatio (null seen), widths (one row
  only)} → items[]
Item type values: "header-image-text", "text", "preview-cards", "image";
  image items save sizingMode "fill"
Partial skeleton (identities and most item fields omitted):
  {"show":true,"roles":[{"layouting":{"rows":[{"height":<px>,
   "defaultHeightRatio":null,"isHeightManual":true}]}}]}
Evidence: [saved] one saved export; no before/after capture or default copy
```

It is separate from `definition.json` sheet declarations, `sheet.json` canvases
and visual owners. Preserve it unchanged on unrelated edits and run
`core/native-samples.md` before changing it.

## Constraints

- [saved] Every inspected role saved three rows holding four or five items;
  these come from one export and are neither defaults nor a schema.
- [open] Those counts fit the documented default layout (one hero banner, two
  sections and one available-sheets block per role), suggesting that
  `header-image-text`, `text` and `preview-cards` map to those blocks; the mapping
  is not captured.
- [open] Rows without `isHeightManual` omit the key rather than saving `false`;
  what absence means, the effects of manual height, `defaultHeightRatio` and
  `widths`, the top-level `show` versus each layout's Show toggle, and the saved
  value for Fit sizing are unresolved.
- Roles, user assignments and Role Security belong to plan security, outside
  this skill; Role Security takes precedence over the layout. Never create roles
  or change security from this skill.
- Hiding a sheet card with Show Sheets only removes it from the block; it does
  not change access. A layout holds one hero banner and one available-sheets list,
  and each role has one layout.
- Preserve unknown nested state and image resource locators exactly. Never
  transplant role, item or resource identities between plans, or infer behaviour
  from field names.
- Change it only on explicit request, from a captured before/after pair of
  exports, one setting at a time.

## Related features

- `CV-ELEM-02` — navigation between sheets inside the item.
- `CV-MODE-01` — reader-facing panes and modes.
