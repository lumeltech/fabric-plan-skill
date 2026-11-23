---
id: MX-CF-03
name: Icons, action dots, and bubbles
area: matrix
category: Conditional formatting
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/apply-conditional-formatting/highlight-tabular-data-with-conditional-formatting
---

# Icons, action dots, and bubbles

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Status icons, action dots and action colours, and bubble sizes driven by rules.

## When to use

- Status columns on operational sheets.

## UI path

Home › Conditional formatting › One-click.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/visualState/cfProps/rules
Observed keys: classificationType:"icon", classificationPosition:"left",
               actionDotMidPercentage, bubbleBasedOn, bubbleColor
```

These reporting Matrix keys do not isolate every icon/action-dot/bubble
variant. Status badges in a screenshot do not prove they use CF rules or an
approval workflow; capture the badge column and its formatting separately.

## Constraints

- Gantt task-grid status symbols and milestone flags/diamonds/checks do not
  establish Matrix icon rules, clickable approvals or a shared status mapping.
  Capture Gantt grid styling and milestone configuration independently.
- Check, cross or flag icons beside status text do not establish action dots,
  clickable actions or a workflow. Confirm Table versus Matrix ownership and
  capture the actual icon rules.
- Pair icons with accessible text and keep one status-to-colour mapping across
  tables, charts and lists; reconcile any difference or state the semantic
  distinction explicitly.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- A saved `classificationType:"icon"` does not alone establish an active
  icon treatment [saved]. Check the rule and master `enabled` flags,
  targets and conditions (`MX-CF-01`).
- Icon rendering and precedence between icon rules were not runtime-tested
  in the companion work [open].

## Related features

- `MX-CF-01`
