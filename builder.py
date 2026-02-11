import os
import subprocess
import sys
import shutil

def build():
    script = "death.py"
    icon = "DEATH.ico"
    logo = "DEATH.jpg"
    app_name = "DEATH_REF"
    
    print("Cleaning workspace...")
    for item in ['dist', 'build', f"{app_name}.spec"]:
        if os.path.exists(item):
            try:
                if os.path.isdir(item): shutil.rmtree(item)
                else: os.remove(item)
            except: pass

    if not os.path.exists(script):
        print(f"Error: {script} not found!")
        return

    print(f"--- Building {app_name} ---")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--name={app_name}",
        "--collect-all", "customtkinter",
        "--collect-all", "tkinterdnd2",
        "--collect-all", "cv2",
        f"--add-data={logo}{os.pathsep}.",
        f"--add-data={icon}{os.pathsep}.",
        f"--icon={icon}",
        script
    ]

    try:
        subprocess.check_call(cmd)
        print(f"\n[+] SUCCESS! File saved in 'dist/{app_name}.exe'")
    except Exception as e:
        print(f"\n[-] Build failed: {e}")

if __name__ == "__main__":
    build()
    input("\nBuild process complete. Press Enter to close...")
