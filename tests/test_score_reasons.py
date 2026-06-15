import unittest

from academic_radar.config import RadarConfig
from academic_radar.render import render_email, serializable_items
from academic_radar.scoring import explain_score, make_item, score


class ScoreReasonTests(unittest.TestCase):
    def test_explain_score_lists_positive_matches(self):
        config = RadarConfig()
        text = "Call for papers: history of science workshop at Cambridge"

        explanation = explain_score(text, config)

        self.assertEqual(score(text, config), explanation["score"])
        self.assertGreater(explanation["score"], 0)
        self.assertIn("call for papers", explanation["event_terms"])
        self.assertIn("workshop", explanation["event_terms"])
        self.assertIn("history of science", explanation["core_field_terms"])
        self.assertIn("cambridge", explanation["source_terms"])
        self.assertFalse(explanation["filtered"])
        self.assertTrue(explanation["reasons"])

    def test_explain_score_records_negative_filter(self):
        config = RadarConfig()

        explanation = explain_score("Call for papers: marketing conference for high school students", config)

        self.assertEqual(explanation["score"], 0)
        self.assertTrue(explanation["filtered"])
        self.assertEqual(explanation["filtered_by"], "negative_terms")
        self.assertIn("marketing", explanation["negative_terms"])

    def test_make_item_and_render_email_include_reasons(self):
        config = RadarConfig()
        item = make_item(
            "Call for papers",
            "https://example.org/cfp",
            "History of science workshop at Cambridge. Deadline: March 1, 2027",
            "RSS",
            config,
            "Example Feed",
        )

        self.assertIsNotNone(item)
        self.assertIn("score_reasons", item)
        self.assertIn("score_matches", item)
        self.assertIn("score_reasons", serializable_items([item])[0])
        self.assertIn("<b>Why:</b>", render_email([item], 20))


if __name__ == "__main__":
    unittest.main()
