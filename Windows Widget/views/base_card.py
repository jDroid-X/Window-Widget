import os
import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen
from PyQt5.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QSizePolicy

class VectorIconWidget(QWidget):
    def __init__(self, icon_name, color="#00E5FF"):
        super().__init__()
        self.icon_name = icon_name
        self.color = QColor(color)
        self.setFixedSize(22, 22)
        
    def set_color(self, color):
        self.color = QColor(color)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        pen = QPen(self.color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        
        # Simple high-quality vector drawings for main indicators
        if self.icon_name == "cpu":
            # Outer chip outline
            painter.drawRoundedRect(3, 3, 16, 16, 2, 2)
            # Inner core
            painter.drawRect(7, 7, 8, 8)
            # Pins
            for i in (6, 11, 16):
                painter.drawLine(i, 0, i, 3)
                painter.drawLine(i, 19, i, 22)
                painter.drawLine(0, i, 3, i)
                painter.drawLine(19, i, 22, i)
        elif self.icon_name == "ram":
            # RAM Stick outline
            painter.drawRect(2, 6, 18, 10)
            # Connector teeth
            for x in range(4, 18, 2):
                painter.drawLine(x, 16, x, 18)
            # Memory chips
            painter.drawRect(4, 8, 3, 6)
            painter.drawRect(9, 8, 3, 6)
            painter.drawRect(14, 8, 3, 6)
        elif self.icon_name == "gpu":
            # GPU Card outline
            painter.drawRoundedRect(2, 4, 18, 14, 2, 2)
            # Cooling fan circles
            painter.drawEllipse(5, 7, 5, 5)
            painter.drawEllipse(12, 7, 5, 5)
            # PCIe connector
            painter.drawLine(4, 18, 12, 18)
        elif self.icon_name == "drive" or self.icon_name == "💾":
            # Floppy disk/drive outline
            painter.drawRoundedRect(3, 3, 16, 16, 2, 2)
            # Label area
            painter.drawRect(6, 11, 10, 8)
            # Sliding shutter
            painter.drawRect(7, 3, 8, 5)
        elif self.icon_name == "wifi":
            # Signal waves
            painter.drawEllipse(10, 17, 2, 2) # Center dot
            painter.drawArc(7, 13, 8, 8, 45*16, 90*16)
            painter.drawArc(4, 9, 14, 14, 45*16, 90*16)
            painter.drawArc(1, 5, 20, 20, 45*16, 90*16)
        elif self.icon_name == "battery":
            # Battery body
            painter.drawRoundedRect(2, 6, 16, 10, 1, 1)
            # Positive terminal tip
            painter.drawRect(18, 9, 2, 4)
        elif self.icon_name == "datetime":
            # Clock face
            painter.drawEllipse(3, 3, 16, 16)
            # Clock hands (3 o'clock / 12 o'clock)
            painter.drawLine(11, 11, 11, 6)
            painter.drawLine(11, 11, 15, 11)
        else:
            # Default fallback box
            painter.drawRect(4, 4, 14, 14)


class HardwareCard(QFrame):
    def __init__(self, icon_name, title_str, click_action=None):
        super().__init__()
        self.setObjectName("MonitorCard")
        self.click_action = click_action
        
        # Expanding horizontal, preferred vertical size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Header: Vector Icon + Title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)
        header_layout.setAlignment(Qt.AlignCenter)
        
        self.icon_widget = VectorIconWidget(icon_name)
        header_layout.addWidget(self.icon_widget)
        
        self.lbl = QLabel(title_str)
        self.lbl.setObjectName("MonitorLabel")
        self.lbl.setWordWrap(True)
        self.lbl.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.lbl)
        layout.addLayout(header_layout)

        # Main Value Display
        self.val = QLabel("--")
        self.val.setObjectName("MonitorVal")
        self.val.setWordWrap(True)
        self.val.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.val)

        # Mini Progress Bar (3px height gauge)
        self.progress = QProgressBar()
        self.progress.setObjectName("MiniProgress")
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(3)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
    def set_metrics(self, value_str, percentage_val, prog_colors=None, thresholds=None):
        self.val.setText(value_str)
        self.progress.setValue(max(0, min(100, int(percentage_val))))
        
        # Determine if vertical from self.settings
        is_vertical = False
        if hasattr(self, "settings") and self.settings:
            is_vertical = (self.settings.get("position", "top") in ["left", "right"])

        # Dynamically size card height in vertical mode to prevent overlapping
        if is_vertical:
            num_value_lines = value_str.count("\n") + 1
            num_title_lines = 1
            # If title is long (e.g. "STORAGE DRIVES (°C)"), it wraps to 2 lines
            if len(self.lbl.text()) > 15:
                num_title_lines = 2
            
            # Retrieve size setting
            icon_sz = "medium"
            if hasattr(self, "settings") and self.settings:
                icon_sz = self.settings.get("icon_size", "medium")
                
            if icon_sz == "small":
                base_h = 36
                line_h = 13
            elif icon_sz == "large":
                base_h = 52
                line_h = 17
            else: # medium
                base_h = 44
                line_h = 15
                
            min_h = base_h + ((num_value_lines + num_title_lines - 1) * line_h)
            self.setMinimumHeight(min_h)
            self.setFixedHeight(min_h)
        else:
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
        
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
