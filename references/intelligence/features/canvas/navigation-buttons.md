---
id: CV-ELEM-02
name: Navigation and buttons
area: canvas
category: Elements
status: IS-Confirmed
encoding: verified
visual: Canvas
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-a-dashboard
---

# Navigation and buttons

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Buttons and navigation between sheets or views.

## When to use

- Multi-sheet reports.

## UI path

Elements › Navigation.

## Definition encoding

```text
Registration: BI_RUNTIME_INPUT; /properties/visualType = 203
Pointer: /properties/visualState/navigatorState
Default keys: type, style, navigatorButtonState, navigatorTabsState, activeEditStyle
Observed types: "PAGE_NAVIGATOR_TABS" (page navigator); "NAVIGATOR_BUTTON" with
  isNavigationBackForDrillThu:true (back button on a drill-through destination)
Page button (UI-saved, runtime-verified): type "NAVIGATOR_BUTTON",
  isNavigationBackForDrillThu:false, navigatorButtonState = {actionType:"PAGE_NAVIGATION",
  bookmarkId:null, pageDestinationId:"<target sheet's numeric id>", webUrl:null}
Sheet numeric id: assigned in creation order and kept when sheets move; it is
  not stored in definition.json. It equals the 1-based position only until a
  sheet is inserted before older ones. Track it in the build manifest; a UI save
  also writes it as every visual's originEntityId.
Tabs: navigatorTabsState.selectedPages lists sheet numeric ids; tabs display in
  Explorer order, not list order.
Hidden target sheets: navigatorTabsState.destinationType = {all:true, hidden:true, tooltip:false}
Icon: style.<STATE>.shapeState.icon.iconTypeMapping.default.src = "<icon name>";
  "Home", "Activity", "Package", "Users", "BookOpen", "Info" rendered;
  "LayoutDashboard" and "TrendingUp" did not.
Evidence: destination captured from a button saved in the report editor; navigation,
  hidden-page targets and icons user-confirmed in a published report.
  Runtime: after four sheets were inserted before Help and Info, tabs selecting
  "1".."5" showed Overview, the first two new sheets, Help and Info, so ids
  follow creation order, not position.
```

Copy the complete saved Fabric Plan navigator; preserve the exact
`isNavigationBackForDrillThu` storage spelling. A visible return control is
not proof of a generic fixed page destination or working back-state
restoration. A sheet GUID in `pageDestinationId` left the Actions panel
without a page. Inserting or reordering sheets does not renumber them, so a
destination derived from the new position opens the wrong page.

## Constraints

- Use the approved [design inspiration treatments](../../design/report-inspiration.md#navigation-treatments)
  for underlined tabs, segmented pills, compact rails or labeled panels only
  as appearance guidance. They do not establish native actions or change this
  feature's encoding confidence.
- Capture each control's actual action, destination and permission behavior;
  appearance, including contact or documentation controls, does not establish
  working page navigation or Help/Info. An info text panel is not an action.
- Visual-specific controls (such as Gantt zoom buttons) are visual controls,
  not generic navigator actions.
- Fixed-page destinations, drill-through return and navigation-history return
  are distinct. Capture and test each control and its filter restoration rather
  than assigning one saved navigator to every control.
- Capture reset (Clear all slicers) scope and defaults separately from back
  actions; visible controls do not prove bookmarks, navigation history or
  drill-through.
- Test filter and context preservation and destination authorization per link.
  Screenshots taken with different selections prove neither synchronized nor
  broken state.
- Validate page titles against navigation labels; capture active-state styling
  and keyboard behavior. A collapsed filter indicator (such as `+N`) does not
  reveal the filter field or selected period.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/navigatorState (object, not a JSON string)
Active types seen: PAGE_NAVIGATOR_TABS, BOOKMARK_TABS, NAVIGATOR_BUTTON
navigatorTabsState: layoutType "grid" | "vertical" | "horizontal", rows, columns, gap,
  scrollDirection "vertical", showScrollButtons, destinationType {all, hidden, tooltip},
  hiddenPages [], allowDeselection, launchOnDeselection "none", tabsShortText {},
  hierarchy {isEnabled, indentation, triggerColor, fixedHeight {isEnabled, value}},
  collapsible {isEnabled, isCollapsed, collapsedWidth, collapseDirection,
  collapseAnimation, identifierType, collapseTriggerIcon}, hiddenBookmarks [],
  isHideDeselectedBookmark, selectedBookmarkNavigatorOption
style: DEFAULT (full shapeState plus shapeType) with partial ACTIVE, HOVER and
  PRESSED overrides; activeEditStyle ("DEFAULT" | "ACTIVE") names the state being
  edited, not the active destination
navigatorButtonState.actionType seen: "NONE", "PAGE_NAVIGATION", "WEB_URL"
Evidence: [saved] page navigators, live buttons and cached states in saved exports;
  clicks not tested
```

- [saved] `navigatorButtonState.actionType: "NONE"` on a tabs owner does not
  disable its page or bookmark tabs; resolve the active `type` before reading any
  destination, and compare donors only with the same subtype.
- [saved] `style.DEFAULT.shapeState.action` (disabled, `"NONE"`) is a separate
  owner from `navigatorButtonState`. Preserve partial state overrides rather than
  expanding them to guessed defaults; a rectangle-like tab is not a `BI_SHAPE`.
- [saved] An explicit `hiddenPages` list and the `destinationType` policy are
  separate state. Keep sheet visibility and destination policy together so hidden
  source sheets do not become public destinations when a navigator is cloned.
- [native-export] A user-corrected vertical page navigator saves
  `navigatorTabsState.selectedPages: ["1","2","3","4","5","6"]`, selecting the six
  analytical sheet ids while Help and Info remain separate icon buttons.
  Its DEFAULT, ACTIVE, HOVER and PRESSED styles are independent partial groups.
  Copy the complete navigator instead of building six fixed-destination buttons;
  preserve its destination selection and test every page after a save.
- [saved] Live web buttons save `actionType: "WEB_URL"` with a `webUrl`; use only
  an approved destination. [open] Target-opening behaviour and the action-panel
  mapping are untested.
- [saved] A live drill-through back button paired
  `isNavigationBackForDrillThu: true` with `actionType: "PAGE_NAVIGATION"`, null
  `pageDestinationId`, `bookmarkId` and `webUrl`, and no pivot assignments; null
  destinations alone do not mark it broken. [open] The back-switch mapping and
  behaviour with and without navigation history.
- [saved] `planProperties.json` `/properties/syncVisualsState` can hold cached
  `NAVIGATOR_BUTTON` states keyed by local IDs that match no current visual. They
  are not live controls or donors and add nothing to visual inventories; preserve
  them on unrelated edits. One cached state paired a populated destination with
  `actionType: "NONE"`, so a destination alone does not enable navigation.
- Prefer sizing rows, columns and gap so every destination fits without scroll
  buttons; reflow or split navigation instead. Test every destination, hidden-page
  exclusion, keyboard focus, legible state styling and reading mode.

## Related features

- `CV-BMK-01`
