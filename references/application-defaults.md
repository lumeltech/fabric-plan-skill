# Application authoring defaults

The business navigation contract exposes Home,
Intelligence dashboards with embedded Planning workbenches, and PowerTables.
Underlying Planning sheets are hidden. Initial InfoBridge refresh is optional;
validate wiring and report untested materialization separately.

Arial, enabled native Home, Intelligence coverage for every Planning sheet,
and a visible native Page Navigator on every Intelligence dashboard are
**this skill's authoring baseline, not a Fabric requirement**. Fabric accepts a
Plan without them. Screenshots, reference JSON, a two-sheet request, omitted
feature mentions and skipped runtime validation do not release it either: every
flow this package runs applies it. Keep source-role colors and rich headers as
well.

Use Arial for all authored text, including effective Matrix per-measure/header
overrides, rich-text CSS, serialized chart text, slicers and native Home text.
Do not carry a different reference font into a newly authored flow.

These are the defaults this package writes into every new Fabric Plan
application, so a prompt that never mentions them still gets them:

1. Consistent measure role colors: amber Input/Forecast, purple Formula, blue
   Power BI, teal linked data. Resolve actual source types and preserve period,
   lock, conditional-format and edit-permission meaning.
2. A rich-text business description and matching legend for every Planning
   sheet. The generated [fields] list is not an acceptable header.
3. Intelligence dashboard coverage for every Planning owner: meaningful text
   header, real semantic-dimension slicers, relevant category/variance charts,
   and the embedded Planning grid below. Preserve standalone owner identity.
4. A visible native Home landing page with the application's purpose, clear
   instructions for starting the workflow, and available-sheet navigation cards.
5. A native Page Navigator on every Intelligence dashboard, including explicitly
   authored dashboards. Use complete render defaults and all visible normal
   pages, with reserved space above the grid. Buttons/bookmark tabs are different
   controls. Use `scripts/plan.py construct-native navigator` for them and `check-application-defaults` to verify coverage; no separate navigation guide is bundled here.

Do not silently omit any default or call an application complete if a required
phase failed. Native Home is not an ordinary sheet named Home and is not the same
thing as an Intelligence dashboard. Home content, role priority/audience and the
Plan's Home visibility switch are separate requirements.

## Contents

- [Defaults owned by other guides](#defaults-owned-by-other-guides)
- [Construct and deploy](#construct-and-deploy)
- [Validate according to the user's current instruction](#validate-according-to-the-users-current-instruction)

## Defaults owned by other guides

These also apply to every new application. Preserve intentional existing
overrides, locks, filters and source bindings.

- **Totals:** every new Planning grid uses explicit row grand total Top, row
  subtotal Top, column grand total Left and column subtotal off. Read the
  planning totals defaults guide. Measure-based roll-forwards use Measures in
  Rows with the native Measure Model; discover ROLL-FORWARD and read the roll
  forward authoring guide with the complete supplied formula reference.
- **Inputs:** new editable inputs default to ReadAndEdit. Business-dependent
  locking uses BasedOnFormula with a real, resolved expression. Read the input
  editability guide.
- **Measure cards:** assigned measure cards stay visible at **All**, with no
  selected values or ranges. Numeric Planning measures use per-measure Auto
  (`13: "auto"`). Apply dimension selections only to the dimension card itself.
  Read the measure display defaults guide.
- **Numeric columns:** Planning, KPI cards and charts aggregate a semantic Column
  in Values with source Sum when no aggregation is supplied. Planning
  `sourceAggregation` is independent of grid total settings, and saved measure
  IDs are preserved. Read the numeric column values guide.
- **Baseline comparisons:** bar and column charts compared against a baseline use
  native integrated variance; ordinary single-series bars are unchanged. Read the
  integrated variance guide for selectors and source-preserving commands.
- **Navigator padding:** new dashboard Navigators carry complete DEFAULT icon,
  text and shape padding even when icons are disabled. Partial state overrides
  remain distinct. Corner radius always uses the stored keys radiusTopLeft,
  radiusTopRight, radiusBottomLeft and radiusBottomRight.

## Construct and deploy

Import supported inputs, formulas, Forecast and conditional formatting together
through the documented phases. There is no reference-only staging shortcut or
automatic reduced-scope deployment; the original request and import-contract
checks stay authoritative.

`scripts/plan.py build` / `build_application` produce these requirements with hidden
underlying Planning owners and dashboard access. The result
includes `home.json`, `homeSpec.json`, and `defaultsCheck.json` in addition to the
existing definition, dashboard and identity files. The generated Plan properties
include `homeLayout.show: true`, so the public create request sets Home
visibility. Role-specific Home content, layout and priority are prepared locally
only, because no public route publishes them. `provision` records that phase as
unsupported and never reports it as delivered.

`home_defaults` preserves existing authored Home blocks, fills missing description
and preview-card content, and requires show=true. New baseline content uses the
__everyone__ layout without changing security or granting access. Preserve
other role layouts, their ordering and audience rules. For an existing application,
start from a fresh export and reuse existing populated content; fill gaps
without replacing unrelated content.

Use flexible Home text widths and content-sized rows; numeric widths are pixels,
not percentages. Read the Home layout fit guide, whose contract the runtime guide also summarizes. Do not create
fake images, temporary asset URLs or external links as substitutes for navigation.

```text
python scripts/plan.py check-application-defaults --input decoded.json --home home.json --out defaults-check.json
```

This command checks Arial plus all five requirements in the supplied definition/content.
It rejects non-Arial effective formatting overrides, not just the global font.
It also rejects absent or hidden Page Navigators, wrong native kinds, orphan
parts, restricted/empty targets and incomplete render defaults. The public create
definition carries the full authored Navigator state alongside its position.
`check-application-presentation` retains its narrower dashboard-coverage meaning.
Low-level `construct.build` is a component assembler; it is not the completion
path for an application. Its evidence explicitly sets `applicationComplete:false`.
Use the normal builder or compose every required phase.

`runtime.application_defaults.require_delivery_phases(authored, home_visible=...,
dashboard_geometry=..., dashboard_visibility=...)` is the completion gate. Pass
the aligned dashboard GUIDs and the dashboard GUIDs declared visible in the
successful public create; Home uses the visibility declared at creation.
Pass real receipts, never optimistic placeholders. The gate reruns the authored
baseline, rejects any missing required phase and reports role-specific Home as
not published. `provision` calls it, including for cached builds. A custom
composed workflow must use the same gate before writing a completed receipt or
claiming full delivery.

The baseline has no switch: `build` and `provision` apply it before any write,
hiding Home raises, and `check-application-defaults` refuses a Plan that skips a
phase. Declining it today means the run stops rather than passing with a note.
Keep construction/save status separate from runtime validation. A
scoped repair does not authorize unrelated report changes; report any unmet
application baseline instead of describing the whole flow as complete.

## Validate according to the user's current instruction

Construction guards always apply. When validation is requested:
- Run the relevant offline regressions for defaults, source identity and formatting.
- Export the saved definition and check `planProperties.properties.homeLayout.show`.
  Role-specific Home content has no public readback; report it as not published.
- Check rich descriptions, source-role colors, dashboard component coverage,
  page-local embed geometry, and exact PowerBI/Visual/InfoBridge field identities.
- Check rendering/navigation in an authorized browser when available. Never work
  around a browser access policy. API/static success cannot certify rendered fit,
  formula results, edit behavior or slicer propagation; report that boundary.

When the user explicitly skips validation, preserve that preference: save the
authorized changes and report receipts without runtime/UI/post-save validation.
An earlier skip does not override a later explicit request to validate.
