---
id: CV-EXPL-01
name: Explore Model
area: canvas
category: Modes
status: IS-Confirmed
encoding: unverified
visual: Sheet
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes
---

# Explore Model

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Ad-hoc exploration of the semantic model from the sheet. The editor toolbar
action opens a Semantic Model Explorer view with Back to Sheet, Layout,
Refresh Data and Close All Panes actions and a Fields pane (Assign Data,
Advanced) with Rows and Columns wells.

## When to use

- Self-service analysis.

## UI path

Explore Model.

## Definition encoding

```text
Path: (capture sample)
Side effect seen in a readback: opening Explore Model from a sheet in the editor
  added a definition.json sheets[] entry {displayName: <current sheet name>,
  sheetType: "BI_REPORTING", isHidden: false, workloadItemEntityVisuals:
  [{visualType: "UNKNOWN", isEmbedded: false}]} with no sheet or visual parts.
Evidence: concurrency diff before an update; the sheet Explorer did not list the
  entry, and the next complete updateDefinition without it removed it with no
  visible change.
```

Not yet captured as an authorable feature. Run `core/native-samples.md` before
writing this feature into a definition.

## Constraints

- Never author the scratch entry. In a concurrency diff, classify a new
  `BI_REPORTING` sheet with one `UNKNOWN` visual and no parts as Explore Model
  state, not a user page; if the user did not open Explore Model on purpose,
  omit it from the next complete update.
- Do not open Explore Model during render checks: it writes to the
  definition.

## Related features

- `CV-MODE-01`
