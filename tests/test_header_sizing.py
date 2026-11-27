"""Header sizing follows the product's title CSS: span font sizes count, paragraph margins do not."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import unittest
from runtime.header_sizing import LINE_HEIGHT, Paragraphs, calculate_header_height


def sizes(content):
    parser = Paragraphs()
    parser.feed(content)
    return [p['size'] for p in parser.paragraphs]


class HeaderSizing(unittest.TestCase):
    def test_span_sizes_count_and_unsized_text_inherits_13px(self):
        self.assertEqual(sizes('<div><p><span style="font-size:22px"><strong>Title</strong></span></p><p>Plain</p></div>'),
                         [22.0, 13.0])

    def test_innermost_inline_size_wins(self):
        self.assertEqual(sizes('<p style="font-size:30px"><span style="font-size:12px">small</span></p>'), [12.0])

    def test_paragraph_margins_add_nothing(self):
        plain = calculate_header_height('<p><span style="font-size:20px">A</span></p>', 600)
        margins = calculate_header_height('<p style="margin:0 0 40px 0"><span style="font-size:20px">A</span></p>', 600)
        self.assertEqual(plain['contentHeight'], round(20 * LINE_HEIGHT, 2))
        self.assertEqual(plain, margins)


if __name__ == '__main__':
    unittest.main()
