"""Tree visual coverage on Intelligence dashboards: recognition, preservation, recorded gaps.

The tree family is a visual type a real dashboard can hold. This package names it,
protects it, and builds decomposition and organization trees; row and measure trees
stay recognition-only.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import json
import unittest
from pathlib import Path

from runtime.discovery import discover
from runtime.intelligence import classify_visual, complete_card_state, tree_visual_types

ROOT = Path(__file__).resolve().parents[1]
TREE_CHART_TYPES = {"DECOMPOSITION_TREE", "ORGANIZATION_TREE", "ROW_TREE", "COLUMN_TREE"}


class TreeVisualCoverageTests(unittest.TestCase):
    def test_every_persisted_tree_discriminator_is_named(self):
        types = tree_visual_types()
        self.assertEqual(set(types), TREE_CHART_TYPES)
        self.assertEqual(types["DECOMPOSITION_TREE"], "Decomposition tree")
        self.assertEqual(types["ORGANIZATION_TREE"], "Organizational tree")
        self.assertEqual(types["ROW_TREE"], "Row tree")
        self.assertEqual(types["COLUMN_TREE"], "Measure tree")
        types["ROW_TREE"] = "rewritten"
        self.assertEqual(tree_visual_types()["ROW_TREE"], "Row tree")

    def test_classification_reads_both_discriminator_positions(self):
        for chart_type in sorted(TREE_CHART_TYPES):
            with self.subTest(chartType=chart_type):
                top = classify_visual({"chartType": chart_type})
                nested = classify_visual({"visualState": {"chartType": chart_type}})
                self.assertEqual(top, nested)
                self.assertEqual(top["family"], "tree")
                self.assertEqual(top["chartType"], chart_type)
                self.assertEqual(top["visual_type"], tree_visual_types()[chart_type])
        self.assertEqual(classify_visual({"visualState": {"chartType": "CARD"}})["family"], "card")
        self.assertIsNone(classify_visual({}))
        self.assertIsNone(classify_visual({"chartType": "A_TYPE_NOT_NAMED_HERE"}))

    def test_card_writer_refuses_to_retype_a_tree(self):
        props = {"chartType": "ORGANIZATION_TREE", "visualState": {"chartType": "ORGANIZATION_TREE"}}
        with self.assertRaises(ValueError) as caught:
            complete_card_state(props)
        self.assertIn("Organizational tree", str(caught.exception))
        self.assertEqual(props["chartType"], "ORGANIZATION_TREE")

    def test_tree_construction_is_no_longer_recorded_as_a_gap(self):
        gaps = json.loads((ROOT / "assets/catalog" / "api-contract-gaps.json").read_text(encoding="utf-8"))
        self.assertNotIn("tree-visual-authoring", {item["id"] for item in gaps["capabilities"]})
        module = next(item for item in discover(query="create tree visual")["modules"]
                      if item["id"] == "INTELLIGENCE-VISUAL-TYPES")
        symbols = [symbol for operation in module["operations"] for symbol in operation["symbols"]]
        self.assertIn("runtime.tree_visuals.tree_visual", symbols)

    def test_discovery_routes_tree_requests_to_the_coverage_guide(self):
        module = next(item for item in discover(query="decomposition tree")["modules"]
                      if item["id"] == "INTELLIGENCE-VISUAL-TYPES")
        self.assertEqual([guide["file"] for guide in module["guides"]], ["intelligence-visual-types.md"])
        symbols = [symbol for operation in module["operations"] for symbol in operation["symbols"]]
        self.assertIn("runtime.intelligence.classify_visual", symbols)
        self.assertIn("runtime.intelligence.tree_visual_types", symbols)
        for operation in module["operations"]:
            self.assertEqual(operation["phase"], "local")


if __name__ == "__main__":
    unittest.main()
