"""
Additional regression and integration tests for OmniBar.
Covers: settings persistence, metrics worker init, atomic saves, mutex safety,
threshold normalization, and GPU fallback.
"""
import os
import json
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMutexLocker

from models.widget_model import (
    DEFAULT_SETTINGS, THEMES, SettingsManager, SystemMetricsWorker
)

APP = None


def _app():
    global APP
    APP = QApplication.instance() or QApplication([])
    return APP


# ── SettingsManager Tests ────────────────────────────────────────────────────

class TestSettingsManager:
    """Tests for SettingsManager load/save/normalize behaviour."""

    def test_default_settings_contain_all_expected_keys(self):
        expected_keys = {
            "position", "auto_hide", "opacity", "icon_size", "theme",
            "sync_windows_theme", "custom_bg_enabled", "custom_bg_color",
            "custom_border_enabled", "custom_border_color",
            "cpu_warn", "cpu_crit", "ram_warn", "ram_crit",
            "gpu_warn", "gpu_crit", "items", "drive_letters", "monitor_index"
        }
        assert expected_keys.issubset(DEFAULT_SETTINGS.keys())

    def test_load_creates_file_on_save(self, tmp_path):
        _app()
        path = str(tmp_path / "test_settings.json")
        sm = SettingsManager(path)
        sm.set("opacity", 50)
        assert os.path.exists(path)
        with open(path, "r") as f:
            data = json.load(f)
        assert data["opacity"] == 50

    def test_atomic_save_produces_valid_json(self, tmp_path):
        _app()
        path = str(tmp_path / "atomic_test.json")
        sm = SettingsManager(path)
        # Rapid successive saves should not corrupt the file
        for i in range(10):
            sm.set("opacity", i * 10)
        with open(path, "r") as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert data["opacity"] == 90

    def test_unknown_keys_in_json_are_ignored(self, tmp_path):
        _app()
        path = str(tmp_path / "extra_keys.json")
        with open(path, "w") as f:
            json.dump({"position": "bottom", "unknown_future_key": 42}, f)
        sm = SettingsManager(path)
        assert sm.get("position") == "bottom"
        # Unknown key should not appear in settings dict
        assert sm.get("unknown_future_key") is None

    def test_corrupted_json_falls_back_to_defaults(self, tmp_path):
        _app()
        path = str(tmp_path / "corrupt.json")
        with open(path, "w") as f:
            f.write("{corrupt json!")
        sm = SettingsManager(path)
        assert sm.get("position") == DEFAULT_SETTINGS["position"]
        assert sm.get("opacity") == DEFAULT_SETTINGS["opacity"]

    def test_set_batch_writes_multiple_keys_atomically(self, tmp_path):
        _app()
        path = str(tmp_path / "batch.json")
        sm = SettingsManager(path)
        sm.set_batch({"position": "left", "opacity": 75, "auto_hide": True})
        assert sm.get("position") == "left"
        assert sm.get("opacity") == 75
        assert sm.get("auto_hide") is True

    def test_invalid_position_normalized_to_default(self, tmp_path):
        _app()
        path = str(tmp_path / "invalid_pos.json")
        with open(path, "w") as f:
            json.dump({"position": "invalid_value"}, f)
        sm = SettingsManager(path)
        assert sm.get("position") == DEFAULT_SETTINGS["position"]

    def test_invalid_theme_normalized_to_default(self, tmp_path):
        _app()
        path = str(tmp_path / "invalid_theme.json")
        with open(path, "w") as f:
            json.dump({"theme": "nonexistent_theme"}, f)
        sm = SettingsManager(path)
        assert sm.get("theme") == DEFAULT_SETTINGS["theme"]

    def test_opacity_clamped_to_valid_range(self, tmp_path):
        _app()
        path = str(tmp_path / "opacity_clamp.json")
        sm = SettingsManager(path)
        sm.set("opacity", 200)
        assert sm.get("opacity") == 100
        sm.set("opacity", -50)
        assert sm.get("opacity") == 0

    def test_drive_letters_normalized_uppercase(self, tmp_path):
        _app()
        path = str(tmp_path / "drives.json")
        sm = SettingsManager(path)
        sm.set("drive_letters", ["c:", "d:", "e:"])
        drives = sm.get("drive_letters")
        assert all(d == d.upper() for d in drives)

    def test_warn_crit_threshold_enforcement(self, tmp_path):
        _app()
        path = str(tmp_path / "thresholds.json")
        sm = SettingsManager(path)
        # Set warn > crit — should be auto-corrected
        sm.set_batch({"cpu_warn": 90, "cpu_crit": 30})
        assert sm.get("cpu_warn") < sm.get("cpu_crit")
        sm.set_batch({"ram_warn": 85, "ram_crit": 20})
        assert sm.get("ram_warn") < sm.get("ram_crit")
        sm.set_batch({"gpu_warn": 99, "gpu_crit": 10})
        assert sm.get("gpu_warn") < sm.get("gpu_crit")


# ── SystemMetricsWorker Tests ────────────────────────────────────────────────

class TestSystemMetricsWorker:
    """Tests for SystemMetricsWorker initialization and cache fields."""

    def test_worker_initializes_all_cache_fields(self, tmp_path):
        _app()
        sm = SettingsManager(str(tmp_path / "worker_test.json"))
        worker = SystemMetricsWorker(sm)

        # All cached fields must exist at construction time
        assert hasattr(worker, "cached_ping")
        assert hasattr(worker, "cached_top_cpu")
        assert hasattr(worker, "cached_top_ram")
        assert hasattr(worker, "cached_drives")
        assert hasattr(worker, "cached_usb_drives")
        assert hasattr(worker, "cached_battery")
        assert hasattr(worker, "cached_wmi_gpu")
        assert hasattr(worker, "metrics_mutex")

        # Default values
        assert worker.cached_ping is None
        assert worker.cached_top_cpu == []
        assert worker.cached_top_ram == []
        assert worker.cached_drives == []
        assert isinstance(worker.cached_battery, dict)
        assert worker.cached_wmi_gpu is None

    def test_worker_has_cpu_metadata(self, tmp_path):
        _app()
        sm = SettingsManager(str(tmp_path / "cpu_meta.json"))
        worker = SystemMetricsWorker(sm)
        assert isinstance(worker.cpu_cores_phys, int)
        assert isinstance(worker.cpu_cores_logical, int)
        assert worker.cpu_cores_logical >= worker.cpu_cores_phys

    def test_trigger_drives_update_clears_cache(self, tmp_path):
        _app()
        sm = SettingsManager(str(tmp_path / "drives_trigger.json"))
        worker = SystemMetricsWorker(sm)
        # Pre-populate cached_drives
        with QMutexLocker(worker.metrics_mutex):
            worker.cached_drives = [{"name": "C:", "percent": 50}]
        # Trigger should clear it
        worker.trigger_drives_update()
        with QMutexLocker(worker.metrics_mutex):
            assert worker.cached_drives == []


# ── Theme Tests ──────────────────────────────────────────────────────────────

class TestThemes:
    """Tests for theme definitions and consistency."""

    def test_all_themes_have_required_keys(self):
        required_keys = {
            "bg_color", "border_color", "text_color", "accent_color",
            "hover_color", "danger_color", "progress_good",
            "progress_warn", "progress_high"
        }
        for name, theme in THEMES.items():
            missing = required_keys - set(theme.keys())
            assert not missing, f"Theme '{name}' is missing keys: {missing}"

    def test_bg_color_supports_opacity_format(self):
        for name, theme in THEMES.items():
            bg = theme["bg_color"]
            # Must contain {opacity} placeholder
            assert "{opacity}" in bg, f"Theme '{name}' bg_color missing {{opacity}} placeholder"
            # Should produce valid string when formatted
            formatted = bg.format(opacity=0.5)
            assert "0.5" in formatted

    def test_default_theme_exists_in_themes(self):
        default_theme = DEFAULT_SETTINGS["theme"]
        assert default_theme in THEMES

    def test_usb_card_and_group_separators(self):
        _app()
        from views.usb_display import UsbCard
        from views.group_separator import GroupSeparatorWidget
        card = UsbCard({})
        card.update_display({"usb_drives": [{"name": "E:", "label": "SANDISK", "percent": 45, "free": 16.0, "total": 32.0}]}, False, "#00FFCC")
        assert card.val.text() == "SANDISK 45%"
        sep = GroupSeparatorWidget("COMPUTE", False)
        assert sep.lbl.text() == "COMPUTE"
