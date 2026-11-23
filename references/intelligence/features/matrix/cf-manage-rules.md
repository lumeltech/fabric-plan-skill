---
id: MX-CF-04
name: Manage conditional formatting rules
area: matrix
category: Conditional formatting
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-conditional-formatting/highlight-tabular-data-with-conditional-formatting
---

# Manage conditional formatting rules

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Orders, edits, disables, and scopes rules (exclude totals, row headers). The
Manage rules panel lists every rule; each can be edited, duplicated, deleted
or toggled on/off, and dragging its gripper changes priority. Editing reopens
the rule settings: title, Apply to (row headers, rows, column headers or
measures), Row hierarchy levels (values, totals or both) and Format by.

## When to use

- Keep CF to decision columns.
- Resolve conflicting rules by setting their priority.
- Pause a rule without losing its settings.
- Review rules created by one-click options before publishing.

## UI path

Home › Conditional formatting › Manage rules (side panel; pencil to edit,
gripper to reorder). New rules: Conditional formatting › Create Rule.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.cfProps.rules[]
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- When several rules match the same cell, the first rule in the list is
  applied; drag rules to change priority.
- Quick rules, heat maps and classifications cannot be duplicated.
- Row hierarchy levels default to Values only; choose Totals only or Values
  and Totals (which adds a row grand total option) to format totals.
- Applying a rule to row headers lets you pick the row dimensions it formats.
- Format by offers Rules (If conditions), Color scale, Classification and
  Ranking.
- A blended column keeps its source columns' conditional formatting; editing
  the source rule updates both columns.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Disabling two individual rules in the UI changed only those rules'
  `enabled` from true to false, in both `cfProps.rules[]` and
  `jet_cfProps.rules[]`; both master `enabled` flags stayed true
  [confirmed]. Inspect and change both collections when adapting rule state.
- Both master flags were true in every inspected populated owner [saved];
  which UI control sets them is unknown, so capture one master-switch change
  before writing a master value [open].
- Keep `rules[]` order and every disabled rule; whether array order equals
  the panel priority above is not isolated [open].
- A save that toggles rules can also change unrelated properties [saved].
  Attribute only the isolated rule-flag change to the toggle and keep a
  controlled comparison separate from the original export.
- Retain disabled rules unless their removal is explicitly requested.

## Related features

- `MX-CF-01`
