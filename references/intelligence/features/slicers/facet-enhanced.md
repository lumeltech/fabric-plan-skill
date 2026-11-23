---
id: SF-FACET-03
name: Facet enhancements (image, text area AND/OR, edit data, hierarchy)
area: slicers
category: Category filters
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
---

# Facet enhancements (image, text area AND/OR, edit data, hierarchy)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Image filter, AND/OR text area, edit data, date in list view, hierarchical data.

## When to use

- Visual product pickers; pasted criteria.

## UI path

Facet › Enhanced.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.facetSettings, displaySettings.enableImageData (capture sample)
Text area: facetSettings.facetViewType = "textArea" (UI save on a name field, with a
  floating toolbar); tokenization and AND/OR settings are not isolated.
Hierarchical data: facet mode off with per-level assignments (SF-HIER-01).
Presentation evidence: screenshots show named text-entry fields, an OR indicator
  and an apply prompt.
```

Only the text-area view value and the hierarchy structure are observed. Run
`core/native-samples.md` before writing image filters, data editing or text-area
operators.

## Constraints

- Text-entry screenshots show presentation only, not image filtering, data
  editing or every enhancement. Confirm entry parsing, OR/AND semantics,
  apply/clear and unmatched values.
- Do not assume the standard toolbar search configuration activates
  text-entry mode; capture the required mode before reuse.
- For image tiles, capture member/image binding and fallback labels. A token
  entry with an OR label does not demonstrate an AND mode or data editing.
- Image filtering does not authorize external data ingestion or model writes.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Saved enabled facets use `"textArea"` beside list, radio and other views;
  text-area selection state is stored apart from toolbar bulk-paste state
  [saved]. Preserve both when cloning or switching views.

## Related features

- `SF-FACET-01`
