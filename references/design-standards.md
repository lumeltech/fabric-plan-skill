> v20: All reports use content-sized rich-text headers plus a small buffer and
> native row/column hierarchy icons `gmate`, independent of business use case.
> Read [report-presentation-defaults.md](report-presentation-defaults.md) and
> discover REPORT-PRESENTATION. Preserve intentional user overrides.

> v19: Every new Planning grid uses explicit row GT Top, row subtotal Top,
> column GT Left, column subtotal null/OFF. Preserve intentional overrides.
> Read [planning-totals-defaults.md](planning-totals-defaults.md). Measure-based
> roll-forwards recommend Measures in Rows + native Measure Model; discover
> ROLL-FORWARD and read [roll-forward-authoring.md](roll-forward-authoring.md)
> plus the complete supplied [formula reference](roll-forward-formula-patterns.md).

> v18: [measure-display-defaults.md](measure-display-defaults.md) is the default: assigned measure cards stay visible at **All**, with no selected values/ranges. Numeric Planning measures use per-measure Auto (`13: "auto"`). Apply dimension selections only to the dimension card itself; preserve all source bindings and intentional existing filters.

> v14 required default: use native integrated variance for bar/column baseline comparisons. Read [integrated-variance.md](integrated-variance.md) for exact selectors, source-preserving commands and business examples. Ordinary single-series bars are unchanged.

> v13: Read [planning-column-presentation.md](planning-column-presentation.md) for dynamic column expansion, selected sizing/default-total rules and native-measure filter cards. Expansion recovery was user-confirmed; the other defaults were subsequently requested. Preserve all existing input and formula identities.

> 2026-11-14 active formatting and identity update: read [matrix-formatting.md](matrix-formatting.md) and [dimension-leaf-keys.md](dimension-leaf-keys.md). Use `plan.py format-matrix` for selected typed formatting and `plan.py leaf-key-mapping` for stable leaf storage defaults. These newer, revision-qualified contracts supersede conflicting older general examples; original source documents remain intact. Formatting is offline-tested, not render-certified. The complete existing native CF seed is not claimed to be an exact copy of the newer source constants.

> Standalone edition: read [runtime-guide.md](runtime-guide.md) for construction and deployment. Source checkout and historical task links below are optional provenance, not runtime prerequisites. Original feature explanations are preserved; the API-only runtime guide and gap inventory distinguish implemented APIs from blocked contracts. Historical UI steps are not execution instructions.

> Active Context/Intelligence construction addendum: read `references/context-intelligence.md`. External Context stays outside the grid and passes the selected scope into Planning; ordinary semantic slicers are separate. The executable constructor now covers Context, slicers, cards, text and page-local embedded geometry. Scenario rows and grid-only dashboards are not equivalent substitutes. Preserve feature-level omissions and separate saved-state checks from behavior verification.

# Fabric Plan Presentation and Layout Standards

## Scope and Authority

For Intelligence-specific design choices, use the
[design mode guide](intelligence/design.md), its
[design topic index](intelligence/index.md#design) and the
[visual feature master list](intelligence/feature-master-list.md). Apply those
details within the latest [skill contract](../SKILL.md), including mandatory
Arial, Home and Page Navigators; historical examples do not override these
application defaults or authorize model changes.

Shared presentation and validation baseline for Fabric Plan creation and updates. This is the design reference for the [internal authoring contract](feature-contracts.md) and applicable AI schema guides, not a Fabric schema, application template or permission to change product code, model/data/security, connections or live artifacts.

Derive the design from the current user's functional request, supplied semantic model and available data, verified platform/property contracts, and these shared standards. Do not inherit business pages, measures, flows, assumptions, identities or layouts from handoffs, demonstrations or unrelated history. No reference Plan is required for creation. Home, typography, classification and overview requirements below are explicit shared standards, not inherited business requirements.

User-supplied decoded Fabric Plan JSONs may illustrate how planning inputs, formulas, connected outputs and presentation containers work together. Study representative feature records, not every property or stored input row, and create an independent business design. Use the [business-to-feature composition guide](feature-contracts.md#business-to-feature-composition) to choose the experience before investigating implementation; reserve code inspection for a specific unresolved setting, compatibility conflict or failed validation.

For updates, inspect only the user's specified current artifact and relevant dependencies, preserve compliant presentation, unrelated configuration and saved-input identities, and apply supported changes. Its private baseline is update context, not a template for other applications. Metadata-only APIs cannot modify visual definitions or establish presentation compliance.

Use verified native properties, writer behavior and ALM serialization for each visual family and target revision. A design requirement is mandatory even when its implementation is unresolved: investigate the applicable writer, record a remaining gap as blocked or a proven non-configurable surface as such, retain supported work, and do not invent a formatting key or claim full compliance. Unknown is not product-unsupported. A declared AI schema field or permissive property bag is not proof that it applies, exports, imports or renders.

## Business-First Execution

When supplied with the feature contracts for a functional creation request, enter [Fabric Plan Business Authoring](runtime-guide.md). These standards guide the best request-specific native application; they are not a definition-only task, a preset financial design, or a reason to return only a blueprint.

Apply supported presentation during construction and inspect alternative native writers for missing settings. An unavailable AI formatting/compiler route is not proof that native Plan authoring is unavailable. Missing renderer access is a post-save verification limit, not a prerequisite for submitting an otherwise supported definition. Preserve the distinction between saving a supported application and claiming complete presentation acceptance.

Do not drop mandatory requirements silently or fabricate properties to satisfy them. Record exact remaining surfaces and continue independently supported business work using the [route-fallback procedure](feature-contracts.md#contract-gap-resolution-and-route-fallback). Full compliance still requires the settings and rendered checks below; a presentation gap must not be misreported as a blanket product limitation.

## Mandatory Standards

### Home and Sheet Introductions

- Every artifact has a polished Home/landing experience with a request-specific business title, description and navigation to its actual sheets. Use verified Home writers/contracts, not another artifact's layout. Do not invent a sheet enum, Home part or permission rules.
- For every new Plan, include one application-specific AI-generated Home illustration unless the user opts out or supplies a preferred image. Follow [Application Illustration: Generate, Upload, Place and Verify](feature-contracts.md#application-illustration-generate-upload-place-and-verify): use an authorized generator, upload the actual file to the destination workload, and place a suitably sized image near the top, normally below the hero. Make the artwork explain the planning purpose rather than reuse a generic landscape; keep essential meaning in native text, verify crop/contrast/navigation, and disclose any generation/upload/rendering gap. Preserve user-authored images on updates; this requirement does not authorize replacement or external disclosure of confidential data.
- Distinguish an Intelligence landing dashboard from native Home role content. The former does not prove the latter was configured. Report a missing Home writer/provider as an affected presentation boundary, continue independently supported work, and do not claim full baseline compliance until the required Home outcome is verified.
- Native Home content must fit, align and remain legible: follow [Home layout fit](home-layout-fit.md). Use flexible widths and content-driven heights for prose/cards; stack prose when available content width is unknown. Numeric Home widths are pixels, so 60/40 is not a percentage split. Check word wrapping, clipping, alignment and excess whitespace separately from API persistence; use the bundled readable constructor and static fit audit during API-only authoring.
- Every sheet has a well-formatted visible title and brief purpose/interaction description. A registry display name alone does not establish a visible introduction. Keep hidden/embedded owners introduced appropriately in their own sheet without showing duplicate headers in an embed.
- Use concise business copy that explains what users review/edit and what results they see. Navigation labels identify actual sheets and resolve authorized destinations, preserving hidden/security rules. Check selected/active states, back/reset behavior where applicable and missing destinations.

### Typography and Consistency

- Use **Arial** for all configurable text: titles, descriptions, headers, grids, charts, KPI/cards, slicers, axis labels, legends and navigation. Audit effective per-visual/per-role font overrides; a theme-level font does not prove every component inherited it. Unsupported/non-configurable surfaces are reported explicitly, not styled through guessed CSS or DTO fields.
- Use one coherent professional theme with consistent backgrounds, text, borders, cards and spacing. Keep readable contrast and clear title/body/data hierarchy. Apply current supported style contracts, not copied caches or a preset application design.
- Match type size to the frame, keep labels readable and provide enough space for long titles/control text. Prefer restrained neutral surfaces with purposeful accents; do not encode meaning only through hue, tiny text or decorative containers.

### Intelligence Dashboard

- Every artifact includes an Intelligence overview appropriate to the current request/model. During an update, a suitable overview in the specified artifact can be preserved. Choose its KPIs, charts and interactions from the business decisions; do not borrow a dashboard or domain flow from another Plan.
- Use verified chart/KPI/color/formatting patterns from [Intelligence Dashboard Patterns](feature-contracts.md#intelligence-dashboard-patterns). Resolve actual source fields, role assignments and active template/subtype/renderer instead of choosing from filenames.
- Every chart and KPI has a clear business title and suitable units, currency/percent/count/scaling/precision/null/zero formatting. Keep axes and legend labels consistent with the values; do not sum percentage measures as additive money.
- Apply IBCS only when requested and supported by the actual visual contract. It is not a universal theme requirement.

### Dashboard Banner Header

For new Intelligence/dashboard sheets, use a prominent editorial banner as the default visible introduction unless the user requests another style. For updates, preserve an existing compliant introduction; this pattern does not authorize replacing unrelated content or moving controls. Derive the wording from the current sheet's business purpose, not another application's banner.

- Use one content-width, rounded dark-navy surface with three left-aligned text levels: a small bold context/eyebrow line, a prominent bold business title, and one brief purpose/interaction description. Keep the title in natural business language; uppercase is optional, not a requirement.
- Use **Arial on every text run**. Starting sizes are 12-14 px for context, 28-32 px for the title and 14-16 px for the description. Adjust to the actual frame and viewport without sacrificing readability or clipping wrapped text.
- A suggested palette is navy `#12303D`, teal context `#75D7C8`, white title `#FFFFFF` and light description `#D5E4EB`. These are design values, not serialized property names. Verify contrast and adapt them to the user's theme; do not reuse Source/Input/Formula colors to imply that the banner itself has a measure classification.
- Align the banner with the page's main content edges. Use consistent outer margins, approximately 16-24 px internal padding and restrained corner rounding through supported fields. Calculate height from the actual text and wrapping; do not impose a fixed-height screenshot template. Keep related filter cards in a separate aligned selection area below the banner, with a clear gutter.
- Use the context line for the actual function/area and, where useful, the verified scenario/period. Do not copy a demonstration's business labels or year. Do not imply that static text tracks slicer selections: use a verified dynamic-text binding or describe the static scope accurately.
- Author through the actual Intelligence text visual's supported rich-text/editor and background/shape writers. Resolve its serialization and styling independently of Planning custom-header canvases; do not invent HTML, CSS, visual enums or formatting keys. Editor selection outlines are not part of the banner design.
- Verify saved text runs, font overrides, background and geometry through readback. Separately check rendered hierarchy, wrapping, padding and contrast, plus access to the filters below. If rendered checks are unavailable, report them as not run. A dashboard banner does not replace native Home content or a Planning owner's own introduction.

**Synthetic content hierarchy, not a serialization template:**

```text
[FUNCTION / AREA] / [VERIFIED SCENARIO OR PERIOD, IF RELEVANT]
[BUSINESS OUTCOME TITLE]
[One sentence explaining what users review or edit and the connected result.]
```

### Planning Measure Groups and Colors

Use the same visible classification and legend across every Planning sheet:

| Group label | Measures | Required color | Meaning |
| --- | --- | --- | --- |
| Source | Power BI, Blend/From Sheets, InfoBridge/From Queries measures | Blue | Values sourced from a resolved model, sheet or query. |
| Input | Data Input and Forecast measures | Amber | Input/forecast class; actual editability still follows permissions, periods and version rules. |
| Formula | Calculated formula measures | Green | Derived values; their formula/dependency references must resolve. |

Classify by actual source/kind and nested discriminator, not display name. Resolve VisualColumn's nested branch and unknown/derived kinds rather than inventing a group or changing `measure_type` to apply a color. Forecast classification does not prove that every forecast is editable. Preserve closed/locked/read-only status independently of color.

Use readable measure headers, suitable cell/background formatting, and an explicit legend with the words **Source**, **Input**, **Formula** and their meanings. Apply the same palette across sheets and matching header text. Do not rely on color alone: retain group labels, source/input/formula text and explicit editable/read-only cues. Maintain contrast for text and selected/hover/locked states. Use only supported header/cell/measure-group formatting locations; a legend is not a new native measure enum or a substitute for actually classifying the measures.

Suggested consistent palette on light surfaces: Source blue `#1F5AA6`, Input amber `#8A5700`, Formula purple `#6B3FA0`. These are design color values, not new serialized property names or a native theme object. Keep the selected palette identical across sheets and verify contrast against the actual header/cell/background/selection colors; use tints only through supported cell/fill fields with legible foregrounds.

### Planning Headers and Connected Steps

- Each Planning sheet's visible header must be a professional, sheet-specific business description, not the autogenerated comma-separated list of measures/dimensions or a generic repeated caption. Use a meaningful business title followed by concise prose explaining the sheet's purpose, eligible editable drivers and resulting business outcomes. Describe only the behavior actually configured for that sheet.
- Author the header as richly formatted text through the supported native header/rich-text writer: a prominent bold title, readable body paragraphs and restrained bold emphasis or short labeled sections. Include readable color-coded Source/Input/Formula text matching the palette and the explicit legend where relevant; do not substitute a long field inventory for an explanation.
- Use **Arial throughout the header**, including every title, body, label and emphasized text run. A grid font or global theme alone does not establish the rich-text header font. Preserve the actual editor serialization and unrelated header/footer settings; do not guess HTML, CSS, font fields or rich-text nodes. If the selected route cannot persist the required content/style, resolve the native writer or report that requirement as blocked rather than leaving the default heading and claiming compliance.
- Explain save/recalculate/refresh steps only when necessary and verified for connected results, using the actual mechanism/order and status. Do not promise automatic propagation or invent an InfoBridge endpoint.
- Keep header/legend copy specific to the request and sheet. Include business rates, calculations and cross-sheet instructions only when supplied or resolved from the current request/model and implemented through verified contracts.

**Synthetic header copy, not a serialization template:**

**Workforce Compensation Planning**

Forecast employee compensation in USD across the selected planning periods. Review source compensation and exchange rates, adjust eligible salary and benefit assumptions, and compare the resulting total employment cost.

**Source:** baseline compensation and exchange rates. **Input:** eligible compensation assumptions. **Formula:** calculated compensation in USD.

Render this hierarchy in Arial using the actual header editor's supported rich-text format; adapt the wording to each sheet's implemented business process rather than repeating this example across sheets.

### Grid and Embedded Layout

- Align charts, cards, slicers, embedded Planning visuals and PowerTables to one consistent canvas grid. Use common margins, gutters, alignment and balanced proportions; keep owner/header/control hierarchy predictable.
- Prevent unintended overlapping visuals, clipped titles/descriptions/control labels and obscured grid toolbars/pagination. Intentional background layers must not hide or intercept foreground controls.
- Give embedded grids enough space for their headers, rows, editable cells, save/refresh controls and footer/pagination. A large surrounding rectangle alone does not prove usable grid space.
- Keep owner geometry and dashboard override geometry consistent where applicable through their verified coordinate/size contracts. Preserve source visual identity and explain whether geometry is owned, overridden or inherited; do not copy an override into every source or invent `embeddedConfig`.
- Record the intended viewport/canvas size and verify the actual layout at that size. If mobile or other viewing sizes are intended, verify them too; empty `mobileProperties` is not responsive acceptance.

### Professional Intelligence Composition

Treat the dashboard as a working interface, not a collection of schema-valid rectangles. Its hierarchy, spacing and usable planning area determine whether users can compare periods, enter values and reach controls. Apply these requirements to every generated or updated Intelligence composition, including Planning grids, charts, slicers, filters, KPIs and navigation, while preserving unrelated existing content.

- Design around task importance. Make the primary Planning sheet a prominent, aligned workbench with meaningful width and height; secondary analysis must not crowd it into a small corner. Reserve room for multiple visible periods, row/column headers, editing, scrollbars, grid toolbars and footer/pagination. Size the actual embedded grid, not merely its outer container.
- Group related dashboard filters into a coherent selection area; keep their labels, selected values, search and dropdown controls readable and accessible. Organize summary KPIs and related charts together, with local navigation near the area it controls. Distinguish summary review from the main editable workbench without scattering related controls across the canvas.
- Use shared alignment tracks and consistent outer margins, inter-component gutters and internal padding. Choose widths/heights from actual labels, content, viewport and interaction needs. Align related edges and baselines; avoid accidental gaps, narrow compressed grids and mismatched component sizes without a functional reason.
- Use the canvas effectively. Leave purposeful whitespace for grouping and readability, but do not surround a tiny planning grid with large unused regions or inflate the canvas to avoid layout decisions. Allocate meaningful area to planning and supporting analysis according to the task, not a fixed template or arbitrary occupancy percentage.
- Balance visual weight across the canvas. Prefer coherent symmetry/alignment; use asymmetry only when intentional and useful, such as a larger primary workbench beside narrower supporting analysis. Empty space on one side and compressed content on the other is a defect, not evidence of intentional design.
- Foreground components and controls must not overlap or obscure one another. Intentional background layers must remain non-obscuring and must not intercept interactions. Check internal content fit as well as outer bounds: a clipped filter, hidden grid footer or unreadable KPI fails even when every rectangle is positive and in bounds.
- Review accessibility and practical use: readable labels and contrast, sufficient control/hit areas, reachable editing/navigation controls and logical keyboard/focus order where configurable. Verify the supported native behavior rather than inventing unsupported accessibility properties.

#### Dropdown Slicers and Selection Area

- Prefer compact dropdown slicers for categorical dashboard selections, especially long member lists. Use another supported control when the task benefits from it, such as a date-range selector; dropdown is a presentation default, not permission to change selection semantics or the underlying filter contract.
- Group related slicers in aligned cards below the banner, with consistent heights, padding and readable Arial labels. Order them by decision flow: scenario/time context first where applicable, then organizational/entity scope and domain-specific selections. Derive fields and order from the current model and task, not a fixed number of screenshot controls.
- Show the current selection clearly through supported selected-value/chip displays; keep dropdown affordances, search, clear/reset and keyboard interaction available where supported. Choose single- versus multi-select from business requirements, preserving existing behavior during updates. Test long labels and multiple selections without compressing the control into unreadability.
- Resolve each slicer's real field binding, initial selection, target visuals and filter propagation, including any embedded Planning sheet. Do not assume dashboard filters automatically reach embedded owners or invent interaction flags. Preserve scenario, period, eligibility and security context; a slicer is not an authorization boundary.
- Avoid duplicate-looking period or entity controls unless they intentionally affect different scopes. If both are needed, label the difference and verify each target. Do not copy demonstration member selections, dates or default scenarios.
- Allow the expanded dropdown to overlay adjacent content as a temporary interaction layer without being clipped by cards/canvas or trapped behind visuals. This is not a permanent-frame collision. Check opening, searching, selecting, clearing and closing in the actual renderer; a closed-control screenshot does not establish usability.

#### Embedded Planning Workbench Explanation

- Place a concise visible explanatory text box directly above each embedded Planning workbench, aligned to its content edges. It must identify what that specific sheet is for, what users review or may edit, and the resulting business outcome. A generic "Planning" label or sheet registry name is insufficient.
- Use a short bold heading followed by readable Arial copy. For a read-only review surface, say that assumptions are maintained elsewhere rather than inviting edits. Explain expansion, navigation or model structure only when that behavior is actually configured.
- Include the explicit **Source**, **Input** and **Formula** legend where relevant, using the shared blue/amber/green classification and readable text, not color alone. Clarify that permissions and locked periods still determine editability. Do not imply that every embedded sheet contains all three classes or editable inputs.
- Include save/recalculate/refresh instructions only when their mechanism and order are verified for that sheet. Do not reproduce an InfoBridge refresh instruction merely because it appears in an example, or promise automatic connected-result propagation.
- Treat the textbox as dashboard-level orientation, distinct from the embedded owner's own native header. Keep both useful without repeating a large header inside the embed; hide a duplicate only through a verified per-instance display setting while preserving the owner's introduction and unrelated settings.
- Size the strip for its actual wrapping and content; leave a clear gutter to the grid and keep navigation, refresh/save controls and grid headers accessible. Do not substitute explanatory text or an empty styled rectangle for a working embedded sheet.

#### Canvas Color and Visual Reading Order

- Give the Intelligence page canvas a pleasant, restrained background through its verified native page-background writer. Prefer a soft blue-gray such as `#EDF4F6` or neutral `#F4F6F8`, with white visual cards (`#FFFFFF`) and subtle borders such as `#DCE5EB`, unless the user/theme requires another palette. These are adaptable design tokens, not property names or a fixed theme schema.
- Apply and read back the actual canvas background independently of card/shape fills. A white card, decorative background rectangle or successful theme call does not prove that the page canvas was styled. Preserve contrast with the banner, text, controls, selected states and planning classification colors.
- Use a deliberate reading sequence: **banner/context -> grouped dropdown selections -> summary KPIs and supporting charts -> local view navigation where needed -> workbench explanation -> prominent embedded Planning sheet**. A smaller aligned analysis column beside the workbench is also appropriate when useful. Adapt the sequence to the task and viewport rather than forcing identical rows on every sheet.
- Align slicer cards, KPI/chart edges, explanation strips and workbench bounds to shared tracks, with consistent gutters, padding and corner treatment through supported settings. Balance chart/KPI weight and reserve the largest useful editing region for the workbench, including multiple periods, scrollbars and footer controls.
- Omit unnecessary components and collapse unused bands instead of leaving decorative empty regions. On smaller target viewports, use supported reflow or scrolling without squeezing controls or the grid below practical usability. Do not move unrelated existing visuals without authorization.
- Judge the settled interface, not editor handles, selection outlines, loading spinners or skeletons. Wait for charts, slicers and embedded grids to initialize before rendered acceptance; record loading/initialization failures separately from layout defects and do not claim a loading screenshot proves the design works.

#### Dimension-Aware View and Pivot Names

- Name each saved pivot/view from the dimensions and business perspective actually configured in that visual. Resolve its effective Rows, Columns, nesting and any bookmark overrides against the visual's bound dimensions; neither a generic template caption nor the full semantic-model field inventory establishes the view's meaning.
- Prefer concise business labels such as "By Region", "By Department" or "Region and Department" only when those descriptions match the configured view. Use current friendly dimension names. Do not retain "Product Pivot" on a visual with no Product dimension, or call a multi-dimension view "Region Pivot" merely because Region is available somewhere in the sheet.
- Do not create a pivot for every available dimension by default. Choose useful views from the actual business task; if a requested perspective has no valid dimension/assignment, resolve that gap rather than renaming an unrelated view to suggest it exists.
- Check labels in the owner's pivot configuration, affected saved bookmark snapshots, navigator captions and selected/active view state so switching views does not restore stale template names. Preserve stable pivot/bookmark/visual/member IDs, formulas and saved inputs; a caption correction is not permission to change axes, filter semantics or business logic.
- Read back each saved view's label and configured dimensions together, then verify displayed labels and view switching where renderer access is available. If labels expose a wrong underlying assignment, report and repair that separately through its verified writer; do not disguise a configuration defect with a cosmetic rename.

#### Layout Generation and Correction

1. Establish intended canvas/viewports and an importance-ranked inventory of every visible component. Allocate grouped filter/navigation, summary-analysis and primary-workbench areas before assigning precise geometry; there is no universal pixel layout.
2. Record each component's actual position, width, height, coordinate units, owner/override source and parent. Include charts, grids, slicers, filter controls, KPI cards, text and navigation, not only embedded visuals. Resolve missing or ambiguous geometry/owner matches as failures of the audit, not zero-collision successes.
3. Normalize bounds into a common audit coordinate space using verified contracts, without changing native units. Check each component against its canvas/parent bounds and inspect pairwise bounding-box intersections between unrelated foreground siblings. Parent/child containment is not a collision, but clipped or inaccessible child content still fails. Audit background layering separately for obscuring or interaction interception.
4. Review the composition beyond coordinates: whitespace distribution, alignment, margins/gutters/padding, visual balance, primary-sheet prominence, periods visible and room for editing/controls. A zero-intersection result cannot pass a tiny or compressed workbench, disproportionate empty canvas or an unusable filter group.
5. Correct known defects before publication: reposition, resize or reflow components; regroup filters/summary content; reduce secondary clutter or move supporting analysis to an appropriate existing/new authorized page when necessary. Do not solve crowding by shrinking the primary sheet below usable size, hiding controls, dropping requested content or expanding the canvas indiscriminately. Preserve identities, bindings, permissions and intentional per-page overrides.
6. Re-run the complete geometry and composition review after each layout correction. Record unresolved defects and withhold the affected layout while it fails definition-level requirements. A supported first save can precede native visual verification, but it does not establish professional acceptance.
7. Where an actual renderer is available and authorized, inspect the real dashboard at each intended viewport and relevant selection/navigation state. Check initialization, visible periods, text fit, internal grid size, scrolling, editing and all controls; compare rendered positions with active owner/override geometry. Correct/reflow and re-verify observed defects before declaring the result ready. If rendering is unavailable, explicitly report `rendered verification: not-run` and retain that acceptance gap.

| Composition example | Result and action |
| --- | --- |
| Grouped filters above aligned summary KPIs/charts, with a large Planning workbench showing several periods and all controls | Valid design candidate; still requires actual bounds/content-fit checks and rendered verification |
| Large Planning workbench with a narrower aligned comparison chart beside it | Useful intentional asymmetry when both surfaces remain readable and usable |
| Small Planning grid off to one side with most of the canvas unused | Invalid; rebalance/reflow and expand the workbench to the useful available area |
| KPI or slicer over the grid header, scrollbar or footer | Invalid; separate the component bounds and preserve access to grid controls |
| Non-overlapping outer frames, but clipped filter labels or a compressed editable grid | Invalid; resize internal/outer geometry and reflow adjacent content, then inspect again |
| Planning region displays Initialization Failed inside an otherwise aligned frame | Failed functional acceptance; investigate initialization independently, and correct layout defects without assuming geometry caused the runtime error |

The user's undesirable dashboard screenshot motivates the prominence, whitespace and practical-usability checks; it is not a reusable layout template or proof of a specific serialization bug. JSON generation, successful publication, positive rectangles and an offline canvas diagram are not proof of professional or functional acceptance. An observed native failure overrides any earlier assumption that an API-successful dashboard was usable.

### Fresh-Run Embedded Placement Sequence

Use this sequence for each independently authorized creation or layout regeneration. The supplied technical placement guide contributes design and audit methods, not a universal Fabric schema or evidence that its historical corrections rendered successfully. Do not copy its page list, canvas dimensions, bookmarks, identities or unrelated cleanup operations.

1. **Inventory before layout.** Separate the page canvas, embedded instance, source Planning visual and grid interior. Record the target-build property paths, units, canvas mode/dimensions, page and source identities, every applicable owner/reactive placement and any alternate layout or saved state carrying geometry. Preserve the hidden direct owner and binding. Resolve missing or duplicate instance matches instead of selecting the first entry or manufacturing another one.
2. **Fetch before every addition.** Use [CLI Visual Placement](feature-contracts.md#cli-visual-placement) to retrieve the full target sheet inventory through the API used by `fetchVisuals`. Include all visuals, Planning embeds, slicers, filters and known pane exclusions. Missing geometry is unresolved occupancy, not free space.
3. **Preserve the coordinate system and requested dimensions.** Work directly in the fetched pixel or fractional units and actual layout bounds. Convert only when a pixel-sized request must be serialized to verified fractional fields, preserving rendered size. Do not scale coordinates arbitrarily, reflow existing visuals or change canvas mode silently. Use consistent gaps and logical aligned bands without unnecessary whitespace.
4. **Calculate before creating.** Use the pure edge-based helper linked from the CLI workflow with complete occupied rectangles. Keep the requested width/height unchanged. Include each new rectangle before placing the next. If none fits, use only authorized supported expansion that preserves existing geometry, or report no fit; never overlap, shrink or move old visuals.
5. **Create and save through APIs.** The inspected creation API does not take geometry; persist the precomputed position/dimension through the supported properties writer as part of the planned addition. For embeds, save the dashboard-local entry without altering the source. Refetch current ETags and reconcile concurrent changes. Do not require React callbacks, mounted stores, browser control edits or a backend/importer fix.
6. **Audit candidate and saved records independently.** Keep the pixel design separate from extracted candidate geometry and later saved geometry. Resolve each record by actual page/source/instance identity; update all applicable authoritative representations, not just the easiest one. Require equality for records that must agree, but preserve legitimate per-page overrides when one owner appears on several dashboards. Missing exported page properties are a transport/evidence gap, not proof that an authored override was activated. Use the authoritative native readback when available and label it separately from ALM evidence.
7. **Refetch and verify persistence.** Retrieve a fresh page-properties response after saving. Compare intended position/dimension, full bounds and clearance against all current visuals and reserved areas; check old rectangles and configuration are unchanged. Persisted geometry can be checked without seeing the UI. Native readability, zoom/panel behavior, bookmarks and query correctness remain separate runtime checks when authorized and available; never claim those from a geometry pass.

Record calculated geometry, API creation/save, fresh persisted geometry and optional rendered usability separately. This is the current skill-only CLI workflow; earlier importer-deployment and manual-repair guidance does not govern it. Never claim a live save or runtime check from this documentation/helper update.

#### Independent Geometry Audit

The supplied `audit_layout.py` consumes a project-owned pixel manifest, not Fabric JSON. Inspect the available utility and its input contract before using it; do not hardcode another user's machine path or assume the attachment is installed with this skill. Extract every relevant visible component, not just the Planning grid, and retain record paths, units, identity mapping and source/candidate/readback hashes in private evidence. Preserve large native IDs losslessly.

- Set `rect` from the intended design; extract `ownerRect` and `reactiveRect` independently from their actual serialized records. Never populate all three by copying the intended rectangle. Set `requirePlacementMatch` only where the verified contract requires those records to agree; an unavailable required record fails that check rather than becoming an empty successful comparison.
- Check unique identities, finite positive sizes, bounds, intersections and declared minimum gutters. Allow only individually justified background/foreground overlap pairs; do not lower the gutter or exempt every pair to force a pass. Add separate assertions for equal selector widths/heights/Y, common edges and repeated gaps because the supplied auditor does not prove symmetry or alignment.
- Re-run after reflow and against saved records. Include negative checks for a stale owner rectangle, duplicate or missing reactive match, wrong coordinate units, out-of-bounds placement, overlap and inadequate gutter. Identity/cardinality checks belong in the extractor when the geometry utility cannot express them. A missing-record or zero-visual inventory must never pass.
- Keep static and rendered outcomes separate. Static agreement cannot establish internal text/control fit, source binding, query refresh, bookmark restoration or native persistence. Retain raw revised JSON and a focused geometry-only change log without credentials; preserve unrelated data/model/connection/formatting settings.

**Synthetic unit/reflow check:** On a 1600 x 1000 canvas, pixel rectangle `{x: 32, y: 500, width: 1536, height: 476}` becomes position `{x: 0.02, y: 0.5}` and dimension `{width: 0.96, height: 0.476}` only in a verified fractional representation. Changing height to 1200 while preserving those pixel bounds requires Y `500 / 1200` and height `476 / 1200`, not the previous fractions. Derive real dimensions from the current task; this is a conversion test, not a page template.

### Embedded Layout and Navigation Checks

- Apply the [embedded placement identity gate](feature-contracts.md#intelligence-dashboard-business-authoring) before accepting canvas geometry. Compare effective page-local placements through a verified runtime mapping; GUID-keyed rectangles can be correct on paper while the live embed falls back to a small frame at the origin. The inspected percentage-mode placement records use fractions; verify each target record's units rather than generalizing from an editor label. Preserve a user's native-saved alignment and validate that readback instead of restoring the generated layout.

The creation supplement reviewed 2026-11-07 adds the following implementation/acceptance checks, not new geometry, formatting or Home schemas. Its historical visual failures are diagnostic hypotheses; reproduce them through the target family's writer and renderer before treating a workaround as verified.

- Map every embedded Planning visual to its real source/owner and dashboard placement. Reconcile canvas, owner, embedded and reactive geometry where those records are authoritative. An update to only one coordinate record can leave another active record positioning the grid over the header; inspect the active owner/override path rather than adding a guessed wrapper.
- Record each family's coordinate units and canvas dimensions before comparing rectangles. Positive finite sizes, in-bounds placement and non-overlap checks do not establish font measurement, control fit or native rendering. Normalize coordinates only in an internal audit representation, never silently in the saved native records.
- Reserve separate areas for the page introduction, selections, KPI/chart analysis, local pivot/bookmark navigation and planning workbench. Leave enough internal height for slicer labels, search/selected values, grid controls and footer/pagination; inspect actual content fit, not only outer frames.
- Name pivot/bookmark views for dimensions actually present in their owning sheet. Do not copy a Product view label into an unrelated sheet. Check actual pivot IDs, filter state, both axis aggregations and switching behavior in standalone and embedded views.
- Keep bookmark navigators local and relevant to the current working area rather than exposing an unrelated artifact-wide strip. Verify selected/default states and permitted destinations without changing private/public visibility or sheet security.
- Keep period labels chronological across years, and initial scope bounded by request/model-relevant selections. Do not hardcode a region, category, cell-count limit or default scenario from a demonstration. Verify that slicers and source-query filtering agree; a consumer cannot recover rows excluded from materialized source data.
- Diagnose an undefined KPI suffix through the KPI/Charts formatting owner. A historical workaround disabled its Number Format setting; this is not a universal instruction to disable formatting or change Matrix scaling. Resolve the active renderer, units and setting before applying and testing any switch.
- Preserve per-family formatting names and encoded boundaries. Matrix separator spellings and Charts separator spellings differ; `autoFixed`, Auto and scaling settings are not globally interchangeable. A reader's empty-object fallback is not a complete writer contract.
- For native Home, verify mode-authoritative role content/order, serialized text, real assets, card inclusion/exclusion, descriptions and navigation separately from visibility. Do not use temporary blob URLs or assume an empty exclusion list excludes future eligible sheets. Preserve sibling state and ETags through the actual save/merge path; role priority and card visibility do not grant access.

Report [construction readiness](feature-contracts.md#construction-readiness-and-evidence), saved presentation settings and rendered behavior separately. Independent feature fixtures and static layout audits are useful evidence, not permission to copy another application's design or proof of compliant native Home/embedded rendering.

An explicit user request to deploy with best-judgment presentation and no runtime verification permits a supported initial save with disclosed native activation limits; it does not make the layout verified. Follow the [best-effort embedded-placement distinction](feature-contracts.md#intelligence-dashboard-business-authoring): keep complete portable ownership, choose usable authored geometry, never guess runtime identities, and report possible default-position fallback separately. Retain the normal layout-acceptance criteria for any later claim of visual correctness.

An offline layout map generated from saved rectangles is a diagnostic diagram, not a native screenshot or evidence of text fit, clipping, grid loading or interactions. For each requested embedded placement, distinguish missing, single and ambiguous owner/override matches before comparing geometry; a loop over zero matching overrides must not count as a successful agreement check. The recorded build matches an existing override's `visualId` to the owner's `originEntityId` within a page that references that portable visual. Verify that route for the target family, preserve intentional per-page overrides, and do not synchronize every instance merely because a historical builder did so. Derive canvas units, bounds and workbench sizes from the current design rather than that build's fixed pixel rectangles.

## Implementation Map and Unsupported Settings

Use the [feature contracts](feature-contracts.md), their current implementation/ALM owners, applicable [public Plan schemas](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/plan-definition), and current AI compiler field maps. These establish different layers; no historical export, report inventory or handoff is a design dependency. Inspect both the writer and importer before emitting a full part.

| Requirement | Verified evidence / applicable layer | Remaining gate; do not invent |
| --- | --- | --- |
| Home | [F24 Home Layout](feature-contracts.md#f24-home-layout): native show/layout items/rows/roles, shallow-update behavior. | Full text-instance fonts, navigation/role mapping, save/export/import/assets remain partial. No guessed Home part or arbitrary rich-text keys. |
| Sheet introductions/navigation | Current Text/Navigator compiler field maps and writers; native schema guides. | Text content schema is not universal font support; destination/page/bookmark identity, rich-text style and ALM mapping must be verified. |
| Arial/theme | [F26 Themes](feature-contracts.md#f26-themes), Charts/Matrix typography readers and native/schema mappings. | Complete theme leaves and inheritance/overrides, per-surface font field and import/render support are not established by a global `fontFamily`. |
| Chart/KPI formatting | [Source-Backed Contract Rules](feature-contracts.md#source-backed-contract-rules), [F03 Quick Format](feature-contracts.md#f03-quick-format), current renderer/role writers. | Resolve each adapter's encoding; number-format keys are not font/title keys. Check actual title/legend/axis writers. |
| Planning colors/groups | [F12 Measure Model](feature-contracts.md#f12-measure-model), [F14 Formatting](feature-contracts.md#f14-formatting), [F15 Conditional Formatting](feature-contracts.md#f15-conditional-formatting), [native kinds](feature-contracts.md#native-measures-and-inputs). | Header/cell wire keys, ID grammar, group serialization and imported preservation remain partial; no guessed group DTO. |
| Canvas geometry | Public visual Position/Dimension declarations and the current AI envelope's separate position/dimension types. | Actual family writer/ALM contract still applies; public type acceptance is not rendered fit or a full visual constructor. |
| Embedded owner/override | [F27 Embedding](feature-contracts.md#f27-embedding) and selected source/owner/import handlers. | Pagination alone does not establish geometry, permissions, source restoration or complete embedding/import. |

For each unresolved setting, record: requirement/surface, target sheet/visual/measure, desired presentation, inspected owner/field map/revision, existing representation, exact missing native/writer/ALM boundary, safe supported alternative if any, and whether the requirement is blocked or truly non-configurable. **Unknown is not product-unsupported.** Do not hide unresolved Arial, Home, grouping or layout requirements behind a generic "theme applied" success.

### Current Source-Corroborated Mappings

The following current compiler/handler owners were independently rechecked without using artifact examples. Source inspection is scoped to their field maps and behavior, not full ALM or rendered acceptance; no product code was modified:

| Owner | Verified mapping / result | Consequence for this baseline |
| --- | --- | --- |
| Text compiler | Only schema `content` -> native `text`, string; writes through `updateTextVisualState`. Character styling is selection-scoped Lexical/textStyleStore work, intentionally unmapped. | No `fontFamily`, font color or bold property may be added to this compiler payload. Content type acceptance does not validate a rich-text document; preserve the actual editor serialization. Arial/title styling remains blocked in this route until a verified styling writer is used. |
| Shape compiler | Schema `fill.color` -> native `fill.fillColor`; `fill.show` -> `fill.isEnabled`; border color/width/style/show and shadow color/blur/show have separate fields. Border styles: solid/dotted/dashed. | Use the friendly schema only through its compiler, native fields only at the actual shape-state layer. Neither is a whole exported visual or an ALM wrapper. Preserve merged siblings; do not use Shape fill as a Planning measure-color DTO. |
| Theme handler | Resolve returns `applied: false` with an implementation warning. Object/name validation alone is not theme application. | Do not claim one base theme call applied Arial/colors across the artifact. Find the supported native theme/visual writer or record the baseline as blocked for this route. |

## Authoring Workflow

1. For creation, map the current request/model to necessary sheets, overview and interactions. For updates, inventory the specified artifact's existing surfaces and input identities. Do not request or search for a reference application. Design the visible business experience first, then choose actual owners and embedding only when it improves usability without losing context or editing controls.
2. Read this baseline and the relevant feature/native/schema/ALM owners. Build a requirement-to-surface mapping with representation/update method and explicit gaps.
3. Configure Arial, coherent theme, palette and request-specific layout through verified fields only. Preserve unrelated state during updates; do not reuse another application's layout or business assumptions.
4. Add/maintain visible Home/sheet/chart/KPI titles, concise descriptions, navigation, Planning header/legend and necessary verified save/refresh copy. Do not silently drop a mandatory requirement because its writer is unknown.
5. Apply [professional Intelligence composition](#professional-intelligence-composition): allocate a prominent Planning workbench, group selections and summaries, then audit every component's bounds, intersections, whitespace, alignment, balance and internal control fit. Correct/reflow defects before publication and re-run checks. Align canvas frames, internal controls and supported embedding overrides to the intended grid/viewport. Preserve unrelated content, permissions and stable identities.
6. Run pre-save definition checks, execute the supported authorized save, then inspect its saved settings and separately authorized rendered behavior. Report completeness, unimplemented/blocked settings and exact evidence; no compliant-artifact claim while mandatory surfaces are unresolved or render verification is missing. Do not require an already-rendered new artifact before its first supported creation.

## Synthetic Examples

The following examples illustrate shared design requirements or a source-declared schema layer. They are synthetic, contain no resource identities and prescribe no default business application.

**Synthetic operational overview:** Derive title, measures, selections and navigation from the current request/model. Apply supported Arial, theme, labels, units and aligned frames. Do not introduce unrelated planning domains. Classification applies only to actual Planning measures.

**Synthetic planning update:** Preserve the specified artifact's stable member/input identities. Classify verified source/input/formula measures blue/amber/green with labels and a legend; keep locked inputs read-only. Use only the actual supported save/refresh mechanism and geometry writers. Unresolved color/group writers are gaps, not invented JSON.

**Unsupported font surface:** If a compiler supports rich-text content but exposes no styling field, do not send an invented `fontFamily` or declare Arial applied. Identify the actual rich-text writer/schema needed, retain supported edits and report the typography requirement unverified/blocked. No raw JSX/CSS/theme injection is a serialization workaround.

**Synthetic native Shape schema fragment:** The source-declared field map accepts this friendly fill section and maps it to `shapeState.fill.fillColor/isEnabled`. The color is a synthetic design choice, not a business default. This does not style a Plan/theme/measure or create a full part.

```json
{"fill":{"color":"#F4F6F8","show":true}}
```

Validate type/mapping, preserve existing shape siblings and later verify actual contrast/rendering. No unsupported typography property is added to make the example satisfy the full artifact baseline.

## Validation Checklists

### Definition-Level Checks

- Record presentation coverage by actual visual family and readiness layer; local helper/geometry checks, API acceptance and imported records are not rendered-layout acceptance.
- Home/dashboard presence and real navigation targets; visible sheet/chart/KPI introductions configured through supported records, not merely registry names.
- Every Planning header has a distinct professional business description and saved rich-text hierarchy with Arial on all text runs; reject autogenerated measure/dimension lists. Inspect persisted header content/style separately from grid/theme settings and record any unresolved writer boundary.
- Every configurable font surface mapped to verified Arial settings and inherited/override paths; unresolved/non-configurable surfaces individually reported.
- Coherent theme and readable palette tokens applied through actual native fields, without invented enums/style paths or lost siblings.
- Actual Intelligence canvas background configured independently of card fills; dropdown slicer presentation, labels, selection semantics, field/target bindings and initial context recorded through verified contracts.
- Every embedded Planning workbench has an aligned, sheet-specific explanatory textbox with accurate edit/read-only and connected-result guidance; dashboard orientation and the owner's header remain distinct without unnecessary duplication.
- Every Planning measure classified by verified kind/provenance; Source/Input/Formula group labels, blue/amber/green header/cell treatment and explicit legend present where supported. Color is not an input permission.
- Appropriate chart/KPI units, precision/scaling/null/zero handling, title/axis/legend references and valid template/assignment combinations; no global IBCS assumption.
- Finite numeric frames with positive sizes, intended viewport/grid alignment/margins/gutters; owner/override consistency where supported; intentional backgrounds distinguished from unintended overlap. Definitions cannot prove text fit or control usability.
- Complete component inventory with position/width/height and verified coordinate spaces; all applicable bounding-box intersections and canvas/parent bounds checked, with no obscured foreground controls. Missing geometry/owner matches fail the audit.
- Primary Planning workbench prominent and sized for multiple periods, headers, editing, scrolling, controls and footer/pagination; filters grouped, summaries organized, navigation local. Review effective canvas use, whitespace, padding, alignment, accessibility and balance, not only numeric rectangles; correct/reflow failed candidates before publishing.
- Exact family wrappers, encoded string boundaries, required companions and source/measure/page/bookmark IDs preserved; no copied tokens/caches/migration flags as required settings.
- Pivot/bookmark labels describe each view's effective dimensions and perspective, not merely any available model field; check owner configs, affected snapshots and navigator captions for stale template names. Navigation references actual views and local groups, and scenario selection remains in persistence/query context even when omitted from visible rows.
- JSON/schema/source checks and export/import preservation results labelled by layer; generated part counts or parse success are not rendered acceptance.

### Rendered-Layout Checks

- Record actual artifact/revision, role, viewport/canvas dimensions and page/selection; inspect Home, every sheet and relevant embedding state.
- Visually confirm Arial where configurable, hierarchy/contrast, title/description/axis/legend/control fit, consistency of selected/hover/locked states and legible classification labels.
- Confirm every Planning header renders its sheet-specific description, rich formatting and Arial without clipping or obscuring the grid, including the relevant source-sheet and embedded states; avoid duplicate introductions in an embed. Save/reopen preservation and actual rendering remain separate from definition-only checks.
- Check grid alignment, no clipped/overlapping/inaccessible controls, adequate Planning/PowerTable area, internal chart/KPI layout and correct owner/override behavior.
- Confirm the primary grid initializes and has practical working space, multiple visible periods and reachable editing/scroll/footer controls; inspect empty-space distribution, grouped filters/summaries, visual balance and accessible control fit at each intended viewport. Reflow observed defects and recheck; a successful save does not overrule failed rendering.
- Exercise local pivot/bookmark switching, selector search/selected-value display and hidden-owner embedding; check reserved header/navigation/workbench areas in their active states, not just initial frames.
- Open dropdown slicers and test search, long labels, multi-selection where applicable, clear/reset and keyboard access. Check popup clipping/layering and actual filtering of intended charts and embedded Planning sheets, not only closed-control geometry.
- Inspect the settled banner-to-filters-to-analysis-to-workbench reading order, pleasant canvas/card contrast and explanatory textbox fit; do not accept loading placeholders or editor selection decorations as final rendering.
- Check images/assets load, navigation resolves permitted destinations, slicers/interactions/reset work and applicable save/refresh copy matches actual behavior.
- Verify intended desktop/mobile or other target sizes, screenshot evidence plus interaction checks when authorized; static bounds alone do not prove text measurement, fonts or responsive behavior.
- Report `rendered verification: not-run` if no actual renderer/browser was used. Never label definition-only formatting as visually verified; full presentation acceptance requires both layers and disclosed gaps.

## Required presentation defaults (v9)

Read [planning-presentation.md](planning-presentation.md). Normal application builds
require rich Intelligence dashboards above their embedded Planning grids. The
complete native TEXT header writer and semantic measure palette are executable
through present-planning; build/provision apply new-application defaults. Use
check-application-presentation for offline coverage. These defaults preserve the
v8 integrity checks and all prior Forecast, formatting, From Sheets and storage fixes.
Explicit requests to skip runtime validation still take precedence; use the
verified identity/ETag reads and save-only placement options described there.


## Required application baseline (v11)

Home is mandatory alongside rich Planning headers, measure colors and embedded
Intelligence dashboards. Read [application-defaults.md](application-defaults.md).
Use `check-application-defaults`; verify Home content, role metadata and workload
visibility separately. Do not silently downgrade a complete application to grids
or dashboards without its native landing page. Retain all source-binding fixes.
