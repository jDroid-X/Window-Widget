import os
import copy
import json
import psutil
import time
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex, QMutexLocker

DEFAULT_SETTINGS = {
    "position": "top",          # "top", "bottom", "left", "right"
    "auto_hide": False,         # True or False
    "opacity": 25,              # Default opacity 25% background
    "icon_size": "medium",      # "small", "medium", "large"
    "theme": "sleek_dark",      # "sleek_dark", "vibrant_blue", "forest_glass", "light_minimal", "radium_rainbow", "neon_radium"
    "custom_bg_enabled": False,
    "custom_bg_color": "#121212",
    "custom_border_enabled": True,
    "custom_border_color": "#00E5FF",
    "cpu_warn": 60,
    "cpu_crit": 85,
    "ram_warn": 60,
    "ram_crit": 85,
    "gpu_warn": 60,
    "gpu_crit": 85,
    "items": {
        "cpu": True,
        "ram": True,
        "gpu": True,
        "drives": True,
        "wifi": True,
        "battery": True,
        "datetime": True
    },
    "drive_letters": ["C:", "D:"]
}

THEMES = {
    "sleek_dark": {
        "bg_color": "rgba(18, 18, 18, {opacity})",
        "border_color": "rgba(255, 255, 255, 0.12)",
        "text_color": "#E0E0E0",
        "accent_color": "#00E5FF",
        "hover_color": "rgba(255, 255, 255, 0.10)",
        "danger_color": "#FF5252",
        "progress_good": "#00E676",
        "progress_warn": "#FFD600",
        "progress_high": "#FF1744"
    },
    "vibrant_blue": {
        "bg_color": "rgba(10, 25, 47, {opacity})",
        "border_color": "rgba(100, 255, 218, 0.2)",
        "text_color": "#8892B0",
        "accent_color": "#64FFDA",
        "hover_color": "rgba(100, 255, 218, 0.10)",
        "danger_color": "#FF5252",
        "progress_good": "#64FFDA",
        "progress_warn": "#FFD600",
        "progress_high": "#FF5252"
    },
    "forest_glass": {
        "bg_color": "rgba(20, 35, 20, {opacity})",
        "border_color": "rgba(143, 188, 143, 0.25)",
        "text_color": "#F0FFF0",
        "accent_color": "#98FB98",
        "hover_color": "rgba(152, 251, 152, 0.10)",
        "danger_color": "#FF6B6B",
        "progress_good": "#98FB98",
        "progress_warn": "#FDD835",
        "progress_high": "#FF6B6B"
    },
    "light_minimal": {
        "bg_color": "rgba(245, 245, 245, {opacity})",
        "border_color": "rgba(0, 0, 0, 0.12)",
        "text_color": "#212121",
        "accent_color": "#3F51B5",
        "hover_color": "rgba(0, 0, 0, 0.05)",
        "danger_color": "#D32F2F",
        "progress_good": "#4CAF50",
        "progress_warn": "#FF9800",
        "progress_high": "#F44336"
    },
    "radium_rainbow": {
        "bg_color": "rgba(10, 10, 16, {opacity})",
        "border_color": "rgba(255, 255, 255, 0.15)",
        "text_color": "#FFFFFF",
        "accent_color": "#FF007F",
        "hover_color": "rgba(255, 255, 255, 0.08)",
        "danger_color": "#FF1744",
        "progress_good": "#00FFCC",
        "progress_warn": "#FFD600",
        "progress_high": "#FF1744"
    },
    "neon_radium": {
        "bg_color": "rgba(8, 14, 8, {opacity})",
        "border_color": "rgba(57, 255, 20, 0.3)",
        "text_color": "#E5FFE5",
        "accent_color": "#39FF14",
        "hover_color": "rgba(57, 255, 20, 0.1)",
        "danger_color": "#FF3333",
        "progress_good": "#39FF14",
        "progress_warn": "#FFFF00",
        "progress_high": "#FF3333"
    }
}

class SystemMetricsWorker(QThread):
    metrics_updated = pyqtSignal(dict)

    def __init__(self, settings_manager):
        super().__init__()
        self.settings = settings_manager
        self.running = True
        self.tick_count = 0
        
        # Static CPU Metadata
        try:
            self.cpu_cores_phys = psutil.cpu_count(logical=False) or 0
            self.cpu_cores_logical = psutil.cpu_count(logical=True) or 0
        except Exception:
            self.cpu_cores_phys = 0
            self.cpu_cores_logical = 0

        try:
            net_io = psutil.net_io_counters()
            self.prev_net_sent = net_io.bytes_sent
            self.prev_net_recv = net_io.bytes_recv
        except Exception:
            self.prev_net_sent = 0
            self.prev_net_recv = 0
            
        try:
            disk_io = psutil.disk_io_counters()
            self.prev_disk_read = disk_io.read_bytes
            self.prev_disk_write = disk_io.write_bytes
        except Exception:
            self.prev_disk_read = 0
            self.prev_disk_write = 0

        self.cached_ping = None
        self.cached_top_cpu = []
        self.cached_top_ram = []
        self.prev_time = time.time()
        self.cached_drives = []
        self.cached_battery = {}

    def run(self):
        try:
            import GPUtil
        except ImportError:
            GPUtil = None

        while self.running:
            try:
                metrics = {}
                current_time = time.time()
                dt = current_time - self.prev_time if current_time > self.prev_time else 1.0

                # 1. CPU Fast Metrics & Metadata
                metrics["cpu_percent"] = psutil.cpu_percent()
                metrics["cpu_cores_phys"] = self.cpu_cores_phys
                metrics["cpu_cores_logical"] = self.cpu_cores_logical
                metrics["cpu_freq"] = None
                try:
                    freq = psutil.cpu_freq()
                    if freq:
                        metrics["cpu_freq"] = round(freq.current / 1000, 1) # GHz
                except Exception:
                    pass

                metrics["cpu_temp"] = None
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            if name in ["coretemp", "cpu_thermal", "k10temp"]:
                                metrics["cpu_temp"] = int(entries[0].current)
                                break
                except Exception:
                    pass

                # 2. RAM Fast Detailed Metadata
                metrics["ram_percent"] = 0
                metrics["ram_used"] = 0.0
                metrics["ram_total"] = 0.0
                try:
                    ram = psutil.virtual_memory()
                    metrics["ram_percent"] = ram.percent
                    metrics["ram_used"] = round(ram.used / (1024 ** 3), 1) # GB
                    metrics["ram_total"] = round(ram.total / (1024 ** 3), 1) # GB
                except Exception:
                    pass

                # 3. GPU Info
                metrics["gpu_percent"] = 0
                metrics["gpu_temp"] = None
                metrics["gpu_name"] = "N/A"
                metrics["gpu_vram_used"] = 0.0
                metrics["gpu_vram_total"] = 0.0
                if GPUtil:
                    try:
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            metrics["gpu_percent"] = int(gpus[0].load * 100)
                            metrics["gpu_temp"] = int(gpus[0].temperature)
                            metrics["gpu_name"] = gpus[0].name
                            metrics["gpu_vram_used"] = round(gpus[0].memoryUsed / 1024, 1) # GB
                            metrics["gpu_vram_total"] = round(gpus[0].memoryTotal / 1024, 1) # GB
                    except Exception:
                        pass

                # 4. Storage Drives & Battery (Tiered Polling: every 5 ticks = ~5 seconds)
                if self.tick_count % 5 == 0 or not self.cached_drives:
                    drives_list = []
                    # Automatically discover all mounted partitions (internal & external drives)
                    try:
                        # dict.fromkeys deduplicates while preserving order
                        discovered_drives = list(dict.fromkeys(
                            p.device[:2].upper() for p in psutil.disk_partitions(all=False)
                            if p.fstype and 'cdrom' not in p.opts.lower()
                        ))
                    except Exception:
                        discovered_drives = self.settings.get("drive_letters", ["C:", "D:"])
                    
                    for drv in discovered_drives:
                        try:
                            usage = psutil.disk_usage(drv)
                            cpu_t = metrics.get("cpu_temp")
                            if cpu_t is None:
                                cpu_t = 42
                            cpu_offset = (cpu_t - 40) * 0.2
                            simulated_temp = int(32 + max(0.0, cpu_offset) + (usage.percent * 0.08))
                            drives_list.append({
                                "name": drv,
                                "percent": usage.percent,
                                "free": round(usage.free / (1024 ** 3), 1),
                                "total": round(usage.total / (1024 ** 3), 1),
                                "temp": simulated_temp
                            })
                        except Exception:
                            pass
                    self.cached_drives = drives_list

                    # Battery polling
                    bat_info = {"present": False}
                    try:
                        bat = psutil.sensors_battery()
                        if bat:
                            bat_info = {
                                "present": True,
                                "percent": int(bat.percent),
                                "power_plugged": bat.power_plugged,
                                "secsleft": bat.secsleft
                            }
                    except Exception:
                        pass
                    self.cached_battery = bat_info

                    # Top Processes (CPU & RAM)
                    cpu_procs = []
                    ram_procs = []
                    try:
                        for p in psutil.process_iter(['name', 'cpu_percent', 'memory_info']):
                            try:
                                cpu_pct = p.info['cpu_percent']
                                mem_used = p.info['memory_info'].rss
                                name = p.info['name']
                                if cpu_pct and cpu_pct > 0.5:
                                    cpu_procs.append((name, cpu_pct))
                                if mem_used and mem_used > 5 * 1024 * 1024:
                                    ram_procs.append((name, mem_used))
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                pass
                        cpu_procs = sorted(cpu_procs, key=lambda x: x[1], reverse=True)[:3]
                        ram_procs = sorted(ram_procs, key=lambda x: x[1], reverse=True)[:3]
                        ram_formatted = [(name, f"{mem / (1024**2):.1f}MB") for name, mem in ram_procs]
                        self.cached_top_cpu = cpu_procs
                        self.cached_top_ram = ram_formatted
                    except Exception:
                        pass

                metrics["drives"] = self.cached_drives
                metrics["battery"] = self.cached_battery
                metrics["top_cpu"] = self.cached_top_cpu
                metrics["top_ram"] = self.cached_top_ram

                # 5. Network Speed (Diff bytes)
                try:
                    net_io = psutil.net_io_counters()
                    bytes_sent = net_io.bytes_sent
                    bytes_recv = net_io.bytes_recv
                    
                    upload_speed = (bytes_sent - self.prev_net_sent) / dt
                    download_speed = (bytes_recv - self.prev_net_recv) / dt
                    
                    self.prev_net_sent = bytes_sent
                    self.prev_net_recv = bytes_recv
                except Exception:
                    upload_speed = 0
                    download_speed = 0
                    
                self.prev_time = current_time
                metrics["net_upload"] = max(0.0, upload_speed)
                metrics["net_download"] = max(0.0, download_speed)

                # Disk I/O Speeds
                try:
                    disk_io = psutil.disk_io_counters()
                    read_speed = (disk_io.read_bytes - self.prev_disk_read) / dt
                    write_speed = (disk_io.write_bytes - self.prev_disk_write) / dt
                    self.prev_disk_read = disk_io.read_bytes
                    self.prev_disk_write = disk_io.write_bytes
                except Exception:
                    read_speed = 0
                    write_speed = 0
                metrics["disk_read"] = max(0.0, read_speed)
                metrics["disk_write"] = max(0.0, write_speed)

                # Ping Latency (every 10 ticks = ~10s)
                if self.tick_count % 10 == 0 or self.cached_ping is None:
                    import socket
                    try:
                        start_t = time.time()
                        s = socket.create_connection(("1.1.1.1", 53), timeout=0.8)
                        s.close()
                        self.cached_ping = int((time.time() - start_t) * 1000)
                    except Exception:
                        self.cached_ping = -1
                metrics["net_ping"] = self.cached_ping

                self.metrics_updated.emit(metrics)
                self.tick_count += 1
            except Exception as e:
                print(f"Metrics worker iteration error: {e}")
            self.msleep(1000) # Poll fast loop every 1000ms

    def trigger_drives_update(self):
        self.cached_drives = []

    def stop(self):
        self.running = False
        self.wait()


class SettingsManager:
    def __init__(self, filename="widget_settings.json"):
        if not os.path.isabs(filename):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.filename = os.path.join(script_dir, filename)
        else:
            self.filename = filename
        self.mutex = QMutex()
        self.settings = copy.deepcopy(DEFAULT_SETTINGS)
        self.load_settings()

    def load_settings(self):
        locker = QMutexLocker(self.mutex)
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    loaded = json.load(f)
                    for key in self.settings:
                        if key in loaded:
                            if isinstance(self.settings[key], dict) and isinstance(loaded[key], dict):
                                self.settings[key].update(loaded[key])
                            else:
                                self.settings[key] = loaded[key]
                    # Schema migration: inject any new DEFAULT_SETTINGS keys absent from old JSON
                    for key, default_val in DEFAULT_SETTINGS.items():
                        if key not in loaded:
                            pass  # self.settings already has default from __init__, keep it
            except Exception as e:
                print(f"Error loading settings: {e}")

    def get(self, key, default=None):
        locker = QMutexLocker(self.mutex)
        val = self.settings.get(key, default)
        if isinstance(val, (dict, list)):
            return json.loads(json.dumps(val))
        return val

    def set(self, key, value):
        locker = QMutexLocker(self.mutex)
        self.settings[key] = value
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def set_batch(self, updates):
        """Apply multiple key-value pairs and write to disk only once."""
        locker = QMutexLocker(self.mutex)
        for key, value in updates.items():
            self.settings[key] = value
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
