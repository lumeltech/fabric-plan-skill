---
id: CH-SORT-01
name: Sorting and Top N in charts
area: charts
category: Chart data
status: IS-Confirmed
encoding: observed
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/sorting-data
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/ranking-data
---

# Sorting and Top N in charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Measure, axis, and variance-based sort; Top N + Others on axes and trellis panels; dynamic ranking with parameters.

## When to use

- Ranked bars; long category lists.

## UI path

Chart › Sort / Ranking.

## Definition encoding

```text
Pointer: /properties/visualState/hiddenProperties_!!!_sorting (JSON string)
Default state: unset (null). Earlier saved sorted bar: sortBy:"Measure[<measure>]",
               sortType:"descending"
Time axis, oldest first (UI-saved line, area and column charts and KPI cards):
  {"sortBy":"category","sortType":"ascending","includeOtherInSort":false,
   "isDefaultValue":false,"reduceOverlaps":false}
Template default {"sortBy":null,"sortType":"reset","isDefaultValue":true} drew a
  month axis newest-first, although the model's sort-by column was chronological.
Pointer: /properties/visualState/hiddenProperties_!!!_ranking (JSON string)
Default keys: enabled:false, type:"off", noOfItems:5, filterBy:"Measure[<measure>]",
              showOthers:false, customOthersColor:false, othersColorConfig
Related groups: panelSorting, stackedSorting, panelRanking, stackRanking
Evidence: live export of a UI-created test Plan (default state); measure sort
          descending rendered as expected in a published report; the ascending time
          sort matches UI-saved charts (its fix in that report awaits confirmation).
```

Ranking is disabled by default even though `noOfItems` is stored; do not
equate a visible ranked order or scroll with Top N. Copy the full matching
groups; active Top N/others needs capture. A visual-level Top N filter on the
axis field (native `NESTED_RANKING` extra filter, see CV-FILT-01) rendered a
working Top 10 bar chart. Change only the `sorting` group for a time axis; the
panel and stack groups belong to small multiples and stacks.

## Constraints

- Define ranking scope: ranking measure (value, signed or absolute variance),
  global versus per-parent N, eligible members and share-of-total denominator.
  A Top N subset need not equal the total.
- Use deterministic ties and define whether Bottom N excludes zero or blank
  members. State N in titles; low volume is not negative growth.
- Keep ranked membership (Top N/others) separate from display order. Captions,
  scrolling, visible member counts, partial branches, cropped paths or dense
  legends do not establish an active Top N, filtering or a saved sort.
- Order period axes by numeric year/month/period keys, independent of legend
  order; periods shown in value order do not prove a saved value-sort control.
  Resolve years missing from period labels; value changes are not rank changes.
- In hierarchies, define parent and child order separately, preserve full
  paths and keep member IDs stable.
- On mirrored or matched-row layouts, use one shared ordering measure or
  category order; never sort sides independently. Compute cumulative shares
  in the displayed order.
- Use a consistent member order across related charts or an explicit
  per-metric ranking. ID order is not a value ranking.
- Keep ranked entity identity distinct from group/parent labels; shared credit
  or mix differences can invalidate naive member comparisons.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- In a native grouped-measure cluster, `hiddenProperties_!!!_stackedSorting`
  sorts by the synthetic `[Measure Value]` descending while the axis
  `sorting` stays `reset` [saved]. Measure assignment order and group indices
  do not prove the rendered legend or bar order; test it [open].

## Related features

- `KPI-CHART-01`
- `CV-FILT-01`
