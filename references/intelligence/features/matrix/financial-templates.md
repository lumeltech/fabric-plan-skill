---
id: MX-TPL-02
name: Financial statement templates
area: matrix
category: Templates and themes
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-financial-reports
---

# Financial statement templates

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Applies simple or standard financial (P&L style) templates with statement
formatting. Simple widens the row-label column for long line-item names;
Standard adds a currency symbol to every measure (adjustable per measure).
The Templates menu also offers Grid (Default, Spreadsheet) and Performance
(IBCS) layouts, and the template can be switched at any time.

## When to use

- P&L, balance sheet, cash flow statements.
- A fast statement layout before subtotal styling, groups and number formats.
- Standard for all-currency measures; Simple for long labels or mixed units.

## UI path

Matrix ribbon > Templates > Financial > Simple (first-party guide).
Pick Standard instead for currency-formatted measures. Then (first-party guide)
bold and border subtotal rows from the Format ribbon, group measures with
Matrix ribbon > Layout > Group > Create Group, and hide the grand total with
Matrix ribbon > Aggregation > Row Grand Total > Off.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.themeColors / globalStyles (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Statement formatting, hierarchical rows, financial separators and scenario
  columns in a screenshot do not prove a selected template or theme. Use the
  optional template only with the approved session design.
- Reconcile row roles, period flows versus balance snapshots and mixed
  amount/per-share units independently of the template.
- Define account roll-ups, cost/display signs and calculated profit rows;
  never add parent accounts to their children. IBCS remains opt-in.
- Switching templates can discard earlier customizations; apply the template
  first, then format.
- Standard puts a currency symbol on every measure; remove it and set
  per-measure scaling for ratios, counts, margins or per-share values.
- The Matrix adds a row grand total automatically; turn it off when summing
  all statement lines is meaningless.

## Related features

- `MX-CALC-01`
- `MX-SIGN-01`
