---
id: CH-MEAS-01
name: Configure measures and dimensions
area: charts
category: Chart data
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/visualization-library/slope-graph
---

# Configure measures and dimensions

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Assigns measures and dimensions, series types per measure, and measure styling.

## When to use

- Every chart.

## UI path

Chart data/series configuration; exact Fabric Plan pane sequence was not captured.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Presentation evidence: screenshots only.
Visible roles: category axis, current/comparison measures, series dimension.
Native bindings and series-style controls: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Confirm each value measure and grain before reusing a chart title. A series
  dimension and a comparison measure are different roles; capture their native
  settings rather than substituting a generic styling property.
- Resolve side/series bindings, category keys and units from the inspected
  semantic model, not title tokens or legend order; appearance does not
  establish assignment keys.
- Map each scenario (actual, prior period, target) to its series type
  explicitly and independently of card measures; capture background-band roles.
- Values above 100 are not automatically percentages; define the score or
  attainment basis. Fractional labels on counts need the measure definition.
  Where low/high values cross, verify scenario versus bound semantics.
- Hierarchical charts need ordered hierarchy dimensions and one additive weight
  at a defined grain. Resolve compact units, unqualified totals and range-band
  boundaries; a status label does not prove a count or lifecycle transition.
- The slope guide maps member identity, ordered points and the numeric value
  to Category, Axis and Actual(s). Resolve native multi-axis bindings and one
  value per member/point; separate-period measures are not proof of an Axis
  dimension, and follow-up horizons are not calendar dates.
- Capture each chart family's data wells; do not borrow roles from another
  family.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/pivotAssignments[] (assignment objects)
Existing model measure in AC/PY: columnType "Measure", dataRoleType "Measure",
  no aggregationType key
Text column counted as a measure: {"bucketId":"AC","columnType":"Column",
  "dataType":"String","dataRoleType":"Measure","aggregationType":"count"}
Pointer: /properties/visualState/hiddenProperties_!!!_measureConfig (JSON string)
config[] keys: role, type, chart, order, yAxis, enable, isVisible,
  chartIsVisible, isTrellis. Types seen: ACTUAL, ADDITIONAL_ACTUAL,
  MULTIPLE_AXIS_CHART, ABSOLUTE_VARIANCE, RELATIVE_VARIANCE. Charts seen:
  groupedBar, integratedVariance, varianceBar, variancePin, bulletChart,
  groupedBarWithWaterfall
Decoded hiddenProperties_!!!_columnFieldsMapping: axis entries from "category",
  stack entries from "group"
Decoded appearance charts.measuresStyle: entries keyed by bucket role (AC, PY,
  PL) and by full measure id; pattern "solid" | "outlined"; lineArea.marker
Evidence: [saved] saved owners.
```

- Keep a counted text column as `dataType: "String"` with `count`; never infer
  distinct count or switch to a summed column [saved]. Match donors by field
  kind and aggregation presence as well as by role [saved].
- Repeated assignments in one bucket are intentional saved structure, not
  duplicates to discard or a supported-series limit [saved].
- When rebinding, change table and field identities only: `columnType` and
  `dataRoleType` stay `"Measure"`, and a blanket string replacement corrupted
  them [saved].
- Role aliases in `measureConfig` (`AC1`, `AC2`, `VA11`) are series-config
  names, not buckets, and `enable`, `isVisible` and `chartIsVisible` are
  separate flags [saved].
- A visual reference whose properties part is missing cannot serve as a
  template [saved].
- Numeric series bound from a Planning visual (`sourceType: "Visual"`,
  `customSource: true`, `visualId`) appear in saved owners [saved]; they are
  not enabled in this release.

## Related features

- `CH-SPLIT-01`
