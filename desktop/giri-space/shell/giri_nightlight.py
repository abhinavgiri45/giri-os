#!/usr/bin/env python3
"""
Giri OS — Night Light & Display Temperature Governor (Giri Night Light)
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Provides circadian blue-light reduction and display color temperature adjustments
for Giri OS 0.1 Genesis using standard X11 xrandr gamma curves.
Zero heavy dependencies: works on all GPU drivers (Intel HD 2000, AMD, NVIDIA, VMSVGA).
"""

import sys
import os
import json
import subprocess
import time

CONFIG_DIR = os.path.expanduser("~/.config/giri")
CONFIG_FILE = os.path.join(CONFIG_DIR, "nightlight.json")

TEMPERATURE_PRESETS = {
    "day": {"name": "Daylight (6500K)", "gamma": "1.0:1.0:1.0", "temp": 6500, "desc": "Normal full-spectrum color profile"},
    "sunset": {"name": "Sunset (4500K)", "gamma": "1.0:0.88:0.75", "temp": 4500, "desc": "Subtle blue reduction for evening work"},
    "warm": {"name": "Warm Night (3500K)", "gamma": "1.0:0.78:0.60", "temp": 3500, "desc": "Comfortable amber tone for nighttime reading"},
    "bedtime": {"name": "Bedtime (2800K)", "gamma": "1.0:0.68:0.45", "temp": 2800, "desc": "Maximum blue suppression for low-light environments"}
}


def load_config():
    """Loads night light configuration from user state."""
    defaults = {
        "enabled": False,
        "mode": "manual",  # 'manual' or 'schedule'
        "current_preset": "day",
        "schedule_start": "20:00",
        "schedule_end": "07:00"
    }
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
    return defaults


def save_config(cfg):
    """Saves night light configuration."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def apply_gamma(gamma_str):
    """Applies gamma string (r:g:b) via xrandr across all connected active outputs."""
    # Check xrandr availability
    if sys.platform != "linux":
        return True  # Mock success on development host

    try:
        # Query connected displays
        res = subprocess.run(["xrandr", "--query"], capture_output=True, text=True)
        if res.returncode != 0:
            return False
        
        outputs = []
        for line in res.stdout.splitlines():
            if " connected" in line:
                out_name = line.split()[0]
                outputs.append(out_name)

        if not outputs:
            # Fallback apply without specifying output
            subprocess.run(["xrandr", "--gamma", gamma_str], check=False)
            return True

        for out in outputs:
            subprocess.run(["xrandr", "--output", out, "--gamma", gamma_str], check=False)
        return True
    except Exception as e:
        print(f"Error applying gamma {gamma_str}: {e}")
        return False


def set_preset(preset_key):
    """Sets a specific color temperature preset and updates configuration."""
    if preset_key not in TEMPERATURE_PRESETS:
        return False
    cfg = load_config()
    cfg["current_preset"] = preset_key
    cfg["enabled"] = (preset_key != "day")
    save_config(cfg)
    gamma = TEMPERATURE_PRESETS[preset_key]["gamma"]
    apply_gamma(gamma)
    return True


def toggle():
    """Toggles between Day (Normal) and Warm Night."""
    cfg = load_config()
    if cfg["enabled"]:
        set_preset("day")
        return "Daylight"
    else:
        set_preset("warm")
        return "Warm Night"


def main():
    if "--verify" in sys.argv:
        print("[+] Verifying Giri Night Light...")
        cfg = load_config()
        assert "enabled" in cfg
        assert "current_preset" in cfg
        assert "day" in TEMPERATURE_PRESETS
        assert "warm" in TEMPERATURE_PRESETS
        print("[+] Giri Night Light logic verified.")
        sys.exit(0)

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ["--toggle", "-t", "toggle"]:
            mode = toggle()
            print(f"Night Light toggled: {mode}")
            sys.exit(0)
        elif cmd in ["--off", "off", "day", "--day"]:
            set_preset("day")
            print("Night Light disabled (Daylight 6500K restored)")
            sys.exit(0)
        elif cmd in ["--warm", "warm", "night", "--night"]:
            set_preset("warm")
            print("Night Light set to Warm Night (3500K)")
            sys.exit(0)
        elif cmd in ["--sunset", "sunset"]:
            set_preset("sunset")
            print("Night Light set to Sunset (4500K)")
            sys.exit(0)
        elif cmd in ["--bedtime", "bedtime"]:
            set_preset("bedtime")
            print("Night Light set to Bedtime (2800K)")
            sys.exit(0)
        else:
            print(f"Unknown argument: {cmd}")
            sys.exit(1)

    # Standalone GUI mini-control if invoked without arguments
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title("Giri Night Light")
        root.geometry("380x280")
        root.configure(bg="#080C1A")

        tk.Label(root, text="GIRI NIGHT LIGHT", font=("Segoe UI", 12, "bold"), fg="#00D2FF", bg="#080C1A").pack(pady=12)
        tk.Label(root, text="Circadian Eye Comfort & Display Temperature", font=("Segoe UI", 9), fg="#8EA4C8", bg="#080C1A").pack(pady=(0, 12))

        for k, v in TEMPERATURE_PRESETS.items():
            btn = tk.Button(
                root,
                text=f"{v['name']} — {v['desc']}",
                font=("Segoe UI", 9),
                bg="#0F172A",
                fg="#C2D5EE",
                activebackground="#1E293B",
                activeforeground="#00D2FF",
                relief="flat",
                pady=6,
                command=lambda pk=k: [set_preset(pk), root.destroy()]
            )
            btn.pack(fill="x", padx=16, pady=3)

        root.mainloop()
    except Exception:
        pass


if __name__ == "__main__":
    main()
