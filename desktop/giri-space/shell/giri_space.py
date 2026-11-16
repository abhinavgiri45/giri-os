#!/usr/bin/env python3
"""
Giri Space — Desktop Environment Prototype
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Official Giri Space desktop shell:
- Four-pane geometric window brand emblem
- Giri Top Bar (Clock, Workspaces, Quick Status, Quick Settings)
- Giri Dock (Floating application dock with active indicators)
- Giri Launch (Categorized high-speed application search launcher)
- Giri Spaces (Virtual workspaces switcher)
- Giri Profile integration (Classic vs Modern visual rendering modes)
"""

import sys
import os
import time
import math
import subprocess

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("Error: Tkinter is required to run the Giri Space desktop prototype.")
    sys.exit(1)

# Import local control center
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
try:
    from desktop.giri_space.control_center.control_center import GiriControlCenter
except Exception:
    try:
        import importlib.util
        cc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "control-center", "control_center.py"))
        spec = importlib.util.spec_from_file_location("control_center", cc_path)
        cc_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cc_mod)
        GiriControlCenter = cc_mod.GiriControlCenter
    except Exception:
        GiriControlCenter = None


class GiriSpaceDesktop(tk.Tk):
    def __init__(self, profile="classic", non_interactive=False):
        super().__init__()
        self.profile = profile.lower()
        self.non_interactive = non_interactive

        self.title("Giri Space — Desktop Environment")
        self.geometry("1120x720")
        self.minsize(960, 600)
        self.configure(bg="#050811")

        # System state
        self.active_space = 1
        self.launcher_open = False
        self.quick_settings_open = False
        self.running_apps = {"Giri Files", "Giri Control"}

        # Official Color Palette
        self.colors = {
            "bg_dark": "#060a14",
            "topbar_bg": "#0a1020",
            "dock_bg": "#0c1428",
            "dock_border": "#1c2b4d",
            "pane_tl": "#00d2ff",   # Electric Cyan-Blue
            "pane_tr": "#0066ff",   # Vivid Electric Blue
            "pane_bl": "#7928ca",   # Electric Violet
            "pane_br": "#a855f7",   # Radiant Violet-Magenta
            "text_light": "#e2e8f0",
            "text_muted": "#8ea4c8",
        }

        self.setup_desktop()
        self.start_clock_timer()

        if self.non_interactive:
            self.withdraw()

    def setup_desktop(self):
        # 1. Background Wallpaper Canvas
        self.canvas = tk.Canvas(self, bg=self.colors["bg_dark"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_wallpaper()

        # 2. Giri Top Bar (Fixed at top of screen)
        self.setup_topbar()

        # 3. Giri Floating Dock (Bottom of screen)
        self.setup_dock()

        # 4. Giri Launch Overlay Menu (Initially hidden)
        self.setup_launcher()

        # 5. Giri Quick Settings Overlay Panel (Initially hidden)
        self.setup_quick_settings()

    def draw_wallpaper(self):
        self.canvas.delete("all")
        w = self.winfo_width() or 1120
        h = self.winfo_height() or 720

        cx, cy = w // 2, h // 2

        # Draw Official Four-Pane Geometric Window Symbol (Center Watermark)
        # Symmetrical 2x2 formation: 120x120 total, 10px spacing
        pane_w = 54
        gap = 12
        x0 = cx - (pane_w * 2 + gap) // 2
        y0 = cy - 70
        x1 = x0 + pane_w + gap
        y1 = y0 + pane_w + gap

        # 4 Geometric Panes (Flat vector design)
        self.canvas.create_rectangle(x0, y0, x0 + pane_w, y0 + pane_w, fill=self.colors["pane_tl"], outline="")
        self.canvas.create_rectangle(x1, y0, x1 + pane_w, y0 + pane_w, fill=self.colors["pane_tr"], outline="")
        self.canvas.create_rectangle(x0, y1, x0 + pane_w, y1 + pane_w, fill=self.colors["pane_bl"], outline="")
        self.canvas.create_rectangle(x1, y1, x1 + pane_w, y1 + pane_w, fill=self.colors["pane_br"], outline="")

        # Wordmark: GIRI OS
        self.canvas.create_text(
            cx, cy + 70,
            text="GIRI OS",
            font=("Segoe UI", 32, "bold"),
            fill="#ffffff"
        )
        self.canvas.create_text(
            cx, cy + 106,
            text="ONE SYSTEM. INFINITE POSSIBILITIES.",
            font=("Segoe UI", 10, "bold"),
            fill="#64748b"
        )

        # Profile indicator on wallpaper
        self.canvas.create_text(
            w - 18, h - 90,
            text=f"Giri OS 0.1 Genesis  •  {self.profile.capitalize()} Mode",
            font=("Segoe UI", 9),
            anchor="e",
            fill="#2c3e66"
        )

    def setup_topbar(self):
        self.topbar = tk.Frame(self, bg=self.colors["topbar_bg"], height=38)
        self.topbar.place(x=0, y=0, relwidth=1.0, height=38)

        # Left: Giri Launcher Trigger with four-pane window glyph
        self.btn_logo = tk.Button(
            self.topbar,
            text=" ⊞ GIRI ",
            font=("Segoe UI", 10, "bold"),
            bg="#101a33",
            fg=self.colors["pane_tl"],
            activebackground="#162447",
            activeforeground="#ffffff",
            relief="flat",
            command=self.toggle_launcher
        )
        self.btn_logo.pack(side="left", padx=8, pady=4)

        # Spaces (Virtual Desktops) Selector
        self.spaces_frame = tk.Frame(self.topbar, bg=self.colors["topbar_bg"])
        self.spaces_frame.pack(side="left", padx=10)

        self.space_btns = []
        spaces = [("1 Core", 1), ("2 Dev", 2), ("3 Game", 3), ("4 Media", 4)]
        for label, num in spaces:
            btn = tk.Button(
                self.spaces_frame,
                text=label,
                font=("Segoe UI", 9),
                bg="#16223d" if num == self.active_space else self.colors["topbar_bg"],
                fg="#ffffff" if num == self.active_space else "#8ea4c8",
                activebackground="#1c2c4f",
                relief="flat",
                padx=8,
                pady=2,
                command=lambda n=num: self.switch_space(n)
            )
            btn.pack(side="left", padx=2)
            self.space_btns.append((num, btn))

        # Center: Clock & Date
        self.lbl_clock = tk.Label(
            self.topbar,
            text="Loading time...",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["text_light"],
            bg=self.colors["topbar_bg"]
        )
        self.lbl_clock.pack(side="left", expand=True)

        # Right Indicators
        self.right_frame = tk.Frame(self.topbar, bg=self.colors["topbar_bg"])
        self.right_frame.pack(side="right", padx=12)

        tier_text = "CLASSIC" if self.profile == "classic" else "MODERN"
        self.lbl_tier = tk.Label(
            self.right_frame,
            text=f" {tier_text} ",
            font=("Segoe UI", 8, "bold"),
            bg="#0066ff" if self.profile == "modern" else "#1b2a47",
            fg="#ffffff" if self.profile == "modern" else "#00d2ff"
        )
        self.lbl_tier.pack(side="left", padx=6)

        self.lbl_cpu = tk.Label(self.right_frame, text="CPU: 5%", font=("Segoe UI", 9), fg="#8ea4c8", bg=self.colors["topbar_bg"])
        self.lbl_cpu.pack(side="left", padx=6)

        self.lbl_ram = tk.Label(self.right_frame, text="RAM: 410 MB", font=("Segoe UI", 9), fg="#8ea4c8", bg=self.colors["topbar_bg"])
        self.lbl_ram.pack(side="left", padx=6)

        self.btn_qs = tk.Button(
            self.right_frame,
            text=" ⚙️ ",
            font=("Segoe UI", 10),
            bg="#101a33",
            fg=self.colors["pane_tl"],
            activebackground="#1a274c",
            relief="flat",
            command=self.toggle_quick_settings
        )
        self.btn_qs.pack(side="left", padx=4)

    def setup_dock(self):
        dock_width = 440
        dock_height = 58
        self.dock_frame = tk.Frame(
            self,
            bg=self.colors["dock_bg"],
            highlightbackground=self.colors["dock_border"],
            highlightthickness=1
        )
        self.dock_frame.place(relx=0.5, rely=1.0, anchor="s", y=-14, width=dock_width, height=dock_height)

        dock_items = [
            ("⊞", "Giri Launch", self.toggle_launcher),
            ("📁", "Giri Files", lambda: self.launch_app("Giri Files")),
            ("🌉", "Giri Bridge", lambda: self.launch_app("Giri Bridge")),
            ("🎮", "Giri Gaming", lambda: self.launch_app("Giri Gaming")),
            ("💻", "Terminal", lambda: self.launch_app("Terminal")),
            ("⚙️", "Giri Control", self.open_control_center),
            ("🔄", "Giri Update", lambda: self.launch_app("Giri Update")),
        ]

        for icon, name, action in dock_items:
            f = tk.Frame(self.dock_frame, bg=self.colors["dock_bg"])
            f.pack(side="left", expand=True, fill="both", padx=3, pady=4)

            btn = tk.Button(
                f,
                text=icon,
                font=("Segoe UI", 14 if icon == "⊞" else 15),
                bg=self.colors["dock_bg"],
                fg=self.colors["pane_tl"] if icon == "⊞" else "#ffffff",
                activebackground="#16223d",
                activeforeground=self.colors["pane_tl"],
                relief="flat",
                command=action
            )
            btn.pack(side="top")

            is_running = name in self.running_apps
            dot = tk.Label(
                f,
                text="•" if is_running else " ",
                font=("Segoe UI", 8),
                fg=self.colors["pane_tl"],
                bg=self.colors["dock_bg"]
            )
            dot.pack(side="bottom")

    def setup_launcher(self):
        self.launcher_frame = tk.Frame(
            self,
            bg="#0a1020",
            highlightbackground=self.colors["pane_tl"],
            highlightthickness=1,
            padx=16,
            pady=16
        )
        self.launcher_frame.place(x=8, y=42, width=380, height=480)
        self.launcher_frame.place_forget()

        lbl_s = tk.Label(self.launcher_frame, text="Search Giri OS...", font=("Segoe UI", 10, "bold"), fg=self.colors["pane_tl"], bg="#0a1020")
        lbl_s.pack(anchor="w")

        self.search_entry = tk.Entry(
            self.launcher_frame,
            font=("Segoe UI", 11),
            bg="#10182c",
            fg="#ffffff",
            insertbackground="#00d2ff",
            relief="flat"
        )
        self.search_entry.pack(fill="x", pady=(4, 12))
        self.search_entry.bind("<KeyRelease>", self.filter_apps)

        self.app_list_frame = tk.Frame(self.launcher_frame, bg="#0a1020")
        self.app_list_frame.pack(fill="both", expand=True)

        self.apps = [
            ("📁 Giri Files", "File Manager & Storage Browser"),
            ("🌉 Giri Bridge", "Windows Application Compatibility (.exe)"),
            ("🎮 Giri Gaming Dashboard", "Steam, GameMode & Controller Manager"),
            ("⚙️ Giri Control", "System Settings, Display & Hardware"),
            ("🔄 Giri Update", "Cryptographic Package & Kernel Updater"),
            ("💻 Giri Terminal", "Bash Console & Shell Utilities"),
            ("🌐 Giri Browser", "Secure Web Browser"),
            ("📝 Text Editor", "Lightweight Code & Document Editor"),
            ("📊 System Monitor", "Live CPU, Memory & Disk Activity"),
        ]
        self.populate_apps(self.apps)

    def populate_apps(self, app_list):
        for w in self.app_list_frame.winfo_children():
            w.destroy()

        for name, desc in app_list:
            btn = tk.Button(
                self.app_list_frame,
                text=f"{name}\n   {desc}",
                font=("Segoe UI", 9),
                justify="left",
                anchor="w",
                bg="#0f172a",
                fg="#c2d5ee",
                activebackground="#162447",
                activeforeground="#00d2ff",
                relief="flat",
                padx=8,
                pady=4,
                command=lambda n=name: self.launch_app(n)
            )
            btn.pack(fill="x", pady=2)

    def filter_apps(self, event=None):
        query = self.search_entry.get().lower().strip()
        filtered = [item for item in self.apps if query in item[0].lower() or query in item[1].lower()]
        self.populate_apps(filtered)

    def setup_quick_settings(self):
        self.qs_frame = tk.Frame(
            self,
            bg="#0c1428",
            highlightbackground="#223359",
            highlightthickness=1,
            padx=16,
            pady=16
        )
        self.qs_frame.place(relx=1.0, x=-340, y=42, width=320, height=360)
        self.qs_frame.place_forget()

        tk.Label(self.qs_frame, text="Quick Settings", font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#0c1428").pack(anchor="w", pady=(0, 10))

        toggles = [
            ("📶 Wi-Fi: Connected", True),
            ("🎮 Game Mode: Ready", True),
            ("🌙 Night Light", False),
            ("⚡ High Performance", False),
        ]
        grid_f = tk.Frame(self.qs_frame, bg="#0c1428")
        grid_f.pack(fill="x", pady=4)

        for i, (text, active) in enumerate(toggles):
            btn = tk.Button(
                grid_f,
                text=text,
                font=("Segoe UI", 9, "bold" if active else "normal"),
                bg="#0066ff" if active else "#16223d",
                fg="#ffffff" if active else "#8ea4c8",
                activebackground="#0088ff",
                relief="flat",
                padx=8,
                pady=8
            )
            btn.grid(row=i//2, column=i%2, sticky="ew", padx=4, pady=4)
        grid_f.grid_columnconfigure(0, weight=1)
        grid_f.grid_columnconfigure(1, weight=1)

        tk.Label(self.qs_frame, text="Visual Profile:", font=("Segoe UI", 10, "bold"), fg="#8ea4c8", bg="#0c1428").pack(anchor="w", pady=(12, 4))
        p_frame = tk.Frame(self.qs_frame, bg="#0c1428")
        p_frame.pack(fill="x")

        tk.Button(p_frame, text="Giri Classic", font=("Segoe UI", 9), bg="#1b2a47" if self.profile == "classic" else "#10182c", fg="#00d2ff" if self.profile == "classic" else "#8ea4c8", relief="flat", command=lambda: self.switch_profile("classic")).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(p_frame, text="Giri Modern", font=("Segoe UI", 9), bg="#0066ff" if self.profile == "modern" else "#10182c", fg="#ffffff" if self.profile == "modern" else "#8ea4c8", relief="flat", command=lambda: self.switch_profile("modern")).pack(side="left", expand=True, fill="x", padx=2)

    def toggle_launcher(self):
        if self.launcher_open:
            self.launcher_frame.place_forget()
            self.launcher_open = False
        else:
            if self.quick_settings_open:
                self.toggle_quick_settings()
            self.launcher_frame.place(x=8, y=42, width=380, height=480)
            self.launcher_frame.lift()
            self.search_entry.focus_set()
            self.launcher_open = True

    def toggle_quick_settings(self):
        if self.quick_settings_open:
            self.qs_frame.place_forget()
            self.quick_settings_open = False
        else:
            if self.launcher_open:
                self.toggle_launcher()
            self.qs_frame.place(relx=1.0, x=-340, y=42, width=320, height=360)
            self.qs_frame.lift()
            self.quick_settings_open = True

    def switch_space(self, num):
        self.active_space = num
        for n, btn in self.space_btns:
            if n == num:
                btn.config(bg="#16223d", fg="#ffffff")
            else:
                btn.config(bg=self.colors["topbar_bg"], fg="#8ea4c8")

    def switch_profile(self, profile):
        self.profile = profile
        tier_text = "CLASSIC" if self.profile == "classic" else "MODERN"
        self.lbl_tier.config(
            text=f" {tier_text} ",
            bg="#0066ff" if self.profile == "modern" else "#1b2a47",
            fg="#ffffff" if self.profile == "modern" else "#00d2ff"
        )
        self.draw_wallpaper()
        if self.quick_settings_open:
            self.toggle_quick_settings()

    def launch_app(self, name):
        clean_name = name.split(" ", 1)[-1]
        self.running_apps.add(clean_name)
        if self.launcher_open:
            self.toggle_launcher()
        if "Control" in name:
            self.open_control_center()
        else:
            messagebox.showinfo("Giri Space Application", f"Launching: {name}\nRunning in Giri {self.profile.capitalize()} environment.")

    def open_control_center(self):
        if GiriControlCenter:
            GiriControlCenter(self)
        else:
            messagebox.showinfo("Giri Control", "Opening Giri Control Center...")

    def start_clock_timer(self):
        def update():
            now_str = time.strftime("%a %b %d  •  %H:%M:%S")
            self.lbl_clock.config(text=now_str)
            self.after(1000, update)
        update()


if __name__ == "__main__":
    profile_arg = "classic"
    if "--profile" in sys.argv:
        idx = sys.argv.index("--profile")
        if idx + 1 < len(sys.argv):
            profile_arg = sys.argv[idx + 1]

    if "--verify" in sys.argv:
        app = GiriSpaceDesktop(profile=profile_arg, non_interactive=True)
        print(f"Giri Space Desktop shell ({profile_arg.upper()} profile) verified successfully.")
        app.destroy()
    else:
        app = GiriSpaceDesktop(profile=profile_arg)
        app.mainloop()
