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

---

## 4. Concurrency & Lifecycle Segregation Matrix (Sequential vs. Parallel Activities)

### A. Sequential Activities (Main GUI Thread - Deterministic Lifecycle)
1. **Application Bootstrap (`main.py`)**: High-DPI attributes setup and Single-Instance Lock (`QLockFile`) acquisition.
2. **MVC Initialization (`WidgetController`)**: State normalization (`SettingsManager`), View instantiation (`WidgetBar`), and bidirectional reference wiring.
3. **GUI Event Loop (`app.exec_()`)**: Deterministic handling of user clicks, drag events, context menus, and graceful shutdown.

### B. Parallel Activities (Asynchronous Background Threads & Independent Event Timers)
1. **Telemetry Harvesting (`SystemMetricsWorker` QThread)**:
   - Runs independently every 1000ms on a background thread so disk/WMI/sensor queries never block GUI rendering.
   - **Smooth Integration Point**: Emits thread-safe `metrics_updated(dict)` Qt Queued Connection signal across the thread boundary -> received cleanly by `WidgetController.on_metrics_updated()`.
2. **Edge Auto-Hide Monitor (`QTimer` in `WidgetBar`)**:
   - Runs independently every 150ms to check mouse hover state.
   - **Smooth Integration Point**: Triggers non-blocking `QPropertyAnimation` slide transitions when the cursor enters or leaves the trigger edge.
3. **Real-Time Live Preview (`⚡ Live Preview`)**:
   - Runs interactively in `SettingsWindow`.
   - **Smooth Integration Point**: Uses `collect_settings_dict()` batch payload -> `controller.apply_configuration()` to update the live desktop bar without blocking modal dialog input.

---

## 5. High-to-Low Priority Waterfall Dataflow Hierarchy & UI/UX Field Chronology (Prime Directive Waterfall Method)

Following the Prime Directive Simple Waterfall Method and Closed-Loop Feedback structure, data and control flow strictly from **Highest Priority (Top — Kernel & State)** down to **Lowest Priority (Bottom — Presentation & Customization)**, with a closed feedback loop returning from user interaction back to the top layers.

```
TOP PRIORITY (Kernel & State Single Source of Truth)
   │   1. Identity & OS Lock (main.py -> QLockFile)
   │   2. Normalized State Schema (models/widget_model.py -> SettingsManager)
   ▼
HIGH PRIORITY (Asynchronous Telemetry Engine - Parallel Model)
   │   3. Hardware Sensors & Telemetry Fields (SystemMetricsWorker)
   │      [CPU Load/Temp/Freq -> RAM -> GPU -> Drives -> USB -> WiFi -> Battery -> Clock]
   ▼
MIDDLE PRIORITY (OOPS MVC Controller & Closed-Loop Router)
   │   4. Lifecycle & Signal Routing (controllers/widget_controller.py -> WidgetController)
   │      [Coordinates Model Signals -> View Repainting & OS System Tray]
   ▼
PRESENTATION PRIORITY (Primary Desktop Shell UI/UX Layout)
   │   5. Top-Level Shell Geometry (views/widget_view.py -> WidgetBar)
   │      [Always-On-Top ToolWindow -> Smart Best-Fit Sizing -> Edge Auto-Hide Docking]
   ▼
SUB-VIEW PRIORITY (Polymorphic Hardware Card Layout & Fields)
   │   6. Card Component Rendering (views/base_card.py -> HardwareCard)
   │      [Vector Icon -> Primary Value Box -> Secondary Telemetry Text -> Multi-Threshold Progress Bars]
   ▼
LOWEST PRIORITY / CLOSED-LOOP ENTRY (Interactive Configuration & Theme Hierarchy)
       7. 4-Phase Waterfall Customization Modal (views/widget_settings_view.py -> SettingsWindow)
          ├── Phase 1: Aesthetics (Theme Chronological Priority: Sleek Dark -> Vibrant Blue -> Forest Glass -> Light Minimal -> Radium Rainbow -> Neon Radium)
          ├── Phase 2: Layout & Docking (Medium Scale Preset -> Dock Position -> Auto-Hide Toggle)
          ├── Phase 3: CardView Customization (4px Inter-Card Spacing -> Font Family -> Show Border)
          └── Phase 4: Hardware Cards & Thresholds (Individual Card Visibility -> Warning/Critical Thresholds)
          │
          └── [CLOSED-LOOP FEEDBACK]: User UI Action -> collect_settings_dict() -> SettingsManager.set_batch() -> WidgetController.apply_configuration() -> Immediate Repaint (No Restart)
```

### Chronological Order of Fields & Codes by Layer Priority

#### Priority Tier 1: Kernel & Persistent State Fields (`models/widget_model.py`)
1. **System Identity & Integrity**: `lock_path`, `single_instance_lock`
2. **Core Presentation Scale & Orientation**: `bar_scale` (`small`/`medium`/`large`), `dock_position` (`top`/`bottom`/`left`/`right`)
3. **Core Feature Toggles**: `enable_autohide`, `enable_startup`, `card_spacing` (`4px` default)

#### Priority Tier 2: Asynchronous Telemetry Fields (`SystemMetricsWorker`)
Ordered chronologically by critical hardware frequency:
1. `cpu_percent`, `cpu_temp`, `cpu_freq`, `cpu_cores_phys`, `cpu_cores_logical`
2. `ram_percent`, `ram_used_gb`, `ram_total_gb`
3. `gpu_percent`, `gpu_temp`, `gpu_vram_used_gb`
4. `drives` list (`name`, `label`, `percent`, `free`, `total`)
5. `usb_drives` list (removable hot-swap volumes)
6. `wifi_ssid` (network connectivity)
7. `battery_percent`, `is_charging` (power state)
8. `date_str`, `time_str` (clock ticks)

#### Priority Tier 3: MVC Controller Routing Protocol (`WidgetController`)
1. `settings` (`SettingsManager` reference)
2. `worker` (`SystemMetricsWorker` reference)
3. `widget_bar` (`WidgetBar` reference)
4. `tray_icon` (`QSystemTrayIcon` reference)

#### Priority Tier 4 & 5: UI/UX Component & Card Field Chronology (`WidgetBar` & `HardwareCard`)
1. **Shell Container Fields**: `normal_geometry`, `hidden_geometry`, `hide_timer`, `anim` (`QPropertyAnimation`)
2. **Card Visual Fields**:
   - `icon_widget` (`VectorIconWidget` polymorphic graphic)
   - `val` (`QLabel` primary metric box synchronized to icon height)
   - `sub_lbl` (`QLabel` secondary detail telemetry string)
   - `prog_bars` (`QProgressBar` threshold-colored indicator bars)

#### Priority Tier 6: 4-Phase Settings UI & Closed Feedback Loop Protocol (`SettingsWindow`)
- **Visual Theme Chronological Priority Sequence**:
  1. `Sleek Dark` (Priority 1 Core Default)
  2. `Vibrant Blue` (Priority 2 Cyber Theme)
  3. `Forest Glass` (Priority 3 Emerald Theme)
  4. `Light Minimal` (Priority 4 Light Theme)
  5. `Radium Rainbow` (Priority 5 Spectral Theme)
  6. `Neon Radium` (Priority 6 Neon Theme)
- **Closed-Loop Feedback Flow**:
  1. User interacts with any control in `SettingsWindow`
  2. `collect_settings_dict()` extracts UI state atomically
  3. `SettingsManager.set_batch(updates)` persists changes cleanly
  4. `WidgetController.apply_configuration()` broadcasts state change to `WidgetBar`
  5. Cards reposition, scale, and recolor instantly (`⚡ Live Preview`) completing the feedback loop.
