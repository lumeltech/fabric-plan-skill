# Pre-flight checklist

<!-- Design topic for the `fabric-plan-skill` skill. Run before handing a Design Brief to authoring, and again on the built definition. -->

## Identity

- [ ] Tone and signature recorded and visible (palette, type, container style, recurring move)
- [ ] `ibcs` explicitly true/false; IBCS references loaded only if true
- [ ] Session profile persisted and copied into brief; supplied designs honored
- [ ] Fresh-session choice differs from available prior designs unless reuse requested
- [ ] When using legacy-report inspiration, chosen family/composition/navigation
      and departures recorded; no reference data, contacts or old findings copied
- [ ] Logo uses an approved asset/variant with correct ratio and clear space,
      or is explicitly pending/omitted; no screenshot crop or invented image binding

## Design choice

- [ ] Each sheet records a chosen example or Custom, layout name, user/session rationale
- [ ] No report type, industry or reference screenshot dictates theme/layout
- [ ] Corresponding page roles reuse session layout templates across reports

## Data binding

- [ ] Every field resolves in `_brief/field-registry.md`
- [ ] Ratios not summed; variance pairs explicit; lower-is-better marked
- [ ] Default slicer selections bound the data volume
- [ ] Monthly axes prefer the model's Month field where appropriate; sort order
      verified and multi-year scope cannot merge same-named months unintentionally
- [ ] Scenario measures do not internally force a different scenario; cards,
      statement rows and totals reconciled under identical filters

## Layout

- [ ] Title element on every sheet; business question as subtitle
- [ ] Regions non-overlapping; gutters consistent; Super Filters fit chosen regions
- [ ] Super Filter position, sizing and overflow/open-state behavior explicit
- [ ] Filter chips, search, clear/reset and selection summaries remain accessible
- [ ] ≤ 12 data visuals and ≤ 4 slicers per sheet (or justified)
- [ ] Space audit filled; empty space justified
- [ ] Native chrome accounted for (slicer search, Matrix toolbar, pagination)
- [ ] Custom dimensions use the native Custom type and survive readback;
      bottom whitespace checked against canvas aspect ratio and viewport fit
- [ ] Date inputs/presets and long selections are unclipped in Reading mode;
      space-heavy facets use titled dropdowns whose open list has room;
      no date preset is preselected unless intended
- [ ] Filter controls vary by cardinality; pop-up mode only with the user's
      approval, and every approved pop-up launcher has a label
- [ ] Background panel drawing and outer padding checked independently;
      foreground visuals do not mask inset borders or create stepped seams
- [ ] Canvas and wallpaper treated as distinct surfaces when requested;
      wallpaper-only edits preserve canvas color, size and visual geometry

## Visuals

- [ ] Chart choice matches the question (`design/chart-selection.md`)
- [ ] Bars meaningfully ordered; time in natural order; scenario styles follow session profile
- [ ] Colour map consistent; legends/keys visible
- [ ] Titles plain language; no raw field names; percentages formatted
- [ ] KPI cards show change ▲/▼ and comparison caption
- [ ] Each KPI has exactly one title; comparison text/series only for bound roles
- [ ] Requested sparklines have a category and applied native chart type;
      visible trend and unchanged headline/ratio semantics checked after rendering
- [ ] Split KPI items do not overlap; every variance badge remains visible,
      with text alignment checked separately from badge position and background
- [ ] Every required comparison line is visible in every small-multiple panel;
      point-label visibility checked independently of axes, titles and legends
- [ ] Calculated subtotal/profit rows excluded from additive totals; generic
      grand total hidden when inappropriate, not used as an arithmetic fix
- [ ] Cost overspend/underspend colors tested against business favorability;
      an IBCS template is not accepted as proof of strict IBCS compliance

## Interaction

- [ ] Cross-filter vs highlight decided; consistent across sheets
- [ ] Sync slicers declared where needed
- [ ] Bookmarks ≤ 8, named for readers
- [ ] Help and Info each have visible controls, real targets/content and close/back,
      or explicit user opt-out; no filter reset when opening explanatory content
- [ ] After the final publish, every tab and Help/Info/Back control opens its
      intended page; destinations use sheet numeric ids (`CV-ELEM-02`)
- [ ] Navigation selection/focus/hover states, labels, real destinations and
      drill/return tested; no decorative imitation of the source application's chrome

## Accessibility

- [ ] Contrast, colour-independent cues, reading order (`design/accessibility.md`)

## Final squint test

- [ ] Blur the sheet: lead visual and KPIs stand out; slicers recede
- [ ] Session reports keep the same theme and page-role geometry; content varies

## Dashboard standards

- [ ] Every item in the [dashboard standards checklist](dashboard-standards.md#checklist)
      passes on the built report, or a recorded user exception covers it

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Content truth

- [ ] Titles and subtitles match the effective metric, comparison, period,
      grain, unit, dimension and ranking
      (content-bound titles)
- [ ] After any filter change, values and static subtitles rechecked under the
      saved context
- [ ] Measure and dimension pairs connected; semi-additive measures at period
      end; like periods compared; at most two comparisons per visual
- [ ] Top N/Others, denominator scope and blank-versus-zero handling recorded;
      selection rationale and rejected alternative in the brief

### Craft

- [ ] One purpose per sheet; no single-value card in the hero slot; no
      duplicate KPI or callout repeating a value
- [ ] No text box duplicates a visual's native title
- [ ] Element and property review
      done, including chart orientation for long labels
- [ ] One unit and scale per sheet, stated in the subtitle; each colour
      encodes information; legend order matches data order
- [ ] Spacing budgets checked separately; nothing cropped at intended zoom,
      including opened controls; overflow never hidden
- [ ] Finishing pass complete; rendering
      checks recorded separately from readback, blocked checks marked
      unverified

### Optional companion checks

**Optional (companion default):** these checks apply only when the user or
session design selects the matching companion defaults and never override the
session theme, supplied designs, report-inspiration guidance or IBCS opt-in.

- [ ] 1600 × 900 canvas, 40 px margins, 8 px-snapped outer geometry, gaps of
      at least 16 px
- [ ] Every visual has its own container fill, one border style and one
      radius; KPI cards bordered
- [ ] No scrollbars in any authored content, without dropping data
- [ ] Design family, appearance, density and decoration recorded
