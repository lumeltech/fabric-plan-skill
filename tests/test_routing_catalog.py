"""The routing catalog and guides may name only public routes and shipped modules.

test_discovery.py already proves the catalog resolves to shipped guides,
registered commands and existing callables. This guards the other direction:
routing text must never invite an agent toward a route this skill cannot use.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Routing text may name only public Fabric REST routes and runtime modules this
# package ships. Prose may still say in words that a capability has no public route.
API_PATH = re.compile(r"/v1/[A-Za-z0-9_{}./-]*")
PUBLIC_PREFIXES = ("/v1/workspaces/", "/v1/connections/", "/v1/operations/")
MODULE = re.compile(r"\bruntime\.([a-z_]+)\b")
SHIPPED = {p.stem for p in (ROOT / "scripts/runtime").glob("*.py")}


def unsupported_references(text):
    paths = [p for p in API_PATH.findall(text) if not p.startswith(PUBLIC_PREFIXES)]
    modules = [m for m in MODULE.findall(text) if m not in SHIPPED]
    return paths + modules


GUIDE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\.md\b")
# Restating why a document is absent is not an invitation to read it.
GAPS_EXEMPT = {"documentationNotBundled"}


class RoutingCatalogBoundaries(unittest.TestCase):
    def test_catalog_names_no_private_route(self):
        text = (ROOT / "assets/catalog" / "module-routing.json").read_text(encoding="utf-8")
        self.assertEqual(unsupported_references(text), [])

    def test_guides_name_no_private_route(self):
        for path in sorted((ROOT / "references").glob("*.md")):
            with self.subTest(guide=path.name):
                self.assertEqual(unsupported_references(path.read_text(encoding="utf-8")), [])

    def test_shipped_text_points_only_at_bundled_guides(self):
        bundled = {path.name for path in (ROOT / "references").glob("*.md")}
        sources = {
            "assets/catalog/module-routing.json": (ROOT / "assets/catalog" / "module-routing.json").read_text(
                encoding="utf-8"
            ),
            "SKILL.md": (ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
        }
        gaps = json.loads((ROOT / "assets/catalog" / "api-contract-gaps.json").read_text(encoding="utf-8"))
        sources["assets/catalog/api-contract-gaps.json"] = json.dumps(
            {key: value for key, value in gaps.items() if key not in GAPS_EXEMPT}
        )
        for name, text in sources.items():
            with self.subTest(source=name):
                self.assertEqual(set(GUIDE_NAME.findall(text)) - bundled - {"SKILL.md"}, set())


if __name__ == "__main__":
    unittest.main()
