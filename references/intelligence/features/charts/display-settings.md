---
id: CH-DISP-01
name: Chart display settings (canvas, legend, number, tooltip)
area: charts
category: Chart settings
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/visualization-library/slope-graph
---

# Chart display settings (canvas, legend, number, tooltip)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Canvas, legend, number scaling, data table, tooltip, and other settings.

## When to use

- Apply the design system.

## UI path

Chart › Display settings.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Presentation evidence: screenshots only.
Visible: series legend, numeric labels and a data table below a combo plot.
Exact data-table activation, layout and display settings: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Capture category placement (center gutter or side), spacing, headings and
  series colors separately. Pale fills do not prove CF or analytic meaning.
- A grid-like button does not verify a configured data table; test the action
  and accessible exact-value display. Match data-table series, category
  order, filters, scale and rounding to the plotted values.
- Capture radial geometry (radius, ring widths, center label, color
  inheritance) from the same chart family; donut geometry keys are not
  evidence of sunburst encoding. Check contrast and path/value access when small.
- The slope guide documents Line color > Individual and Marker/Label > Use
  trend color, not every shape/size/legend setting. Capture native controls,
  overflow and ownership; legend membership does not prove a complete path.
- Screenshots show display context, not every tooltip/canvas setting; capture
  only the options required. Use readable date labels, not copied truncation.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/visualState/hiddenProperties_!!!_numberFormatting (JSON string)
Keys seen: scalingFactor "auto" | "1000" | "1000000"; suffix; showScalingUnit;
  displayScalingIn "title"; positiveValueFormat "x" | "+x";
  negativeValueFormat "-x"; showValueColor; customFormat entries keyed by
  measure identity, _TOTAL, totals and comparison roles, each with enabled
Pointer: hiddenProperties_!!!_legendSettings: legendMarkerStyle
  "lineAndMarkers"; showTitleAsLegend false on several waterfalls and
  horizontal charts
Pointer: hiddenProperties_!!!_chartCustomTitle: custom title HTML, height
  (title allocation), editTitle
Evidence: [saved] saved owners after user finishing edits.
```

- Millions (user correction): with `scalingFactor: "1000000"` leave the
  custom `suffix` empty, because native scaling already shows the unit
  [confirmed]. Validate scaling and suffix together, including enabled
  per-measure overrides; check rendered axes, labels and KPI values for a
  doubled unit, inspect tooltips separately, and never divide already scaled
  values again [confirmed].
- When repairing, clear a redundant `M`/`m` suffix wherever scaling is
  `1000000`, in the root group and in enabled or dormant overrides, without
  enabling them. Keep scaling, precision, signs, currency and other suffixes,
  then read back and confirm none remain [confirmed].
- `customFormat` entries that appear with `enabled: false` after a save are
  materialized defaults, not an applied format change [saved].
- `"auto"` and an older `"autoFixed"` scaling value are distinct settings;
  learn the saved form of the intended option [saved].
- `positiveValueFormat: "+x"` with `showValueColor: true` makes variance
  direction explicit; check favorability per measure [saved].
- Title heights differ by family and edit (about 34-51 px in saved owners);
  keep component-specific allocations rather than one height [saved]. Blank
  saved title text with an enabled auto title does not prove that no title
  renders [saved].
- Saved chart owners carry a `hiddenProperties_!!!_dataTable` group [saved].
  Its activation and layout keys are still not isolated [open].

## Related features

- None.
