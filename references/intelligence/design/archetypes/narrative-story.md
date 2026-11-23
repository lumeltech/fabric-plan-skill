# Archetype: Narrative Story

<!-- Design topic for the `fabric-plan-skill` skill. -->

**Reader:** review meeting, external audience. **Question:** "What happened, and what does it mean?"

## Composition

Optional example, not a required layout for review packs or narrative reports.
Use only when selected in the session design; custom layouts and themes are
equally valid. The suggestions below describe this example, not all reports.

- Title + one-sentence takeaway.
- Sequence of 2–4 visuals in reading order, each with a short annotation.
- Notes/annotations on data points (`MX-NOTE-01`, `CV-ANN-01`).
- Few or no slicers; bookmarks for story steps (`CV-BMK-01`).
- Paginated / exportable version for packs (`MX-PAGE-01`, `MX-EXP-01`).

## Variants

| Variant | Example analytical fit | Layout |
|---|---|---|
| A — Vertical story | One storyline | Stacked sections: headline chart → driver Matrix → outlook |
| B — Bookmark steps | Presenter-led | Same canvas, bookmarks toggle highlights/annotations |
| C — Report pack | Monthly business review | Paginated Matrix with header/footer, export to PDF |

## Rules

- One message per visual; the annotation states it.
- Consistent scales across story steps.
- Avoid interaction surprises: lock slicers to the story's scope.

Typical features: `MX-NOTE-01`, `CV-ANN-01`, `CV-BMK-01`, `MX-PAGE-01`, `MX-EXP-01`.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- The highlight carries the thesis: one saturated series or item, with context
  in light grey (highlight pattern).
- Choose the commentary owner by where it attaches and who writes it: chart or
  KPI notes (`CH-NOTE-01`), Matrix notes (`MX-NOTE-01`), annotations
  (`CV-ANN-01`) or text (`CV-ELEM-01`). A standalone text box is not a
  data-bound note; do not design around unconfirmed note behaviour.
- Check every value fetched into a note against the claim around it (metric,
  scenario and scope).
