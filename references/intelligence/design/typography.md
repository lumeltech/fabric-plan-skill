# Typography

<!-- Design topic for the `fabric-plan-skill` skill. -->

- One family: Segoe UI / Segoe UI Semibold (unless the team design MD says otherwise).
- At most four sizes per sheet: title, visual title, body, KPI value.
- Hierarchy by size and weight, not by colour.

| Role | Size | Weight |
|---|---|---|
| Sheet title | 20–24 | Semibold |
| Visual title | 14 | Semibold |
| KPI value | 28–32 | Semibold |
| Body, axis, Matrix cells | 10–11 (9 min) | Regular |
| Captions, notes, footers | 9–10 | Regular |

## Where it is set

- Matrix: `visualState.globalStyles` (`fontFamily`, `fontSize`,
  `headerFontSize`, `rowHeight`) — feature `MX-FMT-01`.
- Super Filter: `visualState.toolbarSettings` (title) and
  `categoryCustomizeSettings` (items) — feature `SF-DISP-01`.
- Charts / KPI cards: chart format settings — capture a native sample.
- Text elements: element properties — feature `CV-ELEM-01`.

## Rules

- Titles in sentence case; no raw field names.
- Numbers right-aligned; consistent decimals per measure.
- Avoid all caps except small eyebrow labels.
- Tooltips use the same family and a readable size (≥ 11).

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Content-bound titles

A companion user correction: always update a title to match what is actually
shown, and make it particular rather than a generic caption.

- Establish the effective metric, aggregation, actual/reference pair, period
  start and end, grain, dimension, units and ranking basis first; derive the
  title and subtitle from them, not from a copied caption or an intended but
  unverified calculation.
- Keep the title concise and put scope in the subtitle, for example
  `<metric> | <actual> vs <reference>` over `<period> | <currency and scale>`,
  only when the bindings and effective date scope establish those statements.
- Period and scenario words (MTD, YTD, full year, forecast, latest estimate,
  variance, outliers) are business claims. Use them only for genuine
  calculations over one consistent metric; never relabel a different measure
  as a period, call actual plus open forecast "forecast" without explaining
  the blend, or imply a variance ranking when the sort is by value.
- Update the title and subtitle whenever the metric, binding, scenario, date
  scope, grouping, ranking or filter behaviour changes, on every build and
  repair.
- Dynamic, data-bound titles need a tested native binding; do not invent token
  syntax or claim dynamic behaviour [open]. Without one, keep the visible
  scope true for every allowed selection or get approval for a fixed scope.
- Recheck negative, blank, zero and no-data states, selected versus all
  members, calendar versus fiscal periods and actual coverage. A hard-coded
  year, member or end month must not contradict a live selector or the
  calculation cutoff.
- A fixed reporting year does not freeze a latest-actual-month measure:
  approved dated static titles must be regenerated after each source refresh,
  a maintenance dependency to disclose.
- Title correctness is a semantic acceptance check, separate from typography
  and spacing; a polished but inaccurate title fails.

### Fit checks

- Allocate space for the actual text, search or menu chrome, labels and
  numbers at 100% zoom, and check contrast against native fills and images,
  not only the intended background.
- Budget title and subtitle line heights, paragraph spacing, their gap,
  wrapping and inset separately
  (spacing budgets); inspect the
  rendered result rather than copying a line-height value.
- Rich-text headings can carry paragraph or child styles that differ from the
  editor root style; read the effective child styles before judging a heading
  size [saved].
- Saved chart title allocations differ by chart type and content; budget them
  per component instead of forcing one title height [saved].
- Keep rich text, chart notes, Matrix notes, annotations and markers with
  their true owners (`CV-ELEM-01`, `CH-NOTE-01`, `MX-NOTE-01`, `CV-ANN-01`);
  they are not interchangeable text widgets.
- Avoid clipped titles, repeated measure names and unreadable axis labels.

### Header copy

Headers explain what readers can do and how outputs connect, in two or three
sentences: what to select, what colours or markers mean, how results update.
Never show IDs, API steps or internal generation notes, and leave the header
room for two or three readable lines.

### Optional companion type ramp

**Optional (companion default):** a larger type ramp; it applies only when the
user or session design selects it and never overrides the session theme,
supplied designs, report-inspiration guidance or IBCS opt-in.

| Role | Size | Weight |
|---|---|---|
| Sheet title | 28 | Semibold |
| Visual title | 16 | Semibold |
| KPI value | 28–32 | Semibold |
| Body and labels | 12–14 | Regular |
| Subtitle, caption | 12 | Regular, secondary colour |

Segoe UI with a system-ui fallback; still no more than four sizes per sheet.
