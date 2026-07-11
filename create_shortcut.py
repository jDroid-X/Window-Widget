import os
import sys
import winshell
from win32com.client import Dispatch

def create_shortcut():
    try:
        desktop = winshell.desktop()
        old_path = os.path.join(desktop, "OmniBar Hardware Widget.lnk")
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass
        path = os.path.join(desktop, "jDroid-X OmniBar.lnk")
        
        # Use pythonw.exe to prevent bringing up a blank command terminal background window
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, "main.py")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = current_dir
        # Standard system performance style green-graph monitor icon
        shortcut.IconLocation = r"C:\Windows\System32\imageres.dll, 219" 
        shortcut.Description = "Launches jDroid-X OmniBar Hardware Widget"
        shortcut.save()
        print(f"Success: Shortcut created at {path}")
    except Exception as e:
        print(f"Error creating shortcut: {e}")

if __name__ == "__main__":
    create_shortcut()
