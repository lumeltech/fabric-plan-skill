## Contents

- [Required marker](#required-marker)
- [Minimal brief](#minimal-brief)
- [Full template](#full-template)
- [Layout contract rules](#layout-contract-rules)
- [Region to geometry conversion](#region-to-geometry-conversion)
- [Validation checklist](#validation-checklist)
- [Additional details](#additional-details)

<!-- Design topic for the `fabric-plan-skill` skill. Structure adapted from microsoft/skills-for-fabric powerbi-report-cli design-brief (MIT). -->

# Design Brief contract

The `Design Brief:` YAML is the only hand-off from `design`/`discovery` to
`authoring`, which implements it literally and builds nothing beyond it.

Load [session design](session-theme.md) first; full briefs carry its resolved
`session_theme` snapshot. The template below is illustrative, not a universal
design. `archetype` may be `Custom` and `layout_variant` a user-defined name;
both describe the chosen layout and do not prescribe it from report type.
Record design provenance and user/session preference in the rationale.
When using the [report inspiration library](report-inspiration.md), include the
chosen family, composition, navigation and departures in
`session_theme.inspiration`. Resolve exact tokens and page-role layouts; a
reference name alone is not a complete design. Include the approved logo
asset/variant and placement, or its pending/omitted status, in
`session_theme.branding`. These are brief metadata, not Plan JSON properties.

## Required marker

```yaml
Design Brief:
  generated_by: fabric-plan-intelligence
  contract_version: 1
```

## Minimal brief

For a single, focused change (brownfield):

```yaml
Design Brief:
  generated_by: fabric-plan-intelligence
  contract_version: 1
  mode: brownfield
  design_identity: unchanged
  decision: "Add a searchable Customer dropdown slicer to the filters band of 'Sales Overview'"
```

## Full template

```yaml
Design Brief:
  generated_by: fabric-plan-intelligence
  contract_version: 1
  mode: greenfield | brownfield
  session_theme: <complete resolved profile from session-theme.md>
  design_system: design/design-system.md   # or the path of the user's design MD file
  design_identity:
    tone: <tone>
    signature: <signature move>
    ibcs: false            # true only when the user asked for IBCS or picked the IBCS template
    ibcs_theme: null       # strict | flexible, only when ibcs: true
  color_map:
    strategy: measure_match | gradient
    measures:
      "Measure[Revenue]": "#4F46E5"
      "Measure[Revenue Budget]": "#64748B"
  navigation_model: sheet_tabs | buttons | bookmarks | none
  sync_slicers: [ { field: "[Dim] Date[Month]", sheets: [all] } ]
  sheets:
    - name: Sales overview
      role: landing | detail | drill | planning-front-door
      archetype: <chosen example or Custom>
      layout_variant: <chosen example or custom layout name>
      variant_rationale: <user/session choice and analytical suitability>
      canvas_background: "#FAFAFA"
      super_filter_layout:
        position: <top_band | left_rail | right_rail | inline | popup | custom | none>
        region_ids: [filters] # Match actual placement regions; [] only when none.
        rationale: <user/session choice, filter count and available space>
        overflow_behavior: <wrapping, internal scrolling or captured popup behavior>
      layout_contract:
        canvas: { type: keep-existing, width: 1920, height: 1080, units: normalized, margin_px: 32, gutter_px: 16 }
        grid:
          columns: 12
          rows: 12
          regions:
            header:   [1, 1, 8, 2]
            filters:  [8, 1, 13, 2]
            kpis:     [1, 2, 13, 4]
            main:     [1, 4, 9, 13]
            side:     [9, 4, 13, 13]
        placements:
          - id: sheet_title
            region: header
            kind: element:text
            text: "Sales overview — are we on plan?"
          - id: slicer_period
            region: filters
            slot: 1
            of: 3
            kind: slicer:date-month-range
            field_bindings: { category: ["[Dim] Date[Month]"] }
            features: [SF-DATE-02]
          - id: kpi_revenue
            region: kpis
            slot: 1
            of: 4
            kind: kpi
            purpose: "Revenue vs budget"
            field_bindings: { values: ["Measure[Revenue]"], comparison: ["Measure[Revenue Budget]"] }
            features: [KPI-CARD-01]
          - id: mx_region
            region: main
            kind: matrix
            purpose: "Which regions drive the variance?"
            field_bindings:
              rows: ["[Dim] Geography[Region]", "[Dim] Geography[Country]"]
              columns: ["[Dim] Date[Quarter]"]
              values: ["Measure[Revenue]", "Measure[Revenue Budget]"]
            features: [MX-LAY-01, MX-VAR-01, MX-CF-02]
            sort_policy: "Revenue desc"
        space_audit:
          content_cell_count: 120
          placed_cell_count: 120
          empty_cell_pct: 0
          unplaced_regions: []
          largest_region: { name: main, pct_of_content: 60 }
          balance_rationale: "Matrix answers the main question; side holds trend"
  interaction_pattern: cross_filter
  accessibility: { contrast: WCAG_AA, color_independent_cues: true, titles_plain_language: true }
```

## Layout contract rules

- Regions are `[c1, r1, c2, r2]` on a 12 × 12 grid, end-exclusive.
- Regions in one sheet do not overlap; every placement names a region.
- `slot`/`of` splits a region horizontally into equal, gutter-separated parts.
- Every sheet requires a title element.
- Unless the user explicitly opts out, Help and Info controls must appear in
  placements, not just descriptive theme notes, with action/target/content and
  close/back behavior.
- Use the session's regions, slots and shared component positions per page
  role. A focused brownfield brief inherits the existing approved snapshot
  without resetting or silently replacing the session design.
- Record `super_filter_layout` per sheet as brief metadata, not Fabric Plan
  JSON properties: position, named regions, rationale and overflow behavior,
  or `none` with a reason.
- Place each Super Filter in its chosen region/slot with explicit geometry;
  region names need not be `filters`. Top/bottom bands, either side, inline
  groups, popups and custom arrangements are choices, not report-type rules.
  Record custom arrangements precisely.
- Specify filter scope/sync, clear/reset access and selected-value visibility.
  Reserve space for labels, chips, search, lists and dropdown expansion; avoid
  clipping or covering permanent content. For popup/collapsible designs,
  record the user's approval of pop-up mode, then the trigger, expanded
  placement, close behavior and native capture needs.
- For compound filters, record which Category fields share a Super Filter
  panel, per-category styles and cascade dependencies separately from visual
  interaction/sync. Allocate space for hierarchy counts, values/variance,
  images or calendar cells as needed; see the
  [slicer feature files](../features/slicers/_index.md).
- Embedded Planning grids get the largest region and the same sheet's slicers.
- `space_audit.empty_cell_pct` above 15 needs a written reason.

## Region to geometry conversion

`width`/`height` are the 1920 × 1080 reference grid from `design-system.md`;
stored values are fractions, so the plan's own `canvasStyle.dimension` type
can stay unchanged (`keep-existing`).

Authoring converts each placement to normalized geometry:

```text
usable_w = 1 - 2*margin_x          margin_x = margin_px / canvas.width
usable_h = 1 - 2*margin_y          margin_y = margin_px / canvas.height
col_w    = usable_w / 12           row_h    = usable_h / 12
x        = margin_x + (c1-1)*col_w + gutter_x/2
y        = margin_y + (r1-1)*row_h + gutter_y/2
width    = (c2-c1)*col_w - gutter_x
height   = (r2-r1)*row_h - gutter_y
```

with `gutter_x = gutter_px / canvas.width`, `gutter_y = gutter_px / canvas.height`.
Round to 4 decimals. Write the same values wherever the native schema stores
placement (owner `position/dimension` and, for embedded visuals,
`reactiveVisualProperties`).

## Validation checklist

- [ ] Marker, `contract_version`, `design_identity` present; `ibcs` explicit
- [ ] Full `session_theme` snapshot matches current profile ID/revision and tokens
- [ ] Inspiration choices/departures recorded when used; branding asset/variant
      approved or explicitly pending/omitted, with geometry and contrast addressed
- [ ] Page-role layouts match session templates; exceptions explicitly approved
- [ ] Theme/layout user/session-selected, not assigned by report type or screenshot
- [ ] Help and Info controls have placements, native actions and content, or opt-out
- [ ] Every sheet: archetype, variant, rationale, layout contract, title
- [ ] Regions non-overlapping; placements reference defined regions
- [ ] Every data visual has `purpose`, `field_bindings`, `features`
- [ ] Every field resolves in `_brief/field-registry.md`
- [ ] Every feature ID exists in the reference index
- [ ] Slicer types fit field cardinality
- [ ] Super Filter position/regions and overflow behavior recorded; each filter placed
- [ ] Open/closed states, selected values and clear/reset controls usable; scope/sync explicit
- [ ] `space_audit` filled; empty space justified
- [ ] Colour map covers every measure shown in multiple visuals

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Optional companion fields

Optional brief metadata mapped from the companion contract. None is required,
none changes the required marker or fields above, and none is Plan JSON. Add
keys to the existing mappings; do not replace them.

```yaml
Design Brief:
  design_identity:              # extra keys in the existing mapping
    family_id: F-01             # optional profile from design-families.md
    appearance: light           # light | dark | mixed
    density: medium             # low | medium | high
    decoration: restrained      # minimal | restrained | expressive
    selection_reason: <audience, decision, environment and fit>
    preference_evidence: <explicit preference | saved design | recommendation>
    verification: <saved-state, rendered and interaction checks, stated separately>
  storyline: [<where do we stand?>, <why?>, <where exactly?>, <what next?>]
  playbooks: [F2]               # optional starting points from domain-playbooks.md
  preserve: [<brand colours, existing presets, approved deviations>]
  interaction_detail: { drill_targets: [<hidden drill sheets>], slicer_scope: <which visuals each slicer filters> }
  model_gaps: [ { need: <need>, reason: <why> } ]
  library_gaps: [ { need: <need>, closest_used: <feature ID> } ]
  assumptions: [<item to verify>]
  sheets:
    - header_copy: <two or three sentences: what to select, what colours mean, how results update>
      reference_fidelity: none  # none | semantic | exact; only when the user asks to reproduce a reference
      layout_contract:
        placements:
          - id: <visual id>
            purpose: <a question>
            selection_rationale: <why this visual; rejected alternative>
            sort_policy: chronological     # chronological | value_desc | model_order, or free text
            color_strategy: measure_match  # measure_match | gradient | semantic | highlight | neutral
            polarity: higher_is_better     # higher_is_better | lower_is_better
            aggregation: ratio             # sum | ratio | average-leaf
            kpi_style: <a KPI style variant from design-system.md>
            px_rect: { x: 40, y: 120, w: 368, h: 120 } # only with an approved pixel grid
          - id: <frame id>
            kind: element:shape
            role: section_container  # section_container | filled_panel | divider | accent_bar | marker
            wraps: [<visual ids>]
  accessibility:                # extra keys in the existing mapping
    contrast_notes: <text on coloured panels, reversed text, legend colours>
    reading_order: <header, filters, KPIs, main, supporting>
```

- Every placement `id` is unique, and every chart and KPI card has a
  `purpose` phrased as a question.
- `px_rect` records an approved rectangle from the
  companion grid. It must lie inside its
  named region; authoring normalizes it by canvas width and height instead of
  applying the region formula above.
- A `section_container` frames the union of its `wraps` plus 8 px on each side
  (companion default), and each container and content pair is an intentional
  overlap.
- `header_copy` never contains IDs, API steps or generation notes.
- A `reference_fidelity` other than `none` follows
  reproducing a reference.
- When a separate approval document or page plan exists, it agrees with the
  brief on bindings, filters, theme, IDs and placements before authoring.

### Optional approval outline

Outside discovery (which uses the report-spec sections), a design-only request
can carry readable sections before the YAML: model summary; storyline and
sheet plan; per sheet, the pattern, filters and a placement table (element,
library visual, question, bindings, rectangle); theme and colour map; model
additions to consider; library gaps; assumptions and open questions; QA
result. Use real fields throughout and remove an element that cannot be bound
rather than leave a placeholder.
