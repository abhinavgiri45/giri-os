#!/usr/bin/env python3
"""
Giri OS Control Center (Giri Control)
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

System settings and configuration hub for Giri OS.
Manages Display, Wallpapers & Backgrounds, Themes, Hardware Profiles,
Giri Bridge compatibility, and Giri Update.
"""

import sys
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

# Project paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
WALLPAPER_DIR = os.path.join(ROOT_DIR, "branding", "wallpapers")
WALLPAPER_CONFIG = os.path.join(ROOT_DIR, "system", "etc", "giri-wallpaper.json")

# Import local hardware detector if available
sys.path.insert(0, ROOT_DIR)
try:
    import importlib.util
    det_path = os.path.join(ROOT_DIR, "hardware", "giri-hw", "detector.py")
    spec = importlib.util.spec_from_file_location("detector", det_path)
    det_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(det_mod)
    HardwareDetector = det_mod.HardwareDetector
except Exception:
    HardwareDetector = None


class GiriControlCenter(tk.Toplevel):
    def __init__(self, parent=None, non_interactive=False):
        self.parent = parent
        if parent:
            super().__init__(parent)
        else:
            self.root = tk.Tk()
            self._is_standalone = True
            super().__init__(self.root)
            self.root.withdraw()

        self.non_interactive = non_interactive
        self.title("Giri Control — System Settings")
        self.geometry("920x620")
        self.minsize(840, 560)
        self.configure(bg="#080c1a")

        # Load hardware profile
        if HardwareDetector:
            try:
                self.hw_profile = HardwareDetector().profile
            except Exception:
                self.hw_profile = self._default_hw_profile()
        else:
            self.hw_profile = self._default_hw_profile()

        # Load Wallpaper configuration & manifest
        self.wallpaper_config = self._load_wallpaper_config()
        self.wallpapers_manifest = self._load_wallpapers_manifest()
        self.thumb_cache = {}

        self.active_tab = "Desktop Wallpaper"
        self.setup_ui()

    def _default_hw_profile(self):
        return {
            "cpu": {"model": "Intel Core i5-2400 @ 3.10GHz", "cores_logical": 4},
            "ram": {"total_gb": 8.0},
            "gpu": {"model": "Intel HD Graphics 2000", "driver": "i915/crocus", "vulkan_supported": False},
            "storage": {"free_space_gb": 35.0},
            "tier": {"profile_name": "Giri Classic", "code": "classic"}
        }

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

    def _load_wallpapers_manifest(self):
        meta_file = os.path.join(WALLPAPER_DIR, "wallpaper-metadata.json")
        if os.path.isfile(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        manifest_file = os.path.join(WALLPAPER_DIR, "wallpapers.json")
        if os.path.isfile(manifest_file):
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return [
            {"id": "giri-os-default-dark", "name": "Giri OS — Dark Edition", "filename": "giri-os-default-dark.png", "category": "Official Default", "paired_theme": "Dark", "is_official_default": True},
            {"id": "giri-os-default-light", "name": "Giri OS — Light Edition", "filename": "giri-os-default-light.png", "category": "Official Default", "paired_theme": "Light", "is_official_default": True},
            {"id": "giri-origin", "name": "Giri Origin", "filename": "giri-origin.png", "category": "Signature Abstract Architecture", "paired_theme": "Dark / Modern", "is_official_default": True},
            {"id": "infinite-flow", "name": "Infinite Flow", "filename": "infinite-flow.png", "category": "Flowing Abstract", "paired_theme": "Dark / Modern"},
            {"id": "quantum-form", "name": "Quantum Form", "filename": "quantum-form.png", "category": "Geometric Architecture", "paired_theme": "Dark / Modern"},
            {"id": "beyond-horizon", "name": "Beyond Horizon", "filename": "beyond-horizon.png", "category": "Cosmic Horizon", "paired_theme": "Dark / Midnight"},
            {"id": "midnight-architecture", "name": "Midnight Architecture", "filename": "midnight-architecture.png", "category": "Minimalist Architecture", "paired_theme": "Dark / Classic"},
            {"id": "electric-geometry", "name": "Electric Geometry", "filename": "electric-geometry.png", "category": "Geometric Abstract", "paired_theme": "Dark / Modern"},
            {"id": "silent-universe", "name": "Silent Universe", "filename": "silent-universe.png", "category": "Minimalist Space", "paired_theme": "Dark / Midnight"},
            {"id": "violet-dimension", "name": "Violet Dimension", "filename": "violet-dimension.png", "category": "Cinematic 3D Abstract", "paired_theme": "Dark / Modern"},
            {"id": "aurora", "name": "Aurora", "filename": "aurora.png", "category": "Atmospheric Wave", "paired_theme": "Dark / Modern"},
            {"id": "pure-minimal", "name": "Pure Minimal", "filename": "pure-minimal.png", "category": "Ultra-Clean Minimalist", "paired_theme": "Dark / Classic"},
        ]

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
            text="System Configuration & Personalization",
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
        self.content = tk.Frame(body, bg="#080c1a", padx=20, pady=16)
        self.content.pack(side="left", fill="both", expand=True)

        # Sidebar Navigation Buttons
        nav_items = [
            ("Desktop Wallpaper", "🖼️", self.view_wallpapers),
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
                fg="#00d2ff" if name == "Desktop Wallpaper" else "#b0c4de",
                activebackground="#16223d",
                activeforeground="#00d2ff",
                relief="flat",
                padx=16,
                pady=10,
                command=lambda f=func, n=name: self.switch_tab(n, f)
            )
            btn.pack(fill="x")

        # Default View: Wallpaper settings
        self.view_wallpapers()

    def switch_tab(self, name, render_func):
        self.active_tab = name
        for w in self.content.winfo_children():
            w.destroy()
        render_func()

    # =========================================================================
    # 1. Desktop Wallpaper Settings
    # =========================================================================
    def view_wallpapers(self):
        # Section Header
        hdr_frame = tk.Frame(self.content, bg="#080c1a")
        hdr_frame.pack(fill="x", pady=(0, 10))

        tk.Label(hdr_frame, text="Desktop Wallpaper & Backgrounds", font=("Segoe UI", 16, "bold"), fg="#ffffff", bg="#080c1a").pack(side="left")

        btn_box = tk.Frame(hdr_frame, bg="#080c1a")
        btn_box.pack(side="right")

        tk.Button(
            btn_box,
            text="★ Official Dark",
            font=("Segoe UI", 9, "bold"),
            bg="#0f172a",
            fg="#00d2ff",
            activebackground="#1e293b",
            activeforeground="#ffffff",
            relief="flat",
            padx=8,
            pady=3,
            command=self.restore_official_dark
        ).pack(side="left", padx=3)

        tk.Button(
            btn_box,
            text="☀ Official Light",
            font=("Segoe UI", 9, "bold"),
            bg="#f1f5f9",
            fg="#0f172a",
            activebackground="#e2e8f0",
            activeforeground="#0f172a",
            relief="flat",
            padx=8,
            pady=3,
            command=self.restore_official_light
        ).pack(side="left", padx=3)

        tk.Button(
            btn_box,
            text="↺ Giri Origin",
            font=("Segoe UI", 9),
            bg="#16223d",
            fg="#c2d5ee",
            activebackground="#223359",
            activeforeground="#ffffff",
            relief="flat",
            padx=8,
            pady=3,
            command=self.restore_signature_origin
        ).pack(side="left", padx=3)

        # Theme & Auto-Switching Control Banner
        theme_banner = tk.Frame(self.content, bg="#0d1830", padx=14, pady=8, highlightbackground="#1e3a6a", highlightthickness=1)
        theme_banner.pack(fill="x", pady=(0, 10))

        tk.Label(theme_banner, text="System Theme Mode:", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#0d1830").pack(side="left", padx=(0, 10))

        self.theme_var = tk.StringVar(value=self.wallpaper_config.get("theme", "dark"))
        btn_dark = tk.Button(theme_banner, text="🌙 Dark Theme", font=("Segoe UI", 9, "bold" if self.theme_var.get() == "dark" else "normal"), bg="#0f172a" if self.theme_var.get() == "dark" else "#16223d", fg="#00d2ff" if self.theme_var.get() == "dark" else "#8ea4c8", relief="flat", padx=10, pady=2, command=lambda: self.switch_theme("dark"))
        btn_dark.pack(side="left", padx=3)

        btn_light = tk.Button(theme_banner, text="☀ Light Theme", font=("Segoe UI", 9, "bold" if self.theme_var.get() == "light" else "normal"), bg="#e2e8f0" if self.theme_var.get() == "light" else "#16223d", fg="#0f172a" if self.theme_var.get() == "light" else "#8ea4c8", relief="flat", padx=10, pady=2, command=lambda: self.switch_theme("light"))
        btn_light.pack(side="left", padx=3)

        self.auto_switch_var = tk.BooleanVar(value=self.wallpaper_config.get("auto_switch_theme", True))
        chk_auto = tk.Checkbutton(
            theme_banner,
            text="Automatically change wallpaper with theme (Official Light / Dark)",
            variable=self.auto_switch_var,
            font=("Segoe UI", 9),
            fg="#a0aec0",
            bg="#0d1830",
            activebackground="#0d1830",
            activeforeground="#ffffff",
            selectcolor="#0f172a",
            command=self.toggle_auto_switch
        )
        chk_auto.pack(side="right", padx=5)

        # Top Control Row: Current Status + Mode + Space Selector
        ctrl_card = tk.Frame(self.content, bg="#0f172a", padx=14, pady=10)
        ctrl_card.pack(fill="x", pady=(0, 10))

        # Current Active Wallpaper Info
        cur_name = self.wallpaper_config.get("current_name", "Giri Origin")
        self.lbl_cur_status = tk.Label(
            ctrl_card,
            text=f"Active Wallpaper: {cur_name}",
            font=("Segoe UI", 10, "bold"),
            fg="#00d2ff",
            bg="#0f172a"
        )
        self.lbl_cur_status.pack(side="left", padx=5)

        # Placement Mode Picker
        tk.Label(ctrl_card, text="Placement Mode:", font=("Segoe UI", 9, "bold"), fg="#8ea4c8", bg="#0f172a").pack(side="left", padx=(20, 5))
        self.mode_var = tk.StringVar(value=self.wallpaper_config.get("mode", "Fill"))
        modes = ["Fill", "Fit", "Stretch", "Center", "Tile"]
        cb_mode = ttk.Combobox(ctrl_card, textvariable=self.mode_var, values=modes, width=8, state="readonly")
        cb_mode.pack(side="left", padx=2)
        cb_mode.bind("<<ComboboxSelected>>", self.on_mode_change)

        # Virtual Desktop / Space Selector
        tk.Label(ctrl_card, text="Apply To:", font=("Segoe UI", 9, "bold"), fg="#8ea4c8", bg="#0f172a").pack(side="left", padx=(15, 5))
        self.space_target_var = tk.StringVar(value="All Spaces (Global)")
        space_targets = ["All Spaces (Global)", "Space 1 (Core)", "Space 2 (Dev)", "Space 3 (Game)", "Space 4 (Media)"]
        cb_space = ttk.Combobox(ctrl_card, textvariable=self.space_target_var, values=space_targets, width=17, state="readonly")
        cb_space.pack(side="left", padx=2)

        # Custom Wallpaper Button
        btn_custom = tk.Button(
            ctrl_card,
            text="📁 Browse Custom...",
            font=("Segoe UI", 9),
            bg="#0066ff",
            fg="#ffffff",
            activebackground="#0088ff",
            relief="flat",
            padx=10,
            pady=3,
            command=self.browse_custom_wallpaper
        )
        btn_custom.pack(side="right", padx=5)

        # Solid Colour Background Swatches Row
        solid_frame = tk.Frame(self.content, bg="#0c1428", padx=12, pady=6)
        solid_frame.pack(fill="x", pady=(0, 10))

        tk.Label(solid_frame, text="Solid Colours:", font=("Segoe UI", 9, "bold"), fg="#8ea4c8", bg="#0c1428").pack(side="left", padx=(0, 10))
        solids = [
            ("Midnight Black", "#050811"),
            ("Deep Navy", "#0A1128"),
            ("Dark Violet", "#140826"),
            ("Classic Gray", "#1E1E1E"),
            ("Pitch Black", "#000000"),
        ]
        for sname, scolor in solids:
            sbtn = tk.Button(
                solid_frame,
                text=sname,
                font=("Segoe UI", 8),
                bg=scolor,
                fg="#ffffff",
                relief="groove",
                padx=8,
                pady=2,
                command=lambda c=scolor: self.set_solid_color(c)
            )
            sbtn.pack(side="left", padx=4)

        # Wallpaper Gallery Grid Container (Scrollable)
        gallery_container = tk.Frame(self.content, bg="#080c1a")
        gallery_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(gallery_container, bg="#080c1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(gallery_container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#080c1a")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(xscrollcommand=None, yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate Wallpaper Cards in 2 columns
        for idx, wp in enumerate(self.wallpapers_manifest):
            row = idx // 2
            col = idx % 2

            card = tk.Frame(scroll_frame, bg="#0f172a", padx=10, pady=8, highlightbackground="#1e293b", highlightthickness=1)
            card.grid(row=row, column=col, padx=8, pady=6, sticky="nsew")
            scroll_frame.grid_columnconfigure(col, weight=1)

            # Try to load thumbnail
            thumb_path = os.path.join(WALLPAPER_DIR, "thumbnails", wp["filename"])
            photo = None
            if os.path.isfile(thumb_path):
                if thumb_path not in self.thumb_cache:
                    try:
                        pil_img = Image.open(thumb_path)
                        # Scale down slightly for grid
                        pil_img = pil_img.resize((240, 135), Image.Resampling.BILINEAR)
                        self.thumb_cache[thumb_path] = ImageTk.PhotoImage(pil_img)
                    except Exception:
                        pass
                photo = self.thumb_cache.get(thumb_path)

            if photo:
                lbl_img = tk.Label(card, image=photo, bg="#0f172a", cursor="hand2")
                lbl_img.image = photo
                lbl_img.pack(side="top", pady=(0, 4))
                lbl_img.bind("<Button-1>", lambda e, p=wp: self.select_wallpaper(p))

            # Info & Action
            info_frame = tk.Frame(card, bg="#0f172a")
            info_frame.pack(fill="x", side="top")

            name_text = f"★ {wp['name']}" if wp.get("is_default") else wp["name"]
            tk.Label(info_frame, text=name_text, font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#0f172a").pack(side="left")
            tk.Label(info_frame, text=f"({wp.get('paired_theme', '')})", font=("Segoe UI", 8), fg="#8ea4c8", bg="#0f172a").pack(side="right")

            btn_set = tk.Button(
                card,
                text="Apply Wallpaper",
                font=("Segoe UI", 9),
                bg="#1b2a47",
                fg="#00d2ff",
                activebackground="#0066ff",
                activeforeground="#ffffff",
                relief="flat",
                pady=3,
                command=lambda p=wp: self.select_wallpaper(p)
            )
            btn_set.pack(fill="x", pady=(4, 0))

    def select_wallpaper(self, wp_data):
        filename = wp_data["filename"]
        full_path = os.path.join(WALLPAPER_DIR, filename)
        name = wp_data["name"]

        target_space = self.space_target_var.get()

        if "All Spaces" in target_space:
            self.wallpaper_config["current_wallpaper"] = full_path
            self.wallpaper_config["current_name"] = name
            self.wallpaper_config["is_solid_color"] = False
            for s in ["1", "2", "3", "4"]:
                self.wallpaper_config["per_space"][s] = full_path
        else:
            # Per space assignment
            space_num = target_space.split()[1]
            self.wallpaper_config["per_space"][space_num] = full_path
            self.wallpaper_config["current_wallpaper"] = full_path
            self.wallpaper_config["current_name"] = f"{name} (Space {space_num})"

        self.wallpaper_config["user_manually_selected"] = True
        self._save_wallpaper_config()
        self.lbl_cur_status.config(text=f"Active Wallpaper: {name}")

        # Update parent desktop immediately without restart!
        if self.parent and hasattr(self.parent, "set_wallpaper_live"):
            self.parent.set_wallpaper_live(full_path, mode=self.mode_var.get())

        messagebox.showinfo("Wallpaper Applied", f"Successfully applied '{name}' without restarting.")

    def restore_default_wallpaper(self):
        theme = self.wallpaper_config.get("theme", "dark")
        if theme == "light":
            self.restore_official_light()
        else:
            self.restore_official_dark()

    def restore_official_dark(self):
        wp = os.path.join(WALLPAPER_DIR, "giri-os-default-dark.png")
        if not os.path.isfile(wp):
            wp = os.path.join(WALLPAPER_DIR, "giri-origin.png")
        self._apply_global_wallpaper(wp, "Giri OS — Dark Edition")
        self.wallpaper_config["user_manually_selected"] = False
        self._save_wallpaper_config()
        messagebox.showinfo("Official Default Applied", "Giri OS — Dark Edition default wallpaper applied successfully.")

    def restore_official_light(self):
        wp = os.path.join(WALLPAPER_DIR, "giri-os-default-light.png")
        if not os.path.isfile(wp):
            wp = os.path.join(WALLPAPER_DIR, "giri-origin.png")
        self._apply_global_wallpaper(wp, "Giri OS — Light Edition")
        self.wallpaper_config["user_manually_selected"] = False
        self._save_wallpaper_config()
        messagebox.showinfo("Official Default Applied", "Giri OS — Light Edition default wallpaper applied successfully.")

    def restore_signature_origin(self):
        wp = os.path.join(WALLPAPER_DIR, "giri-origin.png")
        self._apply_global_wallpaper(wp, "Giri Origin")
        self.wallpaper_config["user_manually_selected"] = True
        self._save_wallpaper_config()
        messagebox.showinfo("Signature Wallpaper Applied", "Giri Origin signature wallpaper applied successfully.")

    def _apply_global_wallpaper(self, file_path, name):
        self.wallpaper_config["current_wallpaper"] = file_path
        self.wallpaper_config["current_name"] = name
        self.wallpaper_config["is_solid_color"] = False
        self.wallpaper_config["mode"] = "Fill"
        self.mode_var.set("Fill")
        for s in ["1", "2", "3", "4"]:
            self.wallpaper_config["per_space"][s] = file_path
        self._save_wallpaper_config()
        self.lbl_cur_status.config(text=f"Active Wallpaper: {name}")
        if self.parent and hasattr(self.parent, "set_wallpaper_live"):
            self.parent.set_wallpaper_live(file_path, mode="Fill")

    def toggle_auto_switch(self):
        enabled = self.auto_switch_var.get()
        self.wallpaper_config["auto_switch_theme"] = enabled
        if enabled:
            # Re-apply official default for current theme
            theme = self.wallpaper_config.get("theme", "dark")
            if theme == "light":
                self.restore_official_light()
            else:
                self.restore_official_dark()
        else:
            self._save_wallpaper_config()

    def switch_theme(self, theme):
        self.theme_var.set(theme)
        self.wallpaper_config["theme"] = theme
        if self.wallpaper_config.get("auto_switch_theme", True):
            if theme == "light":
                wp = os.path.join(WALLPAPER_DIR, "giri-os-default-light.png")
                name = "Giri OS — Light Edition"
            else:
                wp = os.path.join(WALLPAPER_DIR, "giri-os-default-dark.png")
                name = "Giri OS — Dark Edition"
            if os.path.isfile(wp):
                self._apply_global_wallpaper(wp, name)
                self.wallpaper_config["user_manually_selected"] = False
        else:
            self._save_wallpaper_config()

        # Update parent desktop theme live
        if self.parent and hasattr(self.parent, "switch_theme"):
            self.parent.switch_theme(theme)

    def set_solid_color(self, hex_color):
        self.wallpaper_config["is_solid_color"] = True
        self.wallpaper_config["solid_color"] = hex_color
        self.wallpaper_config["current_name"] = f"Solid Colour ({hex_color})"
        self._save_wallpaper_config()
        self.lbl_cur_status.config(text=f"Active Wallpaper: Solid Colour ({hex_color})")

        if self.parent and hasattr(self.parent, "set_solid_color_live"):
            self.parent.set_solid_color_live(hex_color)

        messagebox.showinfo("Solid Colour Applied", f"Desktop background updated to solid {hex_color}.")

    def browse_custom_wallpaper(self):
        f = filedialog.askopenfilename(
            title="Select Custom Desktop Wallpaper",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"), ("All Files", "*.*")]
        )
        if f and os.path.isfile(f):
            bname = os.path.basename(f)
            self.wallpaper_config["current_wallpaper"] = f
            self.wallpaper_config["current_name"] = bname
            self.wallpaper_config["is_solid_color"] = False
            self._save_wallpaper_config()
            self.lbl_cur_status.config(text=f"Active Wallpaper: {bname}")

            if self.parent and hasattr(self.parent, "set_wallpaper_live"):
                self.parent.set_wallpaper_live(f, mode=self.mode_var.get())

            messagebox.showinfo("Custom Wallpaper", f"Applied custom image '{bname}'.")

    def on_mode_change(self, event=None):
        mode = self.mode_var.get()
        self.wallpaper_config["mode"] = mode
        self._save_wallpaper_config()
        if self.parent and hasattr(self.parent, "set_wallpaper_live"):
            cur_wp = self.wallpaper_config.get("current_wallpaper", "")
            if os.path.isfile(cur_wp):
                self.parent.set_wallpaper_live(cur_wp, mode=mode)

    # =========================================================================
    # 2. Other Giri Control Tabs
    # =========================================================================
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
        card = tk.Frame(self.content, bg="#0f172a", padx=16, pady=14)
        card.pack(fill="x", pady=6)
        tk.Label(card, text="Wine Translation Backend:", font=("Segoe UI", 10, "bold"), fg="#8ea4c8", bg="#0f172a").grid(row=0, column=0, sticky="w", pady=4)
        tk.Label(card, text="Mesa OpenGL (wined3d) — DXVK bypassed for Intel HD 2000 safety", font=("Segoe UI", 10), fg="#00d2ff", bg="#0f172a").grid(row=0, column=1, sticky="w", padx=10, pady=4)

    def view_gaming(self):
        tk.Label(self.content, text="Giri Gaming Optimization", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(0, 15))
        card = tk.Frame(self.content, bg="#0f172a", padx=16, pady=14)
        card.pack(fill="x", pady=6)
        tk.Label(card, text="Game Mode Governor: Active", font=("Segoe UI", 10, "bold"), fg="#00d2ff", bg="#0f172a").pack(anchor="w")
        tk.Label(card, text="PipeWire Audio Buffer: 128 samples / 48kHz (Ultra-low latency)", font=("Segoe UI", 10), fg="#8ea4c8", bg="#0f172a").pack(anchor="w", pady=2)

    def view_updates(self):
        tk.Label(self.content, text="Giri Update Manager", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(0, 15))
        card = tk.Frame(self.content, bg="#0f172a", padx=16, pady=14)
        card.pack(fill="x", pady=6)
        tk.Label(card, text="Current Release: Giri OS 0.1 'Genesis' (Debian Bookworm base)", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#0f172a").pack(anchor="w")
        tk.Label(card, text="Update Channel: Stable (GPG-signed repository)", font=("Segoe UI", 10), fg="#00d2ff", bg="#0f172a").pack(anchor="w", pady=3)

    def view_privacy(self):
        tk.Label(self.content, text="Privacy & Telemetry", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(0, 15))
        card = tk.Frame(self.content, bg="#0f172a", padx=16, pady=14)
        card.pack(fill="x", pady=6)
        tk.Label(card, text="System Telemetry: PERMANENTLY DISABLED", font=("Segoe UI", 11, "bold"), fg="#00d2ff", bg="#0f172a").pack(anchor="w")
        tk.Label(card, text="Giri OS does not track keystrokes, application launches, or user telemetry.", font=("Segoe UI", 10), fg="#a0aec0", bg="#0f172a").pack(anchor="w", pady=4)


if __name__ == "__main__":
    if "--verify" in sys.argv:
        app = GiriControlCenter(non_interactive=True)
        print("Giri Control Center (with Wallpaper management) verified successfully.")
        app.destroy()
    else:
        root = tk.Tk()
        root.withdraw()
        app = GiriControlCenter(root)
        root.mainloop()
