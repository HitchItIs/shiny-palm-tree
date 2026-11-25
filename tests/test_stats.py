import tempfile
import unittest
from pathlib import Path

from core.stats import StatsStorage


class TestStatsStorage(unittest.TestCase):
    def test_records_and_loads_progress(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stats.json"
            stats = StatsStorage(path)
            self.assertEqual(stats.progress("raid"), 0)
            stats.record("raid", 2, 4)
            stats.record("raid", 3, 3)

            reloaded = StatsStorage(path)
            self.assertEqual(reloaded.progress("raid"), 5 / 7 * 100)

    def test_invalid_file_starts_with_empty_progress(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stats.json"
            path.write_text("invalid", encoding="utf-8")
            self.assertEqual(StatsStorage(path).progress("raid"), 0)


if __name__ == "__main__":
    unittest.main()
