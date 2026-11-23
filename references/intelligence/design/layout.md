# Layout

<!-- Design topic for the `fabric-plan-skill` skill. -->

## Canvas facts (Fabric Plan)

- Canvas size: `sheet.json → canvasStyle.dimension` (documented
  `DEFAULT_16_9`; native exports also show `RESPONSIVE` sizes). Design on the
  1920 × 1080 reference grid from `design-system.md`; keep the plan's existing
  canvas type.
- Visual geometry is **normalized**: `position {x,y}` and `dimension {width,height}`
  are canvas fractions. Design in pixels; convert when authoring
  (`design/design-brief.md` § Region to geometry conversion).
- Grid/snap helpers in `canvasStyle.gridLineSettings` (`showGridLines`,
  `snapToGrid`) aid UI authoring but do not enforce layout.
- Layers (`layerProperties.order`) define z-order; name them by band
  (`Header`, `Slicers`, `KPIs`, `Main`).

## Grid

- 8 px rhythm, 32 px outer margin, 16–24 px gutters (see `design-system.md` § 2).
- 12 × 12 contract regions. Typical bands:

| Band | Rows | Content |
|---|---|---|
| Header | 1 | Site header (logo, navigation, Help, Info) and hero (breadcrumb, title, question) |
| Filters | 1–2 (or a 2–3 column left rail) | Super Filter slicers, ≥ 80 px tall, max 4 |
| Outcomes | 2 | KPI cards (3–6) |
| Main | 5–7 | Lead chart or Matrix |
| Supporting | 3–4 | Secondary visuals, detail Matrix |

## Super Filter placement

Choose Super Filter position with the layout, not after sizing charts; see
[session design](session-theme.md#design-interview).

- Offer top band, left/right panel, inline groups, popup/collapsible panel or
  Other/custom where supported, weighing filter count, cardinality, selection
  frequency, label length and remaining analysis space.
- Record the choice in `super_filter_layout` ([design brief](design-brief.md))
  and place each filter in an explicitly named region/slot; mixed
  arrangements use `custom` with exact placements.
- Size for title, search, selected chips, clear/reset and usable list/calendar
  content. Define wrapping/scrolling; test long labels/multiple selections.
- Account for dropdown/popup expansion, canvas edges and keyboard access.
  Keep the trigger and current-selection summary visible when collapsed;
  closing must not unexpectedly reset selections.
- Declare affected visuals/sheets and any synchronization; placement does not
  imply filter scope.
- Compare supported control presentations in the
  [slicer feature files](../features/slicers/_index.md). Specify one
  multi-category panel versus independent visuals; leave room for date cells,
  hierarchy indentation, image labels, child counts and measure/variance
  columns.
- For popup/collapsible designs, first get the user's approval for pop-up
  mode; never choose it on your own [confirmed]. Then use the verified
  [Super Filter pop-up mode](../features/slicers/popup-mode.md): the collapsed
  launcher is a search box without a title, so label it separately. Do not
  invent drawer animations or activation keys.
- A one-row tile, toggle or checkbox filter needed about 104px at a 1600x900
  canvas (76px cropped the controls); a dropdown's open list was cropped in a
  76px band. At 1920x1080, titled dropdown facets about 100px tall fitted a
  116px band [saved].

## Composition templates

Optional examples for any report type, not routing rules. A custom user/session
arrangement is equally valid; the coordinate grid requires no particular region
combination.

**A. Hero + side** — KPI row; main region 8 columns (lead chart/Matrix); side
4 columns (trend or ranking).

**B. Two-up** — KPI row; two equal-weight 6-column visuals; full-width detail
Matrix below.

**C. Rail** — left 3-column filter rail with stacked slicers; 9-column body.
One option for many filters; analyst reports need not use a rail.

**D. Planning front door** — header + slicer band; 2–3 KPI cards; embedded
Planning grid full width with ≥ 55% of the height.
Reference-only for future module integration; not selectable for authoring
in the current semantic-model-only release.

## Rules

- Reuse the session's page-role templates and geometry across reports;
  composition examples are initial choices, not a rotation schedule.
- No overlap unless intentional (a background shape behind a group).
- Align left edges and baselines across rows; equal heights within a row.
- Leave space for native chrome: slicer title/search, Matrix toolbar,
  pagination footer, scrollbars. A slicer that only fits its title is unusable.
- Large Matrices: pin row headers, enable pagination or internal scroll; do
  not enlarge the canvas.
- Check at 100% zoom with editor side panes open, and in reading mode.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Storyline and page plan

Settle audience (executive, finance partner, analyst, operations), cadence
(month-end close, forecast cycle, weekly operations, ad hoc), job (track
against plan, explain variance, explore drivers, monitor exceptions) and scope
from the request and model before asking. Then write the storyline, typically
*Where do we stand?* → *Why?* → *Where exactly?* → *What do we do next?*; each
sheet answers one step and has a one-sentence purpose.

- An optional page-plan line extends the discovery sheet list:
  `<sheet title> — role — purpose — key questions — playbooks — main filters`
  (domain playbooks).
- Page-plan extras worth recording: business decision, navigation position,
  grain, units, favourable direction, date and scenario scope, acceptance
  checks and what cannot yet be verified.
- Do not force every sheet into one analytical pattern; distinct page roles
  can use distinct session templates, chosen once and reused.

### Composition bands

- Header: purpose, scope and short instructions need room for two or three
  readable lines.
- Scope controls: budget the title, search, selection control and menu height.
- Outcomes: a few KPI cards and/or a concise trend, without repeated titles or
  clipped numbers.
- Supporting analysis never covers the lead region. A healthy gap matters
  more than fitting another chart.

### Growing a sheet in layers

Build in layers and stop when the sheet answers its questions; each layer must
earn its space:

1. **Core** — data visuals and filters that answer the questions.
2. **Context** — title, subtitle with period, scenario and unit, comparison
   captions on KPI cards.
3. **Guidance** — a short insight or instruction only where readers need it.
4. **Structure** — shapes or panels only when three or more visual groups need
   separating and spacing alone fails.
5. **Identity** — approved logo or icons from the session profile.

When a sheet gets crowded, split it rather than shrink visuals below readable
size.

### Geometry evidence

- Saved sheets can store element geometry in pixel or percentage scaling
  units; read `canvasStyle.dimension.elementScalingUnit` before converting or
  auditing [saved].
- When repairing a user-authored sheet, keep its deliberate composition (for
  example a full-bleed decorative header with custom title or filter
  placement): record exact bounds and intentional overlaps instead of silently
  reflowing. New decorative exceptions need approval; keep content inside the
  canvas and check foreground contrast and control clickability.

### Optional companion budgets

**Optional (companion default):** per-role visual budgets, stricter than the
12-visual limit; they apply only when the user or session design selects them
and never override the session theme, supplied designs, report-inspiration
guidance or IBCS opt-in.

| Page role | Typical content | Budget |
|---|---|---|
| Executive summary | 3–4 KPI cards, one hero trend or bridge, 1–2 supporting visuals | 7 elements or fewer |
| Variance analysis | Statement or cost Matrix with variance, bridge, variance by organisation | 8 or fewer |
| Analytical exploration | Filter rail, 3–4 linked charts, detail table | 9 or fewer |
| Operational monitor | Status tiles with thresholds, exception table, freshness | 8 or fewer |
| Detail or drill | One Matrix or table, filters, totals | 1–3 |

Count title text and slicers separately from data visuals; more than about
7 ± 2 visual groups overloads readers, so split the sheet.

### Optional companion grid

**Optional (companion default):** a fixed 1600 × 900 authored canvas with 40 px
outer margins, 8 px snapping and gaps of at least 16 px; it applies only when
the user or session design selects it and never overrides the session theme,
supplied designs, report-inspiration guidance or IBCS opt-in. When selected:

- Twelve 112 px columns with 16 px gutters span x 40–1560; N columns are
  128·N − 16 px wide and column c (counting from 0) starts at x = 40 + 128·c.
  Common spans: 2 = 240 (slicer, rail), 3 = 368 (KPI 4-up), 4 = 496 (KPI
  3-up), 6 = 752 (half), 8 = 1008 (hero), 10 = 1264 (beside a rail), 12 = 1520
  (full width).
- Header band y 40–104: title on the left (about 40 px) over a 24 px context
  line; up to three scope controls of 240 × 56 on the right where supported.
  Content y 120–856, inside the 860 px bottom margin; gaps of 16 px within a
  group and 32 px between groups where space permits.
- Supporting charts at least three columns by about 300 px; tables at least
  about 300 px tall. Keep three or fewer visible slicers in the header and
  move four or more to a rail that they fill at least halfway.
- Record approved rectangles as `px_rect` in the
  brief; authoring divides x and
  width by 1600 and y and height by 900, as for any pixel plan
  (canvas layout). Reflowing an
  existing sheet changes only outer geometry; keep native internals,
  identities and bindings, and record the original state.

| Pattern | Slots (x, y, w × h) |
|---|---|
| E1 KPI strip, hero and side pair | KPIs at x 40/424/808/1192, y 120, 368 × 120; hero 40, 256, 1008 × 600; side 1064, 256, 496 × 288 and 1064, 560, 496 × 296 |
| E2 three KPIs and two halves | KPIs at x 40/552/1064, y 120, 496 × 120; charts at x 40 and 808, y 256, 752 × 600 |
| V1 Matrix, bridge and trend | KPIs as E1; Matrix 40, 256, 752 × 600; bridge 808, 256, 752 × 288; trend 808, 560, 752 × 296 |
| A1 filter rail | Rail 40, 120, 240 × 736; main 296, 120, 1264 × 360; lower panels at x 296 and 936, y 496, 624 × 360 |
| C1 small multiples | Six panels of 496 × 360 at x 40/552/1064, y 120/496, shared axes |
| D1 detail | One Matrix or table at 40, 120, 1520 × 736; scope controls in the header |

Adapt sizes to the content, but keep the grid, non-overlap and canvas bounds.

### Presentation checks

- Treat cropped controls and visuals sitting on top of other content as
  functional failures, not cosmetic ones.
- Gutters of 16–24 px are a design starting point, not a platform
  requirement.
- Besides 100% zoom with side panes open and reading mode, inspect the
  narrower viewport in which the report will be presented.
