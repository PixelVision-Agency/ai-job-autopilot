"""The ATS resume's two-column skills list: a long item must stay inside its own column.

It used to be drawn on one line, so a 290pt skill ran into the right column and a parser
read the two items mixed together.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "templates/cv/designed"))

try:
    import fitz
    import render_ats
except ImportError:  # PyMuPDF missing
    fitz = None


@unittest.skipIf(fitz is None, "PyMuPDF not installed")
class TwoColumnsWrap(unittest.TestCase):
    def test_long_item_wraps_inside_its_column(self):
        pdf = fitz.open()
        flow = render_ats.Flow(pdf)
        flow.y = 100
        long_item = "Cloud Infrastructure & Observability (AWS, Terraform, Kubernetes, Grafana, Datadog)"
        flow.two_columns([long_item, "Short"], ["Python", "SQL"])
        right_x = render_ats.MARGIN + (render_ats.RIGHT - render_ats.MARGIN - 22) / 2 + 22
        words = pdf[0].get_text("words")
        left_words = [w for w in words if w[0] < right_x - 5]
        self.assertTrue(all(w[2] <= right_x for w in left_words), "left text crosses into the right column")
        self.assertGreater(len({round(w[3]) for w in left_words}), 2, "long item should take two lines")


if __name__ == "__main__":
    unittest.main()
