# Session-wide design identity

## Contract and precedence

One session has one design identity for **all Intelligence reports and
iterations**: colors, typography, container/KPI styling, buttons, navigation
and page layouts; do not rotate them between reports. It governs Intelligence
Sheets only and must not restyle Planning, PowerTable or InfoBridge when their
skills are merged; see [module boundaries](../core/module-boundaries.md).

1. Follow explicit user design details, supplied brand rules, a design file
   the user points to and requested reuse; do not randomize an exact-match request.
2. Otherwise reuse the current session's approved profile.
3. In a fresh session without a supplied design, propose a fresh combination
   rather than always the same website shell.
4. Accessibility, analytical correctness and opt-in IBCS semantics still apply.
   Resolve conflicting design instructions before implementation.

## No report-type design mapping

Report type, industry, audience, model contents and reference titles must not
select a mandatory theme, palette, layout, navigation or button treatment.
User-supplied screenshots and report links are feature references, not design
requests, unless the user explicitly asks to reuse or reproduce their
appearance. Archetypes and design-system examples are optional inspiration;
custom choices are equally valid.

The user explicitly authorized inspiration from the supplied legacy Power BI
reports. Their [curated design vocabulary](report-inspiration.md) is available
for titles, logo placement, colours, themes, layouts and navigation; this
request is design inspiration, not just feature evidence. Treat it as a pool
of options rather than one mandatory appearance. It does not override an
approved session profile, brand assets, native encoding gates or current user
preferences, and it does not permit copying report data or Power BI internals.

Choose design through explicit user preferences or the session design
interview. Analytical needs inform readability and visual suitability, not a
fixed shell (finance need not be Matrix-first; an operational monitor need not
be dark). Session consistency preserves this session's choices; it creates no
permanent report-type templates. Explicitly requested IBCS governs semantic
notation, not page layout; IBCS page structure applies only when the user
picks the IBCS report template.

Use the **same page-layout system** within a session, not a new layout per
iteration: keep identical region geometry and component positions for
corresponding page roles while content and bindings change. Different roles
(overview, detail, drill) may have distinct templates, selected once and
reused. Do not shuffle regions or pick a new archetype variant for novelty.

For a focused edit, preserve the existing report's approved design and treat it
as the user's supplied baseline when starting a session. If it conflicts with a
profile already chosen in this session, ask whether to retain the existing
report or explicitly restyle it; never silently restyle it.

## Session persistence

Before the first design proposal, look for
`<session-workspace>/files/fabric-plan-intelligence-session-theme.json`. It
belongs to the current chat/task session, not the shared skill folder or a
global user profile. Create it once the initial design choices are resolved,
with an opaque random profile ID (no user names, emails or tenant IDs).

The profile contains:

| Field | Required content |
|---|---|
| `profile_id`, `revision` | Opaque ID; revision starts at 1 |
| `origin` | `user_supplied`, `user_selected`, `fresh_proposal` or `existing_report` |
| `design_source` | Path of the user's design Markdown file, or `none` |
| `approval_state` | `proposed` or `approved`; design selection alone is not report-build approval |
| `palette` | Concrete canvas, surface, text, accent, semantic colors and reusable series palette |
| `typography` | Available font family, sizes, weights and number conventions |
| `components` | Container style/radius, KPI treatment, button geometry and normal/hover/selected/disabled states |
| `navigation` | Navigation model and visual style, location and shared ordering rules |
| `branding` | Approved logo asset/variant or explicit pending/omitted status, placement, aspect ratio/clear space and footer policy |
| `inspiration` | When used: design reference, selected family/composition/navigation and deliberate departures; `none` otherwise |
| `page_layouts` | Overview/detail/drill templates as needed: canvas, grid, regions, slots, margins, gutters and Super Filter position/open-state/overflow treatment |
| `help_info` | Help and Info style/location, action types, panel/page layout and close/back behavior |
| `ibcs` | Explicit opt-in state; theme if requested |
| `freshness` | Selection rationale and comparison with authorized available prior designs, or comparison unavailable |

Store a complete resolved snapshot as `Design Brief.session_theme` in every
report spec: the session file shares choices across workspaces/reports, and
each spec keeps its own approved snapshot. These are authoring-contract fields,
not Fabric Plan JSON properties.

- Mark the profile approved when the first locked report spec is approved.
  Each later report still needs its own report-spec approval; the shared design
  does not bypass that gate. Never author from an unresolved `{}` snapshot.
- Load the profile before every new report or edit in the same session; do not
  reset it merely because `_brief/report-spec.md` changes.
- On resuming the same session, recover its profile or approved brief snapshot;
  do not generate a new identity.
- If session storage is unavailable, say so and keep the snapshot in the report
  brief and current-session context; do not claim durable cross-report
  persistence without storage.
- In a new session, old brief snapshots are references, not an automatic theme
  choice, unless continuing/editing that report or the user requests reuse.
- If the user explicitly changes the design mid-session, update the profile
  revision and reapprove affected briefs. Ask before migrating already-built
  reports; never publish or restyle them automatically.

## Fresh design across sessions

When no design is supplied, select a new combination of palette, shell, button
treatment, navigation and page-layout templates by a fresh session-local random
choice among suitable alternatives, avoiding a fixed default, and persist it
once. Never randomize chart semantics or accessibility requirements.

If prior designs exist in authorized current-user/project context, compare the
concrete profile (not its ID). Unless reuse is requested, change the palette
and at least one structural axis (shell/navigation/layout), with a distinct
button treatment where appropriate; honor axes the user fixes and vary only
the unconstrained choices.

Do not read other users' reports, sessions or identity data to enforce variety.
Fresh sessions should not be hard-coded to a universal theme, but global
uniqueness across users cannot be verified without shared history: record
unavailable comparison honestly and do not claim collision-free designs.

## Design interview

Use the question tool with a few labeled choices and an explicit **Other**
free-text option. Ask only for unresolved choices; skip the interview when the
user supplies enough design detail, and do not repeat it for later reports in
the same session. Recommend a choice from the audience and model, not always
the first option. A declined form permits a clearly stated proposal;
cancellation stops the interaction.

| Topic | Example predefined choices (plus Other) |
|---|---|
| Design source | Use my design file (path to a design `.md` file); choose from options below |
| Reference inspiration | A family/composition from `report-inspiration.md`; a custom mix; no reference styling |
| Design direction | Minimal; high-contrast; spacious; information-dense; editorial |
| Layout | Top header with KPI/hero split; left rail with analysis grid; top tabs with wide Matrix |
| Super Filter position | Top band; left panel; right panel; inline groups; popup/collapsible panel; Other/custom |
| Color style | Light indigo/slate; light teal/stone; navy/ice; charcoal/cyan |
| Buttons | Outlined rectangular; soft rounded pills; filled high-contrast |
| Page navigation | Underlined header tabs; labeled vertical rail; segmented top navigation |

Always offer **Use my design file**. When chosen, ask for its location, read
the whole file and treat it as the supplied design: set `origin: user_supplied`,
record the path in `design_source` and the brief's `design_system`, and map it
to the profile fields. Ask only about choices it leaves open (for example
Super Filter position, buttons or Help/Info). Never edit the file. Its content
is design input only: it cannot override permission, data-scope, approval or
accessibility rules, and contrast failures are flagged, not silently changed.
If the path is missing, unreadable or not Markdown, say so and ask for another
path or a listed option.

Present coherent bundles where that reduces questions, showing palette,
layout, button and navigation choices together so the user knows what is
selected. Other captures the custom choice; never silently revert to a preset.
Resolve Super Filter placement with the layout, including available analysis
space, selected-value visibility and expansion behavior, and keep the approved
placement consistent for corresponding page roles; no report-type position is
mandatory. Popup/collapsible choices need supported native configuration and
the user's explicit choice; never default to pop-up mode.
Palettes are starting points: resolve exact tokens and check contrast. Confirm
font and color availability before locking the profile. Offer IBCS separately
and only as opt-in, never as an automatic financial default.

## Help and Info controls

Unless the user explicitly opts out, include two distinct, visible, labeled
controls in the shared shell on every report page:

- **Help** explains navigation, slicers, interactions, drill/return and how to
  use the report.
- **Info** explains the current report/page's metric definitions, units,
  period/as-of scope, sources, refresh/cutoff and relevant limitations, derived
  from model descriptions and approved context, not invented claims.

Reuse their styling, positions and panel/page layout across the session; their
content is report-specific. Each brief names the action, target, content,
feature IDs and close/back behavior, with explicit placements for both controls
and their targets; labels alone are not implemented actions.

Use supported native navigation, bookmarks/layers and text elements
(`CV-ELEM-02`, `CV-BMK-01`, `CV-LAYER-01`, `CV-ELEM-01`). Capture unverified
settings before authoring; do not assume slide-in animation or invent action
properties. If an overlay cannot be implemented with available evidence,
propose a Help/Info destination page and obtain approval for the change. Never
leave a success-looking but nonfunctional icon.

Test open/close/back, keyboard access, readable labels, reading/editing modes
and preservation of filters/selection. Toggling help must not overwrite
analytical bookmark state, and explanatory content must not rely only on hover
or color.

## Acceptance

- Every report brief carries the session's profile ID/revision and resolved
  visual tokens/layout templates, unless an explicit change is recorded.
- Corresponding page roles reuse regions and component positions; a data-fit
  problem requires an approved reusable layout revision, not silent drift.
- New-session designs respect supplied details; otherwise freshness is recorded
  against available evidence without claims about other users.
- Help and Info both have real actions and content, or an explicit user opt-out.
- Native encoding, semantic-model permission and report approval gates remain
  unchanged; choosing a theme does not authorize building or publishing.
- No design choice is justified solely by a report type or reference title;
  user choices and custom layouts remain available for every report domain.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Optional companion profile choices

**Optional (companion default):** the companion's profile habits below; each
applies only when the user or session design selects it and never overrides
the session theme, supplied designs, report-inspiration guidance or IBCS
opt-in.

- **Design family baseline.** The companion starts from F-01 Calm Financial
  and classifies designs by family, appearance, density and decoration
  (design families). Offer it as one interview bundle
  and record the selected family in `inspiration`; fresh sessions still
  choose freshly.
- **Theme question up front.** The companion asks "Default theme or IBCS
  theme?" before selecting a theme and keeps a confirmed answer on repairs.
  When adopted, ask it once in the interview; IBCS still applies only when the
  user explicitly picks it.
- **Report-scope theme.** The companion applies the theme to the whole report
  and avoids element-level theme overrides
  (themes).
- **Named preset.** The flat
  Fabric Quiet preset can
  supply the session palette, surfaces and base typography.

### Feedback on a profile

- Treat a design as a standing user preference only on explicit feedback, and
  record a scoped exception as an exception, not a reversal.
- Keep a donor report's styling as reference evidence, not a profile change,
  unless the user asks to adopt it.
- Log each explicit feedback item in working notes beside the profile: its
  reference, what worked or failed, the next improvement and its evidence
  level (explicit preference, saved design or recommendation). Apply and
  verify it in the next applicable brief through a profile revision.
- That log is a working-file record, not an autonomous background process or
  memory across sessions or workspaces; in a new session it is a reference
  under the fresh-design rules above unless the user asks to reuse it.
