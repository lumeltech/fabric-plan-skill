# Report design inspiration

## Context and use

The user supplied ten legacy Power BI report screenshots and explicitly asked
to use them as inspiration for titles, layout, logos, design, colours, themes
and navigation. This reference preserves their reusable visual language, not
the original reports, data or implementation.

Use these as an approved inspiration pool when proposing a new Intelligence
design. They are options, not a mandatory default or report-domain router.
Explicit current user requirements and an existing approved session design
take precedence. Select a coherent combination once, resolve its tokens and
page-role layouts, then persist it through [session design](session-theme.md).
Do not switch theme or navigation between reports merely to use more examples.
Custom combinations remain valid.

Screenshots establish appearance only. Use Fabric Plan Matrix, Intelligence
charts/cards, Super Filters and canvas elements; do not copy Power BI visual
definitions, bookmarks, theme JSON or filter-pane implementation. Exact image,
navigation and interaction encodings still require native evidence.

## Shared visual language

- **Recognizable shell:** a restrained logo/wordmark region, navigation,
  page heading, analysis area and quiet footer. A narrow accent rule can tie
  the shell together without adding another data colour.
- **Clear hierarchy:** small section/breadcrumb, one plain-language page
  title, a short business question, then KPIs and the main analysis. Keep
  navigation labels shorter than page titles.
- **Low-noise surfaces:** white cards on a lightly tinted canvas, or dark
  cards on a darker canvas. Use either hairline borders or subtle elevation,
  consistent radii and generous alignment; avoid heavy shadows on every item.
- **Readable information density:** typically four to six headline cards
  when the metrics justify them; fewer are valid. Keep one title per card,
  clear units and comparisons only when real comparison data exists.
- **Purposeful support:** section titles explain the analysis, short captions
  explain units/scope, and compact drill controls sit near the relevant visual.
- **Quiet footer:** approved organization mark/name and verified source or
  refresh/cutoff context. Do not copy screenshot credits, contacts, dates,
  currency, business names, personal records or illustrative values.

## Palette and theme families

These are proposed, approximate tokens inspired by the screenshots, not sampled
brand colours or extracted Power BI themes. Confirm available fonts and native
theme settings, test contrast for the actual foreground/background pair, and
resolve semantic colours separately before approval.

| Family | Canvas | Surface | Header/rail | Primary text | Accent | Character |
|---|---|---|---|---|---|---|
| Paper and ink | `#FAFAFA` | `#FFFFFF` | `#FFFFFF` | `#172033` | `#334155` | Crisp outlines, restrained tabs and exact-value analysis |
| Midnight and gold | `#F3F4F6` | `#FFFFFF` | `#102735` | `#172033` | `#9A6700` | Dark masthead, warm segmented selection, light analysis cards |
| Dark violet | `#0C1017` | `#151C27` | `#151C27` | `#F1F5F9` | `#A78BFA` | Dark surfaces, violet focus, pale labels and subtle dividers |
| Ocean blue | `#F3F8FA` | `#FFFFFF` | `#0B3A4B` | `#172033` | `#036B91` | Compact dark rail, blue emphasis and spacious white panels |
| Forest and mint | `#F2F7F3` | `#FFFFFF` | `#EAF2ED` | `#173C2A` | `#2F6B46` | Light panel shell, green hierarchy and muted mint companions |
| Indigo neutral | `#F5F6FB` | `#FFFFFF` | `#FFFFFF` | `#172033` | `#4338CA` | Underlined tabs, neutral cards and a distinct analytical series |
| Teal and ice | `#F1F8FA` | `#FFFFFF` | `#FFFFFF` | `#164E63` | `#0E7490` | Thin teal rules, clean comparisons and related-hue composition |
| Soft plum | `#F5F0F7` | `#FFFFFF` | `#E8DFEC` | `#34243F` | `#765386` | Pastel title band/panel, tinted card strips and soft boundaries |

Use a light foreground on dark bands and dark text on light bands; do not
apply the table's primary text to every header automatically. Gold/pastel
fills can use dark labels, while outlined or text-only controls need their
own accessible tokens. These families may be used for any report domain.

Keep actual/prior/plan series distinguishable with labels and line styles as
well as hue. Reserve favorable/adverse/warning colours for business meaning:
an increase is not always favorable, and a theme accent is not a status.
Pale companion colours need visible boundaries or a stronger alternative for
small marks. Do not infer IBCS compliance from a monochrome financial example.

## Layout vocabulary

Choose by the user's preferences and the analytical question, not by the
original screenshot's report title. Convert the chosen composition into
explicit regions, slots and normalized placements in the brief.

| Composition | Reusable arrangement | Adaptation |
|---|---|---|
| Statement and diagnostics | Header/tabs, KPI row, large Matrix with two supporting panels beside it | Use for a primary exact-value analysis plus explanations; not restricted to finance |
| Balanced analysis grid | Dark or light masthead, KPI row, two-column analysis cards | Give the lead chart/table enough room; do not force equal heights when labels differ |
| Ranking and exceptions | Highlight cards, large ranked table, supporting ranking/exception panels | Rank and status must come from verified measures, not decorative podium assumptions |
| Compact navigation rail | Slim logo/navigation rail, title/filter band, KPI row and analysis panels | Numbered destinations also need readable labels or an accessible labeled alternative |
| Full utility panel | Left groups for Pages, Filters and optional At a glance/Related; main canvas on the right | Quick facts must bind live values; unrelated modules are not activated by their presence |
| Wide analytical hero | Compact summaries/status strip above one wide chart or Matrix | Suitable for timelines, trends or dense comparison; statuses need explicit labels and rules |
| Trend and change pair | KPI row, wide multi-period trend and narrower change chart | Align period/scenario context; do not copy screenshot gaps or extrapolated curves |
| Scorecard and comparison | Large Matrix/table with native in-cell trends beside a comparison chart | Keep row identity, units and favorable direction consistent between both views |

The screenshots' outer application border and vertical Filters strip are not
part of the reusable canvas. Do not paint fake host chrome or a nonfunctional
filter drawer. Use a supported Fabric Plan filter/Super Filter configuration,
or an explicitly approved captured alternative.

Plan at the report's target viewport rather than copying screenshot pixels.
Budget the logo/header, navigation, filter expansion, footer and native visual
toolbars before sizing the analysis. Keep text readable and containers fitted;
long tables scroll or paginate internally. Do not inherit tiny footer text,
clipped labels, ambiguous rankings or excessive empty regions from an example.

## Title and narrative system

Use the model descriptions and approved report objective to write:

1. **Section/breadcrumb:** short context, subordinate to the page title.
2. **Page title:** a concrete subject and purpose, such as
   `<subject> Overview`, `<metric> vs Plan`, `<process> Performance`,
   `<entity> Detail` or `<subject> Exceptions`. These are writing patterns,
   not literal placeholders to publish.
3. **Question subtitle:** one short reader question, such as
   "Where are the largest gaps?" or "Which items need attention?"
4. **Visual title:** the metric and breakdown/comparison; include units and
   comparison scope in a short subtitle or tooltip rather than a long title.
5. **KPI:** one metric label; keep comparison captions explicit and separate
   from the title. Do not repeat the label in a second decorative text element.

Do not reuse reference-specific report/company names or copy findings into a
new report. Dynamic headlines must resolve under current filters. A screenshot
timestamp is not evidence of model freshness; display only verified refresh,
as-of or cutoff context. Follow the
[storytelling rules](design-system-part-02.md#9-titles-and-storytelling).

## Branding and logo treatment

Borrow the placement discipline: full wordmark in a roomy header, compact
brand mark in a narrow rail, optional smaller footer mark, and clear separation
between the brand and navigation. Keep the approved asset's aspect ratio,
clear space and light/dark variant; never stretch it into a card.

Ask for the approved original logo asset if it has not been supplied.
Do not crop logos from these screenshots, trace/recreate them, infer ownership,
bundle the old organization as a universal brand, or invent an image URL.
An approved text wordmark or an intentionally empty reserved area can be
proposed while the asset is unavailable; disclose that the logo is pending.
Record asset/variant and placement in the session profile.

Image configuration remains uncaptured in
[text, shapes and images](../features/canvas/text-shapes-images.md).
Branding inspiration is not proof of an upload or image-binding encoding.

## Navigation treatments

| Treatment | Presentation | Behavior to specify and test |
|---|---|---|
| Underlined header tabs | Quiet text tabs with a short active rule | Real sheet destinations, selected state and keyboard focus |
| Segmented pills | Small set of destinations in a shared rounded track | Active/hover/disabled styles and readable labels on each fill |
| Compact numbered rail | Brand mark and short vertical destinations | Label discovery, focus order and any supported expanded alternative |
| Labeled page panel | Pages grouped above filters or contextual helpers | Destination order, selected marker and adequate filter space |
| In-card drill control | Compact text or outlined action near a chart/table heading | Drill field/context, destination and a distinct return action |

Choose one primary page-navigation treatment for the session; drill/return,
Help and Info are complementary actions, not competing navigation systems.
Distinguish sheet navigation from same-page bookmark/view toggles and filter
controls. Do not assume collapse animation, history restoration or bookmark
scope from appearance.

Keep both Help and Info unless the user opts out, even when an inspiration
example shows only Help. Bind real actions, destinations and close/back
behavior through [navigation features](../features/canvas/navigation-buttons.md)
and [session Help/Info rules](session-theme.md#help-and-info-controls).
Record normal, hover, selected, keyboard-focus and disabled styling.

## Adoption and verification

Record the selected family, composition and navigation in
`session_theme.inspiration`, with this reference as provenance and any custom
departures stated. Resolve the actual palette, typography, component states,
branding, title conventions, page-role geometry and filter behavior in the
profile; these are design-brief fields, not new Plan JSON keys.

Retain the native-sample requirements for every feature used. Check the
rendered report at its target viewport, including long titles/navigation,
logo contrast/ratio, KPI labels, filter expansion, Help/Info, drill/return and
selection preservation. A design selection does not authorize report
building, model changes or publishing.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Reproducing a reference on request

When the user explicitly asks to reproduce a screenshot or reference design:

- Decide whether the goal is semantic resemblance or exact native fidelity and
  record it as `reference_fidelity` in the
  brief.
- Record the reference identity, crop and dimensions, exact versus adapted
  intent, the same-kind native readback to copy for each element, typography
  and effect owners, grouping, image-asset dependencies, semantic mapping and
  verification gaps.
- A reference with a different aspect ratio needs an approved geometry
  exception; never silently force it into the session canvas or change the
  standard for unrelated reports.
- Preserve text structure, container membership, navigation state styling and
  image-resource dependencies. Appearance never establishes analytical
  correctness or interaction behaviour.
- Compare the rendered result at matching crop and zoom; when blocked, mark
  fidelity unverified. Saved example reports show how a design was built, not
  approval of their historical geometry or styles.

### More optional families

Design families adds F-01 Calm Financial and the flat
Fabric Quiet preset (Default 1) to this pool on the same terms: options for the
session design, never report-type defaults.
