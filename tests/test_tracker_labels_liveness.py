"""tools/tracker_labels.py, tools/liveness.py and tools/patterns.py: the pure parts, no network."""
import unittest

from tools.liveness import api_target, page_signal
from tools.patterns import ats, fit_band
from tools.tracker_labels import CHANNELS, ROLE_TYPES, normalize_channel, normalize_role_type


class Labels(unittest.TestCase):
    def test_role_types(self):
        cases = [
            ("Product Designer", "", "product-design"),
            ("product design", "", "product-design"),
            ("AI product design", "", "product-design"),
            ("Design Engineer / Front-end", "", "design-engineering"),
            ("AI solutions engineering", "", "solutions"),
            ("Front-end engineering", "", "frontend"),
            ("Full-time", "Senior Product Designer", "product-design"),  # junk -> title
            ("", "Senior Designer (Berlin)", "product-design"),
            ("Real estate agent", "Real Estate Agent", "other"),
            ("", "Product Manager", "product-management"),
            ("", "Senior Data Analyst", "data"),
            ("", "Backend Engineer (Go)", "backend"),
            ("", "Site Reliability Engineer", "devops"),
            ("", "iOS Developer", "mobile"),
        ]
        for role_type, title, expected in cases:
            with self.subTest(role_type=role_type, title=title):
                self.assertEqual(normalize_role_type(role_type, title), expected)

    def test_channels(self):
        cases = [
            ("LinkedIn job alert (Easy Apply)", "", "email-alert"),
            ("LinkedIn Easy Apply", "", "linkedin"),
            ("portal", "https://www.linkedin.com/jobs/view/1", "linkedin"),
            ("portal", "https://himalayas.app/x", "job-board"),
            ("Company careers (Ashby)", "", "careers-page"),
            ("online", "", "careers-page"),
            ("Hacker News Who is hiring (Notion form)", "", "hn"),
        ]
        for channel, source, expected in cases:
            with self.subTest(channel=channel):
                self.assertEqual(normalize_channel(channel, source), expected)

    def test_canonical_values_are_stable(self):
        for value in ROLE_TYPES:
            self.assertEqual(normalize_role_type(value, "Senior Designer"), value)
        for value in CHANNELS:
            self.assertEqual(normalize_channel(value, ""), value)


class Liveness(unittest.TestCase):
    def test_closure_wording(self):
        self.assertTrue(page_signal("<p>No longer accepting applications</p>"))
        self.assertTrue(page_signal("Cette offre n’est plus. This job has expired."))
        self.assertTrue(page_signal("The position has been filled."))
        self.assertTrue(page_signal("The job ad is no longer active"))  # djinni
        self.assertIsNone(page_signal("Once the application form has been filled, we reply."))
        self.assertIsNone(page_signal("This role is closed-loop control of the platform."))
        self.assertIsNone(page_signal("<h1>Senior Frontend Engineer</h1><button>Apply</button>"))

    def test_api_targets(self):
        self.assertEqual(api_target("https://job-boards.greenhouse.io/figma/jobs/123")[1],
                         "https://boards-api.greenhouse.io/v1/boards/figma/jobs/123")
        self.assertEqual(api_target("https://boards.greenhouse.io/embed/job_app?for=acme&gh_jid=55")[1],
                         "https://boards-api.greenhouse.io/v1/boards/acme/jobs/55")
        self.assertEqual(api_target("https://jobs.eu.lever.co/acme/abc-1/apply")[1],
                         "https://api.eu.lever.co/v0/postings/acme/abc-1")
        self.assertEqual(api_target("https://jobs.ashbyhq.com/acme/uuid-1?utm_source=x")[2], "uuid-1")
        self.assertEqual(api_target("https://www.linkedin.com/jobs/view/senior-dev-at-x-4481886608/")[2],
                         "4481886608")
        self.assertIsNone(api_target("https://evil-greenhouse.example/jobs/1"))
        self.assertIsNone(api_target("https://acme.com/careers/frontend"))


class Patterns(unittest.TestCase):
    def test_helpers(self):
        self.assertEqual(fit_band("62"), "60-69")
        self.assertEqual(fit_band(""), "no score")
        self.assertEqual(ats("https://jobs.ashbyhq.com/acme/1"), "ashby")
        self.assertEqual(ats(""), "no url")


class CustomRoleTypes(unittest.TestCase):
    def test_profile_rules_come_first(self):
        import tempfile
        from pathlib import Path
        from unittest import mock

        import tools.tracker_labels as tl
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "role_types.txt"
            path.write_text("# my families\nnursing nurse|midwife\nproduct-design product\n", encoding="utf-8")
            with mock.patch.object(tl, "ROLE_FILE", path):
                rules = tl._load_rules()
        self.assertEqual(rules, (("nursing", "nurse|midwife"), ("product-design", "product")))


if __name__ == "__main__":
    unittest.main()
