---
id: KPI-CONT-01
name: KPI containers, groups, and flex layout
area: kpi
category: KPI cards
status: IS-Confirmed
encoding: unverified
visual: KPI card
sources:
---

# KPI containers, groups, and flex layout

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Groups multiple KPIs in one container with flexible layout. A KPI card can be
split into containers that each hold metrics, a chart, an insight chart or an
image. Groups combine elements so they move and resize as one; flex containers
also arrange elements horizontally or vertically with gap, alignment, padding
and per-element Fixed or Fill sizing. Container appearance sets background
colour and opacity, border, corner radius, accent bar and shadow.

## When to use

- KPI strips.
- One card that pairs a headline metric with supporting metrics, a trend
  chart or an image.
- Evenly spaced, aligned KPI tiles that should reflow together (flex).
- Status tiles where a variance measure colours the background, border or
  accent bar.

## UI path

Card › Containers. Select the KPI card, then use Design › Add in the KPI
ribbon or the card's on-object add icon to insert a container (top, bottom,
left or right) and choose its element type. Layer › Customize Layers opens the
Layers pane for groups and flex containers; select a container to open its
Appearance menu.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState (capture sample)
Evidence: none yet
```

True group/flex creation is not yet captured. Existing flat `gridLayout` text
and chart items can be restyled with the scoped, runtime-confirmed patterns in
[card customization](card-customization.md); this does not establish group
membership or flex-container encoding. Run `core/native-samples.md` before
creating uncaptured groups or flex layouts.

## Constraints

- A variance measure chosen for the background overrides the background
  colour. For a custom border or accent-bar colour, set its variance measure
  to None.
- Resizing a group scales its elements proportionally; use the group's
  Position and Size settings for exact placement.
- Flex direction also sets where new elements are inserted. Gap is fixed by
  default; Auto spaces elements evenly. Fill elements expand into free space.
- Borders run along one side or as a full box; corner radius is uniform (All)
  or set per corner (Custom).
- Container metrics and variance measures come only from the bound semantic
  model in this release.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Inside one card

```text
Pointer: /properties/visualState/hiddenProperties_!!!_kpiControls (JSON string)
Decoded: coreContainer {width, height} and gridContainer {width, height} in
  card-local pixels; gridLayout[] items "text" | "chart" | "image" with pixel
  position/dimension, percentagePosition/percentageDimension, groupIds, isHidden
Evidence: [saved] saved native card owners
```

- Scale core, grid and item geometry together and keep pixel and percentage
  values consistent; they are never sheet coordinates [saved].
- Native fits are fractional and differ per card; a save can shift a
  container by about 1px, so preserve native fit, not a fixed size [saved].
- For alignment/fill-only changes, leave both geometry representations and
  native `initialHeight` unchanged. Use tolerant numeric comparisons for
  fractional fits rather than rounding them to pass an exact test.
- Overlapping a full-height main text item with a variance item hid the badge
  in the renderer [confirmed]. Keep items disjoint; use the native panel
  background behind them for a continuous fill instead of extending an item
  over its neighbor. See [split backgrounds](card-customization.md#split-number-panel-and-sparkline-backgrounds).
- How UI containers map to `gridLayout` items or `groupIds` is not isolated
  [open].
- Variance-coloured borders and accent bars sit at decoded
  `kpiControls.variance.border.position` and `variance.accentBar.position`,
  saved as `"none"` on cards without that styling [saved]. Whether `"none"`
  is the UI's None measure is unresolved [open].
- The companion library lists Add and Layout under a KPI ribbon Insert
  group, while the UI path above says Design › Add; the path above stands
  until the label is confirmed in the UI [open].

### Card rows in a horizontal BOX

```text
Registration: BOX; /properties/visualType = 206
Pointer: /properties/visualState/boxState (object)
Keys: boxType "horizontal", initialBoxType, gap, horizontalAlignment,
  verticalAlignment, wrapContent, isExpanded, overflow {horizontal, vertical}
  (both "hidden" when saved)
Membership: each child card's /properties/layerProperties/layerProperties/groupIds
  holds the container's local preVisualId string, not its GUID; sheet.json
  visualGroupMap stayed empty
Evidence: [saved] saved native containers and child cards
```

- `boxType` is the active value and can differ from `initialBoxType` [saved].
- Children can carry other group ids: change only the container entry and
  never replace a numeric string globally [saved].
- Do not infer membership from overlap or names; a childless BOX is not a
  shape [saved].
- `gap` is not an offset to add to normalized child coordinates; update the
  container and child bounds together [saved].
- With hidden overflow, over-wide children may clip instead of wrapping;
  resizing, selection and clickability are untested [open].

## Related features

- `KPI-CARD-01`
