from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy


class GroupSeparatorWidget(QFrame):
    """Sleek contextual category separator grouping related telemetry cards on the widget bar."""
    def __init__(self, category_title, is_vertical=False):
        super().__init__()
        self.category_title = category_title
        self.is_vertical = is_vertical
        self.setObjectName("GroupSeparator")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.lbl = QLabel(category_title)
        self.lbl.setObjectName("GroupSeparatorLabel")
        self.lbl.setAlignment(Qt.AlignCenter)

        if is_vertical:
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            layout = QHBoxLayout(self)
            layout.setContentsMargins(6, 4, 6, 4)
        else:
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(4, 6, 4, 6)

        layout.addWidget(self.lbl)

    def set_orientation(self, is_vertical):
        self.is_vertical = is_vertical
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Subtle glowing separator accent line
        pen = QPen(QColor(255, 255, 255, 38), 1.0)
        painter.setPen(pen)
        if self.is_vertical:
            painter.drawLine(8, self.height() - 1, self.width() - 8, self.height() - 1)
        else:
            painter.drawLine(1, 8, 1, self.height() - 8)
