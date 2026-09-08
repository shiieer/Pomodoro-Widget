import json
from copy import deepcopy
from pathlib import Path

from config import DEFAULT_SETTINGS, SETTINGS_PATH


def _merge(default: dict, saved: dict) -> dict:
    result = deepcopy(default)
    for key, value in saved.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


class SettingsStore:
    def __init__(self, path: Path = SETTINGS_PATH):
        self.path = path
        self.data = deepcopy(DEFAULT_SETTINGS)
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.save()
            return
        try:
            saved = json.loads(self.path.read_text(encoding="utf-8"))
            self.data = _merge(DEFAULT_SETTINGS, saved)
        except (json.JSONDecodeError, OSError):
            self.data = deepcopy(DEFAULT_SETTINGS)

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def update(self, values: dict) -> None:
        self.data = _merge(self.data, values)
        self.save()
