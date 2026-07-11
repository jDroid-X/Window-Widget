import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, 
    QSlider, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox,
    QGridLayout, QSpinBox, QColorDialog
)

class SettingsWindow(QDialog):
    def __init__(self, settings_manager, controller):
        super().__init__()
        self.settings = settings_manager
        self.controller = controller
        
        self.setWindowTitle("OmniBar Configuration")
        self.setMinimumSize(430, 580)
        self.resize(450, 600)
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

        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(self.settings.get("opacity", 25))
        opacity_slider.valueChanged.connect(self.on_opacity_change)
        aes_layout.addWidget(opacity_slider)
        self.opacity_slider = opacity_slider

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

        # Sync with Windows Theme Checkbox
        self.sync_theme_chk = QCheckBox("Sync with Windows Theme")
        self.sync_theme_chk.setChecked(self.settings.get("sync_windows_theme", False))
        self.sync_theme_chk.setToolTip("Automatically switches between Dark and Light mode based on Windows settings")
        aes_layout.addWidget(self.sync_theme_chk)

        # Custom Background Color Chooser
        color_layout = QHBoxLayout()
        self.custom_bg_chk = QCheckBox("Custom Background:")
        self.custom_bg_chk.setChecked(self.settings.get("custom_bg_enabled", False))
        self.color_preview = QPushButton("Choose Color")
        self.color_preview.setFixedSize(120, 24)
        self.custom_color_hex = self.settings.get("custom_bg_color", "#121212")
        self.color_preview.setStyleSheet(f"background-color: {self.custom_color_hex}; border: 1px solid #777; border-radius: 3px; color: #FFF; font-weight: bold;")
        self.color_preview.clicked.connect(self.choose_custom_color)
        color_layout.addWidget(self.custom_bg_chk)
        color_layout.addWidget(self.color_preview)
        aes_layout.addLayout(color_layout)

        # Custom Border Color Chooser
        border_color_layout = QHBoxLayout()
        self.custom_border_chk = QCheckBox("Custom Border:")
        self.custom_border_chk.setChecked(self.settings.get("custom_border_enabled", True))
        self.border_preview = QPushButton("Choose Color")
        self.border_preview.setFixedSize(120, 24)
        self.custom_border_hex = self.settings.get("custom_border_color", "#00E5FF")
        self.border_preview.setStyleSheet(f"background-color: {self.custom_border_hex}; border: 1px solid #777; border-radius: 3px; color: #FFF; font-weight: bold;")
        self.border_preview.clicked.connect(self.choose_custom_border_color)
        border_color_layout.addWidget(self.custom_border_chk)
        border_color_layout.addWidget(self.border_preview)
        aes_layout.addLayout(border_color_layout)

        main_layout.addWidget(aes_group)

        # 3.5. RAG Thresholds
        rag_group = QGroupBox("RAG Threshold Settings (%)")
        rag_layout = QGridLayout(rag_group)
        
        # CPU
        rag_layout.addWidget(QLabel("CPU Warning:"), 0, 0)
        self.cpu_warn_spin = QSpinBox()
        self.cpu_warn_spin.setRange(10, 95)
        self.cpu_warn_spin.setValue(self.settings.get("cpu_warn", 60))
        rag_layout.addWidget(self.cpu_warn_spin, 0, 1)
        
        rag_layout.addWidget(QLabel("CPU Critical:"), 0, 2)
        self.cpu_crit_spin = QSpinBox()
        self.cpu_crit_spin.setRange(15, 99)
        self.cpu_crit_spin.setValue(self.settings.get("cpu_crit", 85))
        rag_layout.addWidget(self.cpu_crit_spin, 0, 3)
        
        # RAM
        rag_layout.addWidget(QLabel("RAM Warning:"), 1, 0)
        self.ram_warn_spin = QSpinBox()
        self.ram_warn_spin.setRange(10, 95)
        self.ram_warn_spin.setValue(self.settings.get("ram_warn", 60))
        rag_layout.addWidget(self.ram_warn_spin, 1, 1)
        
        rag_layout.addWidget(QLabel("RAM Critical:"), 1, 2)
        self.ram_crit_spin = QSpinBox()
        self.ram_crit_spin.setRange(15, 99)
        self.ram_crit_spin.setValue(self.settings.get("ram_crit", 85))
        rag_layout.addWidget(self.ram_crit_spin, 1, 3)
        
        # GPU
        rag_layout.addWidget(QLabel("GPU Warning:"), 2, 0)
        self.gpu_warn_spin = QSpinBox()
        self.gpu_warn_spin.setRange(10, 95)
        self.gpu_warn_spin.setValue(self.settings.get("gpu_warn", 60))
        rag_layout.addWidget(self.gpu_warn_spin, 2, 1)
        
        rag_layout.addWidget(QLabel("GPU Critical:"), 2, 2)
        self.gpu_crit_spin = QSpinBox()
        self.gpu_crit_spin.setRange(15, 99)
        self.gpu_crit_spin.setValue(self.settings.get("gpu_crit", 85))
        rag_layout.addWidget(self.gpu_crit_spin, 2, 3)
        
        main_layout.addWidget(rag_group)

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

    def choose_custom_color(self):
        color = QColorDialog.getColor(QColor(self.custom_color_hex), self, "Choose Background Color")
        if color.isValid():
            self.custom_color_hex = color.name()
            self.color_preview.setStyleSheet(f"background-color: {self.custom_color_hex}; border: 1px solid #777; border-radius: 3px; color: #FFF; font-weight: bold;")

    def choose_custom_border_color(self):
        color = QColorDialog.getColor(QColor(self.custom_border_hex), self, "Choose Border Color")
        if color.isValid():
            self.custom_border_hex = color.name()
            self.border_preview.setStyleSheet(f"background-color: {self.custom_border_hex}; border: 1px solid #777; border-radius: 3px; color: #FFF; font-weight: bold;")

    def save_settings(self):
        items = {}
        for key, chk in self.item_chks.items():
            items[key] = chk.isChecked()

        drives = [d.strip().upper() for d in self.drive_input.text().split(",") if d.strip()]

        # Collect all changes into a single batch write
        updates = {
            "position": self.pos_combo.currentText().lower(),
            "auto_hide": self.hide_chk.isChecked(),
            "icon_size": self.size_combo.currentText().lower(),
            "items": items,
            "drive_letters": drives if drives else ["C:", "D:"],
            "opacity": self.opacity_slider.value(),
            "theme": self.theme_combo.currentText().lower().replace(" ", "_"),
            "sync_windows_theme": self.sync_theme_chk.isChecked(),
            "custom_bg_enabled": self.custom_bg_chk.isChecked(),
            "custom_bg_color": self.custom_color_hex,
            "custom_border_enabled": self.custom_border_chk.isChecked(),
            "custom_border_color": self.custom_border_hex,
            "cpu_warn": self.cpu_warn_spin.value(),
            "cpu_crit": self.cpu_crit_spin.value(),
            "ram_warn": self.ram_warn_spin.value(),
            "ram_crit": self.ram_crit_spin.value(),
            "gpu_warn": self.gpu_warn_spin.value(),
            "gpu_crit": self.gpu_crit_spin.value(),
        }
        self.settings.set_batch(updates)

        from controllers.widget_controller import set_startup_enabled
        set_startup_enabled(self.startup_chk.isChecked())

        self.controller.apply_configuration()
        self.accept()

    def create_desktop_shortcut(self):
        try:
            from installer.create_shortcut import create_desktop_shortcut as _create_shortcut
            success, msg = _create_shortcut()
            if success:
                QMessageBox.information(self, "Shortcut Created", f"Desktop shortcut created successfully:\n{msg}")
            else:
                QMessageBox.warning(self, "Shortcut Failed", f"Could not create shortcut:\n{msg}")
        except Exception as e:
            QMessageBox.warning(self, "Shortcut Failed", f"Could not create shortcut:\n{e}")
