---
id: MX-RANK-01
name: Row and column ranking
area: matrix
category: Sort, filter, Top N
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/ranking-data
---

# Row and column ranking

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Adds rank columns overall or within a group. Overall ranking ranks rows across
groups in one click but leaves subtotals unranked; Ranking within a group ranks
members inside each parent and also ranks subtotals. Choose the base measure
and insert the rank as a visual measure or a visual column.

## When to use

- League tables.
- Peer ranking inside each region or category (within a group).
- An explicit rank number beside values rather than filtering or colouring.

## UI path

Insert › Quick formula › Rank. Pick Overall ranking or Ranking within a group,
then set Insert as (measure or column) and the base measure.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Overall ranking applies no ranks to subtotal rows; use Ranking within a group
  when parent levels need ranks too.
- A visual measure repeats under each column category; a visual column appears
  once at the end, outside the column hierarchy.
- Quick formula results can be referenced in custom formulas.
- Rank columns neither filter nor highlight: use Top N (`MX-SRT-03`) to limit
  rows, or a conditional-formatting Ranking rule for top/bottom N or top %.
- Ranking rules on parent categories need Row hierarchy levels set to Values
  and totals.

## Related features

- `MX-SRT-03`
