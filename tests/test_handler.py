import datetime as dt
import unittest
from unittest.mock import patch

from daka import handler


class TestHandler(unittest.TestCase):
    def test_parse_date_defaults_to_today(self):
        self.assertEqual(handler.parse_date(None), dt.date.today().isoformat())

    def test_parse_date_invalid_raises(self):
        with self.assertRaises(SystemExit):
            handler.parse_date("2026-02-30")

    def test_ask_choice_back(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(handler.ask_choice(["a"], "prompt"), ("back", None))

    def test_ask_choice_quit(self):
        with patch("builtins.input", return_value="q"):
            self.assertEqual(handler.ask_choice(["a"], "prompt"), ("quit", None))

    def test_ask_choice_question_is_add(self):
        with patch("builtins.input", return_value="question"):
            self.assertEqual(handler.ask_choice(["a"], "prompt"), ("add", "question"))

    def test_ask_choice_select(self):
        with patch("builtins.input", return_value="1"):
            self.assertEqual(handler.ask_choice(["a", "b"], "prompt"), ("select", 0))

    def test_ask_choice_add(self):
        with patch("builtins.input", return_value="new item"):
            self.assertEqual(handler.ask_choice(["a"], "prompt"), ("add", "new item"))

    def test_check_in_deduplicates_and_sorts(self):
        item = {"name": "Pushups", "checkins": ["2026-01-03"]}

        self.assertTrue(handler.check_in(item, "2026-01-02"))
        self.assertFalse(handler.check_in(item, "2026-01-02"))
        self.assertEqual(item["checkins"], ["2026-01-02", "2026-01-03"])

    def test_run_quits_on_single_q(self):
        with patch("builtins.input", side_effect=["q"]), patch.object(
            handler, "load_data", return_value={"resolutions": []}
        ), patch.object(handler, "save_resolutions") as mock_save_resolutions, patch.object(
            handler, "save_checkins"
        ) as mock_save_checkins:
            handler.run("2026-03-04")

        mock_save_resolutions.assert_not_called()
        mock_save_checkins.assert_not_called()

    def test_run_question_is_new_item_not_quit(self):
        data = {"resolutions": [{"name": "study", "items": []}]}

        # Select resolution 1 -> add item "question" -> back item menu -> back top menu.
        with patch("builtins.input", side_effect=["1", "question", "", ""]), patch.object(
            handler, "load_data", return_value=data
        ), patch.object(handler, "save_resolutions") as mock_save_resolutions, patch.object(
            handler, "save_checkins"
        ) as mock_save_checkins:
            handler.run("2026-03-04")

        self.assertEqual(data["resolutions"][0]["items"][0]["name"], "question")
        self.assertEqual(data["resolutions"][0]["items"][0]["checkins"], ["2026-03-04"])
        mock_save_resolutions.assert_called_once()
        mock_save_checkins.assert_called_once()


if __name__ == "__main__":
    unittest.main()
