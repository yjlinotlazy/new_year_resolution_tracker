import csv
import json
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from daka import data_loader


class TestDataLoader(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        base = Path(self.temp_dir.name)
        self.config_dir = base / ".config" / "daka"
        self.resolutions_file = self.config_dir / "resolutions.json"
        self.data_file = self.config_dir / "data.csv"

        self.stack = ExitStack()
        self.stack.enter_context(patch.object(data_loader, "CONFIG_DIR", self.config_dir))
        self.stack.enter_context(patch.object(data_loader, "RESOLUTIONS_FILE", self.resolutions_file))
        self.stack.enter_context(patch.object(data_loader, "DATA_FILE", self.data_file))

    def tearDown(self):
        self.stack.close()
        self.temp_dir.cleanup()

    def test_save_resolutions_writes_structure(self):
        data = {
            "resolutions": [
                {
                    "name": " Fitness ",
                    "items": [{"name": " Pushups "}, {"name": ""}],
                }
            ]
        }

        data_loader.save_resolutions(data)

        with self.resolutions_file.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        self.assertEqual(
            payload,
            {"resolutions": [{"name": "Fitness", "items": [{"name": "Pushups"}]}]},
        )

    def test_save_checkins_writes_unique_sorted_rows(self):
        data = {
            "resolutions": [
                {
                    "name": "Fitness",
                    "items": [
                        {
                            "name": "Pushups",
                            "checkins": ["2026-01-03", "2026-01-01", "2026-01-03"],
                        }
                    ],
                }
            ]
        }

        data_loader.save_checkins(data)

        with self.data_file.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))

        self.assertEqual(rows[0], ["resolution", "item", "date"])
        self.assertEqual(rows[1:], [["Fitness", "Pushups", "2026-01-01"], ["Fitness", "Pushups", "2026-01-03"]])

    def test_load_data_merges_from_csv_when_json_missing(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with self.data_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["resolution", "item", "date"])
            writer.writerow(["Fitness", "Pushups", "2026-01-02"])
            writer.writerow(["Fitness", "Pushups", "2026-01-01"])
            writer.writerow(["Fitness", "Pushups", "2026-01-02"])
            writer.writerow(["Art", "Sketch", "2026-01-05"])

        loaded = data_loader.load_data()

        self.assertEqual(len(loaded["resolutions"]), 2)
        fitness = next(r for r in loaded["resolutions"] if r["name"] == "Fitness")
        pushups = next(i for i in fitness["items"] if i["name"] == "Pushups")
        self.assertEqual(pushups["checkins"], ["2026-01-01", "2026-01-02"])


if __name__ == "__main__":
    unittest.main()
