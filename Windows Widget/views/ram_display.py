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
        
        if is_vertical:
            self.set_metrics(f"{percent}% ({used}G)", percent, prog_cols, ram_thresh)
        else:
            self.set_metrics(f"{percent}% ({used}/{total}GB)", percent, prog_cols, ram_thresh)
            
        ram_title = f"RAM ({ram_thresh[0]}/{ram_thresh[1]}%)"
        self.lbl.setText(ram_title)

        top_ram = metrics.get("top_ram", [])
        if top_ram:
            ram_tt = "Top Memory Processes:\n" + "\n".join([f"• {name}: {val}" for name, val in top_ram])
            self.setToolTip(ram_tt)
        else:
            self.setToolTip("RAM Telemetry")
