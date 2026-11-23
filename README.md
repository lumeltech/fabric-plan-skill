# Fabric Planning Skills

<p align="center">
  <a href="https://lumel.com/">
    <img src="https://lumel.com/wp-content/uploads/lumel-orange.svg" alt="Lumel" width="180">
  </a>
</p>

> **Lumel project** · [Canonical repository](https://github.com/lumeltech/fabric-plan-skill) · [Fabric Plan documentation](https://docs.fabricplan.com/) · [Lumel](https://lumel.com/)

An agent skill for building and maintaining **Microsoft Fabric Plan** applications
from business requirements and a Power BI semantic model. An AI coding agent
(GitHub Copilot, Claude Code, Codex or any client that supports skills) reads
`SKILL.md`, routes the request to the right guide, and uses the bundled Python
runtime to construct, validate and deploy Plan content.

> This is a Lumel-maintained community project, not an official Microsoft
> product. The repository uses public Fabric APIs for the Plan lifecycle. New
> reports set sheet visibility in the initial public create request.
> Role-specific Home layout is not supported by this skill.

In v50, the public Create Plan request places each embedded Planning matrix on its dashboard. The original Planning sheet is hidden in Explorer when a visible dashboard embeds it. Its GUID continues to identify the grid for cross-sheet formulas and From Sheets bindings. For wide dashboards, the default layout puts navigation and slicers on the left, the matrix above the charts, and aligns the bottom edges. Supply the inner Reading viewport dimensions to size the layout for a particular display.

## About Lumel and Fabric Plan

[Lumel](https://lumel.com/) develops planning, business intelligence and
writeback solutions for Microsoft Fabric. This repository is published from the
[Lumel Technologies GitHub organization](https://github.com/lumeltech) as a
community resource for authoring and maintaining Fabric Plan applications.

- [Fabric Plan documentation](https://docs.fabricplan.com/)
- [Fabric Planning Community](https://community.fabricplan.com/) — forums,
  documentation and training
- [Microsoft Fabric Community](https://community.fabric.microsoft.com/) —
  Microsoft's broader Fabric user community
- [Planning in Microsoft Fabric: a shared vision through collaboration with Lumel](https://www.microsoft.com/en-us/microsoft-fabric/blog/2024/12/04/planning-in-microsoft-fabric-a-shared-vision-through-collaboration-with-lumel/)
- [Lumel IBCS resources](https://lumel.com/ibcs/)
 

## Microsoft and Lumel

Microsoft describes its work with Lumel as a collaboration that brings
enterprise performance management for planning applications to Power BI and
Microsoft Fabric. Lumel subsequently announced that Planning in Fabric IQ was
co-engineered as a native first-party experience and made available in public
preview.

<p align="center">
  <a href="https://www.microsoft.com/en-us/microsoft-fabric/blog/2024/12/04/planning-in-microsoft-fabric-a-shared-vision-through-collaboration-with-lumel/">
    <img src="https://www.microsoft.com/en-us/microsoft-fabric/blog/wp-content/uploads/2024/12/Fabric_392264_Blog_241203.jpg" alt="Microsoft and Lumel collaboration for enterprise planning in Microsoft Fabric" width="720">
  </a>
</p>

- Read Microsoft's announcement:
  [Planning in Microsoft Fabric: A shared vision through collaboration with Lumel](https://www.microsoft.com/en-us/microsoft-fabric/blog/2024/12/04/planning-in-microsoft-fabric-a-shared-vision-through-collaboration-with-lumel/)
- Read Lumel's first-party alliance announcement:
  [Enterprise Planning in Microsoft Fabric](https://lumel.com/newsroom/lumel-microsoft-strategic-first-party-alliance-fabric-planning/)

These links describe the Microsoft–Lumel collaboration for the Fabric planning
capability. They do not imply that Microsoft endorses, publishes or maintains
this skill repository. Microsoft, Microsoft Fabric, Lumel and related product
names and images are the property of their respective owners.

## Stay connected

[Lumel on GitHub](https://github.com/lumeltech) ·
[LinkedIn](https://www.linkedin.com/company/lumeltech/) ·
[X](https://x.com/lumel_tech) ·
[YouTube](https://www.youtube.com/@LumelTechnologies)

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
| Plan lifecycle | Discover workspaces and models, create a new Plan, export and update its definition, deploy and read back |
| Planning sheets | Input measures (number, text, checkbox, person, select, date), formulas and formula equality, forecasts and time intelligence, roll-forward balances, totals, measure hierarchies, anchors for business-grain assumptions, measure-weighted allocation rules, numeric input constraints |
| Intelligence dashboards | Page Navigators, integrated variance charts, chart visual filters, Matrix formatting, conditional formatting, typography and layout defaults, embedded Planning and PowerTable visuals |
| Home | Home content and business navigation within the public Plan definition |
| PowerTable | Column configuration, lookups and source metadata |
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
python plan.py --help
python plan.py discover "workforce merit salary cost"
python plan.py usecase list
python plan.py validate --help
```

`discover` is read-only. Local builds write files, not workspace items. Commands that write to a
workspace need an explicit destination file (see
`examples/five-usecases/`) and `FABRIC_TOKEN`.

## Repository layout

| Path | Contents |
|---|---|
| `SKILL.md` | Agent instructions and routing |
| `plan.py` | Command-line entry point |
| `runtime/` | Constructors, codecs, validators and public Fabric API client |
| `references/` | Feature guides and contracts, loaded on demand |
| `schemas/` | Plan definition part schemas |
| `examples/` | Request and destination examples, including the five use cases |
| `fixtures/` | Test and reference fixtures |
| `tools/` | Node helpers (payload codec, HTTP, visual placement) |
| `vendor/lzutf8/` | Third-party LZ-UTF8 library (MIT) |
| `tests/` | Offline unit tests |

For dashboards embedded in a Plan, use the direct [planning references](SKILL.md#planning-references).
The standalone Intelligence reporting library is not distributed with this skill.

## Tests

The tests are offline and need no credentials:

```text
python -m unittest discover tests
```

## Safety

- Workspace writes need an explicit destination file that names the workspace,
  the allowed public hosts and `authorizedMutation`; local commands never write.
- Operations without a supported public route are out of scope.
- Credentials come only from environment variables; none are stored.
- Do not commit exported Plan definitions that contain customer data.
- Do not add task briefs, native exports, handoff notes or third-party material
  without verified redistribution rights. Removing a tracked file does not
  remove it from earlier Git history.

## License

MIT; see [LICENSE](LICENSE). `vendor/lzutf8` is Copyright (c) 2014-2018 Rotem Dan,
under the MIT license in `vendor/lzutf8/LICENSE.txt`.

Microsoft and Microsoft Fabric are trademarks of the Microsoft group of companies.
