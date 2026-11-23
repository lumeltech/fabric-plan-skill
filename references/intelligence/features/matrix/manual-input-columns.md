---
id: MX-INCOL-01
name: Manual input columns
area: matrix
category: Calculations
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
---

# Manual input columns

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Number, dropdown, text, checkbox, and date input columns with default values
(static, measure- or dimension-based). Insert as a visual measure (one per
column category) or one visual column. Options: entry on totals/subtotals,
Prevent null and Allow input (by mode or a Boolean formula). Dropdowns use
lists or presets, option colors and Chip/Arrow/Plain text styles; text adds
word wrap and length/type/email/URL/regex checks; dates add format and min/max.

## When to use

- Comments-like status columns on a report.
- Presentation-only flags, categories or dates beside model values.
- Short notes that need a validated format such as length, email or URL.

## UI path

Insert › Column › Data input.
Choose Number, Text, Single select, Multi select, Date or Checkbox, set the
side-panel options and select Create; double-click a cell to enter a value.
Change options or dropdown lists later via Manage Measures.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Notes, status or reviewer columns in screenshots are
presentation evidence, not proof of manual-input types, persisted values,
workflow approval or writeback. User confirmation establishes availability,
not those properties or encoding confidence. Capture Fabric Plan input-column
encoding before use.

## Constraints

- For planning input use a Planning sheet.
- Typed values do not change the bound semantic model; persisted inputs and
  writeback belong to other modules and are not enabled in this release.
- Prevent null requires a default value; a dimension-based dropdown default
  needs Allow user to add new option. Checkbox columns lack default values.
- Multi-select dropdowns have no presets. Text and date checks reject
  non-conforming entries; invalid date formats are treated as blanks.
- Visual columns cannot be reordered, unlike visual measures.
- Dropdown columns are not carried into Excel exports; test exports before
  relying on input columns in distributed packs.

## Related features

- `MX-INROW-01`
