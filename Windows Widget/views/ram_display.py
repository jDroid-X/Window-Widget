from views.base_card import HardwareCard

class RamCard(HardwareCard):
    def __init__(self, settings, click_action=None):
        super().__init__("ram", "RAM", click_action)
        self.settings = settings
        self.setObjectName("ram_card")
        
    def update_display(self, metrics, is_vertical, prog_cols):
        ram_thresh = (self.settings.get("ram_warn", 60), self.settings.get("ram_crit", 85))
        percent = metrics.get("ram_percent", 0)
        used = metrics.get("ram_used", 0.0)
        total = metrics.get("ram_total", 0.0)
        
        sub_str = f"{used} GB / {total} GB"
        self.set_metrics(f"{percent}% USED", percent, prog_cols, ram_thresh, sub_str=sub_str)

        top_ram = metrics.get("top_ram", [])
        if top_ram:
            ram_tt = "Top Memory Processes:\n" + "\n".join([f"• {name}: {val}" for name, val in top_ram])
            self.setToolTip(ram_tt)
        else:
            self.setToolTip("RAM Telemetry")
