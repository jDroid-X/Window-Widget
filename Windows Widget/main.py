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
    """Acquire single-instance lock. Returns QLockFile on success, or None on failure after user declines."""
    # Clean up stale lock left by a previous crash
    if os.path.exists(lock_path):
        try:
            os.remove(lock_path)
            print("[INFO] Removed stale lock file.")
        except OSError:
            pass  # File may be legitimately locked by a running instance

    lock_file = QLockFile(lock_path)
    lock_file.setStaleLockTime(3000)

    if lock_file.tryLock(100):
        return lock_file

    # Lock acquisition failed — ask the user what to do
    response = QMessageBox.question(
        None,
        "OmniBar Already Running",
        "Another instance of OmniBar appears to be running.\n\n"
        "• Click 'Yes' to force-start a new instance.\n"
        "• Click 'No' to exit.",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )
    if response == QMessageBox.Yes:
        # Force-remove the lock and retry
        try:
            lock_file.removeStaleLockFile()
        except Exception:
            pass
        try:
            os.remove(lock_path)
        except OSError:
            pass
        lock_file = QLockFile(lock_path)
        lock_file.setStaleLockTime(3000)
        if lock_file.tryLock(100):
            return lock_file

    # User declined or second attempt also failed
    return None


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
    main()
