import os
import sys
import winreg
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from widget_model import SettingsManager, SystemMetricsWorker
from widget_settings_view import SettingsWindow

def is_startup_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, "OmniBarWidget")
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def set_startup_enabled(enable):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
        if enable:
            exe_path = sys.executable.replace("python.exe", "pythonw.exe")
            main_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
            cmd = f'"{exe_path}" "{main_script}"'
            winreg.SetValueEx(key, "OmniBarWidget", 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, "OmniBarWidget")
            except Exception:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error setting registry startup: {e}")
        return False


def create_tray_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Outer circle cyan/aqua
    painter.setBrush(QBrush(QColor(0, 229, 255)))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(4, 4, 56, 56)
    
    # Inner dark core
    painter.setBrush(QBrush(QColor(18, 18, 18)))
    painter.drawEllipse(12, 12, 40, 40)
    
    # Center dot
    painter.setBrush(QBrush(QColor(0, 230, 118)))
    painter.drawEllipse(24, 24, 16, 16)
    painter.end()
    
    return QIcon(pixmap)


class WidgetController:
    def __init__(self):
        self.settings = SettingsManager()
        self.widget_bar = None
        self.settings_window = None
        
        # Start hardware monitoring thread
        self.metrics_worker = SystemMetricsWorker(self.settings)
        self.metrics_worker.metrics_updated.connect(self.on_metrics_updated)
        self.metrics_worker.start()

        self.setup_tray_icon()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(create_tray_icon())
        self.tray_icon.setToolTip("OmniBar Hardware Widget Suite (Running)")
        
        self.tray_menu = QMenu()

        # Dock Positions Submenu / Actions
        self.act_top = QAction("Dock to Top (Horizontal Row)", self.tray_menu)
        self.act_top.triggered.connect(lambda: self.set_dock_position("top"))
        self.tray_menu.addAction(self.act_top)

        self.act_bottom = QAction("Dock to Bottom (Horizontal Row)", self.tray_menu)
        self.act_bottom.triggered.connect(lambda: self.set_dock_position("bottom"))
        self.tray_menu.addAction(self.act_bottom)

        self.act_left = QAction("Dock to Left (Vertical Column)", self.tray_menu)
        self.act_left.triggered.connect(lambda: self.set_dock_position("left"))
        self.tray_menu.addAction(self.act_left)

        self.act_right = QAction("Dock to Right (Vertical Column)", self.tray_menu)
        self.act_right.triggered.connect(lambda: self.set_dock_position("right"))
        self.tray_menu.addAction(self.act_right)

        self.tray_menu.addSeparator()

        # Auto-hide toggle
        self.act_autohide = QAction("Auto-Hide at Screen Edge", self.tray_menu)
        self.act_autohide.setCheckable(True)
        self.act_autohide.setChecked(self.settings.get("auto_hide", False))
        self.act_autohide.triggered.connect(self.toggle_autohide)
        self.tray_menu.addAction(self.act_autohide)

        # Run at Windows Startup toggle
        self.act_startup = QAction("Start automatically with Windows", self.tray_menu)
        self.act_startup.setCheckable(True)
        self.act_startup.setChecked(is_startup_enabled())
        self.act_startup.triggered.connect(self.toggle_startup)
        self.tray_menu.addAction(self.act_startup)

        self.tray_menu.addSeparator()

        # Open Settings
        act_settings = QAction("⚙ Configuration Settings...", self.tray_menu)
        act_settings.triggered.connect(self.show_settings)
        self.tray_menu.addAction(act_settings)

        # Quit
        act_quit = QAction("✕ Quit OmniBar", self.tray_menu)
        act_quit.triggered.connect(QApplication.instance().quit)
        self.tray_menu.addAction(act_quit)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_settings()

    def set_dock_position(self, pos):
        self.settings.set("position", pos)
        self.apply_configuration()

    def toggle_autohide(self, checked):
        self.settings.set("auto_hide", checked)
        self.apply_configuration()

    def toggle_startup(self, checked):
        set_startup_enabled(checked)

    def set_widget_bar(self, widget_bar):
        self.widget_bar = widget_bar

    def on_metrics_updated(self, metrics):
        if self.widget_bar:
            self.widget_bar.update_metrics(metrics)

    def show_settings(self):
        self.settings_window = SettingsWindow(self.settings, self)
        self.settings_window.show()

    def apply_configuration(self):
        if self.widget_bar:
            self.widget_bar.setup_ui()
            self.widget_bar.apply_theme()
            self.widget_bar.reposition_and_resize()
        # Keep tray menu state synced
        if hasattr(self, "act_autohide"):
            self.act_autohide.setChecked(self.settings.get("auto_hide", False))

    def shutdown(self):
        if hasattr(self, "tray_icon") and self.tray_icon:
            self.tray_icon.hide()
        self.metrics_worker.stop()
