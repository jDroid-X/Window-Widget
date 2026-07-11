# 🚀 OmniBar Hardware Widget

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?style=for-the-badge&logo=windows)](https://github.com/jDroid-X/Window-Widget)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**OmniBar** is a sleek, ultra-customizable hardware monitoring bar and dock for Windows 10 & 11. It docks cleanly to any screen edge with smart margins, monitors real-time CPU, RAM, Disk, Network, and Battery stats, and features stunning neon & radium spectral themes.

---

## ✨ Key Features

- **📊 Real-Time Hardware Monitoring:** Live CPU load, RAM usage, Disk utilization, Network upload/download speeds, and Battery level.
- **🌈 Vibrant Radium & Spectral Themes:**
  - `Sleek Dark` — Clean, minimal dark interface with cyan accents.
  - `Vibrant Blue` — Deep navy background with teal/aqua highlights.
  - `Forest Glass` — Nature-inspired dark-green glassmorphism.
  - `Light Minimal` — Clean light background with indigo accents.
  - `Radium Rainbow` — Spectral neon rainbow glow with smooth dark backgrounds.
  - `Neon Radium` — Glowing radioactive green accents.
- **🖥️ Smart Screen Docking:**
  - Dock to **Top**, **Bottom**, **Left**, or **Right**.
  - Automatically maintains a clean **3cm / ~115px edge gap** on both sides so it never overlaps or blocks screen corners.
  - Responsive font scaling (`Small`, `Medium`, `Large`) with proportional layout resizing.
- **🔒 Single-Instance Protection:** Prevents duplicate taskbars or overlapping instances automatically (`QLockFile`).
- **📌 Desktop Shortcut & Auto-Startup:** Automatically registers for Windows Startup and creates a handy desktop shortcut named **`jDroid-X OmniBar`** (formatted across 2 rows on desktop).

---

## ⚡ Quick Installation (Direct from GitHub)

You can install and launch **OmniBar** directly from this repository on any Windows PC with Python installed.

### Method 1: One-Line PowerShell Installer (Recommended)
Open **PowerShell** and run:
```powershell
irm https://raw.githubusercontent.com/jDroid-X/Window-Widget/main/install.ps1 | iex
```
This command will automatically:
1. Download the latest version from `https://github.com/jDroid-X/Window-Widget`.
2. Install files to your user profile directory (`C:\Users\<Username>\OmniBar`).
3. Install required Python packages (`PyQt5`, `psutil`, `GPUtil`, `pywin32`, `winshell`).
4. Create the Desktop shortcut (**`jDroid-X OmniBar`**) and register Windows auto-start.
5. Launch the widget cleanly in the background.

---

### Method 2: Clone or Download ZIP
1. **Download ZIP** from GitHub: [Download Latest Release](https://github.com/jDroid-X/Window-Widget/archive/refs/heads/main.zip) (or `git clone https://github.com/jDroid-X/Window-Widget.git`).
2. Extract the folder.
3. Double-click **`install.bat`** inside the folder.

---

## 🛠️ Desktop Shortcut & Installation Path

- **Installation Directory:** `%USERPROFILE%\OmniBar` (e.g., `C:\Users\YourUsername\OmniBar`)
- **Desktop Shortcut Name:** `jDroid-X OmniBar` (displays across 2 rows on Desktop)

Double-clicking the desktop shortcut runs `main.py` via `pythonw.exe` without opening a command prompt window.

---

## ⚙️ Customization & Settings

Right-click anywhere on the OmniBar widget, use the Windows System Tray icon, or click the **⚙️ Settings** icon to open the Settings panel where you can:
- **Visual Theme & Custom Color:** Choose curated palettes (*Radium Rainbow*, *Neon Radium*, *Sleek Dark*) or use the **Custom Background Color Chooser** (#HEX color dialog) with adjustable opacity %.
- **RAG Threshold Controls:** Configure custom warning (amber) and critical (red) limits for CPU, RAM, and GPU percentage indicators.
- **Unified Storage Drives:** View all internal and external partitions grouped together under one clean **STORAGE DRIVES (°C)** card. Clicking opens Windows Explorer ("This PC").
- **Dock Position & System Tray Checks:** Dock to *Top*, *Bottom*, *Left*, or *Right* with active checkmarks (`✓`) displayed in the System Tray context menu.
- **Edge Auto-Hide:** Accurate off-screen auto-hide geometry for horizontal and vertical dock layouts.
