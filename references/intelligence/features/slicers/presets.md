---
id: SF-FEAT-04
name: Presets (CF, saved, measure, rank based)
area: slicers
category: Features
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
---

# Presets (CF, saved, measure, rank based)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Preset buttons that apply selections by rule, saved filter, measure threshold, or rank.

## When to use

- 'Top 10 customers', 'Loss-making stores' buttons.

## UI path

Presets.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.presetSettings, filterHiddenSettings.customPresets/groupedPresets
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- For measure-threshold and Top N buttons, capture the rule, measure, units,
  scope/aggregation, ties and reevaluation on context changes.
- Members below a threshold can remain visible: distinguish member selection,
  list visibility, CF and downstream filtering. A button label alone does not
  establish a saved predicate or exact threshold encoding.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Few saved owners set `presetSettings.enablePreset: true` with custom-preset
  collections; other owners keep `enablePreset: false` [saved].
- Preset application and re-evaluation are untested [open]. Resolve preset
  references against target fields; never reuse donor member lists.

## Related features

- `SF-FEAT-01`
