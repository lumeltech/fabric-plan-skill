## Contents

- [How to read this file](#how-to-read-this-file)
- [Overall experience](#overall-experience)
- [Building visuals](#building-visuals)
  - [KPI cards](#kpi-cards)
  - [Charts](#charts)
  - [Tables and Matrix](#tables-and-matrix)
  - [Slicers](#slicers)
  - [Page navigation](#page-navigation)
  - [Titles and subtitles](#titles-and-subtitles)
  - [Text boxes](#text-boxes)
  - [Color](#color)
- [Layout principles](#layout-principles)
- [Copies and repairs](#copies-and-repairs)
- [Checklist](#checklist)

<!-- Design topic for the `fabric-plan-skill` skill. User-confirmed dashboard standards distilled from user-finalized saved reports: principles for visual building and overall experience, plus small craft techniques. Apply to every new report and to repairs within the requested scope. -->

# Dashboard standards (user-confirmed)

## How to read this file

These are the user's standing rules for how dashboards should look and work
[confirmed]. Learn the principle, then apply it to the report at hand.
Pixel values, positions and canvas sizes below are examples from one
reviewed report, not defaults: canvas size, shell geometry and sizes are
chosen per report [confirmed].

Tags: [confirmed] stated by the user; [saved] observed in the user-finalized
saved definitions the user designated as the reference.

The standards govern craft and experience. The session theme still owns
palette, fonts, brand and navigation style ([session design](session-theme.md)).
For the order of work on a multi-page report (mockup, pilot page, user polish,
cloning, render checks), follow the [dashboard build playbook](dashboard-playbook.md).
An explicit request for one report overrides a standard; record that
exception in the brief. IBCS notation applies only on request.

## Overall experience

What users need from every dashboard [confirmed]:

- **Clean and calm.** Every element answers a question. Remove decorative
  text, duplicate titles, redundant labels, unused shapes and clutter such as
  markers or overlays nobody asked for.
- **A clear reading order.** Headline KPIs first, then trends and drivers,
  then exact detail in a Matrix or table [saved].
- **The same shell on every page.** Navigation, filters, header, context
  line, footer and Help/Info controls sit in identical positions with
  identical sizes, so users never relearn a page.
- **Easy to operate.** A page navigator, a few standard filters, a short
  context line about the active scope, and Help/Info behind small icon
  buttons on hidden pages without slicers [confirmed].
- **Nothing broken or cropped.** No scrollbars on text, no clipped labels,
  no visuals hidden behind shapes, no empty bands beside a visual.
- **Trustworthy numbers.** A currency symbol only on monetary values and
  only when the user specified a currency (USD in the reviewed reports);
  otherwise plain numbers. Counts stay plain; ratios show as true
  percentages; totals never sum ratios; a source and coverage footer states
  scope [confirmed][saved]. A symbol is not a conversion; state the source
  currency.

## Building visuals

### KPI cards

- Keep cards simple: title, value, one comparison line (two when the approved
  design compares with both prior year and budget) and the native sparkline
  (`KPI-CHART-01`) [confirmed].
- Make the sparkline clearly visible: give it roughly a third of the card
  height and never shrink it to fit more text [confirmed][saved].
- No data labels and no point markers on sparklines unless the user asks
  [confirmed]. Saved off-state: `dataLabel.labelStyle.<measure>.enabled:
  false` with line markers disabled [saved].
- Clear type hierarchy: value largest, title medium, captions smallest; the
  same sizes for the same roles on every card (reviewed: 30, 14 and 12 px)
  [saved]. Plain card interiors: the user removed colored card fills
  [confirmed]. One title per card, inside the card.
- Give each measure one colour for its card accent and sparkline line and
  keep it on every page; set it on the measure-keyed sparkline style
  (`KPI-CHART-01`) [saved].
- Ratio cards (margin %, discount %) compare values, such as "vs PY 29.6% ▼",
  rather than showing a percent change of a percent [saved]. Lower-is-better
  measures such as discount or cost invert the arrow colours (`KPI-VAR-01`).

### Charts

- Use the native chart title for title and subtitle
  (`chartCustomTitle.showTitle: true`): bold title over a smaller, muted,
  italic subtitle [saved]. No text boxes for chart titles.
- Data labels off by default; enable them only when every label fits
  without overlap, typically few categories in a wide plot [confirmed].
  Integrated variance bars keep their built-in labels [saved].
- Line charts: no point markers, data labels, sparklines or analytics
  overlays by default; ask the user [confirmed]. Deviation lines and bands
  need space; leave them out of compact charts [confirmed].
- One chart text size across the report for axis labels, legends, data
  labels and footers (reviewed: 13 px). Setting the global font in the UI
  rewrote every element to that size [saved].
- Bars sorted by value; time in natural order.

### Tables and Matrix

- Use the built-in Matrix title and subtitle (`MX-HF-01`) instead of text
  boxes, and let the Matrix grow into the freed space [confirmed][saved].
- Fill the width: when the Matrix is wider than its columns, increase every
  column's width (row label, each hierarchy level and each measure) until
  together they fill the visual. Keep label columns wider than number
  columns. Rebalance after adding or hiding measures. Leave no empty band
  on the right and force no horizontal scroll at normal zoom (`MX-COLW-01`)
  [confirmed][saved].
- Compact, readable rows and headers with one text size (reviewed: rows
  28–32 px, headers 30–36 px, 12 px text) [saved].
- Use Matrix features before adding visuals [confirmed]:
  - hierarchy expand/collapse; Table layout for full-detail lists so each
    level gets its own column (`MX-LAY-01`) [saved];
  - grand total at the top and frozen for long lists, or at the bottom of a
    short grid, labelled `Total` (`MX-TOT-01`) [saved];
  - native variance columns from the scenario buckets; hide the absolute
    column when width is tight and keep the relative % (`MX-VAR-01`) [saved];
  - a currency prefix only on monetary measures; Sum totals for additive
    measures and none for ratios [saved].
- Short plain headers on every column (Qty, PY, GM %), renamed at the measure
  assignment; never a raw measure name (`MX-VAR-01`).
- One visual idea per Matrix: in-cell bars on the lead measure, red/green on
  variance columns, or a light-to-dark colour scale for a two-dimension
  heatmap or a ranked % column (`MX-CHART-01`, `MX-CF-02`) [saved]. Colour
  rules paint only on engine ids from a user-saved Matrix.
- Sort ranked lists by the lead measure (`MX-SRT-01`) [saved]; show percent
  columns with one `%` sign and consistent decimals (`MX-NUM-01`); give
  hierarchy parents bold text and a clear indent (`MX-HIER-01`); hide the
  Rows/Columns status bar (`MX-VIS-01`).
- Whenever rows hold two or more fields, show the expand/collapse icons
  (plus/minus boxes) so readers see the hierarchy can open and close;
  single-level rows need none (`MX-HIER-01`) [confirmed].

### Slicers

- One shared filter panel per analytical page, identical in position, size,
  order and labels on every page [confirmed][saved].
- Only the 3–5 decision filters, such as the period and the main business
  hierarchy; never every column [confirmed].
- Pick the control by list length: tile chips for short lists such as year,
  region or channel, with search off and every chip visible in one row
  [confirmed]; a dropdown facet showing its own title for long lists such as
  brand, city or customer, with room for its open list [confirmed]. Never use
  pop-up mode (`SF-FEAT-05`) without first asking the user and getting
  approval [confirmed]. Single-select the period with a saved default;
  multi-select business dimensions [saved]. No slicers on Help and Info pages
  [confirmed].
- Page-specific filters go at the right end of the same band, in the same
  slots on every page; their own titles replace separate text labels [saved].

### Page navigation

- One tab navigator in the header lists the analysis pages in page order, the
  active tab underlined; Help and Info are separate outlined buttons beside
  it, and Help and Info pages carry a Back to report button [saved].
- Tab and button destinations are sheet numeric ids, which follow creation
  order, not position. Keep a name → id map and click every tab and button
  after pages are added (`CV-ELEM-02`).

### Titles and subtitles

- Page header: one title and one plain-language subtitle.
- Every chart, Matrix, table and KPI card carries its own native title and
  subtitle [confirmed]. A text box above a visual carrying its title is a
  defect; during repairs remove it and give the height to the visual [saved].

### Text boxes

Text must never show a scrollbar [confirmed]:

1. Turn padding off so no gap sits between the text and the box edges and
   corners. Use a 0 corner radius on large titles [saved].
2. Size the height for the actual lines, about twice the font size for one
   line and a few pixels more for small text (reviewed: 12 px text in 28 px,
   13 px in 30 px, 17 px in 34 px, 28 px titles in 51 px) [saved].
3. If a scrollbar still appears, add a few pixels of height, for example
   22 → 25 px [confirmed]. Never shrink the font to fit.
4. Check in Reading mode, where scrollbars show up.

### Color

- Use the same colors for the same meaning across the whole report
  [confirmed]: one color per scenario or measure role in every visual
  (reviewed: actuals teal, prior year slate, budget amber), one
  favorable/unfavorable pair, and the same rail, header and panel colors on
  every page [saved].
- Canvas background and wallpaper always use two distinct colors
  [confirmed].
- The session theme chooses the palette; the report keeps it unchanged.

## Layout principles

- Canvas size is chosen per report and model; keep the plan's canvas type
  and never assume a fixed size such as 1600 × 900 [confirmed].
- Define the shell once per report and reuse it unchanged on every page.
  The reviewed report used a left rail (about 18% of the width) for logo,
  navigator, filters and Help/Info; a header (about 20% of the height) for
  title, subtitle and context; a content band; and a one-line footer [saved].
  Another used a top shell: a dark header band (about 10% of the height) with
  title, page tabs and Help/Info; a filter band; a KPI row; a hero panel about
  two thirds wide beside a side panel; and a one-line source footer [saved].
  Other shells are equally valid when chosen in the design interview.
- One gutter and one panel inset for the whole report (reviewed: about 1% of
  the width for gutters, smaller insets inside panels) [saved].
- Equal sizes within a row and aligned edges; KPI rows split the content
  width into equal cards [saved].
- Fill space deliberately: when an element is removed, grow the remaining
  visual into the space instead of leaving gaps [confirmed][saved].
- Layer order: background shapes behind, content in front; check every
  visual is visible after reordering [confirmed].

## Copies and repairs

- A copy must match its source without user rework [confirmed]: set the
  semantic-model URL at creation, re-upload uploaded images in the new item
  (`CV-ELEM-01`) and compare a semantic readback (see
  [Copying a plan](../management-part-02.md#copying-a-plan)).
- When the user edits a report, diff the newest readback against the last
  verified one before the next change, and apply deliberate edits as the
  standard for the remaining pages. A pilot page the user polished in the
  editor is the template for every later page
  ([playbook](dashboard-playbook.md#7-clone-the-remaining-pages)) [confirmed].

## Checklist

- [ ] Shell identical on every page; canvas and wallpaper colors differ
- [ ] Every visual uses its native title and subtitle; no title text boxes
- [ ] KPI sparklines clearly visible; no sparkline labels or markers unless
      requested
- [ ] Chart labels only where they fit; line charts without markers or
      labels unless requested; one chart text size
- [ ] One shared panel of 3–5 standard filters per analytical page; none on
      Help and Info; filter chips fully visible; long lists as titled
      dropdowns; pop-up mode only with the user's approval
- [ ] Every tab and every Help, Info and Back button opens its intended page
- [ ] Each Matrix fills its container, and its columns fill its width
- [ ] Matrix headers short and plain; grand total labelled; one `%` sign per
      percent; every colour rule and bar paints; multi-level rows show
      expand/collapse icons
- [ ] No text box shows a scrollbar in Reading mode
- [ ] Same color for the same meaning everywhere; currency only where
      requested and monetary; ratios as %
