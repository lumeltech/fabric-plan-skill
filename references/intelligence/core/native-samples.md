## Contents

- [Why native samples](#why-native-samples)
- [Encoding status](#encoding-status)
- [User-confirmed feature availability](#user-confirmed-feature-availability)
- [Capture workflow](#capture-workflow)
- [Recording an encoding](#recording-an-encoding)
- [Sample library layout](#sample-library-layout)
- [Merged companion-library evidence](#merged-companion-library-evidence)
- [Additional details](#additional-details)

<!-- Core reference for the `fabric-plan-skill` skill. Used by authoring whenever a feature file is not `encoding: verified`. -->

# Learning feature encodings from native samples

## Why native samples

The official Plan definition documents the containers (`properties.json`,
`visualState`, assignments) but not the meaning of every engine setting inside
`visualState`. Feature JSON must come from a definition saved by the product
UI, not from labels in documentation.

The [upstream/public schema references](upstream-references.md) now document
Intelligence's page wrapper and visual array as well as shared contracts.
They establish container structure, not isolated engine-setting values.
Retain observed flat native shapes where present, record schema/readback
discrepancies, and do not upgrade feature encoding confidence from a source
link or schema alone.

## Encoding status

Every feature file declares one of:

| `encoding` | Meaning | May author without a new sample? |
|---|---|---|
| `verified` | Exact keys and values captured from a native export and checked at runtime | Yes |
| `observed` | The `visualState` group/keys exist in a native export, but the values for this feature were not isolated | No — run the capture workflow, or copy the whole group from a working visual |
| `unverified` | Documentation or screenshot presentation evidence only; no isolated encoding | No — capture first |

## User-confirmed feature availability

On **2026-11-08**, the user confirmed that the features in the preceding
34-item Inforiver-reference inventory are available in Fabric Plan
Intelligence Sheets, except for these three retained-reference entries:

- [Number display settings](../features/matrix/number-settings.md): retain
  the legacy citation only for its previously uncovered options; existing
  Fabric Plan signed-display coverage is unchanged.
- [Performance-mode drill down/roll up](../features/matrix/performance-mode-drill.md).
- [Variables](../features/matrix/variables.md).

For the other **31 features**, this confirmation replaces the Inforiver
documentation citations as availability evidence. Their existing feature
details remain applicable; entries formerly marked `Inforiver-only` become
`IS-Confirmed`. The affected feature IDs are:

`MX-AGG-01`, `MX-BLEND-01`, `MX-CHART-04`, `MX-COLW-01`, `MX-EXPL-01`,
`MX-FMT-02`, `MX-FMT-03`, `MX-FMT-04`, `MX-HIER-02`, `MX-INCOL-01`,
`MX-MISC-01`, `MX-PIN-01`, `MX-SHOW-01`, `MX-SIGN-01`, `MX-SRT-02`,
`MX-TB-01`, `MX-TPL-03`, `MX-TROW-01`, `CH-CALC-01`, `CH-LIB-13`,
`CH-LIB-19`, `CH-NOTE-01`, `CH-SPLIT-01`, `SF-DATE-07`, `SF-DISP-01`,
`SF-PLAY-01`, `KPI-CONT-01`, `TB-CHART-01`, `TB-SUM-01`, `CV-LAYER-01`,
`CV-NAV-01`.

This is user-confirmed availability, not first-party documentation, a native
capture or a runtime test. It does not upgrade `encoding`, verify exact UI
paths/property values, or enable authoring without the required native sample.
Preserve feature semantics and serialized identifiers such as `INFORIVER`.
Existing semantic-model-only, module-boundary, permission and writeback gates
remain in force; availability is not authorization to change data.

### Documentation-derived feature details

The user also confirmed that the legacy product documentation describes the
same Intelligence Sheet features. Feature descriptions, use cases, UI paths and
constraints for features that lacked them were completed from that
documentation without citing it. Fabric Plan documentation takes precedence
where both exist. Ribbon and menu labels can differ in Fabric Plan (for example
Matrix, Format and Data ribbons); confirm the label in the UI before giving
step-by-step instructions. Documentation never establishes Plan JSON keys,
so these details do not change any `encoding` value or the capture gate.

## Capture workflow

### Live capture status

A live `getDefinition` export of a UI-created test Plan (default visuals plus
one configured drill-through, 2026-11-08) refreshed the observed encodings of
the most-used card, chart, Super Filter, Matrix, table, text, navigation and
drill-through features; see `assets/encoding-ledger.json`. It also showed that
some groups, such as donut `pieChartSettings`, are absent until a setting
changes. Insight charts (`KPI-CHART-01`) and chart conditional formatting
(`CH-CF-01`) had no keys in default visuals. Store capture exports outside the
skill; record only generic keys in feature files.

A report build on 2026-11-11 added three kinds of evidence, recorded in the
ledger:

- **User UI saves read back from the live report**: a Matrix CF rule (engine
  ids and the native rule object), a page-navigation button destination, a
  slicer default selection and a chip gap. These isolate exact values.
- **Read-only exports of other UI-saved Plans in the same workspace**:
  multi-level hierarchy filters, list and dropdown hierarchy views, text-area
  and numeric filters, pop-up settings and floating/hidden toolbars.
- **User-confirmed rendering** of the published report across review rounds.

A multi-page report build on 2026-11-20 used a pilot page as the evidence
source ([dashboard build playbook](../design/dashboard-playbook.md)): the user
polished the published Overview in the editor, and its readback supplied a
Matrix colour scale (`targetValue` rule), in-cell bars, a column sort, a total
column and label, and tile-chip formatting. Cloned to four new pages, they
rendered. The same build found at runtime that page ids follow sheet creation
order (`CV-ELEM-02`), colour rules paint only on engine ids (`MX-CF-02`), extra
measure headers need `customName` (`MX-VAR-01`), a `%` code on a model percent
measure doubles the sign (`MX-NUM-01`) and Explore Model writes a scratch sheet
(`CV-EXPL-01`). Details are in the ledger.

Features whose primary encoding was both captured and confirmed at runtime are
now `verified` (for example `SF-FACET-01`, `SF-FEAT-05`, `KPI-CARD-01`,
`KPI-CHART-01`, `KPI-VAR-01`, `MX-CF-01`, `MX-NUM-03`, `CV-ELEM-02`,
`CV-LAYOUT-01`, `CV-FILT-01`); each feature file states which variants are
still only observed.

1. In Fabric Plan, create (or copy) a small test plan bound to the same model.
2. Add the visual with default settings. Save. Export the baseline:
   `management` → `getDefinition` → `python -I scripts/plan_def.py unpack _build/base.json _build/captures/<feature>/before`.
3. Change **only** the target feature in the UI. Save.
4. Export again into `_build/captures/<feature>/after`.
5. Diff: `python -I scripts/plan_def.py diff _build/captures/<feature>/before _build/captures/<feature>/after`.
6. Ignore churn (timestamps, `filterContextHash`, ids that the UI regenerates).
   Keep the minimal key set that changed.
7. Re-apply only that key set to a fresh copy of the baseline, publish to the
   test plan, reopen in the UI, and confirm the feature renders. Only then mark
   it `verified`.

## Recording an encoding

Update the feature file:

- Set frontmatter `encoding: verified` (or `observed`).
- List only documentation URLs in `sources`. Record native evidence as generic
  paths and keys in **Definition encoding** and in the ledger; never add report,
  sample-file or capture paths, IDs or model field names to feature files.
  Preserve the three Inforiver exceptions; do not restore superseded citations
  merely because native encoding is uncaptured. Availability confirmation
  does not change encoding confidence or required serialized engine names.
- Fill **Definition encoding** with the JSON path and a minimal fragment, e.g.

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.numberFormatting
Fragment: { "scalingFactor": "<value>", "noOfDecimal": 1 }
Evidence: before/after live capture (details in the ledger)
```

- Add a row to `assets/encoding-ledger.json`.
- Re-run `python -I scripts/build_index.py` and `python -I scripts/lint_references.py`.

Strip names, emails, and tenant-specific IDs from stored fragments.

## Saved-definition evidence

Feature files record generic paths and keys observed in saved Plan
definitions; they do not point to sample files. Copy same-kind visuals from a
current native readback (an existing plan or a UI-created test Plan) into the
working definition. Observed evidence is not verified: no before/after capture,
publish, or reopen was performed. A disabled/default setting proves a key
exists, not that the corresponding feature was active.

Charts often contain JSON strings at
`/properties/visualState/hiddenProperties_!!!_<group>`; Matrix and Super Filter
groups are objects in the inspected examples. Preserve both levels of encoding.
Use `INFORIVER`/10 for the saved Matrix, `INFORIVER`/15 for the table and
`ANALYTICS_PLUS`/50 for saved charts and cards; `PowerBI` remains the semantic-field source enum, not a visual family.

User-supplied screenshots are feature references when the live source is
inaccessible. Screenshots cannot
prove filter synchronization, tooltip-page wiring, drill-through propagation,
writeback, or exact property values. Their presentation observations must not
be promoted to `verified` encodings.

## Capture workspace layout

Keep captures in the working folder, not in the shipped skill; exports can
contain model field names and tenant IDs.

```text
_build/captures/
  <feature-id>/
    before/   decoded baseline parts
    after/    decoded parts after the single UI change
    diff.txt  plan_def.py diff output
    notes.md  product build, date, what was clicked
```

An earlier embedded Planning-grid readback describes that grid only. It is not
standalone reporting Matrix or chart evidence.

## Merged companion-library evidence

Feature, design, core and IBCS files may contain an **Additional details**
section merged from a companion Intelligence authoring library that studied
saved native Plan exports and recorded user corrections. These sections are
additive: they never override the guidance above them in the same file, the
frontmatter `encoding`, or the capture workflow in this file. Each merged
statement about native keys, values, shapes or runtime behavior carries a tag:

| Tag | Meaning | Authoring rule |
|---|---|---|
| `[saved]` | Seen in saved native Plan exports; not isolated by a before/after capture in this skill | Treat as `observed`: copy the whole group from a same-kind native readback; never hand-write it from the note |
| `[confirmed]` | User correction, or rendering/readback the user confirmed in the companion work | Apply as guidance; exact JSON still follows the feature's `encoding` |
| `[open]` | Meaning, range or runtime effect unresolved | Capture before relying on it |

Merged statements are generic: they carry no report names, IDs, dates, sample
values or model field names. Where a merged statement differs from guidance
above it, the existing guidance wins until a native capture resolves the
difference. Companion defaults that differ from this skill's design rules are
recorded only as optional guidance.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Matching native donors and reference peers

- Match on the full identity signature: root registration, numeric owner
  `visualType`, owner `chartType`, template ID, template chart type, renderer
  type and the active subtype or mode (for example date, facet or pop-up
  state). Dormant settings of an inactive mode must not create false peers
  [saved].
- Flags alone do not establish an active mode: saved filters carried
  date-range activation without date bindings, and variance activation with a
  single measure reference [saved]. Inspect bindings and registration before
  declaring a mode functional.
- Registration arrays can repeat field context, including capitalized
  `Category` entries without a top-level bucket [saved]. Compare multiplicities
  and unique binding sets, and keep extra context distinct from missing
  bindings.
- Keep collections family-specific: Super Filter `cfSettings.rules` are not
  Matrix `cfProps`, chart `hiddenProperties_!!!_cfProps` is not a Matrix rule
  collection, and a table owner does not need Matrix collections [saved].
- A saved Matrix can omit both conditional-format collections [saved]; check
  presence, master settings and individual rule flags separately.
- Preserve a user-confirmed UI identity that conflicts with the exported root
  identity, and exclude that visual from donor comparisons rather than
  normalizing it [confirmed].
- An unmatched peer is not evidence that a feature is unsupported.

### Frequencies are not defaults

- Count deduplicated owners and repeated instances separately, and give both
  visible-owner and all-owner denominators; a hidden duplicate sheet is not an
  independent preference.
- Saved-value frequencies, including disabled settings, are persistence
  counts, not factory defaults or user-edit rates. A reference gallery is not a
  paired default-versus-customized experiment.
- Donor styling, canvas size and spacing stay reference evidence; they never
  override this skill's design rules or the session design.

### Capture refinements

When isolating one property with the capture workflow above:

- Record the product build, visual family, active mode, exact UI label and
  whether the change is a one-report choice or a standing preference.
- Capture the setting panel and the rendered result at the same zoom, filters
  and viewport as the export.
- An off/on/off sequence helps separate an active property from incidental
  save-time state; record unchanged consumers as negative controls.
- If one save contains several unrelated changes, label the attribution
  ambiguous instead of claiming causality. No-change and unexpected-target
  outcomes are evidence, not failures to hide.

### Registration discrepancy

- Companion saved exports register the table owner (`visualType` 15) as
  `TABLE`, distinct from `INFORIVER`/10, whereas the guidance above names
  `INFORIVER`/15; the guidance above wins until a native capture in this skill
  resolves the registration [open].

### Recording a new lesson

1. State the business principle and why it matters; record the concrete
   observed configuration separately from the general pattern.
2. Name the evidence source (user requirement or correction, saved
   definition, API response, static check or native UI behavior). Keep a
   desired behavior, a saved native schema, a locally generated
   implementation, an observed runtime result and an unresolved hypothesis
   distinct, and keep the reason for a user correction with it.
3. Keep a counterexample or failed hypothesis when it prevents a repeated
   mistake.
4. Reconcile the lesson with earlier guidance, mark what it supersedes and
   update the owning section instead of appending only the newest finding.
5. Keep product-build, environment and item-identity assumptions visible
   where they affect reuse; exclude credentials and personal identifiers.
6. Never record one implementation route as the only supported pattern.

### Donor hygiene

- A definition this skill generated proves persistence after a clean
  readback, not native UI encoding; keep it apart from UI-saved donors unless
  the capture workflow above has verified it.
- An enabled saved setting that targets a field the visual does not bind,
  such as a conditional-format rule on an unassigned measure, is a defect
  candidate, not a pattern [saved]. Do not copy it; under read-only learning
  authorization, record it instead of repairing the live report.
- In a user's corrected save, separate deliberate design changes from
  incidental churn: case-only colour changes, 1 px internal refits, editor
  metadata, newly saved disabled settings and fonts of inactive chart
  families are not design features or new defaults [saved].
