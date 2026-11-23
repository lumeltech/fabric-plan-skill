---
id: AREA-CAT-00
name: Feature name
area: matrix | slicers | charts | kpi | table | canvas
category: Category name shown in the master list
status: IS-Confirmed | Inforiver-only | IS-native
encoding: verified | observed | unverified
visual: Matrix | Super Filter | Chart | KPI card | Table | Canvas | Sheet
sources:
  - https://docs.fabricplan.com/...
---

# Feature name

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. Copy this file to add a new feature, then run `python -I scripts/build_index.py`. -->

## What it does

One or two sentences in plain language.

Describe the Intelligence Sheet surface only. Source-module behavior belongs
to its owning namespace. Product availability does not override the current
semantic-model-only release gate; record cross-module integration dependencies.

List relevant Fabric Plan documentation and official Microsoft contract/schema
URLs in `sources`; a reviewed upstream documentation link may supplement them
with its evidence limits stated. Never list report, native-sample or capture
paths. Remove superseded Inforiver references. See
[confirmed availability and exceptions](../core/native-samples.md).
Do not change encoding confidence solely because availability or sources change.

## When to use

- Report situation where this feature helps.
- Model signal that suggests it (see `core/model-inspection.md`).

## UI path

Where an author turns it on in the Intelligence Sheet (toolbar tab › button, or
format pane › section). A new visual starts in the Visualizations pane: its
tile, and for charts Charts 100+ › category (or Search Charts). Never write
Insert › Chart.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.<group>
Keys: <keys>
Evidence: <live capture summary, or "none"; details in the ledger>
```

If `encoding` is not `verified`, follow `core/native-samples.md` before writing it.
Screenshots are feature references only: describe observed presentation
generically, without report names, timestamps, sample values or attachment
paths. Screenshots establish presentation only. Record generic part paths and
JSON pointers for stored keys (no sample-file paths, IDs or model field names),
identify JSON-string groups explicitly, and retain actual serialized enums.

## Constraints

- Limits, interactions with other features, known issues.

## Related features

- `OTHER-ID` — why it is related.
