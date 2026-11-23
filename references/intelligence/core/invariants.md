## Contents

- [Field closure](#field-closure)
- [Identifier registries](#identifier-registries)
- [Three-part filter state](#three-part-filter-state)
- [Geometry](#geometry)
- [Serialization](#serialization)
- [Cloning native visuals](#cloning-native-visuals)
- [Removing visuals](#removing-visuals)
- [Formatting gotchas](#formatting-gotchas)
- [Volume](#volume)
- [Security](#security)
- [Evidence classes](#evidence-classes)
- [Additional details](#additional-details)

<!-- Core reference for the `fabric-plan-skill` skill. Distilled from fabric-plan-authoring (SKILL.md invariants, intelligence-layout.md, Fabric-Planning-Brain failure library). -->

# Authoring invariants

These rules hold for every Intelligence Sheet definition. Each one exists
because breaking it produced a real runtime failure.

## Field closure

- Apply the current [semantic-model-only release gate](module-boundaries.md).
  Cross-module blending is supported by the product but not enabled here.
  Never treat a foreign measure as a missing model field or bypass validation
  for it; preserve existing bindings and report the unsupported source.
- Reference only semantic-model fields that exist in `_brief/field-registry.md`
  (exact table, column, and measure names, including prefixes such as
  `[Dim] ` / `[Fact] `).
- Never rename, pluralize, or guess a measure from a business term.
- If a measure is missing: build it in Fabric Plan as a visual measure when
  possible; otherwise create it with `model-measures` only if the user allowed
  model edits and approves that specific measure; otherwise report the gap.
- Never edit existing model objects. Only measures annotated
  `fabricPlanIntelligence.createdBy` may be edited, each with fresh approval.
- Before validation, list every semantic reference in the definition and check
  it against a registry captured from the live model in this task
  (`plan_def.py fields --registry`; `validate` requires it). An unresolved field produces "Semantic model updated
  – some fields used in this sheet are no longer available" at runtime.

## Identifier registries

Sheet IDs, visual IDs, `originEntityId`s, inserted measure IDs (19 digits),
filter IDs (`filter_<unixms>_<suffix>`), bookmark IDs and query IDs are
**separate namespaces**. Keep one registry per namespace in the working folder
(`_build/id-registry.json`).

- Generate new GUIDs for new sheets and visuals; keep existing ones on edit.
- Never globally search-and-replace GUIDs in a definition.
- Formulas reference inserted measures as `M_<19-digit id>`, never by label.
- Captured calculated-row formulas use `R_<native row ID>` instead. Track row
  identities separately and resolve operands in the target Matrix; neither
  display labels nor another report's IDs are valid substitutes.
- `originEntityId`: a UI save stamps every visual with its origin sheet's
  numeric id (creation order, unchanged when sheets move) and makes
  `preVisualId` a plan-wide counter. Authored definitions may instead use unique sheet-local integers;
  both rendered, and `plan_def.py validate` accepts both.
- Matrix `manage_measures[].id` and `rowDimensions[].id` are engine-assigned
  numeric strings. The engine replaces authored ids on an edit-mode load and
  can re-key them in a later session; conditional-formatting rules must use
  the current ids, so read them from the newest readback (see
  [CF rules](../features/matrix/cf-rules.md)).
- Button `pageDestinationId` is the target sheet's 1-based position; reordering
  sheets changes every destination.

## Three-part filter state

| Part | Purpose | Failure when missing |
|---|---|---|
| Assignment | Binds the field to the slicer/visual bucket | Empty or invalid visual |
| Registration | Makes the field known to the filter pane/query state (`filterHiddenSettings.isRegistered`, page/visual filter assignments) | Slicer shows the field but its filter card is blank |
| Selection | Stored members/range/All state | Unexpected initial scope or no filtering |

Assignment alone was proven insufficient. Copy the full native trio from a
working slicer. A slicer's selection or default lives in
`visualState.slicerFilterAssignments` (VALUES include, captured from a UI
save); `superFilterAssignments[].filter` restricts the slicer's own member list
and is not the selection.

Extra visual filters on fields not bound to a visual bucket are not default
bound-field filters. Copying slicer defaults with `isDefault: true` caused a
later field edit to regenerate defaults and drop the extra filter. A native
extra-filter capture omits top-level `bucketId`, `isDefault`, `isDaxMeasure`
and `isDefaultMeasure`; its field pivots use `bucketId: "Category"`, with
`configuration.selectAllState: "UNSELECTED"` and VALUES include state.
Copy the full matching extra-filter object, not just these flags. After UI
field changes, save/read back and reconcile the filtered value to confirm
that scope survived.

## Geometry

- All placement values are **normalized** 0–1 fractions of the canvas.
- Owned visuals: `properties.position` + `properties.dimension`.
- Embedded visuals: the hosting sheet's `reactiveVisualProperties[]`. If the
  embedded visual also carries owner placement, both must agree — an embedded
  grid once rendered at the origin `(0,0,0.3,0.4)` over the header because only
  one copy changed.
- Keep every rectangle inside `[0,1]`, positive size, no unintended overlap,
  consistent gutters. `scripts/plan_def.py validate` checks this.

## Serialization

- Parse each JSON part once; never double-encode (`"[object Object]" is not valid JSON`).
- Numeric settings that natively use wrappers keep them: `{"Static": 100}`, not `100`.
- Preserve the form of `visualState` (object vs string) found in the source.
- Preserve unrelated parts byte-for-byte (cube, InfoBridge, Planning sheets).
- Remove audit identity fields (user names, emails) from portable examples.
- `hiddenProperties_!!!_<group>` values are JSON strings in most charts but
  objects in some saved visuals of the same family; preserve each group's
  representation individually.
- An editor save converted object-valued groups to JSON strings and wrote
  hundreds of default keys into charts and KPI cards without changing
  appearance [saved]. When diffing readbacks, parse strings and compare
  values; filter `preVisualId`, layer-order resequencing and 1–2 px
  auto-layout before calling a change a user design edit.

## Cloning native visuals

When a visual is cloned from another report or sheet, rebind fields by exact
id replacement and reset what belongs to the source:

- Caches the editor fills on load: slicer `embeddedSuperFilter`,
  `filterContextProperties`, chart `filterContextSetting` (`hash`,
  `filterContextKey`, `filterContextJson`) and Matrix `filterContextHashMap`.
- Stored selections and presets: `slicerFilterAssignments`,
  `filterHiddenSettings.categorySelectAllState`, `selectedDatePreset` (a native
  date slider ships with "Last Year" preselected) and `selectedPreset`.
- Measure-keyed style maps and labels that name fields absent from the target
  registry; rename leftover template captions.
- Matrix conditional-formatting rules: rebuild them against the target
  Matrix's engine ids.

A stale stored selection on another field produced "No data" visuals.

## Removing visuals

`updateDefinition` does not delete a visual that the payload omits: the
service kept its parts and its `definition.json` registration, so removed
filters reappeared over their replacements. To retire a visual:

1. Prefer reusing its id for a replacement of the same family (the whole
   `properties.json` is replaced).
2. Otherwise re-emit it hidden and inert: `layerProperties.layerProperties.isHidden:
   true`, a `Retired - …` layer name, stored selections cleared, shrunk and
   stacked behind an opaque element.
3. Or ask the user to delete it in the editor, and keep its parts from the
   last readback that still had it (see below).

### After the user deletes visuals in the editor

After a user deleted two visuals in the editor, every complete update that
omitted them failed with `ImportFailed` "Sheets could not be imported.
Event-trigger replacement rollback failed" (not retriable), and nothing
persisted. That held for edited payloads, an unchanged round trip of the live
definition, a retry with the report closed and a payload that carried the live
`dataInput.json` parts. Re-emitting both visuals hidden under their original
ids (`properties.json`, `writeback.json` and the `definition.json`
registration, copied from the pre-deletion readback) made the next update
persist; it reported `UnknownError` but read back complete (`native-export`).
Keep re-emitting such visuals in every later update. Whether the block clears
on its own is unverified, so never omit them to test it on a user's report.

## Formatting gotchas

- KPI card values rendered as `147.0undefined`: turn KPI **Number Format off**
  (copy the native saved representation).
- "Auto" number scaling and `scalingFactor: "autoFixed"` are different settings.
- Row/column grand totals are not measure aggregation; configure separately.
- Time axes need an explicit ascending category sort
  (`hiddenProperties_!!!_sorting` `{"sortBy":"category","sortType":"ascending"}`);
  the template default `reset` drew months newest-first.
- Changing a currency prefix does not convert values; state the source currency.

## Volume

- Grid visuals have a practical limit of about 1.2 million cells. Default
  slicers to a bounded period and one top-level member when the hierarchy is large.
- Prefer search, dropdown or hierarchy slicers for high-cardinality fields;
  give a dropdown room, because its open list can be cropped inside a short
  frame. Pop-up (min mode) slicers need the user's approval first.

## Security

- Never store bearer tokens, `MWCToken`s, cookies, or authorization headers in
  definitions, scripts, briefs, or logs.
- Correct field placement does not prove row-level security; test RLS with a
  restricted identity separately.

## Evidence classes

Record for every non-trivial property: `user-confirmed`, `native-export`
(observed in a saved definition), `documented` (official docs), `inferred`,
or `unverified`. Only `user-confirmed` and `native-export` justify writing a
value without a fresh sample.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.
For completion claims see validation layers.

### Field closure and rebinding

- Rebind table and field identities without touching measure-role enums: a
  rebind that replaced every `Measure` string corrupted `columnType` and
  `dataRoleType` [confirmed]. Both stay `Measure` throughout assignments and
  encoded filter state.
- A String column saved with `aggregationType: "count"` is an aggregated
  column, not a semantic measure or a distinct count [saved]. Keep model
  measures and aggregated columns distinct, and preserve absent aggregation
  keys.

### Identifiers

- Record an old-to-new map for every remapped identity; remap only what must
  change.
- Container membership in `layerProperties.layerProperties.groupIds` referenced
  the container's local `preVisualId`, not its GUID [saved]. Rebind membership
  through that namespace.
- Runtime counters (note counters, the plan-wide `preVisualId` counter) are not
  identities [saved]; never force them equal or derive IDs from them.

### Geometry

- The companion library also reports saved sheets with
  `canvasStyle.dimension.elementScalingUnit: "pixel"` and pixel-valued owner
  placements. A user-corrected native report confirmed this representation.
  Preserve the saved unit per sheet. `plan_def.py` normalizes pixel geometry
  using that sheet's positive canvas width and height for bounds and overlap
  checks; it does not rewrite the saved placements. Percentage sheets retain
  normalized 0-1 placements. Convert geometry explicitly when copying between
  sheets with different units [native-export, user-confirmed].
- Notes and markers keep their own coordinate spaces; do not apply canvas
  normalization to them [saved].
- Before updating placements together, establish which records describe the
  same instance: owner rectangle, `reactiveVisualProperties`, container layout
  and any mobile or responsive copy. Agreement is required within one instance;
  independent placements of one shared source are not copies [saved]. Check
  that mobile or responsive copies hold no stale placement.
- **New visual on a populated sheet.** Find a genuinely free in-bounds
  rectangle. If none fits, shrink the new visual while its content stays
  usable; ask before compacting existing visuals or changing the canvas. A
  card placed below the bottom edge to avoid reflow was rejected by the user
  [confirmed]. Hidden retained visuals and background shapes are not free slots.
- Declare intended overlap pairs (for example a header background behind its
  title and filters) and check that covered controls stay clickable. Permission
  to overlap does not make a covered control usable.

### Layout-manifest audit (optional)

An optional static audit compares rectangles extracted from the saved
definition; the manifest is a working file, not Plan JSON. Per page it holds
an ID, canvas width and height and a minimum gutter (16 by default); per
visual an ID, a reference rectangle, optional owner and reactive rectangles
with a flag requiring them to match, plus a list of allowed overlap pairs. It
checks:

- unique page and visual IDs, a positive finite canvas, nonnegative positions
  and positive sizes;
- every rectangle inside the canvas within a small tolerance (0.5 units by
  default);
- owner and reactive rectangles agreeing with the reference rectangle when
  present or required;
- no overlap except declared pairs, and horizontal and vertical gaps of at
  least the minimum gutter.

Extract the actual saved placements, converting fractions to pixels once.
Copying the intended rectangle into every field only proves the template is
internally consistent. A pass is one static layer; it does not confirm
coordinate interpretation, filter behavior, query success or rendering.

### Serialization

- Recursively expanded analysis copies are for inspection only; never deploy
  them.
- Optional groups can be absent rather than empty or null, as seen for chart
  annotation groups [saved]. Preserve absence, explicit `null` and explicit
  `false` separately; inspection tools must not materialize default objects.

### Cloning

- Clone the latest complete working preset and verify its active and locked
  template identity, not only visual labels; forcing an older preset undid
  user fixes [confirmed].
- Reconcile root references, companion ownership, every filter-context copy,
  source bindings and page/plan state together.

### Volume

- Hidden sheets and visual pagination do not necessarily reduce query
  cardinality [open].

### Security

- Scan distributable artifacts (payloads, logs, handoff packages) for tokens,
  cookies and copied authorization headers independently of JSON validity.
- Check that cached or materialized results and lookup metadata do not expose
  values a restricted identity must not see; record security checks
  separately from layout and import checks.

### Changing a reference

- Item-level identities (workspace, plan item, semantic-model item and
  connection) are separate namespaces too. Record them in the run state and
  never derive one from another or from a definition-level ID.
- Before changing a reference, locate its source and every consumer in the
  current definition (formulas, filters, sort and rank, conditional
  formatting, interactions, navigation and bookmarks), compare a same-kind
  native sample and update the consumers together.
- After an import or UI save, confirm that numeric identities still match the
  serialized references (see the Matrix engine ids and `originEntityId` rules
  above), then exercise the consuming visual before calling the reference
  fixed.
- Never fix a missing reference by renaming measures, stripping characters
  from unrelated metadata or substituting a generated identifier that no
  native save has shown.

### Rebinding scope

- Never rewrite every key with a generic name, such as each `connection`
  field; change only the binding the request targets.
- Root `appDBconnection` and the connection inside `semanticModelReference`
  are separate keys [saved]; removing or changing one is not a change to the
  other.

### Decoding scope

- Decode only the parts you inspect or edit and carry the rest through
  byte-for-byte. If a part does not decode as JSON, preserve its bytes and
  report it; never re-encode or drop it.

### Cell-limit estimate

- At the cell limit, reduce the selected scope and dimensional combinations.
  Estimate from the full expanded grid (valid leaf intersections × periods ×
  displayed measures, including subtotals), not from the visible rows.
