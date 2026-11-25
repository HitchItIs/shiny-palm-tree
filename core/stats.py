import json
from pathlib import Path


class StatsStorage:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else Path(__file__).resolve().parents[1] / "stats.json"
        self._stats = self._load()

    def _load(self) -> dict[str, dict[str, int]]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return {}
        if not isinstance(data, dict):
            return {}

        valid_stats: dict[str, dict[str, int]] = {}
        for category, values in data.items():
            if (
                isinstance(category, str)
                and isinstance(values, dict)
                and isinstance(values.get("points_earned"), int)
                and isinstance(values.get("max_points"), int)
                and values["points_earned"] >= 0
                and values["max_points"] >= 0
            ):
                valid_stats[category] = {
                    "points_earned": values["points_earned"],
                    "max_points": values["max_points"],
                }
        return valid_stats

    def progress(self, category: str) -> float:
        values = self._stats.get(category)
        if values is None or values["max_points"] == 0:
            return 0.0
        return values["points_earned"] / values["max_points"] * 100

    def record(self, category: str, points_earned: int, max_points: int) -> None:
        values = self._stats.setdefault(category, {"points_earned": 0, "max_points": 0})
        values["points_earned"] += points_earned
        values["max_points"] += max_points
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(self._stats, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except OSError:
            pass
