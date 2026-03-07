import io
import datetime as dt
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from daka import analytic_handler


class TestAnalyticHandler(unittest.TestCase):
    def test_display_width_handles_cjk_and_ansi(self):
        self.assertEqual(analytic_handler._display_width("abc"), 3)
        self.assertEqual(analytic_handler._display_width("任务"), 4)
        self.assertEqual(analytic_handler._display_width("\033[31m任务\033[0m"), 4)

    def test_pad_display_uses_terminal_width(self):
        padded = analytic_handler._pad_display("任务", 6)
        self.assertEqual(analytic_handler._display_width(padded), 6)

    def test_completion_bar_bounds_and_shape(self):
        self.assertEqual(analytic_handler._completion_bar(0), "[--------------------]")
        self.assertEqual(analytic_handler._completion_bar(100), "[####################]")
        self.assertEqual(analytic_handler._completion_bar(50), "[##########----------]")

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

    def test_summarize_completion_prints_percentage_for_current_year(self):
        year = dt.date.today().year
        data = {
            "resolutions": [
                {
                    "name": "Fitness",
                    "items": [
                        {
                            "name": "Pushups",
                            "checkins": [f"{year}-01-01", f"{year}-01-08", f"{year-1}-12-31"],
                        }
                    ],
                }
            ]
        }

        with patch.object(analytic_handler, "load_data", return_value=data), patch.object(
            analytic_handler, "_should_use_color", return_value=False
        ):
            out = io.StringIO()
            with redirect_stdout(out):
                analytic_handler.summarize_completion()

        days_in_year = 366 if dt.date(year, 12, 31).timetuple().tm_yday == 366 else 365
        total_weeks_in_year = (days_in_year + 6) // 7
        expected_day_ratio = f"2/{days_in_year}"
        expected_day_pct = f"{(2 / days_in_year) * 100:.2f}%"
        expected_week_ratio = f"2/{total_weeks_in_year}"
        expected_week_pct = f"{(2 / total_weeks_in_year) * 100:.2f}%"
        text = out.getvalue()
        self.assertIn("Yearly Summary", text)
        self.assertIn("Weekly Summary", text)
        self.assertIn("Fitness / Pushups", text)
        self.assertIn(expected_day_ratio, text)
        self.assertIn(expected_day_pct, text)
        self.assertIn(expected_week_ratio, text)
        self.assertIn(expected_week_pct, text)
        self.assertIn("[", text)
        self.assertIn("]", text)

    def test_summarize_completion_prints_none_when_no_tasks(self):
        with patch.object(analytic_handler, "load_data", return_value={"resolutions": []}):
            out = io.StringIO()
            with redirect_stdout(out):
                analytic_handler.summarize_completion()

        self.assertIn("(none)", out.getvalue())

    def test_summarize_completion_deduplicates_and_ignores_invalid_dates(self):
        year = dt.date.today().year
        data = {
            "resolutions": [
                {
                    "name": "Fitness",
                    "items": [
                        {
                            "name": "Pushups",
                            "checkins": [
                                f"{year}-01-01",
                                f"{year}-01-01",
                                f"{year}-01-02",
                                "not-a-date",
                                "",
                            ],
                        }
                    ],
                }
            ]
        }

        with patch.object(analytic_handler, "load_data", return_value=data), patch.object(
            analytic_handler, "_should_use_color", return_value=False
        ):
            out = io.StringIO()
            with redirect_stdout(out):
                analytic_handler.summarize_completion()

        days_in_year = 366 if dt.date(year, 12, 31).timetuple().tm_yday == 366 else 365
        total_weeks_in_year = (days_in_year + 6) // 7
        text = out.getvalue()
        self.assertIn(f"2/{days_in_year}", text)
        self.assertIn(f"1/{total_weeks_in_year}", text)

    def test_summarize_completion_counts_week_buckets_correctly(self):
        year = dt.date.today().year
        data = {
            "resolutions": [
                {
                    "name": "Fitness",
                    "items": [
                        {
                            "name": "Pushups",
                            # Jan 7 and Jan 8 fall into two different 7-day buckets.
                            "checkins": [f"{year}-01-07", f"{year}-01-08"],
                        }
                    ],
                }
            ]
        }

        with patch.object(analytic_handler, "load_data", return_value=data), patch.object(
            analytic_handler, "_should_use_color", return_value=False
        ):
            out = io.StringIO()
            with redirect_stdout(out):
                analytic_handler.summarize_completion()

        days_in_year = 366 if dt.date(year, 12, 31).timetuple().tm_yday == 366 else 365
        total_weeks_in_year = (days_in_year + 6) // 7
        text = out.getvalue()
        self.assertIn(f"2/{days_in_year}", text)
        self.assertIn(f"2/{total_weeks_in_year}", text)


if __name__ == "__main__":
    unittest.main()
