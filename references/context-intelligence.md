# External Context and rich Intelligence workspaces

For each chart/KPI assignment, also construct its visible ordinary visual-level filter with `runtime.chart_filters`. Read the chart visual filters guide. Hidden embedded scope and Planning Context registrations do not replace these cards.

Every dashboard also keeps the mandatory baseline in the application defaults guide, including a visible Page Navigator, measure cards at All, integrated variance for baseline comparisons and source Sum for numeric Columns. For the five end-to-end business examples, read the five usecase recipes guide.

## Contents

- [Business meaning first](#business-meaning-first)
- [Observed persistence contract](#observed-persistence-contract)
- [Build an Intelligence workspace, not only an embedded table](#build-an-intelligence-workspace-not-only-an-embedded-table)
- [Composition and geometry](#composition-and-geometry)
- [Acceptance and graceful degradation](#acceptance-and-graceful-degradation)
- [Filters, KPI stores and query identity](#filters-kpi-stores-and-query-identity)
- [Presentation, source binding and Home](#presentation-source-binding-and-home)
- [Fit a layout to a Reading viewport](#fit-a-layout-to-a-reading-viewport)

## Business meaning first

A planner chooses a version outside the grid, then works on employee, product or account rows within that version. The Context selection is passed into the embedded Planning visual. Scenario/version does not become a visible row or column unless the business explicitly asks for a comparison layout. Context also identifies the input coordinate; an ordinary dashboard filter alone does not configure that storage binding.

Rows and Columns already define storage grain. External Context is only for additional stored selections, never ordinary page or global filtering. Connected Planning owners must match the Context, and query outputs must retain it; read the storage context guide for the bundled guards and build-time query evidence.

Separate four concepts:

| Concept | Purpose | Construction |
|---|---|---|
| External **Context** | Select the scenario/version for scoped inputs | `context` on the Planning spec; complete registration, mirrored state and input binding |
| Dashboard slicers | Narrow the working view by period, region, department, employee, product or channel | `SUPER_FILTER` visuals using semantic master-table columns |
| Dimension ID mapping | Keep input identity stable when labels change | Same-table key mapping and full lookup descriptors; context-only descriptors stay off visible axes |
| Lock/security policy | Decide whether a user may edit or see a coordinate | Separate policy and acceptance; Context is not authorization |

Do not silently substitute Scenario rows for Context. Do not claim assignments or slicers enforce RLS. Shared assumptions that intentionally ignore version context need a separate explicitly modeled policy; this factory rejects unbound inputs on a context-scoped sheet.

## Observed persistence contract

Synthetic definition fixtures and mocked long-running-operation responses cover
these paths. Construction uses no exported tenant report or historical identity.

On a Planning visual, `properties.superFilterAssignments[]` contains the full external registration:

- `isContextDimension: true`, `filterLevel: "visual"`, a fresh `filter_<uuid>`, `position: "RIGHT"`.
- `pivotAssignments[0].bucketId: "Category"` (capital C), the real semantic table/column/source ID and grouping metadata.
- `filter[]` holds typed `VALUES`, with aligned `columnIds`, `columnNames`, `columnDataType`, `dataType`, `tableNames`, `sourceType`, and `valuesFilter` arrays.
- `configuration` supplies the Context label, FACET mode, explicit single selection, expansion, sort and filter settings.
- The **same full registration**, including its fresh ID, is mirrored at `properties.visualState.embeddedSuperFilter.superFilterAssignments[]`.
- `properties.visualState.filterContextSettings` enables `filterContextStatus`, `isCommentFilterContext`, and `isNoteFilterContext`. It is not a top-level visual property.
- Each scoped input has `columnMeta.measure_type.DataInput.bound_to_filter_context: true` and outer `boundToFilterContext: 10`. The Boolean and numeric domains are different. `20` denotes the unbound outer state.

The Context field is absent from visible `pivotAssignments` Rows/Columns, `rowDimensions`, `columnDimensions`, and saved-pivot axes. Its `dimension_id_mapping.pivot` descriptor may use native `bucket_type: "Row"` purely as lookup metadata; this does **not** mean it is visible. Add both label and same-table key descriptors when ID mapping is requested.

Do not copy `filterContextHashMap`, `filterContextHash`, `filterContextJson`, last selection caches or historical input coordinates into a new application. They are not prerequisites to author the external Context registration. Let native initialization build runtime state. Never change context identity on an existing populated sheet without a separate input-migration and retention check.

`scripts/runtime/filters.py` provides typed selection DTOs, `registration`, `prepare_context`, `apply_context`, and `audit_context`. `construct.planning` consumes the symbolic `context` list automatically; `scope` and `workflow` retain it.

```json
{
  "name": "Workforce inputs",
  "rows": ["Geography[Area]", "People[Name]"],
  "columns": ["Time[Month]"],
  "context": [{"field": "Version[Name]", "values": ["Proposal"]}],
  "dimensionIdMappings": {
    "People[Name]": {"ID": "People[Key]"},
    "Version[Name]": {"ID": "Version[Key]"}
  },
  "measures": [{"key": "pay", "kind": "DataInput", "label": "Monthly pay", "context_bound": true}]
}
```

Resolve fields, relationships, uniqueness and selected members from the current model before using this pattern. These sample names are not defaults. The selected factory supports single-member Context; multi-member storage context and date/hierarchy filters require their own supported branches. An unsupported branch affects its dependent sheet/feature, not unrelated application work.

## Build an Intelligence workspace, not only an embedded table

For each requested business workspace derive relevant controls from its grain. Workforce commonly needs planning year, region, department and employee; Commercial commonly needs period, region, product and channel. Finance commonly needs period, region, account and scenario Context. Use actual available dimensions; do not invent missing fields. Aim for three or four useful slicers and two or three meaningful KPIs when the model supports them. Do not add controls merely to reach a count.

The observed reference workspace has four native slicers, three native KPI cards, a banner, a workbench note, and one embedded Planning owner. `scripts/runtime/intelligence.py` constructs these active branches parametrically:

| Visual | Declaration / native type | Relevant state |
|---|---|---|
| Slicer | `SUPER_FILTER` / `60` | `pivotAssignments` bucket `category` (lowercase), ordinary `superFilterAssignments`, `slicerFilterAssignments`, `facetSettings`, `displaySettings`, `toolbarSettings`, `measureFilterSettings` |
| KPI | `ANALYTICS_PLUS` / `50` | measure bucket `AC`, `chartType: "CARD"`, serialized `hiddenProperties_!!!_chartsMode`, `..._chartCustomTitle`, `..._kpiControls`, `..._numberFormatting` |
| Chart | `ANALYTICS_PLUS` / `50` | top-level `chartType` and `visualState.chartType` naming the same template (`COLUMN_VERTICAL` by default; an IBCS recipe selects its own). Buckets `axis`, `AC`/`PY`/`PL`/`FC` and, on stacked templates, `stack`. See the IBCS charts guide |
| Banner/note | `BI_TEXT` / `202` | `visualState.text` as a serialized Lexical document |
| Embedded plan | `PLANNING`, `isEmbedded: true` | Portable GUID reference to the direct owner plus post-import page-local runtime geometry |
| Tree | `TREE` / `25` | Takes a chart slot when a chart spec has `tree`. `chartType` `DECOMPOSITION_TREE` or `ORGANIZATION_TREE` in both selectors. Roles `rows`, `ameasure` and, for an organization tree, `parentid`, `fieldid` and `columns`. See the visual type coverage guide |
| Matrix table | `INFORIVER` / `10` | Replaces the embedded plan when the dashboard has `table`. Buckets `rows`, `columns`, `ameasure`, `pymeasure`, `plmeasure` and `fcmeasure`. See the IBCS charts guide |

The table lists the dashboard branches this package constructs, including decomposition
and organization trees. A dashboard can also hold a visual type outside it, such as a row
or measure tree or another Analytics+ chart family. Read the Intelligence visual type
coverage guide: classify the visual from its current properties, pass those properties
through unchanged, and report construction of an unlisted type as unavailable.

Ordinary slicers are **not** `isContextDimension` registrations. Use semantic dimension columns for slicers and grouping; use actual semantic measures or registered InfoBridge outputs for KPI values. Do not derive query-field IDs from labels. `card(..., query_fields=actual_catalog)` accepts a fully registered InfoBridge field. The composed `build/provision` path currently handles semantic KPI fields; query-backed cards must be added through the component path after query registration, then exported and checked. Do not substitute semantic actuals for plan KPIs without clearly labeling the changed meaning.

Numeric period ranges emit one `RANGE` DTO. Do not retain a contradictory old `VALUES` filter alongside it. Single-select defaults must contain exactly one actual member; optional detail slicers start with All. Required selections disable clear/select-all controls. Relevant dropdowns have visible labels, search and appropriate clear behavior.

KPI renderer configuration remains JSON **strings** where the native contract uses strings. Dynamic `[$Title]` and `[$Value]` tokens display the assigned field; never place synthetic totals in a KPI. Do not copy dormant chart templates, default custom-format keys, inherited query IDs or runtime entity IDs from examples.

### Initial scope versus live propagation

The Planning owner's Context selection is mirrored inside its own state. A dashboard embed references that owner, preserving Context. KPI consumers receive a hidden selected-scenario filter; initial ordinary slicer selections can be forwarded into `visualState.embeddedSuperFilter.superFilterAssignments`. These are initial persisted states, **not proof of event propagation**. Preserve full Context registrations when forwarding ordinary filters; do not freeze dashboard slicer defaults into the reusable Planning owner's filter list.

Default native interactions are retained (`visualInteractions: {}`). Do not invent undocumented interaction IDs or claim that this object proves filtering works. Verify native selection propagation separately: changing region/department must update the intended grid/cards, clearing must restore the intended scope, and Context changes must preserve separate input values. A query result must carry compatible keys/grain or a validated semantic relationship; matching labels alone cannot establish filtering. A missing downstream period/scenario column is a query-contract defect, not something to hide by dropping the slicer.

## Composition and geometry

The normal spec supports a top-level `dashboards` list referencing source owners by this run's sheet names. See `assets/fixtures/context-dashboard-model.json` and `assets/fixtures/context-dashboard-spec.json` for a complete offline example. Use:

```text
python scripts/plan.py build --model assets/fixtures/context-dashboard-model.json --spec assets/fixtures/context-dashboard-spec.json --out trial/context-dashboard
```

When layout is unspecified, use a full-width header, a left rail with vertical page navigation above the slicers, and a wide matrix above a balanced chart row. KPI cards form rows above the matrix when present. The compiler uses a 1920-unit default width, 24-unit outer margins and 16-unit gutters. It sizes navigation for the page count, divides available filter height across the rail, and aligns the last filter with the bottom of the chart area. Odd final rows fill the available width. For an explicit design, pass dashboard.layout as a pixel layout with width, height and rectangles keyed by header, navigator, note, grid, slicer:0, card:0, chart:0 and subsequent indices as applicable. Use the stacked preset for the former full-width lower matrix. The builder checks bounds and separation before import.

The public create carries the canvas, direct visual rectangles and embedded matrix declarations. Each dashboard stores its matrix rectangle under sheet.properties.reactiveVisualProperties[]. The outer visualId and inner properties.originEntityId are report-local numeric strings. The inner properties also contain position and dimension. The source visual GUID remains in the embed declaration. In fresh builds the runtime derives both local IDs from the generated declaration sequence. For existing Plans, use the destination’s saved mapping. Reuse the same source pair on pages sharing a matrix and calculate each rectangle in its own canvas coordinates.

## Acceptance and graceful degradation

- Before create: validate semantic fields/member values; Context off axes; input-binding consistency; same-table ID descriptors; native visual source roles; typed single/range filters; fresh identities; no stale hashes; geometry and required modules.
- After import: export/poll/read back Context on the **owner**, both mirrors, selected members, bindings, dashboard direct visual types, active card state and embedded owner reference. Compare the exported page-local embedded placement with the requested rectangle.
- Behavior is a separate gate: Context switch/input retention, ordinary slicer selection/clear, KPI query refresh and lock/security checks. API/property persistence or schema checks alone do not establish these outcomes. Remain API-only; do not introduce UI steps or ask the user to hand-fix JSON.
- The fresh reference export confirms saved native shapes; generated constructors have offline tests and mocked API transactions. Newly generated visual initialization, rendering and dynamic propagation still require destination acceptance. The bundled public schema currently omits some observed Intelligence declaration enums and disagrees with the native `Edit` input enum; preserve the native evidence and record schema conflicts rather than falsely claiming all schemas pass.
- If an optional KPI/slicer cannot bind, omit that visual with a coverage entry and relayout the rest. If Context cannot be built safely, do not silently turn it into Scenario rows or unbound editable data. Retain independent sheets and report the affected scope. A page with missing controls is a partial workspace, not equivalent to the requested rich dashboard.

The constructors need no source repositories, old artifacts, cached filter hashes or manual JSON repair.

## Filters, KPI stores and query identity

Follow the consumer repair guide for complete KPI stores, the uppercase `RIGHT` filter-pane position and the rule that native input-record row IDs are never query output-column IDs. It also covers semantic-model and workspace intake and generic FabricSql OAuth connection selection. A definition readback is not proof of rendering or financial propagation.

## Presentation, source binding and Home

- Read the planning presentation guide. Normal application builds require rich
  Intelligence dashboards above their embedded Planning grids. `present-planning`
  writes the complete native TEXT header and semantic measure palette; build and
  provision apply these new-application defaults, and
  `check-application-presentation` checks coverage offline. An explicit request
  to skip runtime validation still takes precedence.
- Read the measure source bindings guide before assigning or replacing measures.
  `resolve-measure-binding` constructs exact PowerBI, Visual and InfoBridge
  identities with typed metadata. Native companion records are not sheet outputs.
  Reconcile ordinary filter cards with changed chart assignments; captions alone
  do not identify a source.
- Home is mandatory alongside rich Planning headers, measure colors and embedded
  Intelligence dashboards. Read the application defaults guide and run
  `check-application-defaults`. Home visibility is published in the definition;
  role-specific Home content is prepared locally only. Do not silently downgrade a
  complete application to grids or dashboards without its landing page.

## Fit a layout to a Reading viewport

Measure the drawable area between the open panes and toolbars at fit-to-width. Set `dashboard.viewport` to an object such as `{"width": 1600, "height": 1000}`. For the default layout the builder uses this aspect ratio and reserves enough space for the page count, slicers and matrix. The stacked preset can grow its bottom matrix. Content that needs more space keeps its height.

For a custom pixel layout, add `fitColumns` alongside the existing `width`, `height` and `rectangles`. The initial height represents the minimum design height when fitting is enabled. For example, a left rail with three filters and a main column with a matrix above two charts could declare:

```json
{
  "bottomMargin": 24,
  "fitColumns": [
    {"rows": ["slicer:0", "slicer:1", "slicer:2"], "weights": [1, 1, 2]},
    {"rows": ["grid", ["chart:0", "chart:1"]], "weights": [2, 1]}
  ]
}
```

List each column from top to bottom. Group adjacent visuals that share a top and height into one row. Weights distribute **additional** height. Equal weights add equal height, so start comparable charts at equal heights. A zero weight keeps a row at its authored height as earlier rows expand. Headers and navigation above a stack can stay at their original coordinates. Declare every column that should reach the common bottom margin. Horizontal positions, existing gutters, and source identities are preserved. With a fixed custom layout, omit `fitColumns` to retain the supplied dimensions. Use separate target layouts for materially different Reading viewports when one saved arrangement cannot serve both.
