from views.base_card import HardwareCard

class DrivesCard(HardwareCard):
    def __init__(self, settings, click_action=None):
        super().__init__("drive", "STORAGE DRIVES (°C)", click_action)
        self.settings = settings
        self.setObjectName("drives_card")
        
    def update_display(self, metrics, is_vertical, prog_cols):
        drive_metrics = metrics.get("drives", [])
        disk_read = metrics.get("disk_read", 0.0)
        disk_write = metrics.get("disk_write", 0.0)
        
        def format_io(b_s):
            if b_s >= 1024 * 1024:
                return f"{b_s / (1024*1024):.1f}MB/s"
            elif b_s >= 1024:
                return f"{b_s / 1024:.0f}KB/s"
            else:
                return f"{b_s:.0f}B/s"
        
        io_str = f" [R: {format_io(disk_read)} | W: {format_io(disk_write)}]" if (disk_read > 1024 or disk_write > 1024) else ""
        
        parts = []
        max_pct = 0
        for d in drive_metrics:
            drv_name = d["name"]
            drv_pct = d["percent"]
            free = d.get("free", 0.0)
            total = d.get("total", 0.0)
            drv_temp = d.get("temp", 34)
            if drv_pct > max_pct:
                max_pct = drv_pct
            if is_vertical:
                parts.append(f"{drv_name} {drv_pct}% {drv_temp}°C")
            else:
                parts.append(f"DRV {drv_name} {drv_pct}% {drv_temp}°C ({free}/{total}GB Free)")
        
        separator = "\n" if is_vertical else " | "
        combined_str = separator.join(parts) if parts else "No Drives Detected"
        
        if io_str:
            if is_vertical:
                combined_str += f"\nIO: R:{format_io(disk_read)} W:{format_io(disk_write)}"
            else:
                combined_str += io_str
                
        self.set_metrics(combined_str, max_pct, prog_cols)
