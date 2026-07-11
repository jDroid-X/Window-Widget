import os
import sys
import shutil
import winreg
import subprocess

# Define the target installation directory under the user profile folder
TARGET_DIR = os.path.join(os.environ["USERPROFILE"], "OmniBar")

def copy_files():
    print(f"[1/4] Copying files to installation directory: {TARGET_DIR}")
    try:
        os.makedirs(TARGET_DIR, exist_ok=True)
        
        # Files to install
        files_to_copy = [
            "main.py",
            "widget_model.py",
            "widget_view.py",
            "widget_settings_view.py",
            "widget_controller.py",
            "widget_settings.json",
            "requirements.txt",
            "installer_helper.py"
        ]
        
        source_dir = os.path.dirname(os.path.abspath(__file__))
        for file in files_to_copy:
            src = os.path.join(source_dir, file)
            dst = os.path.join(TARGET_DIR, file)
            if os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dst):
                shutil.copy2(src, dst)
                print(f"  Copied {file}")
        print("File copying completed successfully.")
    except Exception as e:
        print(f"Error copying files: {e}")
        sys.exit(1)

def install_dependencies():
    print("[2/4] Installing Python dependencies via pip...")
    try:
        # Run pip install referencing the requirements file inside the target installation directory
        req_file = os.path.join(TARGET_DIR, "requirements.txt")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        print("Dependencies installed successfully.")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def register_startup():
    print("[3/4] Registering OmniBar to start automatically with Windows...")
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
        exe_path = sys.executable.replace("python.exe", "pythonw.exe")
        main_script = os.path.abspath(os.path.join(TARGET_DIR, "main.py"))
        cmd = f'"{exe_path}" "{main_script}"'
        winreg.SetValueEx(key, "OmniBarWidget", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        print("Registry startup registration complete.")
    except Exception as e:
        print(f"Error registering startup: {e}")

def create_desktop_shortcut():
    print("[4/4] Creating Desktop shortcut...")
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        old_path = os.path.join(desktop, "OmniBar Hardware Widget.lnk")
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass
        path = os.path.join(desktop, "jDroid-X OmniBar.lnk")
        target = sys.executable.replace("python.exe", "pythonw.exe")
        script_path = os.path.abspath(os.path.join(TARGET_DIR, "main.py"))
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = TARGET_DIR
        shortcut.IconLocation = r"C:\Windows\System32\imageres.dll, 219"
        shortcut.Description = "Launches jDroid-X OmniBar Hardware Widget"
        shortcut.save()
        print(f"Desktop shortcut created successfully: {path}")
    except Exception as e:
        print(f"Error creating shortcut: {e}")

if __name__ == "__main__":
    copy_files()
    install_dependencies()
    register_startup()
    create_desktop_shortcut()
    print("\n===================================================")
    print("OmniBar installation completed successfully!")
    print(f"Installed Path: {TARGET_DIR}")
    print("===================================================\n")
