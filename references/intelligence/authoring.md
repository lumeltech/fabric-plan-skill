## Contents

- [Must/Prefer/Avoid](#mustpreferavoid)
- [Inputs and working folder](#inputs-and-working-folder)
- [Workflow](#workflow)
  - [Step 1 — Load the contract](#step-1--load-the-contract)
  - [Step 2 — Field closure](#step-2--field-closure)
  - [Step 3 — Start from a native definition](#step-3--start-from-a-native-definition)
  - [Step 4 — Sheets](#step-4--sheets)
  - [Step 5 — Visuals](#step-5--visuals)
  - [Step 6 — Features](#step-6--features)
  - [Step 7 — Validate](#step-7--validate)
  - [Step 8 — Hand off](#step-8--hand-off)
- [Additional details](#additional-details)

<!-- Mode reference for the `fabric-plan-skill` skill. Loaded on demand from `SKILL.md` when the request matches the `authoring` mode. -->

# fabric-plan-skill authoring mode — Plan definition authoring

> **Required continuation.** After this file, open
> [authoring-part-02.md](authoring-part-02.md) (visual recipes, ID
> generation, and edit patterns).

Authoring turns an approved spec + `Design Brief:` (or a focused edit request)
into decoded Plan definition files and validates them. It never publishes.

## Must/Prefer/Avoid

### MUST

- Read `core/definition-structure.md` and `core/invariants.md` before the first edit.
- Check the relevant [public-contract sources](core/upstream-references.md).
  Preserve the part's schema and native wrapper shape; do not flatten the
  documented Intelligence page/visual containers or substitute another module's
  `properties.json` schema. Structural checks are not complete schema validation.
- Follow [module boundaries](core/module-boundaries.md): this release consumes
  only model-backed data and native visual calculations over it. Do not bind
  other modules' measures or add embeddings; preserve existing foreign parts.
- Apply the brief's [session design](design/session-theme.md) snapshot: preserve
  palette, typography, buttons, navigation and page-role geometry across reports.
  Implement Help and Info placements/actions or document an explicit opt-out;
  capture missing native settings rather than leaving inert controls.
  Before completion, compare rendered tokens/layouts with the approved profile
  and exercise both controls, close/back and filter preservation. If runtime
  access is unavailable, report these checks as pending, not passed.
- Treat user-supplied screenshots or report links as feature references only:
  map visible elements to feature files and bind roles to the live field
  registry, never to sample field names or figures. Implement the approved
  user/session design, including custom choices; reproduce a reference
  appearance only when requested. Screenshots prove presentation, not
  encodings or runtime behavior.
- The [legacy-report inspiration library](design/report-inspiration.md) is
  explicitly authorized design input. Implement only its resolved choices in
  the approved brief; use Fabric Plan native visuals, approved logo assets and
  captured navigation/image settings, not copied Power BI internals or host chrome.
- Implement each sheet's `super_filter_layout` through its approved placements
  and captured native settings; the brief field is not a Plan JSON key.
  Validate filter expansion, clipping, selected-value visibility, clear/reset,
  keyboard access and declared scope/sync. Do not force a top band or left rail.
- For Super Filters, use the relevant [slicer feature files](features/slicers/_index.md)
  to capture per-category style, panel composition,
  date/range semantics, measure/CF/variance/rank bindings and toolbar actions.
  Verify cascade separately from visual interactions/sync; static examples do
  not verify popup, paste, saved filters or playback. Do not upgrade encoding
  confidence or write guessed property keys from screenshot captions.
- Work on **decoded** parts in a local folder (`_build/def/`), produced by
  `python -I scripts/plan_def.py unpack`.
- Resolve every semantic field against `_brief/field-registry.md`.
- For monthly categories, prefer an existing Month field over a start-of-month
  date when it represents the intended grain. Inspect type and sort order;
  retain year context or use an existing year-month key for multi-year scopes.
- Inspect existing measure expressions as well as descriptions before reusing
  them for another scenario: a measure that forces Actual internally will not
  become Budget merely by changing its bucket or filter.
- Use native KPI variance icons and sparklines (`KPI-VAR-01`, `KPI-CHART-01`);
  do not create SVG/image-data measures to render them. Capture missing native
  settings instead of substituting custom graphics.
- Read its table/column/measure descriptions and semantic decisions before
  binding it or calculating a derivative; names alone are not business context.
  Give every new measure a meaningful description. For visual measures, record
  it in the report spec and use native description metadata only where supported;
  never invent a Plan JSON key. Model measures require persisted descriptions.
- Open the feature file for every feature used. Write only `verified`
  encodings directly; for `observed`/`unverified` ones, run the native-sample
  workflow (`core/native-samples.md`) or copy the full settings group from a
  working native visual.
- For Matrix calculations or calculated CF flags, read
  [Matrix formula syntax](features/matrix/formula-syntax.md). Use the reporting
  subset of the Fabric Plan formula reference, not Planning-only functions;
  confirm runtime support and capture stored formulas separately.
- Treat display sign, arithmetic sign and favorable/unfavorable direction as
  separate settings. Reconcile profit formulas after any row sign inversion;
  test overspending and underspending explicitly rather than trusting a
  stored inversion flag or green/red appearance.
- Keep every sheet ID, visual ID, inserted measure ID and each sheet's numeric
  navigation id (creation order, `CV-ELEM-02`) in `_build/id-registry.json`.
- Run `python -I scripts/plan_def.py validate _build/def --registry <live registry>` after
  each logical batch, adding `--baseline _build/readback` for an existing plan. The
  Data pane field check is part of it and is never skipped.

### PREFER

- Clone native objects (a saved slicer, Matrix, chart, KPI) and change
  bindings and settings, rather than composing objects from scratch.
- For a multi-page report, finish one pilot page, let the user polish it in
  the editor, then clone the remaining pages from the user-saved readback
  ([dashboard build playbook](design/dashboard-playbook.md)).
- Small batches: one sheet or one visual family at a time.
- Keep existing IDs and unrelated parts untouched when editing.

### AVOID

- Publishing or calling Fabric write APIs (that is `management`).
- Changing `semanticModelReference` unless the user asked to rebind.
- Writing to the semantic model (only `model-measures` may, with permission).
- Editing Planning, PowerTable, InfoBridge, or cube parts; their owning skills
  are not integrated yet. Preserve them byte-for-byte and report dependencies.
- Guessing enum values, `visualType` codes, or `chartType` strings.
- Power BI native visuals or `chartType` values that are not in the
  Intelligence chart library (`features/charts/`).

## Inputs and working folder

```text
_brief/report-spec.md          approved spec (greenfield)
_brief/field-registry.md       model fields (closure source)
_build/source.json             getDefinition result or template payload
_build/def/                    decoded parts (edit here)
_build/readback/               untouched decoded readback of an existing plan (validate --baseline)
_build/id-registry.json        sheet/visual/measure/filter IDs
_build/captures/<feature>/     native before/after captures (not shipped)
_build/payload.json            packed payload for management
```

`_build/source.json` comes from:

- an existing plan → management `getDefinition`;
- a team template plan (recommended for greenfield) → `getDefinition` of the template;
- a UI-created test Plan readback with same-kind visuals (see
  [native samples](core/native-samples.md)); copy them into the working
  definition and never edit capture folders.

## Workflow

### Step 1 — Load the contract

Read `_brief/report-spec.md` YAML and the `Design Brief:`. For a focused edit,
write a minimal brief in working notes (sheet, visual, change, feature IDs).
If `ibcs: true`, load `references/intelligence/ibcs/ibcs-rules.md`.

### Step 2 — Field closure

Check source provenance before model-name lookup. If the requested measure is
from another module, report **module integration pending**; do not manufacture
a model replacement or relax closure checks.

List every field the brief binds (rows, columns, values, category, slicer
fields, CF measures, sort measures). Check each against the registry by exact
name, including table prefixes. For a missing measure:

1. Build it in Fabric Plan if a visual measure can compute it
   (`MX-CALC-02`, `MX-CALC-01`, `MX-QF-01`, `MX-VAR-01`, `MX-AGG-01`, `CH-CALC-01`, `KPI-FMT-01`).
   For Matrix logic, check `MX-FML-01`, including reporting time functions,
   before treating the calculation as a model gap.
2. Otherwise, if `model_measure_permission` is `ask-per-measure`, switch to
   `model-measures` for that measure (its own approval), then refresh the registry.
3. Otherwise stop and report it as a model gap.

### Step 3 — Start from a native definition

```bash
python -I scripts/plan_def.py unpack _build/source.json _build/def
python -I scripts/plan_def.py inspect _build/def
```

`inspect` lists sheets, visuals, visual types, bucket fields, and geometry.
Record existing IDs in `_build/id-registry.json`.

### Step 4 — Sheets

For each new Intelligence sheet:

1. New `recordGuid` (UUID v4). Add to `definition.json → sheets[]` with
   `sheetType: "REPORTING"`, `displayName`, `isHidden: false`, and an empty
   `workloadItemEntityVisuals` list (filled in Step 5).
2. Create `sheets/<id>/sheet.json` by copying a native REPORTING `sheet.json`
   and resetting: `pageLevelFilterAssignments: []`,
   `reactiveVisualProperties: []`, `visualGroupMap: {}`,
   `sourceVisualsMeta: {}`, `assignmentColumnMap: {}`; set
   `canvasStyle.dimension` and background from the brief.
3. Copy `commentSettings.json` from the native REPORTING sheet with a new
   `recordGuid` if the native sample has one.

For an existing sheet, edit in place.

### Step 5 — Visuals

For each placement in the brief:

1. Pick a native source object of the same kind (see
   `authoring-part-02.md` § Visual recipes).
2. Allocate a visual GUID and a sheet-local `originEntityId` (next integer as
   a string, unique within the sheet).
3. Create `sheets/<sheetId>/visuals/<visualId>/properties.json` from the
   source; set `position`/`dimension` (normalized, from the brief's region
   conversion), `layerProperties` (name, order), `visualStyles`.
4. Bind fields in `pivotAssignments` (and `superFilterAssignments` for slicers)
   using the registry names. Copy companion keys exactly from the native object.
5. Copy `writeback.json` only if the native source of that kind has one.
6. Register in `definition.json → sheets[i].workloadItemEntityVisuals` with
   the native `visualType` name (`SUPER_FILTER`, `PLANNING`, …) and
   `isEmbedded`.
7. New embedded Planning/PowerTable placements are blocked in this release.
   Preserve existing registrations and `reactiveVisualProperties` unchanged;
   their documented encoding is context, not permission to add them.

### Step 6 — Features

For each feature ID on the placement, open its file and apply its
**Definition encoding** inside `properties.visualState` (or the stated path).
Record in `_build/feature-log.md`: feature ID, visual ID, encoding status,
evidence path.

### Step 7 — Validate

```bash
python -I scripts/plan_def.py validate _build/def \
  --registry _build/info-columns.json --registry _build/info-measures.json \
  --baseline _build/readback   # existing plans only; omit for a new plan
```

The registry must come from the live model in this task (re-run the INFO
queries in `core/model-inspection.md` if it is older). Every Data pane field
must resolve; a missing field is an error, not a warning. A mixed-source plan
also lists each From Sheets binding as a warning; report them to the user. With
`--baseline`, any added, removed or changed cross-module binding is an error
(see [cross-module blend](core/cross-module-blend.md)).

Fix every error. Warnings need a written reason in the feature log. Then pack:

```bash
python -I scripts/plan_def.py pack _build/def _build/payload.json
```

### Step 8 — Hand off

Report: files changed, sheets/visuals added, features applied with encoding
status, validation result, Data pane field check result (fields checked / missing), unverified items that need a UI check after
publish. Switch to `management` only if the user asked to publish.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- **Scope.** A narrow repair keeps a still-valid approval; do not force an
  unrelated redesign. If the approved scope turns out to need material page,
  model or connection changes, stop and return to `discovery` for re-approval.
- **Inventory before a sheet edit.** Inventory `definition.json`,
  `planProperties.json`, the sheet declaration, its owner parts and companion
  state. Keep sheet type, visibility, order, grouping, commentary and
  navigation consistent. Besides the visual folder and its registration, add
  the shared filter, variable and interaction registrations a same-kind
  readback uses.
- **Identity before appearance.** Read the canvas scaling unit and each
  visual's family (registration plus owner `visualType`) before geometry or
  template edits (visual identity).
- **Recheck context.** After any filter or binding change, recheck period and
  scenario comparisons, headings and subtitles in the new context; a visually
  improved save is not proof of financial comparability [confirmed].
- **Complete parts.** Never rebuild a sheet or visual from its visible field
  assignments; measures and properties live in companion structures. Reduced
  copies produced empty sheets [confirmed].
- **New visual parts.** Keep the donor's complete envelope
  (definition structure);
  treat a `no $schema` warning from `validate` on a new visual part as a
  defect to fix.
- **Placement.** For a new visual on a populated sheet, follow the
  free-rectangle procedure in invariants.
- **Step 4 difference.** The companion library keeps `reactiveVisualProperties`
  absent when a cloned standalone native sheet omits it and warns against
  initializing it as `{}`; a blank-canvas report after such an addition was
  never attributed. Step 4's reset list wins until a capture resolves this
  [open].
- **Reporting.** Report results with the layers and statuses in
  validation layers, and log business-critical
  values with the metric contract.
