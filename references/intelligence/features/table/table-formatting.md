---
id: TB-FMT-01
name: Table formatting and number settings
area: table
category: Table
status: IS-Confirmed
encoding: unverified
visual: Table
sources:
---

# Table formatting and number settings

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Cell formatting, number formatting, and display settings for tables. Style
options format a selected column, row or cell (font, alignment, row padding)
and hide measures or columns. Number settings cover scaling (uniform,
per-measure, auto, native or custom), %, prefix/suffix, decimals, separators,
percentage/basis points, null and zero handling and custom unit labels.
Canvas settings add theme, font, row highlights, indent, total row and gridlines.

## When to use

- Apply the design system.
- Measures of different magnitudes in one table (per-measure or auto scaling).
- Finance tables needing IBCS display or percentage-point/basis-point variances.

## UI path

Table › Format. Select a column, row or cell and use the Style, Quick format,
% and decimal options; display settings › Number for report-wide scaling,
separators, null and zero handling; display settings › Canvas for theme, font,
row highlight and gridlines. Re-show hidden measures from the measure series
configuration.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- For mixed-unit rows (actual, target, gap), capture per-row formats and
  distinguish rate percentage-point gaps, relative percentages, rating points,
  currency, counts and days. Calculate from unrounded values.
- Blank cells must not ambiguously represent both zero and missing data.
  Treat null as zero and the zero display options (blank, zero, null, hide)
  decide this; set them deliberately.
- Use display names, not raw field names, for headers. Apply one scaling per
  column and integer formats for counts.
- For wide scrollable detail, use the user/session palette with readable
  contrast and give truncated text an accessible full value. Do not show
  placeholder midnight times on date-only fields.
- Preserve negative values and genuine zero rows rather than formatting them
  into success-shaped results. Suppress zeros hides rows only when every
  measure is 0; Suppress null variance shows ±100% instead of a blank.
- The IBCS display format sets one report-level scaling; Custom shows each
  value's factor. Percentage- and basis-point display needs Percentage scaling.
- A display-settings prefix/suffix applies to every column; set column-specific
  ones from the toolbar. Fit mode applies only with the trellis Responsive Grid.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Saved Table owners keep style state in object-valued `globalStyles` and
  `gridStyles`, like the Matrix (`MX-FMT-01`, `MX-FMT-04`) [saved]; their
  formatting values remain not isolated.
- With Millions scaling, leave the custom suffix empty instead of adding
  `M`; see `MX-NUM-01` [confirmed].

## Related features

- `TB-TABLE-01`
