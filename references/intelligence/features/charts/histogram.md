---
id: CH-LIB-11
name: Histograms
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
---

# Histograms

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Frequency of values in bins.

## When to use

- Distribution of deal sizes.
- Age or stay-duration distributions with explicit bin boundaries.

## UI path

Visualizations pane › Charts 100+; type histogram in Search Charts or check the
Statistical category. Capture the histogram, bin and overlay controls. A
labeled frequency plot does not expose their storage keys.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: duration and age frequency bars; one view adds a bell-shaped-looking line.
Bin definitions, native family and overlay calculation/scaling: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Establish whether frequencies count distinct entities or observations (such
  as person-periods or events) before labeling the frequency axis; bin totals
  above the entity count signal observation grain. Capture missing-value rules.
- Intelligence chart library only; never a Power BI native visual.
- Validate complete, nonoverlapping bin bounds and edge inclusion against
  labels; do not infer missing intervals. Define the age reference date,
  duration units, under/overflow and excluded/missing values.
- The largest bin is not necessarily a majority. A curved overlay does not
  prove a normal fit or density estimate; capture its method and count/density
  scale. Unequal bin widths require explicit frequency-versus-density treatment.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "HISTOGRAM"
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"otherChart"
Pointer: /properties/pivotAssignments (axis + AC; one owner adds stack)
Pointer: /properties/visualState/hiddenProperties_!!!_histogram (JSON string)
Decoded keys: binType:"custom" | "excel" | "powerbi"; gapWidth; cumulativeBar;
              showDistributionBar; xAxis{bucketType:"custom" | "step", count or
              step values}; points; overFlowBin{enabled, ...};
              underFlowBin{enabled, ...}
Partial: {"binType":"powerbi","cumulativeBar":true,"showDistributionBar":false,"gapWidth":6}
Evidence: [saved] every inspected saved histogram; saved frequencies, not defaults.
```

- `showDistributionBar` was false in every inspected owner; `gapWidth`,
  `cumulativeBar` and the overflow/underflow flags varied [saved].
- `binType` and `xAxis.bucketType` are independent saved fields; do not make
  them match or infer a named binning algorithm from either [saved].
- Keep `"powerbi"` examples beside `"excel"` and `"custom"` ones; none
  supersedes another [confirmed].
- Count/step values and bin limits persist behind disabled flags [saved].
  Keep them in complete target-specific owners, but never copy business
  cutpoints into reusable fragments.
- What `cumulativeBar` and `showDistributionBar` draw, bin algorithms and edge
  inclusion are unresolved [open].
- Reconcile bin totals with source counts or weights before labeling.

## Related features

- `CH-AX-01`
- `CH-LBL-01`
