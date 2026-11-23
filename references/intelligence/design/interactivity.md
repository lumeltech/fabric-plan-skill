# Interactivity

<!-- Design topic for the `fabric-plan-skill` skill. -->

## Slicer scope

| Scope | Where it lives | Use |
|---|---|---|
| Visual-level | `superFilterAssignments[].filterLevel: "visual"` | Default for on-canvas slicer visuals |
| Sheet-level | `sheet.json → pageLevelFilterAssignments` | Filter pane; filters every visual on the sheet |
| Report-level | `planProperties.json → workloadLevelFilterAssignments` | Filters every sheet |
| Synced slicers | `planProperties.json → syncSlicerConfig` | Same slicer state across sheets (feature `CV-INT-02`) |

Remember the three-part filter state (assignment, registration, selection) in
`core/invariants.md`.

For compound Super Filters, use the [slicer feature files](../features/slicers/_index.md).
Declare separately: in-panel cascade between categories, interaction targets
between visuals and cross-sheet synchronization. Define whether
search/rank/presets change available members, selected members or both. Test
invalidated selections and measure recalculation; matching chips or captions
in a screenshot do not establish any of these behaviors.

## Visual interactions

- `properties.visualInteractions { <originEntityId>: { dataInteractionType } }`
  stores edit interactions per source visual (feature `CV-INT-01`).
- Default: clicking a chart or Matrix **filters** other visuals.
- Use highlight only when part-to-whole context matters and the user asks.
- Turn interactions off for text elements and for visuals pinned to a fixed scope.

## Drill

- Matrix: expand/collapse hierarchies, drill down in performance mode
  (`MX-LAY-03`).
- Charts: drill down / up on hierarchical axes (capture sample).
- Drill-through between sheets: `planProperties.drillThroughConfig`
  (feature `CV-INT-03`) — capture a native sample before authoring.

## Bookmarks and navigation

- Bookmarks capture view state for toggles and story steps (feature `CV-BMK-01`).
- Navigation follows the session profile (tabs, rail or supported buttons);
  do not reset to sheet tabs for every report (feature `CV-ELEM-02`).
- Keep bookmarks ≤ 8 per report and name them for the reader.
- Include Help and Info controls per [session design](session-theme.md) with
  native actions; isolate bookmark scope so explanatory panels do not reset
  data selections.

## Embedded Planning sheets

- Place slicers that drive the embedded grid on the same Intelligence sheet.
- Keep scenario selection in a single-select filter context.
- Bound the default selection (one region, one year) to stay under the grid
  cell budget.

## Reading vs editing mode

Consumers use reading mode, whose toolbar options are set per visual
(`readModeToolbar`, `readViewConfig`). Decide which actions readers need
(export, notes, sort); hide the rest.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Filter levels and defaults

- Put each filter at the narrowest level that works: report (period, entity,
  currency, scenario context) → sheet (dimensions relevant to that sheet) →
  visual (Top N, fixed comparison).
- Every slicer changes something visible; show the active filter context in
  the sheet subtitle.
- Defaults give a meaningful first view, such as the latest closed period,
  not All across years.
- A scenario or version selector must not remove the comparison a visual
  depends on (actual against plan): scope it to visuals that show one
  scenario, or use a comparison selector the model provides.
- Per-visual filter metadata does not prove propagation to other visuals or
  sheets; test it [open].
- After any filter change, recheck KPI, chart and bridge values under the
  saved context and make static period, member and scenario subtitles agree;
  an earlier reconciliation does not cover a broader scope.

### Click, drill and navigation intent

- Specify cross-filtering or drill only where it answers the next question in
  the storyline, and state what changes when the reader clicks.
- Use only navigation elements that have feature files; when navigation is
  unconfirmed, design sheets to stand alone and mark navigation for
  verification.
- Design drill-through with the destination's drill-through fields and the
  source's field, hierarchy and action state; registrations alone do not prove
  the route, and repeated labels prove neither expected behaviour nor a
  duplicate-query fault [confirmed].

### Saved selections versus defaults

- A selection the user set or cleared in a saved report is scope state for
  that review, not a new default. Keep defaults from the approved brief, and
  record a changed saved scope as a risk to reconcile rather than a newly
  approved period or member default.
