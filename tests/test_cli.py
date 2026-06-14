import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from academic_radar.cli import main


class CliTests(unittest.TestCase):
    def run_cli(self, args):
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(args)
        return exit_code, output.getvalue()

    def test_list_presets_cli_prints_known_presets(self):
        exit_code, output = self.run_cli(["--list-presets"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Available Academic Radar presets:", output)
        self.assertIn("hps:", output)
        self.assertIn("photography-history:", output)

    def test_summary_cli_uses_profile_without_network(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            profile = Path(tmpdir) / "profile.json"
            profile.write_text(
                json.dumps(
                    {
                        "name": "CLI Summary Radar",
                        "files": {
                            "opml": "feeds.opml",
                            "bsky_watchlist": "watchlist.txt",
                            "state": "seen.json",
                        },
                        "settings": {
                            "max_email_items": 7,
                        },
                        "scoring": {
                            "event_terms": ["call for papers"],
                            "core_field_terms": ["history of science"],
                        },
                        "bluesky": {
                            "queries": ['"call for papers" "history of science"'],
                        },
                    }
                ),
                encoding="utf-8",
            )

            exit_code, output = self.run_cli(["--config", str(profile), "--summary"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Name: CLI Summary Radar", output)
        self.assertIn("OPML: feeds.opml", output)
        self.assertIn("Max digest items: 7", output)
        self.assertIn("Public search queries: 1", output)

    def test_init_cli_prints_summary_next_step(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            profile = Path(tmpdir) / ".radar" / "profiles" / "local.json"

            exit_code, output = self.run_cli(
                [
                    "--init",
                    "--init-profile",
                    str(profile),
                    "--preset",
                    "hps",
                    "--bsky-handle",
                    "@example.bsky.social",
                    "--rss-feed",
                    "Example=https://example.org/feed.xml",
                ]
            )

            self.assertTrue(profile.exists())

        self.assertEqual(exit_code, 0)
        self.assertIn("Created local Academic Radar files:", output)
        self.assertIn("Inspect the profile with:", output)
        self.assertIn("--summary", output)


if __name__ == "__main__":
    unittest.main()
