import subprocess
from views.base_card import HardwareCard


class UsbCard(HardwareCard):
    def __init__(self, settings, click_action=None):
        if click_action is None:
            click_action = lambda: subprocess.Popen("explorer.exe =")
        super().__init__("usb", "USB", click_action)
        self.settings = settings
        self.setObjectName("usb_card")

    def update_display(self, metrics, is_vertical, prog_cols):
        usb_list = metrics.get("usb_drives", [])
        
        if not usb_list:
            self.set_metrics("READY", 0, prog_cols, sub_str="0 Hot-Swap Drives")
            self.setToolTip(
                "USB / Removable Hot-Swap Storage\n"
                "• Status: Active listening for device insertion\n"
                "• Connected Drives: None\n"
                "• Click to open This PC"
            )
        else:
            first = usb_list[0]
            name = first.get("name", "USB")
            label = first.get("label", name)
            pct = first.get("percent", 0)
            free = first.get("free", 0.0)
            total = first.get("total", 0.0)
            
            sub_str = f"{len(usb_list)} Drive{'s' if len(usb_list)>1 else ''} | {free}GB Free"
            self.set_metrics(f"{label} {int(pct)}%", pct, prog_cols, sub_str=sub_str)
            
            lines = [f"Connected USB Hot-Swap Drives ({len(usb_list)}):"]
            for d in usb_list:
                lines.append(
                    f"• [{d.get('name')}] {d.get('label')} ({d.get('fstype', 'FAT32')}): "
                    f"{d.get('percent', 0)}% used | {d.get('free', 0)}GB free of {d.get('total', 0)}GB"
                )
            lines.append("\nClick to open This PC / File Explorer")
            self.setToolTip("\n".join(lines))
