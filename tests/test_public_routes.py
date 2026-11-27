"""The public-route allowlist is the skill's main network safety boundary.

Python (runtime/transport.py) and Node (tools/http.cjs) load the same
public_routes.json. These cases run through both and must get the same answer.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from runtime.transport import Client  # noqa: E402

BASE = "https://api.fabric.microsoft.com"
WS = "10000000-0000-4000-8000-000000000010"
PLAN = "10000000-0000-4000-8000-000000000020"

ALLOWED = [
    "/v1",
    f"/v1/workspaces/{WS}/plans",
    f"/v1/workspaces/{WS}/plans/{PLAN}",
    f"/v1/workspaces/{WS}/plans/{PLAN}/getDefinition",
    f"/v1/workspaces/{WS}/plans/{PLAN}/updateDefinition",
    f"/v1/workspaces/{WS}/semanticModels/{PLAN}",
    f"/v1/workspaces/{WS}/semanticModels/{PLAN}/getDefinition?format=TMDL",
    f"/v1/workspaces/{WS}/sqlDatabases/{PLAN}/getDefinition?format=sqlproj",
    f"/v1/operations/{PLAN}",
    f"/v1/operations/{PLAN}/result",
]

REJECTED = [
    f"/v1/workspaces/{WS}/items",
    f"/v1/workspaces/{WS}/plans/..",
    f"/v1/workspaces/{WS}/plans/.",
    f"/v1/workspaces/{WS}/plans/../../admin",
    f"/v1/workspaces/../plans",
    f"/v1/workspaces/{WS}/plans/a%2Fb",
    f"/v1/workspaces/{WS}/plans/a%2e%2e",
    f"/v1/workspaces/{WS}/plans/a%0Ab",
    f"/v1/workspaces/{WS}/plans/{PLAN}/jobs",
    "/v1/admin/tenants",
    "/v1/workload/plans",
    "/metadata/x",
    "/v2/workspaces",
    "/",
]


JOURNAL = tempfile.mkdtemp(prefix="route-test-")


def python_allows(path):
    client = Client(BASE + "/v1", "UNSET_ROUTE_TEST_TOKEN", journal=JOURNAL,
                    adapter=lambda *a: (_ for _ in ()).throw(AssertionError("no network")))
    try:
        client.check_url(BASE + path)
        return True
    except ValueError:
        return False


def node_allows(paths):
    script = ("const {isPublicFabricUrl}=require(process.argv[1]);"
              "const urls=JSON.parse(process.argv[2]);"
              "process.stdout.write(JSON.stringify(urls.map(isPublicFabricUrl)));")
    out = subprocess.run(
        [shutil.which("node"), "-e", script, str(ROOT / "scripts/tools/http.cjs"),
         json.dumps([BASE + p for p in paths])],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


class PublicRouteTests(unittest.TestCase):
    def test_python_allows_only_public_routes(self):
        for path in ALLOWED:
            with self.subTest(path=path):
                self.assertTrue(python_allows(path))
        for path in REJECTED:
            with self.subTest(path=path):
                self.assertFalse(python_allows(path))

    @unittest.skipUnless(shutil.which("node"), "Node.js not installed")
    def test_node_and_python_agree(self):
        paths = ALLOWED + REJECTED
        self.assertEqual(node_allows(paths), [python_allows(p) for p in paths])

    def test_other_hosts_rejected(self):
        client = Client(BASE + "/v1", "UNSET_ROUTE_TEST_TOKEN", journal=JOURNAL)
        for url in ("https://example.com/v1/workspaces", "http://api.fabric.microsoft.com/v1",
                    "https://api.fabric.microsoft.com.evil.test/v1"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                client.check_url(url)


if __name__ == "__main__":
    unittest.main()
