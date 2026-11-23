---
id: MX-NUM-03
name: Semantic formatting (signed colours)
area: matrix
category: Number formatting
status: IS-Confirmed
encoding: verified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-financial-reports
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-conditional-formatting/highlight-tabular-data-with-conditional-formatting
---

# Semantic formatting (signed colours)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Formats values by sign: positive/negative colour, parentheses, +/− prefix, IBCS-style notation.

## When to use

- Variance columns.
- Finance statements.

## UI path

Format ribbon > Appearance > Numbers > Semantic Formatting (financial guide).

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.numberFormatting (semanticFormatting, positiveValueColor, negativeValueColor, positiveValueFormat, negativeValueFormat, ibcsformat)
Runtime-verified: semanticFormatting:true with positiveValueColor and negativeValueColor
  colours every value by sign without rule ids (useful where CF rules would need
  engine-assigned ids).
Evidence: applied to several reporting matrices; signed colours user-confirmed in a
  published report. Parentheses/prefix formats and ibcsformat are not isolated.
```

Copy the whole native `numberFormatting` group and change only these keys.

## Constraints

- Parenthesized negatives do not imply a red convention, invert-sign
  activation, financial favorability or an IBCS template. Expense magnitudes
  may reconcile differently from their displayed signs; resolve ledger,
  calculation and display signs separately.
- Arithmetic sign and business favorability are different. Define expense
  direction per account class, separate from display sign and subtraction order.
- Colour variances by account-type-aware favorability, not raw sign; do not
  copy a colour convention from screenshots without an agreed financial
  contract.
- Format percent variance as a percent, consistently with other columns.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Chart-owned number formatting stores sign templates as strings: changing
  `positiveValueFormat` from `"x"` to `"+x"` added an explicit plus sign
  beside `negativeValueFormat:"-x"` and a separate value-colour flag
  [saved]. Whether the Matrix group uses the same templates is not
  isolated; the note above on prefix formats stands [open].

## Related features

- `MX-VAR-01`
- `MX-CF-01`
