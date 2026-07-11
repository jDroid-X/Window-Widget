import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, 
    QSlider, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox
)

class SettingsWindow(QDialog):
    def __init__(self, settings_manager, controller):
        super().__init__()
        self.settings = settings_manager
        self.controller = controller
        
        self.setWindowTitle("OmniBar Configuration")
        self.setFixedSize(430, 570)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint)
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 1. Dock & Auto-Hide Options
        layout_group = QGroupBox("Layout & Dock Position")
        layout_grid = QVBoxLayout(layout_group)
        
        pos_layout = QHBoxLayout()
        pos_label = QLabel("Dock Position:")
        self.pos_combo = QComboBox()
        self.pos_combo.addItems(["Top", "Bottom", "Left", "Right"])
        current_pos = self.settings.get("position", "top").capitalize()
        self.pos_combo.setCurrentText(current_pos)
        
        pos_layout.addWidget(pos_label)
        pos_layout.addWidget(self.pos_combo)
        layout_grid.addLayout(pos_layout)

        self.hide_chk = QCheckBox("Auto-hide bar at edge (Hover 3px border to slide out)")
        self.hide_chk.setChecked(self.settings.get("auto_hide", False))
        layout_grid.addWidget(self.hide_chk)

        from widget_controller import is_startup_enabled, set_startup_enabled
        self.startup_chk = QCheckBox("Launch OmniBar automatically at Windows startup")
        self.startup_chk.setChecked(is_startup_enabled())
        layout_grid.addWidget(self.startup_chk)

        size_layout = QHBoxLayout()
        size_label = QLabel("Scale / Size:")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["Small", "Medium", "Large"])
        current_size = self.settings.get("icon_size", "medium").capitalize()
        self.size_combo.setCurrentText(current_size)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_combo)
        layout_grid.addLayout(size_layout)

        main_layout.addWidget(layout_group)

        # 2. Hardware Monitors
        items_group = QGroupBox("Visible Hardware Cards")
        items_layout = QVBoxLayout(items_group)
        
        self.item_chks = {}
        items_dict = self.settings.get("items", {})
        for key, name in [
            ("cpu", "💻 CPU Utilization & Celsius Temp"), 
            ("ram", "📊 RAM Utilization & Breakdown"), 
            ("gpu", "🎮 GPU Load & Temp"), 
            ("drives", "💾 Storage & USB Partitions"), 
            ("wifi", "📶 Network Speeds (Upload/Download)"),
            ("battery", "🔋 Battery / AC Power Status"),
            ("datetime", "🕒 Date & Time Clock")
        ]:
            chk = QCheckBox(name)
            chk.setChecked(items_dict.get(key, True))
            items_layout.addWidget(chk)
            self.item_chks[key] = chk

        drive_layout = QHBoxLayout()
        drive_label = QLabel("Drives (e.g. C:,D:,E:):")
        self.drive_input = QLineEdit()
        self.drive_input.setText(",".join(self.settings.get("drive_letters", ["C:", "D:"])))
        drive_layout.addWidget(drive_label)
        drive_layout.addWidget(self.drive_input)
        items_layout.addLayout(drive_layout)

        main_layout.addWidget(items_group)

        # 3. Aesthetics & Transparency
        aes_group = QGroupBox("Aesthetics & Transparency")
        aes_layout = QVBoxLayout(aes_group)

        opacity_lbl_layout = QHBoxLayout()
        opacity_lbl = QLabel("Background Opacity:")
        self.opacity_val_lbl = QLabel(f"{self.settings.get('opacity', 25)}%")
        opacity_lbl_layout.addWidget(opacity_lbl)
        opacity_lbl_layout.addWidget(self.opacity_val_lbl)
        aes_layout.addLayout(opacity_lbl_layout)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(self.settings.get("opacity", 25))
        self.opacity_slider.valueChanged.connect(self.on_opacity_change)
        aes_layout.addWidget(self.opacity_slider)

        theme_layout = QHBoxLayout()
        theme_label = QLabel("Visual Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "Sleek Dark",
            "Vibrant Blue",
            "Forest Glass",
            "Light Minimal",
            "Radium Rainbow",
            "Neon Radium"
        ])
        current_theme = self.settings.get("theme", "sleek_dark").replace("_", " ").title()
        self.theme_combo.setCurrentText(current_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        aes_layout.addLayout(theme_layout)

        main_layout.addWidget(aes_group)

        # 4. Buttons
        btn_layout = QHBoxLayout()
        
        self.shortcut_btn = QPushButton("Create Desktop Shortcut")
        self.shortcut_btn.clicked.connect(self.create_desktop_shortcut)
        btn_layout.addWidget(self.shortcut_btn)
        
        save_btn = QPushButton("Apply Settings")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        main_layout.addLayout(btn_layout)

    def on_opacity_change(self, val):
        self.opacity_val_lbl.setText(f"{val}%")

    def save_settings(self):
        self.settings.set("position", self.pos_combo.currentText().lower())
        self.settings.set("auto_hide", self.hide_chk.isChecked())
        self.settings.set("icon_size", self.size_combo.currentText().lower())

        items = {}
        for key, chk in self.item_chks.items():
            items[key] = chk.isChecked()
        self.settings.set("items", items)

        drives = [d.strip().upper() for d in self.drive_input.text().split(",") if d.strip()]
        self.settings.set("drive_letters", drives if drives else ["C:", "D:"])

        self.settings.set("opacity", self.opacity_slider.value())

        theme_key = self.theme_combo.currentText().lower().replace(" ", "_")
        self.settings.set("theme", theme_key)

        from widget_controller import set_startup_enabled
        set_startup_enabled(self.startup_chk.isChecked())

        self.controller.apply_configuration()
        self.accept()

    def create_desktop_shortcut(self):
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "OmniBar Hardware Widget.lnk")
            target = sys.executable.replace("python.exe", "pythonw.exe")
            
            current_dir = os.path.abspath(os.path.dirname(__file__))
            script_path = os.path.join(current_dir, "main.py")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.Arguments = f'"{script_path}"'
            shortcut.WorkingDirectory = current_dir
            shortcut.IconLocation = r"C:\Windows\System32\imageres.dll, 219"
            shortcut.Description = "Launches OmniBar Hardware Widget Bar"
            shortcut.save()
            
            QMessageBox.information(self, "Shortcut Created", "Desktop shortcut 'OmniBar Hardware Widget' created successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Shortcut Failed", f"Could not create shortcut: {e}")
