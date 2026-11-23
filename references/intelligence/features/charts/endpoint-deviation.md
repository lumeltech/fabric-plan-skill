---
id: CH-DEV-02
name: Endpoint deviation brackets and arrows
area: charts
category: Chart analytics
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-a-dashboard
---

# Endpoint deviation brackets and arrows

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Connects two points with a bracket/arrow and an absolute and/or relative delta.
This is distinct from integrated scenario variance bars.

## When to use

- First-to-last month change on a trend; quarter-to-quarter deviation.
- Start/end callouts on faceted trend panels, forecast lines and
  period-grouped bars.

## UI path

Chart deviation controls; the exact Fabric Plan click sequence was not captured.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/visualState/hiddenProperties_!!!_deviationLine (JSON string)
Decoded keys: enabled:true, label:"both", arrowStyle:"closedArrow",
              multipleDeviations[], connectorLineStyle:"solid"
Observed endpoint entry: categories.from:0, categories.to:11,
                        measure.from/to:"Measure[<measure>]"
```

Copy the complete matching group and remap measure/category/group references
through field closure. This is saved multi-panel state, not a minimal verified
fragment. Follow `core/native-samples.md` to isolate endpoint settings.

## Constraints

- Define endpoints, comparison denominator and zero/missing handling.
- Endpoints can be selected members, category totals, scenario totals (such
  as PY to AC) or periods; capture which, and bind the exact endpoint measures
  independently of intermediate bars. Capture endpoint scale/break behavior.
- A difference between two percentages is in percentage points, not
  necessarily relative percent; label it accordingly.
- A visible bracket does not prove YoY growth, CAGR or a causal explanation.
- Stored category/group IDs and indices depend on ordering/filter context;
  do not reuse them blindly on another model.
- Sort, ranking or filter changes must preserve the intended endpoints or
  explicitly clear an invalid comparison; never silently retarget them.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Saved owners without a visible bracket, KPI cards included, still carry a
  `hiddenProperties_!!!_deviationLine` group; its presence is not activation
  [saved].
- A color edit saved inside a disabled deviation line is dormant, not a
  visible enhancement; read `enabled` before treating a difference as a
  design change [saved].

## Related features

- `CH-DEV-01` — integrated variance.
- `CH-ANLY-01` — average/trend analytics.
- `CH-MULT-01` — panel-specific endpoints.
