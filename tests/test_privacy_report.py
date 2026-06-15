import unittest

from academic_radar.config import RadarConfig
from academic_radar.privacy_report import OK, WARN, build_privacy_report, format_privacy_report


class PrivacyReportTests(unittest.TestCase):
    def test_private_runtime_paths_are_ok(self):
        config = RadarConfig(
            opml_file=".radar/feeds.opml",
            bsky_watchlist_file=".radar\watchlist.txt",
            state_file=".radar/seen.json",
        )
        config.name = "Privacy Test"

        report = build_privacy_report(config, env={})

        self.assertEqual(report["profile"], "Privacy Test")
        self.assertTrue(all(item["status"] == OK for item in report["local_files"]))

    def test_repository_paths_warn_for_personal_runtime_data(self):
        config = RadarConfig(
            opml_file="config/feeds.opml",
            bsky_watchlist_file="examples/watchlist.txt",
            state_file="sent_items.json",
        )

        report = build_privacy_report(config, env={})
        statuses = {item["label"]: item["status"] for item in report["local_files"]}

        self.assertEqual(statuses["OPML feed list"], WARN)
        self.assertEqual(statuses["Bluesky watchlist"], WARN)
        self.assertEqual(statuses["Seen-link state"], OK)

    def test_email_values_are_not_rendered(self):
        config = RadarConfig(
            opml_file=".radar/feeds.opml",
            bsky_watchlist_file=".radar/watchlist.txt",
            state_file=".radar/seen.json",
        )
        env = {
            "SMTP_USER": "alice@example.com",
            "SMTP_PASS": "super-secret",
            "TO_EMAIL": "bob@example.com",
        }

        text = format_privacy_report(build_privacy_report(config, env=env))

        self.assertIn("Email delivery", text)
        self.assertIn("SMTP delivery is configured", text)
        self.assertNotIn("alice@example.com", text)
        self.assertNotIn("bob@example.com", text)
        self.assertNotIn("super-secret", text)


if __name__ == "__main__":
    unittest.main()
