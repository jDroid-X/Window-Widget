from views.base_card import HardwareCard

class WifiCard(HardwareCard):
    def __init__(self, settings, click_action=None):
        super().__init__("wifi", "NET", click_action)
        self.settings = settings
        self.setObjectName("wifi_card")
        
    def update_display(self, metrics, is_vertical, prog_cols):
        up_speed = metrics.get("net_upload", 0)
        down_speed = metrics.get("net_download", 0)
        ping = metrics.get("net_ping")
        # This is a TCP-connect measurement to Cloudflare DNS, not ICMP ping.
        ping_str = f" | TCP {ping}ms" if (ping is not None and ping != -1) else ""
        
        def format_speed_short(bytes_per_sec):
            if bytes_per_sec >= 1024 * 1024:
                return f"{bytes_per_sec / (1024*1024):.0f}M"
            else:
                return f"{bytes_per_sec / 1024:.0f}K"
        
        def format_speed(bytes_per_sec):
            if bytes_per_sec >= 1024 * 1024:
                return f"{bytes_per_sec / (1024*1024):.1f} MB/s"
            else:
                return f"{bytes_per_sec / 1024:.0f} KB/s"
        
        down_str = format_speed(down_speed)
        up_str = format_speed(up_speed)
        ping_part = f" | {ping}ms" if (ping is not None and ping != -1) else ""
        
        self.set_metrics(f"▼ {down_str}", min(100, int((down_speed + up_speed) / (1024 * 50))), prog_cols, sub_str=f"▲ {up_str}{ping_part}")
