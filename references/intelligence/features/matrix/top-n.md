---
id: MX-SRT-03
name: Top N + Others
area: matrix
category: Sort, filter, Top N
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/ranking-data
---

# Top N + Others

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Keeps the top or bottom N members (nested rules supported) and groups the rest
as 'Others'. N can be a count or a percentage. The Others row shows how many
members it holds, previews them on hover and lists them all via its expand
icon. Added rules nest further levels (for example bottom N children within
each top N parent), each level with its own Others row.

## When to use

- Long member lists; product or customer rankings.
- Leaders or laggards within each parent group (nested Top N).
- Keep the long tail visible as a single Others row.

## UI path

Home › Top N. Select the ranking measure column first, then complete the
Top N dialog (Value or Percentage; Add rule for nested levels) › Apply.
Delete removes a rule; Reset all clears every rule. Row gripper › Add row to
others / Remove from others adjusts the bucket.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.ranking_config (rank_rules, show_others, others_title, exemptions)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Top N works on one measure column at a time; applying it to another column
  warns and replaces the existing rule via Remove and proceed.
- Rules can nest beyond two hierarchy levels. The suffix option appends the
  category name to every inner Others row; the outermost stays 'Others'.
- For hierarchical data, Current Category moves a member into or out of
  Others under its immediate parent only; All Category does so at every level
  containing that member. Flat data uses Current Category.
- Highlight add/remove rows - TopN (Display settings › Miscellaneous) marks
  manually moved rows with custom background and border colours; adding rows
  to Others prompts a notification pointing to that setting.

## Related features

- `MX-SRT-01`
- `MX-RANK-01`
