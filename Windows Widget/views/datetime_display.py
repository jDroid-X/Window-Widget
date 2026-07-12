from PyQt5.QtCore import QTime, QDate
from views.base_card import HardwareCard

class DateTimeCard(HardwareCard):
    def __init__(self, settings, click_action=None):
        super().__init__("datetime", "TIME", click_action)
        self.settings = settings
        self.setObjectName("datetime_card")
        
    def update_display(self, metrics, is_vertical, prog_cols):
        current_time = QTime.currentTime().toString("hh:mm:ss")
        current_date = QDate.currentDate().toString("ddd, MMM d, yyyy")
        self.set_metrics(current_time, 0, sub_str=current_date)
