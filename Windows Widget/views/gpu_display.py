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
            self.hide()
        else:
            self.show()
            if is_vertical:
                temp_str = f" | {temp}°C" if temp is not None else " | --°C"
                vram_str = f" ({vram_used}G)" if vram_used else ""
                self.set_metrics(f"{percent}%{temp_str}{vram_str}", percent, prog_cols, gpu_thresh)
            else:
                temp_str = f" | {temp}°C Celsius" if temp is not None else " | --°C"
                name_str = f" [{name}]" if name != "N/A" else ""
                vram_str = f" | {vram_used}/{vram_total}GB VRAM" if vram_used else ""
                self.set_metrics(f"{percent}%{temp_str}{vram_str}{name_str}", percent, prog_cols, gpu_thresh)
                
            gpu_title = f"GPU ({gpu_thresh[0]}/{gpu_thresh[1]}%)"
            self.lbl.setText(gpu_title)
