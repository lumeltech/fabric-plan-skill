---
id: SF-FACET-01
name: Facet filter (list, dropdown, tile, toggle, radio …)
area: slicers
category: Category filters
status: IS-Confirmed
encoding: verified
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/create-a-filter-panel
---

# Facet filter (list, dropdown, tile, toggle, radio …)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Category slicer with view types: checkbox, radio, list, dropdown, tile, toggle, text area, pagination, alphabet buttons; cascade, single select, counts, progress bar.

## When to use

- Any categorical field; choose the view by cardinality.

## UI path

Add Super Filter and place the required dimensions in Category. In the Filter
ribbon choose Quick Mode › Facet; Properties › Style › Category Styling sets
each dimension's control style. First-party filter-panel docs describe Cascade
Filter for dependent options; capture its saved state rather than guessing keys.

## Definition encoding

```text
Registration: SUPER_FILTER; /properties/visualType = 60
Pointer: /properties/superFilterAssignments/0/configuration/visualType = "FACET"
Pointer: /properties/visualState/facetSettings (object)
  enableFacetMode: true (false switches the visual to hierarchy mode, SF-HIER-01)
  facetViewType values in UI saves: "tile", "toggle", "checkbox", "dropdown", "textArea"
  columns (items per row; set it to the member count for a one-row control),
  isColumnResponsive, singleSelect, displaySelectAll, showCount, showFacetHeader
Selection and default: /properties/visualState/slicerFilterAssignments[] =
  {filterType:"VALUES", columnIds:[<field>], columnNames, columnDataType,
   columnType:["Column"], tableNames, sourceType:["PowerBI"], dataType:["string"],
   valuesFilter:[{id:[<member>], label:[<member>]}], valuesFilterApplicationType:"include"}
  superFilterAssignments[].filter restricts the slicer's own member list; it is not
  the selection.
Single choice with a default (newest year first):
  configuration.singleSelect:true; facetSettings.singleSelect:true;
  displaySettings.forcedSelection:true; configuration.sort[0].direction:"DESC";
  default member stored in slicerFilterAssignments.
Dropdown facet (user editor save replacing a pop-up launcher): facetViewType
  "dropdown", minModeSettings.enableMinModeFilter false, toolbarSettings.showTitle
  true (customTitleText as the label, titleFontSize 13, titleFontBold false); the
  editor added displaySettings.imageDataPosition "right". The separate text label
  was deleted; the frame grew to about 96–104 px in a 116 px band (1920 × 1080).
Evidence: UI-saved selection captured from the report editor; native facet samples.
  Runtime: tile view, single-select default and forced selection user-confirmed in a
  published report. Toggle and checkbox views are UI-saved values applied in a report
  build; their rendering awaits confirmation. Radio is still uncaptured.
```

Clone a native facet of the same kind and change only the view and options.
`singleSelect` is observed on the assignment configuration as well as in
`facetSettings`; keep both consistent. One field per visual was the pattern
used for top-band filters; a multi-field facet panel stores one
`superFilterAssignments` entry per field (see SF-HIER-01 for the per-level
structure).

## Constraints

- Mix control types to suit cardinality: tiles, toggles or checkboxes for up to
  about five members; dropdowns showing their own title, or trees (SF-HIER-01),
  for long lists [confirmed]. Use pop-ups (SF-FEAT-05) only after the user
  approves pop-up mode. A report where every filter is a tile row was rejected
  in review as repetitive; vary the view type within a page.
- A dropdown's open list rendered cropped inside a 76px filter band in a report
  review. Give a dropdown room (the user's own dropdowns were about 100 px tall
  in a 116 px band) and check the open list at the target viewport; collapsed
  size alone is not proof.
- When cloning, clear stored state from the template: `slicerFilterAssignments`,
  `embeddedSuperFilter`, `filterHiddenSettings.categorySelectAllState` and
  `selectedDatePreset`. A stale stored selection produced "No data" visuals.
- Resolve the field actually bound to each control and correct mismatched
  display titles. Placement (top band, left/right rail, inline, popup or
  custom) and visible control style do not prove the field or filter scope.
- Capture single/multi-select, select-all and clear defaults per category.
  One checked or filled item, or a collapsed `+N` count, does not establish
  the selection mode or the selected values.
- When a facet switches the analyzed account or measure, require exactly one
  selection and never sum members with different meanings. Capture whether
  metric-switch buttons are a facet on a measure-selection field or bookmarks.
- A year or month selection alone does not set a QTD/MTD as-of date. Trends
  that keep history under a month selection may be intentional; make that
  explicit and test month/year rollover and overnight-shift date roles.
- Verify filter coverage and grain across actuals, PY, budget/AOP, outlook and
  targets, especially coarser-grain budgets. Define coverage and no-data
  behavior for facts the filtered dimension does not apply to.
- First-party docs confirm one multi-dimension visual; panels may mix
  checkbox, toggle, dropdown, tile, radio and list styles. Capture each
  category's style, collapse/scroll rules and composition; captions do not
  establish style enums.
- Repeated or similar controls across panels or pages do not prove shared
  selections, cross-visual filtering or cross-sheet sync. Verify per-category
  selection rules, cascade dependencies and invalidated selections. Each page's
  slicer stores its own default; set it on every page that needs it.
- Verify propagation to thresholds, status rules and trends, not only
  headlines. Multi-member selections need explicit weighted metrics and
  aggregate target rules, not an arbitrary member's threshold.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
More view values: saved (not captured) facets also use "radio" and "list" [saved]
Pointer: /properties/visualState/facetSettings/cascadeFilter = true on every enabled
  facet where inspected (dropdown, toggle, tile, checkbox) [saved]
  Its link to the documented Cascade Filter switch and its runtime effect: not isolated [open]
Partial: {"enableFacetMode":true,"facetViewType":"dropdown","cascadeFilter":true} [saved]
Registration configuration also saves filterMode:"basic", filterOperator:"is", hide,
  isExpanded, locked, measureSearch, paneWidth, sheetDataItemAggregationType:"sum",
  toolBarTrigger, sort[] and topN{} (SF-FEAT-06) [saved]
  position:"RIGHT" is the only saved value; its rendering effect is unknown [open]
Selection typing: columnDataType ["String"] with dataType ["string"] (numbers: SF-NUM-01) [saved]
```

- The Single select switch changed only `facetSettings.singleSelect` (false to
  true); the registration `configuration.singleSelect` stayed unchanged [confirmed].
- Saved owners pair facet `singleSelect: true` with registration
  `singleSelect: false` [saved]. This differs from "keep both consistent" above;
  that guidance wins for authored single-choice controls until captured [open].
- A cloned facet kept the donor's `facetSettings.enableCategorySearch: true`
  and, in a 68px-tall top band, showed only a search box; with search off the
  same 68px control showed no tiles, only a scroll indicator [confirmed]. With
  a fixed toolbar the facet keeps about 34px of padding between the title and
  the tiles: at 100px (28px header, 36px tiles) one tile row still scrolled;
  at 132px (26px header, 30px tiles) it showed without scrolling [confirmed].
  The exact minimum is not established [open].
- Compact chips like a design mockup: `isTileResponsive: false`,
  `isColumnResponsive: false`, `columns` = member count and a fixed
  `tileWidth` sized to the longest label rendered as left-aligned tiles
  [confirmed]. Native 54px tile slicers use `toolbarType: "float"`, which
  likely drops the persistent title [open].
- Toggle or tile appearance does not establish single selection: enabled
  facets, toggles included, saved `singleSelect: false` in one inspected set [saved].
- Classify the active view before counting or cloning: date and other non-facet
  owners keep a dormant `facetViewType` (often "checkbox") with `enableFacetMode: false`
  [saved]. A control seen as a dropdown saved "checkbox", so the visible form can
  come from another group such as the pop-up or hierarchy dropdown [open].
- An empty `slicerFilterAssignments` on a registered owner means no stored own
  selection, not an unbound control [saved].
- Owner and registration pivots use lowercase `category`; page-level entries use
  `Category` (CV-FILT-01); never substitute one for the other [saved].
- A static text box showing a year is not a selector; the user replaced one
  with a registered Super Filter on the year field [confirmed]. A text label, a
  page-level lock and a visible selector are three different capabilities.
- A cloned control's layer name can keep the donor's field name; resolve the
  bound field, not the layer label [saved].
- Rebind the field and its typed members together; a same-named field in
  another table is not interchangeable.
- Optional companion guidance: currency or reporting-unit selectors are
  single-select and required; a version selector is a comparison selector or
  scoped to visuals showing one version, never a page filter over
  actual-versus-budget visuals; month-end packs default to the last closed
  month, not All across years. Keep titles that name the selected period or
  member consistent with the effective selection.

## Related features

- `SF-FACET-02`
- `SF-FEAT-02`
- `SF-HIER-01`
- `SF-FEAT-05`
