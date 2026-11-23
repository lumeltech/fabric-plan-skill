---
id: MX-FMT-02
name: Insert blank rows
area: matrix
category: Formatting
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
---

# Insert blank rows

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Adds spacer rows to separate statement sections. An empty row is inserted below
the selected row in one step, can be added at any level of the row hierarchy
and is removed individually from its own row gripper.

## When to use

- Statement readability.
- White space between statement blocks or above key totals.
- Pure spacing; use a break row when the divider needs its own formatting.

## UI path

Matrix toolbar: select a row › Insert › Insert Row › Layout › Empty Row.
Alternative: Row gripper › Insert › Add empty row. Remove: Row gripper on the
blank row › Remove Empty Row.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- The empty row goes below the selected row, so select the row that should sit
  above the gap. Blank rows can be inserted at every hierarchy level.
- Row gripper › Insert › Add Break Row adds a formatted divider (for example a
  fill colour) between row categories; Actions › Add row break on a parent row
  instead starts a new page per category.
- For horizontal spacing use Insert › Quick formula › Empty Column or Empty
  Measure; values cannot be entered in these spacers.
- Use layout rows only: data-input rows on the same Insert Row menu are
  persisted inputs that belong to other modules and are not enabled in this
  release.

## Related features

- `MX-TPL-02`
