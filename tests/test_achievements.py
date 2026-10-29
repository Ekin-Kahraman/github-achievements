import json
from pathlib import Path
import subprocess
import sys
import unittest

from checker import fetch_profile, parse_badges
from progress import build_report

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "catalog.json").read_text())
FIXTURE = Path(__file__).with_name("profile.html")


class ProfileTests(unittest.TestCase):
    def test_mobile_duplicates_and_unrelated_images(self):
        badges = parse_badges(FIXTURE.read_text())
        self.assertEqual(set(badges), {"pull-shark", "pair-extraordinaire", "quickdraw"})
        self.assertEqual(badges["pull-shark"]["tier"], "silver")

    def test_unknown_asset_is_not_assumed_to_be_default(self):
        badges = parse_badges('<img class="achievement-badge-sidebar" alt="Achievement: YOLO" src="new-format.svg">')
        row = next(r for r in build_report(CATALOG, badges) if r["id"] == "yolo")
        self.assertTrue(row["visible"])
        self.assertEqual(row["observed_tier"], "unknown")
        self.assertIsNone(row["target"])

    def test_higher_tier_wins_duplicate(self):
        badges = parse_badges(''.join(
            f'<img class="achievement-badge-sidebar" alt="Achievement: Pull Shark" src="pull-shark-{tier}-abc.png">'
            for tier in ["default", "gold", "silver"]
        ))
        self.assertEqual(badges["pull-shark"]["tier"], "gold")

    def test_reject_invalid_username_before_network(self):
        for username in ["../settings", "a?tab=stars", "", "-invalid", "a" * 40]:
            with self.subTest(username=username), self.assertRaises(ValueError):
                fetch_profile(username)


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.badges = parse_badges(FIXTURE.read_text())

    def row(self, slug, counts=None):
        return next(r for r in build_report(CATALOG, self.badges, counts) if r["id"] == slug)

    def test_badge_does_not_invent_event_count(self):
        row = self.row("pair-extraordinaire")
        self.assertEqual(row["target"], 48)
        self.assertIsNone(row["supplied_count"])
        self.assertIsNone(row["remaining"])

    def test_explicit_count_and_pending_award(self):
        self.assertEqual(self.row("pair-extraordinaire", {"pair-extraordinaire": 42})["remaining"], 6)
        row = self.row("pair-extraordinaire", {"pair-extraordinaire": 48})
        self.assertEqual(row["remaining"], 0)
        self.assertEqual(row["observed_tier"], "silver")

    def test_not_visible_does_not_mean_never_earned(self):
        row = self.row("galaxy-brain")
        self.assertFalse(row["visible"])
        self.assertIsNone(row["supplied_count"])
        self.assertEqual(row["target"], 2)

    def test_single_tier_badge_has_no_further_target(self):
        self.assertIsNone(self.row("quickdraw")["target"])

    def test_bad_count_input_is_rejected(self):
        for counts in [{"quickdraw": -1}, {"yolo": True}, {"yolo": 1.2}, {"typo": 1}, []]:
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                build_report(CATALOG, self.badges, counts)


class CommandTests(unittest.TestCase):
    def test_json_report_works_offline(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "cli.py"), "example", "--html", str(FIXTURE), "--json"],
            capture_output=True, text=True, check=True,
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["username"], "example")
        self.assertEqual(len(report["achievements"]), 7)

    def test_missing_html_file_has_clear_error(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "cli.py"), "example", "--html", str(ROOT / "missing.html")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stderr)


if __name__ == "__main__":
    unittest.main()
