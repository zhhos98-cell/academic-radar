import unittest

from academic_radar.config import RadarConfig, config_from_profile
from academic_radar.summary import summarize_config


class SummaryTests(unittest.TestCase):
    def test_config_from_profile_preserves_profile_name(self):
        config = config_from_profile({"name": "My Local Radar"})
        self.assertEqual(config.name, "My Local Radar")

    def test_summarize_config_reports_counts_and_paths(self):
        config = RadarConfig(
            name="Test Radar",
            opml_file=".radar/feeds.opml",
            bsky_watchlist_file=".radar/bsky_watchlist.txt",
            state_file=".radar/seen.json",
            event_terms=["call for papers"],
            core_field_terms=["history of science", "photography"],
            prestige_or_core_sources=["bshs"],
            negative_terms=["marketing"],
            bluesky_queries=['"call for papers" "history of science"'],
        )

        summary = summarize_config(config)

        self.assertIn("Name: Test Radar", summary)
        self.assertIn("OPML: .radar/feeds.opml", summary)
        self.assertIn("Event terms: 1", summary)
        self.assertIn("Field terms: 2", summary)
        self.assertIn("Public search queries: 1", summary)


if __name__ == "__main__":
    unittest.main()
