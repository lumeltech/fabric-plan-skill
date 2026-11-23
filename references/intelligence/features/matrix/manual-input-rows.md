---
id: MX-INROW-01
name: Manual input rows
area: matrix
category: Calculations
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/build-financial-reports
---

# Manual input rows

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Inserts rows whose values are typed in the visual. Row options: title, scaling
factor (Auto by default), Include in total and Bind for cross filter/RLS.
Bulk insert adds several child rows or a new parent level; a row hierarchy
adds one custom level for typed, calculated or aggregated rows. Manage Rows
edits, deletes or hides inserted rows; Insert Row Settings can lock a level
against new categories, enforce distinct values or allow blank categories.

## When to use

- Adjustments or memo lines not in the model.
- Placeholder lines or a custom grouping level needed only for presentation.

## UI path

Select the anchor row > Data ribbon > Insert Row > Data Input > Number
(first-party guide); name the row and enter values. Change its scaling in the
Matrix ribbon; for a hierarchy insert a parent row and indent children with
Format ribbon > Increase Indent (first-party guide). The row gripper's Insert
section offers Insert Rows for bulk child rows or a new parent level; rules
sit in Manage Rows > Insert Row Settings.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Governed planning input belongs to the Planning module; integration is pending.
- Typed values stay in the report and do not change the bound semantic model;
  persisted inputs and writeback belong to other modules and are not enabled
  in this release.
- Include in total rolls typed values into parent and grand totals; keep it
  off for memo lines and label any adjustment that is included.
- Without Bind for cross filter/RLS, inserted rows ignore cross-filtering and
  row-level security; bind them to a reference row or dimension member.
- Blank row categories are rejected unless Allow Blank Values is on; a level
  locked in Insert Row Configuration accepts no new categories.
- Hiding an inserted row is temporary and deleting it is permanent; keep the
  inserted-row indicator visible so typed lines stay distinct from model rows.

## Related features

- `MX-INCOL-01`
