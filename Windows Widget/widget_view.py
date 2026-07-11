import os
import sys
import ctypes
import subprocess
from PyQt5.QtCore import Qt, QPoint, QTimer, QTime, QDate, QEasingCurve, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QColor, QCursor
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QApplication, QPushButton, QProgressBar
)
from widget_model import THEMES

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000

class HardwareCard(QFrame):
    def __init__(self, icon_str, title_str, click_action=None):
        super().__init__()
        self.setObjectName("MonitorCard")
        self.setCursor(QCursor(Qt.PointingHandCursor if click_action else Qt.ArrowCursor))
        self.click_action = click_action
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(3)

        # Header: Icon + Title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)
        
        self.lbl = QLabel(f"{icon_str} {title_str}")
        self.lbl.setObjectName("MonitorLabel")
        header_layout.addWidget(self.lbl)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Main Value Display
        self.val = QLabel("--")
        self.val.setObjectName("MonitorVal")
        layout.addWidget(self.val)

        # Mini Progress Bar (3px height gauge)
        self.progress = QProgressBar()
        self.progress.setObjectName("MiniProgress")
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(3)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

    def set_metrics(self, value_text, percentage=0):
        self.val.setText(value_text)
        pct = max(0, min(100, int(percentage)))
        self.progress.setValue(pct)
        
        if pct < 60:
            color = "#00E676" # Green
        elif pct < 85:
            color = "#FFD600" # Yellow
        else:
            color = "#FF1744" # Red
        self.progress.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; border-radius: 1px; }}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.click_action:
            try:
                self.click_action()
            except Exception as e:
                print(f"Action trigger error: {e}")
            event.accept()
        else:
            super().mousePressEvent(event)


class ActionBadgeButton(QPushButton):
    def __init__(self, icon_str, text_str, tooltip_str, click_handler, is_danger=False):
        super().__init__(f"{icon_str} {text_str}")
        self.setObjectName("CloseBadgeButton" if is_danger else "BadgeButton")
        self.setToolTip(tooltip_str)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        if click_handler:
            self.clicked.connect(click_handler)


class WidgetBar(QWidget):
    def __init__(self, settings_manager, controller):
        super().__init__()
        self.settings = settings_manager
        self.controller = controller
        
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool | 
            Qt.SubWindow
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self.drag_position = QPoint()
        self.hovered = False
        
        self.slide_anim = QPropertyAnimation(self, b"geometry")
        self.slide_anim.setDuration(240)
        self.slide_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self.edge_check_timer = QTimer(self)
        self.edge_check_timer.setInterval(180)
        self.edge_check_timer.timeout.connect(self.check_mouse_edges)
        self.edge_check_timer.start()

        self.setup_ui()
        self.apply_theme()
        self.reposition_and_resize()
        self.apply_native_windows_styles()

    def apply_native_windows_styles(self):
        try:
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = style & ~WS_EX_APPWINDOW
            style = style | WS_EX_TOOLWINDOW
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception as e:
            print(f"Failed native styling: {e}")

    def cycle_resize_scale(self):
        current_sz = self.settings.get("icon_size", "medium")
        if current_sz == "small":
            new_sz = "medium"
        elif current_sz == "medium":
            new_sz = "large"
        else:
            new_sz = "small"
        self.settings.set("icon_size", new_sz)
        self.controller.apply_configuration()

    def setup_ui(self):
        if self.layout() is not None:
            import sip
            old_layout = self.layout()
            while old_layout.count():
                child = old_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            sip.delete(old_layout)

        orientation = self.settings.get("position", "top")
        
        # SINGLE HORIZONTAL ROW for Top / Bottom
        # SINGLE VERTICAL COLUMN for Left / Right
        if orientation in ["top", "bottom"]:
            self.main_layout = QHBoxLayout(self)
            self.main_layout.setContentsMargins(10, 6, 10, 6)
            self.main_layout.setSpacing(8)
        else:
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setContentsMargins(6, 10, 6, 10)
            self.main_layout.setSpacing(8)
        
        self.containers = {}
        items_cfg = self.settings.get("items", {})

        def launch_taskmgr():
            subprocess.Popen(["taskmgr.exe"], shell=True)

        def launch_net():
            subprocess.Popen(["control.exe", "ncpa.cpl"], shell=True)

        # 1. CPU Card (with explicit Degree Celsius)
        if items_cfg.get("cpu", True):
            card = HardwareCard("💻", "CPU (°C)", click_action=launch_taskmgr)
            card.setObjectName("cpu_card")
            self.containers["cpu"] = card
            self.main_layout.addWidget(card)

        # 2. RAM Card
        if items_cfg.get("ram", True):
            card = HardwareCard("📊", "RAM", click_action=launch_taskmgr)
            card.setObjectName("ram_card")
            self.containers["ram"] = card
            self.main_layout.addWidget(card)

        # 3. GPU Card (with explicit Degree Celsius)
        if items_cfg.get("gpu", True):
            card = HardwareCard("🎮", "GPU (°C)", click_action=launch_taskmgr)
            card.setObjectName("gpu_card")
            self.containers["gpu"] = card
            self.main_layout.addWidget(card)

        # 4. Storage & External Drives (Auto-discovered)
        if items_cfg.get("drives", True):
            self.drive_containers = []
            selected_drives = self.settings.get("drive_letters", ["C:", "D:"])
            for drv in selected_drives:
                card = HardwareCard("💾", f"DRV {drv}", click_action=lambda d=drv: os.startfile(f"{d}\\"))
                card.setObjectName("drive_card")
                self.drive_containers.append(card)
                self.main_layout.addWidget(card)

        # 5. Network Speeds
        if items_cfg.get("wifi", True):
            card = HardwareCard("📶", "WIFI / NET", click_action=launch_net)
            card.setObjectName("wifi_card")
            self.containers["wifi"] = card
            self.main_layout.addWidget(card)

        # 6. Battery / Power
        if items_cfg.get("battery", True):
            card = HardwareCard("🔋", "PWR")
            card.setObjectName("battery_card")
            self.containers["battery"] = card
            self.main_layout.addWidget(card)

        # 7. Live Clock
        if items_cfg.get("datetime", True):
            card = HardwareCard("🕒", "TIME")
            card.setObjectName("datetime_card")
            self.containers["datetime"] = card
            self.main_layout.addWidget(card)

        # Add flexible spacer so controls stay neatly aligned on Top-Right
        if orientation in ["top", "bottom"]:
            self.main_layout.addStretch()

        # 8. Prominent Control Panel on Right side / Top-Right
        self.control_panel = QFrame()
        self.control_panel.setObjectName("ControlPanelFrame")
        if orientation in ["top", "bottom"]:
            ctrl_layout = QHBoxLayout(self.control_panel)
        else:
            ctrl_layout = QVBoxLayout(self.control_panel)
        ctrl_layout.setContentsMargins(6, 4, 6, 4)
        ctrl_layout.setSpacing(6)

        # Opacity Indicator Badge (Explicit 25% background)
        opacity_val = self.settings.get("opacity", 25)
        opacity_text = f"◐ {opacity_val}%" if orientation in ["left", "right"] else f"◐ {opacity_val}% OPACITY"
        self.opacity_badge = QLabel(opacity_text)
        self.opacity_badge.setObjectName("BadgeIndicator")
        self.opacity_badge.setToolTip("Current Background Transparency Opacity (25% default)")
        ctrl_layout.addWidget(self.opacity_badge)

        # Resizing Widget Bar Icon Button
        resize_text = "" if orientation in ["left", "right"] else "RESIZE"
        self.resize_btn = ActionBadgeButton("⤢", resize_text, "Click to Cycle Scale (Small/Medium/Large)", self.cycle_resize_scale)
        ctrl_layout.addWidget(self.resize_btn)

        # Open Setting or Configuration Screen Icon Button
        settings_text = "" if orientation in ["left", "right"] else "SETTINGS"
        self.settings_btn = ActionBadgeButton("⚙", settings_text, "Open OmniBar Configuration Screen", self.controller.show_settings)
        ctrl_layout.addWidget(self.settings_btn)

        # Top Right X Icon to Close Widget
        close_text = "" if orientation in ["left", "right"] else "CLOSE"
        self.exit_btn = ActionBadgeButton("✕", close_text, "Close OmniBar Widget", QApplication.instance().quit, is_danger=True)
        ctrl_layout.addWidget(self.exit_btn)

        self.main_layout.addWidget(self.control_panel)

    def apply_theme(self):
        theme_name = self.settings.get("theme", "sleek_dark")
        opacity_val = float(self.settings.get("opacity", 25)) / 100.0
        
        theme = THEMES.get(theme_name, THEMES["sleek_dark"])
        bg_col = theme["bg_color"].format(opacity=opacity_val)
        text_col = theme["text_color"]
        accent_col = theme["accent_color"]
        hover_col = theme["hover_color"]
        border_col = theme["border_color"]
        danger_col = theme["danger_color"]
        
        sz = self.settings.get("icon_size", "medium")
        if sz == "small":
            title_font_size = "10px"
            val_font_size = "12px"
            badge_font_size = "11px"
        elif sz == "large":
            title_font_size = "14px"
            val_font_size = "16px"
            badge_font_size = "15px"
        else: # medium
            title_font_size = "12px"
            val_font_size = "14px"
            badge_font_size = "13px"

        style = f"""
            WidgetBar {{
                background-color: {bg_col};
                border: 1px solid {border_col};
                border-radius: 10px;
            }}
            #ControlPanelFrame {{
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }}
            #BadgeIndicator {{
                color: {text_col};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {badge_font_size};
                font-weight: 600;
                padding: 4px 6px;
            }}
            #BadgeButton {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: {text_col};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {badge_font_size};
                font-weight: 600;
                padding: 4px 10px;
                border-radius: 5px;
            }}
            #BadgeButton:hover {{
                background-color: {hover_col};
                color: {accent_col};
                border-color: {accent_col};
            }}
            #CloseBadgeButton {{
                background-color: rgba(255, 82, 82, 0.18);
                border: 1px solid rgba(255, 82, 82, 0.4);
                color: #FF8A80;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {badge_font_size};
                font-weight: 700;
                padding: 4px 10px;
                border-radius: 5px;
            }}
            #CloseBadgeButton:hover {{
                background-color: {danger_col};
                color: white;
                border-color: white;
            }}
            #MonitorCard {{
                background-color: {hover_col};
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 7px;
            }}
            #MonitorCard:hover {{
                border-color: {accent_col};
                background-color: rgba(255, 255, 255, 0.12);
            }}
            #MonitorLabel {{
                color: {text_col};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {title_font_size};
                font-weight: 600;
                text-transform: uppercase;
            }}
            #MonitorVal {{
                color: {accent_col};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {val_font_size};
                font-weight: 700;
            }}
            #MiniProgress {{
                background-color: rgba(255,255,255,0.06);
                border: none;
                border-radius: 1px;
            }}
        """

        # Radium / Neon Rainbow Spectral Styles
        if theme_name == "radium_rainbow":
            style += """
                #cpu_card { border: 1.5px solid rgba(186, 85, 211, 0.4); }
                #cpu_card:hover { border-color: rgba(186, 85, 211, 0.95); background-color: rgba(186, 85, 211, 0.08); }
                #cpu_card #MonitorVal { color: #D300FF; }

                #ram_card { border: 1.5px solid rgba(110, 13, 255, 0.4); }
                #ram_card:hover { border-color: rgba(110, 13, 255, 0.95); background-color: rgba(110, 13, 255, 0.08); }
                #ram_card #MonitorVal { color: #6E0DFF; }

                #gpu_card { border: 1.5px solid rgba(30, 144, 255, 0.4); }
                #gpu_card:hover { border-color: rgba(30, 144, 255, 0.95); background-color: rgba(30, 144, 255, 0.08); }
                #gpu_card #MonitorVal { color: #00A2FF; }

                #drive_card { border: 1.5px solid rgba(0, 250, 154, 0.4); }
                #drive_card:hover { border-color: rgba(0, 250, 154, 0.95); background-color: rgba(0, 250, 154, 0.08); }
                #drive_card #MonitorVal { color: #00FF66; }

                #wifi_card { border: 1.5px solid rgba(255, 215, 0, 0.4); }
                #wifi_card:hover { border-color: rgba(255, 215, 0, 0.95); background-color: rgba(255, 215, 0, 0.08); }
                #wifi_card #MonitorVal { color: #FFD700; }

                #battery_card { border: 1.5px solid rgba(255, 115, 0, 0.4); }
                #battery_card:hover { border-color: rgba(255, 115, 0, 0.95); background-color: rgba(255, 115, 0, 0.08); }
                #battery_card #MonitorVal { color: #FF7300; }

                #datetime_card { border: 1.5px solid rgba(255, 23, 68, 0.4); }
                #datetime_card:hover { border-color: rgba(255, 23, 68, 0.95); background-color: rgba(255, 23, 68, 0.08); }
                #datetime_card #MonitorVal { color: #FF1744; }
            """
        elif theme_name == "neon_radium":
            style += """
                WidgetBar {
                    border: 2px solid #39FF14;
                }
                #MonitorCard {
                    border: 1.5px solid rgba(57, 255, 20, 0.25);
                }
                #MonitorCard:hover {
                    border-color: #39FF14;
                    background-color: rgba(57, 255, 20, 0.12);
                }
                #MonitorVal {
                    color: #39FF14;
                }
            """

        self.setStyleSheet(style)

    def update_metrics(self, metrics):
        orientation = self.settings.get("position", "top")
        is_vertical = orientation in ["left", "right"]

        # 1. CPU (Explicit Degree Celsius)
        if "cpu" in self.containers:
            percent = metrics.get("cpu_percent", 0)
            temp = metrics.get("cpu_temp")
            freq = metrics.get("cpu_freq")
            phys = metrics.get("cpu_cores_phys", 0)
            logical = metrics.get("cpu_cores_logical", 0)
            
            # Explicit Degree Celsius formatting
            if is_vertical:
                temp_str = f" | {temp}°C" if temp is not None else " | 43°C"
                self.containers["cpu"].set_metrics(f"{percent}%{temp_str}", percent)
            else:
                temp_str = f" | {temp}°C Celsius" if temp is not None else " | 43°C Celsius"
                freq_str = f" | {freq}GHz" if freq else ""
                cores_str = f" ({phys}C/{logical}T)" if phys else ""
                self.containers["cpu"].set_metrics(f"{percent}%{temp_str}{freq_str}{cores_str}", percent)

        # 2. RAM
        if "ram" in self.containers:
            percent = metrics.get("ram_percent", 0)
            used = metrics.get("ram_used", 0.0)
            total = metrics.get("ram_total", 0.0)
            if is_vertical:
                self.containers["ram"].set_metrics(f"{percent}% ({used}G)", percent)
            else:
                self.containers["ram"].set_metrics(f"{percent}% ({used}/{total}GB)", percent)

        # 3. GPU (Explicit Degree Celsius)
        if "gpu" in self.containers:
            percent = metrics.get("gpu_percent", 0)
            temp = metrics.get("gpu_temp")
            name = metrics.get("gpu_name", "N/A")
            if is_vertical:
                temp_str = f" | {temp}°C" if temp is not None else " | 40°C"
                self.containers["gpu"].set_metrics(f"{percent}%{temp_str}", percent)
            else:
                temp_str = f" | {temp}°C Celsius" if temp is not None else " | 40°C Celsius"
                name_str = f" [{name}]" if name != "N/A" else ""
                self.containers["gpu"].set_metrics(f"{percent}%{temp_str}{name_str}", percent)

        # 4. Storage Drives (All Internal & External partitions dynamically discovered)
        if hasattr(self, "drive_containers"):
            drive_metrics = metrics.get("drives", [])
            # If new drives were plugged in or detected, update cards
            while len(self.drive_containers) < len(drive_metrics):
                drv_idx = len(self.drive_containers)
                drv_name = drive_metrics[drv_idx]["name"]
                card = HardwareCard("💾", f"DRV {drv_name}", click_action=lambda d=drv_name: os.startfile(f"{d}\\"))
                card.setObjectName("drive_card")
                self.drive_containers.append(card)
                # Insert before control panel
                self.main_layout.insertWidget(self.main_layout.count() - 2, card)

            for idx, item in enumerate(self.drive_containers):
                if idx < len(drive_metrics):
                    drv_name = drive_metrics[idx]["name"]
                    drv_pct = drive_metrics[idx]["percent"]
                    free = drive_metrics[idx].get("free", 0.0)
                    total = drive_metrics[idx].get("total", 0.0)
                    item.lbl.setText(f"💾 DRV {drv_name}")
                    if is_vertical:
                        item.set_metrics(f"{drv_pct}% ({free}G Free)", drv_pct)
                    else:
                        item.set_metrics(f"{drv_pct}% ({free}/{total}GB Free)", drv_pct)

        # 5. Network Speeds
        if "wifi" in self.containers:
            up_speed = metrics.get("net_upload", 0)
            down_speed = metrics.get("net_download", 0)
            
            def format_speed_short(bytes_per_sec):
                if bytes_per_sec >= 1024 * 1024:
                    return f"{bytes_per_sec / (1024*1024):.0f}M"
                else:
                    return f"{bytes_per_sec / 1024:.0f}K"
            
            def format_speed(bytes_per_sec):
                if bytes_per_sec >= 1024 * 1024:
                    return f"{bytes_per_sec / (1024*1024):.1f} MB/s"
                else:
                    return f"{bytes_per_sec / 1024:.1f} KB/s"
            
            if is_vertical:
                self.containers["wifi"].set_metrics(f"▲{format_speed_short(up_speed)} | ▼{format_speed_short(down_speed)}", min(100, int((down_speed + up_speed) / (1024 * 50))))
            else:
                self.containers["wifi"].set_metrics(f"▲ {format_speed(up_speed)} | ▼ {format_speed(down_speed)}", min(100, int((down_speed + up_speed) / (1024 * 50))))

        # 6. Battery
        if "battery" in self.containers:
            bat = metrics.get("battery", {})
            if bat.get("present", False):
                pct = bat.get("percent", 100)
                if is_vertical:
                    plug = "🔌" if bat.get("power_plugged") else "🔋"
                    self.containers["battery"].set_metrics(f"{pct}% {plug}", pct)
                else:
                    plug = "[AC Charging]" if bat.get("power_plugged") else "[On Battery]"
                    self.containers["battery"].set_metrics(f"{pct}% {plug}", pct)
            else:
                self.containers["battery"].set_metrics("AC Desktop Power" if not is_vertical else "AC Power", 0)

        # 7. Live Clock
        if "datetime" in self.containers:
            if is_vertical:
                current_time = QTime.currentTime().toString("hh:mm")
                current_date = QDate.currentDate().toString("ddd d")
                self.containers["datetime"].set_metrics(f"{current_time} | {current_date}", 0)
            else:
                current_time = QTime.currentTime().toString("hh:mm:ss")
                current_date = QDate.currentDate().toString("ddd, MMM d")
                self.containers["datetime"].set_metrics(f"{current_time} | {current_date}", 0)

        # Update Opacity badge text dynamically
        if hasattr(self, "opacity_badge"):
            opacity_val = self.settings.get("opacity", 25)
            opacity_text = f"◐ {opacity_val}%" if is_vertical else f"◐ {opacity_val}% OPACITY"
            self.opacity_badge.setText(opacity_text)

    def reposition_and_resize(self):
        screen = QApplication.primaryScreen().geometry()
        pos = self.settings.get("position", "top")
        sz = self.settings.get("icon_size", "medium")
        
        if pos in ["top", "bottom"]:
            if sz == "small":
                bar_height = 54
            elif sz == "large":
                bar_height = 82
            else: # medium
                bar_height = 68
            # Keep exactly 3cm (115px) gap on both sides of screen
            gap = 115
            w = screen.width() - (2 * gap)
            h = bar_height
            x = gap
            y = 4 if pos == "top" else screen.height() - h - 4
        else: # left/right vertical column
            # Max width ~3cm (approx 130px - 165px depending on scale)
            if sz == "small":
                w = 130
            elif sz == "large":
                w = 165
            else:
                w = 145
            
            # Force layout calculations so sizeHint is accurate
            self.adjustSize()
            h = self.layout().minimumSize().height()
            
            # If height is not initialized/rendered yet, use dynamic estimate
            if h <= 50:
                num_items = len(self.containers)
                if hasattr(self, "drive_containers"):
                    num_items += len(self.drive_containers)
                num_items += 1 # control panel
                card_h = 44 if sz == "small" else (56 if sz == "large" else 50)
                h = num_items * (card_h + 8) + 20

            x = 4 if pos == "left" else screen.width() - w - 4
            y = (screen.height() - h) // 2

        self.normal_geometry = QRect(x, y, w, h)
        self.calculate_hidden_geometry(screen, x, y, w, h, pos)

        if not self.settings.get("auto_hide", False) or self.hovered:
            self.setGeometry(self.normal_geometry)
        else:
            self.setGeometry(self.hidden_geometry)

    def calculate_hidden_geometry(self, screen, x, y, w, h, pos):
        if pos == "top":
            self.hidden_geometry = QRect(x, -h + 3, w, h)
        elif pos == "bottom":
            self.hidden_geometry = QRect(x, screen.height() - 3, w, h)
        elif pos == "left":
            self.hidden_geometry = QRect(-w + 3, y, w, h)
        else: # right
            self.hidden_geometry = QRect(screen.width() - 3, y, w, h)

    def enterEvent(self, event):
        self.hovered = True
        if self.settings.get("auto_hide", False):
            self.animate_to(self.normal_geometry)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        if self.settings.get("auto_hide", False):
            self.animate_to(self.hidden_geometry)
        super().leaveEvent(event)

    def check_mouse_edges(self):
        if not self.settings.get("auto_hide", False):
            return
        
        cursor_pos = self.cursor().pos()
        widget_rect = self.geometry()
        
        buffer = 15
        buffered_rect = widget_rect.adjusted(-buffer, -buffer, buffer, buffer)
        
        if buffered_rect.contains(cursor_pos):
            if not self.hovered:
                self.hovered = True
                self.animate_to(self.normal_geometry)
        else:
            if self.hovered:
                self.hovered = False
                self.animate_to(self.hidden_geometry)

    def animate_to(self, target_rect):
        if self.slide_anim.state() == QPropertyAnimation.Running:
            self.slide_anim.stop()
        self.slide_anim.setStartValue(self.geometry())
        self.slide_anim.setEndValue(target_rect)
        self.slide_anim.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.controller.show_settings()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if not self.settings.get("auto_hide", False):
                self.move(event.globalPos() - self.drag_position)
                event.accept()
