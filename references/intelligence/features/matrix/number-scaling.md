---
id: MX-NUM-01
name: Number scaling and decimals
area: matrix
category: Number formatting
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-financial-reports
---

# Number scaling and decimals

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Measure-level, uniform, auto, or native scaling (K, M, B), decimals, percentages, prefix and suffix.

## When to use

- Compact amounts; consistent decimals.

## UI path

Matrix ribbon > Quick Format; select a measure for measure-specific scaling.
Decimal icons control precision; Prefix/Suffix applies to selected rows/cells.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/visualState/numberFormatting (object)
Observed keys: enabled:true, formatType:"flexible", scalingFactor:"auto",
               noOfDecimal:2, noOfDecimalPercent:2, millions:"m", billions:"b"
Measure overrides (UI-saved): /properties/visualState/formatConfig.measure["<measure id>"] =
  [{format:{"<code>": value}, order:n}, …], later entries win; formatSize = next order.
  Codes seen: "8" prefix ("$"), "9":"%" (show as percentage), "11" decimals,
  "13" scaling ("auto" | "none"), "25" in-cell chart subtype, "26" in-cell chart colour.
  Row overrides formatConfig.row["<row id>"]: "1" bold, "12" border sides, "20" border
  colour, "34" border width, "39" border style.
```

This is a reporting Matrix group, not inherited Planning-grid evidence.
For mixed measures, a saved Matrix kept the global `prefix` empty and set
`"8":"$"` only on currency measures; counts used `"13":"none"` and `"11":0`.
Rendered: a measure-level `"8"` prefix sits at the left edge of plain value
cells (accounting style), while the global `prefix` and a column with an in-cell
bar show it next to the number. A model percent measure renders with the
model's live format string (its decimals win over the assignment
`formatString` and `"11"`); adding `"9":"%"` to it printed a doubled sign
("25.80%%"). Keep `"9":"%"` for engine-computed variance % columns only; saved
renamed percent model measures carried no codes.
Copy the complete native group; preserve native spelling such as
`decimalSeperator` if present; chart formatting uses a different serialized group.

## Constraints

- Statements may mix scaled amounts with unscaled per-share values (EPS).
  Determine whether source amounts are already scaled; never scale per-share
  values or concatenate symbols into numeric measures. Capture per-row
  overrides when amounts and per-share values share a measure; measure-level
  controls alone do not prove that mixed-row configuration.
- 'Auto' and scalingFactor 'autoFixed' differ; copy the native value.
- Confirm thousands separators and locale rather than copying them from
  screenshots. For IBCS, use ISO currency with prefix in titles and ≤ 4
  digits in tables.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- With Millions scaling, leave the custom suffix empty and never also enter
  `M`: native scaling and a custom suffix are separate controls, not two
  required steps [confirmed].
- Validate active scaling and custom suffix together, including enabled
  per-measure overrides. Check rendered values for doubled unit labels and
  never divide already scaled values again.
- When repairing, clear a redundant `M`/`m` suffix wherever its configured
  scaling is millions (root group, nested measure overrides and dormant
  formatters) without enabling anything; keep scaling, precision, signs,
  currency prefixes and unrelated suffixes, report active fixes apart from
  dormant cleanup, and re-audit the fresh readback [confirmed].
- Chart-owned formatting saves millions as `scalingFactor:"1000000"` with
  `suffix:""`; its scaling-unit display flags and disabled per-measure
  entries are separate controls that do not override the active format
  [saved]. The Matrix `millions`/`billions` unit labels were not isolated
  against a custom suffix [open].
- Scaling must not change a percentage input's meaning; keep percentages,
  currency, counts, unit rates and additive values distinct.
- Saved values alone do not prove the absence of clipping, suffix defects or
  misleading labels; check the readback and the native rendering.

## Related features

- `MX-NUM-02`
- `MX-NUM-03`
