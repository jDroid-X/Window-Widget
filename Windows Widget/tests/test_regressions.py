import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

from models.widget_model import DEFAULT_SETTINGS, SettingsManager
from views.widget_view import WidgetBar

APP = None


class _Controller:
    def show_settings(self):
        pass

    def apply_configuration(self):
        pass


def _app():
    global APP
    APP = QApplication.instance() or QApplication([])
    return APP


def test_widget_accepts_metrics_immediately_after_construction(tmp_path):
    _app()
    settings = SettingsManager(str(tmp_path / "settings.json"))
    bar = WidgetBar(settings, _Controller())

    bar.update_metrics({})

    assert bar.update_tick == 1
    assert bar.containers
    bar.close()


def test_sync_theme_is_a_persisted_setting(tmp_path):
    settings = SettingsManager(str(tmp_path / "settings.json"))
    settings.set("sync_windows_theme", True)

    loaded = SettingsManager(str(tmp_path / "settings.json"))

    assert "sync_windows_theme" in DEFAULT_SETTINGS
    assert loaded.get("sync_windows_theme") is True


def test_invalid_threshold_order_is_normalized(tmp_path):
    settings = SettingsManager(str(tmp_path / "settings.json"))
    settings.set_batch({"cpu_warn": 95, "cpu_crit": 15})

    assert settings.get("cpu_warn") < settings.get("cpu_crit")


def test_settings_window_opens_without_crash(tmp_path):
    _app()
    from views.widget_settings_view import SettingsWindow
    settings = SettingsManager(str(tmp_path / "settings.json"))
    win = SettingsWindow(settings, _Controller())
    assert win.windowTitle() == "OmniBar Configuration"
    win.close()

