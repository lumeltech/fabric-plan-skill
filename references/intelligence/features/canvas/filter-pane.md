---
id: CV-FILT-01
name: Report, sheet, and visual filters (filter pane)
area: canvas
category: Interactions
status: IS-Confirmed
encoding: verified
visual: Sheet
sources:
  - https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/Intelligence/Properties/1.0.0/schema.json
  - https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/PlanProperties/1.0.0/schema.json
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data
---

# Report, sheet, and visual filters (filter pane)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Filters applied from the filter pane at report, sheet, or visual level.

## When to use

- Hidden scope rules; report-wide filters.

## UI path

Filter pane.

## Definition encoding

```text
Path: planProperties.json → workloadLevelFilterAssignments; sheet.json → pageLevelFilterAssignments, filterPanePosition
Report filter (runtime-verified): workloadLevelFilterAssignments[] = {filterLevel:"global",
  configuration:{…native single-select facet configuration…, locked:true, hide:false},
  filter:[{filterType:"VALUES", columnIds:[<field>], valuesFilter:[{id:[<member>],
  label:[<member>]}], valuesFilterApplicationType:"include", …}],
  pivotAssignments:[{bucketId:"Category", …}], id:"filter_<unix-ms>_<suffix>",
  position:"RIGHT"}; a locked report filter kept an actuals-only scope on every sheet.
Visual-level extra filters (runtime-verified): appended to a chart's
  superFilterAssignments without bucketId; NESTED_RANKING (Top N by a measure) and
  VALUES include bodies both worked (see core/invariants.md).
Evidence: decoded native readback; report filter totals reconciled to DAX and Top N /
  VALUES extra filters user-confirmed in a published report.
```

Sheet-level filters were not exercised; copy the whole group from a working
visual or run `core/native-samples.md` before writing them.

## Constraints

- Public page settings include `pageLevelFilterAssignments`,
  `filterPanePosition` (`LEFT`, `RIGHT`, `TOP`, `BOTTOM`) and
  `topPositionFilterExpandConfig`; retain the page wrapper described in
  [definition structure](../../core/definition-structure.md). These container
  contracts do not establish filter-selection encoding or runtime propagation.
- Remember the three-part filter state.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Distinguish workload, page, visual, synced-slicer, embedded-plan and
  planning-persistence scope; place each field in its actual owner rather than in
  every assignment list.
- [saved] A chart owner can keep only its own field registration in
  `superFilterAssignments`, while `visualState.embeddedSuperFilter.superFilterAssignments`
  holds compact `{"filter":[...]}` received-context entries without registration
  `id`, `bucketId` or `pivotAssignments`. These layers are not visual-level
  filters and need not match; validate each layer's own scope.
- [confirmed] User correction: a static Text label that states a period is not
  a selector. A locked page filter, a caption and a visible selector are three
  separate capabilities; do not substitute one for another.
- [saved] In the corrected report the selector's own selection was empty while a
  locked page filter kept the period scope. Inspect owner binding, own selection,
  received context and page scope separately, and recheck dated titles when the
  effective scope can change.
- Registration repair: list each visual's assigned fields and sources, choose each
  field's scope (visual, sheet, report or received context), keep intentional
  explicit filters, context dimensions and their selections, and add only missing
  compatible registrations: one default registration per assigned field, matched
  by stable field identity (table, column, type, source) rather than by label.
  Editor-filled context caches follow `SF-CTX-01`.
- Make a repair idempotent, so a rerun changes nothing and keeps every existing
  selection. A completed metadata audit is a persisted-definition check, not proof
  that filter cards appear or that selections filter data; reopen each visual and
  test.

## Related features

- `SF-FACET-01`
