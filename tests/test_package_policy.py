import argparse
import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_GUID = re.compile(r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}")
LARGE_NUMBER = re.compile(r"(?<![A-Za-z0-9])\d{16,20}(?![A-Za-z0-9])")
# Release-history tags such as "v29" or "(v10)"; API paths like "/v1/" are excluded.
VERSION_TAG = re.compile(r"(?<![/\w.])v\d{1,2}\b")
ISO_DATE = re.compile(r"\b20\d\d-[01]\d-[0-3]\d\b")
# Private PowerTable service route, request header and error-code family.
PRIVATE_DETAIL = re.compile(r"/v2/powertable|x-target-visual|\bPT_WB_\d+", re.I)
TEXT_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".cjs", ".js"}
RUNTIME_CEILINGS = {"modules": 73, "lines": 9687, "subcommands": 49}


def cli_subcommands():
    """Map each plan.py subcommand to the summary it advertises in `plan.py -h`."""
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from plan import build_parser
    finally:
        sys.path.pop(0)
    subparsers = next(
        action for action in build_parser()._actions
        if isinstance(action, argparse._SubParsersAction)
    )
    return {action.dest: (action.help or "") for action in subparsers._choices_actions}


def shipped_guides():
    return sorted((ROOT / "references").glob("*.md")) + [ROOT / "SKILL.md", ROOT / "README.md"]


def prose_lines(path):
    """Yield numbered lines outside fenced code, where sample data may carry dates."""
    fenced = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced:
            yield number, line


def double_encoded_runs(text):
    """Runs of UTF-8 bytes that were decoded as Windows-1252, such as an encoded multiplication sign."""
    runs = []
    for run in re.findall(r"[^\x00-\x7f]+", text):
        try:
            repaired = run.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        if repaired != run:
            runs.append(run)
    return runs


class PackagePolicyTests(unittest.TestCase):
    def test_guides_carry_no_release_history_or_dated_evidence(self):
        findings = [
            f"{path.relative_to(ROOT).as_posix()}:{number}: {line.strip()[:80]}"
            for path in shipped_guides()
            for number, line in prose_lines(path)
            if VERSION_TAG.search(line) or ISO_DATE.search(line)
        ]
        self.assertEqual(findings, [])

    def test_shipped_text_names_no_private_service_detail(self):
        sources = shipped_guides() + sorted((ROOT / "assets/catalog").glob("*.json"))
        findings = [
            path.relative_to(ROOT).as_posix()
            for path in sources
            if PRIVATE_DETAIL.search(path.read_text(encoding="utf-8"))
        ]
        self.assertEqual(findings, [])

    def test_tracked_text_has_no_double_encoded_characters(self):
        tracked = subprocess.check_output(
            ["git", "ls-files", "-z"], cwd=ROOT, text=False
        ).decode().split("\0")
        findings = {}
        for name in tracked:
            path = ROOT / name
            if path.suffix in TEXT_SUFFIXES and path.is_file():
                runs = double_encoded_runs(path.read_text(encoding="utf-8"))
                if runs:
                    findings[name] = runs[:3]
        self.assertEqual(findings, {})

    def test_manifest_covers_public_package_roots(self):
        manifest = json.loads((ROOT / "package-manifest.json").read_text())
        required = {"scripts/runtime/", "references/", "assets/fixtures/", "assets/schemas/", "scripts/tools/", "scripts/vendor/"}
        self.assertTrue(required <= set(manifest["classification"]["runtime-required"]))
        for path in manifest["retained-unreferenced-assets"]:
            if "*" in path:
                self.assertTrue(list(ROOT.glob(path)), path)
            else:
                self.assertTrue((ROOT / path).is_file(), path)

    def test_no_tracked_bytecode_or_private_workspace_content(self):
        tracked = subprocess.check_output(
            ["git", "ls-files", "-z"], cwd=ROOT, text=False
        ).decode().split("\0")
        forbidden = tuple(
            path for path in tracked
            if path.endswith((".pyc", ".pyo"))
            or any(marker in path for marker in ("__pycache__", "_brief/", "_build/", "_samples/"))
        )
        self.assertEqual(forbidden, ())

    def test_package_excludes_maintainer_and_contribution_metadata(self):
        manifest = json.loads((ROOT / "package-manifest.json").read_text())
        excluded = set(manifest["classification"]["excluded-from-package"])
        self.assertTrue({".trail/", ".changeset/", ".github/", "build/"} <= excluded)

    def test_reference_markdown_is_bounded_and_machine_data_is_elsewhere(self):
        limit = json.loads((ROOT / "package-manifest.json").read_text())[
            "limits"]["references_markdown_max_bytes"]
        oversized = [
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "references").glob("*.md")
            if path.stat().st_size > limit
        ]
        self.assertEqual(oversized, [])
        # skills-for-fabric layout: references/ holds markdown only; data lives in assets/.
        self.assertEqual([p.name for p in (ROOT / "references").iterdir() if p.suffix != ".md"], [])
        self.assertTrue((ROOT / "assets/preservation-manifest.json").is_file())

    def test_request_examples_use_deterministic_synthetic_id_ranges(self):
        examples = [
            ROOT / "assets/examples/planning-presentation.request.json",
            ROOT / "assets/examples/measure-display.request.json",
            ROOT / "assets/examples/five-usecases/destination.example.json",
        ]
        for path in examples:
            relative = path.relative_to(ROOT)
            text = path.read_text()
            for identifier in SYNTHETIC_GUID.findall(text):
                self.assertTrue(
                    identifier.lower().startswith(
                        ("f0000000-0000-4000-8000-", "10000000-0000-4000-8000-")
                    ),
                                f"{relative}: non-synthetic UUID {identifier}")
            for identifier in LARGE_NUMBER.findall(text):
                self.assertTrue(
                    identifier.startswith(("100000000000000", "200000000000000")),
                                f"{relative}: non-synthetic numeric identity")

    def test_cli_sums_up_every_command_uniquely(self):
        # An agent picks a subcommand from this text, so it must be present and must differ
        # from every other command's summary.
        subcommands = cli_subcommands()
        findings = sorted(name for name, summary in subcommands.items() if not summary)
        summaries = {}
        for name, summary in subcommands.items():
            summaries.setdefault(summary, []).append(name)
        findings += sorted(", ".join(sorted(names)) for names in summaries.values() if len(names) > 1)
        self.assertEqual(findings, [])

    def test_runtime_stays_within_its_frozen_budget(self):
        # Nothing in the runtime is dead, so growth needs an argument: raise a ceiling only in
        # a pull request that says which capability needed the room.
        modules = sorted((ROOT / "scripts/runtime").glob("*.py"))
        actual = {
            "modules": len(modules),
            "lines": sum(len(path.read_text(encoding="utf-8").splitlines()) for path in modules),
            "subcommands": len(cli_subcommands()),
        }
        over = [
            f"{label}: {count} > {RUNTIME_CEILINGS[label]}"
            for label, count in actual.items()
            if count > RUNTIME_CEILINGS[label]
        ]
        self.assertEqual(over, [])


if __name__ == "__main__":
    unittest.main()
