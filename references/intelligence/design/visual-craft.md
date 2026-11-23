## Contents

- [Title hierarchy: one title per idea](#title-hierarchy-one-title-per-idea)
- [Effective spacing budgets](#effective-spacing-budgets)
- [Element and property review](#element-and-property-review)
- [KPI card surfaces](#kpi-card-surfaces)
- [Optional companion framing](#optional-companion-framing)
- [Optional no-scroll acceptance](#optional-no-scroll-acceptance)
- [Finishing pass](#finishing-pass)
- [Checklist](#checklist)

<!-- Design topic for the `fabric-plan-skill` skill. Finishing craft merged from the companion Intelligence authoring library; optional companion defaults never override the session design. -->

# Visual craft and finishing

Merged from the companion Intelligence authoring library. Additive only:
session design, the design system and
the other design topics take precedence; companion defaults appear only as
labelled optional guidance. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

Apply this craft layer to every new or repaired sheet without waiting for a
polish request, within the authorized scope. It complements
layout (canvas, grid, gaps), colour and
typography; native settings stay with their feature files.

## Title hierarchy: one title per idea

- The sheet title and subtitle live once, in the header. Every other title is
  the visual's own native title: the chart title, the Matrix or table header,
  or the KPI card title (`KPI-FMT-01`).
- Before adding a text box near a chart, table or KPI card, check whether the
  visual exposes a title or caption. If it does, set the title there and add no
  text that repeats it.
- Standalone text is justified only for the sheet header or subtitle, a short
  callout that restates no visual's title, a label for a group of visuals that
  no single member can carry, or a visual family that a fresh native readback
  shows has no title capability.
- On a repair whose requested scope includes that visual, remove a text box
  that repeats an adjacent native title after
  confirming it carries no note, annotation or instruction, and reclaim its
  space. Leaving a visual out of an update request did not delete it; confirm
  removal by readback [saved].

## Effective spacing budgets

- Treat outer margin, gutter between visuals, container padding,
  title/subtitle gap and plot margins as separate budgets. A valid outer
  rectangle and a 16 px neighbour gap do not prove that titles, labels or
  controls fit inside it.
- Size a heading for its actual title and subtitle line boxes, paragraph
  spacing, deliberate gap and top/bottom inset, and check wrapping. Do not give
  every two-line heading one fixed height or rely on font size alone.
- For charts, reserve title/subtitle, legend, headers, axes, ticks and labels
  before sizing the plot, and keep a clear gap between subtitle and plot. A
  native chart title height is its allocated area, not the title/subtitle gap
  [saved].
- Apply padding per component and mode: flat panels still need usable inset,
  compact filters should not inherit chart-card padding, and padding is never
  disabled globally as a shortcut. Stored padding values have no effect while
  padding is disabled; read the enable and uniform/custom flags first [saved].

## Element and property review

Consider each element deliberately before authoring, even when the answer is
"not needed":

| Element | Review |
|---|---|
| Header, title, subtitle | Header purpose, title hierarchy, explicit text contrast, period/scenario/currency/active scope; decorative full-bleed bounds versus inset content |
| Shapes and layers | Shape type, drawing fill and border versus container effects, padding, radius, shadow, layer order, intentional overlap, clickability (`CV-LAYER-01`) |
| KPI and chart frames | Outer border, corner radius, padding and background; the KPI's internal accent is a separate surface |
| Charts | Orientation suited to the labels, natural financial order, axes, number format, legend and label legibility |
| Visible controls | Native control identity, field and selection, interaction scope, clear/default behaviour and actual selection tests |
| Geometry | Saved scaling unit, canvas size, margins, header exceptions, gutters, hidden layers and every stored placement |

## KPI card surfaces

- A KPI card has two different borders: the outer container border (element
  styling) and the internal ribbon or accent line, which is often zero on
  single cards. Do not conflate them or show two nested borders [saved].
- Review the card's chart background, panel background, outer surface and
  actual text spans together: a light card can keep an unrelated dark plot
  fill until it is aligned [saved]. An emphasized filled card needs readable
  text on its actual fill.
- Emphasize one outcome card only when warranted; do not fill every card.
- Card trellis panels keep their own panel border, which does not replace the
  card's outer frame (`KPI-MULT-01`) [saved].

## Optional companion framing

**Optional (companion default):** every data visual (chart, Matrix or table,
KPI card, slicer) gets its own container fill distinct from the canvas, a quiet
border and one shared corner radius, and every KPI card has a visible outer
border. It applies only when the user or session design selects it and never
overrides the session theme, supplied designs, report-inspiration guidance or
IBCS opt-in; flat borderless profiles remain valid session choices.

| Property | Companion default | Notes |
|---|---|---|
| Border | 1 px, enabled, stroke token, all sides | Outer container border, not the KPI accent |
| Corner radius | 8 px, one value for the sheet | Do not mix square and rounded containers |
| Padding | 12–16 px effective inset for cards and charts | Compact controls may use reduced or zero outer padding [saved] |
| Spacing | 16 px within a group, 32 px between groups | See the companion grid |
| Shadow | None | Depth comes from fill, border and radius |
| Decorative shapes | Behind data visuals, for grouping only | Never over data or text |

- Set framing on each visual's own element styling (`CV-LAYER-01`), not with a
  shape behind every visual; a per-visual backdrop shape may drift out of
  alignment on resize or reorder [open]. A shape still suits framing a group
  such as a KPI band.
- Record approved deviations (another radius, a sharp-cornered IBCS theme, an
  intentionally borderless accent) in the brief so later repairs keep them.
- Verify in a fresh readback and on the rendered sheet that container fills
  differ from the canvas and that content never touches a border.

## Optional no-scroll acceptance

**Optional (companion default):** no horizontal or vertical scrollbars anywhere
in authored content (sheet, chart, Matrix, trellis, filter body or opened
member list). It applies only when the user or session design selects it and
never overrides the session theme, supplied designs, report-inspiration
guidance or IBCS opt-in. Otherwise long Matrices and tables may scroll or
paginate inside their container as the
design system allows.

- Fit content through sizing, reflow, concise nonessential copy, searchable
  controls or separate navigable sheets; never drop members or data to fit.
- Never conceal overflow with clipping, hidden scrollbar decoration, zoom
  reduction or illegible text. If no native control or layout meets both
  requirements, report the limitation.
- Saved geometry, disabled scrollbar settings or a successful import do not
  prove absence of overflow. Inspect the normal view and opened controls at the
  intended zoom, or record the check as unverified.

## Finishing pass

Treat a correctly bound, layout-valid sheet as a draft until this pass is done.
On repairs it does not authorize an unrelated restyle or theme reset.

1. **Hierarchy and contrast** — check the heading, quiet subtitle, visual
   titles, KPI captions and values at normal size; inspect rich-text children,
   not only root styles.
2. **Fit the control, not its rectangle** — check native inset,
   dropdown/search/clear chrome and selected text; avoid double padding on
   compact selectors; test opening, selection and clear/reset separately.
3. **Readable numbers** — check currency or percentage, scale, precision and
   variance polarity; use explicit signs where they show direction.
4. **Remove nonessential chart clutter** — review label placement, axis
   readability, redundant axis titles and inherited average or reference
   overlays; keep meaningful titles, units and necessary baselines; choose
   label density for the space.
5. **Protect meaning while polishing** — review styling changes separately from
   filter selections, bindings, dormant settings and save-time geometry; if
   scope changed, reconcile values and titles again.
6. **Prevent cropping** — at normal zoom, inspect every card, panel and
   control, including opened ones. If anything clips, enlarge it, reflow or
   split the sheet; never hide overflow or shrink text below legibility.
7. **Verify** — record definition readback and a native 100% viewing check
   separately; when UI access is blocked, report rendering as unverified.

## Checklist

- [ ] No duplicate titles; every native title is set on its visual
- [ ] Spacing budgets checked separately; headings fit their actual text
- [ ] Element and property review done; KPI outer frame and accent intentional
- [ ] Nothing cropped at intended zoom, including opened controls
- [ ] Finishing pass complete; rendering recorded separately from readback
- [ ] If selected: companion framing and no-scroll checks pass; approved
      deviations recorded in the brief
