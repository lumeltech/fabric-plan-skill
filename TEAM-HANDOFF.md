# AI Session Context: Improving the Fabric Plan Skill

## Your role

Help the user build and maintain native Fabric Plan applications using the
`fabric-plan-skill` skill, and improve the skill using the findings and
corrections shared during that work. The objective is not just to fix a single
application: carry reusable, verified learnings back into the skill so future
sessions benefit.

## Background and structure

Start with [SKILL.md](SKILL.md) and follow its routing, scope, approval gates,
and validation requirements. Its latest release-specific corrections take
precedence over older retained workflow or fallback wording.

Resolve this file's parent as the skill root. Run `python plan.py discover`
there, then use [module routing](references/module-routing.md) to select the
functional guides, commands or callables, prerequisites and execution phases
for every requested business outcome. Use the
[runtime guide](references/runtime-guide.md) for execution. For Intelligence
feature details, use the [Intelligence index](references/intelligence/index.md)
and [feature master list](references/intelligence/feature-master-list.md).
Load only the references needed for the current task.

The skill covers Planning, Intelligence, Home, native Forecast, connected
planning, InfoBridge, PowerTable, dimension mapping and the other documented
module routes. Check each feature's construction state and limits; coverage
does not imply that every advanced factory or runtime behavior is verified.
This skill is for Fabric Plan, not ordinary Power BI reports. These session
instructions supplement the skill; they do not override its boundaries or
permission requirements.

Use Python 3.11+ and Node.js 24+ for the applicable compressed-payload/HTTPS
adapters. The bundled runtime does not require a source checkout, an old report,
a task-local repair script or a particular agent's tools. Keep task data,
operation ledgers and API journals outside the skill root. Credentials belong
only in the named process environment.

Many references end with an `## Additional details` section merged from a
companion Intelligence authoring library. Those sections are additive, tag
each native claim `[saved]`, `[confirmed]` or `[open]` as defined in
[merged companion-library evidence](references/intelligence/core/native-samples.md#merged-companion-library-evidence),
and never override the guidance above them or a feature's `encoding`. When a
report test confirms or corrects a merged statement, update that statement
and its tag in place.

## Authoring and delivery contract

- Interpret the business outcome before choosing a recipe. Read
  [adaptive business authoring](references/adaptive-business-authoring.md) for
  new or materially changed requests. The five bundled use cases are composable
  examples, not the limit of the skill.
- Resolve current model metadata and source identities. If the semantic model
  ID or URL is missing from both the request and unambiguous task context, ask
  for it. Default creation to its resolved hosting workspace unless the user
  specifies another destination; ask if that workspace cannot be resolved or
  cannot host the Plan. Never substitute fixtures or historical target IDs.
- Follow the [verified authoring flow](references/verified-authoring-flow.md)
  using bundled API constructors and authenticated adapters. There is no native
  UI authoring fallback. Preserve requested inputs, formulas, Forecast and
  conditional formatting together; do not silently deploy a reduced substitute.
  State precise gaps and continue independent authorized work.
- New applications require Arial, enabled native Home with business guidance
  and navigation cards, Intelligence coverage with an embedded grid for every
  Planning owner, and a visible native Page Navigator on every Intelligence
  dashboard. Include rich-text descriptions/legends and source-role measure
  colors. Follow [application defaults](references/application-defaults.md).
- Use `plan.py provision` for standard reports. Follow the latest public
  deployment contract for geometry, navigation, visibility and matrix placement;
  native workload calls are reserved for role-specific Home layout. Hide a
  Planning sheet only when its grid is embedded in a visible dashboard, and use
  that dashboard as the Explorer/Home destination. Keep requested business
  PowerTables visible and preserve owner GUIDs, grid IDs and connected bindings.
- Size dashboards for the drawable Reading viewport and verify page-local
  placement without moving source owners. Preserve existing inputs, storage
  coordinates, unknown fields and unrelated state during updates. Mandatory
  new-application defaults do not authorize unrelated writes in scoped repairs.
- Use explicit authorized destinations, fresh baselines and ETags where
  required. Create once, poll asynchronous operations to completion and
  reconcile uncertain submissions instead of duplicating items or replaying
  mutations at alternate routes. Initial InfoBridge refresh is optional; do
  not report skipped propagation checks as passed.

## Sharing and extracting a ZIP on Windows

Native samples contain nested sheet and visual GUID folders. A long extraction
destination can exceed Windows Explorer's legacy path limit and cause
`0x80010135: Path too long`, including for `writeback.json`.

- When creating the ZIP, select only the allowlisted contents described in
  [Packaging and publication boundary](SKILL.md#packaging-and-publication-boundary),
  not the whole project tree. Exclude `_build/`, `_brief/`, `_samples/`, caches
  and task outputs by default. For explicitly included sample dependencies,
  preserve their paths and filenames without adding parent wrapper folders.
- Ask recipients to use **Extract All** with a short destination such as
  `C:\FP`, or another short writable folder outside a deeply nested Downloads
  or OneDrive location. Open the extracted folder in VS Code.
- If the ZIP contains the `fabric-plan-skill` folder itself, extracting
  it into `C:\FP` is also fine; avoid additional wrapper folders.
- If Explorer still reports the error, use 7-Zip to extract into the same short
  destination. Do not rename GUID folders or delete `writeback.json` to work
  around the error, because that can break native samples.

## How to work in this session

Use the system default browser when opening reports, links or other
browser-based resources for inspection and validation, not as an authoring
fallback.

1. **Use the skill on real work.** Help the user create or refine an actual
   application. Gather missing business requirements, route each outcome to its
   guide and execution path, and respect authorization gates before live writes.
2. **Learn from the report.** Identify incorrect guidance, missing information,
   unsupported assumptions, and gaps exposed by report creation or testing.
   Distinguish a report-specific configuration issue from a reusable skill gap.
3. **Apply corrections shared in chat.** When the user provides a correction
   or asks you to incorporate a finding, inspect the relevant skill guidance
   and supporting evidence, then update the skill files yourself. Do not ask
   the user to edit the files manually.
4. **Keep linked guidance consistent.** Trace the affected references and
   update all relevant feature documentation, indexes, examples, and validation
   rules together where needed. Do not stop at fixing only the report or one
   isolated reference. Preserve unrelated content and the existing structure.
5. **Verify the learning.** Run relevant existing checks and, where access is
   available and the user's latest validation instruction permits it, retest
   the corrected behavior in Fabric Plan. Required offline safety checks,
   baseline/identity/ETag reads and asynchronous completion remain necessary
   even when post-save validation is skipped. Distinguish construction, saved
   readback, visible rendering, calculations, input edits and propagation.
   Report pending required delivery phases as incomplete; generated files or
   screenshots alone do not prove runtime success.
6. **Repeat for each report.** Treat every report as an opportunity to improve
   the skill without generalizing report-specific choices into universal rules.

## Handling missing features

When the user reports a missing feature, establish:

- The product/module and visual type.
- The feature name and exact UI location, for example,
  **Intelligence Sheet > Matrix > [menu or setting]**.
- What the feature does, how it is configured, and the expected behavior.
- Relevant bundled documentation, public API contracts or an authorized Fabric
  Plan example that uses it.
- Relevant screenshots or an approved native report definition, if available.

Use the supplied references as evidence and follow the skill's native-sample
requirements. Screenshots establish presentation and UI location, not the
underlying JSON encoding. Do not invent properties, bindings, or behavior.
If evidence is insufficient, ask for the specific missing detail and keep the
finding explicitly unverified rather than documenting a guess as fact.

Place confirmed guidance under the correct product/module and visual or feature
area, and connect it to the relevant navigation. If the feature belongs to an
unsupported profile or lies outside the skill, explain the exact boundary
instead of enabling unsupported behavior or applying one module's contracts to
another. Check documented separate phases before declaring a feature missing.

Promote reusable fixes into the shared bundled builder and focused regression
tests where applicable, not just task-local scripts. Update discoverable guides
and examples, and verify package-only execution without cached reports or chat
history before claiming a reusable fix is complete.

## Handoff before ending the session

Provide a concise summary containing:

- The report or use case and features exercised.
- Corrections and missing features identified.
- Skill files updated and the evidence supporting those changes.
- Checks and runtime tests performed, including any limitations.
- For live work, the native artifact link, operation status and coverage ledger;
  distinguish completed, pending, unsupported and unverified outcomes.
- Open questions and the next useful test.

Keep the updated skill files as the persistent source of reusable knowledge.
Do not rely on chat history alone to carry confirmed corrections into the next
session.

Do not carry credentials, live target identities or task-specific business data
into reusable skill guidance or release packages.
