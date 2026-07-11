from PyQt5.QtCore import QTime, QDate
from views.base_card import HardwareCard

class DateTimeCard(HardwareCard):
    def __init__(self, settings, click_action=None):
        super().__init__("datetime", "DATE & TIME", click_action)
        self.settings = settings
        self.setObjectName("datetime_card")
        
    def update_display(self, metrics, is_vertical, prog_cols):
        if is_vertical:
            current_time = QTime.currentTime().toString("hh:mm")
            current_date = QDate.currentDate().toString("ddd d")
            self.set_metrics(f"{current_time} | {current_date}", 0)
        else:
            current_time = QTime.currentTime().toString("hh:mm:ss")
            current_date = QDate.currentDate().toString("ddd, MMM d")
            self.set_metrics(f"{current_time} | {current_date}", 0)
