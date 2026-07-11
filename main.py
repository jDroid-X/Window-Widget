import os
import sys

# Force working directory and sys.path to the folder of this script
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from widget_controller import WidgetController
from widget_view import WidgetBar

def main():
    # Fix High DPI scaling rendering blur on modern Windows resolutions
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        pass # Handle case for older Qt versions

    app = QApplication(sys.argv)
    
    # Single Instance Lock to prevent multiple overlapping widget processes
    from PyQt5.QtCore import QLockFile, QDir
    global lock_file
    lock_file = QLockFile(QDir.tempPath() + "/omnibar_widget_v2.lock")
    lock_file.setStaleLockTime(3000)
    if not lock_file.tryLock(100):
        print("OmniBar is already running. Exiting.")
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
