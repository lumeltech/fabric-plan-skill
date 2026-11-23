# Visual and chart selection

> Choose only from the **Intelligence chart library** (`features/charts/`),
> the Intelligence Matrix, KPI cards and Super Filter slicers. Never use
> Power BI native or custom visuals.

<!-- Design topic for the `fabric-plan-skill` skill. -->

## First: Matrix, chart, KPI card, or slicer?

| The reader needs… | Use | Feature area |
|---|---|---|
| Exact numbers, many measures, hierarchies, statements | Matrix | `features/matrix/` |
| Shape: trend, ranking, composition, distribution, relationship | Chart | `features/charts/` |
| 1 headline number with a comparison | KPI card | `features/kpi/` |
| To scope everything else | Slicer (Super Filter) | `features/slicers/` |
| Context, navigation, legend, branding | Element | `features/canvas/` |

## Encoding hierarchy

Position → length → angle → area → hue. Prefer bars and lines; use angle
(pie/donut) only for share with ≤ 5 parts.

## Question → chart

| Question | First choice | Alternatives | Avoid |
|---|---|---|---|
| How does it change over time? | Line (≤ 5 series) / column (≤ 24 periods) | Area (single series), sparkline in Matrix | Pie, stacked area with many series |
| Which is largest? | Sorted horizontal bar | Lollipop / pin, Top N Matrix | Unsorted column, pie |
| How do parts make the whole? | Stacked bar (few parts) / waterfall (bridge) | Treemap, 100% stacked, Marimekko (two dimensions) | 3D pie |
| Actual vs plan / PY? | Column with plan overlay or variance bars | Bullet, integrated variance column in Matrix | Two separate charts |
| What explains the change? | Waterfall (bridge) | Variance Matrix, Sankey (flows) | Line |
| Distribution? | Histogram / box plot | Dot strip | Average-only card |
| Relationship between two measures? | Scatter / bubble | Quadrant with averages | Dual-axis line |
| Same chart per segment? | Small multiples / trellis | Matrix with sparklines | 12 colours in one chart |
| Schedule / timeline? | Gantt | Matrix with dates | Bar with date axis hacks |
| Flow between stages? | Sankey / funnel (nested stages only) | Network graph (relations) | Pie |
| Multiple measures, different units? | Multi-measure chart, separate clearly labelled axes | Small multiples | Unlabelled dual axis |

## Matrix layout choice

| Need | Layout feature |
|---|---|
| Drillable hierarchy | Hierarchy layout (`MX-LAY-01`) |
| Flat list / export-like | Table layout (`MX-LAY-01`) |
| Statement (P&L, balance sheet) | Financial template + calculated rows (`MX-TPL-02`, `MX-CALC-01`) |
| Many measures as rows | Measures-in-rows (`MX-LAY-02`) |
| Variance at a glance | Variance columns + integrated bars/CF (`MX-VAR-01`, `MX-CHART-*`) |
| Long lists | Top N + Others (`MX-SRT-03`), pagination (`MX-PAGE-01`) |

## Slicer choice (Super Filter)

| Field | Slicer type |
|---|---|
| Date, executive | Date presets / month range calendar (`SF-DATE-02`, `SF-DATE-04`) |
| Date, analyst | Date slider or calendar with range (`SF-DATE-01`) |
| Rolling window | Relative date (`SF-DATE-03`) |
| Hierarchy (Region › Country) | Hierarchy filter (`SF-HIER-01`): inline tree in a panel, or its dropdown variant in a short band |
| ≤ 8 members | Tiles / toggle / checkbox (`SF-FACET-01`); radio is uncaptured |
| 9–200 members | Dropdown facet with search and its own title (`SF-FACET-01`), list or tree; give the open list room |
| > 200 members | Dropdown with search; mass filter for pasted lists (`SF-FEAT-03`) |

Pop-up mode (`SF-FEAT-05`) replaces any of these only after the user approves it.
| Numeric range | Measure / numeric filter (`SF-MEAS-01`) |
| Animated time story | Play axis (`SF-PLAY-01`) |

Vary the control type across a sheet's filters; one style repeated for every
field (for example all tile rows) was rejected in review as repetitive.

## Sample before committing

Look at the data: a flat line, two bars or 40 overlapping series means the
chart is wrong; re-choose before handing off.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### State the question first

- Match the visual to the question, not the data type. Write the question as
  one sentence, confirm the chart is the most direct encoding (position >
  length > slope > angle > area > colour) and check that a simpler visual
  would not do.
- One question per visual: split a visual that answers two; drop one that
  answers none.

### More question guidance

| Question | First choice | Alternative | Avoid |
|---|---|---|---|
| Part-to-whole, by number of parts | Donut for 5 or fewer; sorted bar for 6–15; treemap for 16–30 | 100% stacked bar | Pie with more than 5 slices |
| Composition over time | Stacked columns, 5 series or fewer | 100% stacked columns | Stacked area to compare middle series |

- For one status value, a bullet chart against target (`CH-LIB-08`) is an
  alternative to a KPI card.
- Variance bars diverge from zero and are coloured by polarity (`CH-LIB-27`);
  never draw them from an arbitrary baseline.
- Use a bubble chart only when a third measure carries meaning.
- Location questions: when location is only a ranking, use a sorted bar. This
  skill indexes no Intelligence map chart, so do not propose a map without
  native evidence [open].

### Finance-specific choices

- Scenario comparison over time without IBCS: paired columns with a separate
  variance row or variance bars; overlapping IBCS columns only when IBCS was
  requested.
- Variance bridge: a waterfall from plan (or prior year) to actual by account
  group, entity or driver. Every bar is an existing measure sliced by a
  dimension, or a documented visual calculation (`CH-CALC-01`).
- Plan against run rate: monthly actual columns plus a reference value only
  when a run-rate or target measure exists (`CH-ANLY-01`).
- When plan is drawn as a line over actual columns with different date
  coverage, say so or align the coverage.

### Cardinality heuristics

| Visual | Comfortable limit | When exceeded |
|---|---|---|
| Bar / column | 12–15 categories | Top N + Others, or a search slicer |
| Clustered columns | 3 series or fewer | Small multiples (`CH-MULT-01`) |
| Treemap | 30 tiles or fewer, at most 2 levels | Bar with hierarchy |
| Small multiples | 4–12 panels, shared axis | Filter or Top N |
| Matrix | 5–8 visible value columns | Hide low-value columns; drill |
| KPI cards in one row | 3–4, up to 6 compact | Second sheet or a Matrix |

These are readability heuristics, not product limits or automatic data
reduction. Decide from actual cardinality, label length and space; never drop
members silently, and record any Top N/Others rule and how totals treat it.

### Binding checks

- Use model hierarchies (account, date, geography) where they exist so readers
  can expand and collapse.
- Slice a measure only by dimensions connected to its fact table through
  active relationships; an unconnected pair repeats the grand total on every
  row and looks like bad data. Use an inactive relationship only through a
  measure that activates it.
- Show ratios and percentages only where they are recomputed (KPI cards,
  Matrix cells, tooltips), never stacked or summed.
- Show semi-additive measures (balances, headcount, inventory) at period end,
  and flag a measure that sums over time.

### Per-visual specification

Beyond design mode Step 4, state per visual: the question; bindings by the
field-well names in its feature file; Top N and Others behaviour; data labels
(on for about 12 bars or fewer, off for dense charts); comparison and variance
display with polarity per measure; and interactions only where meaningful.

### Mapping to a feature file

1. Take visual, field-well and setting names verbatim from the feature file.
2. If two library visuals fit, choose the one whose file describes the same
   question and note the alternative.
3. If none fits, choose the closest, record the library gap in the brief and
   never describe settings the feature file does not list.

### Common mistakes

- Defaulting to clustered columns for every question.
- One line chart per measure instead of combining related measures or using
  KPI cards.
- Titles that name the chart type instead of the visual's purpose.

### Analytical selection gate

Before styling, test each proposed visual:

1. **Comparison validity** — compatible population, grain, currency, dates and
   scenario; a plausible actual/plan pair with different coverage is not a
   valid variance.
2. **Denominator and totals** — the approved weighted ratio, distinct count or
   period-end measure; never sums of displayed percentages or averages.
3. **Encoding assumptions** — part-to-whole needs a meaningful common whole
   and compatible non-negative parts; waterfalls need additive contributions
   that reconcile from start to end; scatter needs observations at one defined
   grain, and association is not causation.
4. **Missing and exceptional data** — distinguish blank from zero, incomplete
   from complete periods and unavailable from zero baselines; never hide them
   through formatting, smoothing or silent filtering.
5. **Selection effects** — record Top N and Others, sort order, denominator
   scope, fixed or dynamic axes, and whether filters change the ranking or
   comparison population.
6. **Capability and fit** — a chart recommendation does not establish native
   support; check required labels and panels at the intended zoom and reflow
   rather than accept cropping.

Record a short selection rationale and the rejected alternative in the brief.
If a metric definition is unknown, ask or keep the design explicitly
provisional; never create an unapproved measure to fill the gap.

### More slicer choices

| Field | Control |
|---|---|
| Month for month-end packs | Dropdown or tiles defaulting to the last closed month |
| Scenario or version | Comparison selector, or scoped to visuals that show one scenario; never a sheet filter over actual-against-plan visuals |
| Currency or reporting unit | Single-select, required |

### Variety and multi-measure bridges

- Vary chart types only where each adds information (trend, ranking,
  composition or a reconciled bridge); never trade correct aggregation or
  usable space for variety.
- The companion library built bridges whose bars need different measures
  from a new disconnected axis table plus a selector measure. This skill never
  creates model tables, so use an existing step dimension with one signed
  impact measure (waterfall) or a
  documented visual calculation; the guidance above wins [open].
