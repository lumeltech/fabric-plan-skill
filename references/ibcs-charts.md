# IBCS charts and dashboards

Use this guide when a dashboard needs IBCS content:

- a named chart recipe (C01–C13), a stacked or 100% stacked chart, a waterfall, or an overlapped actual-versus-reference comparison;
- a Matrix table in place of the embedded Planning grid;
- a message title and footnotes;
- the IBCS Plan theme.

The builder writes chart templates, field bindings, the IBCS chart theme with its colors, the Matrix, story text and, when asked, the Plan theme. See [IBCS chart theme and colors](#ibcs-chart-theme-and-colors). The rest of each chart's IBCS styling is a separate concern; see [The IBCS look](#the-ibcs-look).

**Attribution.** IBCS, the International Business Communication Standards, is the notation also published as ISO 24896. IBCS is a registered trademark of HICHERT+FAISST GmbH, IBCS Institute, which owns and oversees the marks. This guide applies the notation's published rules to Microsoft Fabric Plan report parts and restates no IBCS document. Its redistribution terms are not verified here; see the License section of this package's README.

## Contents

- [Request shape](#request-shape)
- [Recipe catalog](#recipe-catalog)
- [Template rules the builder enforces](#template-rules-the-builder-enforces)
- [What the definition carries](#what-the-definition-carries)
- [IBCS chart theme and colors](#ibcs-chart-theme-and-colors)
- [IBCS dashboard page](#ibcs-dashboard-page)
- [Plan theme](#plan-theme)
- [The IBCS look](#the-ibcs-look)
- [Chart styling](#chart-styling)
- [Check and report](#check-and-report)

## Request shape

Add the chart to a dashboard's `charts` list. A chart that names `recipe` or `chartType` is built by `scripts/runtime/ibcs_charts.py`. Any other chart stays a plain column chart, or an integrated variance chart when it has `comparisonField`.

```json
{
  "label": "Sales by region",
  "recipe": "C01",
  "category": "Geo[Region]",
  "stack": "Product[Segment]",
  "measures": {
    "AC": "Facts[Sales]",
    "PL": {"field": "Facts[Plan]", "label": "Plan"},
    "FC": {"field": "Facts[Forecast]", "aggregation": "sum", "label": "Forecast"}
  }
}
```

- `category` is a model dimension and goes in the `axis` bucket. It is required.
- `stack` is a second dimension. Use it only where the template has a stack bucket.
- `measures` is keyed by bucket. **AC** holds the actual. **PY**, **PL** and **FC** hold the comparisons: prior year, plan and forecast.
- A measure value is a field ID, or an object with `field` plus optional `aggregation` and `label`. On LINE and AREA, AC also accepts a list of fields.
- Fields come from the current model or a registered query output. Never derive them from labels or from example names.
- `recipe` alone selects the recipe's default template. Give `chartType` as well only to pick one of the recipe's alternatives (C08 mixed uses AREA). `chartType` without `recipe` builds that template with its own rules.
- `theme` selects the chart's theme: `ibcs` or `plan`. Every chart built here keeps the IBCS chart theme, whether it names a `recipe` or only a `chartType`. Give `"theme": "plan"` for a chart that should follow the Plan theme and its palette instead.
- `style` gives the chart's own background, global font and data-label formatting; see [Chart styling](#chart-styling).
- Unknown options are refused, including every styling key other than `theme` and `style`.

## Recipe catalog

| Code | Recipe | `chartType` | Required bindings |
|---|---|---|---|
| C01 | Stacked Column | `STACKED_COLUMN_VERTICAL` | axis, AC, PL, FC, stack |
| C02 | Stacked Bar | `STACKED_COLUMN_HORIZONTAL` | axis, AC, stack |
| C03 | Overlapped Column | `COLUMN_VERTICAL` | axis, AC, PY, FC |
| C04 | Overlapped Bar | `COLUMN_HORIZONTAL` | axis, AC, PL |
| C05 | Waterfall + Column | `COLUMN_WATERFALL_VERTICAL` | axis, AC, PY |
| C06 | Waterfall + Bar | `COLUMN_WATERFALL_HORIZONTAL` | axis, AC, PY |
| C07 | Line | `LINE` | axis, AC |
| C08 | Stacked Area | `STACKED_AREA`; mixed variant `AREA` | axis, AC, stack; mixed: axis, AC (one or more) |
| C09 | Scatter | `SCATTER_PLOT` | axis, AC (x), PY (y) |
| C10 | Bubble | `BUBBLE_PLOT` | axis, AC (x), PY (y), PL (size) |
| C11 | Related Driver Panels | `LINE` | axis, AC (one panel per driver) |
| C12 | Side-by-Side Waterfall | `SIDE_BY_SIDE_WATERFALL` | one axis field, AC, PY |
| C13 | Overlapped Column, date/forecast | `COLUMN_VERTICAL` | axis, AC |

C07 and C13 assume a date axis. The builder does not check the axis data type, so choose the period field yourself.

C11 is a set of panels, not one chart. Add one C11 chart for each driver, all on the same axis field, each with a single measure in AC. Related drivers have their own scales, so they are not drawn as several lines in one chart. Connectors and shared scale bands between the panels are not authored.

An unknown code is refused: find out which chart the user means instead of guessing an alias. `runtime.ibcs_charts.recipes()` returns this table, and `required_buckets(code, chartType)` returns the required bindings.

Bucket names are chart roles, not business periods. In C09 and C10, PY and PL hold the y coordinate and the bubble size, not a prior year or a plan. Bind the measures the user names for each role. If a required binding cannot be resolved from the model, name it and ask; do not substitute a similar field.

## Template rules the builder enforces

- The AC, PY, PL and FC buckets each take one field. The exception is AC on LINE and AREA, which takes up to 27.
- Scatter has only AC and PY, and both are required. Bubble has AC, PY and PL, and all three are required.
- The native stacked area has only AC and FC. It has no PY or PL bucket.
- Stacked and 100% stacked charts (column or bar) need either a stack dimension or measures in at least two buckets. With two or more measures and no stack, the chart stacks the measures. With one measure and no stack, the chart renders as a plain column or bar, so the builder refuses that combination. The native stacked area always needs a stack.
- Waterfalls and the side-by-side waterfall compare at least two measures in different buckets. The side-by-side waterfall takes a single axis field.
- The category and the stack must be different dimensions. A semantic measure cannot be a dimension. The same value cannot be bound to two buckets.
- Small multiples (row and column trellis), tooltip measures and text categories are not built here.

## What the definition carries

Each chart is an `ANALYTICS_PLUS` visual (type 50). It carries:

- the template in two places, top-level `chartType` and `visualState.chartType`, with the same value;
- pivot assignments with `bucketId` set to the bucket name: `axis`, `stack`, `AC`, `PY`, `PL` or `FC`;
- one ordinary visual-level filter card for each assigned field. Two parts of these cards are not yet confirmed from an export:
  - The stack's card follows the same rule as the category's.
  - A comparison measure's card registers under bucket `AC`, with the real bucket kept on its nested assignment. This was observed for PY and is applied to PL and FC as well.
- on the IBCS chart theme, one saved appearance setting (`hiddenProperties_!!!_appearance`) with the theme selection and its colors.

Fabric saves the same template selectors and assignments when a chart is added. The chart then writes its own template state on first render. **Do not pre-write** template, measure configuration, column-field or comparison mappings. **Do not add title settings.** IBCS charts keep the title the chart produces, and an explicit title belongs to a separate, user-requested edit.

Fabric loads a chart with no saved `chartType` as `COLUMN_VERTICAL`. The plain column chart now names that template explicitly, which changes nothing at runtime but keeps its buckets checked against a known template. Each template has its own bucket names, and a field in a bucket the template lacks binds nothing. Charts from earlier builds of this package keep their category in the generic `category` bucket, so they show values without categories. To restore the category, move it to `axis` together with its filter cards.

## IBCS chart theme and colors

A chart in a Plan starts on the **Customize** theme, which takes its colors from the Plan theme. That is not the IBCS theme, so a chart saved without a theme of its own does not show IBCS scenario notation. The builder therefore saves **IBCS Theme**, the choice under Standards in the chart's theme menu, as the chart's own theme on every recipe and template chart. The chart then keeps it under any Plan theme.

IBCS Standards 2.0 set the notation, not the color codes: an organization picks the codes and keeps them consistent. The chart's IBCS theme supplies these.

| Meaning | IBCS rule | Bucket | Fill | Color |
|---|---|---|---|---|
| Actual (measured data) | UN 3.2, solid dark | AC | solid | `#262626` |
| Previous period in a comparison | UN 3.2, lighter solid | PY | solid | `#bfbfbf` |
| Plan or budget | UN 3.2, outlined | PL | outlined | `#4e4e4e` |
| Forecast | UN 3.2, hatched in the actual color | FC | hatched | `#262626` |
| Desirable variance | UN 4.1, green | | solid | `#8eb900` |
| Undesirable variance | UN 4.1, red | | solid | `#ff000a` |
| Series of a stack | SI 2.2, no decorative colors | stack | solid | greys from `#4B4B4B` |

What the builder saves on the chart:

- the theme selection, and the flag that the chart keeps its own theme instead of following the Plan theme;
- the measure style of each bound role. On LINE and AREA, further actuals take the roles `AC1`, `AC2` and so on, in grey additional colors;
- the variance colors for bars, groups, the waterfall breakdown and trends.

Series colors are not saved. The chart reads its grey series palette from the IBCS theme, so a stack shows greys in place of the Plan palette. On scatter and bubble charts the buckets are coordinates, so the scenario fills do not apply and groups take the series colors.

- `runtime.ibcs_charts.ibcs_palette()` returns these values. `assets/fixtures/ibcs-chart-theme.json` holds the saved state.
- **Existing chart.** Call `runtime.ibcs_charts.apply_chart_theme(properties)` on the freshly exported chart properties. It keeps every other saved setting, replaces the styles of the bound roles and clears explicit group and category colors, as the chart does on a theme change.
- The theme's neutral variance color is a light grey (`#DDDDDD`). The standard names blue for neutral or ambiguous variances and blue-green in place of green for readers with a color deficiency. Report that difference when the user asks for strict notation; do not recolor on your own.

## IBCS dashboard page

Two optional dashboard keys turn a workspace into an IBCS page. Both are built by `scripts/runtime/ibcs_report.py`.

```json
{
  "table": {"label": "Sales detail", "rows": ["Geo[Region]"], "columns": ["Period[Month]"],
            "measures": {"AC": "Facts[Sales]", "PL": {"field": "Facts[Plan]", "label": "Plan"}}},
  "ibcs": {"message": "Sales 5% above plan, driven by EMEA", "subtitle": "Sales in EUR m",
           "detail": "FY2026, AC vs PL", "footnotes": ["AC = actual, PL = plan"]}
}
```

**`table` adds a Matrix.** The Matrix is an `INFORIVER` visual (type 10), and it takes the grid slot in place of the embedded Planning grid.

- `rows` takes one or more dimensions. `columns` takes zero or more.
- AC goes in `ameasure`; it takes one or more measures. PY, PL and FC go in `pymeasure`, `plmeasure` and `fcmeasure`, and each takes one.
- The definition spells the type exactly `INFORIVER`. A misspelled type imports as a Planning visual.
- The Matrix reads model or registered query values. It does not show the Planning grid's input cells or unsaved values.
- When no other dashboard embeds the Planning owner, the owner's own Planning page stays visible, so users enter values there. The coverage check reports this case as `inputOnVisiblePlanningPage`.
- The note slot captions the Matrix with the table label, unless `note` or footnotes are given.
- The Matrix gets no visual-level filter cards. Slicer selections are not saved into its state either; that behavior has not been confirmed for a Matrix.

**`ibcs` adds the story.**

- `message` is required: the one statement the page should convey.
- On a Matrix page, the message title replaces the workspace banner. It follows Fabric's own IBCS report title: the message in bold 18px, then `subtitle` at 13px and `detail` at 11px. The text uses Arial, and its color is left to the theme.
- On a page that still embeds the Planning grid, the message heads the dark workspace banner instead. The banner keeps the role-color key, because the grid's input, Power BI, formula and From Sheets colors still need it.
- `footnotes` takes a list of lines. Each becomes an 11px paragraph in the note slot. In the left-rail and stacked layouts that slot moves to the bottom of the page and grows with the number of lines. A custom layout places the note rectangle itself.
- Footnotes and `note` share one slot, so give only one of them.
- Threaded comments, and notes anchored to data cells or chart points, cannot be authored through a definition. Report them as unavailable.

**Template pages.** Pages for the IBCS business reporting templates are composed like this.

| Page | Content |
|---|---|
| C01–C10, C12 | One recipe chart |
| C11 | One C11 line panel for each driver |
| C13 | A C13 column chart by period, with a C04 bar chart by category beside it |
| T01, T02 | A Matrix by hierarchy, with a bar chart for each comparison beside it |
| T03 | A Matrix, with one C04 bar chart |
| T04 | A Matrix, with a C12 side-by-side waterfall |

Bind each value to the bucket of its scenario. A previous-year value in PL is drawn outlined, as a plan. C04 needs a plan in PL, so for actual against previous year build the bar chart from `"chartType": "COLUMN_HORIZONTAL"` with AC and PY.

## Plan theme

`planProperties.json` `properties.theme.type` selects the Plan theme; type 5 is IBCS.

- **New Plan.** Add a top-level `"theme": "ibcs"` to the build spec. The provisioning capability is `plan.theme`; the Matrix capability is `intelligence.matrix`.
- **Existing Plan.** Call `runtime.ibcs_report.set_plan_theme(planProperties, "ibcs")` on the freshly exported part. It changes `type` and keeps every other member of the theme object.

The theme applies to the whole Plan. Set it only when the user explicitly asks for an IBCS Plan theme; asking for IBCS charts is not enough. Product code shows these effects:

- Matrix and Table visuals re-apply the Plan theme each time they load.
- Planning grids follow the Plan theme only when the tenant has Plan themes enabled for Planning.
- A chart that keeps its own theme ignores the Plan theme. Recipe and template charts keep the IBCS chart theme, so they look the same under every Plan theme.
- A chart that follows the Plan theme changes, on load, only the settings still at the previous theme's values. A sheet the Plan has not themed before has no previous value to compare against. So the Plan theme alone does not reliably restyle a plain column chart, or a chart built with `"theme": "plan"`. When a plain column chart must show IBCS colors, build it from `"chartType": "COLUMN_VERTICAL"` with its value in `measures.AC`.

A readback of the definition proves only that the value was saved. It does not prove what any visual renders.

## The IBCS look

Each recipe pairs its template with styling: the IBCS theme, data labels, measure fill patterns, ranking, deviation callouts and number format. The builder writes the theme selection, the measure fills and patterns and the variance colors. **It does not write the rest**, except what a chart style carries.

- **Other theme-owned settings.** Picking a theme in the product also recomputes settings outside the chart's appearance: title mode, comparison notation, data label defaults, number scaling and more. `apply_chart_theme` does not reproduce that cascade; a built chart has IBCS colors and scenario fills with default labels, title and scaling. `"style": {"theme": ...}` runs the real cascade instead, within the limits below.
- **Settings with no authoring route.** Top-N ranking, deviation callouts, number format, forecast population, axis breaks, reference bands, bubble sizes, explicit group colors, series labels, and line and sorting options have no saved-definition route in the current product.

## Chart styling

`runtime.chart_styling` writes on two channels of unequal reliability; say which one each part used.

**Data labels go to the chart store, and this route renders.** `apply_chart_style` writes the store's `dataLabel` slice as the stringified `hiddenProperties_!!!_dataLabel` member of `visualState`; the host re-reads it on load and merges it over the theme defaults. No switch is on that path, and `data_labels` reads it back.

**Background, global font, theme and variance labels go to the AI schema channel**, as `visualAiSchemaState` beside `visualState`: the chart hands it to its schema compiler before its first render, which then clears it. It loads only while the host's `planningAIAssistant` switch is on, which is off by default; with it off the object is inert — no error, no styling, indistinguishable from a broken write.

- A chart spec takes `"style"`: `{"theme", "background", "font": {"family", "size", "color", "responsive", "autoColor"}, "dataLabels": {"all", "measures": {<measure label>: ...}, "variance"}}`. `runtime.intelligence.card` and a page-level `"style"` take the same key, the latter as the page default; a visual's own style overrides only the options it names.
- Address a data label by the label the chart shows (the spec's `label`, an export's `customName`); the writer resolves it to the store key, the measure's **role** (`AC`, `PY`, …), because `savePropertyAgainstRole` is on by default. A name the chart does not bind, or an option the product rejects, **fails the build** rather than quietly doing nothing.
- `color` clears `contrastColor`, or the theme's auto-contrast color wins; `background` sets `showBackground`, or it reads as transparent; `show` alone toggles labels.
- `axis`, `legend`, `measureSeries` and `rows` share the AI channel and are not written here. Only an ANALYTICS_PLUS chart carries a style, and `apply_chart_style` merges with what an export already carries.

## Check and report

1. Before the build, confirm that every required binding resolves to a current model or query field.
2. After building, `runtime.ibcs_charts.describe(properties)` lists the template, matching recipes, bucket bindings, whether the two template selectors agree, the chart theme (`ibcs` or `plan`), the AI schema style and the data-label slice; `runtime.chart_styling.chart_style` and `data_labels` read the two back. `runtime.chart_filters.audit_chart_filters(properties)` checks the filter cards.
3. After an authorized update, export the Plan and compare it with what was built:
   - each chart's two `chartType` values;
   - the assignments of each chart and Matrix, by field ID and bucket;
   - each IBCS chart's theme, and the fill color and pattern of its bound roles. The chart saves more appearance settings once it has rendered, so compare these members only;
   - each styled chart's `hiddenProperties_!!!_dataLabel`, role by role, and its `visualAiSchemaState`, including whether the chart cleared the latter after it rendered;
   - the Plan theme `type`.
4. Report outcomes separately:
   - templates, bindings, the IBCS chart theme and colors, the Matrix, story text and the Plan theme value as saved;
   - data labels as written to the chart store, switch-free, pending the browser check;
   - chart background, global font, theme and variance labels as saved through the AI schema only, rendering only where `planningAIAssistant` is on; claim them rendered only from the browser;
   - the rest of the IBCS chart styling as not applied;
   - rendering as not tested.
