---
id: CV-INT-01
name: Edit interactions (filter, highlight, none)
area: canvas
category: Interactions
status: IS-Confirmed
encoding: observed
visual: Canvas
sources:
  - https://github.com/microsoft/json-schemas/blob/main/fabric/item/plan/definition/Intelligence/Properties/1.0.0/schema.json
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/switch-between-reading-and-editing-modes
---

# Edit interactions (filter, highlight, none)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Controls how a selection in one visual affects others.

## When to use

- Consistent cross-filtering.

## UI path

Edit interactions.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualInteractions {<originEntityId>: {dataInteractionType}}
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- The public Intelligence container stores visual configuration under
  `visuals[].properties.properties`; native flat parts use the observed path
  above. Preserve origin/embedded references and the appropriate wrapper.
  See [definition contracts](../../core/definition-structure.md).
  A schema field alone does not verify a source/target interaction.
- When selected-period cards sit beside full-period trends, test the intended
  period exceptions and actual/target/status coverage per visual. Matching
  control placement does not prove sync; align context before comparing views.
- A caption promising page-wide updates is not evidence of configured
  interactions. Verify each source/target pair (date and facet filters, charts,
  cards, Matrix) and distinguish highlight, filtering and expansion.
- Check AC and LM use consistent non-time context, and that clear/reset and
  no-data selections behave as specified. Matching totals alone do not prove
  configured interactions.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- For each interaction, record source, targets, direction, trigger, fields or
  keys, selection-clearing behaviour and expected result. Distinguish
  cross-filtering, highlighting, hierarchy drill, drill-through, bookmarks and
  synced slicers, and inspect both the visual's own state and shared page and plan
  registrations.
- [saved] An embedded placement carries its own `visualInteractions` inside the
  host sheet's `reactiveVisualProperties[].properties`; inventory it per placement,
  separately from the source owner.
- [saved] Exports with empty configuration slots, cached control state and
  recognizable UI labels contained no working interaction; such evidence never
  establishes one. Without a configured same-family donor, state the gap and
  capture a minimal UI example rather than inventing keys.
- Trigger and clear selections: intended targets change and unrelated visuals do
  not. Test with the real layers and containers, since static z-order does not
  prove click or hover usability. Re-export to confirm persistence, and label any
  interaction that could not be exercised as untested.

## Related features

- `CV-INT-02`
