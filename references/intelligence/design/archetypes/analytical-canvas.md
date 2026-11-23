# Archetype: Analytical Canvas

<!-- Design topic for the `fabric-plan-skill` skill. Optional example, never an automatic fallback. -->

**Reader:** analysts. **Question:** "Why did this happen, and where?"

## Composition

Optional example, not a required layout for analytical reports. Use only
when selected in the session design; custom layouts and themes are equally
valid. The suggestions below describe this example, not all reports.

- Filter rail or band with 3–5 slicers (hierarchy, facet, search).
- Main exploration visual: Matrix with hierarchy rows and time columns, or a
  chart with drill-down.
- 2–3 supporting views: distribution, relationship (scatter), Top N.
- Cross-filtering between all visuals.

## Variants

| Variant | Example analytical fit | Layout |
|---|---|---|
| A — Rail + Matrix | Hierarchies, many measures | 3-col left rail; 9-col Matrix with drill and Top N; supporting chart below |
| B — Two-up exploration | Two lenses (time × segment) | KPI row (optional); two 6-col charts; detail Matrix full width |
| C — Scatter quadrant | Two measures per entity | Scatter with average lines; ranking Matrix; facet slicers |

## Rules

- Enable search on long slicers; hierarchy slicer for nested dimensions.
- Matrix: pin row headers, Top N + Others for long lists, totals labelled.
- Explain quadrant / outlier logic in the subtitle or a note.

Typical features: `MX-LAY-01`, `MX-LAY-03`, `MX-SRT-03`, `SF-HIER-01`, `SF-FEAT-02`, `CH-LIB-01`, `CV-INT-01`.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Record Top N and Others, denominator scope and whether filters change the
  ranking population
  (selection gate).
- Quadrant views need observations at one defined grain; association is not
  causation, so explain it as a relationship, not a cause.
- **Optional (companion default):** A1 filter-rail slots on the
  companion grid, used only when four
  or more slicers fill at least half the rail, with at most nine elements;
  this applies only when the user or session design selects it and never
  overrides the session theme, supplied designs, report-inspiration guidance
  or IBCS opt-in.
