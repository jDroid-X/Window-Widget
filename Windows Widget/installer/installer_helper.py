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
        
        # Resolve source root directory (parent of installer/ folder)
        installer_dir = os.path.dirname(os.path.abspath(__file__))
        source_root = os.path.dirname(installer_dir)
        
        # Subdirectories to copy
        subdirs = ["models", "views", "controllers", "installer"]
        for s in subdirs:
            src_sub = os.path.join(source_root, s)
            dst_sub = os.path.join(TARGET_DIR, s)
            
            temp_settings = None
            if s == "models":
                settings_dst = os.path.join(dst_sub, "widget_settings.json")
                if os.path.exists(settings_dst):
                    try:
                        with open(settings_dst, 'r') as f:
                            temp_settings = f.read()
                    except Exception:
                        pass

            if os.path.exists(dst_sub):
                shutil.rmtree(dst_sub, ignore_errors=True)
                
            shutil.copytree(src_sub, dst_sub)
            
            if s == "models" and temp_settings is not None:
                try:
                    with open(os.path.join(dst_sub, "widget_settings.json"), 'w') as f:
                        f.write(temp_settings)
                    print("  Preserved existing user configuration (widget_settings.json)")
                except Exception as e:
                    print(f"  Warning: Could not restore settings: {e}")
            print(f"  Copied directory {s}/")

        # Copy main.py
        shutil.copy2(os.path.join(source_root, "main.py"), os.path.join(TARGET_DIR, "main.py"))
        print("  Copied main.py")
        print("File copying completed successfully.")
    except Exception as e:
        print(f"Error copying files: {e}")
        sys.exit(1)

def install_dependencies():
    print("[2/4] Installing Python dependencies via pip...")
    try:
        # Run pip install referencing the requirements file inside the target installation directory
        req_file = os.path.join(TARGET_DIR, "installer", "requirements.txt")
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
        from create_shortcut import create_desktop_shortcut as _create_shortcut
        success, msg = _create_shortcut(TARGET_DIR)
        if success:
            print(f"  Desktop shortcut created successfully: {msg}")
        else:
            print(f"  [ERROR] Could not create shortcut: {msg}")
    except Exception as e:
        print(f"  [ERROR] Could not create shortcut: {e}")

if __name__ == "__main__":
    copy_files()
    install_dependencies()
    register_startup()
    create_desktop_shortcut()
    print("\n===================================================")
    print("OmniBar installation completed successfully!")
    print(f"Installed Path: {TARGET_DIR}")
    print("===================================================\n")
