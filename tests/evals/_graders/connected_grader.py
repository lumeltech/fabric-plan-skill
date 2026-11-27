"""Vally program grader for the connected evals.

Reads the real Plan state in the test workspace through the public Fabric API,
independently of what the agent reports, then deletes every Plan the case
created so no trial leaves anything behind.

Environment (set by the eval spec and tests/run-evals.sh):
  CONNECTED_CASE   lifecycle | deploy | delete | missing
  WORKSPACE_ID     test workspace
  RUN_ID           unique prefix part for this run's Plan names
  FABRIC_TOKEN     fallback only; the grader asks `az` for a current token (never printed)
  EVALUATE_WORKSPACE, EVALUATE_GRADER_INPUT  set by Vally

Prints one GraderResult JSON object on stdout; diagnostics go to stderr.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.fabric.microsoft.com/v1"
HEADER = {"x-ms-fabric-skill": "fabric-plan-skill"}


_TOKEN = None


def token():
    """A token valid now: ask `az` (it refreshes near expiry); fall back to FABRIC_TOKEN."""
    global _TOKEN
    if _TOKEN is None:
        import subprocess
        try:
            _TOKEN = subprocess.run(
                ["az", "account", "get-access-token", "--resource", "https://api.fabric.microsoft.com",
                 "--query", "accessToken", "-o", "tsv"],
                capture_output=True, text=True, check=True, timeout=60).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            _TOKEN = os.environ["FABRIC_TOKEN"]
    return _TOKEN


def call(method, route):
    req = urllib.request.Request(API + route, method=method, headers={
        **HEADER, "Authorization": "Bearer " + token()})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None), dict(r.headers)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            body = json.loads(raw) if raw else None
        except ValueError:
            body = None
        return e.code, body, dict(e.headers)


def plans(ws):
    out, route = [], f"/workspaces/{ws}/plans"
    while route:
        status, body, _ = call("GET", route)
        if status != 200:
            raise RuntimeError(f"list plans returned {status}")
        out += body.get("value", [])
        nxt = body.get("continuationUri")
        route = nxt[len(API):] if nxt and nxt.startswith(API) else None
    return out


def export(ws, plan_id):
    status, body, headers = call("POST", f"/workspaces/{ws}/plans/{plan_id}/getDefinition")
    if status == 202:  # long-running operation: poll it, then read its result
        h = {k.lower(): v for k, v in headers.items()}
        # Like the skill's client, poll the public operations route by operation ID.
        op_id = h.get("x-ms-operation-id")
        if not op_id:
            raise RuntimeError("export returned no operation ID")
        op, deadline = "/operations/" + urllib.parse.quote(op_id, safe=""), time.time() + 300
        while True:
            time.sleep(int(h.get("retry-after") or 2))
            status, body, headers = call("GET", op)
            h = {k.lower(): v for k, v in headers.items()}
            state = (body or {}).get("status")
            if state == "Succeeded":
                status, body, _ = call("GET", op + "/result")
                break
            if state in ("Failed", "Cancelled") or time.time() > deadline:
                raise RuntimeError(f"export operation {state or 'timed out'}")
    if status != 200:
        raise RuntimeError(f"export returned {status}")
    return {p["path"]: p for p in body["definition"]["parts"]}


def cleanup(ws, prefix):
    removed = []
    for p in plans(ws):
        if p["displayName"].startswith(prefix):
            status, _, _ = call("DELETE", f"/workspaces/{ws}/plans/{p['id']}")
            removed.append((p["displayName"], status))
    return removed


def agent_commands():
    data = json.loads(Path(os.environ["EVALUATE_GRADER_INPUT"]).read_text(encoding="utf-8"))
    events = (data.get("trajectory") or {}).get("events") or []
    cmds = []
    for e in events:
        args = (e.get("data") or {}).get("arguments")
        if isinstance(args, dict) and isinstance(args.get("command"), str):
            cmds.append(args["command"])
    return cmds


def build_outputs(cmds):
    """Folders the agent passed to `plan.py build --out`, resolved against its `cd`."""
    import re, shlex
    found = []
    for c in cmds:
        if "plan.py" not in c or " build " not in c:
            continue
        cwd = Path(os.environ.get("EVALUATE_WORKSPACE") or ".")
        m = re.match(r"\s*cd\s+(\S+)\s*&&", c)
        if m:
            cwd = Path(os.path.expanduser(m.group(1).strip("'\"")))
        try:
            words = shlex.split(c.split("plan.py", 1)[1])
        except ValueError:
            continue
        if "--out" in words and words.index("--out") + 1 < len(words):
            out = Path(os.path.expanduser(words[words.index("--out") + 1]))
            found.append(out if out.is_absolute() else cwd / out)
    return found


def find_built_envelope(cmds=()):
    roots = [Path(os.environ.get("EVALUATE_WORKSPACE") or ".")] + build_outputs(cmds)
    for path in sorted(p for root in roots if root.exists() for p in root.rglob("envelope.json")):
        try:
            env = json.loads(path.read_text(encoding="utf-8"))
            if env.get("definition", {}).get("parts"):
                return env
        except (ValueError, OSError):
            continue
    return None


def sheet_ids(parts):
    return sorted({p.split("/")[1] for p in parts if p.startswith("sheets/")})


def grade():
    ws, run_id, case = os.environ["WORKSPACE_ID"], os.environ["RUN_ID"], os.environ["CONNECTED_CASE"]
    prefix = f"fps-eval-{run_id}-{case}"
    checks = []
    by_name = {p["displayName"]: p for p in plans(ws)}
    cmds = agent_commands()

    if case == "lifecycle":
        renamed = by_name.get(prefix + "-renamed")
        checks.append(("renamed Plan exists in the workspace", renamed is not None))
        checks.append(("original name no longer exists", prefix not in by_name))
        if renamed:
            parts = export(ws, renamed["id"])
            checks.append(("service export has definition.json", "definition.json" in parts))
    elif case == "deploy":
        plan = by_name.get(prefix)
        checks.append(("deployed Plan exists in the workspace", plan is not None))
        built = find_built_envelope(cmds)
        checks.append(("agent built a local candidate (envelope.json)", built is not None))
        if plan and built:
            saved = export(ws, plan["id"])
            built_parts = {p["path"] for p in built["definition"]["parts"]}
            missing = sorted(built_parts - set(saved))
            checks.append((f"every built part was saved ({len(missing)} missing)", not missing))
            checks.append(("sheet IDs preserved", sheet_ids(built_parts) == sheet_ids(saved)
                           and len(sheet_ids(saved)) > 0))
    elif case == "delete":
        checks.append(("Plan is gone from the workspace", not any(n.startswith(prefix) for n in by_name)))
        checks.append(("agent ran the skill's confirmed delete",
                       any("plan.py" in c and "api delete" in c for c in cmds)))
    elif case == "missing":
        checks.append(("agent ran no delete", not any("api delete" in c or "--method delete" in c.lower()
                                                     for c in cmds)))
    else:
        raise ValueError("Unknown CONNECTED_CASE " + case)

    checks.append(("no raw REST or private route used",
                   not any(("az rest" in c and "--method" in c and "get" not in c.lower())
                           or "curl " in c for c in cmds)))
    removed = cleanup(ws, prefix)
    failed = [name for name, ok in checks if not ok]
    evidence = "; ".join(f"{'PASS' if ok else 'FAIL'} {name}" for name, ok in checks)
    if removed:
        evidence += f"; cleanup deleted {len(removed)} Plan(s)"
    return {"name": f"connected-{case}", "kind": "code", "passed": not failed,
            "score": round(sum(ok for _, ok in checks) / len(checks), 3), "evidence": evidence}


if __name__ == "__main__":
    try:
        result = grade()
    except Exception as exc:  # report, never crash silently
        print(f"connected grader error: {exc}", file=sys.stderr)
        try:  # still try to clean up this case's Plans
            cleanup(os.environ["WORKSPACE_ID"], f"fps-eval-{os.environ['RUN_ID']}-{os.environ['CONNECTED_CASE']}")
        except Exception:
            pass
        result = {"name": "connected", "kind": "code", "passed": False, "score": 0,
                  "evidence": f"grader error: {exc}"}
    print(json.dumps(result))
