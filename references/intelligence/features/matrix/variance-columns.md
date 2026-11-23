---
id: MX-VAR-01
name: Variance columns
area: matrix
category: Variance
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
  - https://docs.fabricplan.com/planning-sheets/reference/formula-syntax
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-a-dashboard
---

# Variance columns

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Adds absolute and % variance between two measures (AC vs PL/PY/FC), integrated in the Matrix.

## When to use

- Any actual-vs-plan or year-over-year table.

## UI path

Insert › Variance.

## Definition encoding

```text
Presentation evidence: screenshots; UI-saved native variance columns below.
Native variance: bind the comparison to plmeasure (PL) or pymeasure (PY) beside one
  ameasure actual; the engine adds an absolute and a relative variance column to
  manage_measures (e.g. "Net Sales - PY Net Sales"/"YoY", "YoY%").
Engine ids come as a set: PL saves used AC 2055735705734354016, PL 9837477649726619647,
  Var 8238374486369709813, Var% 6390941348790046018; a PY save used AC 5897060598503614240,
  PY 9188474335526959778, YoY 5194609792639898746, YoY% 2237550015955116046.
Labels: manage_measures[].label and columnTitleConfigs {id, levelId:"measuresTitle", value};
  hide a variance column with manage_measures[].visible:false (UI-saved).
Extra ameasure fields show as plain columns without their own variance. Their header
  comes from the pivot assignment: customName + isRenamed:true (customSource:true), as on
  the native plmeasure "Budget"; a manage_measures label alone left the full measure name.
```

Keep a donor's AC/comparison/variance ids together: replacing only the AC and
PL ids removed the variance columns [confirmed]. Ids for extra plain measures
can be new. Resolve existing model variance measures first; do not invent a
`visualState.variance` group or infer formulas from headers.

## Constraints

- Name both compared measures in the brief and bind each delta to its own
  baseline; attainment, relative variance and completion rates are different
  measures.
- Recompute total variances and percentages from the underlying total
  measures, respecting distinct-count non-additivity, and define zero/missing
  baseline behavior. Scaled displayed values may not subtract exactly.
- Determine polarity from the full row meaning (for example feedback
  statements), not from the delta sign.
- Use [Matrix formula syntax](formula-syntax.md) for custom absolute/relative
  variance calculations, including explicit denominator fallback and
  favorability. This does not verify an inserted variance-column encoding.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Saved INFORIVER/10 owners bind compared values to the native scenario
  buckets `ameasure`, `plmeasure` and `pymeasure`, beside `rows`, `columns`
  and an optional `annotation` bucket [saved].
- Slot names do not establish business meaning: a saved Matrix holds a
  plan-scenario (PL-role) measure in `pymeasure` [saved]. Never relabel a PY
  slot as prior year or infer a year-over-year variance from the bucket
  name; confirm date scope and comparison meaning from the measure
  definition.
- Native variance columns [saved]: with an actual in `ameasure` and a
  comparison measure in `pymeasure`, the engine added variance entries to
  `visualState.manage_measures[]` (an absolute column labelled
  `<AC> - <PY>` and a relative `YoY%`, renameable, for example `YoY`), each
  with `visible`. Users hid the absolute column with `visible: false` to save
  width while keeping the relative % [saved]. Entry ids are engine-assigned;
  never hand-write them.
- The same assignment added default conditional-format rules to
  `cfProps.rules` and `jet_cfProps.rules`: relative-variance rules (red
  `#FF4400` below zero, green `#008000` above) enabled on the relative
  column and generic absolute/relative rules disabled [saved]. Check
  polarity for lower-is-better measures before accepting them.

## Related features

- `MX-FML-01`
- `MX-CHART-01`
- `MX-NUM-03`
- `MX-TPL-04`
