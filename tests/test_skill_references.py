import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import argparse
import contextlib
import io
import re
import shlex
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^]\n]*\]\(([^)\s]+)\)")
PLAN_COMMAND = re.compile(r"python (plan\.py [^`\n]*)")


def local_links(document):
    for target in LINK.findall(document.read_text(encoding="utf-8")):
        url = urlsplit(target)
        if not url.scheme and not url.netloc and url.path:
            yield (document.parent / unquote(url.path)).resolve()


def heading_slug(heading):
    heading = re.sub(r"[`*_~]", "", heading.strip().lower())
    heading = re.sub(r"[^\w\s-]", "", heading, flags=re.UNICODE)
    return re.sub(r"\s", "-", heading)


class SkillReferences(unittest.TestCase):
    def test_all_markdown_guides_are_one_hop_from_skill(self):
        guides = set((ROOT / "references").rglob("*.md"))
        links = set(local_links(ROOT / "SKILL.md"))
        self.assertEqual(guides - links, set())
        self.assertEqual({path for path in links if not path.exists()}, set())
        for guide in guides:
            with self.subTest(guide=guide.relative_to(ROOT)):
                self.assertEqual(guides.intersection(local_links(guide)) - {guide}, set())

    def test_long_references_have_contents_lists(self):
        for guide in sorted((ROOT / "references").glob("*.md")):
            text = guide.read_text(encoding="utf-8")
            if len(text.splitlines()) <= 100:
                continue
            with self.subTest(guide=guide.name):
                self.assertIn("## Contents", text)
                contents = text.split("## Contents", 1)[1].split("\n## ", 1)[0]
                links = LINK.findall(contents)
                headings = re.findall(r"(?m)^## (.+)$", text)
                self.assertTrue(links)
                self.assertTrue(all(target.startswith("#") for target in links))
                expected = [heading_slug(h) for h in headings if h != "Contents"]
                self.assertCountEqual([target[1:] for target in links], expected)

    def test_documented_plan_commands_parse(self):
        import plan

        parse = argparse.ArgumentParser.parse_args

        class Parsed(Exception):
            pass

        def parse_only(parser):
            parse(parser)
            raise Parsed

        documents = sorted((ROOT / "references").glob("*.md")) + [ROOT / "SKILL.md", ROOT / "README.md"]
        for document in documents:
            for line in PLAN_COMMAND.findall(document.read_text(encoding="utf-8")):
                argv = shlex.split(line.strip().rstrip("."))
                if "--help" in argv:
                    continue
                with self.subTest(document=document.name, command=line), \
                        patch.object(sys, "argv", argv), \
                        patch.object(argparse.ArgumentParser, "parse_args", parse_only), \
                        contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(Parsed):
                        plan.main()
