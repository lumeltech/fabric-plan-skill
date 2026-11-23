---
id: CH-LBL-01
name: Data labels
area: charts
category: Chart settings
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
---

# Data labels

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Label position, content, min/max highlight, formatting.

## When to use

- Replace gridlines with labels.

## UI path

Chart › Data labels.

## Definition encoding

```text
Pointer: /properties/visualState/hiddenProperties_!!!_appearance (JSON string)
Pointer: /properties/visualState/hiddenProperties_!!!_numberFormatting (JSON string)
Earlier saved number keys: enabled:true, noOfDecimal:1, noOfDecimalPercent:2,
                           scalingFactor:"auto"
Default label-related keys: commonSettings.showDataLabelOnHighlight,
  showDataLabelAsSubTitle, applyHighlightedDataLabelColor,
  highlightedDataLabelColor; chartCustomTitle.isDataLabelTitleAdded
Evidence: live export of a UI-created test Plan (default state); not isolated by
          a before/after change or re-rendered after reapplication.
```

Some default chart exports omit the dedicated data-label group; omission does
not mean labels are off. Label content, position and min/max activation keys
are **not isolated**. Copy matching whole settings or capture a one-change
sample. Screenshots show extrema, endpoint, value/share
and donut category/value/share labels, not their settings. Do not invent
`minMaxLabels` or contribution properties.

## Constraints

- Data labels are off by default. Enable them only when every label fits
  without overlap or crowding, typically few categories in a wide plot
  [confirmed]. Integrated variance charts keep their built-in labels.
  Saved off-state: `dataLabel.labelStyle.<measure>.enabled: false` [saved].
- Format axes and labels independently from each measure's verified units:
  integers for counts, percent for rates/shares, explicit currency scaling and
  rate units. Distinguish percentage points, score points, shares, cumulative
  percentages and compact magnitudes.
- Use enough precision that nonzero values never render as `0.0` or negative
  zero and signs match the graphic. Rounded labels round independently; check
  raw totals/shares before calling a small mismatch a data error.
- Give every share label an explicit denominator (parent, root or overall).
- Capture each label layer (value, share, category, interval caps) with its
  content order, anchor, orientation and contrast. Test collisions, leader
  lines, clipping and short bars; overlapping equal values are not duplicates.
- Keep each label tied to its scenario/series. Where values are omitted,
  compact or unreadable, provide exact values via native labels or a verified
  tooltip; never estimate from lengths, pixels or rounded shares.
- Use full legends and untruncated names. Disclose unlike units on parallel
  axes, and derive histogram labels from verified bin settings.
- Colored min/max/end labels, or a caption promising them, do not prove saved
  activation keys or favorable performance. Never expose protected identities
  through full-label tooltips.
- Gantt has its own label position/font/background/offset controls; do not
  borrow chart-engine keys. Test collisions with connectors and zoom; crossing
  lines are not evidence of completed-task strikethrough formatting.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_dataLabel (JSON string)
Decoded children: selectionMeasureKeys, allMeasureStyle, measureOverrides,
  labelStyle
labelStyle: keyed by native measure identity, never a caption; entry display
  "auto" (density fit) or "limited"; labelFormat.valueType[] lists numeric and
  text roles, e.g. {"value":"TXT1","measureKey":"TXT1"} (partial);
  labelFormat.displayFormat is a separate structure
measureOverrides: may be empty; can hold numeric flags and dotted keys such
  as "enabled": 1 and "labelFormat.valueType": 1
Evidence: [saved] saved line and bar owners; not isolated one change at a time.
```

- Preserve dotted keys and JSON types: numeric override flags are not
  interchangeable with the boolean `labelStyle[...].enabled` [saved]. Never
  copy `valueType` over `displayFormat` [saved]. Their precedence is
  unresolved [open].
- Rebind `labelStyle` keys and the record's runtime `measureName` to the
  target measure identities [saved].
- Text roles (TXT1, TXT2) need real `TextCategory` bindings; a model field is
  in scope, while InfoBridge text outputs are not enabled in this release
  [saved]. A saved text label does not prove that it renders [open].
- An empty `hiddenProperties_!!!_seriesLabels.labels` array does not mean
  labels are off; label formatting lives in `dataLabel` [saved].
- Signed variance bars: auto label density with explicit `+` signs and value
  color is one saved finishing pattern (`CH-DISP-01`), not a universal rule
  [saved].

### Disabling labels on a line trellis

The following native label-style variant was published, read back and visually
checked on both actual/PY LINE trellises [confirmed]:

```text
hiddenProperties_!!!_dataLabel (JSON string):
  {"labelStyle": {
    "<native actual measure id>":
      {"enabled":false,"display":"none","varianceDisplay":"none"},
    "<native prior-year measure id>":
      {"enabled":false,"display":"none","varianceDisplay":"none"}
  }}
```

Resolve each key from the target measure binding, never its displayed caption
or just `AC`/`PY`. The tested source had no dataLabel group; adding it removed
the default point labels. When a group already exists, preserve its other
settings and update the applicable entries, respecting existing overrides.
Panel titles, legends, axis ticks and tooltips are separate owners and were
retained. Do not remove axes or clear `seriesLabels` as a substitute.

## Related features

- None.
