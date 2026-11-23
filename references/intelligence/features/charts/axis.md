---
id: CH-AX-01
name: Axis customisation
area: charts
category: Chart settings
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/visualization-library/multi-axis-chart
---

# Axis customisation

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

X and Y axis scale, labels, gridlines, breaks, and titles.

## When to use

- Readable scales; zero baseline for bars.

## UI path

Use the selected Fabric Plan chart's axis controls; capture the exact scale,
title, gridline and break controls for that family. Multi-axis documentation
establishes separate measure axes, not every axis customization switch.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Presentation evidence: screenshots only.
Visible: separate quantity/rate axes, category labels and mirrored scales.
Exact domains, axis mapping, gridline/title controls and breaks: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Capture zero baselines, axis direction, bounds and category order. Screenshots
  do not prove automatic domains or axis breaks; avoid inventing those settings.
- Mirrored layouts plot positive magnitudes on both sides; leftward does not
  mean negative. Capture each side's zero origin, reversal and shared bounds.
- Give each overlay (percentage, cumulative, reference) its own labeled scale;
  never read an overlay's position against the bar-value axis.
- Same-unit comparisons (actual versus plan, period endpoints) should share a
  domain; otherwise equal values can sit at different heights. If scales stay
  independent, disclose it and compute changes from raw values.
- Label every unit and domain; never equate lengths across independent domains.
- Capture bounds, direction, normalization, filter behavior and tick precision;
  a compact tick label is not enough to infer the axis minimum.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_xAxis (JSON string)
Keys seen: label.display "auto" | "rotated"; label.rotation -90 | 0;
  label.isBold; title.enabled; isDefaultValue; enableScroll "auto"; step
Pointer: /properties/visualState/hiddenProperties_!!!_yAxis (JSON string)
Keys seen: yAxis1.enabled, show, label.enabled, label.fontSize, title.enabled,
  position "leftOrTop" | "rightOrBottom", customMinMax {enabled, customMin,
  formattedCustomMin}; secondary-axis label and title flags
Evidence: [saved] user-finished saved owners; not isolated one change at a time.
```

- Read label mode and angle together: `"rotated"` with `rotation: 0` is not
  vertical text [saved].
- Manual bounds apply only when `customMinMax.enabled` is true; a retained
  `customMin` with `enabled: false` is no axis floor [saved].
- Secondary-axis flags alone do not prove a rendered secondary scale [saved].
- An axis font size saved as `null` inherits the theme rather than a
  hard-coded size [saved].
- A finished horizontal bar hid its redundant measure-name axis title and
  moved the primary axis to `rightOrBottom` [saved]; these are not universal
  rules, and the rendered placement on horizontal charts is unconfirmed
  [open].
- Multi-axis tick-label weight default: see `CH-MULTI-01`.
- Saved owners also carry `hiddenProperties_!!!_linearXAxis` [saved]. Its
  role is unresolved [open].

## Related features

- None.
