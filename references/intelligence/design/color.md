# Colour

<!-- Design topic for the `fabric-plan-skill` skill. Palette values come from the approved session profile, not report type or example hex; IBCS rules apply only on request. -->

## Principles

- Colour carries meaning; decoration uses neutrals.
- Reuse the session palette across reports; semantic colours (favourable, adverse,
  plan/reference, warning) are reserved and identical everywhere.
- Each measure keeps one colour across all visuals (`color_map`).
- Never encode meaning by colour alone: add ▲/▼, signs, labels, or patterns.

## color_map strategies

| Strategy | Meaning |
|---|---|
| `measure_match` | Same base colour for a measure in every KPI, chart and Matrix highlight |
| `gradient` | Light → base ramp of the measure colour for breakdowns |

## Conditional formatting intent

Describe intent in the brief; authoring maps it to features:

| Intent | Feature |
|---|---|
| Sign of variance (good/bad) | Matrix rule-based CF / semantic formatting (`MX-CF-01`, `MX-NUM-03`) |
| Magnitude across a column | Data bars or colour scale (`MX-CF-02`) |
| Threshold status | Icons / action dots (`MX-CF-03`) |
| Rank emphasis | Ranking CF (`MX-CF-01`) |
| Chart point highlight | Chart CF / comparison bands (`CH-CF-01`) |

- Lower-is-better measures invert favourable/adverse.
- Limit CF to columns answering the sheet's question.

## Themes in Fabric Plan

- Report-level theme: `planProperties.theme` (observed `type` integer and
  per-sheet `appliedThemes`).
- Dashboard / chart / KPI themes: features `CV-THEME-01`.
- Matrix and enterprise themes: `MX-TPL-03`.

Capture a native sample before changing theme codes.

## Contrast

- Text on background ≥ 4.5:1 (≥ 3:1 for 18 pt+ or bold 14 pt+).
- Chart marks vs container ≥ 3:1.
- Check the dark wallboard variant separately if used.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Palette principles

- Match the palette family to the data: sequential for ordered values,
  diverging for values around a meaningful midpoint, categorical for nominal
  categories.
- Never use a rainbow on ordered data; it has no perceptual order.
- Cap categorical palettes at 7–8 hues and group the rest into Others.
- Keep most of the canvas neutral so colour draws the eye to what matters.

### Palette reference

Starting points only: resolve final tokens in the session profile and test
contrast. Pale entries (yellow, light tints) need a boundary or a darker
alternative for small marks and are never text colours.

| Sequential | 5-step ramp | CVD | Use |
|---|---|---|---|
| Blues | `#EFF3FF` `#BDD7E7` `#6BAED6` `#3182BD` `#08519C` | Safe | Default low-to-high magnitude |
| YlOrRd | `#FFFFB2` `#FECC5C` `#FD8D3C` `#F03B20` `#BD0026` | Deutan marginal | Heat or urgency |
| Viridis | `#440154` `#3B528B` `#21908C` `#5DC863` `#FDE725` | Safe | Perceptually uniform, print-safe |
| Cividis | `#002051` `#3F5B75` `#8E8E52` `#CBBE2D` `#FDEA45` | Safe, also greyscale | Most robust; blue-yellow only |

| Diverging | Low → mid → high | CVD |
|---|---|---|
| RdBu | `#B2182B` → `#F7F7F7` → `#2166AC` | Safe |
| BrBG | `#8C510A` → `#F5F5F5` → `#01665E` | Safe |
| PiYG | `#C51B7D` → `#F7F7F7` → `#4D9221` | Protan marginal |

| Categorical | Colours | CVD |
|---|---|---|
| Okabe-Ito (8) | `#E69F00` `#56B4E9` `#009E73` `#F0E442` `#0072B2` `#D55E00` `#CC79A7` `#000000` | Safe |
| Set2 (8) | `#66C2A5` `#FC8D62` `#8DA0CB` `#E78AC3` `#A6D854` `#FFD92F` `#E5C494` `#B3B3B3` | Safe |
| Tableau 10 | `#4E79A7` `#F28E2B` `#E15759` `#76B7B2` `#59A14F` `#EDC948` `#B07AA1` `#FF9DA7` `#9C755F` `#BAB0AC` | Deutan clash at colours 9–10 |

```text
Nominal     8 or fewer categories → Okabe-Ito or Set2; more → group into Others
Ordered     CVD-critical → Cividis or Viridis; otherwise → Blues
Diverging   CVD-critical → BrBG; otherwise → RdBu
Status      the session's favourable, warning and adverse tokens
```

### Semantic roles

- Amber marks a warning or an approaching threshold, between green and red.
- Grey is neutral context or a benchmark, and the default for non-highlighted
  marks; blue suits information or a brand accent when there is no semantic
  load.
- Never redefine green as adverse without an explicit user instruction;
  lower-is-better measures change which outcome is favourable, not what the
  colours mean.
- In some East Asian financial contexts red signals gain; note it and confirm
  with the user when the audience is in those markets.
- Standard-notation scenario roles: prior year in light grey and forecast as a
  lighter tint of the actual colour, with dashes or hatching so hue is never
  the only cue.
- Input colour coding of editable cells (amber inputs, blue context, green
  outcomes) is for embedded Planning, not enabled in this release.

### Assignment details

- The same category keeps the same colour on every sheet and visual of the
  report; a category with inherent meaning (for example a critical status)
  takes its semantic colour first.
- Assign series in palette order without skipping slots, and sort the legend
  to match the visual order of the data.
- A breakdown ramp runs from a light tint (about halfway to white) to the base
  colour, so the shading also reinforces the sort order.
- Data labels use neutral dark text, never the series accent colour.

### Highlight pattern

| Element | Treatment |
|---|---|
| Highlighted bar or line | Saturated accent or semantic colour |
| Context bars or lines | Light grey |
| Reference line | Medium grey, 1 px dashed |
| Background | White or near-white |

In narrative sheets the highlight is the thesis; in analytical sheets it is
the selected subset. Apply it with chart conditional formatting (`CH-CF-01`)
and label the highlighted item.

### More formatting techniques

| Technique | Use on | Feature |
|---|---|---|
| Per-category colour | Bars or columns where category identity matters | Chart colour settings (capture first) |
| Threshold colour | KPI value or background by favourable, neutral or adverse threshold | `KPI-MULT-01` |
| Colour gradient | Matrix cells, heatmaps | `MX-CF-02` |
| Highlight and grey | Any chart | `CH-CF-01` |

Reserve conditional formatting for traffic-light status, heatmaps and
threshold alerts.

### Optional palette budgets

**Optional (companion default):** palette budgets per example archetype; they
apply only when the user or session design selects them and never override the
session theme, supplied designs, report-inspiration guidance or IBCS opt-in.

| Example archetype | Palette strategy | Colours |
|---|---|---|
| Executive Summary | Favourable, warning and adverse + one accent + grey | About 5 |
| Operational Monitor | Red/amber/green status + status grey + one highlight | About 5 |
| Analytical Canvas | Categorical (Okabe-Ito or Set2) + a sequential ramp for heatmaps | Up to 8 |
| Narrative Story | One highlight + grey context | 2–3 |
| Comparative Benchmark | Diverging (RdBu) or paired categorical | 4–6 |

### Optional distinct pie colours

**Optional (companion default):** pie and donut slices take distinct category
colours rather than a ramp of one measure colour; this applies only when the
user or session design selects it and never overrides the session theme,
supplied designs, report-inspiration guidance or IBCS opt-in. The companion's
user-supplied fix sets the chart appearance flag
`individualCategoryColor: true`, not `individualColor` [confirmed]; exact
JSON follows the pie and donut feature's
`encoding`.
