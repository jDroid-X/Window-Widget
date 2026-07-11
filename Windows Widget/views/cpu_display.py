from views.base_card import HardwareCard

class CpuCard(HardwareCard):
    def __init__(self, settings, click_action=None):
        super().__init__("cpu", "CPU", click_action)
        self.settings = settings
        self.setObjectName("cpu_card")
        
    def update_display(self, metrics, is_vertical, prog_cols):
        cpu_thresh = (self.settings.get("cpu_warn", 60), self.settings.get("cpu_crit", 85))
        percent = metrics.get("cpu_percent", 0)
        temp = metrics.get("cpu_temp")
        freq = metrics.get("cpu_freq")
        phys = metrics.get("cpu_cores_phys", 0)
        logical = metrics.get("cpu_cores_logical", 0)
        
        if is_vertical:
            temp_str = f" | {temp}°C" if temp is not None else " | --°C"
            self.set_metrics(f"{percent}%{temp_str}", percent, prog_cols, cpu_thresh)
        else:
            temp_str = f" | {temp}°C Celsius" if temp is not None else " | --°C"
            freq_str = f" | {freq}GHz" if freq else ""
            cores_str = f" ({phys}C/{logical}T)" if phys else ""
            self.set_metrics(f"{percent}%{temp_str}{freq_str}{cores_str}", percent, prog_cols, cpu_thresh)
            
        cpu_title = f"CPU ({cpu_thresh[0]}/{cpu_thresh[1]}%)"
        self.lbl.setText(cpu_title)

        top_cpu = metrics.get("top_cpu", [])
        if top_cpu:
            cpu_tt = "Top CPU Processes:\n" + "\n".join([f"• {name}: {pct:.1f}%" for name, pct in top_cpu])
            self.setToolTip(cpu_tt)
        else:
            self.setToolTip("CPU Telemetry")
