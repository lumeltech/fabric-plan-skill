# Fabric Planning Skills

> [Canonical repository](https://github.com/lumeltech/fabric-plan-skill) · [Fabric Plan documentation](https://docs.fabricplan.com/)

An agent skill for building and maintaining **Microsoft Fabric Plan** applications
from business requirements and a Power BI semantic model. An AI coding agent
(GitHub Copilot, Claude Code, Codex or any client that supports skills) reads
`SKILL.md`, routes the request to the right guide, and uses the bundled Python
runtime to construct, validate and deploy Plan content.

> This is a Lumel-maintained community project, not an official Microsoft
> product. The repository uses only public Fabric APIs for the Plan lifecycle. New
> reports set sheet visibility in the initial public create request.
> Role-specific Home layout is not supported by this skill.

The public Create Plan request places each embedded Planning matrix on its dashboard. The original Planning sheet is hidden in Explorer when a visible dashboard embeds it. Its GUID continues to identify the grid for cross-sheet formulas and From Sheets bindings. For wide dashboards, the default layout puts navigation and slicers on the left, the matrix above the charts, and aligns the bottom edges. Supply the inner Reading viewport dimensions to size the layout for a particular display.

## Release layout

Use this repository root as the package-layout root, not as the ZIP's full
contents. Follow the [packaging and publication boundary](SKILL.md#packaging-and-publication-boundary)
and include required instructions, runtime resources and selected
reusable examples directly at the ZIP root. Use reviewed, tracked files only;
exclude private working material, native exports, caches and task-specific outputs.

Publishing a Fabric Plan is separate: send only its validated definition and
required report assets through the documented workflow, never the repository
folder or `_build/`.

## What it does

| Area | Coverage |
|---|---|
| Plan lifecycle | Discover workspaces and models, create a new Plan, export and update its definition, deploy and read back; list, inspect, rename and delete Plans |
| Planning sheets | Input measures (number, text, checkbox, person, select, date), formulas and formula equality, forecasts and time intelligence, roll-forward balances, totals, measure hierarchies, anchors for business-grain assumptions, measure-weighted allocation rules, numeric input constraints |
| Intelligence dashboards | Page Navigators, integrated variance charts, chart visual filters, Matrix formatting, conditional formatting, typography and layout defaults, embedded Planning and PowerTable visuals |
| Home | Home content and business navigation within the public Plan definition |
| PowerTable | Existing or SQL-prepared tables with product column defaults, lookups, Row access, Forms and Automations; approver-user assignment has no public route |
| Connected planning | InfoBridge sources, queries and mappings, Planning-source identity, From Sheets bindings |
| Data sources | Semantic-model bindings, Fabric SQL and OneLake (From Sheets and From Queries) |
| Dimensions | Dimension ID mapping, leaf keys and native XXH3 dimension hashing |
| Checks and repair | Definition validation, import-contract checks, layout and presentation audits, formatting and property repair that preserves IDs and stored values |
| Business recipes | Five local construction examples (below); building a recipe does not verify live behavior |

### Business use cases

| Case | Request | Result |
|---|---|---|
| `01-sales-targets` | Monthly regional sales targets from prior-year sales, flag shortfalls | 1 Planning sheet, 1 dashboard |
| `02-workforce-merit` | Employee merit from 0% to 15% with salary cost impact | 1 Planning sheet, 1 dashboard |
| `03-expense-budget` | Expense budget with inflation, adjustments and monthly explanations | 1 Planning sheet, 1 dashboard |
| `04-rolling-review` | Monthly sales forecast rolled into a quarterly review with commentary | 2 Planning sheets, 2 dashboards |
| `05-currency-risk` | Local estimates, risk and FX adjustments, quarterly executive outlook | 3 Planning sheets, 3 dashboards |

## Requirements

- Python 3.11 or later. The runtime uses only the standard library.
- Node.js 24 or later, for the bundled compressed-payload and HTTPS adapters. Set
  `FABRIC_PLAN_NODE` (and on managed Windows, `FABRIC_PLAN_HTTP_NODE`) to your Node
  executable when it is not on `PATH`.
- A Fabric workspace on a capacity that supports Plan, a Power BI semantic model,
  and permission to create or edit Plan items.
- For live operations, an access token in the `FABRIC_TOKEN` environment variable
  (for example from `az account get-access-token`). Local and offline commands
  need no token. Never write tokens into files.

## Install

The skill folder is the repository root (`SKILL.md` is at the top), and the skill
is named `fabric-plan-skill`, the same as the repository. Clone it into your
agent's skills directory; the default clone folder already has the right name.

| Client | Location |
|---|---|
| GitHub Copilot | `~/.copilot/skills/fabric-plan-skill` |
| Claude Code | `~/.claude/skills/fabric-plan-skill` (or `.claude/skills/fabric-plan-skill` in a project) |
| Other clients | Follow the client's skill-installation instructions |

For example, for GitHub Copilot:

```text
git clone https://github.com/lumeltech/fabric-plan-skill.git ~/.copilot/skills/fabric-plan-skill
```

Start a new agent session, then ask, for example:

> Use fabric-plan-skill to build a 2026 regional sales target Plan from my Sales model.

## Use the runtime directly

Run from the skill folder:

```text
python scripts/plan.py --help
python scripts/plan.py discover "workforce merit salary cost"
python scripts/plan.py usecase list
python scripts/plan.py validate --help
```

`discover` is read-only. Local builds write files, not workspace items. Commands that write to a
workspace need an explicit destination file (see
`assets/examples/five-usecases/`) and `FABRIC_TOKEN`.

## Repository layout

| Path | Contents |
|---|---|
| `SKILL.md` | Agent instructions and routing |
| `scripts/plan.py` | Command-line entry point |
| `scripts/runtime/` | Constructors, codecs, validators and the public Fabric API client |
| `assets/catalog/` | Machine-readable discovery routing and the ledger of capabilities with no public route |
| `references/` | Feature guides and contracts, loaded on demand |
| `assets/schemas/` | Plan definition part schemas |
| `assets/examples/` | Request and destination examples, including the five use cases |
| `assets/fixtures/` | Test and reference fixtures |
| `scripts/tools/` | Node helpers (payload codec, HTTP, visual placement) |
| `scripts/vendor/lzutf8/` | Third-party LZ-UTF8 library (MIT) |
| `assets/preservation-manifest.json` | Roll-forward preservation data |
| `tests/` | Offline unit tests (`tests/evals/` holds the Vally smoke and full evals) |

For dashboards embedded in a Plan, use the direct [planning references](SKILL.md#planning-references).
The standalone Intelligence reporting library is not distributed with this skill.

## Tests

The tests are offline and need no credentials:

```text
python scripts/plan.py test
```

### Before you open a PR

CI runs only the offline checks. Run the agent evals on your machine with your
own Copilot model (macOS or Linux; needs Python 3.11+, Node.js 24+, `gh`, and
`az` for connected runs):

1. Copy `tests/evals/local.config.example.json` to `tests/evals/local.config.json`
   (git-ignored). Set `githubAccount` to a `gh` login whose Copilot plan lists
   the `model` and `judgeModel`.
2. Run `tests/run-evals.sh --dry-run` to check the setup, then
   `tests/run-evals.sh --full`. Add `--connected` (with `allowWrites: true` and
   `az login`) to run against your test workspace.
3. Paste the summary line it prints into the pull request.

Results are written to `vally-results/` (git-ignored).

How each tier, eval case and grader works, and how the evals stay safe in a
shared workspace: [the evals guide in tests/evals/](tests/evals/).

## Safety

- Workspace writes need an explicit destination file that names the workspace,
  the allowed public hosts and `authorizedMutation`; local commands never write.
  Deleting a Plan also needs `confirmDeletePlanId` and the Plan's current
  display name.
- Operations without a supported public route are out of scope. They are recorded
  with their reason and the public part that remains in
  [`assets/catalog/api-contract-gaps.json`](assets/catalog/api-contract-gaps.json); report them as
  unavailable rather than routing around them.
- Plan item create, rename and delete overlap with the enterprise `plan-cli` skill. Prefer
  `plan-cli` for those item operations when it is installed; `python scripts/plan.py api` keeps
  them available for standalone use under the same authorization and confirmation rules.
- Public Fabric requests include
  `x-ms-fabric-skill: fabric-plan-skill` for skill-level telemetry.
- Credentials come only from environment variables; none are stored.
- Do not commit exported Plan definitions that contain customer data.
- Do not add task briefs, native exports, handoff notes or third-party material
  without verified redistribution rights. Removing a tracked file does not
  remove it from earlier Git history.

## License

MIT; see [LICENSE](LICENSE). `scripts/vendor/lzutf8` is Copyright (c) 2014-2018 Rotem Dan,
under the MIT license in `scripts/vendor/lzutf8/LICENSE.txt`.

### IBCS

The chart conventions in [references/ibcs-charts.md](references/ibcs-charts.md) follow the
International Business Communication Standards (IBCS), the notation also published as
ISO 24896. The standards, their figures and their documents belong to the IBCS Institute;
this skill restates no IBCS document and distributes no IBCS licensing text, and the
implementations in `scripts/runtime/ibcs_charts.py` and `scripts/runtime/ibcs_report.py`
apply the notation's published rules to Microsoft Fabric Plan report parts.

Whether the IBCS standards carry a share-alike or other redistribution condition is **not
verified**. The statements above are attribution, not a licence grant; clear the terms with
the IBCS Institute before redistributing the guide outside this repository.

Microsoft and Microsoft Fabric are trademarks of the Microsoft group of companies. IBCS is a
registered trademark (IBCS®) owned and overseen by HICHERT+FAISST GmbH, IBCS Institute.
Mention of either marks does not imply endorsement or a sponsorship.
