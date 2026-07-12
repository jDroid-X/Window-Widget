# Antigravity AI Enterprise OOPS MVC Architecture & Program Mapping

## 1. Chronological Order of Activities (Simple Waterfall OOPS MVC Lifecycle)

The entire application executes in strict sequential waterfall order following clean OOPS MVC decoupling:

```
1. main.py (Entry Point)
   ├── Apply High-DPI scaling attributes & Single Instance Lock
   ├── Instantiate WidgetController() [Controller]
   │    ├── Initialize SettingsManager() [Model]
   │    └── Start SystemMetricsWorker QThread [Model Worker]
   ├── Instantiate WidgetBar(settings, controller) [View]
   │    └── Build HardwareCard components (CPU, RAM, GPU, Drives, USB, WiFi, Battery, Clock)
   ├── Wire bidirectional Controller <-> View reference (controller.set_widget_bar(bar))
   └── Execute application event loop (app.exec_())
```

---

## 2. Master Program Mapping (Relationship & Dependency Table)

| Module / File | Layer (MVC) | Primary Responsibilities | Dependencies & Integration Points | Redundancy Status |
| :--- | :--- | :--- | :--- | :--- |
| **`main.py`** | Entry Point | Bootstrapping, DPI configuration, Single Instance Lock, MVC instantiation. | `WidgetController`, `WidgetBar` | Clean (No duplicates) |
| **`models/widget_model.py`** | Model | State persistence (`SettingsManager`), async hardware telemetry (`SystemMetricsWorker`), `THEMES` schema. | `psutil`, `WMI`, `QThread`, `json` | Clean (No duplicates) |
| **`controllers/widget_controller.py`** | Controller | Coordinates Model <-> View updates, System Tray lifecycle, Windows startup registry sync. | `WidgetBar`, `SettingsManager`, `SystemMetricsWorker` | Clean (No duplicates) |
| **`views/widget_view.py`** | Main View | Top-level OmniBar layout container, auto-hide edge animations, scale/orientation responsive geometry. | `HardwareCard` subclasses, `SettingsManager` | Audited & Cleaned |
| **`views/base_card.py`** | View Base | Abstract base class `HardwareCard`, polymorphically encapsulated `VectorIconWidget`. | `QPainter`, `SettingsManager` | Clean (No duplicates) |
| **`views/widget_settings_view.py`** | Configuration View | 4-Phase Waterfall Settings screen, direct real-time `⚡ Live Preview` updates. | `WidgetController`, `SettingsManager` | Clean (`set_batch` single source of truth) |
| **`views/cpu_display.py`** | Sub-View | CPU load, temp, clock frequency, top process tooltip rendering. | Inherits `HardwareCard` (`base_card.py`) | Clean |
| **`views/ram_display.py`** | Sub-View | RAM utilization percentage, absolute memory usage telemetry display. | Inherits `HardwareCard` (`base_card.py`) | Clean |
| **`views/gpu_display.py`** | Sub-View | GPU core utilization, VRAM usage, dedicated temperature monitoring. | Inherits `HardwareCard` (`base_card.py`) | Clean |
| **`views/drives_display.py`** | Sub-View | Storage drive partition occupancy & explorer launcher click action. | Inherits `HardwareCard` (`base_card.py`) | Clean |
| **`views/usb_display.py`** | Sub-View | Hot-swap removable USB storage partition detection & eject action. | Inherits `HardwareCard` (`base_card.py`) | Clean |
| **`views/wifi_display.py`** | Sub-View | Network SSID connection status & network control panel launcher. | Inherits `HardwareCard` (`base_card.py`) | Clean |
| **`views/battery_display.py`** | Sub-View | Battery percentage, charging status indicator, AC power telemetry. | Inherits `HardwareCard` (`base_card.py`) | Clean |
| **`views/datetime_display.py`** | Sub-View | Clock, calendar date display, and calendar launcher click action. | Inherits `HardwareCard` (`base_card.py`) | Clean |
| **`views/icon_view.py`** | View Strategy | Strategy pattern icon drawing definitions for crisp vector rendering. | Used by `VectorIconWidget` | Clean |

---

## 3. Code Redundancy & Duplication Audit Results

1. **Dead Imports Removed**:
   - Removed unused `from views.group_separator import GroupSeparatorWidget` in `views/widget_view.py`.
2. **Zero Code Duplication in Settings Persistence**:
   - Both `apply_live_changes()` and `save_settings()` utilize the shared `collect_settings_dict()` single-source-of-truth method, avoiding any duplicate dictionary construction logic.
3. **OOP Strategy & Inheritance Enforcement**:
   - All 8 hardware display widgets inherit directly from `HardwareCard` (`base_card.py`), eliminating repeated border, font, layout scaling, and progress bar drawing code.
