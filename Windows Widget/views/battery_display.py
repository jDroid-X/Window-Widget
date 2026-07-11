from views.base_card import HardwareCard

class BatteryCard(HardwareCard):
    def __init__(self, settings, click_action=None):
        super().__init__("battery", "BATTERY", click_action)
        self.settings = settings
        self.setObjectName("battery_card")
        
    def update_display(self, metrics, is_vertical, prog_cols):
        bat = metrics.get("battery", {})
        if bat.get("present", False):
            self.show()
            pct = bat.get("percent", 100)
            secsleft = bat.get("secsleft", -1)
            if is_vertical:
                plug = "🔌" if bat.get("power_plugged") else "🔋"
                self.set_metrics(f"{pct}% {plug}", pct, prog_cols)
            else:
                if bat.get("power_plugged"):
                    plug_str = "[AC Charging]"
                elif secsleft > 0:
                    h_left = secsleft // 3600
                    m_left = (secsleft % 3600) // 60
                    plug_str = f"[{h_left}h {m_left}m left]"
                else:
                    plug_str = "[On Battery]"
                self.set_metrics(f"{pct}% {plug_str}", pct, prog_cols)
        else:
            self.hide()
