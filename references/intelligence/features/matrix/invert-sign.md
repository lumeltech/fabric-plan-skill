---
id: MX-SIGN-01
name: Invert sign
area: matrix
category: Calculations
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-ibcs-formats/table-templates
---

# Invert sign

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Flips the sign of selected rows (e.g. costs shown positive). Invert works on
cells, rows or measures; inverting a parent cascades to its children, and a
selected measure can become a new signed measure. Sign in headers shows signs
in row headers (optionally + signs and = on totals); a −1/+1/0 sign column
from the model can drive signs instead.

## When to use

- Statements where costs are stored negative.
- Expenses stored positive that must subtract when aggregating to profit.
- Showing which rows add, deduct or total through signs in row headers.

## UI path

Select rows or cells › Data ribbon › Invert (select again to reset). Show
positive signs under Format › Appearance › Numbers › Show Positive Sign; add an
"=" sign to a total through the row gripper › Add "=" symbol (first-party
guide). Include in Total and Sign in headers sit with the number display
options; confirm their exact labels in the Fabric Plan ribbon.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Inverted values feed totals and subtotals by default; turn off Include in
  Total to change only the display.
- Calculated rows cannot be inverted; Invert is disabled for them.
- Inverting a parent row, or a measure at parent level, cascades to all child
  rows.
- Selecting Invert again on an inverted selection resets it after confirmation.
- A sign column (−1, +1, 0 for totals) must already exist in the model; bound
  as the sign field it disables Invert, and column fields cannot be added.
- Keep display sign, calculation sign and business favorability separate
  (`MX-NUM-03`).

## Related features

- `MX-TPL-02`
