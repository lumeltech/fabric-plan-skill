## Contents

- [Fabric Plan at a glance](#fabric-plan-at-a-glance)
- [Where the Intelligence Sheet fits](#where-the-intelligence-sheet-fits)
- [Visual families on an Intelligence Sheet](#visual-families-on-an-intelligence-sheet)
- [Feature heritage](#feature-heritage)
- [Modes: edit and read](#modes-edit-and-read)
- [Data path](#data-path)
- [Sibling skill routing](#sibling-skill-routing)
- [Additional details](#additional-details)

<!-- Core reference for the `fabric-plan-skill` skill. Read once per task before the first authoring or management action. -->

# Fabric Plan product architecture

## Fabric Plan at a glance

Fabric Plan is a Microsoft Fabric workload item (item type `Plan`). In this
skill's current workflow, a Plan is bound to one Power BI semantic model and contains an ordered list of
**sheets**. Each sheet has a `sheetType` and owns one or more **visuals**.

| Sheet type (`sheetType`) | What it is | Owning skill |
|---|---|---|
| `REPORTING` | **Intelligence Sheet** — free-form canvas with Matrix, slicers, charts, KPI cards, elements | **this skill** |
| `PLANNING` | Planning sheet — editable grid with inputs, formulas, forecasts, scenarios, writeback | Planning module team; integration pending |
| `POWERTABLE` | PowerTable — editable database table with approvals, automations, forms | PowerTable module team; integration pending |
| `INFOBRIDGE` | InfoBridge — query/transformation layer across sheets and sources | InfoBridge module team; integration pending |
| `SUPER_FILTER`, `BI_REPORTING`, `BI_ADHOC_ANALYSIS`, `BI_DASHBOARD` | Other documented sheet types | Treat as unverified; inspect a native sample before authoring |

The Plan definition (the JSON the REST API accepts) is described in
[definition-structure.md](definition-structure.md).

## Where the Intelligence Sheet fits

The Intelligence Sheet is the visualisation and reporting layer of Fabric Plan,
the counterpart of a Power BI report page. It is commonly the **front door** of
a plan:

- Read-only analysis on the semantic model (Matrix, charts, KPI cards).
- Scope controls (Super Filter slicers) that filter every visual on the sheet.
- Optional **embedded** Planning or PowerTable visuals, so users plan from the
  dashboard. The embedded visual is owned by its source sheet; the Intelligence
  sheet only stores its placement and interactions.

The list describes product capability. This skill currently authors only
semantic-model-backed reporting, not embeddings or cross-module inputs; read
[module boundaries](module-boundaries.md) before proposing them.

## Visual families on an Intelligence Sheet

| Family | Native code / hint (observed) | Feature folder |
|---|---|---|
| Matrix (tabular, hierarchical, financial, IBCS tables) | `visualType: 10`, registration `INFORIVER` | `features/matrix/` |
| Slicer (Super Filter) | `visualType: 60`, listed in `definition.json` as `SUPER_FILTER` | `features/slicers/` |
| Charts (Intelligence library, IBCS C01–C13) | `visualType: 50`, registration `ANALYTICS_PLUS`; native `chartType`, e.g. `LINE`, `DONUT_CHART` | `features/charts/` |
| Table (Analytics+ table) | Capture a native sample | `features/table/` |
| KPI cards (Intelligence cards) | `ANALYTICS_PLUS`/50, `chartType: CARD` | `features/kpi/` |
| Canvas elements (text, shape, image, button) | `BI_TEXT`/202, `BI_SHAPE`/201, navigation `BI_RUNTIME_INPUT`/203; images not isolated | `features/canvas/` |
| Embedded Planning grid | `visualType: 80`, listed as `PLANNING` with `isEmbedded: true` | `features/canvas/embed-planning-sheet.md` |

Codes were observed in native saved definitions; capture new evidence with
[native samples](native-samples.md).
The user-facing product is Fabric Plan. Preserve legacy storage enum names,
including `INFORIVER`, `ANALYTICS_PLUS`, `SUPER_FILTER`, and field `PowerBI`.
These names neither authorize external Inforiver formats nor Power BI visuals.

**Adding visuals (UI).** Every visual is added from the **Visualizations**
pane (icons on the right of the canvas), never from an Insert › Chart menu.
Top-level tiles: Charts 100+, Planning, PowerTable, Matrix, Table, Tree
(decomposition tree), Gantt, Super Filter and KPIs. **Charts 100+** opens the
chart library: Search Charts, All / IBCS / Special filters (IBCS charts;
storytelling charts), Quick Picks, and the categories Bar/ Column, Line, Area,
Waterfall, Combo, Funnel, Bubble/ Scatter, Pie/ donut, Hierarchy, Gauge,
Radar/Polar, Statistical, Bullet, Marimekko and Special Charts. Each feature
file's UI path names its tile or category; search by chart name when a
variant is not where expected, because category contents can change by build.

## Feature heritage

- **Matrix** reuses the Inforiver Reporting Matrix engine. Most Reporting Matrix
  features (layouts, templates, number formatting, totals, calculated rows and
  columns, quick formulas, conditional formatting, in-cell charts, Top N,
  pagination, notes, export) are available. Writeback-Matrix-only features are
  out of scope here unless the feature file says otherwise.
- **Slicers** reuse Inforiver Super Filter. All Super Filter features are
  available: date filters, facet, hierarchy, measure, numeric, alphanumeric,
  treemap, play axis, saved filters, presets, search, mass filter.
- **Charts, KPI cards, tables, and storyboard elements** come from the
  Intelligence chart library, which is Inforiver Analytics+. **All Analytics+
  charts are available**: column/bar, line, area, combo, waterfall, pie/donut,
  scatter/bubble, bullet, Marimekko, box plot, histogram, gauge, treemap,
  sunburst, packed bubble, funnel/pyramid, radar, decomposition tree, range,
  ribbon, tornado, slope, parallel coordinates, lollipop, Sankey, network,
  variance, Gantt; plus trellis/small multiples, multi-measure charts, cards,
  tables, and IBCS chart templates C01–C13 (IBCS® certified May 2026).
- **Power BI native visuals are never used** on an Intelligence Sheet.
- Each feature file records `status` (`IS-Confirmed`, `Inforiver-only`,
  `IS-native`). `Inforiver-only` means the feature exists in Inforiver docs but
  has not been confirmed in Fabric Plan docs yet — confirm in the UI before
  promising it.

## Modes: edit and read

`planProperties.json → workloadModeConfig` controls panes per mode:

- `EDIT` — authors see Data, Fields, Elements, Filter panes (plus optional
  Bookmarks, Comments, Personalize, Variables, Lumel AI panes).
- `READ` — consumers see the Filter pane and whichever panes are enabled.

Reading view and editing view toggles, notes, export, Explore Model, edit
interactions, sync slicer, and personalise are documented at
`https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes`.

## Data path

1. In this release, the semantic model is the only data source this skill uses.
   This is a temporary integration boundary, not a product restriction.
   Intelligence visuals can blend model data with other modules' measures;
   see [Blend capability and release gate](module-boundaries.md#product-capability-versus-current-release).
   Currently supported model fields are
   referenced by `[Table][Column]` style IDs, e.g. `"[Dim] Date[Financial Year]"`,
   or `Measure[<name>]` for model measures.
2. Visual buckets (`pivotAssignments`) bind model fields to roles:
   `rows`, `columns`, `ameasure` / values, `category`.
3. Slicers bind fields through `superFilterAssignments` and register filter
   state (see `core/invariants.md`, three-part filter state).
4. Inserted/visual measures (formulas, calculated rows/columns) live inside the
   visual state and use 19-digit measure IDs and `M_<id>` formula tokens.

## Sibling skill routing

| Request | Route |
|---|---|
| Create/edit Planning sheets, inputs, forecasts, allocations, scenarios | Owning Planning skill; blocked until integrated |
| InfoBridge queries, Blend, From Sheets / From Queries, P&L consolidation | Owning InfoBridge skill; blocked until integrated |
| PowerTables, approvals, automations, forms | Owning PowerTable skill; blocked until integrated |
| Create a **new** model measure that Fabric Plan cannot compute (with permission) | **this skill** (`model-measures`) |
| Change existing model measures, or any columns, tables, relationships | semantic-model skill (outside this skill) |
| Add/rebind an embedded grid or cross-module measure on an Intelligence sheet | Blocked until module integration and source-aware validation |

Existing embeddings and other module parts remain unchanged. After integration,
the Intelligence side owns presentation; the source module owns its data and
behavior. Do not assume sibling skills are present or activate them by name.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Visual identity before chart template

- Establish a visual's family from its `definition.json` registration and its
  owner `visualType` before reading `chartType` or template state. Text, shape,
  Super Filter and embedded Planning owners can keep incidental chart fields;
  a Text owner saved `chartType: "COLUMN_VERTICAL"` [saved]. Scripts that
  traverse or patch charts by `chartType` must filter by family first.
- Chart template identity spans the owner `chartType`, the decoded template
  `id`, `previousId` and `lockedTemplateId`, plus `rendererType` and
  `chartOrientation` [saved]. Compare and change them as one set.
- Template chart type and renderer type are separate: row-trellis cards saved
  a template chart type `columnChart` with
  `rendererType: "smallMultiplesChart"` [saved].
- Compare the active subtype as well: page tabs, bookmark tabs and a live
  navigation button are different `BI_RUNTIME_INPUT`/203 subtypes [saved].

### Additional observed families

| Family | Observed code | Note |
|---|---|---|
| Image | `BI_IMAGE`/207 | Stores an encoded resource locator rather than image bytes [saved] |
| Layout container | `BOX`/206 | Horizontal layout container, not a decorative `BI_SHAPE`/201 [saved] |
| Table | owner `visualType` 15 [saved] | Registration name unresolved; see native samples |

These codes do not change any feature `encoding`; capture a native sample
before authoring them.
