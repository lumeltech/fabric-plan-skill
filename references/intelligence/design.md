## Contents

- [Must/Prefer/Avoid](#mustpreferavoid)
- [Topic Files](#topic-files)
- [Workflow](#workflow)
  - [Step 0 — Data-First Investigation](#step-0--data-first-investigation)
  - [Step 1 — Design Identity](#step-1--design-identity)
  - [Step 2 — Layout Choice](#step-2--layout-choice)
  - [Step 3 — Visual Selection](#step-3--visual-selection)
  - [Step 4 — Visual Configuration](#step-4--visual-configuration)
  - [Step 5 — Theme](#step-5--theme)
  - [Step 6 — Canonical Design Contract](#step-6--canonical-design-contract)
  - [Step 7 — Review and Handoff](#step-7--review-and-handoff)
- [IBCS (opt-in)](#ibcs-opt-in)
- [Gotchas](#gotchas)
- [Additional details](#additional-details)

<!-- Mode reference for the `fabric-plan-skill` skill. Loaded on demand from `SKILL.md` when the request matches the `design` mode. Structure adapted from microsoft/skills-for-fabric powerbi-report-cli (MIT). -->

# fabric-plan-skill design mode — Intelligence Sheet visual design

This mode decides **what** an Intelligence Sheet should look like and **why**:
identity, archetype per sheet, visual choice (Matrix, chart, KPI card, slicer),
layout, colour, typography, accessibility. It does **not** write definition
files. Hand the `Design Brief:` contract to `authoring`.

## Must/Prefer/Avoid

### MUST

- Read `_brief/field-registry.md` (or inspect the model per
  `core/model-inspection.md`) before any design decision.
- Use table, column and measure descriptions to choose report questions,
  hierarchy, units, comparison measures and favorable/adverse cues. Carry
  description/expression conflicts into the brief rather than guessing.
- Produce concrete choices: tone, signature, archetype per sheet, visual
  rationale, layout regions, colour map, typography, accessibility.
- Load [session design](design/session-theme.md) first: honor supplied designs;
  otherwise select a fresh session profile and reuse its theme and page layouts
  for every report. Use `design/design-system.md` for baseline guidance.
- Apply the user-confirmed [dashboard standards](design/dashboard-standards.md)
  to every new report and in-scope repair: native visual titles, uncrowded KPI
  sparklines, labels only where they fit, 3–5 standard filters, Matrices whose
  columns fill their width, scroll-free text boxes, one color per meaning and
  an identical shell on every page. They govern craft, not theme; canvas size
  is chosen per report.
- Never infer a required theme/layout from report type, industry or audience.
  Screenshots and report links are feature references; reproduce their layout
  or palette only on explicit request.
- Use the user's explicitly requested legacy-report
  [design inspiration](design/report-inspiration.md) as a reusable pool for
  titles, branding, palette, composition and navigation. Resolve a coherent
  session choice rather than reproducing every example or changing themes
  per report. Screenshot appearance is not native encoding evidence.
- Specify built-in KPI variance icons and sparklines (`KPI-VAR-01`,
  `KPI-CHART-01`), not SVG measures or separate decorative visuals.
- Express every visual as a Fabric Plan visual kind and name the feature IDs
  it needs, so authoring loads the right feature files.
- Decide Super Filter position with the layout (top, left/right, inline,
  popup/collapsible or custom; never inferred from report type). Record
  `super_filter_layout` with each filter's placement, sizing and expanded state.
- Use the [slicer feature files](features/slicers/_index.md) for available
  control presentations, not a prescribed theme/grid. Decide multi-category
  panel versus separate filters and budget space for date cells, hierarchy
  levels, images, measure/variance columns and selection summaries.

### PREFER

- Ask only for missing inputs that change the outcome.
- Matrix for exact numbers and hierarchies; charts for shape, trend, and
  comparison; KPI cards for 3–6 headline numbers.
- Super Filter slicer types matched to field cardinality and audience.

### AVOID

- Writing `sheet.json`, `properties.json`, or any definition part.
- Vague "make it modern" advice without regions, colours, and visual choices.
- Applying IBCS notation unless the user asked for IBCS.

## Topic Files

| File | When to read |
|---|---|
| `design/session-theme.md` | **First** — session persistence, fresh-session choices, design interview, Help and Info |
| `design/dashboard-standards.md` | **Every report** — user-confirmed principles for experience, titles, KPI cards, labels, slicers, Matrix fit, text boxes, color and layout; canvas size chosen per report |
| `design/dashboard-playbook.md` | **Every multi-page report** — journey from data to delivery: mockup, pilot page, user polish, cloning, render checks; right-first-time component defaults |
| `design/report-inspiration.md` | User-authorized legacy-report design vocabulary; optional palette, layout, title, logo and navigation choices |
| `design/design-system.md` + `design-system-part-02.md` | Design guidance and optional style examples; no universal shell |
| `design/archetypes/<name>.md` | Optional composition examples; custom layouts are equally valid |
| `design/chart-selection.md` | **Before** choosing any visual kind or chart type |
| `design/layout.md` | **Before** placing visuals — normalized canvas, grid, bands |
| `design/color.md` | Palette, semantic colours, conditional formatting intent |
| `design/typography.md` | Font sizes and weights |
| `design/interactivity.md` | Slicer scope, sync slicers, cross-filter vs highlight, drill, bookmarks |
| `design/accessibility.md` | **Before** finalizing — contrast, colour-independent cues, titles |
| `design/anti-patterns.md` | **Before** finalizing |
| `design/design-brief.md` | **Before handoff** — full contract template and validation |
| `design/pre-flight-checklist.md` | Final audit |
| `ibcs/ibcs-rules.md` | **Only** when the user asks for IBCS or picks the IBCS report template |
| `design/visual-craft.md` | **Before finalizing** — one title per idea, spacing budgets, element review, finishing pass; optional companion framing and no-scroll |
| `design/design-families.md` | Optional named profiles (F-01 Calm Financial, Fabric Quiet preset) and design classification |
| `design/domain-playbooks.md` | Optional finance and operations question maps (F1–F10, O1–O3); never select theme or layout |

## Workflow

### Step 0 — Data-First Investigation

Apply [module boundaries](core/module-boundaries.md): cross-module measures
and new embeddings are deferred until integration. Design only supported
semantic-model-backed visuals; do not imply the product lacks blend measures.

From the field registry, map each measure × dimension to the question it
answers. Note scenario tags (AC/PL/PY/FC), hierarchies, cardinalities, and
date grain. A design that needs a missing measure is a model gap, not a design.

### Step 1 — Design Identity

Load the session profile before choosing anything. If absent, follow the
supplied design or the session design interview (predefined choices, a user
design file or Other), then persist the profile. Do not reselect identity per
report.

Commit to a **tone** (e.g. corporate calm, finance precise, operational alert,
editorial) and one **signature** move that recurs on every sheet (e.g. the KPI
tile with coloured delta line from `design-system.md`, a variance column with
integrated bars, a consistent hero Matrix). Record `ibcs: true` only when the
user asked for IBCS, including by choosing the IBCS report template.

### Step 2 — Layout Choice

Choose or reuse the session layout with the user, independently of report
type. There is no automatic archetype router or ambiguous-purpose fallback.
Use any of these examples, combine ideas, or choose a custom layout.

| Example pattern | Analytical focus (not a selection rule) | Reference |
|---|---|---|
| Executive Summary | Headline performance | `design/archetypes/executive-summary.md` |
| Operational Monitor | Exceptions and status | `design/archetypes/operational-monitor.md` |
| Analytical Canvas | Exploration | `design/archetypes/analytical-canvas.md` |
| Narrative Story | Annotated explanation | `design/archetypes/narrative-story.md` |
| Comparative Benchmark | Scenario and peer comparisons | `design/archetypes/comparative-benchmark.md` |
| IBCS report template | Opt-in IBCS pages with chart templates C01–C13 and table templates T01–T05 | `ibcs/ibcs-rules.md` |
| Custom | User-selected composition for any question | Record directly in the brief |

For a new session layout, offer 2–3 named options, the IBCS report template
and Other; explain the tradeoffs and record the choice and rationale in
`variant_rationale`. Then reuse the session's page-role layout templates across
reports. Archetypes guide analytical content, not permission to move approved
regions; resolve a data-fit conflict through an approved session layout revision.

### Step 3 — Visual Selection

Read `design/chart-selection.md`. Choose among:

- **Matrix** — exact values, hierarchies, financial statements, variance
  tables, Top N lists (features under `features/matrix/`).
- **Chart** — trend, comparison, composition, distribution, relationship,
  from the Intelligence chart library only (features under `features/charts/`;
  never Power BI native visuals).
- **KPI card** — headline value with comparison (features under `features/kpi/`).
- **Slicer** — Super Filter type per field (features under `features/slicers/`).
- **Element** — title, text, shape, image, button (features under `features/canvas/`).

Respect the encoding hierarchy: position → length → angle → area → hue.

### Step 4 — Visual Configuration

Per visual decide: sort, Top N, labels, number scaling and decimals, totals,
conditional formatting intent, in-cell charts, titles in plain language
(no raw field names), tooltips. Name the feature IDs.

### Step 5 — Theme

Apply the session profile's background, container style, palette, fonts,
buttons, navigation, Help/Info controls and layout templates without rotating
them between reports. Fabric Plan themes live in `planProperties.theme` and
dashboard themes (features `CV-THEME-*`); authoring owns the mechanics.

### Step 6 — Canonical Design Contract

Emit a `Design Brief:` YAML block. Minimal shape (full template in
`design/design-brief.md`):

```yaml
Design Brief:
  generated_by: fabric-plan-intelligence
  contract_version: 1
  mode: greenfield
  session_theme: <complete resolved session profile snapshot>
  design_identity: { tone: <tone>, signature: <signature>, ibcs: false }
  sheets:
    - name: <descriptive sheet name>
      role: <landing | detail | drill | planning-front-door>
      archetype: <Executive | Operational | Analytical | Narrative | Comparative | IBCS | Custom>
      layout_variant: <chosen example or custom layout name>
      variant_rationale: <user/session choice and analytical suitability>
      super_filter_layout:
        position: <chosen position or none>
        region_ids: [filters]
        rationale: <user/session choice and filter usability>
        overflow_behavior: <chosen wrapping/scrolling/open-state behavior>
      layout_contract:
        canvas: { type: keep-existing, width: 1920, height: 1080, units: normalized, margin_px: 32, gutter_px: 16 }
        grid:
          columns: 12
          rows: 12
          regions:
            header:  [1, 1, 9, 2]
            filters: [9, 1, 13, 2]
            body:    [1, 2, 13, 13]
        placements:
          - id: sheet_title
            region: header
            kind: text
            text: <title that names the sheet>
          - id: <visual id>
            region: <region>
            kind: <matrix | chart:<chartType> | kpi | slicer:<type> | element:<type> | embedded-planning>
            purpose: <one analytical question>
            field_bindings: { rows: [], columns: [], values: [], category: [] }
            features: [<feature ids>]
        space_audit:
          content_cell_count: <n>
          placed_cell_count: <n>
          empty_cell_pct: <0-100>
          unplaced_regions: []
          balance_rationale: <why sizes match priorities>
```

When used inside discovery, embed this block in `_brief/report-spec.md`.

### Step 7 — Review and Handoff

Walk `design/design-brief.md` validation and `design/pre-flight-checklist.md`.
Fix issues, then hand off to `authoring`.

## IBCS (opt-in)

Load `ibcs/ibcs-rules.md` (and its `-part-XX` continuations) **only** when the
user explicitly asks for an IBCS report, IBCS theme or IBCS notation, or picks
the IBCS report template. IBCS rules then override the colour and chart
guidance in `design-system.md` for scenario encoding, variance display, scaling
and titles. Set `ibcs: true` in the contract.

## Gotchas

- **Tone declared but not propagated** — palette, type, and container
  treatment must visibly change with the tone.
- **Overlap** — no visual rectangles overlap unless intentional (e.g. a
  background shape). Super Filters occupy the approved regions, not necessarily
  a top band; account for dropdown/popup expansion and permanent content.
- **Redundant KPI tiles** — a tile repeating the number already shown in the
  adjacent chart is noise; tiles need a comparison or threshold.
- **Slicer grain** — executive sheets usually need Year/Month presets, not a
  day-level calendar.
- **Raw field names** — rename every header, axis, and legend to plain language.
- **Percentages** — ratios display as `53%`, never `0.53`; never sum ratios.
- **Embedded Planning grid** — give it the largest region; keep slicers that
  drive it on the same sheet; bounded default selection.
- **Matrix width** — wide month × measure grids need pinned row headers and
  horizontal scroll inside the visual, not a wider canvas.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- **Step 0:** optional domain playbooks map
  model signals to report questions; they never select theme or layout.
- **Step 1:** optional named profiles and design classification are in
  design families.
- **Step 3:** run the
  analytical selection gate
  and record a rationale and the rejected alternative for each visual.
- **Step 4:** also decide data-label density, polarity per measure, and Top N
  and Others behaviour.
- **Step 6:** optional companion fields are listed in the
  design brief.
- **Step 7:** complete the finishing pass
  before handoff and again on the built sheet.
- **Optional (companion default):** the fixed 1600 × 900 canvas, framed
  containers, no-scroll acceptance, the up-front Default-or-IBCS question, the
  F-01 baseline, distinct pie colours and the domain playbooks each apply only
  when the user or session design selects them and never override the session
  theme, supplied designs, report-inspiration guidance or IBCS opt-in.
