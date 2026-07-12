from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QWidget


class IconPainterStrategy:
    """Abstract base OOP strategy for rendering vector icons."""
    def draw(self, painter: QPainter):
        raise NotImplementedError


class CpuIconStrategy(IconPainterStrategy):
    def draw(self, painter: QPainter):
        painter.drawRoundedRect(3, 3, 16, 16, 2, 2)
        painter.drawRect(7, 7, 8, 8)
        for i in (6, 11, 16):
            painter.drawLine(i, 0, i, 3)
            painter.drawLine(i, 19, i, 22)
            painter.drawLine(0, i, 3, i)
            painter.drawLine(19, i, 22, i)


class RamIconStrategy(IconPainterStrategy):
    def draw(self, painter: QPainter):
        painter.drawRect(2, 6, 18, 10)
        for x in range(4, 18, 2):
            painter.drawLine(x, 16, x, 18)
        painter.drawRect(4, 8, 3, 6)
        painter.drawRect(9, 8, 3, 6)
        painter.drawRect(14, 8, 3, 6)


class GpuIconStrategy(IconPainterStrategy):
    def draw(self, painter: QPainter):
        painter.drawRoundedRect(2, 4, 18, 14, 2, 2)
        painter.drawEllipse(5, 7, 5, 5)
        painter.drawEllipse(12, 7, 5, 5)
        painter.drawLine(4, 18, 12, 18)


class DriveIconStrategy(IconPainterStrategy):
    def draw(self, painter: QPainter):
        painter.drawRoundedRect(3, 3, 16, 16, 2, 2)
        painter.drawRect(6, 11, 10, 8)
        painter.drawRect(7, 3, 8, 5)


class WifiIconStrategy(IconPainterStrategy):
    def draw(self, painter: QPainter):
        painter.drawEllipse(10, 17, 2, 2)
        painter.drawArc(7, 13, 8, 8, 45*16, 90*16)
        painter.drawArc(4, 9, 14, 14, 45*16, 90*16)
        painter.drawArc(1, 5, 20, 20, 45*16, 90*16)


class BatteryIconStrategy(IconPainterStrategy):
    def draw(self, painter: QPainter):
        painter.drawRoundedRect(2, 6, 16, 10, 1, 1)
        painter.drawRect(18, 9, 2, 4)


class DateTimeIconStrategy(IconPainterStrategy):
    def draw(self, painter: QPainter):
        painter.drawEllipse(3, 3, 16, 16)
        painter.drawLine(11, 11, 11, 6)
        painter.drawLine(11, 11, 15, 11)


class UsbIconStrategy(IconPainterStrategy):
    def draw(self, painter: QPainter):
        painter.drawRect(7, 2, 8, 5)
        painter.drawRoundedRect(5, 7, 12, 12, 2, 2)
        painter.drawRect(9, 3, 1, 2)
        painter.drawRect(12, 3, 1, 2)


class DefaultIconStrategy(IconPainterStrategy):
    def draw(self, painter: QPainter):
        painter.drawRect(4, 4, 14, 14)


ICON_STRATEGY_REGISTRY = {
    "cpu": CpuIconStrategy(),
    "ram": RamIconStrategy(),
    "gpu": GpuIconStrategy(),
    "drive": DriveIconStrategy(),
    "💾": DriveIconStrategy(),
    "usb": UsbIconStrategy(),
    "wifi": WifiIconStrategy(),
    "battery": BatteryIconStrategy(),
    "datetime": DateTimeIconStrategy(),
}


class VectorIconWidget(QWidget):
    """Encapsulated vector icon view utilizing OOP Strategy Pattern for icon rendering."""
    def __init__(self, icon_name, color="#00E5FF"):
        super().__init__()
        self.strategy = ICON_STRATEGY_REGISTRY.get(icon_name, DefaultIconStrategy())
        self.color = QColor(color)
        self.scale_factor = 1.0
        self.setFixedSize(22, 22)
        
    def set_color(self, color):
        self.color = QColor(color)
        self.update()
        
    def set_size(self, size_str):
        if size_str == "small":
            self.scale_factor = 18.0 / 22.0
            self.setFixedSize(18, 18)
        elif size_str == "large":
            self.scale_factor = 28.0 / 22.0
            self.setFixedSize(28, 28)
        else:
            self.scale_factor = 1.0
            self.setFixedSize(22, 22)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.scale(self.scale_factor, self.scale_factor)
        pen = QPen(self.color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        
        # Delegate drawing to the polymorphic OOP strategy instance
        self.strategy.draw(painter)
