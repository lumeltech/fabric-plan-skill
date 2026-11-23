---
design_system: Session-selected report design
version: 1.1
applies_to: Fabric Plan Intelligence Sheets
---

## Contents

- [1. Design identity](#1-design-identity)
- [2. Canvas, grid and shell](#2-canvas-grid-and-shell)
- [3. Typography](#3-typography)
- [4. Colour system](#4-colour-system)
- [5. Navigation](#5-navigation)
- [6. Drill, interactions, bookmarks](#6-drill-interactions-bookmarks)
- [7. KPI cards](#7-kpi-cards)
- Sections 8–14 (charts, titles, numbers, branding, model, workflow, checklist): [design-system-part-02.md](design-system-part-02.md)
- [Additional details](#additional-details)

<!-- Design topic for the `fabric-plan-skill` skill. Optional style examples, not a universal or report-type-specific theme. IBCS semantic rules apply only when requested. -->

# Design system: Session-selected report design

> **Required continuation.** Next, open
> [design-system-part-02.md](design-system-part-02.md) (charts, titles,
> numbers, branding, model conventions, workflow, pre-flight checklist).

A reusable guide with optional examples for Intelligence reports.
Resolve `{{placeholders}}` from the [session profile](session-theme.md).
The shell, colors, typography, button treatments, geometry and branding below
are illustrative, not mandatory defaults; adopt them only when selected in the
session design. There is no default website shell or report-type design mapping
([session design](session-theme.md#no-report-type-design-mapping)); never
choose a fresh shell per report within a session. Accessibility, analytical
correctness and native encoding rules still apply.
The [report inspiration library](report-inspiration.md) adds user-requested
legacy-report examples for titles, logo placement, theme families, compositions
and navigation. Choose compatible elements as a coherent session identity;
the examples do not assign styles by report type.
Items marked **(check)** should be verified by authoring and by
`scripts/plan_def.py validate` where possible.

## 1. Design identity

- **Tone:** set by the user/session, not inferred from industry or report name.
- **Feel:** any supported user-selected composition; website-like shell optional.
- **Signature element:** a recurring treatment chosen in the session profile,
  not necessarily a KPI card, hero Matrix or prescribed accent line.
- **Avoid:** gauges for single numbers, 3D, dual axes without labels, glass or
  gradient tiles, decorative fonts, harsh colours, low-energy grey sheets.

## 2. Canvas, grid and shell

| Item | Spec |
|---|---|
| Design canvas | 1920 × 1080 reference grid (16:9); placement stored **normalized** (0–1): `x = px / 1920`, `y = px / 1080`. Keep the plan's existing `canvasStyle.dimension` type unless the user asks otherwise. **The sheet never scrolls**; long Matrices and tables scroll or paginate in their container **(check)** |
| Grid | 8 px snap, margin 32, gutter 16–24, 12-column logic. Only thin accent lines may sit off-grid **(check)** |
| Content area | y ≈ 184 → 1032 px (from 240 with pills navigation). Sections must fit **(check)** |
| Canvas background | From the session palette (`canvasStyle.background` / `wallpaper`); `#FAFAFA` is one light example, not a limit on blue or dark backgrounds |
| Containers | White, radius 8–20, 1 px hairline `#E2E8F0` (outlined) or soft shadow (elevated), padding 16 (`visualStyles`) |
| Chrome | Filter pane hidden in reading mode unless needed (`planProperties.workloadModeConfig.READ.showFilterPane`); minimal reading-mode toolbars; white tooltips styled to match |
| Limits | ≤ 12 data visuals per sheet, ≤ 4 slicers, slicers ≥ 80 px tall (a one-row tile/toggle/checkbox filter needed about 104 px at 1600x900) **(check)** |

### Optional website-style structure, top to bottom

Use only if selected; no report type requires it.

1. **Site header (0–72 px).** White, 1 px bottom line (optional 4 px accent stripe on top).
   - Left: logo (image element).
   - Centre (nav style `header`): sheet links with accent underline (navigation buttons).
   - Right: **Back** (drill sheets only), **Help** and **Info**.
2. **Hero.**
   - Breadcrumb in small caps: `{{Company}} · {{Section}} › {{Report}} › {{Drill sheet}}`, section in accent colour.
   - **Sheet title (19–24 pt) names the sheet**, e.g. "Group Performance Overview".
   - **Business question as subtitle (10–11 pt)**, e.g. "Is the group on track against plan?"
   - Slicers on the right as compact controls (dropdowns with their own titles and room for the open list, date presets, or Super Filter pop-ups once the user approves them).
3. **Sections** in reading order, 16 px gaps. Optional one-line section labels only for clearly separate groups.
4. **Footer (y ≈ 1040).** Hairline, logo mark, `{{Company}} · © {{Year}}` left; refresh note right (data refreshed, closed-through period, projection notice, sample-data note).
5. **Help and Info** ([session design](session-theme.md#help-and-info-controls)):
   native navigation or captured bookmarks/layers; do not assume slide-in animation.

### Helper-element rules

- Footer and "Selected X" labels are unobtrusive. Help/Info controls use the
  session button tokens, readable labels and visible states.
- Large shapes are not rounded (they read as ovals); use a text element with a rounded border instead.
- An invisible shape outline needs full transparency.

## 3. Typography

- **One font family only** (Segoe UI and Segoe UI Semibold recommended) **(check)**.
- Max four sizes per sheet.

| Role | Size / weight | Colour |
|---|---|---|
| Sheet title | 19–24 Semibold | `#1F2937` |
| Visual title | 14 Semibold | `#1F2937` |
| KPI value | 28–32 | `#1F2937` |
| KPI caption, subtitles | 10–11 Regular | `#4B5563` |
| Axis, legend, Matrix/table text | 9–10 Regular (9 minimum) | `#4B5563` |
| Navigation buttons | 12 Semibold | |
| Drill link | 10 | accent |

- Numbers right-aligned in Matrices and tables; text columns left-aligned.

## 4. Colour system

### Example semantic colours (resolve from the session palette)

Keep meanings consistent within the session; hex values are not fixed.

| Meaning | Hex |
|---|---|
| Favourable | `#15803D` |
| Adverse | `#B91C1C` |
| Plan / budget / reference | `#64748B` (dashed on lines) |
| Warning | `#B45309` |
| Text primary / secondary / tertiary | `#1F2937` / `#4B5563` / `#6B7280` |
| Hairline | `#E2E8F0` |
| Gridlines | dotted `#EDEFF2`, value axis only, hidden where data labels show |
| Button outline | `#9CA3AF` |

- Use distinguishable session scenario styles (e.g. solid actual, dashed plan,
  hatched forecast); requested IBCS has its own notation.
- Never rely on red/green alone: always add an arrow or data label.
- Keep contrast ≥ 4.5:1 for text and small marks.

### Theme tokens (set once per session and reuse for every report)

| Token | Purpose | Example |
|---|---|---|
| `accent` | Active nav, breadcrumb, drill links, primary series | `{{#4F46E5}}` |
| `accentSoft` | Tinted tiles, slicer chips, hover | `{{#E0E7FF}}` |
| `pageTint` | Optional canvas background tint | `#FAFAFA` light example |
| `ink` / `brand2` | Optional brand colours for bands or logo | `{{...}}` |
| `cardStyle` | `outlined` (1 px line) or `elevated` (soft shadow) | |
| `corners` | Container radius 8 / 12 / 16 / 20 | |
| `kpiLineSide` | KPI accent line: top, left or bottom | |
| `lineStyle` | Line charts: smooth with area, straight or stepped | |
| `headerStyle` | Bottom line or accent stripe | |

Rules:

- One accent and component system per session (colors, card style, corners,
  KPI treatment, buttons, navigation, page layouts), varied only across fresh
  sessions.
- KPI cards take palette slots in reading order; a chart of the same measure
  reuses that card's colour, a breakdown a light-to-dark ramp of it, and a
  different measure the next slot.
- Every measure keeps the same colour everywhere (maintain the brief's `color_map`).
- Tokens map to Fabric Plan theme and style settings (`CV-THEME-01`,
  `MX-TPL-03`, container `visualStyles`).

### Optional shell variants

| Variant | Look |
|---|---|
| Website-style shell | White header, hero, slicers on the right |
| Dark band | Solid dark band behind header, hero and nav, reversed logo, secondary highlight colour; light canvas below with white containers; compact band (≈ 150 px) |
| Side rail | Full-height dark rail with logo, sheet links, quick facts. Collapsed 72 px (mark, ☰, numbered sheets, Help) ↔ 256 px panel |
| Filter panel | Light left panel (≈ 288 px) with Sheets, Filters, At a glance and Related as white rounded cards on a tinted background |
| Corporate panel | Pastel title band (~96 px), 248 px left panel with SHEETS on top and FILTERS below as separate white cards |
| Dark palette | Token swap of ink, card, line, good, bad; reversed logo. Optional for any report, not required for wallboards |

## 5. Navigation

Pick **one style per session**, applied across reports and visible sheets:

| Style | Example arrangement (not routing rules) |
|---|---|
| `header` | Links in the header with accent underline |
| `pills` | Few sheets; centred segmented control under the hero (content starts ~240 px) |
| `rail` | Left sidebar with accent marker |
| Panel (filter or corporate) | Sheets and slicers grouped in a left panel |
| View toggle | One sheet with 2–3 states; bookmarks, max 4 + Reset |
| None | Single sheet or glance monitor |

Rules:

- **No bottom dock** (it cannot stay fixed) **(check)**.
- Every visible sheet is linked **(check)**. Drill sheets are hidden from
  navigation (`isHidden: true`); they open by drilling and use Back.
- Optional rail panel contents: logo, section eyebrow, report name, sheets each with its
  question, **At a glance** (≤ 4 live numbers, label above value), **Related
  reports**, footer.
- Never show internal codes to users.
- Every link and button has a hover state.

### Buttons

- Use the session's outlined, filled, pill or user-supplied treatment with clear
  text labels (Help, Info, Back); icons may supplement them.
- Navigation buttons share typography and normal/hover/selected/disabled states
  from the session profile; do not hard-code a grey style for every session.
- **Drill link:** compact text "Drill: <sheet> →", 10 pt accent, no fill or
  outline, 24 px tall, soft hover, on the container's subtitle line, right edge
  on the container's 16 px padding.

## 6. Drill, interactions, bookmarks

- Each drill sheet needs a source visual with its drill field, a visible
  "Drill: X →" link, a Back button and a **"Selected X" label** **(check)**
  (`CV-INT-03`, `CV-ELEM-02`).
- Decide drill filter inheritance explicitly. A facts line with a 2×2 chart
  grid is optional, not a required entity-detail layout.
- **Interactions** (`CV-INT-01`):
  - Clicking any chart, Matrix or table **filters** every other chart, Matrix,
    table and KPI card. **Do not use highlight.**
  - Clicks never change slicers or label elements.
  - "No interaction" only with a written reason **(check)**.
- **Tooltips:** main charts get a styled hover card (≈ 320 × 240 px) via the
  chart tooltip settings (`CH-DISP-01`).
- **Field switching:** single-select slicer with a plain default; no annotations.
- **Bookmarks:** Help/Info panels and view toggles, max 8 per report, scoped to
  their own visuals (`CV-BMK-01`).

## 7. KPI cards

- **Contents:** value (28 pt, auto units K / M / bn), caption, change below,
  then a grey caption naming the comparison ("vs budget", "vs last year, same
  days", "vs last month-end") **(check)** (`KPI-CARD-01`).
- **Change figure:** green or red with ▲/▼ from the card's variance settings
  (`KPI-VAR-01`), percent or percentage points (`pp`) as appropriate.
- **Accent line:** green or red by comparison sign, grey with no comparison.
  Bottom-line cards need ≥ 144 px height.
- **Lower-is-better measures** (days, minutes, cost): invert colour logic on
  cards and signed Matrix columns.
- **Like-for-like:** prior-period measures compare the same elapsed period,
  capped at the report or cutoff date **(check)**.
- Every KPI has a comparison. For an `undefined` value suffix, turn the card's
  Number Format off.

### KPI style variants (select per session; reuse across reports)

| Style | Use |
|---|---|
| Classic card | One optional value/comparison treatment |
| Spark card | 12-month sparkline on the right half (`KPI-CHART-01`) |
| Ring card | Progress ring with target tick; waffle (10×10) variant |
| Bullet card | Value on top, full-width bullet strip at the bottom (≈ 176 px tall) |
| Chart card | Value left, frameless mini column or line chart right |
| Multi-value card | Each value its own rounded tinted tile with a 4 px left accent; 4–5 values max (`KPI-CONT-01`) |
| Strip tile | Bordered tile with a tinted header strip |
| Icon badge | Round tinted badge with line icon, top right |
| Chip strip | Grey chips with caption and bold value |
| Status strip / month strip | Count pills, or 12 coloured month squares |
| Gauge | Only for a ratio on a fixed 0..max scale |
| Formula band | Full-width boxes joined by − and = (e.g. income − cost = net) |

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### More KPI card guidance

- Give each distinct business metric one comparison card carrying actual,
  reference, Δ and Δ% where supported, rather than several cards for one
  metric.
- When the same comparison and time series repeat for each member, one card
  trellis with a shared axis (`KPI-MULT-01`) can replace several
  near-identical cards; check every panel label and any overflow after
  rendering.
- Surfaces, emphasis, and the outer frame versus the internal accent:
  KPI card surfaces.

### More token sources

Optional named profiles (F-01 Calm Financial, the Fabric Quiet preset and a
Fluent-style neutral set) live in design families; like
the examples above, they apply only when selected in the session design.
