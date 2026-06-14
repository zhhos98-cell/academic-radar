import json
import tempfile
import unittest
from pathlib import Path

from academic_radar.presets import available_presets, merge_presets
from academic_radar.setup import build_opml, normalize_bsky_handle, parse_feed_arg, write_first_run_files


class SetupTests(unittest.TestCase):
    def test_parse_feed_arg_accepts_title_url_pair(self):
        self.assertEqual(parse_feed_arg("Example=https://example.org/feed.xml"), ("Example", "https://example.org/feed.xml"))

    def test_normalize_bsky_handle_removes_at_prefix(self):
        self.assertEqual(normalize_bsky_handle("@example.bsky.social"), "example.bsky.social")

    def test_build_opml_escapes_values(self):
        opml = build_opml([("A & B", "https://example.org/?a=1&b=2")])
        self.assertIn("A &amp; B", opml)
        self.assertIn("https://example.org/?a=1&amp;b=2", opml)

    def test_presets_are_available(self):
        self.assertIn("hps", available_presets())
        self.assertIn("photography-history", available_presets())
        self.assertIn("scientific-instruments", available_presets())

    def test_merge_presets_accepts_comma_separated_names(self):
        merged = merge_presets(["photography-history,scientific-instruments"])
        self.assertIn("photographic history", merged["field_terms"])
        self.assertIn("calibration", merged["field_terms"])

    def test_merge_presets_rejects_unknown_name(self):
        with self.assertRaises(ValueError):
            merge_presets(["unknown-preset"])

    def test_write_first_run_files_creates_local_private_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            profile_path = Path(tmpdir) / ".radar" / "profiles" / "local.json"
            result = write_first_run_files(
                profile_path=profile_path,
                field_terms=["photographic history"],
                bsky_handles=["@example.bsky.social"],
                rss_feeds=["Example=https://example.org/feed.xml"],
            )
            self.assertTrue(Path(result["profile"]).exists())
            self.assertTrue(Path(result["opml"]).exists())
            self.assertTrue(Path(result["watchlist"]).exists())

            profile = json.loads(Path(result["profile"]).read_text(encoding="utf-8"))
            self.assertIn("photographic history", profile["scoring"]["core_field_terms"])
            self.assertIn('"call for papers" "photographic history"', profile["bluesky"]["queries"])
            self.assertEqual(profile["files"]["state"], str(Path(tmpdir) / ".radar" / "seen.json"))

    def test_write_first_run_files_applies_presets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            profile_path = Path(tmpdir) / ".radar" / "profiles" / "local.json"
            result = write_first_run_files(
                profile_path=profile_path,
                presets=["photography-history", "scientific-instruments"],
            )
            profile = json.loads(Path(result["profile"]).read_text(encoding="utf-8"))
            self.assertIn("history of photography", profile["scoring"]["core_field_terms"])
            self.assertIn("calibration", profile["scoring"]["core_field_terms"])
            self.assertIn('"call for papers" "history of photography"', profile["bluesky"]["queries"])


if __name__ == "__main__":
    unittest.main()
