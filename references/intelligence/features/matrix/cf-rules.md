---
id: MX-CF-01
name: Conditional formatting rules
area: matrix
category: Conditional formatting
status: IS-Confirmed
encoding: verified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-conditional-formatting/create-rules
  - https://docs.fabricplan.com/planning-sheets/reference/formula-syntax
---

# Conditional formatting rules

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

If-condition, field-value, classification, and ranking rules that colour cells, rows, or headers.

## When to use

- Highlight adverse variance; flag thresholds.

## UI path

Home › Conditional formatting › Create rule.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/visualState/cfProps (object; enabled:true, rules[])
Observed rule keys include applyTextColor, applyBackgroundColor,
                           basedOnMeasureName, color, classificationType
Pointer: /properties/visualState/jet_cfProps (companion group; UI saves keep it identical to cfProps)
UI-saved rule (runtime-verified):
  {ruleType:"rule", ruleFor:"child", columnRuleFor:"child", columnRuleType:"default",
   heatMapType:"columnHeatMap", displayName:"<label>", enabled:true,
   name:"<engine measure id><8 uppercase letters>", basedOn:"<engine measure id>",
   applyTextColor, color, applyBackgroundColor, background, textColorFor:"font",
   conditionalOperator:"or",
   conditions:[{conditionType:"singleMeasure", basedOn:"<engine measure id>",
                operator:"<" | ">" | "<=" | …, valueType:"static", comparisonValue, …}],
   …full native key set…}
Engine ids: basedOn and condition basedOn reference visualState.manage_measures[].id
  (numeric strings); row-level targets use visualState.rowDimensions[].id.
Target fields: highlightedMeasure, highlightedMeasureName and bubbleBasedOn name the
  painted column; conditions[].basedOn and comparisonMeasure name the tested one.
  A cloned rule keeps its donor's values; retargeting all five to the Δ BUD id made a
  cloned ΔPL% rule colour that column [confirmed].
Evidence: rule saved in the report editor and read back; font and background
  highlights user-confirmed in a published report.
```

Copy full reporting Matrix rule/companion state and resolve all target/
comparison measures against the registry. Adverse/favorable variance colours
in screenshots do not establish rule thresholds, precedence or target measure.

The engine assigns `manage_measures`/`rowDimensions` ids itself and replaces
authored ids on an edit-mode load (it re-keyed one Matrix again on a later
editor session); pivot `measureGuid` values stay as authored. Rules written
against authored ids did nothing. Read the ids from the latest readback before
writing rules, keep the builder pinned to them, and re-read after any editor
save. The same field received the same id in several matrices, but the
derivation is not a standard hash; never compute ids.

## Constraints

- Status labels may not follow from gap sign alone. Define per-KPI threshold
  units, direction (revenue/expense favorability), tolerance, precedence,
  effective dates and missing-data behavior explicitly.
- Apply one classification across tables, charts and exception lists, or
  state differing scope explicitly. Test exact boundaries, rule precedence
  and totals in the Matrix.
- For calculated comparison measures or flags, read
  [Matrix formula syntax](formula-syntax.md), especially conditions, logical
  functions and numeric/blank handling. Bind the resulting measure or flag
  through a supported rule; formula syntax does not establish that `cfProps`
  accepts arbitrary expressions.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/cfProps/rules[] (array in the object group; partial record)
Fragment: {"enabled":false,"ruleType":"rule"}  (a disabled saved rule record)
Evidence: saved native Matrix exports [saved]
```

- Rule count differs per owner and every inspected populated owner kept
  some disabled rules beside enabled ones; no fixed collection size exists
  [saved]. Never truncate a list to match a donor or synthesize rules from
  its length; keep complete records, order, native measure identities and
  inactive settings.
- A stored `enabled:true` proves the flag, not that the rule matches data,
  executes or wins precedence [open].
- Presence is its own check: an INFORIVER/10 owner can save neither
  `cfProps` nor `jet_cfProps` [saved]. Absent is not empty, not a disabled
  master and no licence to synthesize defaults; keep absent, null and empty
  distinct.
- An empty `rules` array, even one a save newly added (seen on a chart
  owner), is not a created rule [saved].
- Resolve every target before reusing a donor: `basedOn`, nested
  `conditions[].basedOn` and any apply-to list (chart-owned rules also save
  `applyToOptions`), not only the visible field wells [saved].
- A saved chart owner kept an enabled rule whose target measure the visual
  no longer bound [saved]; JSON/API acceptance does not validate such a rule
  and its rendered effect is unverified [open]. Check Matrix donors the same
  way; remap or remove such rules only within authorized scope.
- Never import Super Filter `cfSettings.rules` or chart
  `hiddenProperties_!!!_cfProps` (a JSON string) as Matrix `cfProps`; the
  Table (visual type 15) does not require these collections [saved].
- The companion treated equal collections as per-owner saved evidence, not
  proof that every save synchronizes them; the companion-group guidance
  above wins [open].
- Completion checks: rows/columns, measure roles, totals, null behaviour,
  rule-target closure and rendered formatting. Retain disabled rules unless
  their removal is explicitly requested.

## Related features

- `MX-FML-01`
- `MX-CF-02`
- `MX-CF-03`
- `MX-CF-04`
