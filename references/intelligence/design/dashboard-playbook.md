## Contents

- [Purpose](#purpose)
- [Journey at a glance](#journey-at-a-glance)
- [1. Understand the data](#1-understand-the-data)
- [2. Plan the pages](#2-plan-the-pages)
- [3. Mock up and approve](#3-mock-up-and-approve)
- [4. Create a lean item](#4-create-a-lean-item)
- [5. Build the pilot page](#5-build-the-pilot-page)
- [6. Capture the user's polish](#6-capture-the-users-polish)
- [7. Clone the remaining pages](#7-clone-the-remaining-pages)
- [8. Render check and fix pass](#8-render-check-and-fix-pass)
- [9. Deliver and learn](#9-deliver-and-learn)
- [Right-first-time defaults](#right-first-time-defaults)
- [Editor-only today](#editor-only-today)

<!-- Design topic for the `fabric-plan-skill` skill. The proven end-to-end journey for a multi-page dashboard: data, plan, mockup, pilot page, user polish, cloning, render checks and learning. Load for every multi-page report; the mode guides keep their own gates. -->

# Dashboard build playbook

## Purpose

This is the order of work that took a multi-page Matrix, KPI and Super Filter
report from a semantic model to a clean published Plan with the fewest rework
rounds; the user directed each step [confirmed]. It strings the modes together
and does not replace their gates: discovery approval, the Data pane field
check, model-measure permission and the native-sample rules still apply.

Pixel values are examples from one 1920 × 1080 report. Choose canvas, palette
and geometry per report ([dashboard standards](dashboard-standards.md),
[session design](session-theme.md)); keep the proportions and the principles.

## Journey at a glance

| Phase | Goal | Output | Gate |
|---|---|---|---|
| 1 Understand the data | Know what the model can answer | Field registry, data profile, comparison map | — |
| 2 Plan the pages | One question per page | Report spec with filter, KPI and Matrix plans | User reviews the plan |
| 3 Mock up | Agree the look before building | Image, then a clickable multi-page HTML mockup | User approves spec and mockup |
| 4 Create lean | Item in the right folder, Matrices reachable | Plan item with the model `url` | Readback |
| 5 Pilot page | Shared shell and first page complete | Published pilot | Render check |
| 6 User polish | Editor-only finishing on the pilot | User-saved pilot | Fresh readback diff |
| 7 Clone pages | Remaining pages from the pilot | Full report | Validate, concurrency diff, readback |
| 8 Fix pass | One batched correction | Final report | Every page rendered and clicked |
| 9 Deliver and learn | Honest status; skill updated | Summary, updated references | Lint and tests |

## 1. Understand the data

- Capture the registry from the live model ([model inspection](../core/model-inspection.md))
  and read measure expressions and descriptions, not just names.
- Profile before planning: years with data (prior-year comparisons need two),
  budget and target coverage, member counts of candidate filter fields, ratio
  measures with their model format strings (a Matrix shows a model percent
  measure's decimals as stored), currency and sign conventions.
- Build a comparison map: each headline measure against its available
  baselines (prior year, budget, target) and its favourable direction;
  discount and cost are lower-is-better.

## 2. Plan the pages

- Give each page one question and one analytical pattern; the Overview comes
  first, Help and Info last. Reuse one shell on every page.
- Filters: one shared band of decision filters (period plus the two main
  business dimensions) identical on every page, plus at most two page-specific
  filters for long lists as dropdowns showing their own titles. Ask the user
  before planning any pop-up filter [confirmed].
- KPI row: three to five cards per page, each naming its comparison. Ratio
  cards compare values ("vs PY 29.6% ▼") rather than a percent change of a
  percent.
- Matrix plan per visual: rows (at most three hierarchy levels), comparison
  role (prior year, or budget/target), extra measures with short header names,
  colour intent (variance colours, heatmap, in-cell bars) and sort.
- Feasibility pass: classify each planned feature from its feature file and
  the ledger as **verified**, **cloneable** from a user-saved donor, or
  **editor-only**. Tell the user up front which finishing steps they will do in
  the editor; see [Editor-only today](#editor-only-today).

## 3. Mock up and approve

- When the user wants to see the design, offer a static image first, then a
  clickable multi-page HTML mockup built from data exported from the model
  (the same totals the report will show), with working tabs, filters, Help and
  Info [confirmed].
- Draw only what Fabric Plan renders: Matrix, Intelligence cards and charts,
  Super Filters and canvas elements. Mark editor-only or unverified items in
  the mockup legend so the approval stays honest.
- The approved mockup and spec are the design contract for every page:
  colours, sizes, labels and filter set. Keep it open during the build and
  compare page by page.

## 4. Create a lean item

- Create the Plan in the requested folder with the semantic-model `url` in the
  create payload; give each sheet's comment-settings root `recordGuid` a new
  UUID; omit Matrix `dataInput.json` parts
  ([copying a plan](../management-part-02.md#copying-a-plan)).
- Sheet numeric ids follow creation order and drive page tabs, button
  destinations, `originEntityId` and `appliedThemes`
  ([`CV-ELEM-02`](../features/canvas/navigation-buttons.md)). Create sheets in
  their final order when the page list is known; otherwise keep a name → id
  map in the build manifest and never derive ids from list position.

## 5. Build the pilot page

- Build the shared shell once (header with title, tabs, Help and Info; filter
  band; KPI row; content panels; source footer) and complete the first page,
  usually the Overview, with its Help and Info pages [confirmed].
- Clone every visual from a native saved donor of the same kind; never
  compose large visual objects from scratch.
- Publish, read back and check the render, then batch targeted fixes. If a
  feature has no captured encoding and one evidence-based attempt fails, stop
  and list it for the user's editor pass instead of iterating blind.

## 6. Capture the user's polish

- Ask the user to finish what cannot yet be authored (for example a Matrix
  colour scale, in-cell bars, a column sort or tile chips) and to say when they
  are done [confirmed].
- Take a fresh readback, diff it against the last verified one and separate
  deliberate edits from editor normalization (`dataInput.json` parts, re-keyed
  ids, Explore Model scratch sheets).
- Keep the last readback from before the user's save. If the user deleted
  visuals, later complete updates must re-emit them hidden under their
  original ids from that readback; omitting them made every import fail
  ([removing visuals](../core/invariants.md#after-the-user-deletes-visuals-in-the-editor)).
- Record each newly saved encoding in its feature file and the ledger, then
  rebase the builder on that readback: the user-saved pilot is the donor for
  everything that follows.

## 7. Clone the remaining pages

- Copy every shell element from the user-saved pilot with identical geometry
  and styling; change only titles, page-specific filters, KPI bindings and
  Matrix fields ("keep the same formatting, same filters") [confirmed].
- KPI cards: clone, replace the exact `_Measures[<name>]` token and the pivot
  fields ([`KPI-CARD-01`](../features/kpi/kpi-cards.md)), recolour the
  measure-keyed sparkline style ([`KPI-CHART-01`](../features/kpi/insight-charts.md))
  and invert colours for lower-is-better measures
  ([`KPI-VAR-01`](../features/kpi/kpi-variance.md)).
- Matrices: clone from a user-saved Matrix with the same comparison role so
  its engine id set (actual, comparison, variance, variance %) stays intact
  ([`MX-VAR-01`](../features/matrix/variance-columns.md)). Reuse its colour
  scale, bars, sort and total-row formatting only on those engine ids.
- Update every page's tabs and Help, Info and Back destinations with sheet
  ids; restamp `originEntityId`; add an `appliedThemes` entry per sheet id.
- Validate with the live registry and the readback baseline, write compact
  JSON, run the concurrency diff and send the complete definition. A
  339-part, 10 MB update ran 23–33 minutes; resume the saved operation instead
  of resubmitting ([REST and LRO](../core/rest-and-lro.md)).

## 8. Render check and fix pass

Check every page after publishing, at fit-to-canvas and zoomed in for cell
text:

- the tabs list the analysis pages in order; each tab and the Help, Info and
  Back buttons open their pages;
- filters show their tiles or titled dropdowns with no scroll marks, and each
  dropdown's open list has room;
- KPI values, comparison arrows and colours, and each card's own sparkline
  colour;
- every Matrix: short plain headers, a `Total` label, single `%` signs, bars,
  red/green variance, heatmap colours, sort order, expand/collapse icons on
  multi-level rows and no status bar;
- no text box shows a scrollbar.

Collect every defect first and fix them in one update; each large update costs
about half an hour. Logistics: the browser must be in front to repaint; reload
after publishing; navigate with the page list; restore any zoom change; avoid
toolbar actions such as Explore Model, which saves a scratch sheet into the
definition ([`CV-EXPL-01`](../features/canvas/explore-model.md)).

## 9. Deliver and learn

- Report which layers passed (static, API, readback, rendering) and list the
  editor-only items with exact steps for the user
  ([validation layers](../core/validation-layers.md)).
- Feed reusable findings back into feature files, the ledger, the
  [dashboard standards](dashboard-standards.md) and the
  [troubleshooting table](../authoring-part-02.md#troubleshooting); keep
  report-specific choices out. Run `build_index.py`, `lint_references.py` and
  the tests.

## Right-first-time defaults

Rendered as intended in a published multi-page report (1920 × 1080 canvas).

| Component | Default | Reference |
|---|---|---|
| Shell | Header about 10% of the height (title left; tabs, Help and Info right); filter band about 11%; KPI row about 17%; panels about half; one-line source footer. Backgrounds behind content; accent bars in front of their cards | [`CV-LAYER-01`](../features/canvas/layers-elements.md), [layout](layout.md) composition A |
| Navigation | Underlined tabs for the analysis pages only; outlined Help and Info buttons; Back to report on Help and Info; ids from the manifest | [`CV-ELEM-02`](../features/canvas/navigation-buttons.md) |
| Shared filters | Period, region and channel as tile chips: search off, fixed chip width, 30 px chips, 132 px tall facet | [`SF-FACET-01`](../features/slicers/facet-filter.md) |
| Page filters | Up to two dropdown facets at the band's right end, showing their own titles (13 px regular), about 100 px tall; no separate labels; pop-up mode only with the user's approval | [`SF-FACET-01`](../features/slicers/facet-filter.md), [`SF-FEAT-05`](../features/slicers/popup-mode.md) |
| KPI cards | Title, value, one or two comparison lines; sparkline about a third of the height in the measure's colour, matching the accent bar | [`KPI-CARD-01`](../features/kpi/kpi-cards.md), [`KPI-CHART-01`](../features/kpi/insight-charts.md) |
| Matrix title | One native title element: bold title and a muted subtitle with period, comparison and colour key | [`MX-HF-01`](../features/matrix/header-footer.md) |
| Matrix layout | Renamed headers; column widths that fill the visual; row heights that fill the panel (here 44 px hierarchy rows, 56 px heatmap rows) | [`MX-COLW-01`](../features/matrix/column-widths.md), [`MX-VIS-01`](../features/matrix/matrix-visual.md) |
| Matrix totals | Grand total labelled `Total`; `totalRowsDisplay` kept; status bar off | [`MX-TOT-01`](../features/matrix/totals-subtotals.md) |
| Matrix numbers | `$` only on money; the `%` code only on computed variance %; model percent measures keep the model format | [`MX-NUM-01`](../features/matrix/number-scaling.md) |
| Matrix colour | Red/green variance (light fills where useful); bars on the lead measure; light-to-dark heatmap scale; colour rules only on engine ids | [`MX-CF-01`](../features/matrix/cf-rules.md), [`MX-CF-02`](../features/matrix/cf-data-bars-color-scales.md), [`MX-CHART-01`](../features/matrix/inline-charts.md) |
| Hierarchies | Bold parent rows, 16 px indent, plus/minus expand/collapse icons on every multi-level row set, at most three levels | [`MX-HIER-01`](../features/matrix/manage-hierarchies.md) |
| Text boxes | Padding off; height at least font × 1.35 + 9 px per line | [`CV-ELEM-01`](../features/canvas/text-shapes-images.md) |

## Editor-only today

Plan these as user finishing steps unless the feature file has since been
upgraded:

- Colour scales or rules on extra Matrix measures whose ids the builder
  assigned; they paint only on engine ids taken from a user-saved Matrix.
- Collapsed default hierarchy levels: rows open fully expanded, and the
  expand/collapse icons let readers close them.
- Sorting by a column other than the cloned lead measure, and Top N with
  Others ([`MX-SRT-03`](../features/matrix/top-n.md)).
- A first colour scale, in-cell bar or sort on a new Matrix kind: after the
  user saves one, it becomes cloneable.
