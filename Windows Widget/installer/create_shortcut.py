import os
import sys

def create_desktop_shortcut(target_dir=None):
    """Create or update the desktop shortcut for OmniBar.
    Returns (True, shortcut_path) on success, or (False, error_message) on failure.
    """
    try:
        import winshell
    except ImportError:
        return False, "'winshell' package is not installed (pip install winshell)"
    try:
        from win32com.client import Dispatch
    except ImportError:
        return False, "'pywin32' package is not installed (pip install pywin32)"

    try:
        if target_dir is None:
            target_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        desktop = winshell.desktop()
        old_path = os.path.join(desktop, "OmniBar Hardware Widget.lnk")
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass

        path = os.path.join(desktop, "jDroid-X OmniBar.lnk")

        # Resolve pythonw.exe robustly
        python_exe = sys.executable
        exe_dir = os.path.dirname(python_exe)
        pythonw_path = os.path.join(exe_dir, "pythonw.exe")
        if not os.path.isfile(pythonw_path):
            pythonw_path = python_exe.replace("python.exe", "pythonw.exe")
        if not os.path.isfile(pythonw_path):
            pythonw_path = python_exe

        script_path = os.path.abspath(os.path.join(target_dir, "main.py"))

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = pythonw_path
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = target_dir
        shortcut.IconLocation = r"C:\Windows\System32\imageres.dll, 219"
        shortcut.Description = "Launches jDroid-X OmniBar Hardware Widget"
        shortcut.save()
        return True, path
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    success, msg = create_desktop_shortcut()
    if success:
        print(f"Success: Shortcut created at {msg}")
    else:
        print(f"Error creating shortcut: {msg}")
