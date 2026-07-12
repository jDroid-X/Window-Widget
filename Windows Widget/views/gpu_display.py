from views.base_card import HardwareCard

class GpuCard(HardwareCard):
    def __init__(self, settings, click_action=None):
        super().__init__("gpu", "GPU", click_action)
        self.settings = settings
        self.setObjectName("gpu_card")
        
    def update_display(self, metrics, is_vertical, prog_cols):
        gpu_thresh = (self.settings.get("gpu_warn", 60), self.settings.get("gpu_crit", 85))
        percent = metrics.get("gpu_percent", 0)
        temp = metrics.get("gpu_temp")
        name = metrics.get("gpu_name", "N/A")
        vram_used = metrics.get("gpu_vram_used", 0.0)
        vram_total = metrics.get("gpu_vram_total", 0.0)
        
        if name == "N/A" and percent == 0 and temp is None:
            self.show()
            self.set_metrics("IDLE / N/A", 0, prog_cols, gpu_thresh, sub_str="Integrated / No NVML")
        else:
            self.show()
            temp_str = f"{temp}°C" if temp is not None else ""
            short_name = name.split()[-2] + " " + name.split()[-1] if len(name.split()) >= 2 else name
            sub_details = " | ".join([s for s in [temp_str, short_name] if s])
            self.set_metrics(f"{percent}% LOAD", percent, prog_cols, gpu_thresh, sub_str=sub_details)
