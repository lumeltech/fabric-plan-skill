import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^]\n]*\]\(([^)\s]+)\)")


def local_links(document):
    for target in LINK.findall(document.read_text(encoding="utf-8")):
        url = urlsplit(target)
        if not url.scheme and not url.netloc and url.path:
            yield (document.parent / unquote(url.path)).resolve()


class SkillReferences(unittest.TestCase):
    def test_all_markdown_guides_are_one_hop_from_skill(self):
        guides = set((ROOT / "references").rglob("*.md"))
        links = set(local_links(ROOT / "SKILL.md"))
        self.assertEqual(guides - links, set())
        self.assertEqual({path for path in links if not path.exists()}, set())
        for guide in guides:
            with self.subTest(guide=guide.relative_to(ROOT)):
                self.assertEqual(guides.intersection(local_links(guide)) - {guide}, set())
