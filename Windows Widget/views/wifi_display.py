from views.base_card import HardwareCard

class WifiCard(HardwareCard):
    def __init__(self, settings, click_action=None):
        super().__init__("wifi", "WIFI / NET", click_action)
        self.settings = settings
        self.setObjectName("wifi_card")
        
    def update_display(self, metrics, is_vertical, prog_cols):
        up_speed = metrics.get("net_upload", 0)
        down_speed = metrics.get("net_download", 0)
        ping = metrics.get("net_ping")
        ping_str = f" | {ping}ms" if (ping is not None and ping != -1) else ""
        
        def format_speed_short(bytes_per_sec):
            if bytes_per_sec >= 1024 * 1024:
                return f"{bytes_per_sec / (1024*1024):.0f}M"
            else:
                return f"{bytes_per_sec / 1024:.0f}K"
        
        def format_speed(bytes_per_sec):
            if bytes_per_sec >= 1024 * 1024:
                return f"{bytes_per_sec / (1024*1024):.1f} MB/s"
            else:
                return f"{bytes_per_sec / 1024:.1f} KB/s"
        
        if is_vertical:
            self.set_metrics(f"▲{format_speed_short(up_speed)} | ▼{format_speed_short(down_speed)}{ping_str}", min(100, int((down_speed + up_speed) / (1024 * 50))), prog_cols)
        else:
            self.set_metrics(f"▲ {format_speed(up_speed)} | ▼ {format_speed(down_speed)}{ping_str}", min(100, int((down_speed + up_speed) / (1024 * 50))), prog_cols)
