from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen
from PyQt5.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QSizePolicy

from views.icon_view import VectorIconWidget


class HardwareCard(QFrame):
    def __init__(self, icon_name, title_str, click_action=None):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("hardwareCard", "true")
        self.setObjectName("MonitorCard")
        self.click_action = click_action
        
        # Expanding horizontal, preferred vertical size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(145)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        
        # Side-by-side: Left Column (Icon + Name Below) & Right Column (Metadata Next to Icon)
        top_hbox = QHBoxLayout()
        top_hbox.setContentsMargins(0, 0, 0, 0)
        top_hbox.setSpacing(10)
        
        # Left Column: Icon on top, Name below it
        icon_col = QVBoxLayout()
        icon_col.setContentsMargins(0, 0, 0, 0)
        icon_col.setSpacing(3)
        icon_col.setAlignment(Qt.AlignCenter)
        
        self.icon_widget = VectorIconWidget(icon_name)
        icon_col.addWidget(self.icon_widget, 0, Qt.AlignCenter)
        
        self.lbl = QLabel(title_str)
        self.lbl.setObjectName("MonitorLabel")
        self.lbl.setWordWrap(False)
        self.lbl.setAlignment(Qt.AlignCenter)
        icon_col.addWidget(self.lbl, 0, Qt.AlignCenter)
        
        top_hbox.addLayout(icon_col)
        
        # Right Column: Metadata in front/next to the icon column
        meta_col = QVBoxLayout()
        meta_col.setContentsMargins(0, 0, 0, 0)
        meta_col.setSpacing(2)
        meta_col.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Main Prominent Value Display
        self.val = QLabel("--")
        self.val.setObjectName("MonitorVal")
        self.val.setWordWrap(True)
        self.val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        meta_col.addWidget(self.val)

        # Secondary Detail / Subtitle Display
        self.sub_val = QLabel("")
        self.sub_val.setObjectName("MonitorSubVal")
        self.sub_val.setWordWrap(True)
        self.sub_val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        meta_col.addWidget(self.sub_val)
        
        top_hbox.addLayout(meta_col, 1)
        layout.addLayout(top_hbox)

        # Mini Progress Bar (4px height gauge)
        self.progress = QProgressBar()
        self.progress.setObjectName("MiniProgress")
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Crisp visible base card border
        border_color = QColor(255, 255, 255, 65)
        if hasattr(self, "settings") and self.settings:
            if self.settings.get("custom_border_enabled", True):
                hex_col = self.settings.get("custom_border_color", "#00E5FF")
                border_color = QColor(hex_col)
                border_color.setAlpha(160)
                
        if hasattr(self, "settings") and self.settings and self.settings.get("show_card_border", True) is False:
            return

        radius = 7
        if hasattr(self, "settings") and self.settings and self.settings.get("card_radius") is not None:
            radius = int(self.settings.get("card_radius", 7))
            
        pen = QPen(border_color, 1.2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), radius, radius)
        
    def apply_layout_scale(self, size_mode="medium", is_vertical=False):
        """Universal OOP responsive layout sizing for Small, Medium, and Large views."""
        self.icon_widget.set_size(size_mode)

        if size_mode == "small":
            min_w = 150 if is_vertical else 130
            min_h = 54 if is_vertical else 48
            self.layout().setContentsMargins(8, 6, 8, 6)
            self.layout().setSpacing(4)
        elif size_mode == "large":
            min_w = 200 if is_vertical else 175
            min_h = 76 if is_vertical else 66
            self.layout().setContentsMargins(14, 10, 14, 10)
            self.layout().setSpacing(8)
        else:  # medium (Default)
            min_w = 175 if is_vertical else 150
            min_h = 64 if is_vertical else 54
            self.layout().setContentsMargins(10, 8, 10, 8)
            self.layout().setSpacing(6)

        if hasattr(self, "settings") and self.settings:
            if self.settings.get("card_padding") is not None:
                pad = int(self.settings.get("card_padding", 8))
                self.layout().setContentsMargins(pad + 2, pad, pad + 2, pad)
            if self.settings.get("card_min_width") is not None:
                min_w = int(self.settings.get("card_min_width", min_w))
            if self.settings.get("card_min_height") is not None:
                min_h = int(self.settings.get("card_min_height", min_h))
            ff = str(self.settings.get("font_family", "Segoe UI"))
            v_sz = int(self.settings.get("card_val_font_size", 11))
            s_sz = int(self.settings.get("card_sub_font_size", 9))
            show_txt_border = bool(self.settings.get("show_textbox_border", False))
            txt_border_css = "border: 1px solid rgba(0, 229, 255, 140); border-radius: 4px; padding: 2px 5px;" if show_txt_border else "border: none; padding: 0px;"
            self.val.setStyleSheet(f"font-family: '{ff}'; font-size: {v_sz}pt; font-weight: bold; {txt_border_css}")
            self.lbl.setStyleSheet(f"font-family: '{ff}'; font-size: {s_sz}pt;")
            self.sub_val.setStyleSheet(f"font-family: '{ff}'; font-size: {s_sz}pt;")

        icon_h = 18 if size_mode == "small" else (28 if size_mode == "large" else 22)
        self.val.setFixedHeight(icon_h)

        self.setMinimumWidth(min_w)
        self.setMinimumHeight(min_h)
        self.setMaximumSize(16777215, 16777215)

    def set_metrics(self, value_str, percentage_val, prog_colors=None, thresholds=None, sub_str=""):
        self.val.setText(value_str)
        if sub_str:
            self.sub_val.setText(sub_str)
            self.sub_val.show()
        else:
            self.sub_val.hide()
        self.progress.setValue(max(0, min(100, int(percentage_val))))
        
        # Automatically adjust scale profile if settings are available
        if hasattr(self, "settings") and self.settings:
            is_vert = (self.settings.get("position", "top") in ["left", "right"])
            sz = self.settings.get("icon_size", "medium")
            self.apply_layout_scale(sz, is_vert)
        
        # Dynamic color scaling based on RAG thresholds (if provided)
        if prog_colors and len(prog_colors) == 3:
            good_col, warn_col, high_col = prog_colors
            
            color_to_use = good_col
            if thresholds and len(thresholds) == 2:
                warn_limit, crit_limit = thresholds
                if percentage_val >= crit_limit:
                    color_to_use = high_col
                elif percentage_val >= warn_limit:
                    color_to_use = warn_col
            else:
                # Default linear scaling if no limits are configured
                if percentage_val >= 85:
                    color_to_use = high_col
                elif percentage_val >= 60:
                    color_to_use = warn_col
                    
            self.progress.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {color_to_use};
                    border-radius: 1px;
                }}
            """)
            
    def enterEvent(self, event):
        if self.click_action:
            self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.click_action:
            self.click_action()
        super().mousePressEvent(event)
