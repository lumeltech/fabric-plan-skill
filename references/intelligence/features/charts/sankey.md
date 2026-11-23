---
id: CH-LIB-25
name: Sankey charts
area: charts
category: Chart library
status: IS-Confirmed
encoding: unverified
visual: Chart
sources:
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/visualization-library/sankey-chart
  - https://docs.fabricplan.com/intelligence-sheets/how-tos/visualization-library
---

# Sankey charts

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Weighted flows between stages.

## When to use

- Flows, allocations.

## UI path

Visualizations pane › Charts 100+ › Special Charts › Horizontal Sankey or
Vertical Sankey.
First-party docs assign stage dimensions to Category and the link measure
to Actual(s). Capture the resulting native bindings and node/link settings.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.chartType (capture value) + visualState
Presentation evidence: screenshots only.
Visible: multi-stage weighted flows; a caption limits the last stage to Top N.
Native family, node/link assignments, Top N and styling: not captured.
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- A flow layout does not establish an allocation or native JSON schema.
  Capture stable node IDs, stage roles, effective assignment dates and the
  link measure/population; keep upstream node labels readable.
- Aggregate links without duplicating source records or assignment rows; do
  not assume aggregate totals equal event-log counts.
- Flows between categorical attributes are a joint distribution, not temporal
  progression or causality. Resolve entity grain, missing categories and
  duplicate associations before checking conservation.
- Intelligence chart library only; never a Power BI native visual.
- Define Top N scope, tie handling and omitted/Other members. Reconcile flows
  to the retained population rather than comparing a filtered Sankey to
  unfiltered totals.
- Use authorized aggregates, protect small cohorts and respect staff/account
  detail permissions.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Pointer: /properties/chartType = "SANKEY_HORIZONTAL" | "SANKEY_VERTICAL"
         (matches the decoded template id)
Pointer: /properties/visualState/hiddenProperties_!!!_template (JSON string)
Decoded keys: rendererType:"sankeyChart"; chartOrientation:"horizontal" | "vertical"
Pointer: /properties/pivotAssignments (three to eight ordered axis stages; one AC)
Pointer: /properties/visualState/hiddenProperties_!!!_appearance; decoded path
         charts.sankey: filterNegativeValues; hideBlankValues; hover;
         node{width, nodeSpacing}; flow{colorType:"gradient", opacity}; node
         opacity; active and inactive flow opacity; categorical node alignment
Partial: {"hideBlankValues":true,"filterNegativeValues":false,
          "node":{"width":10,"nodeSpacing":12},"flow":{"colorType":"gradient","opacity":25}}
Evidence: [saved] companion-library saved owners; not isolated or re-rendered.
```

- Saved stage counts are not a tested limit; retain every stage field in its
  saved order [saved].
- `hideBlankValues` was true in every inspected owner, while
  `filterNegativeValues`, node width and spacing, and flow opacities varied;
  these are internal chart settings, not dashboard spacing or palette rules
  [saved].
- `filterNegativeValues: false` does not prove negative flows render or that
  flows conserve [open].
- Orientation switching, long-stage layout, blank handling, negative-flow
  behavior and hover effects are unresolved [open].
- Never transfer network-graph layout keys into Sankey state.

## Related features

- `CH-AX-01`
- `CH-LBL-01`
