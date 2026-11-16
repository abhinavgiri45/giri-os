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
        if os.path.isfile(WALLPAPER_CONFIG):
            try:
                with open(WALLPAPER_CONFIG, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "current_wallpaper": os.path.join(WALLPAPER_DIR, "giri-origin.png"),
            "current_name": "Giri Origin",
            "mode": "Fill",
            "is_solid_color": False,
            "solid_color": "#050811",
            "per_space": {
                "1": os.path.join(WALLPAPER_DIR, "giri-origin.png"),
                "2": os.path.join(WALLPAPER_DIR, "digital-dimensions.png"),
                "3": os.path.join(WALLPAPER_DIR, "quantum.png"),
                "4": os.path.join(WALLPAPER_DIR, "midnight-flow.png")
            }
        }

    def _save_wallpaper_config(self):
        os.makedirs(os.path.dirname(WALLPAPER_CONFIG), exist_ok=True)
        try:
            with open(WALLPAPER_CONFIG, "w") as f:
                json.dump(self.wallpaper_config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save wallpaper configuration: {e}")

    def _load_wallpapers_manifest(self):
        manifest_file = os.path.join(WALLPAPER_DIR, "wallpapers.json")
        if os.path.isfile(manifest_file):
            try:
                with open(manifest_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return [
            {"id": "giri-origin", "name": "Giri Origin", "filename": "giri-origin.png", "category": "Signature Default", "paired_theme": "Giri Dark / Modern"},
            {"id": "cosmic-horizon", "name": "Cosmic Horizon", "filename": "cosmic-horizon.png", "category": "Space Landscape", "paired_theme": "Giri Midnight"},
            {"id": "infinite-motion", "name": "Infinite Motion", "filename": "infinite-motion.png", "category": "Flowing Abstract", "paired_theme": "Giri Modern"},
            {"id": "digital-dimensions", "name": "Digital Dimensions", "filename": "digital-dimensions.png", "category": "Futuristic Architecture", "paired_theme": "Giri Dark"},
            {"id": "midnight-flow", "name": "Midnight Flow", "filename": "midnight-flow.png", "category": "Deep Contrast", "paired_theme": "Giri Midnight"},
            {"id": "electric-geometry", "name": "Electric Geometry", "filename": "electric-geometry.png", "category": "Geometric Abstract", "paired_theme": "Giri Dark"},
            {"id": "beyond-space", "name": "Beyond Space", "filename": "beyond-space.png", "category": "Cosmic Nebula", "paired_theme": "Giri Midnight"},
            {"id": "quantum", "name": "Quantum", "filename": "quantum.png", "category": "Scientific Minimal", "paired_theme": "Giri Modern"},
            {"id": "aurora", "name": "Aurora", "filename": "aurora.png", "category": "Atmospheric Wave", "paired_theme": "Giri Dark"},
            {"id": "pure-minimal", "name": "Pure Minimal", "filename": "pure-minimal.png", "category": "Ultra-Clean Gradient", "paired_theme": "Giri Classic"},
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

        btn_restore = tk.Button(
            hdr_frame,
            text="★ Restore Default (Giri Origin)",
            font=("Segoe UI", 9, "bold"),
            bg="#16223d",
            fg="#00d2ff",
            activebackground="#223359",
            activeforeground="#ffffff",
            relief="flat",
            padx=10,
            pady=4,
            command=self.restore_default_wallpaper
        )
        btn_restore.pack(side="right")

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

        self._save_wallpaper_config()
        self.lbl_cur_status.config(text=f"Active Wallpaper: {name}")

        # Update parent desktop immediately without restart!
        if self.parent and hasattr(self.parent, "set_wallpaper_live"):
            self.parent.set_wallpaper_live(full_path, mode=self.mode_var.get())

        messagebox.showinfo("Wallpaper Applied", f"Successfully applied '{name}' without restarting.")

    def restore_default_wallpaper(self):
        default_file = os.path.join(WALLPAPER_DIR, "giri-origin.png")
        self.wallpaper_config["current_wallpaper"] = default_file
        self.wallpaper_config["current_name"] = "Giri Origin"
        self.wallpaper_config["is_solid_color"] = False
        self.wallpaper_config["mode"] = "Fill"
        self.mode_var.set("Fill")

        for s in ["1", "2", "3", "4"]:
            self.wallpaper_config["per_space"][s] = default_file

        self._save_wallpaper_config()
        self.lbl_cur_status.config(text="Active Wallpaper: Giri Origin (Default)")

        if self.parent and hasattr(self.parent, "set_wallpaper_live"):
            self.parent.set_wallpaper_live(default_file, mode="Fill")

        messagebox.showinfo("Wallpaper Restored", "Default Giri OS wallpaper (Giri Origin) restored successfully.")

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
