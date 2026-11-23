---
id: MX-CHART-03
name: Integrated waterfalls and stacked charts in cells
area: matrix
category: In-cell charts
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-ibcs-formats/table-templates
---

# Integrated waterfalls and stacked charts in cells

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Shows cumulative waterfall or stacked composition bars inside the Matrix.
Waterfalls come as Solid, Colored or Invert colored, can run continuously
across row hierarchy levels and label bars by value, percentage or both.
Stacked charts show absolute (Stacked) or relative (Percentage stacked)
composition across several selected columns. A Customize tab sets axes,
labels, fill pattern, colours, series sorting and height or measure scaling.

## When to use

- Statement bridges (IBCS T04 when IBCS requested).
- Show how row items build up or reduce a value towards a final total.
- Compare each row's composition across column categories.

## UI path

Insert › Chart › Waterfall/Stacked. Select the measure column first (stacked:
all component columns), then pick the variant from the Waterfall or
Bullet/Stacked dropdown (Percentage stacked is in its Others category).
The Customize tab then holds the chart options; Remove chart deletes it.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Continuous is offered only when the selected column has a row hierarchy.
- Show label (Value, Percentage, Both) and Percentage scaling need Data label
  on; scaling appears only for Percentage or Both. Universal (default) is the
  share of the grand total; By level is the share of the parent.
- Colored waterfalls default to green positive and red negative bars; Invert
  colored swaps them. Positive, negative, axis and bar colours are adjustable.
- Fill pattern offers the IBCS notations Solid, Outlined and Hatched; apply
  IBCS semantics only when IBCS is requested.
- Height scaling: Individual (default, per row) or Universal (by parent level).
  Waterfall measure scaling: Universal (default, one min/max across all
  charted measures) or Individual (each measure's own range).
- Stacked options: series Sorting (ascending/descending), label Alignment
  (Left by default, Center, Right), Show axis and Series Display colours
  (IBCS, default palette or custom per value).
- Some axis, label and appearance options are unavailable for certain chart
  types or variants.

## Related features

- `MX-TPL-04`
