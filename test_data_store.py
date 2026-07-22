import csv
import tempfile
import unittest
from pathlib import Path

from data_store import CsvStore, QuestionAnswer


class CsvStoreTest(unittest.TestCase):
    def test_creates_csv_and_round_trips_multiline_text(self):
        with tempfile.TemporaryDirectory() as folder:
            store = CsvStore(folder)
            item = QuestionAnswer("空はなぜ青い？", "光が\n散乱するためです。")
            store.append(item)

            self.assertEqual(store.read_all(), [item])
            self.assertTrue((Path(folder) / "data.csv").exists())

    def test_rejects_csv_without_required_headers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as file:
                csv.writer(file).writerows((("foo", "bar"), ("a", "b")))

            with self.assertRaises(ValueError):
                CsvStore(folder).read_all()


if __name__ == "__main__":
    unittest.main()
