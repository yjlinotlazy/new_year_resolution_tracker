import unittest
from unittest.mock import patch

from daka import cli


class TestCli(unittest.TestCase):
    def test_main_summary_mode(self):
        with patch("sys.argv", ["daka", "-s"]), patch.object(
            cli, "summarize_all_checkins"
        ) as mock_summary, patch.object(cli, "parse_date") as mock_parse_date, patch.object(
            cli, "run"
        ) as mock_run, patch.object(
            cli, "rename_entities"
        ) as mock_rename:
            cli.main()

        mock_summary.assert_called_once()
        mock_parse_date.assert_not_called()
        mock_run.assert_not_called()
        mock_rename.assert_not_called()

    def test_main_rename_mode(self):
        with patch("sys.argv", ["daka", "--rename"]), patch.object(
            cli, "rename_entities"
        ) as mock_rename, patch.object(cli, "summarize_all_checkins") as mock_summary, patch.object(
            cli, "parse_date"
        ) as mock_parse_date, patch.object(
            cli, "run"
        ) as mock_run:
            cli.main()

        mock_rename.assert_called_once()
        mock_summary.assert_not_called()
        mock_parse_date.assert_not_called()
        mock_run.assert_not_called()

    def test_main_checkin_mode(self):
        with patch("sys.argv", ["daka", "-d", "2026-03-04"]), patch.object(
            cli, "parse_date", return_value="2026-03-04"
        ) as mock_parse_date, patch.object(cli, "run") as mock_run, patch.object(
            cli, "summarize_all_checkins"
        ) as mock_summary, patch.object(
            cli, "rename_entities"
        ) as mock_rename:
            cli.main()

        mock_parse_date.assert_called_once_with("2026-03-04")
        mock_run.assert_called_once_with("2026-03-04")
        mock_summary.assert_not_called()
        mock_rename.assert_not_called()


if __name__ == "__main__":
    unittest.main()
