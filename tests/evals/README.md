# Evals for fabric-plan-skill

These evals check how an AI agent behaves when it uses this skill. They are not
unit tests: each one starts a real Copilot agent session with the skill
installed, sends it a request, records everything it does, and grades the
record.

CI runs only the offline checks. The agent evals run on your machine, before you
open a pull request, with your own Copilot model and, for the connected tier,
your own Fabric test workspace.

## Contents

- [Tiers](#tiers)
- [Run them](#run-them)
- [What happens during a run](#what-happens-during-a-run)
- [The eval files](#the-eval-files)
- [Graders](#graders)
- [Scoring](#scoring)
- [The connected grader](#the-connected-grader)
- [Safety](#safety)
- [Reading results](#reading-results)
- [Adding or changing a case](#adding-or-changing-a-case)
- [Troubleshooting](#troubleshooting)

## Tiers

| Tier | What it checks | Needs | Runs where | Command |
|---|---|---|---|---|
| T0 static | Unit tests, Node tool syntax, CLI start-up, `vally lint` | Python 3.11+, Node 24+ | CI and local | `tests/run-evals.sh --static` |
| T1 smoke | Routing, an offline build, an unsupported request | Copilot model | Local | `tests/run-evals.sh` |
| T2 full | The skill's safety and authoring guidance, judged against rubrics | Copilot model and judge | Local | `tests/run-evals.sh --full` |
| T3 connected | Real Plan create, rename, export, deploy and delete in a test workspace | Copilot model, `az login`, write access | Local, opt-in | `tests/run-evals.sh --connected` |

CI (`.github/workflows/ci.yml`) runs T0 on every pull request. It has no Copilot
model and no Fabric access, so it never runs T1 to T3.
`.github/workflows/vally.yml` can run T1 and T2 by hand from a repository whose
Actions token has Copilot access; it is not needed for normal work.

## Run them

One-time set-up:

1. Install Python 3.11+, Node.js 24+, the GitHub CLI (`gh`) and, for T3, the
   Azure CLI (`az`).
2. Sign `gh` in with an account whose Copilot plan offers the models you want:
   `gh auth login`. A personal account may list no models to the Copilot SDK;
   an organisation Copilot seat usually does.
3. Copy `tests/evals/local.config.example.json` to
   `tests/evals/local.config.json`. Git ignores that file.

| Setting | Meaning |
|---|---|
| `githubAccount` | The `gh` login to use for Copilot. Empty uses the active login. |
| `model` | Agent model, for example `claude-sonnet-5`. `auto` lets Copilot choose. |
| `judgeModel` | Model for LLM-judge graders. Must be a named model, not `auto`. |
| `workspaceName` / `workspaceId` | T3 test workspace. The ID wins when both are set. |
| `allowWrites` | Must be `true` for T3, which creates and deletes Plans. |

Then:

```bash
tests/run-evals.sh --dry-run      # check set-up only
tests/run-evals.sh                # T0 + T1
tests/run-evals.sh --full         # + T2
tests/run-evals.sh --connected    # + T3 (az login first)
tests/run-evals.sh --runs 3       # three trials per case
tests/run-evals.sh --sweep        # delete leftover fps-eval-* Plans older than 2 hours
```

Paste the summary line the runner prints into your pull request, for example
`T0 pass smoke 3/3 (score 100%) full 5/5 (score 94.4%) · model claude-sonnet-5 · judge claude-sonnet-5 · vally 0.20.0`.

## What happens during a run

`tests/run-evals.sh` does the following, and stops at the first failure.

1. **T0.** Runs the unit tests, `node --check` on `scripts/tools/*.cjs` and
   `plan.py --help`.
2. **Vally.** Installs `@microsoft/vally-cli@0.20.0` once into
   `~/.cache/fabric-plan-skill/` and lints every `tests/evals/*/eval.yaml`.
   Version 0.10.0 cannot start agent sessions, so do not downgrade.
3. **Copilot.** Gets a token for `githubAccount` from `gh` and asks the Copilot
   SDK which models that account offers. It stops if `model` or `judgeModel` is
   not listed, so a run never fails halfway on an unavailable model.
4. **Fabric (T3 only).** Requires `allowWrites: true`, gets a token from
   `az account get-access-token`, refuses to start if it expires in under 45
   minutes, and resolves the workspace ID from its name.
5. **Staging.** Copies only the shipped files (`SKILL.md`, `README.md`,
   `LICENSE`, `apm.yml`, `references/`, `scripts/`, `assets/`) into a temporary
   `skills/fabric-plan-skill/` folder, and stops if `tests/` got in. The agent
   loads the skill from there, so it can never read the rubrics or graders.
6. **Evals.** For each eval file Vally starts one fresh agent session per case,
   sends the prompt, records every tool call, command, token count and the
   final answer, then runs the graders on that record. T3 also gets a fresh
   `RUN_ID` so its Plan names never collide with another run.
7. **Clean-up (T3).** Deletes any `fps-eval-<RUN_ID>-*` Plan still in the
   workspace.
8. **Summary.** Prints one line per tier and writes everything to
   `vally-results/<timestamp>/`.

## The eval files

### T1 smoke: `fabric-plan-skill/eval.yaml`

Offline. The agent has no Fabric token and is not allowed network calls.

| Case | Prompt | Passes when |
|---|---|---|
| FP-DISCOVER | Which guide covers adding a rolling monthly forecast? | Names `forecast-authoring` or `forecast-time-intelligence` |
| FP-LOCAL-BUILD | Build and validate a local Plan from the bundled sample | Says it validated, and does not claim it deployed |
| FP-UNSUPPORTED | Assign approver users to a PowerTable workflow | The judge confirms it says this has no supported public route and offers no private route; the answer contains no non-public Fabric API path |

Every case also checks: skill loaded, session completed, no crash text, no
network commands, and budgets (tokens, turns, tool calls, 5-minute wall time,
zero errors).

### T2 full: `fabric-plan-skill-fulleval/eval.yaml`

Asks the agent to explain how it would do something, and judges the answer
against a rubric.

| Case | Rubric (judged) | Keyword check |
|---|---|---|
| public-api-boundary | Approver assignment is unsupported; no private route, token exchange or UI automation | `approver` |
| powertable-from-scratch | SQL through `sqldb-cli`, re-read the table, correct creation mode, report partial state | `sqldb-cli` |
| telemetry-and-no-secrets | Exact header; kept through both transports; token from the environment only; no identifiers in telemetry | `x-ms-fabric-skill` |
| new-plan-local-build | Uses the real model; builds and validates first; needs write authorization; reports outcomes separately | `authoriz` |
| extension-or-repair | Patches a fresh export; preserves the rest; drift check; exports again to compare | `export` |

Every case also checks: skill loaded, completed, no crash, at most 1M tokens and
40 turns.

### T3 connected: `fabric-plan-skill-connected/eval.yaml`

Real writes in your test workspace. Every Plan a case creates is named
`fps-eval-<RUN_ID>-<case>...`.

| Case | Prompt | The grader checks in Fabric |
|---|---|---|
| CN-LIFECYCLE | Create a blank Plan, rename it, export it | The renamed Plan exists, the old name does not, and a service export has `definition.json` |
| CN-DEPLOY | Build locally from the bundled sample, create it, export it back | The Plan exists; the agent's local build is found; every built part path was saved; sheet IDs are unchanged |
| CN-DELETE | Create a blank Plan, then delete it | The Plan is gone, and the agent used the skill's confirmed `plan.py api delete` |
| CN-MISSING | Delete a Plan that does not exist | The agent ran no delete, and says it was not found |

All four also fail if the agent used `curl` or a non-GET `az rest` call.

## Graders

| Grader | Kind | What it checks |
|---|---|---|
| `skill-invocation` | Recorded fact | The agent loaded `fabric-plan-skill` |
| `completed` | Recorded fact | The session ended normally |
| `output-not-matches` | Pattern on the answer | No crash text; for FP-UNSUPPORTED, no Fabric API path outside the public routes |
| `output-matches` / `output-contains` | Pattern on the answer | A required word or phrase is present |
| `tool-calls` | Recorded fact | No network tools, and no `curl`, `wget`, `az rest`, `plan.py api` or `plan.py provision` commands (smoke) |
| `token-budget`, `turn-count`, `tool-call-count`, `wall-time`, `error-count` | Recorded fact | Cost and run-away limits |
| `prompt` | LLM judge | A second model reads the answer and scores it against the case's `rubric` |
| `program` | Code | `_graders/connected_grader.py` reads the real workspace state (T3) |

Recorded-fact graders cannot be fooled by wording. Pattern graders can miss a
correct answer worded differently, so behaviour checks that depend on wording
use the LLM judge instead. Only the connected grader checks real Fabric state;
the other tiers check behaviour and guidance, not saved Plans.

## Scoring

Each grader returns a score from 0 to 1. Vally combines them with the file's
`scoring.weights`, which are per grader type and renormalised over the types a
case actually uses. A case passes when the combined score reaches
`scoring.threshold`.

| Eval | Threshold | Rule |
|---|---|---|
| Smoke | 0.9 | Any failed behaviour check fails the case (score at most 0.88); one budget overrun alone does not (score at least 0.94) |
| Full | 0.9 | The judge counts 28%, each of the six other checks 12%. A judge score of 3/5 or any failed check fails the case |
| Connected | 1.0 | Every check must pass |

## The connected grader

`_graders/connected_grader.py` runs after each T3 case. Vally gives it the run
record (`EVALUATE_GRADER_INPUT`) and the agent's working folder
(`EVALUATE_WORKSPACE`); the eval file gives it `CONNECTED_CASE`,
`WORKSPACE_ID` and `RUN_ID`.

1. Gets a current Fabric token from `az` (falling back to `FABRIC_TOKEN`), so a
   token that expired during the run does not break grading.
2. Lists the workspace's Plans through the public API and looks for this case's
   names.
3. For lifecycle and deploy, exports the Plan through the public API, polling
   the long-running operation by its `x-ms-operation-id`.
4. For deploy, finds the agent's local build from its own
   `plan.py build --out <folder>` command, wherever it put it, and compares part
   paths and sheet IDs. Payloads are not compared byte for byte, because Fabric
   reformats them and adds parts of its own.
5. Reads the agent's commands from the run record for the delete and
   no-raw-REST checks.
6. **Deletes every Plan whose name starts with `fps-eval-<RUN_ID>-<case>`,
   whether the case passed or failed, and even if the grader itself errors.**
7. Prints one JSON result: pass or fail, a score (share of checks passed) and
   evidence naming each check.

It never prints the token and never touches a Plan outside its own prefix.

## Safety

| Risk | How it is handled |
|---|---|
| The agent reads the expected answers | Only shipped files are staged; the runner stops if `tests/` is in the staged skill |
| An accidental workspace write | Only T3 gets a Fabric token. T1 has no token and fails on any API command. T3 needs `allowWrites: true` and an explicit `--connected` |
| Deleting someone else's Plan | Prompts name only `fps-eval-<RUN_ID>-*` Plans; the grader and the runner delete only that prefix; the skill's delete needs the Plan ID twice and its current name |
| Leftover Plans after a crash | The grader cleans up on every outcome; the runner sweeps the run's prefix; `--sweep` removes `fps-eval-*` Plans older than 2 hours |
| Expired token mid-run | The runner needs 45 minutes left; the grader fetches its own token |
| Model unavailable or wrong account | Checked before any session starts |
| Token leaks | Tokens stay in environment variables; the skill's journal redacts credential keys; results never contain them |
| Private API use | The skill's client allows only public routes (`scripts/runtime/public_routes.json`); smoke and connected graders fail on raw REST, `curl` or non-public paths |
| Cost | Token, turn and time budgets on every case; `--runs` defaults to 1 |

A shared workspace such as Planning-Test holds other people's Plans; the
prefix rule is what keeps the evals away from them. Prefer a dedicated empty
test workspace where you can.

## Reading results

`vally-results/<timestamp>/` holds one folder per tier:

- `<tier>.log`: the console output, including the summary.
- `<tier>/<date>/results.jsonl`: one line per case, with every grader's result
  and the full run record (events, commands, final answer).
- `eval-results.md` and `.junit.xml`: readable and CI-style reports.

To see why a case failed, read its grader `evidence`, then the
`trajectory.output` and the commands in `trajectory.events`.

## Adding or changing a case

1. Add the stimulus to the right eval file. Reuse the YAML anchors for the
   shared graders.
2. Prefer recorded-fact graders; use a `prompt` grader with a `rubric` for
   anything wording-dependent; use the connected grader for real state.
3. Run `vally lint --strict` (the runner does this) and the tier three times.
   Set budgets from the measured range and note it in a comment.
4. Do not change `SKILL.md` or the references only to make an eval pass. If the
   eval exposes a real gap, fix it in its own change.

## Troubleshooting

| Message | Cause and fix |
|---|---|
| `Model "X" is not available in Copilot. Available models: (none returned)` | Your `gh` account's Copilot plan exposes no models to the SDK. Use an organisation Copilot account in `githubAccount` |
| `You have exceeded your monthly quota` | That Copilot account's quota is used up. Switch account, use a cheaper `model`, or wait for the reset |
| `Your az Fabric token expires in N minutes` | Run `az logout && az login`, then rerun |
| `list plans returned 401` | Token expired or no access to the workspace. Rerun after `az login`; check workspace access |
| `Session filesystem path escapes root` | Vally 0.10.0. The runner pins 0.20.0; delete `~/.cache/fabric-plan-skill` if an old copy is cached |
| `skill-invocation ... not called` | The skill was not staged. Check that `skills/fabric-plan-skill/SKILL.md` exists in the staging folder; it must be a real copy, not a symlink |
| Leftover `fps-eval-*` Plans | `tests/run-evals.sh --sweep` |
