import os
import sys
import shutil
import winreg
import subprocess
import time
import json

# Define the target installation directory under the user profile folder
TARGET_DIR = os.path.join(os.environ["USERPROFILE"], "OmniBar")

def terminate_existing_instance():
    """Terminate any running OmniBar instance before reinstalling."""
    try:
        import psutil
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['pid'] == current_pid:
                continue
            try:
                cmdline = proc.info.get('cmdline') or []
                cmdline_str = ' '.join(cmdline).lower()
                # Match any python/pythonw process running OmniBar's main.py
                if 'main.py' in cmdline_str and 'omnibar' in cmdline_str:
                    pid = proc.info['pid']
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                        print(f"[Pre-install] Terminated previous OmniBar process PID {pid}")
                    except Exception:
                        try:
                            proc.kill()
                            print(f"[Pre-install] Force-killed OmniBar process PID {pid}")
                        except Exception:
                            pass
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"[Pre-install] Could not clean previous instance: {e}")

def copy_files():
    # Ensure any running instance is stopped before copying
    terminate_existing_instance()
    print(f"[1/4] Copying files to installation directory: {TARGET_DIR}")
    try:
        # Ensure the base installation directory exists
        os.makedirs(TARGET_DIR, exist_ok=True)

        installer_dir = os.path.dirname(os.path.abspath(__file__))
        # Repository root (one level up from the installer folder)
        repo_root = os.path.abspath(os.path.join(installer_dir, ".."))
        # Source root is the repository root (no separate src folder)
        source_root = repo_root

        # PowerShell runs this helper from the already-copied target directory.
        # Always copy files to ensure updates propagate, even if target already exists.
        # No early return; we will copy files regardless of source/target equality.


        subdirs = ["models", "views", "controllers", "installer"]
        for s in subdirs:
            src_sub = os.path.join(source_root, s)
            dst_sub = os.path.join(TARGET_DIR, s)
            
            if not os.path.isdir(src_sub):
                print(f"[WARN] Source subdirectory '{s}' not found at {src_sub}, skipping.")
                continue
            
            temp_settings = None
            if s == "models":
                settings_dst = os.path.join(dst_sub, "widget_settings.json")
                if os.path.exists(settings_dst):
                    try:
                        with open(settings_dst, 'r') as f:
                            temp_settings = f.read()
                    except Exception:
                        pass
            
            # Ensure destination exists (copytree will create if needed)
            os.makedirs(TARGET_DIR, exist_ok=True)  # Ensure parent directory exists
            # os.makedirs(dst_sub, exist_ok=True)  # removed to let copytree handle creation
            # Remove existing destination subdirectory to avoid copy errors
            if os.path.isdir(dst_sub):
                shutil.rmtree(dst_sub)
            # Copy source directory to destination
            print(f"  Copying {s} from {src_sub} to {dst_sub}")
            shutil.copytree(src_sub, dst_sub, dirs_exist_ok=True)
            
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
        print(f"[ERROR] Error copying files: {e}")
        raise


def install_dependencies():
    print("[2/4] Installing Python dependencies via pip...")
    try:
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
    # Exit after installation; launching the widget is the caller's responsibility.
    sys.exit(0)
