---
id: KPI-FMT-01
name: Card formatting, formulas, text, and images
area: kpi
category: KPI cards
status: IS-Confirmed
encoding: observed
visual: KPI card
sources:
---

# Card formatting, formulas, text, and images

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Text, formulas, images, number settings, and card display options.

## When to use

- Apply the design system.

## UI path

Card › Display settings.

## Definition encoding

```text
Pointer: /properties/visualState/hiddenProperties_!!!_kpiControls (JSON string)
Decoded paths: title, total, measures, groups, coreContainer, layout, preset,
               responsiveFontSize, kpiFitMode, isMinimalView, minimalViewConfig
Earlier saved style paths: title.style, total.style
Evidence: live export of a UI-created test Plan (default state); not isolated by
          a before/after change or re-rendered after reapplication.
```

Copy the complete saved Fabric Plan card state for layout/text styling.
Formula, image and categorical content controls are not isolated; do not
invent expressions from screenshot captions. Categorical, ratio and date cards
require explicit category/ratio/date roles, not only number formatting.

```text
Value format inside kpiControls.gridLayout[].staticText mention attributes
  (HTML-escaped JSON): {"prefix":"$","noOfDecimal":2,"enabled":true} — the native
  default prefix is "$"; replace the prefix for another currency symbol.
  Percent values: {"noOfDecimal":1,"scalingFactor":"percentage","enabled":true}
  with isPercentageVal:true and userModifiedPercentage:true on the mention.
  Counts: {"prefix":"","noOfDecimal":1,"enabled":true}.
Evidence: card values rendered as expected in a published report (currency prefix,
  percentages and counts user-confirmed).
```

Auto scaling shows k/m suffixes; lakh/crore scaling has no native encoding.
Changing the currency symbol does not convert values: state the source currency
or apply an approved conversion measure.

### One title per card

There are independent outer and internal title surfaces. The outer visual
uses decoded `hiddenProperties_!!!_chartCustomTitle.showTitle`; the internal
card uses `hiddenProperties_!!!_kpiControls.title` and rich-text
`gridLayout[].staticText`, which can contain `[$Title]`. Changing only
`title.enabled` may leave a template title visible.

A captured single-title configuration hides the outer title with
`showTitle: false` and retains the internal native title. Preserve the full
card template and verify exactly one title after rendering. Comparison
mentions such as Plan belong only on cards with the corresponding bound role.

## Constraints

- Verify registry bindings before writing or relabeling titles and support
  captions. A title or caption that disagrees with its bound value is a
  binding to resolve, not a naming template; labels must describe the measure.
- Preserve each metric's unit and scale: currency, counts, durations, days,
  ratios, percentages and rating scales. Use integer formats for observed
  counts; keep event counts, row counts, scores and percentages distinct.
- Format headline, support, comparison and mini-chart roles independently.
  Percentage headlines must not become raw fractions in chart labels; format
  per-day rates separately from totals and ratios.
- Format identical raw measures consistently (full or compact) and keep scaled
  labels consistent with model descriptions. Display rounding must never change
  the calculation; fractional budget counts may represent allocations.
- Apply percent format only to a true ratio or a documented normalized score,
  and label its basis; composite achievement needs documented weighting.
  Do not silently cap legitimate above-target attainment values.
- Capture static versus bound text and any rank/share scope. Highlighted tokens
  or a variable caption do not prove Matrix variables or editable inputs.
- Capture pictogram/icon ownership separately from built-in dynamic variance
  controls, and pair status color with accessible status text or icons.
- Underlined or highlighted titles do not establish link actions or persisted
  formatting; capture whether a highlight is transient.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Text items and mentions

```text
Pointer: /properties/visualState/hiddenProperties_!!!_kpiControls (JSON string)
Decoded gridLayout[] item types: "text", "chart", "image"
Text item keys: type, id ("staticId_TopBottom", "staticId_TopBottom_2"), name,
  measureKey "AC", dataType 4, padding, groupIds, isHidden, staticText,
  format {bold, italic, underline, subScript, superScript, strikeThrough,
  textAlign "unstyled", link {text "[$Value]"}, fontSize, color}, position,
  dimension, initialHeight, layoutStyle {alignment "center", justifyContent
  "center", bgColor}, percentagePosition, percentageDimension
Mention: <span class="mention" data-id="TITLE | VALUE | TITLE_VARIANCE"
  data-value="HTML-escaped JSON {name, id, label, image, avatar}">[$Title]</span>
Evidence: [saved] saved native card owners
```

- Copy mention spans whole, including `data-id` and `data-value`; bare
  `[$Value]` tokens render as literal text [confirmed].
- Doubled braces in `data-value` (an unformatted template string) rendered
  the literal placeholder, such as `[$Variance]`; read back `staticText` and
  require single-brace JSON [confirmed].
- `data-value` can be single- or double-quoted; parse HTML attributes rather
  than matching one quote style [saved].
- A mention's own `numberFormatting` can be a JSON string inside the escaped
  `data-value`, inside the `kpiControls` string. Keep absent keys absent and
  do not copy one token's override to other measures [saved].
- `gridLayout` holds items directly; no nested `elements` key [saved].

### Alignment-only changes

- On a captured split-card text item, `layoutStyle.alignment: "flex-start"`
  with `justifyContent: "center"` and outer paragraphs
  `<p style="text-align:left">` rendered vertically centered, left-aligned text
  [confirmed]. Reversing the layout values rendered top-left, not middle-left;
  do not infer axes from generic flex conventions.
- Centering an existing variance badge used both layout values `"center"` and
  `<p style="text-align:center">` [confirmed]. Preserve the badge's pixel and
  percentage geometry, padding, colors and mention spans when only text
  alignment is requested. Edit literal outer paragraphs, not escaped mention
  metadata or nested formula HTML.
- These values were checked on native flat split-card items, not arbitrary
  grouped/flex layouts. Recheck the rendered main block and every badge.

### Presets, layout and styling

- In every inspected saved card owner `kpiFitMode` is `"Content"`; `layout`
  is mostly 1 or 2 and split sparkline cards save 4; `preset` is usually 0,
  with 1, 2, 4, 5 and 11 also saved; `responsiveFontSize: true` is common
  [saved].
- Numeric `layout`/`preset` UI meanings are unmapped; never infer a named
  preset from the integers [open].
- Preset flags travel with the layout flags: `isSimplePreset`,
  `isLayoutEdited`, `isLayoutModified`, `isDefaultPreset`, `previousPreset`
  [saved].
- Restyling only `staticText`/`format` left stale geometry and preset
  metadata (`isDefaultPreset: false`, `previousPreset`), so correct text
  rendered wrongly; deep-copy a complete compatible `kpiControls` instead
  [confirmed]. Then reapply the card's comparisons, chart items and content;
  never apply a single-card reset to a trellis or sparkline card.
- Formatting follows the preset: a user-corrected preset keeps one
  title/value/variance text item with `format: null` and inline 14/28/12px
  spans, plus `numberFormatting.semanticFormatting: true`, while an earlier
  split layout lost styling with `format: null` and needed an explicit
  element `format`, which can override inline spans [confirmed]. Clone the
  chosen preset; do not normalize all cards.
- Optional donor styles (the session design wins): Light puts the title over
  the value (16px regular, 32px bold accent) on a white panel; Filled puts the
  value over the title (28px bold, 14px regular) on a solid panel fill with
  auto-contrast or explicit white spans [saved]. Do not carry Light's
  coloured spans into Filled.
- Native fits are fractional (text widths just under 100%); preserve them
  rather than rounding [saved].

### Borders and surfaces

```text
Outer border: /properties/visualStyles/border {isEnabled, color, width,
  side "all"}, mirrored at /properties/visualState/visualStyles
Internal: /properties/visualState/hiddenProperties_!!!_smallMultipleAppearance
  (JSON string): panelBackground {type "all", panelBackgroundColor,
  alternatePanelBackgroundColor}; panelBorder {enabled, position, color,
  style, thickness, isDefault}; accentBar {enabled, position, color, style,
  thickness}
Evidence: [saved] saved native card owners
```

- KPI › Border › Weight is `panelBorder.thickness`; on non-trellis cards
  keep it and `accentBar.thickness` at 0. A stale `thickness: 1` drew a
  nested double border after the layout was fixed [confirmed].
- `isEnabled: true` with `width: 0` drew no outer border [confirmed].
- Fixing `kpiControls` does not fix a stale `smallMultipleAppearance`; set
  both independently [confirmed].
- Whether Layout › Effects › Border writes exactly `visualStyles.border` is
  unconfirmed [open].
- Optional companion default (the session `cardStyle` wins): a 1px neutral
  outer container border on every card, separate from the internal panel
  border; never show two visible nested borders.
- Check the active `appearance.charts.chartBackground`, panel fill, outer
  fill and span colours together: a user save aligned a light card's
  inherited dark chart background to its white panel [confirmed].
- `charts.globalAutoFontColor: true` coexists with explicit span colours and
  is not a theme selector [saved].

### Split number-panel and sparkline backgrounds

- Audit outer `visualStyles` and its `visualState.visualStyles` mirror,
  `appearance.charts.chartBackground`, `customTheme.chart.background`,
  `smallMultipleAppearance.panelBackground` and each item's
  `layoutStyle.bgColor`. A stale native panel fill can remain visible even
  when the other background owners agree [confirmed].
- For a continuous colored number side and white sparkline, the captured
  solution sets both native panel background colors to the chosen number-side
  color and retains a full-height white chart item on the right. This fills
  behind the main text and badge without overlapping their items [confirmed].
  Use the approved palette, not a fixed purple/white theme.
- Keep the main text and variance items non-overlapping. Expanding the main
  text item to full height hid the badge despite a successful save/readback
  [confirmed]. In one working split, main text occupied the upper 74%, the
  badge started at 74% with 20% height, and the chart occupied the right 56%
  at full height. These are sample proportions, not universal defaults.
- For an unwanted gap inside an outer border, inspect
  `visualStyles.padding` before enlarging the card. Disabling padding and
  zeroing its four stored side values on the owner and existing mirror
  removed the outer inset [confirmed]; item padding is a separate setting.

### Number formatting group

```text
Pointer: /properties/visualState/hiddenProperties_!!!_numberFormatting (JSON string)
Keys: enabled, ibcsformat, thousandSeparator, decimalSeparator, noOfDecimal,
  noOfDecimalPercent, scalingFactor, showScalingUnit, semanticFormatting,
  showNullAs "hidden", showZeroAs, kpiTotalType "native", displayScalingIn
  "title", customFormat (per measure), shortUnitText {thousands, millions,
  billions, trillions, percentagePoints "pp", basisPoints "bps"}
scalingFactor types: strings "auto", "none", "uniform"; number 1000000
Evidence: [saved] saved native card owners; preserve JSON types
```

- Companion rule: percentage measures set `scalingFactor: "percentage"` and
  `showScalingUnit: false`, because `"auto"` can show a raw fraction or the
  wrong unit [open].
- Verify the rendered unit before changing `displayScalingIn` [open].
- A report-only currency override can require changes in measure assignment
  `formatString`, chart number-format overrides and each current/PY mention's
  nested number format, not only the top-level prefix [confirmed]. Limit it
  to monetary roles; preserve counts, percentages, values and model metadata.
  Inspect decoded characters for malformed source currency markers rather
  than blindly replacing text across the report. Symbol changes are not FX.

### Image items

```text
Decoded gridLayout[] item: {"type":"image","isHidden":false,"fgImage":
  {"source":"custom","foregroundFill":"contain","customForegroundImage":"<string>"}}
Saved with layout 1 and preset 11 on single-AC cards that keep the
  COLUMN_VERTICAL template and "columnChart" renderer
Evidence: [saved] saved native card owners
```

- `customForegroundImage` held a base64 `data:image` URI in one source and
  encoded resource locators in others, so base64 does not prove a
  self-contained image [saved]. Use a destination-owned asset; never copy
  donor resource ids.
- An image is not a series, comparison or sparkline binding; caption it with
  text items. Image plus sparkline on one card is uncaptured [open].
- The preset label, asset picker and rendering are unconfirmed [open].

### Filled preset variants

- Filled donors differ: later ones put the title above the value with
  explicit white spans. Neither ordering nor auto-contrast is universal, so
  keep the selected preset whole [saved].

## Related features

- `KPI-CARD-01`
