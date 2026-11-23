## Contents

- [Use and precedence](#use-and-precedence)
- [Classification fields](#classification-fields)
- [F-01 Calm Financial](#f-01-calm-financial)
- [Family catalog](#family-catalog)
- [Fabric Quiet preset (Default 1)](#fabric-quiet-preset-default-1)
- [Fluent-style neutral tokens](#fluent-style-neutral-tokens)

<!-- Design topic for the `fabric-plan-skill` skill. Optional named design profiles merged from the companion Intelligence authoring library; never a report-type default. -->

# Design families and named profiles

Merged from the companion Intelligence authoring library. Additive only:
session design and the other design topics take
precedence; every profile here is optional. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

## Use and precedence

**Optional (companion default):** the companion library starts reports from
the F-01 Calm Financial family and catalogs designs by family; this applies
only when the user or session design selects it and never overrides the
session theme, supplied designs, report-inspiration guidance or IBCS opt-in.

- Offer these profiles in the design interview
  next to the inspiration families.
  Report type, industry or audience never selects one; fresh sessions still
  choose freshly.
- Resolve exact tokens, test contrast and record the choice in the session
  profile; a profile name alone is not a complete design.
- Keep family, appearance, notation, density and decoration independent: a
  light finance design can use standard or IBCS notation, and one dark card
  does not make a dark theme. Do not infer dark mode from finance or technical
  subject matter.
- Expressive decoration needs a stated communication purpose. High density
  never waives readable text, truthful titles, spacing or data access; reflow
  or split detail sheets instead.

## Classification fields

Optional profile and brief fields
(design brief):

| Field | Values / interpretation |
|---|---|
| `family_id` | F-01 to F-05, or a custom family name |
| `appearance` | light / dark / mixed; mixed needs a functional reason |
| `density` | low / medium / high, from the reading task |
| `decoration` | minimal / restrained / expressive |
| `selection_reason` | Audience, decision, environment and why the combination fits |
| `preference_evidence` | Explicit user preference, saved design or unconfirmed recommendation |
| `verification` | Saved-state, rendered and interaction checks, each stated separately |

Notation stays in `design_identity.ibcs`; IBCS applies only on explicit request.

## F-01 Calm Financial

The companion user's favourite finance design language, taken from saved
finance overview and plan-versus-forecast sheets. Improve clarity within the
family rather than switching style for novelty, and adapt the composition to
the task; not every report is a finance dashboard.

| Attribute | Starting treatment |
|---|---|
| Appearance | Light, calm, polished and restrained; data first |
| Surfaces | Pale cool canvas, white panels, quiet neutral borders, consistent modest rounding |
| Hierarchy | Clear title and context subtitle; compact scope controls; a focused KPI band; larger analysis and detail regions |
| Accents | Navy/indigo structure with selective purple comparison accents; one emphasized outcome card when warranted |
| Detail | Enough labels, signs, units and comparison context to explain the result; no decorative excess |
| Craft | Native titles without duplicates, fitted controls, deliberate inset and gutters, no clipping |

Reference tokens; the canvas, panel and border values were seen in a saved
finished sheet, while accent and text reflect authored intent [saved]:

| Role | Token |
|---|---|
| Canvas | `#F4F5FA` |
| Ordinary panel | `#FFFFFF` |
| Border | `#E0E0E0`, 1 px |
| Emphasized surface | `#222B6A`, with white text |
| Secondary accent | `#9170F3` |
| Primary text | `#202446` |
| Panel rounding | 8 px |

These are design tokens, not native theme settings. Do not carry over filter
selections, bindings, disabled settings or a report-specific theme number as
portable defaults. Never use the accents where they would contradict status,
variance meaning or requested IBCS notation. The border is only about 1.2:1
against the canvas, so separation also relies on the white panel fill.

## Family catalog

Recommendations for the design interview, not confirmed preferences or native
presets; "Use when" describes fit and never selects a family automatically.

| Family | Use when | Appearance / density / decoration | Avoid |
|---|---|---|---|
| F-01 Calm Financial | Finance or executive overview, plan/forecast comparison, statements | Light / medium / restrained | Filling every KPI, redundant labels, generic captions |
| F-02 Analytical Detail | Analysts reconcile drivers, compare categories or read statements | Light / high but fitted / minimal | Crowding, tiny type, hiding required detail |
| F-04 Focused Presentation | One main message for a short executive narrative | Light / low / restrained, one focal treatment | Extra charts, ornamental shapes, ungrounded insight text |
| F-05 Dark Monitoring | Explicit dark preference or confirmed low-light monitoring | Dark / low–medium / minimal, accessible contrast | Assuming dark looks premium; dense statement sheets |

F-03 (planning workbench) is for embedded Planning, not enabled in this
release.

## Fabric Quiet preset (Default 1)

**Optional (companion default):** a flat global theme preset that a companion
user supplied as the reference for later updates; it applies only when the
user or session design selects it and never overrides the session theme,
supplied designs, report-inspiration guidance or IBCS opt-in. The exact preset
is kept as an optional asset (`assets/themes/default-1-fabric-quiet.user-theme.json`)
with notes (`assets/themes/README.md`).

The preset values, which a saved global theme registration matched
[confirmed]:

| Layer | Values |
|---|---|
| Ordered primary colours | `#3a6fd8` `#14958a` `#d9693a` `#7b61d1` `#4e8a3e` `#c2508a` `#b98a12` `#c8434e` |
| Semantic | Positive `#82BA00`, negative `#FF000A`, neutral `#B3B3B3` |
| Structural | Outlines `#A6A6A6` and `#E6E6E6`, background token `#F5F5F5`, icon `#333333`, accent `#117865`, subtle fill `#FFFFFF` |
| Surfaces | White canvas, wallpaper and element backgrounds; the background token is not the page fill |
| Framing | Page and element borders off, shadows off, zero effective corner radius |
| Padding | On, uniform 5 px |
| Typography | Segoe UI fallback chain, 14 px responsive base, `#333333`, automatic font colour off |

- The 14 px base is responsive; it does not establish that every title or
  axis renders at 14 px, and role-specific text keeps its own styling [open].
- A confirmed reference chart kept explicit local container effects (1 px
  border, 8 px corners, 16 px padding) and 10 px axis labels under this preset
  [confirmed]; local framing on chosen visuals and a flat global preset can
  coexist.
- On white, the positive green (about 2.3:1) and the neutral grey (about
  2.1:1) fall below 3:1, and the negative red (about 4.0:1) is below 4.5:1 for
  small text; pair them with signs or labels and test small marks.
- Rendering, accessibility and inheritance by every visual were not tested.
  Applying a theme is an authoring action (themes);
  copy native theme state from a same-build readback.

## Fluent-style neutral tokens

**Optional (companion default):** the companion's generic light token set for
reports without a family or brand; it applies only when the user or session
design selects it and never overrides the session theme, supplied designs,
report-inspiration guidance or IBCS opt-in.

| Token | Hex | Use |
|---|---|---|
| Canvas | `#F5F5F5` | Sheet background |
| Card | `#FFFFFF` | Visual containers |
| Stroke | `#E0E0E0` | 1 px borders; `#D0D0D0` was the companion's light-page KPI border |
| Text primary / secondary | `#242424` / `#616161` | Titles and values / subtitles and captions |
| Accent | `#117865` | Selected states, highlights |
| Link / selection | `#0F6CBD` | Links, focus |
| Positive / negative | `#107C10` / `#D13438` | Favourable / adverse |

Series order: `#0F6CBD`, `#117865`, `#8764B8`, `#CA5010`, `#4F6BED`, `#986F0B`.
