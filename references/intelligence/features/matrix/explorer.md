---
id: MX-EXPL-01
name: Explorer pane
area: matrix
category: Sort, filter, Top N
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
---

# Explorer pane

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Slice-and-dice pane inside the Matrix with filters and KPI header presets.
The explorer toolbar filters measures and row/column categories, with a date
range slider when dates are in the visual; each category shows its value for
the selected measure. Categories sort by name or value, KPIs can be hidden and
values highlighted with range or rule flags.

## When to use

- Analyst self-service on one visual.
- Isolate a category, region or date range without adding slicers.
- Flag high or low values with ranges or rules while exploring.

## UI path

Matrix toolbar: Home › Analyze › Explorer. Pane menu (arrow): Explorer full
view, Unpin toolbar, Show KPI, Clear all. Filter by date toggle; Flag icon ›
Rules or Ranges; category gripper › Sort by values.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Works with all table and measure layouts of the Matrix.
- The date slider needs dates in the visual; turning Filter by date off lists
  the date levels as ordinary filters.
- Selections filter the Matrix and narrow the explorer lists (such as child
  levels) together; Clear all removes them.
- Category values aggregate the measure chosen in the explorer drop-down;
  switch the measure to explore another KPI.
- Ranges use percentage or numeric thresholds; icons and colours can be
  reversed and reset to defaults.
- A KPI header preset reflects explorer selections only when that preset is
  chosen for the header.

## Related features

- `MX-SRT-02`
