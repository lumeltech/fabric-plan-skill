---
id: CH-SPLIT-01
name: Splitting and grouping measures
area: charts
category: Chart data
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Splitting and grouping measures

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Split shows each measure of a multi-measure chart in its own panel and adds a
Measures category that can be placed in rows, columns or the legend (legend
placement renders the measures stacked). Group measures combines selected
measures into named custom groups, one panel per group, each with its own
chart type. In small-multiples (matrix) mode, row or column groups combine
measures or dimension members into a single row or column.

## When to use

- Multi-measure comparisons.
- Many non-comparative measures crowding one chart: one panel per measure.
- Related measures, such as actual and comparison measures of one period,
  that belong in a shared panel.

## UI path

Chart › Split / Group. On the chart ribbon (Measure group) select Split; open
the Split dropdown › Group Measure › Add new group, select the measures, enter
a Title and Apply. Change each group panel's chart type afterwards. In
small-multiples mode the Group Measure pane adds a Bucket option (Row or
Column) for row or column groups.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Split is documented for multiple non-comparative measures.
- A new measure group renders as a line chart by default; set each panel's
  chart type explicitly.
- Dimension groups work only in matrix mode (dimensions in rows or columns,
  not both), and only row groups or column groups at a time.
- Placing the Measures category in the legend stacks the measures; rows or
  columns keep one panel per measure.
- Documented UI steps are not encoding evidence; capture a native split or
  group sample before writing it into a definition.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Measures category (native measure grouping), saved encoding, partial:
Pointer: /properties/transformMeasure = "groupMeasure"
Pointer: /properties/pivotAssignments: stack entry {"bucketId":"stack",
  "id":"[Measure Name]","columnName":"Measures Category",
  "columnType":"MeasureCategory","dataRoleType":"Grouping"}, no tableName
Pointer: /properties/groupMeasureAssignments[]: each grouped measure with
  bucketId "__group_measure_assignments__", columnType "Measure", order 0..n
Decoded hiddenProperties_!!!_comparisonMeasureMapping: config
  {"AC":"[Measure Value]"}, allMeasures [{"AC":"[Measure Value]"}],
  defaultBucket "auto", standardNotation true
Decoded hiddenProperties_!!!_columnFieldsMapping: axis and activeAxisBucket keep
  the axis field; stack uses "[Measure Name]" for name, hierarchy and
  fieldName with from "group"
Decoded appearance charts.groupStyle: keys "C0-%-<measure or group caption>";
  splitByCategory.pivotValueAssignments empty in this mode
Evidence: [saved] a user-corrected clustered column; also seen in clustered
  and stacked lines and in breakdown waterfalls.
```

- `[Measure Name]` and `[Measure Value]` are synthetic: they are not
  semantic-model fields or model gaps, and must never be created as model
  measures [confirmed].
- Clone the complete grouped owner and rebind the axis and each grouped
  measure as one change; adding only the synthetic category or only the
  measures is incomplete [confirmed].
- Reconcile group keys, the group-index map (`hiddenProperties_!!!_groupIndexMap`),
  styles and labels with the real measure names; stale keys can remain after
  regrouping and are not the active ones [saved]. Keep each grouped measure's
  own identity, format and order; never fabricate ordinary AC/AC1
  assignments instead [saved].
- Saved owners also carry `hiddenProperties_!!!_groupMeasures` [saved].
  Whether it stores named Group Measure panels is unresolved [open].
- Whether this encoding comes from the Split (Measures category in the
  legend) or the Group Measure route, and how group order renders, is
  unresolved [open].

## Related features

- None.
