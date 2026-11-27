#!/usr/bin/env bash
# Run the fabric-plan-skill checks and Vally evals locally before opening a PR.
#
#   tests/run-evals.sh                     T0 static checks + T1 smoke eval
#   tests/run-evals.sh --full              ... + T2 full eval
#   tests/run-evals.sh --connected         ... + T3 connected eval (your workspace)
#   tests/run-evals.sh --sweep             delete leftover fps-eval-* Plans older than 2 hours
#   tests/run-evals.sh --static            T0 only (no model, no Copilot)
#   tests/run-evals.sh --runs 3            trials per stimulus
#   tests/run-evals.sh --dry-run           check setup only; run no eval
#
# Settings come from tests/evals/local.config.json (git-ignored; copy
# tests/evals/local.config.example.json). Copilot access uses a GitHub account
# that is already signed in to `gh`; Fabric access uses your `az login` token.
set -euo pipefail

VALLY_VERSION="0.20.0"
SKILL_NAME="fabric-plan-skill"
# Shipped files only (package-manifest.json runtime-required + examples).
SHIPPED="SKILL.md README.md LICENSE apm.yml references scripts assets"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="$ROOT/tests/evals/local.config.json"
VALLY_HOME="${FABRIC_PLAN_VALLY_HOME:-$HOME/.cache/$SKILL_NAME/vally-$VALLY_VERSION}"

full=0; connected=0; sweep=0; static_only=0; dry_run=0; runs=1
while [ $# -gt 0 ]; do
  case "$1" in
    --full) full=1 ;;
    --connected) connected=1 ;;
    --sweep) sweep=1; connected=1 ;;
    --static) static_only=1 ;;
    --dry-run) dry_run=1 ;;
    --runs) runs="$2"; shift ;;
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

step() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
fail() { printf '\033[31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }
cfg() { python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get(sys.argv[2],""))' "$CONFIG" "$1"; }

cd "$ROOT"
summary=()

# ---------------------------------------------------------------- T0 static
step "T0 static checks"
command -v python3 >/dev/null || fail "python3 is required"
command -v node >/dev/null || fail "Node.js is required"
if python3 -c 'import pytest' 2>/dev/null; then
  python3 -m pytest -q tests || fail "unit tests failed"
else
  python3 scripts/plan.py test >/dev/null || fail "unit tests failed (run python3 scripts/plan.py test)"
fi
for f in scripts/tools/*.cjs; do node --check "$f" || fail "syntax error in $f"; done
python3 scripts/plan.py --help >/dev/null || fail "plan.py does not start"
summary+=("T0 pass")

if [ "$static_only" = 1 ]; then
  step "Summary"; echo "${summary[*]}"; exit 0
fi

# ---------------------------------------------------------------- setup
step "Setup"
[ -f "$CONFIG" ] || fail "Create $CONFIG from tests/evals/local.config.example.json"
gh_account="$(cfg githubAccount)"
model="$(cfg model)"; judge="$(cfg judgeModel)"
[ -n "$model" ] && [ -n "$judge" ] || fail "Set model and judgeModel in $CONFIG"

if [ ! -x "$VALLY_HOME/node_modules/.bin/vally" ]; then
  echo "Installing @microsoft/vally-cli@$VALLY_VERSION into $VALLY_HOME"
  mkdir -p "$VALLY_HOME"
  (cd "$VALLY_HOME" && npm install --silent --no-fund --no-audit "@microsoft/vally-cli@$VALLY_VERSION")
fi
VALLY="$VALLY_HOME/node_modules/.bin/vally"

for spec in tests/evals/*/eval.yaml; do
  "$VALLY" lint --eval-spec "$spec" --strict >/dev/null || { "$VALLY" lint --eval-spec "$spec" --strict; fail "lint failed: $spec"; }
done
echo "Eval specs lint clean"

command -v gh >/dev/null || fail "GitHub CLI (gh) is required for Copilot access"
if [ -n "$gh_account" ]; then
  GH_TOKEN="$(gh auth token -u "$gh_account" 2>/dev/null)" || fail "gh has no login for $gh_account (run: gh auth login)"
else
  GH_TOKEN="$(gh auth token 2>/dev/null)" || fail "gh is not signed in (run: gh auth login)"
fi
export GH_TOKEN GITHUB_TOKEN="$GH_TOKEN"

# Vally refuses a model the Copilot runtime does not list; check both up front.
cat > "$VALLY_HOME/list-models.mjs" <<'EOF'
import { CopilotClient } from "@github/copilot-sdk";
const c = new CopilotClient({ gitHubToken: process.env.GH_TOKEN });
try { await c.start(); console.log((await c.listModels()).map((m) => m.id).join("\n")); }
catch (e) { console.error(String(e.message || e).split("\n")[0]); process.exitCode = 1; }
finally { await c.stop().catch(() => {}); }
EOF
models="$(cd "$VALLY_HOME" && node list-models.mjs 2>&1)" || fail "Copilot model lookup failed for ${gh_account:-the active gh account}: $models"
for m in "$model" "$judge"; do
  [ "$m" = auto ] && [ "$m" = "$model" ] && continue
  printf '%s\n' "$models" | grep -qx "$m" || fail "Model '$m' is not available to ${gh_account:-the active gh account}. Available: $(printf '%s ' $models)"
done
echo "Copilot account ${gh_account:-active} offers $model (agent) and $judge (judge)"

if [ "$connected" = 1 ]; then
  command -v az >/dev/null || fail "Azure CLI (az) is required for --connected"
  [ "$(cfg allowWrites)" = "True" ] || fail "--connected creates and deletes Plans; set allowWrites to true in $CONFIG"
  FABRIC_TOKEN="$(az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv 2>/dev/null)" \
    || fail "No Fabric token from az (run: az login)"
  export FABRIC_TOKEN
  # The agent keeps this token for the whole connected run (up to ~45 minutes), and
  # az hands out its cached token until a few minutes before it expires.
  left="$(python3 -c 'import base64,json,os,time;p=os.environ["FABRIC_TOKEN"].split(".")[1];print(int((json.loads(base64.urlsafe_b64decode(p+"==="))["exp"]-time.time())//60))')"
  [ "$left" -ge 45 ] || fail "Your az Fabric token expires in $left minutes; the connected run needs 45. Run 'az logout && az login' for a fresh token, or rerun after it expires."
  ws_id="$(cfg workspaceId)"
  if [ -z "$ws_id" ]; then
    ws_name="$(cfg workspaceName)"
    ws_id="$(az rest --method get --url https://api.fabric.microsoft.com/v1/workspaces \
      --resource https://api.fabric.microsoft.com --headers "x-ms-fabric-skill=$SKILL_NAME" \
      --query "value[?displayName=='$ws_name'].id | [0]" -o tsv)"
    [ -n "$ws_id" ] || fail "Workspace '$ws_name' not found for your az account"
  fi
  echo "Fabric token from az; workspace ${ws_id}"
fi

# Delete this skill's eval Plans (name prefix, and older than N hours when N > 0).
sweep_plans() { # prefix min_age_hours
  python3 - "$ws_id" "$1" "$2" <<'PY'
import json, os, sys, urllib.request, datetime
ws, prefix, hours = sys.argv[1], sys.argv[2], float(sys.argv[3])
api = "https://api.fabric.microsoft.com/v1"
import subprocess
tok = subprocess.run(["az", "account", "get-access-token", "--resource", "https://api.fabric.microsoft.com", "--query", "accessToken", "-o", "tsv"], capture_output=True, text=True).stdout.strip() or os.environ["FABRIC_TOKEN"]
head = {"Authorization": "Bearer " + tok, "x-ms-fabric-skill": "fabric-plan-skill"}
def call(method, route):
    req = urllib.request.Request(api + route, method=method, headers=head)
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read(); return json.loads(raw) if raw else None
items, route = [], f"/workspaces/{ws}/plans"
while route:
    page = call("GET", route); items += page.get("value", [])
    nxt = page.get("continuationUri"); route = nxt[len(api):] if nxt and nxt.startswith(api) else None
gone = 0
for p in items:
    name = p["displayName"]
    if not name.startswith(prefix):
        continue
    if hours > 0:  # fps-eval-<MMDDHHMMSS><random>-... : skip Plans from runs still in progress
        try:
            stamp = datetime.datetime.strptime(name.split("-")[2][:10], "%m%d%H%M%S").replace(
                year=datetime.datetime.utcnow().year)
            if datetime.datetime.utcnow() - stamp < datetime.timedelta(hours=hours):
                continue
        except (IndexError, ValueError):
            pass
    call("DELETE", f"/workspaces/{ws}/plans/{p['id']}"); gone += 1
    print("deleted leftover", name)
print(f"sweep: {gone} Plan(s) deleted")
PY
}

if [ "$sweep" = 1 ]; then
  step "Sweep"; sweep_plans "fps-eval-" 2; exit 0
fi

# The skill folder Vally loads must be a real copy named after the skill, and
# hold only what ships (package-manifest.json). Never stage tests/: the eval
# rubrics, grader patterns and connected grader must stay out of the agent's reach.
stage="$(mktemp -d "${TMPDIR:-/tmp}/$SKILL_NAME-evals.XXXXXX")"
trap 'rm -rf "$stage"' EXIT
mkdir -p "$stage/skills/$SKILL_NAME"
(cd "$ROOT" && rsync -aR --exclude __pycache__ --exclude '*.pyc' $SHIPPED "$stage/skills/$SKILL_NAME/")
[ ! -e "$stage/skills/$SKILL_NAME/tests" ] || fail "tests/ must not be staged into the skill"

[ "$dry_run" = 1 ] && { step "Summary"; echo "${summary[*]} · setup ok (dry run)"; exit 0; }

# ---------------------------------------------------------------- evals
out="$ROOT/vally-results/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$out"
status=0

run_eval() { # name spec [extra vally args...]
  local name="$1" spec="$2"; shift 2
  step "$name"
  local log="$out/$name.log"
  set +e
  "$VALLY" eval -e "$spec" --skill-dir "$stage/skills" --model "$model" --judge-model "$judge" \
    --runs "$runs" --workers 1 --max-retries 0 --output-dir "$out/$name" "$@" 2>&1 | tee "$log" \
    | perl -pe 's/\e\[[0-9;]*m//g' | sed -n '/^Summary/,/^Saved/p'
  local rc=${PIPESTATUS[0]}
  set -e
  local line; line="$(perl -pe 's/\e\[[0-9;]*m//g' "$log" | grep -Eo '[0-9]+/[0-9]+ \(score [0-9.]+%' | head -1)"
  summary+=("$name ${line:-error}${line:+)}")
  [ "$rc" = 0 ] || status=1
}

run_eval smoke tests/evals/$SKILL_NAME/eval.yaml
[ "$full" = 1 ] && run_eval full tests/evals/$SKILL_NAME-fulleval/eval.yaml
if [ "$connected" = 1 ]; then
  run_id="$(date -u +%m%d%H%M%S)$RANDOM"
  echo "Connected run ID $run_id: Plans are named fps-eval-$run_id-*"
  run_eval connected "tests/evals/$SKILL_NAME-connected/eval.yaml" \
    --param "WORKSPACE_ID=$ws_id" --param "RUN_ID=$run_id"
  sweep_plans "fps-eval-$run_id-" 0
fi

step "Summary (paste into the PR)"
echo "${summary[*]} · model $model · judge $judge · vally $VALLY_VERSION"
echo "Results: $out"
exit $status
