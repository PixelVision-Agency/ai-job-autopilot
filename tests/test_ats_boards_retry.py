import importlib.util
import unittest
import urllib.error
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

CLI = Path(__file__).resolve().parents[1] / ".agents/skills/ats-boards-search/cli.py"
spec = importlib.util.spec_from_file_location("ats_boards_cli", CLI)
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


class BoardRetryTests(unittest.TestCase):
    """A board that times out once is retried; a 404 is not."""

    def run_search(self, board):
        args = SimpleNamespace(companies="x", query=None, days=14)
        with mock.patch.object(cli, "load_companies", return_value=[("ashby", "acme")]), \
                mock.patch.object(cli, "board", side_effect=board):
            return cli.search(args)

    def test_timeout_is_retried_once(self):
        calls = []

        def board(ats, slug):
            calls.append(slug)
            if len(calls) == 1:
                raise TimeoutError("The read operation timed out")
            return []

        out = self.run_search(board)
        self.assertEqual(len(calls), 2)
        self.assertEqual(out["meta"]["failed_boards"], [])

    def test_http_404_is_not_retried(self):
        calls = []

        def board(ats, slug):
            calls.append(slug)
            raise urllib.error.HTTPError("u", 404, "Not Found", None, None)

        out = self.run_search(board)
        self.assertEqual(len(calls), 1)
        self.assertIn("404", out["meta"]["failed_boards"][0]["error"])


class FilterTests(unittest.TestCase):
    JOBS = [{"id": "1", "title": "Senior Designer", "company": "Acme", "location": None, "date": None,
             "url": "u1", "workplace": "onsite"},
            {"id": "2", "title": "Design Intern", "company": "Acme", "location": None, "date": None,
             "url": "u2", "workplace": "remote"},
            {"id": "3", "title": "Accountant", "company": "Acme", "location": None, "date": None,
             "url": "u3", "workplace": None}]

    def run_search(self, **opts):
        args = SimpleNamespace(companies="x", query=None, exclude=None, days=14, no_onsite=False, **{})
        for key, value in opts.items():
            setattr(args, key, value)
        with mock.patch.object(cli, "load_companies", return_value=[("ashby", "acme")]), \
                mock.patch.object(cli, "board", return_value=self.JOBS):
            return [j["id"] for j in cli.search(args)["results"]]

    def test_no_keywords_keeps_everything(self):
        self.assertEqual(sorted(self.run_search()), ["1", "2", "3"])

    def test_include_exclude_and_onsite(self):
        self.assertEqual(sorted(self.run_search(query="design")), ["1", "2"])
        self.assertEqual(self.run_search(query="design", exclude="intern"), ["1"])
        self.assertEqual(self.run_search(query="design", exclude="intern", no_onsite=True), [])

    def test_missing_company_list_exits_with_a_hint(self):
        with self.assertRaises(SystemExit) as ctx:
            cli.load_companies(Path("/nonexistent/ats-companies.txt"))
        self.assertIn("ats-companies.txt", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
