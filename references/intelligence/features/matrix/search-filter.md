---
id: MX-SRT-02
name: Search and filter in the Matrix
area: matrix
category: Sort, filter, Top N
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
---

# Search and filter in the Matrix

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Search rows; nested and grouped filters; column-level filters. Search matches
text or numbers as you type and steps through the results. Filters take nested
AND/OR conditions on row or column hierarchies or measures, with Advanced
filter groups, Disable all, Persist filters and Reset all. Column-level filters
offer conditions suited to the column's data type.

## When to use

- Long lists without a slicer.
- Threshold conditions on a measure (greater than, less than).
- Combined AND/OR conditions across hierarchy levels and measures.

## UI path

Matrix toolbar: Home › Analyze › Search, or Filter › Add Filter (Advanced › Add
group). Column-level: Column gripper › filter icon › condition › Add rule.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Search covers all pages when the Matrix uses multiple pages or page breaks.
- Filters also detect inserted calculated and template rows.
- Persist filters keeps filters when switching between pages; Disable all
  turns them off temporarily; Reset all clears them.
- Column-level conditions adapt to the column's data type, including text in a
  measure column; Clear filter removes all column-level filters at once.

## Related features

- `SF-FACET-01`
