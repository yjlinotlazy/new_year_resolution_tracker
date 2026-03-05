import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from daka import analytic_handler


class TestAnalyticHandler(unittest.TestCase):
    def test_resolution_color_map_assigns_different_colors(self):
        data = {
            "resolutions": [
                {"name": "Fitness", "items": []},
                {"name": "Art", "items": []},
            ]
        }
        colors = analytic_handler._resolution_color_map(data)
        self.assertIn("Fitness", colors)
        self.assertIn("Art", colors)
        self.assertNotEqual(colors["Fitness"], colors["Art"])

    def test_summarize_all_checkins_prints_none_when_empty(self):
        with patch.object(analytic_handler, "load_data", return_value={"resolutions": []}):
            out = io.StringIO()
            with redirect_stdout(out):
                analytic_handler.summarize_all_checkins()

        self.assertIn("Summary", out.getvalue())
        self.assertIn("(none)", out.getvalue())

    def test_summarize_all_checkins_prints_all_items(self):
        data = {
            "resolutions": [
                {
                    "name": "Fitness",
                    "items": [
                        {"name": "Pushups", "checkins": ["2026-01-02", "2026-01-01"]},
                        {"name": "Run", "checkins": ["2026-01-03"]},
                    ],
                }
            ]
        }

        with patch.object(analytic_handler, "load_data", return_value=data):
            out = io.StringIO()
            with redirect_stdout(out):
                analytic_handler.summarize_all_checkins()

        text = out.getvalue()
        self.assertIn("Fitness / Pushups: 2", text)
        self.assertIn("2026-01-01, 2026-01-02", text)
        self.assertIn("Fitness / Run: 1", text)

    def test_summarize_all_checkins_uses_ansi_color_when_enabled(self):
        data = {
            "resolutions": [
                {
                    "name": "Fitness",
                    "items": [{"name": "Pushups", "checkins": ["2026-01-01"]}],
                },
                {
                    "name": "Art",
                    "items": [{"name": "Sketch", "checkins": ["2026-01-02"]}],
                },
            ]
        }

        with patch.object(analytic_handler, "load_data", return_value=data), patch.object(
            analytic_handler, "_should_use_color", return_value=True
        ):
            out = io.StringIO()
            with redirect_stdout(out):
                analytic_handler.summarize_all_checkins()

        text = out.getvalue()
        self.assertIn("\033[", text)
        self.assertIn("Fitness", text)
        self.assertIn("Art", text)


if __name__ == "__main__":
    unittest.main()
