---
id: SF-QUICK-01
name: Quick mode setup
area: slicers
category: Setup
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/create-a-filter-panel
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/filter-data/add-date-filters
---

# Quick mode setup

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Fast configuration of filter type and options: Quick Mode lists only the
filter types applicable to the bound data and switches the Super Filter to the
chosen type with essential options. Types include date slider, period, date
range, relative date, calendar heatmap, preset bar, filter panel (checkbox,
radio, dropdown, tile, toggle, list, text area), hierarchy, tree map, measure,
mass filter, play axis, text slicer, pop-up, variance and a dark theme.

## When to use

- Any new slicer.
- Switching filter types quickly while building a sheet.
- Trying alternative layouts for the same field, such as a dropdown versus a
  tile panel or a date slider versus a preset bar.

## UI path

Add Super Filter and bind Category fields; Filter ribbon › Quick Mode.
First-party docs identify Facet, Date Picker and Relative Date entry points.
The Quick Mode (+) icon at the filter's bottom-left also lists the applicable
types; select one to switch. A Show Quick Mode setting controls the icon.

## Definition encoding

```text
Quick Mode is an authoring aid; what persists is the chosen filter type:
  Facet: configuration.visualType "FACET", facetSettings.enableFacetMode:true,
         facetSettings.facetViewType ("tile" | "toggle" | "checkbox" | "dropdown" | "textArea")
  Hierarchy: configuration.visualType stays "FACET"; facetSettings.enableFacetMode:false;
         hierarchySettings.hierarchyTreeViewType / enableDropdown (SF-HIER-01)
  Date picker / slider: configuration.visualType "DATE" + dateSettings (SF-DATE-*)
  Numeric: configuration.visualType "NUMERIC" (SF-NUM-01)
Evidence: UI-saved filters of each kind in native Plan exports; no before/after
  capture of the Quick Mode action itself.
```

Other Quick Mode types (tree map, measure, mass filter, play axis, text slicer,
variance) remain uncaptured. Run `core/native-samples.md` before writing them.

## Constraints

- UI entry points come from first-party docs, not inspected properties;
  screenshots do not show the authoring ribbon. The resulting filter types are
  observed in saved definitions (above); the Quick Mode action itself was not
  captured.
- Use a date field rather than Date Hierarchy for documented date-picker/
  relative-date setup, and multiple Category dimensions for a facet panel.
- Quick Mode is an authoring aid; its icon is not available to readers in
  read mode, even when Show Quick Mode is on.
- Quick Mode sets essential options only; refine advanced settings in the
  full filter configuration afterwards.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Every variant is one `SUPER_FILTER`/60 owner; facet, date, hierarchy/map,
  measure, play-axis, preset, rank, variance and CF settings are object-valued
  `visualState` branches that can coexist on one owner, not separate families
  [saved]. Extra groups seen: `varianceSettings`, `cfSettings` (SF-FEAT-06) [saved].
- A Super Filter owner's `chartType` is incidental; classify the family from the
  root registration and the owner `visualType` [saved].

```text
Active-type signature (classify from all parts, not one flag):
  Date:      category field dataType "DateTime" + registration visualType "DATE" +
             dateSettings.enableDateRange:true; dateViewType "dateSlider" | "dateCalendar"
  Facet:     facetSettings.enableFacetMode:true + facetViewType
  Hierarchy: registration visualType "FACET" + enableFacetMode:false +
             hierarchySettings.hierarchyViewType "tree" | "list" | "map"
  Buckets:   grouping fields lowercase "category"; numeric measures lowercase "measure"
Evidence: complete saved owners in several inspected exports [saved]
```

- Flags alone mislead: owners saved `enableDateRange: true` with String fields
  and FACET/NUMERIC registrations [saved]. Do not count them as date controls or
  clear their date settings automatically.
- Keep absent branches, `false`, empty strings and numbers distinct when
  comparing donors; some owners omit `rankSettings` entirely [saved].
- Each registration `bucketId` must match a bucket in the owner's
  `pivotAssignments`; an orphaned `bucketId` is unlikely to render [open].
- Registration pivots can repeat category context beside a measure, so their
  count is not the owner field count [saved]. Some owners also keep
  registrations without a top-level `bucketId` whose pivots use capitalized
  `Category` [saved]. They resemble the extra-filter shape (CV-FILT-01), but
  their purpose on a control is unconfirmed, so preserve them [open].
- New part envelope: keep the `$schema`, `eventTriggers` and `properties`
  wrapper of a same-sheet visual and replace only `properties`; a part sent as
  `{"properties": …}` alone passed local checks but read back as an empty
  visual shell [saved]. Whether it caused the import timeout is unknown [open].
- An exported `SUPER_FILTER` reference can lack its properties part; treat its
  settings as unknown [saved]. One root `ANALYTICS_PLUS` reference resolved to an
  owner with `visualType` 60 and `chartType: "CARD"`; keep such mismatches
  separate [open].
- When a control showed its field but its Visual level filter card stayed
  blank, removing and re-adding the field in the native UI restored the card
  [confirmed]. No single guessed flag is known to fix it [open]. Place each
  field only in its owner list; never set `isDaxMeasure` just to make it appear.
- Choose the owner by the needed experience: per-visual registrations sit
  behind each visual's own filter (CV-FILT-01), a page-level entry scopes the
  sheet without a canvas control, and a standalone Super Filter is the visible
  control [saved]. Keep a visible selector, its selection, inherited page scope
  and consumer context coherent.
- Validation pass: select each control and check its field and filter card;
  change one selection and confirm grids, KPIs and charts all take the scope;
  inspect query state when a visual ignores it; check the saved readback, not
  the editor, and the default after reopening; test RLS separately with a
  restricted identity.
- A fresh re-export of an unchanged control gallery differed from the previous
  export only in two owners' `visualState.slicerFilterAssignments` [saved]. Treat
  such selection-state differences as noise unless the selection is under test;
  they are not evidence of a changed control type, a user action or runtime
  behavior.

## Related features

- `SF-FACET-01`
