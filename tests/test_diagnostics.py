import tempfile
import unittest
from pathlib import Path

from academic_radar.config import RadarConfig
from academic_radar.diagnostics import ERROR, OK, WARN, diagnose_config, diagnostics_exit_code, format_diagnostics


class DiagnosticsTests(unittest.TestCase):
    def test_diagnose_config_reports_local_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            opml = root / "feeds.opml"
            watchlist = root / "watchlist.txt"
            state = root / "seen.json"
            opml.write_text(
                '<?xml version="1.0"?><opml version="2.0"><body><outline text="Example" xmlUrl="https://example.org/feed.xml" /></body></opml>',
                encoding="utf-8",
            )
            watchlist.write_text("example.bsky.social\n", encoding="utf-8")
            config = RadarConfig(opml_file=str(opml), bsky_watchlist_file=str(watchlist), state_file=str(state))

            results = diagnose_config(config)
            self.assertEqual(diagnostics_exit_code(results), 0)
            self.assertTrue(any(result["status"] == OK and result["check"] == "opml" for result in results))
            self.assertTrue(any(result["status"] == OK and result["check"] == "watchlist" for result in results))
            self.assertIn("Academic Radar diagnostics:", format_diagnostics(results))

    def test_diagnose_config_warns_for_missing_input_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = RadarConfig(
                opml_file=str(root / "missing.opml"),
                bsky_watchlist_file=str(root / "missing.txt"),
                state_file=str(root / "seen.json"),
            )
            results = diagnose_config(config)
            self.assertEqual(diagnostics_exit_code(results), 0)
            self.assertTrue(any(result["status"] == WARN and result["check"] == "opml" for result in results))
            self.assertTrue(any(result["status"] == WARN and result["check"] == "watchlist" for result in results))

    def test_diagnose_config_errors_for_invalid_settings(self):
        config = RadarConfig(max_email_items=0)
            
        results = diagnose_config(config)
        self.assertEqual(diagnostics_exit_code(results), 1)
        self.assertTrue(any(result["status"] == ERROR and result["check"] == "max_email_items" for result in results))


if __name__ == "__main__":
    unittest.main()
