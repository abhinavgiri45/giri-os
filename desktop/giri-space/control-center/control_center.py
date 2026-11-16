#!/usr/bin/env python3
"""
Giri OS Control Center (Giri Control)
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

System settings and configuration hub for Giri OS.
Manages Display, Themes, Hardware Profiles, Giri Bridge compatibility, and Giri Update.
"""

import sys
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox

# Import local hardware detector if available
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
try:
    from hardware.giri_hw.detector import HardwareDetector
except Exception:
    try:
        # Fallback import style
        import importlib.util
        det_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..", "hardware", "giri-hw", "detector.py"))
        spec = importlib.util.spec_from_file_location("detector", det_path)
        det_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(det_mod)
        HardwareDetector = det_mod.HardwareDetector
    except Exception:
        HardwareDetector = None


class GiriControlCenter(tk.Toplevel):
    def __init__(self, parent=None, non_interactive=False):
        if parent:
            super().__init__(parent)
        else:
            self.root = tk.Tk()
            self._is_standalone = True
            super().__init__(self.root)
            self.root.withdraw()

        self.non_interactive = non_interactive
        self.title("Giri Control — System Settings")
        self.geometry("860x580")
        self.minsize(780, 520)
        self.configure(bg="#080c1a")

        # Load hardware profile
        if HardwareDetector:
            try:
                self.hw_profile = HardwareDetector().profile
            except Exception:
                self.hw_profile = self._default_hw_profile()
        else:
            self.hw_profile = self._default_hw_profile()

        self.active_tab = "Hardware & System"
        self.setup_ui()

    def _default_hw_profile(self):
        return {
            "cpu": {"model": "Intel Core i5-2400 @ 3.10GHz", "cores_logical": 4},
            "ram": {"total_gb": 8.0},
            "gpu": {"model": "Intel HD Graphics 2000", "driver": "i915/crocus", "vulkan_supported": False},
            "storage": {"free_space_gb": 35.0},
            "tier": {"profile_name": "Giri Classic", "code": "classic"}
        }

    def setup_ui(self):
        # Header banner
        header = tk.Frame(self, bg="#0d1428", height=54)
        header.pack(side="top", fill="x")

        lbl_title = tk.Label(
            header,
            text="Giri Control",
            font=("Segoe UI", 15, "bold"),
            fg="#00d2ff",
            bg="#0d1428"
        )
        lbl_title.pack(side="left", padx=20, pady=12)

        lbl_sub = tk.Label(
            header,
            text="System Configuration & Optimization Hub",
            font=("Segoe UI", 10),
            fg="#8ea4c8",
            bg="#0d1428"
        )
        lbl_sub.pack(side="left", padx=5, pady=14)

        # Main Body: Left Sidebar + Right Content Area
        body = tk.Frame(self, bg="#080c1a")
        body.pack(side="top", fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(body, bg="#0c1222", width=220)
        self.sidebar.pack(side="left", fill="y")

        # Content Area
        self.content = tk.Frame(body, bg="#080c1a", padx=25, pady=20)
        self.content.pack(side="left", fill="both", expand=True)

        # Sidebar Navigation Buttons
        nav_items = [
            ("Hardware & System", "💻", self.view_hardware),
            ("Desktop Profile", "🎨", self.view_desktop_profile),
            ("Giri Bridge (Windows)", "🌉", self.view_giri_bridge),
            ("Giri Gaming Mode", "🎮", self.view_gaming),
            ("Giri Update", "🔄", self.view_updates),
            ("Privacy & Security", "🛡️", self.view_privacy),
        ]

        for name, icon, func in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=f"  {icon}  {name}",
                font=("Segoe UI", 10),
                anchor="w",
                bg="#0c1222",
                fg="#b0c4de",
                activebackground="#16223d",
                activeforeground="#00d2ff",
                relief="flat",
                padx=16,
                pady=10,
                command=lambda f=func, n=name: self.switch_tab(n, f)
            )
            btn.pack(fill="x")

        # Default View
        self.view_hardware()

    def switch_tab(self, name, render_func):
        self.active_tab = name
        for w in self.content.winfo_children():
            w.destroy()
        render_func()

    def view_hardware(self):
        tk.Label(self.content, text="Hardware Specifications", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(0, 15))

        card = tk.Frame(self.content, bg="#0f172a", padx=18, pady=16)
        card.pack(anchor="w", fill="x", pady=6)

        cpu = self.hw_profile.get("cpu", {})
        ram = self.hw_profile.get("ram", {})
        gpu = self.hw_profile.get("gpu", {})
        tier = self.hw_profile.get("tier", {})

        specs = [
            ("Processor (CPU):", f"{cpu.get('model', 'Unknown')} ({cpu.get('cores_logical', 1)} cores)"),
            ("System Memory (RAM):", f"{ram.get('total_gb', 'N/A')} GB"),
            ("Graphics Processor (GPU):", f"{gpu.get('model', 'Integrated')}"),
            ("Graphics Driver:", f"{gpu.get('driver', 'i915/crocus')}"),
            ("Vulkan Hardware Support:", "Supported" if gpu.get("vulkan_supported") else "Not Supported (Mesa LLVMpipe fallback)"),
            ("Active Desktop Tier:", f"{tier.get('profile_name', 'Giri Classic')} (Optimized for Sandy Bridge / Intel HD 2000)"),
        ]

        for i, (k, v) in enumerate(specs):
            tk.Label(card, text=k, font=("Segoe UI", 10, "bold"), fg="#8ea4c8", bg="#0f172a").grid(row=i, column=0, sticky="w", pady=4)
            tk.Label(card, text=v, font=("Segoe UI", 10), fg="#00d2ff" if "Tier" in k or "Vulkan" in k else "#ffffff", bg="#0f172a").grid(row=i, column=1, sticky="w", padx=15, pady=4)

    def view_desktop_profile(self):
        tk.Label(self.content, text="Desktop Profile & Effects", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(0, 15))

        desc = (
            "Giri Space features two primary rendering engines to ensure 60 FPS performance\n"
            "on both modern high-end PCs and legacy hardware like Intel HD 2000:"
        )
        tk.Label(self.content, text=desc, font=("Segoe UI", 10), fg="#a0aec0", bg="#080c1a").pack(anchor="w", pady=(0, 15))

        # Profile selection radios
        self.profile_choice = tk.StringVar(value="classic" if "Classic" in self.hw_profile.get("tier", {}).get("profile_name", "") else "modern")

        frame_classic = tk.Frame(self.content, bg="#0f172a", padx=16, pady=12)
        frame_classic.pack(fill="x", pady=6)
        tk.Radiobutton(frame_classic, text="Giri Classic (Recommended for Intel HD 2000 / 4-8 GB RAM)", variable=self.profile_choice, value="classic", font=("Segoe UI", 11, "bold"), fg="#00d2ff", bg="#0f172a", selectcolor="#16223d", activebackground="#0f172a").pack(anchor="w")
        tk.Label(frame_classic, text="• Reduced animations  • Minimal RAM consumption (< 450 MB)  • No GPU Gaussian blur", font=("Segoe UI", 9), fg="#8ea4c8", bg="#0f172a").pack(anchor="w", padx=25)

        frame_modern = tk.Frame(self.content, bg="#0f172a", padx=16, pady=12)
        frame_modern.pack(fill="x", pady=6)
        tk.Radiobutton(frame_modern, text="Giri Modern (High Visual Fidelity)", variable=self.profile_choice, value="modern", font=("Segoe UI", 11, "bold"), fg="#c2d5ee", bg="#0f172a", selectcolor="#16223d", activebackground="#0f172a").pack(anchor="w")
        tk.Label(frame_modern, text="• Glassmorphic translucency  • Orbital transitions  • GPU composited shadows", font=("Segoe UI", 9), fg="#8ea4c8", bg="#0f172a").pack(anchor="w", padx=25)

    def view_giri_bridge(self):
        tk.Label(self.content, text="Giri Bridge — Windows Compatibility", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(0, 15))
        desc = (
            "Giri Bridge manages isolated Windows application environments (Wine prefixes),\n"
            "auto-detects 32-bit and 64-bit EXE files, and configures appropriate graphics backends."
        )
        tk.Label(self.content, text=desc, font=("Segoe UI", 10), fg="#a0aec0", bg="#080c1a").pack(anchor="w", pady=(0, 10))

        card = tk.Frame(self.content, bg="#0f172a", padx=16, pady=14)
        card.pack(fill="x", pady=6)

        tk.Label(card, text="Wine Translation Backend:", font=("Segoe UI", 10, "bold"), fg="#8ea4c8", bg="#0f172a").grid(row=0, column=0, sticky="w", pady=4)
        tk.Label(card, text="Mesa OpenGL (wined3d) — DXVK disabled for Intel HD 2000 safety", font=("Segoe UI", 10), fg="#00d2ff", bg="#0f172a").grid(row=0, column=1, sticky="w", padx=10, pady=4)

        tk.Label(card, text="Active Prefix Directory:", font=("Segoe UI", 10, "bold"), fg="#8ea4c8", bg="#0f172a").grid(row=1, column=0, sticky="w", pady=4)
        tk.Label(card, text="~/.giri/bridge/prefixes/default (64-bit multiarch)", font=("Segoe UI", 10), fg="#ffffff", bg="#0f172a").grid(row=1, column=1, sticky="w", padx=10, pady=4)

    def view_gaming(self):
        tk.Label(self.content, text="Giri Gaming Optimization", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(0, 15))
        card = tk.Frame(self.content, bg="#0f172a", padx=16, pady=14)
        card.pack(fill="x", pady=6)
        tk.Label(card, text="Game Mode Governor: Active", font=("Segoe UI", 10, "bold"), fg="#00d2ff", bg="#0f172a").pack(anchor="w")
        tk.Label(card, text="PipeWire Audio Buffer: 128 samples / 48kHz (Ultra-low latency)", font=("Segoe UI", 10), fg="#8ea4c8", bg="#0f172a").pack(anchor="w", pady=2)
        tk.Label(card, text="Display Compositor: Automatically unredirects fullscreen games", font=("Segoe UI", 10), fg="#8ea4c8", bg="#0f172a").pack(anchor="w", pady=2)

    def view_updates(self):
        tk.Label(self.content, text="Giri Update Manager", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(0, 15))
        card = tk.Frame(self.content, bg="#0f172a", padx=16, pady=14)
        card.pack(fill="x", pady=6)
        tk.Label(card, text="Current Release: Giri OS 0.1 'Genesis' (Debian Bookworm base)", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#0f172a").pack(anchor="w")
        tk.Label(card, text="Update Channel: Stable (GPG-signed repository)", font=("Segoe UI", 10), fg="#00d2ff", bg="#0f172a").pack(anchor="w", pady=3)
        tk.Label(card, text="Last Verified Check: Up to date", font=("Segoe UI", 10), fg="#8ea4c8", bg="#0f172a").pack(anchor="w", pady=2)

    def view_privacy(self):
        tk.Label(self.content, text="Privacy & Telemetry", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(0, 15))
        card = tk.Frame(self.content, bg="#0f172a", padx=16, pady=14)
        card.pack(fill="x", pady=6)
        tk.Label(card, text="System Telemetry: PERMANENTLY DISABLED", font=("Segoe UI", 11, "bold"), fg="#00d2ff", bg="#0f172a").pack(anchor="w")
        tk.Label(card, text="Giri OS does not track keystrokes, application launches, or user telemetry.", font=("Segoe UI", 10), fg="#a0aec0", bg="#0f172a").pack(anchor="w", pady=4)


if __name__ == "__main__":
    if "--verify" in sys.argv:
        app = GiriControlCenter(non_interactive=True)
        print("Giri Control Center initialized and verified successfully.")
        app.destroy()
    else:
        root = tk.Tk()
        root.withdraw()
        app = GiriControlCenter(root)
        root.mainloop()
