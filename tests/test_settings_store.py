"""
Tests for core/settings_store.py — SettingsStore.

Covers:
  - default values when no file exists
  - get / update / save / load round-trip
  - deep-merge of nested dicts (gifs sub-dict)
  - corrupt file fallback
  - partial update doesn't wipe other keys
"""

import json

import pytest

from config import DEFAULT_SETTINGS
from core.settings_store import SettingsStore

# ── fixture ───────────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_store(tmp_path):
    return SettingsStore(path=tmp_path / "settings.json")


# ── defaults ──────────────────────────────────────────────────────────────────


class TestDefaults:
    def test_work_minutes_default(self, tmp_store):
        assert tmp_store.get("work_minutes") == DEFAULT_SETTINGS["work_minutes"]

    def test_opacity_default(self, tmp_store):
        assert tmp_store.get("opacity") == DEFAULT_SETTINGS["opacity"]

    def test_unknown_key_returns_none(self, tmp_store):
        assert tmp_store.get("nonexistent_key") is None

    def test_unknown_key_returns_default_param(self, tmp_store):
        assert tmp_store.get("nonexistent_key", 42) == 42

    def test_gifs_sub_dict_present(self, tmp_store):
        gifs = tmp_store.get("gifs")
        assert isinstance(gifs, dict)
        assert "work" in gifs
        assert "short_break" in gifs
        assert "long_break" in gifs


# ── get / update ──────────────────────────────────────────────────────────────


class TestGetUpdate:
    def test_update_changes_value(self, tmp_store):
        tmp_store.update({"work_minutes": 45})
        assert tmp_store.get("work_minutes") == 45

    def test_update_does_not_wipe_other_keys(self, tmp_store):
        tmp_store.update({"work_minutes": 45})
        assert (
            tmp_store.get("short_break_minutes")
            == DEFAULT_SETTINGS["short_break_minutes"]
        )

    def test_update_nested_dict(self, tmp_store):
        tmp_store.update({"gifs": {"work": "/path/to/work.gif"}})
        assert tmp_store.get("gifs")["work"] == "/path/to/work.gif"
        # other gif keys should still be there
        assert "short_break" in tmp_store.get("gifs")

    def test_update_multiple_keys_at_once(self, tmp_store):
        tmp_store.update({"work_minutes": 30, "opacity": 0.8})
        assert tmp_store.get("work_minutes") == 30
        assert tmp_store.get("opacity") == 0.8


# ── persistence ───────────────────────────────────────────────────────────────


class TestPersistence:
    def test_save_creates_file(self, tmp_path):
        path = tmp_path / "settings.json"
        SettingsStore(path=path)
        assert path.exists()

    def test_reload_recovers_updated_values(self, tmp_path):
        path = tmp_path / "settings.json"
        s1 = SettingsStore(path=path)
        s1.update({"work_minutes": 55})

        s2 = SettingsStore(path=path)
        assert s2.get("work_minutes") == 55

    def test_reload_recovers_nested_values(self, tmp_path):
        path = tmp_path / "settings.json"
        s1 = SettingsStore(path=path)
        s1.update({"gifs": {"work": "/my.gif"}})

        s2 = SettingsStore(path=path)
        assert s2.get("gifs")["work"] == "/my.gif"

    def test_corrupt_file_falls_back_to_defaults(self, tmp_path):
        path = tmp_path / "settings.json"
        path.write_text("this is not json", encoding="utf-8")
        store = SettingsStore(path=path)
        assert store.get("work_minutes") == DEFAULT_SETTINGS["work_minutes"]

    def test_partial_saved_file_fills_missing_keys(self, tmp_path):
        path = tmp_path / "settings.json"
        path.write_text(json.dumps({"work_minutes": 99}), encoding="utf-8")
        store = SettingsStore(path=path)
        assert store.get("work_minutes") == 99
        # default keys not in file should still be present
        assert (
            store.get("short_break_minutes") == DEFAULT_SETTINGS["short_break_minutes"]
        )


# ── deep merge ────────────────────────────────────────────────────────────────


class TestDeepMerge:
    def test_nested_key_doesnt_overwrite_sibling(self, tmp_path):
        path = tmp_path / "settings.json"
        path.write_text(
            json.dumps({"gifs": {"work": "work.gif"}}),
            encoding="utf-8",
        )
        store = SettingsStore(path=path)
        gifs = store.get("gifs")
        assert gifs["work"] == "work.gif"
        assert gifs["short_break"] == DEFAULT_SETTINGS["gifs"]["short_break"]
        assert gifs["long_break"] == DEFAULT_SETTINGS["gifs"]["long_break"]
