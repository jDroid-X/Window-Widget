import os
import sys

# Force working directory and sys.path to the folder of this script
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt5.QtCore import Qt, QLockFile, QDir
from PyQt5.QtWidgets import QApplication, QMessageBox
from controllers.widget_controller import WidgetController
from views.widget_view import WidgetBar


def _apply_dpi_settings():
    """Apply High-DPI scaling attributes before QApplication is created."""
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        pass  # Older Qt versions don't support these attributes


def _acquire_lock(lock_path):
    """Acquire single-instance lock. Automatically terminates any older instance so the new instance takes over cleanly."""
    lock_file = QLockFile(lock_path)
    lock_file.setStaleLockTime(30000)

    if lock_file.tryLock(100):
        return lock_file

    # Automatically terminate existing/old OmniBar instance
    try:
        import psutil
        current_pid = os.getpid()
        for p in psutil.process_iter(['pid', 'name', 'cmdline']):
            if p.info['pid'] == current_pid:
                continue
            cmd = ' '.join(p.info.get('cmdline') or []).lower()
            if 'main.py' in cmd and ('omnibar' in cmd or 'windows widget' in cmd):
                try:
                    p.terminate()
                    p.wait(timeout=2)
                except Exception:
                    pass
    except Exception:
        pass

    # Remove stale lock file if present and retry acquiring lock
    lock_file.removeStaleLockFile()
    if lock_file.tryLock(500):
        return lock_file

    return lock_file

def main():
    _apply_dpi_settings()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Single Instance Lock to prevent multiple overlapping widget processes
    lock_path = QDir.tempPath() + "/omnibar_widget_v2.lock"
    lock_file = _acquire_lock(lock_path)
    if lock_file is None:
        print("OmniBar: exiting (lock not acquired).")
        sys.exit(0)

    # Run MVC Controller structure
    controller = WidgetController()
    bar = WidgetBar(controller.settings, controller)
    controller.set_widget_bar(bar)
    bar.show()

    exit_code = app.exec_()
    controller.shutdown()
    lock_file.unlock()
    sys.exit(exit_code)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback, os
        log_file = os.path.join(os.path.dirname(__file__), "error_log.txt")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("--- Exception during startup ---\n")
            f.write(traceback.format_exc())
        print(f"[ERROR] OmniBar failed to start: {e}")
        # Ensure the application exits cleanly
        sys.exit(1)
