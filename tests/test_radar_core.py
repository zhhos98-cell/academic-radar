import tempfile
import unittest
from pathlib import Path

from academic_radar.config import RadarConfig
from academic_radar.render import render_email
from academic_radar.scoring import make_item, score
from academic_radar.state import load_seen_links, save_seen_links


class RadarCoreTests(unittest.TestCase):
    def test_scores_relevant_cfp(self):
        config = RadarConfig()
        text = "Call for papers: history of science workshop at Cambridge"
        self.assertGreater(score(text, config), 0)

    def test_filters_unrelated_event(self):
        config = RadarConfig()
        text = "Call for papers: marketing conference for high school students"
        self.assertEqual(score(text, config), 0)

    def test_make_item_classifies_cfp(self):
        config = RadarConfig()
        item = make_item(
            "Call for papers",
            "https://example.org/cfp",
            "History of science symposium deadline: March 1, 2027",
            "RSS",
            config,
            "Example Feed",
        )
        self.assertIsNotNone(item)
        self.assertEqual(item["category"], "CFP / Calls")
        self.assertEqual(item["tag"], "CFP")

    def test_render_empty_digest(self):
        body = render_email([], 20)
        self.assertIn("No new relevant items", body)

    def test_state_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state" / "seen.json"
            save_seen_links([{"link": "https://example.org/item"}], str(state_file))
            self.assertIn("https://example.org/item", load_seen_links(str(state_file)))


if __name__ == "__main__":
    unittest.main()
