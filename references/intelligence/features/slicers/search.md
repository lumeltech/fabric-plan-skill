---
id: SF-FEAT-02
name: Search (wildcard, operators, autocomplete)
area: slicers
category: Features
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
---

# Search (wildcard, operators, autocomplete)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Search members with wildcards, measure operators, focused text filter, and autocomplete.

## When to use

- High-cardinality fields.

## UI path

Toolbar › Search.

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/visualState/toolbarSettings
Observed keys: enableSearch:true, searchDimension:"<Table>[<Column>]",
               caseSensitiveSearch:false, clearSearchAfterSelect:true
```

Copy the full saved Fabric Plan toolbar/filter-state groups and remap
`searchDimension` to a registry field (for a hierarchy filter, the leaf level).
A visible search box does not isolate wildcard, operator or autocomplete
behavior. A pop-up launcher (SF-FEAT-05) collapses to this search box.

## Constraints

- Inline text entry with Enter/apply wording or an OR indicator is a distinct
  mode from toolbar search. Capture its matching/token semantics before
  reusing toolbar settings; OR does not prove wildcard, bulk paste or
  executed filtering.
- For person names and other sensitive fields, respect authorized visibility in
  suggestions/counts/results, distinguish duplicates by stable keys and test
  with synthetic identities, including no-match and clear states.
- Explanatory wildcard/operator captions do not prove an executed query.
  Validate literal escaping, case, AND/OR, scaled numeric operands and
  Enter/apply timing.
- Define whether search only narrows the available list or selects members
  and filters data. Captions do not establish autocomplete or regex syntax.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Toolbar search is off on most saved owners; `enableSearch: true` appeared on
  few inspected controls [saved]. Do not assume search is on by default.
- `measureSearch: true` (also a registration configuration key) and
  `unifiedSearch: false` were saved on every owner in one inspected set,
  including owners with toolbar search off [saved]. `measureSearch` alone does
  not enable search.
- In a user-corrected control, `searchDimension` named the same field as the
  owner binding [saved].
- Facet-level category search and copy switches stayed off on every inspected
  owner, including those with toolbar search or paste on [saved]; copy the
  whole toolbar, facet and registration context.

## Related features

- `SF-FEAT-03`
- `SF-FACET-03`
