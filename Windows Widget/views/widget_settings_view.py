import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, 
    QSlider, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox,
    QGridLayout, QSpinBox, QColorDialog, QApplication, QScrollArea, QWidget
)

class SettingsWindow(QDialog):
    def __init__(self, settings_manager, controller):
        super().__init__()
        self.settings = settings_manager
        self.controller = controller
        
        self.setWindowTitle("OmniBar Configuration")
        self.setMinimumSize(540, 420)
        self.resize(640, 580)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint)
        
        self.setup_ui()

    def setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(12, 12, 12, 12)
        outer_layout.setSpacing(10)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # =========================================================
        # PHASE 1: Aesthetics & Visual Theme Hierarchy (Waterfall Top)
        # =========================================================
        aes_group = QGroupBox("1. Aesthetics & Visual Theme")
        aes_layout = QVBoxLayout(aes_group)
        aes_layout.setSpacing(10)
        aes_layout.setContentsMargins(12, 16, 12, 12)

        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Visual Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(26)
        self.theme_combo.addItems([
            "Neon Radium", "Radium Rainbow", "Vibrant Blue",
            "Forest Glass", "Sleek Dark", "Light Minimal"
        ])
        current_theme = self.settings.get("theme", "sleek_dark").replace("_", " ").title()
        self.theme_combo.setCurrentText(current_theme)
        theme_layout.addWidget(self.theme_combo, 2)

        theme_layout.addSpacing(15)
        theme_layout.addWidget(QLabel("Monitor:"))
        self.monitor_combo = QComboBox()
        self.monitor_combo.setMinimumHeight(26)
        monitors = QApplication.screens()
        self.monitor_combo.addItem("Primary", None)
        for idx_mon, _ in enumerate(monitors):
            self.monitor_combo.addItem(f"Monitor {idx_mon+1}", idx_mon)
        current_monitor = self.settings.get("monitor_index")
        if current_monitor is None:
            self.monitor_combo.setCurrentIndex(0)
        else:
            self.monitor_combo.setCurrentIndex(current_monitor + 1)
        theme_layout.addWidget(self.monitor_combo, 1)
        aes_layout.addLayout(theme_layout)

        # Background Opacity & Custom Background Color Row
        opacity_bg_row = QHBoxLayout()
        opacity_bg_row.addWidget(QLabel("Background Opacity:"))
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(self.settings.get("opacity", 25))
        opacity_slider.valueChanged.connect(self.on_opacity_change)
        self.opacity_slider = opacity_slider
        opacity_bg_row.addWidget(opacity_slider, 2)
        
        self.opacity_val_lbl = QLabel(f"{self.settings.get('opacity', 25)}%")
        self.opacity_val_lbl.setMinimumWidth(40)
        opacity_bg_row.addWidget(self.opacity_val_lbl)

        opacity_bg_row.addSpacing(15)
        self.custom_bg_chk = QCheckBox("Custom Background Color:")
        self.custom_bg_chk.setChecked(self.settings.get("custom_bg_enabled", False))
        opacity_bg_row.addWidget(self.custom_bg_chk)
        
        self.color_preview = QPushButton("Choose Color")
        self.color_preview.setFixedSize(110, 26)
        self.custom_color_hex = self.settings.get("custom_bg_color", "#121212")
        self.color_preview.setStyleSheet(f"background-color: {self.custom_color_hex}; border: 1px solid #777; border-radius: 4px; color: #FFF; font-weight: bold;")
        self.color_preview.clicked.connect(self.choose_custom_color)
        opacity_bg_row.addWidget(self.color_preview)
        aes_layout.addLayout(opacity_bg_row)

        # Border Color & Theme Sync Row
        border_sync_row = QHBoxLayout()
        self.custom_border_chk = QCheckBox("Custom Border Color:")
        self.custom_border_chk.setChecked(self.settings.get("custom_border_enabled", True))
        border_sync_row.addWidget(self.custom_border_chk)
        
        self.border_preview = QPushButton("Choose Color")
        self.border_preview.setFixedSize(110, 26)
        self.custom_border_hex = self.settings.get("custom_border_color", "#00E5FF")
        self.border_preview.setStyleSheet(f"background-color: {self.custom_border_hex}; border: 1px solid #777; border-radius: 4px; color: #FFF; font-weight: bold;")
        self.border_preview.clicked.connect(self.choose_custom_border_color)
        border_sync_row.addWidget(self.border_preview)

        border_sync_row.addSpacing(20)
        self.sync_theme_chk = QCheckBox("Automatically sync theme with Windows Light / Dark mode")
        self.sync_theme_chk.setChecked(self.settings.get("sync_windows_theme", False))
        border_sync_row.addWidget(self.sync_theme_chk)
        border_sync_row.addStretch()
        aes_layout.addLayout(border_sync_row)

        main_layout.addWidget(aes_group)

        # =========================================================
        # PHASE 2: Layout & Dock Position
        # =========================================================
        layout_group = QGroupBox("2. Layout & Dock Position")
        layout_grid = QVBoxLayout(layout_group)
        layout_grid.setSpacing(10)
        layout_grid.setContentsMargins(12, 16, 12, 12)
        
        row1_layout = QHBoxLayout()
        row1_layout.addWidget(QLabel("Dock Position:"))
        self.pos_combo = QComboBox()
        self.pos_combo.setMinimumHeight(26)
        self.pos_combo.addItems(["Top", "Bottom", "Left", "Right"])
        self.pos_combo.setCurrentText(self.settings.get("position", "top").capitalize())
        row1_layout.addWidget(self.pos_combo, 1)
        
        row1_layout.addSpacing(20)
        row1_layout.addWidget(QLabel("Scale / Size Preset:"))
        self.size_combo = QComboBox()
        self.size_combo.setMinimumHeight(26)
        self.size_combo.addItems(["Small", "Medium", "Large"])
        self.size_combo.setCurrentText(self.settings.get("icon_size", "medium").capitalize())
        row1_layout.addWidget(self.size_combo, 1)
        layout_grid.addLayout(row1_layout)

        self.hide_chk = QCheckBox("Auto-hide bar at screen edge (Hover 3px border to slide out)")
        self.hide_chk.setChecked(self.settings.get("auto_hide", False))
        layout_grid.addWidget(self.hide_chk)

        from controllers.widget_controller import is_startup_enabled
        self.startup_chk = QCheckBox("Launch OmniBar automatically at Windows startup")
        self.startup_chk.setChecked(is_startup_enabled())
        layout_grid.addWidget(self.startup_chk)

        main_layout.addWidget(layout_group)

        # =========================================================
        # PHASE 3: CardView Customization & Element Settings
        # =========================================================
        card_group = QGroupBox("3. CardView Customization & Element Settings (Default Preset: Medium)")
        card_grid = QVBoxLayout(card_group)
        card_grid.setSpacing(10)
        card_grid.setContentsMargins(12, 16, 12, 12)

        # Spacing, Margins & Padding row
        card_space_row = QHBoxLayout()
        card_space_row.addWidget(QLabel("Bar Margin (px):"))
        self.margin_spin = QSpinBox()
        self.margin_spin.setMinimumHeight(26)
        self.margin_spin.setRange(0, 30)
        self.margin_spin.setValue(int(self.settings.get("bar_margin", 10)))
        card_space_row.addWidget(self.margin_spin)

        card_space_row.addSpacing(15)
        card_space_row.addWidget(QLabel("Spacing (px):"))
        self.spacing_spin = QSpinBox()
        self.spacing_spin.setMinimumHeight(26)
        self.spacing_spin.setRange(0, 30)
        self.spacing_spin.setValue(int(self.settings.get("card_spacing", 10)))
        card_space_row.addWidget(self.spacing_spin)

        card_space_row.addSpacing(15)
        card_space_row.addWidget(QLabel("Padding (px):"))
        self.padding_spin = QSpinBox()
        self.padding_spin.setMinimumHeight(26)
        self.padding_spin.setRange(0, 25)
        self.padding_spin.setValue(int(self.settings.get("card_padding", 8)))
        card_space_row.addWidget(self.padding_spin)
        card_grid.addLayout(card_space_row)

        # Dimensions & Corner Radius row
        card_row1 = QHBoxLayout()
        card_row1.addWidget(QLabel("Card Min Width (px):"))
        self.card_w_spin = QSpinBox()
        self.card_w_spin.setMinimumHeight(26)
        self.card_w_spin.setRange(80, 400)
        self.card_w_spin.setValue(int(self.settings.get("card_min_width", 150)))
        card_row1.addWidget(self.card_w_spin)

        card_row1.addSpacing(15)
        card_row1.addWidget(QLabel("Card Min Height (px):"))
        self.card_h_spin = QSpinBox()
        self.card_h_spin.setMinimumHeight(26)
        self.card_h_spin.setRange(30, 150)
        self.card_h_spin.setValue(int(self.settings.get("card_min_height", 54)))
        card_row1.addWidget(self.card_h_spin)

        card_row1.addSpacing(15)
        card_row1.addWidget(QLabel("Corner Radius (px):"))
        self.card_rad_spin = QSpinBox()
        self.card_rad_spin.setMinimumHeight(26)
        self.card_rad_spin.setRange(0, 25)
        self.card_rad_spin.setValue(int(self.settings.get("card_radius", 7)))
        card_row1.addWidget(self.card_rad_spin)
        card_grid.addLayout(card_row1)

        # Global UI Font Family & Base Size row
        font_row = QHBoxLayout()
        font_row.addWidget(QLabel("Font Family:"))
        self.font_combo = QComboBox()
        self.font_combo.setMinimumHeight(26)
        self.font_combo.addItems(["Segoe UI", "Inter", "Consolas", "Tahoma", "Arial", "Microsoft YaHei"])
        curr_font = self.settings.get("font_family", "Segoe UI")
        self.font_combo.setCurrentText(curr_font)
        font_row.addWidget(self.font_combo, 2)

        font_row.addSpacing(15)
        font_row.addWidget(QLabel("Font Size (pt):"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimumHeight(26)
        self.font_size_spin.setRange(7, 18)
        self.font_size_spin.setValue(int(self.settings.get("font_size", 10)))
        font_row.addWidget(self.font_size_spin, 1)
        card_grid.addLayout(font_row)

        # Card Typography Font Sizes row
        card_row2 = QHBoxLayout()
        card_row2.addWidget(QLabel("Primary Value Font (pt):"))
        self.card_val_f_spin = QSpinBox()
        self.card_val_f_spin.setMinimumHeight(26)
        self.card_val_f_spin.setRange(7, 22)
        self.card_val_f_spin.setValue(int(self.settings.get("card_val_font_size", 11)))
        card_row2.addWidget(self.card_val_f_spin)

        card_row2.addSpacing(20)
        card_row2.addWidget(QLabel("Sub-Title Font (pt):"))
        self.card_sub_f_spin = QSpinBox()
        self.card_sub_f_spin.setMinimumHeight(26)
        self.card_sub_f_spin.setRange(6, 18)
        self.card_sub_f_spin.setValue(int(self.settings.get("card_sub_font_size", 9)))
        card_row2.addWidget(self.card_sub_f_spin)
        card_grid.addLayout(card_row2)

        border_row = QHBoxLayout()
        self.show_card_border_chk = QCheckBox("Show Card Frame Border")
        self.show_card_border_chk.setChecked(self.settings.get("show_card_border", True))
        border_row.addWidget(self.show_card_border_chk)

        border_row.addSpacing(20)
        self.show_textbox_border_chk = QCheckBox("Show Textbox Border around Value")
        self.show_textbox_border_chk.setChecked(self.settings.get("show_textbox_border", False))
        border_row.addWidget(self.show_textbox_border_chk)
        card_grid.addLayout(border_row)

        reset_card_btn = QPushButton("Reset All CardView Settings to Default Medium Preset")
        reset_card_btn.setMinimumHeight(30)
        reset_card_btn.clicked.connect(self.reset_cardview_defaults)
        card_grid.addWidget(reset_card_btn)

        main_layout.addWidget(card_group)

        # =========================================================
        # PHASE 4: Visible Hardware Cards & RAG Alert Thresholds (%)
        # =========================================================
        items_group = QGroupBox("4. Visible Hardware Cards & RAG Alert Thresholds (%)")
        items_grid = QGridLayout(items_group)
        items_grid.setSpacing(12)
        items_grid.setContentsMargins(12, 16, 12, 12)
        
        self.item_chks = {}
        items_dict = self.settings.get("items", {})

        rag_items = [
            ("cpu", "💻 CPU Utilization & Celsius Temp", "cpu_warn", 60, "cpu_crit", 85),
            ("ram", "📊 RAM Utilization & Breakdown", "ram_warn", 60, "ram_crit", 85),
            ("gpu", "🎮 GPU Load & Temp", "gpu_warn", 60, "gpu_crit", 85),
        ]
        
        for idx, (key, name, w_key, w_def, c_key, c_def) in enumerate(rag_items):
            chk = QCheckBox(name)
            chk.setMinimumHeight(26)
            chk.setChecked(items_dict.get(key, True))
            items_grid.addWidget(chk, idx, 0)
            self.item_chks[key] = chk

            warn_box = QHBoxLayout()
            warn_box.addWidget(QLabel("Warn:"))
            w_spin = QSpinBox()
            w_spin.setMinimumHeight(26)
            w_spin.setMinimumWidth(70)
            w_spin.setRange(10, 95)
            w_spin.setValue(self.settings.get(w_key, w_def))
            warn_box.addWidget(w_spin)
            items_grid.addLayout(warn_box, idx, 1)

            crit_box = QHBoxLayout()
            crit_box.addWidget(QLabel("Crit:"))
            c_spin = QSpinBox()
            c_spin.setMinimumHeight(26)
            c_spin.setMinimumWidth(70)
            c_spin.setRange(15, 99)
            c_spin.setValue(self.settings.get(c_key, c_def))
            crit_box.addWidget(c_spin)
            items_grid.addLayout(crit_box, idx, 2)

            setattr(self, f"{key}_warn_spin", w_spin)
            setattr(self, f"{key}_crit_spin", c_spin)

        row_idx = len(rag_items)
        
        chk_drives = QCheckBox("💾 Storage & USB Partitions")
        chk_drives.setMinimumHeight(26)
        chk_drives.setChecked(items_dict.get("drives", True))
        items_grid.addWidget(chk_drives, row_idx, 0)
        self.item_chks["drives"] = chk_drives

        drive_layout = QHBoxLayout()
        drive_layout.addWidget(QLabel("Drives:"))
        self.drive_input = QLineEdit()
        self.drive_input.setMinimumHeight(26)
        self.drive_input.setPlaceholderText("e.g. C:,D: (blank = all)")
        self.drive_input.setText(",".join(self.settings.get("drive_letters", ["C:", "D:"])))
        drive_layout.addWidget(self.drive_input)
        items_grid.addLayout(drive_layout, row_idx, 1, 1, 2)

        row_idx += 1
        for key, name in [
            ("wifi", "📶 Network Speeds (Upload/Download)"),
            ("battery", "🔋 Battery / AC Power Status"),
            ("datetime", "🕒 Date & Time Clock")
        ]:
            chk = QCheckBox(name)
            chk.setMinimumHeight(24)
            chk.setChecked(items_dict.get(key, True))
            items_grid.addWidget(chk, row_idx, 0, 1, 3)
            self.item_chks[key] = chk
            row_idx += 1

        main_layout.addWidget(items_group)
        main_layout.addStretch()

        scroll.setWidget(content_widget)
        outer_layout.addWidget(scroll, 1)

        # Fixed Action Buttons Footer outside scroll area
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(4, 6, 4, 4)
        
        self.live_update_chk = QCheckBox("⚡ Live Preview")
        self.live_update_chk.setChecked(True)
        self.live_update_chk.setToolTip("When checked, changes apply to OmniBar instantly in real time without clicking Apply.")
        btn_layout.addWidget(self.live_update_chk)
        
        btn_layout.addStretch()

        self.shortcut_btn = QPushButton("Create Desktop Shortcut")
        self.shortcut_btn.setMinimumHeight(32)
        self.shortcut_btn.clicked.connect(self.create_desktop_shortcut)
        btn_layout.addWidget(self.shortcut_btn)
        
        save_btn = QPushButton("Apply & Close")
        save_btn.setMinimumHeight(32)
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        outer_layout.addLayout(btn_layout)
        self.connect_live_signals()

    def connect_live_signals(self):
        """Connects UI controls to live instant application when Live Preview is checked."""
        self.theme_combo.currentTextChanged.connect(lambda _: self.apply_live_changes())
        self.monitor_combo.currentIndexChanged.connect(lambda _: self.apply_live_changes())
        self.pos_combo.currentTextChanged.connect(lambda _: self.apply_live_changes())
        self.size_combo.currentTextChanged.connect(lambda _: self.apply_live_changes())
        self.margin_spin.valueChanged.connect(lambda _: self.apply_live_changes())
        self.spacing_spin.valueChanged.connect(lambda _: self.apply_live_changes())
        self.padding_spin.valueChanged.connect(lambda _: self.apply_live_changes())
        self.card_w_spin.valueChanged.connect(lambda _: self.apply_live_changes())
        self.card_h_spin.valueChanged.connect(lambda _: self.apply_live_changes())
        self.card_rad_spin.valueChanged.connect(lambda _: self.apply_live_changes())
        self.card_val_f_spin.valueChanged.connect(lambda _: self.apply_live_changes())
        self.card_sub_f_spin.valueChanged.connect(lambda _: self.apply_live_changes())
        self.font_combo.currentTextChanged.connect(lambda _: self.apply_live_changes())
        self.font_size_spin.valueChanged.connect(lambda _: self.apply_live_changes())
        self.show_card_border_chk.toggled.connect(lambda _: self.apply_live_changes())
        self.show_textbox_border_chk.toggled.connect(lambda _: self.apply_live_changes())
        self.opacity_slider.valueChanged.connect(lambda _: self.apply_live_changes())
        self.hide_chk.toggled.connect(lambda _: self.apply_live_changes())
        for chk in self.item_chks.values():
            chk.toggled.connect(lambda _: self.apply_live_changes())

    def reset_cardview_defaults(self):
        """Resets all CardView dimensions and typography to the pristine Medium preset."""
        self.card_w_spin.setValue(150)
        self.card_h_spin.setValue(54)
        self.card_rad_spin.setValue(7)
        self.card_val_f_spin.setValue(11)
        self.card_sub_f_spin.setValue(9)
        self.margin_spin.setValue(10)
        self.spacing_spin.setValue(10)
        self.padding_spin.setValue(8)
        self.font_combo.setCurrentText("Segoe UI")
        self.font_size_spin.setValue(10)
        self.show_card_border_chk.setChecked(True)
        self.show_textbox_border_chk.setChecked(False)
        self.apply_live_changes()

    def on_opacity_change(self, val):
        self.opacity_val_lbl.setText(f"{val}%")

    def choose_custom_color(self):
        color = QColorDialog.getColor(QColor(self.custom_color_hex), self, "Choose Background Color")
        if color.isValid():
            self.custom_color_hex = color.name()
            self.color_preview.setStyleSheet(f"background-color: {self.custom_color_hex}; border: 1px solid #777; border-radius: 3px; color: #FFF; font-weight: bold;")
            self.apply_live_changes()

    def choose_custom_border_color(self):
        color = QColorDialog.getColor(QColor(self.custom_border_hex), self, "Choose Border Color")
        if color.isValid():
            self.custom_border_hex = color.name()
            self.border_preview.setStyleSheet(f"background-color: {self.custom_border_hex}; border: 1px solid #777; border-radius: 3px; color: #FFF; font-weight: bold;")
            self.apply_live_changes()

    def collect_settings_dict(self):
        items = {}
        for key, chk in self.item_chks.items():
            items[key] = chk.isChecked()

        drives = [d.strip().upper() for d in self.drive_input.text().split(",") if d.strip()]

        return {
            "position": self.pos_combo.currentText().lower(),
            "auto_hide": self.hide_chk.isChecked(),
            "icon_size": self.size_combo.currentText().lower(),
            "bar_margin": self.margin_spin.value(),
            "card_spacing": self.spacing_spin.value(),
            "card_padding": self.padding_spin.value(),
            "card_min_width": self.card_w_spin.value(),
            "card_min_height": self.card_h_spin.value(),
            "card_radius": self.card_rad_spin.value(),
            "card_val_font_size": self.card_val_f_spin.value(),
            "card_sub_font_size": self.card_sub_f_spin.value(),
            "show_card_border": self.show_card_border_chk.isChecked(),
            "show_textbox_border": self.show_textbox_border_chk.isChecked(),
            "font_family": self.font_combo.currentText(),
            "font_size": self.font_size_spin.value(),
            "items": items,
            "drive_letters": drives,
            "opacity": self.opacity_slider.value(),
            "theme": self.theme_combo.currentText().lower().replace(" ", "_"),
            "monitor_index": self.monitor_combo.currentData(),
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

    def apply_live_changes(self):
        """Instantly updates the live OmniBar widget without closing the dialog."""
        if not hasattr(self, "live_update_chk") or not self.live_update_chk.isChecked():
            return
        updates = self.collect_settings_dict()
        self.settings.set_batch(updates)
        self.controller.apply_configuration()

    def save_settings(self):
        updates = self.collect_settings_dict()
        # Validate threshold values (warn <= crit)
        for res in ["cpu", "ram", "gpu"]:
            warn_key = f"{res}_warn"
            crit_key = f"{res}_crit"
            warn_val = updates[warn_key]
            crit_val = updates[crit_key]
            if warn_val > crit_val:
                new_crit = min(99, warn_val + 1)
                updates[crit_key] = new_crit
                QMessageBox.warning(self, "Threshold Adjustment",
                    f"{res.upper()} warning ({warn_val}%) was greater than critical ({crit_val}%). Adjusted critical to {new_crit}%.")
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
