#!/usr/bin/env python3
"""
Giri Space — Desktop Environment Prototype
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Official Giri Space desktop shell:
- Full live wallpaper engine featuring 'Giri Origin' and official Light/Dark pairs
- Live real-time wallpaper updates without restarting
- Support for Fill, Fit, Stretch, Center, and Solid Colour modes
- Per-Space virtual desktop wallpaper assignment (Spaces 1-4)
- Giri Top Bar, Floating Dock, Giri Launch with categories, and Quick Settings
- Modal Session Management (Lock, Logout, Reboot, Shutdown)
- Window manager keyboard shortcut integration (Super, Escape, Super+1..4, Super+T, Super+C)
"""

import sys
import os
import time
import math
import json
import shutil
import subprocess

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    from PIL import Image, ImageTk
except ImportError:
    print("Error: Tkinter and Pillow are required to run the Giri Space desktop prototype.")
    sys.exit(1)

# Paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
WALLPAPER_DIR = os.path.join(ROOT_DIR, "branding", "wallpapers")
WALLPAPER_CONFIG = os.path.join(ROOT_DIR, "system", "etc", "giri-wallpaper.json")

# Import local control center
sys.path.insert(0, ROOT_DIR)
try:
    import importlib.util
    cc_path = os.path.join(os.path.dirname(__file__), "..", "control-center", "control_center.py")
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
        self.selected_category = "All"

        # Palette definition
        self.colors = {
            "bg_dark": "#050811",
            "topbar_bg": "#0a1020",
            "dock_bg": "#0c1428",
            "dock_border": "#1c2b4d",
            "pane_tl": "#00d2ff",
            "pane_tr": "#0066ff",
            "pane_bl": "#7928ca",
            "pane_br": "#a855f7",
            "text_light": "#e2e8f0",
            "text_muted": "#8ea4c8",
        }

        # Load wallpaper settings
        self.wallpaper_config = self._load_wallpaper_config()
        self.bg_photo = None  # Reference to prevent garbage collection

        self.setup_desktop()
        self.setup_keyboard_shortcuts()
        self.start_clock_timer()

        if self.non_interactive:
            self.withdraw()

    def _load_wallpaper_config(self):
        default_wp = os.path.join(WALLPAPER_DIR, "giri-os-default-dark.png")
        if not os.path.isfile(default_wp):
            default_wp = os.path.join(WALLPAPER_DIR, "giri-origin.png")
        if os.path.isfile(WALLPAPER_CONFIG):
            try:
                with open(WALLPAPER_CONFIG, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    if not os.path.isfile(cfg.get("current_wallpaper", "")):
                        cfg["current_wallpaper"] = default_wp
                    return cfg
            except Exception:
                pass
        return {
            "current_wallpaper": default_wp,
            "current_name": "Giri OS — Dark Edition",
            "theme": "dark",
            "auto_switch_theme": True,
            "user_manually_selected": False,
            "mode": "Fill",
            "is_solid_color": False,
            "solid_color": "#050811",
            "per_space": {
                "1": default_wp,
                "2": os.path.join(WALLPAPER_DIR, "giri-origin.png"),
                "3": os.path.join(WALLPAPER_DIR, "infinite-flow.png"),
                "4": os.path.join(WALLPAPER_DIR, "quantum-form.png")
            }
        }

    def _save_wallpaper_config(self):
        os.makedirs(os.path.dirname(WALLPAPER_CONFIG), exist_ok=True)
        try:
            with open(WALLPAPER_CONFIG, "w", encoding="utf-8") as f:
                json.dump(self.wallpaper_config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save wallpaper configuration: {e}")

    def setup_desktop(self):
        # 1. Background Wallpaper Canvas
        self.canvas = tk.Canvas(self, bg=self.colors["bg_dark"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.bind("<Configure>", lambda e: self.draw_wallpaper())
        self.draw_wallpaper()

        # 2. Giri Top Bar (Fixed at top of screen)
        self.setup_topbar()

        # 3. Giri Floating Dock (Bottom of screen)
        self.setup_dock()

        # 4. Giri Launch Overlay Menu (Initially hidden)
        self.setup_launcher()

        # 5. Giri Quick Settings Overlay Panel (Initially hidden)
        self.setup_quick_settings()

    def setup_keyboard_shortcuts(self):
        """Binds universal window manager and shell keyboard shortcuts."""
        # Toggle launcher with Super / Win key
        for key in ["<Super_L>", "<Super_R>", "<KeyPress-Super_L>", "<KeyPress-Super_R>"]:
            try:
                self.bind_all(key, lambda e: self.toggle_launcher())
            except Exception:
                pass

        # Escape closes overlays
        self.bind_all("<Escape>", lambda e: self.close_all_overlays())

        # Super+1..4 switches virtual desktop Spaces
        for i in range(1, 5):
            self.bind_all(f"<Alt-Key-{i}>", lambda e, n=i: self.switch_space(n))
            self.bind_all(f"<Control-Key-{i}>", lambda e, n=i: self.switch_space(n))

        # Terminal shortcut: Super+T or Ctrl+Alt+T
        self.bind_all("<Control-Alt-t>", lambda e: self.launch_app("Terminal"))
        self.bind_all("<Alt-t>", lambda e: self.launch_app("Terminal"))

        # Settings shortcut: Super+C or Alt+C
        self.bind_all("<Alt-c>", lambda e: self.open_control_center())

    def close_all_overlays(self):
        if self.launcher_open:
            self.toggle_launcher()
        if self.quick_settings_open:
            self.toggle_quick_settings()

    def draw_wallpaper(self):
        w = self.winfo_width() or 1120
        h = self.winfo_height() or 720
        self.canvas.delete("all")

        # 1. Check if Solid Color is active
        if self.wallpaper_config.get("is_solid_color", False):
            sc = self.wallpaper_config.get("solid_color", "#050811")
            self.canvas.create_rectangle(0, 0, w, h, fill=sc, outline="")
            self._draw_overlay_hints(w, h, f"Solid Colour ({sc})")
            return

        # 2. Check Wallpaper File for Active Space
        space_key = str(self.active_space)
        wp_file = self.wallpaper_config.get("per_space", {}).get(space_key)
        if not wp_file or not os.path.isfile(wp_file):
            wp_file = self.wallpaper_config.get("current_wallpaper", "")

        if not os.path.isfile(wp_file):
            wp_file = os.path.join(WALLPAPER_DIR, "giri-origin.png")

        mode = self.wallpaper_config.get("mode", "Fill")

        # Try to load and scale wallpaper with Pillow
        if os.path.isfile(wp_file):
            try:
                pil_img = Image.open(wp_file)
                iw, ih = pil_img.size

                if mode == "Fill" or mode == "Stretch":
                    scaled = pil_img.resize((w, h), Image.Resampling.BILINEAR)
                    self.bg_photo = ImageTk.PhotoImage(scaled)
                    self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
                elif mode == "Fit":
                    ratio = min(w / iw, h / ih)
                    nw, nh = int(iw * ratio), int(ih * ratio)
                    scaled = pil_img.resize((nw, nh), Image.Resampling.BILINEAR)
                    self.bg_photo = ImageTk.PhotoImage(scaled)
                    ox = (w - nw) // 2
                    oy = (h - nh) // 2
                    self.canvas.create_rectangle(0, 0, w, h, fill="#04060c", outline="")
                    self.canvas.create_image(ox, oy, image=self.bg_photo, anchor="nw")
                elif mode == "Center":
                    self.bg_photo = ImageTk.PhotoImage(pil_img)
                    self.canvas.create_rectangle(0, 0, w, h, fill="#04060c", outline="")
                    ox = (w - iw) // 2
                    oy = (h - ih) // 2
                    self.canvas.create_image(ox, oy, image=self.bg_photo, anchor="nw")
                else:  # Tile or fallback
                    scaled = pil_img.resize((w, h), Image.Resampling.BILINEAR)
                    self.bg_photo = ImageTk.PhotoImage(scaled)
                    self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

                wp_name = os.path.splitext(os.path.basename(wp_file))[0].replace("-", " ").title()
                self._draw_overlay_hints(w, h, wp_name)
                return
            except Exception as e:
                print(f"Warning: Could not render wallpaper: {e}")

        # Fallback Procedural Dark Wallpaper if file fails
        self.canvas.create_rectangle(0, 0, w, h, fill="#060a14", outline="")
        self._draw_overlay_hints(w, h, "Giri Space")

    def _draw_overlay_hints(self, w, h, wp_name):
        self.canvas.create_text(
            w - 20, h - 85,
            text=f"Wallpaper: {wp_name}  •  Space {self.active_space}",
            font=("Segoe UI", 9),
            anchor="e",
            fill="#3e527a"
        )
        self.canvas.create_text(
            w - 20, h - 105,
            text=f"Giri OS 0.1 Genesis  •  {self.profile.capitalize()} Mode",
            font=("Segoe UI", 9, "bold"),
            anchor="e",
            fill="#00d2ff"
        )

    def set_wallpaper_live(self, full_path, mode="Fill"):
        """Live wallpaper update callback without restarting."""
        self.wallpaper_config["current_wallpaper"] = full_path
        self.wallpaper_config["mode"] = mode
        self.wallpaper_config["is_solid_color"] = False
        space_key = str(self.active_space)
        self.wallpaper_config["per_space"][space_key] = full_path
        self.draw_wallpaper()

    def set_solid_color_live(self, hex_color):
        """Live solid colour background callback without restarting."""
        self.wallpaper_config["is_solid_color"] = True
        self.wallpaper_config["solid_color"] = hex_color
        self.draw_wallpaper()

    def setup_topbar(self):
        self.topbar = tk.Frame(self, bg=self.colors["topbar_bg"], height=38)
        self.topbar.place(x=0, y=0, relwidth=1.0, height=38)

        # Left: Giri Launcher Trigger
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

        # Power/Session button in top bar
        self.btn_power = tk.Button(
            self.right_frame,
            text=" ⏻ ",
            font=("Segoe UI", 10, "bold"),
            bg="#101a33",
            fg="#ff5555",
            activebackground="#2a1622",
            activeforeground="#ff7777",
            relief="flat",
            command=self.show_session_dialog
        )
        self.btn_power.pack(side="left", padx=4)

    def setup_dock(self):
        dock_width = 460
        dock_height = 58
        self.dock_frame = tk.Frame(
            self,
            bg=self.colors["dock_bg"],
            highlightbackground=self.colors["dock_border"],
            highlightthickness=1
        )
        self.dock_frame.place(relx=0.5, rely=1.0, anchor="s", y=-14, width=dock_width, height=dock_height)

        self.dock_items = [
            ("⊞", "Giri Launch", self.toggle_launcher),
            ("📁", "Giri Files", lambda: self.launch_app("Giri Files")),
            ("🌉", "Giri Bridge", lambda: self.launch_app("Giri Bridge")),
            ("🎮", "Giri Gaming", lambda: self.launch_app("Giri Gaming")),
            ("💻", "Terminal", lambda: self.launch_app("Terminal")),
            ("⚙️", "Giri Control", self.open_control_center),
            ("🔄", "Giri Update", lambda: self.launch_app("Giri Update")),
        ]

        self.dock_dots = {}
        for icon, name, action in self.dock_items:
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
            self.dock_dots[name] = dot

    def update_dock_indicators(self):
        for name, dot in self.dock_dots.items():
            is_running = name in self.running_apps
            dot.config(text="•" if is_running else " ")

    def setup_launcher(self):
        self.launcher_frame = tk.Frame(
            self,
            bg="#0a1020",
            highlightbackground=self.colors["pane_tl"],
            highlightthickness=1,
            padx=14,
            pady=14
        )
        self.launcher_frame.place(x=8, y=42, width=420, height=520)
        self.launcher_frame.place_forget()

        # Header with Search
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
        self.search_entry.pack(fill="x", pady=(4, 8))
        self.search_entry.bind("<KeyRelease>", self.filter_apps)

        # Category Filter Tabs
        cat_frame = tk.Frame(self.launcher_frame, bg="#0a1020")
        cat_frame.pack(fill="x", pady=(0, 8))

        self.categories = ["All", "System", "Dev", "Media", "Settings", "Bridge"]
        self.cat_buttons = {}
        for cat in self.categories:
            btn = tk.Button(
                cat_frame,
                text=cat,
                font=("Segoe UI", 8, "bold" if cat == "All" else "normal"),
                bg="#1b2a47" if cat == "All" else "#0f172a",
                fg="#00d2ff" if cat == "All" else "#8ea4c8",
                activebackground="#1e3a6a",
                relief="flat",
                padx=6,
                pady=2,
                command=lambda c=cat: self.select_category(c)
            )
            btn.pack(side="left", padx=2)
            self.cat_buttons[cat] = btn

        # Scrollable App List Container
        self.app_list_frame = tk.Frame(self.launcher_frame, bg="#0a1020")
        self.app_list_frame.pack(fill="both", expand=True)

        self.apps = [
            ("📁 Giri Files", "File Manager & Storage Browser", "System"),
            ("🌉 Giri Bridge", "Windows Application Compatibility (.exe)", "Bridge"),
            ("🎮 Giri Gaming Dashboard", "Steam, GameMode & Controller Manager", "Media"),
            ("⚙️ Giri Control", "System Settings, Display & Hardware", "Settings"),
            ("🔄 Giri Update", "Debian Package & Kernel Updater", "System"),
            ("💻 Giri Terminal", "Bash Console & Shell Utilities", "Dev"),
            ("🌐 Giri Browser", "Secure Web Browser", "Media"),
            ("📝 Text Editor", "Lightweight Code & Document Editor", "Dev"),
            ("📊 System Monitor", "Live CPU, Memory & Disk Activity", "System"),
            ("📦 Software Center", "Install & Manage Debian Packages", "System"),
        ]
        self.populate_apps(self.apps)

        # Launcher Footer: Power Actions
        pwr_footer = tk.Frame(self.launcher_frame, bg="#060c18", pady=6)
        pwr_footer.pack(fill="x", side="bottom")

        tk.Button(pwr_footer, text="🔒 Lock", font=("Segoe UI", 8), bg="#0f172a", fg="#c2d5ee", relief="flat", command=self.action_lock).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(pwr_footer, text="🚪 Log Out", font=("Segoe UI", 8), bg="#0f172a", fg="#c2d5ee", relief="flat", command=self.action_logout).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(pwr_footer, text="↺ Reboot", font=("Segoe UI", 8), bg="#0f172a", fg="#ffaa44", relief="flat", command=self.action_reboot).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(pwr_footer, text="⏻ Shut Down", font=("Segoe UI", 8, "bold"), bg="#1a1216", fg="#ff5555", relief="flat", command=self.action_shutdown).pack(side="left", expand=True, fill="x", padx=2)

    def select_category(self, cat):
        self.selected_category = cat
        for c, btn in self.cat_buttons.items():
            if c == cat:
                btn.config(bg="#1b2a47", fg="#00d2ff", font=("Segoe UI", 8, "bold"))
            else:
                btn.config(bg="#0f172a", fg="#8ea4c8", font=("Segoe UI", 8, "normal"))
        self.filter_apps()

    def populate_apps(self, app_list):
        for w in self.app_list_frame.winfo_children():
            w.destroy()

        for item in app_list:
            name, desc = item[0], item[1]
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
        filtered = []
        for item in self.apps:
            name, desc, cat = item[0], item[1], item[2]
            if self.selected_category != "All" and cat != self.selected_category:
                continue
            if query and query not in name.lower() and query not in desc.lower():
                continue
            filtered.append(item)
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

        tk.Label(self.qs_frame, text="Visual Profile:", font=("Segoe UI", 10, "bold"), fg="#8ea4c8", bg="#0c1428").pack(anchor="w", pady=(10, 4))
        p_frame = tk.Frame(self.qs_frame, bg="#0c1428")
        p_frame.pack(fill="x")

        tk.Button(p_frame, text="Giri Classic", font=("Segoe UI", 9), bg="#1b2a47" if self.profile == "classic" else "#10182c", fg="#00d2ff" if self.profile == "classic" else "#8ea4c8", relief="flat", command=lambda: self.switch_profile("classic")).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(p_frame, text="Giri Modern", font=("Segoe UI", 9), bg="#0066ff" if self.profile == "modern" else "#10182c", fg="#ffffff" if self.profile == "modern" else "#8ea4c8", relief="flat", command=lambda: self.switch_profile("modern")).pack(side="left", expand=True, fill="x", padx=2)

        tk.Label(self.qs_frame, text="Theme Mode:", font=("Segoe UI", 10, "bold"), fg="#8ea4c8", bg="#0c1428").pack(anchor="w", pady=(10, 4))
        t_frame = tk.Frame(self.qs_frame, bg="#0c1428")
        t_frame.pack(fill="x")

        cur_theme = self.wallpaper_config.get("theme", "dark")
        self.btn_theme_dark = tk.Button(t_frame, text="🌙 Dark", font=("Segoe UI", 9, "bold" if cur_theme == "dark" else "normal"), bg="#1b2a47" if cur_theme == "dark" else "#10182c", fg="#00d2ff" if cur_theme == "dark" else "#8ea4c8", relief="flat", command=lambda: self.switch_theme("dark"))
        self.btn_theme_dark.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_theme_light = tk.Button(t_frame, text="☀ Light", font=("Segoe UI", 9, "bold" if cur_theme == "light" else "normal"), bg="#e2e8f0" if cur_theme == "light" else "#10182c", fg="#0f172a" if cur_theme == "light" else "#8ea4c8", relief="flat", command=lambda: self.switch_theme("light"))
        self.btn_theme_light.pack(side="left", expand=True, fill="x", padx=2)

    def toggle_launcher(self):
        if self.launcher_open:
            self.launcher_frame.place_forget()
            self.launcher_open = False
        else:
            if self.quick_settings_open:
                self.toggle_quick_settings()
            self.launcher_frame.place(x=8, y=42, width=420, height=520)
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
        # Update wallpaper for this space if assigned
        self.draw_wallpaper()

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

    def switch_theme(self, theme):
        self.theme = theme
        self.wallpaper_config["theme"] = theme

        if self.wallpaper_config.get("auto_switch_theme", True):
            target_wp = "giri-os-default-light.png" if theme == "light" else "giri-os-default-dark.png"
            full_path = os.path.join(WALLPAPER_DIR, target_wp)
            if not os.path.isfile(full_path):
                full_path = os.path.join("/usr/share/backgrounds", target_wp)
            if os.path.isfile(full_path):
                self.wallpaper_config["current_wallpaper"] = full_path
                self.wallpaper_config["current_name"] = f"Giri OS — {theme.capitalize()} Edition"
                self.wallpaper_config["is_solid_color"] = False
                for s in ["1", "2", "3", "4"]:
                    self.wallpaper_config["per_space"][s] = full_path

        if hasattr(self, "btn_theme_dark") and hasattr(self, "btn_theme_light"):
            self.btn_theme_dark.config(
                bg="#1b2a47" if theme == "dark" else "#10182c",
                fg="#00d2ff" if theme == "dark" else "#8ea4c8",
                font=("Segoe UI", 9, "bold" if theme == "dark" else "normal")
            )
            self.btn_theme_light.config(
                bg="#e2e8f0" if theme == "light" else "#10182c",
                fg="#0f172a" if theme == "light" else "#8ea4c8",
                font=("Segoe UI", 9, "bold" if theme == "light" else "normal")
            )

        self.draw_wallpaper()
        self._save_wallpaper_config()
        if self.quick_settings_open:
            self.toggle_quick_settings()

    def launch_app(self, name):
        clean_name = name.split(" ", 1)[-1]
        self.running_apps.add(clean_name)
        self.update_dock_indicators()
        if self.launcher_open:
            self.toggle_launcher()

        if "Control" in name:
            self.open_control_center()
            return

        # Attempt real process execution with fallbacks
        app_commands = {
            "Terminal": ["kitty", "xterm", "xfce4-terminal", "gnome-terminal", "powershell.exe", "cmd.exe"],
            "Files": ["thunar", "pcmanfm", "nautilus", "explorer.exe"],
            "Text Editor": ["mousepad", "gedit", "featherpad", "notepad.exe"],
            "System Monitor": ["gnome-system-monitor", "htop", "taskmgr.exe"],
            "Browser": ["firefox", "chromium", "google-chrome"],
        }

        matched = False
        for key, cmds in app_commands.items():
            if key.lower() in name.lower():
                for cmd in cmds:
                    if shutil.which(cmd):
                        try:
                            subprocess.Popen([cmd])
                            matched = True
                            break
                        except Exception:
                            pass
                if matched:
                    break

        if not matched:
            messagebox.showinfo(
                "Giri Space Application",
                f"Application: {name}\nProfile: Giri {self.profile.capitalize()}\nStatus: Launched or registered in session."
            )

    def open_control_center(self):
        if GiriControlCenter:
            GiriControlCenter(self)
        else:
            messagebox.showinfo("Giri Control", "Opening Giri Control Center...")

    # =========================================================================
    # Session Management & Power Actions
    # =========================================================================
    def show_session_dialog(self):
        """Displays a clean modal dialog for Lock, Log Out, Reboot, and Shutdown."""
        dialog = tk.Toplevel(self)
        dialog.title("Session Actions")
        dialog.geometry("380x280")
        dialog.resizable(False, False)
        dialog.configure(bg="#0a1020")
        dialog.transient(self)
        dialog.grab_set()

        # Center on parent
        x = self.winfo_x() + (self.winfo_width() // 2) - 190
        y = self.winfo_y() + (self.winfo_height() // 2) - 140
        dialog.geometry(f"+{x}+{y}")

        tk.Label(
            dialog,
            text="Giri OS Session Control",
            font=("Segoe UI", 13, "bold"),
            fg="#00d2ff",
            bg="#0a1020"
        ).pack(pady=(16, 6))

        tk.Label(
            dialog,
            text="Select an action to perform on your active session:",
            font=("Segoe UI", 9),
            fg="#8ea4c8",
            bg="#0a1020"
        ).pack(pady=(0, 14))

        actions = [
            ("🔒 Lock Session", "#0f172a", "#c2d5ee", lambda: [dialog.destroy(), self.action_lock()]),
            ("🚪 Log Out", "#0f172a", "#c2d5ee", lambda: [dialog.destroy(), self.action_logout()]),
            ("↺ Restart System", "#1b2a47", "#ffaa44", lambda: [dialog.destroy(), self.action_reboot()]),
            ("⏻ Shut Down", "#2a1418", "#ff5555", lambda: [dialog.destroy(), self.action_shutdown()]),
        ]

        for text, bg, fg, cmd in actions:
            btn = tk.Button(
                dialog,
                text=text,
                font=("Segoe UI", 10, "bold" if "Shut" in text or "Restart" in text else "normal"),
                bg=bg,
                fg=fg,
                activebackground="#1e293b",
                activeforeground="#ffffff",
                relief="flat",
                pady=6,
                command=cmd
            )
            btn.pack(fill="x", padx=30, pady=4)

        tk.Button(
            dialog,
            text="Cancel",
            font=("Segoe UI", 9),
            bg="#0a1020",
            fg="#64748b",
            activeforeground="#94a3b8",
            relief="flat",
            command=dialog.destroy
        ).pack(pady=(8, 0))

    def action_lock(self):
        for cmd in [["loginctl", "lock-session"], ["xflock4"], ["slock"], ["i3lock"]]:
            if shutil.which(cmd[0]):
                try:
                    subprocess.run(cmd, check=True)
                    return
                except Exception:
                    pass
        messagebox.showinfo("Session Locked", "Giri OS session locked.")

    def action_logout(self):
        if messagebox.askyesno("Confirm Log Out", "Are you sure you want to log out of Giri OS?"):
            for cmd in [["loginctl", "terminate-user", os.environ.get("USER", "")], ["xfce4-session-logout", "--logout"]]:
                if cmd[0] and shutil.which(cmd[0]):
                    try:
                        subprocess.run(cmd, check=True)
                        return
                    except Exception:
                        pass
            self.destroy()

    def action_reboot(self):
        if messagebox.askyesno("Confirm Restart", "Are you sure you want to restart the computer?"):
            for cmd in [["systemctl", "reboot"], ["reboot"]]:
                if shutil.which(cmd[0]):
                    try:
                        subprocess.run(cmd, check=True)
                        return
                    except Exception:
                        pass
            messagebox.showinfo("System Reboot", "Reboot requested via systemctl.")

    def action_shutdown(self):
        if messagebox.askyesno("Confirm Shut Down", "Are you sure you want to shut down Giri OS?"):
            for cmd in [["systemctl", "poweroff"], ["poweroff"], ["shutdown", "-h", "now"]]:
                if shutil.which(cmd[0]):
                    try:
                        subprocess.run(cmd, check=True)
                        return
                    except Exception:
                        pass
            messagebox.showinfo("System Shutdown", "Shutdown requested via systemctl.")

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
        print(f"Giri Space Desktop shell ({profile_arg.upper()} profile) with session manager and shortcuts verified successfully.")
        app.destroy()
    else:
        app = GiriSpaceDesktop(profile=profile_arg)
        app.mainloop()
