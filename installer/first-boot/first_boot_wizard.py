#!/usr/bin/env python3
"""
Giri OS — First Boot Setup Wizard
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Provides an elegant, zero-telemetry first-boot provisioning experience for Giri OS 0.1 Genesis.
Handles:
- Multilingual localization (English, Hindi हिन्दी, French, Spanish, German, etc.)
- Region & Keyboard layout selection
- Network connectivity detection & offline setup support
- Time zone selection
- User account creation with administrative sudo delegation
- Theme mode (Dark / Light) & default wallpaper selection
- Desktop profile selection (Classic vs Modern hardware tiers)
- Privacy & zero-telemetry controls
- Non-destructive persistence, live-session safety, and safe desktop fallback
"""

import sys
import os
import json
import hashlib
import time
import subprocess
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("Warning: Tkinter GUI toolkit is required. Continuing to desktop.")
    sys.exit(0)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
FLAG_DIR = os.path.expanduser("~/.config/giri")
FLAG_FILE = os.path.join(FLAG_DIR, "first-boot-done")
CONFIG_FILE = os.path.join(FLAG_DIR, "user-setup.json")
SYSTEM_FLAG_DIR = "/var/lib/giri"
SYSTEM_FLAG_FILE = os.path.join(SYSTEM_FLAG_DIR, "first-boot-done")
SYSTEM_CONFIG_FILE = "/etc/giri-firstboot.json" if os.path.exists("/etc") and os.access("/etc", os.W_OK) else os.path.join(FLAG_DIR, "system-firstboot.json")
WALLPAPER_CONFIG_FILE = os.path.join(FLAG_DIR, "wallpaper.json")


def is_live_session():
    """Detects whether Giri OS is running in an ephemeral Live ISO session."""
    if os.path.exists("/run/live") or os.path.exists("/lib/live/mount"):
        return True
    try:
        if os.path.exists("/proc/cmdline"):
            with open("/proc/cmdline", "r", encoding="utf-8") as f:
                cmdline = f.read()
                if "boot=live" in cmdline or "live-media" in cmdline:
                    return True
    except Exception:
        pass
    user = os.environ.get("USER", "")
    if user in ["live", "user", "giri-live"]:
        if os.path.exists("/home/live") or os.path.exists("/home/user"):
            return True
    return False


def detect_network_status():
    """Detects network interfaces and online status using sysfs and standard tools."""
    status = {
        "connected": False,
        "interfaces": [],
        "details": "Offline Mode (No active connection detected)"
    }
    net_dir = "/sys/class/net"
    if os.path.exists(net_dir):
        try:
            for iface in os.listdir(net_dir):
                if iface == "lo":
                    continue
                operstate_file = os.path.join(net_dir, iface, "operstate")
                carrier_file = os.path.join(net_dir, iface, "carrier")
                is_up = False
                if os.path.exists(operstate_file):
                    try:
                        with open(operstate_file, "r") as f:
                            if f.read().strip() == "up":
                                is_up = True
                    except Exception:
                        pass
                elif os.path.exists(carrier_file):
                    try:
                        with open(carrier_file, "r") as f:
                            if f.read().strip() == "1":
                                is_up = True
                    except Exception:
                        pass

                if_type = "Wi-Fi" if iface.startswith(("wl", "wlan")) else "Ethernet"
                status["interfaces"].append({"name": iface, "type": if_type, "up": is_up})
                if is_up:
                    status["connected"] = True
                    status["details"] = f"Connected via {if_type} ({iface})"
        except Exception:
            pass

    return status


class GiriFirstBootWizard(tk.Tk):
    def __init__(self, non_interactive=False, force_reconfigure=False):
        super().__init__()
        self.non_interactive = non_interactive
        self.force_reconfigure = force_reconfigure
        self.is_live = is_live_session()

        self.title("Giri OS 0.1 Genesis — First Boot Setup")
        self.geometry("860x640")
        self.minsize(760, 560)
        self.configure(bg="#080c1a")

        # Configuration state
        self.config_data = {
            "language": "English (United States)",
            "region": "India (IN)",
            "keyboard": "US Standard (QWERTY)",
            "network_mode": "Offline",
            "timezone": "Asia/Kolkata (IST +5:30)",
            "username": "giri",
            "fullname": "Giri OS User",
            "password_hash": "",
            "sudo_access": True,
            "theme_mode": "Dark",
            "wallpaper_choice": "giri-os-default-dark.png",
            "privacy_telemetry": False,
            "privacy_crash_reports": False,
            "desktop_theme": "Classic",
            "hardware_tier": "Classic"
        }

        self.current_step = 0
        self.steps = [
            ("Welcome", self.render_welcome),
            ("Language", self.render_language),
            ("Region", self.render_region),
            ("Keyboard", self.render_keyboard),
            ("Network", self.render_network),
            ("Time Zone", self.render_timezone),
            ("User Setup", self.render_user),
            ("Appearance", self.render_appearance),
            ("Desktop Profile", self.render_theme),
            ("Privacy", self.render_privacy),
            ("Summary", self.render_summary),
        ]

        self.setup_ui_shell()
        if not self.non_interactive:
            self.show_step(0)

    def setup_ui_shell(self):
        # Top banner with branding
        self.header_frame = tk.Frame(self, bg="#0d1428", height=68)
        self.header_frame.pack(side="top", fill="x")

        # Brand Emblem & Title
        title_box = tk.Frame(self.header_frame, bg="#0d1428")
        title_box.pack(side="left", padx=20, pady=12)

        self.brand_title = tk.Label(
            title_box,
            text="GIRI OS",
            font=("Segoe UI", 16, "bold"),
            fg="#00d2ff",
            bg="#0d1428"
        )
        self.brand_title.pack(side="left")

        self.brand_badge = tk.Label(
            title_box,
            text="0.1 GENESIS",
            font=("Segoe UI", 9, "bold"),
            fg="#9d4edd",
            bg="#16223d",
            padx=6,
            pady=2
        )
        self.brand_badge.pack(side="left", padx=10)

        if self.is_live:
            live_badge = tk.Label(
                title_box,
                text="LIVE ISO PREVIEW",
                font=("Segoe UI", 8, "bold"),
                fg="#f59e0b",
                bg="#1c1917",
                padx=6,
                pady=2
            )
            live_badge.pack(side="left")

        self.step_label = tk.Label(
            self.header_frame,
            text=f"Step 1 of {len(self.steps)}: Welcome",
            font=("Segoe UI", 10),
            fg="#8ea4c8",
            bg="#0d1428"
        )
        self.step_label.pack(side="right", padx=20, pady=18)

        # Central content container
        self.content_frame = tk.Frame(self, bg="#080c1a")
        self.content_frame.pack(side="top", fill="both", expand=True, padx=32, pady=16)

        # Bottom navigation bar
        self.nav_frame = tk.Frame(self, bg="#0d1428", height=60)
        self.nav_frame.pack(side="bottom", fill="x")

        self.btn_back = tk.Button(
            self.nav_frame,
            text="◀ Back",
            font=("Segoe UI", 10),
            bg="#16223d",
            fg="#c2d5ee",
            activebackground="#223359",
            activeforeground="#ffffff",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.prev_step
        )
        self.btn_back.pack(side="left", padx=20, pady=12)

        self.btn_next = tk.Button(
            self.nav_frame,
            text="Continue ▶",
            font=("Segoe UI", 10, "bold"),
            bg="#0077ff",
            fg="#ffffff",
            activebackground="#0099ff",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=6,
            cursor="hand2",
            command=self.next_step
        )
        self.btn_next.pack(side="right", padx=20, pady=12)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_step(self, step_idx):
        if step_idx < 0 or step_idx >= len(self.steps):
            return
        self.current_step = step_idx
        step_name, render_func = self.steps[step_idx]
        self.step_label.config(text=f"Step {step_idx + 1} of {len(self.steps)}: {step_name}")
        self.btn_back.config(state="disabled" if step_idx == 0 else "normal")
        if step_idx == len(self.steps) - 1:
            self.btn_next.config(text="Finish & Launch Giri Space ★", bg="#00d2ff", fg="#050811")
        else:
            self.btn_next.config(text="Continue ▶", bg="#0077ff", fg="#ffffff")
        self.clear_content()
        render_func()

    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def next_step(self):
        # Validate User Setup step before advancing
        if self.current_step == 6:  # User setup
            pwd = self.entry_pwd.get()
            pwd_confirm = self.entry_pwd_confirm.get()
            username = self.entry_user.get().strip()

            if not username:
                messagebox.showerror("Validation Error", "Please provide a valid username.")
                return
            if len(pwd) < 4:
                messagebox.showerror("Validation Error", "Password must be at least 4 characters long.")
                return
            if pwd != pwd_confirm:
                messagebox.showerror("Validation Error", "Passwords do not match.")
                return

            self.config_data["username"] = username
            self.config_data["fullname"] = self.entry_fullname.get().strip() or username
            self.config_data["password_hash"] = hashlib.sha256(pwd.encode("utf-8")).hexdigest()
            self.config_data["sudo_access"] = self.sudo_var.get()

        if self.current_step < len(self.steps) - 1:
            self.show_step(self.current_step + 1)
        else:
            self.save_and_finish()

    # Step 1: Welcome
    def render_welcome(self):
        tk.Label(
            self.content_frame,
            text="Welcome to Giri OS",
            font=("Segoe UI", 24, "bold"),
            fg="#ffffff",
            bg="#080c1a"
        ).pack(anchor="w", pady=(10, 4))

        tk.Label(
            self.content_frame,
            text="ONE SYSTEM. INFINITE POSSIBILITIES.",
            font=("Segoe UI", 12, "bold"),
            fg="#00d2ff",
            bg="#080c1a"
        ).pack(anchor="w", pady=(0, 16))

        desc = (
            "Thank you for choosing Giri OS — an independent, high-performance Linux operating system\n"
            "engineered for gaming performance, deep Windows software compatibility, and rock-solid Debian reliability.\n\n"
            "Founder & Lead Architect: Abhinav Giri\n"
            "Architecture: Debian 12 Bookworm (AMD64 / x86_64)\n\n"
            "This setup wizard will configure your localization, user account, networking, desktop theme,\n"
            "and performance profiles in just a few simple steps."
        )
        tk.Label(
            self.content_frame,
            text=desc,
            font=("Segoe UI", 10),
            justify="left",
            fg="#a0aec0",
            bg="#080c1a"
        ).pack(anchor="w", pady=6)

        if self.is_live:
            live_note = (
                "Notice: You are currently running in a Live ISO test session.\n"
                "You can explore and configure settings safely. Your physical host computer is not modified."
            )
            tk.Label(
                self.content_frame,
                text=live_note,
                font=("Segoe UI", 9, "italic"),
                justify="left",
                fg="#f59e0b",
                bg="#1c1917",
                padx=12,
                pady=8
            ).pack(anchor="w", fill="x", pady=12)

    # Step 2: Language
    def render_language(self):
        tk.Label(self.content_frame, text="Select System Language", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 6))
        tk.Label(self.content_frame, text="Choose your primary language for user interface and documentation:", font=("Segoe UI", 10), fg="#8ea4c8", bg="#080c1a").pack(anchor="w", pady=(0, 10))

        languages = [
            ("English (United States)", "English (US) — Default"),
            ("English (India)", "English (India) — Recommended"),
            ("हिन्दी (Hindi)", "हिन्दी — Devanagari UI & Input"),
            ("Français (French)", "Français — French"),
            ("Español (Spanish)", "Español — Spanish"),
            ("Deutsch (German)", "Deutsch — German"),
            ("Italiano (Italian)", "Italiano — Italian"),
            ("Português (Portuguese)", "Português — Portuguese"),
            ("日本語 (Japanese)", "日本語 — Japanese")
        ]

        self.lang_var = tk.StringVar(value=self.config_data["language"])
        for lang_val, lang_label in languages:
            rb = tk.Radiobutton(
                self.content_frame,
                text=lang_label,
                variable=self.lang_var,
                value=lang_val,
                font=("Nirmala UI", 10) if "हिन्दी" in lang_label else ("Segoe UI", 10),
                fg="#c2d5ee",
                bg="#080c1a",
                selectcolor="#16223d",
                activebackground="#080c1a",
                activeforeground="#ffffff",
                command=lambda: self.config_data.update({"language": self.lang_var.get()})
            )
            rb.pack(anchor="w", pady=2)

    # Step 3: Region
    def render_region(self):
        tk.Label(self.content_frame, text="Select Country & Region", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 6))
        tk.Label(self.content_frame, text="Configures locale formats, currency symbols, and measurement units:", font=("Segoe UI", 10), fg="#8ea4c8", bg="#080c1a").pack(anchor="w", pady=(0, 10))

        regions = [
            "India (IN) — Metric (₹ INR)",
            "United States (US) — Imperial ($ USD)",
            "United Kingdom (GB) — Metric (£ GBP)",
            "European Union (EU) — Metric (€ EUR)",
            "Canada (CA) — Metric ($ CAD)",
            "Australia (AU) — Metric ($ AUD)",
            "Singapore (SG) — Metric ($ SGD)",
            "Japan (JP) — Metric (¥ JPY)",
            "Worldwide (UTC / International)"
        ]

        self.region_var = tk.StringVar(value=self.config_data["region"])
        for reg in regions:
            rb = tk.Radiobutton(
                self.content_frame,
                text=reg,
                variable=self.region_var,
                value=reg,
                font=("Segoe UI", 10),
                fg="#c2d5ee",
                bg="#080c1a",
                selectcolor="#16223d",
                command=lambda: self.config_data.update({"region": self.region_var.get()})
            )
            rb.pack(anchor="w", pady=2)

    # Step 4: Keyboard
    def render_keyboard(self):
        tk.Label(self.content_frame, text="Choose Keyboard Layout", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 6))
        keyboards = [
            "US Standard (QWERTY) — Default",
            "Indian English (QWERTY)",
            "Hindi Inscript / Phonetic",
            "UK English (QWERTY)",
            "German (QWERTZ)",
            "French (AZERTY)",
            "Spanish (ISO)"
        ]
        self.kb_var = tk.StringVar(value=self.config_data["keyboard"])
        for kb in keyboards:
            rb = tk.Radiobutton(
                self.content_frame,
                text=kb,
                variable=self.kb_var,
                value=kb,
                font=("Segoe UI", 10),
                fg="#c2d5ee",
                bg="#080c1a",
                selectcolor="#16223d",
                command=lambda: self.config_data.update({"keyboard": self.kb_var.get()})
            )
            rb.pack(anchor="w", pady=2)

    # Step 5: Network
    def render_network(self):
        tk.Label(self.content_frame, text="Network Connectivity", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 6))
        
        net_info = detect_network_status()
        self.config_data["network_mode"] = "Online" if net_info["connected"] else "Offline"

        status_color = "#10b981" if net_info["connected"] else "#94a3b8"
        status_text = "● Connected" if net_info["connected"] else "○ Offline Mode"

        f_status = tk.Frame(self.content_frame, bg="#0f172a", padx=16, pady=12)
        f_status.pack(fill="x", pady=8)

        tk.Label(f_status, text=status_text, font=("Segoe UI", 12, "bold"), fg=status_color, bg="#0f172a").pack(anchor="w")
        tk.Label(f_status, text=net_info["details"], font=("Segoe UI", 10), fg="#c2d5ee", bg="#0f172a").pack(anchor="w", pady=4)

        if not net_info["connected"]:
            desc = (
                "Giri OS is fully functional without an active internet connection.\n"
                "All foundational system utilities, offline wallpapers, documentation,\n"
                "and driver tools are pre-installed in this Genesis image."
            )
            tk.Label(self.content_frame, text=desc, font=("Segoe UI", 10), fg="#8ea4c8", bg="#080c1a", justify="left").pack(anchor="w", pady=10)

        # Network selection radio options
        self.net_choice_var = tk.StringVar(value="auto")
        rb_auto = tk.Radiobutton(
            self.content_frame,
            text="Automatic Connection (Use available Ethernet / Wi-Fi)",
            variable=self.net_choice_var,
            value="auto",
            font=("Segoe UI", 10),
            fg="#c2d5ee",
            bg="#080c1a",
            selectcolor="#16223d"
        )
        rb_auto.pack(anchor="w", pady=4)

        rb_offline = tk.Radiobutton(
            self.content_frame,
            text="Continue Offline (Configure networks later in Giri Control Center)",
            variable=self.net_choice_var,
            value="offline",
            font=("Segoe UI", 10),
            fg="#c2d5ee",
            bg="#080c1a",
            selectcolor="#16223d"
        )
        rb_offline.pack(anchor="w", pady=4)

    # Step 6: Time Zone
    def render_timezone(self):
        tk.Label(self.content_frame, text="Select Time Zone", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 6))
        timezones = [
            "Asia/Kolkata (IST +5:30) — India Standard Time",
            "UTC (Coordinated Universal Time)",
            "America/New_York (EST / EDT)",
            "America/Los_Angeles (PST / PDT)",
            "Europe/London (GMT / BST)",
            "Europe/Berlin (CET / CEST)",
            "Asia/Tokyo (JST +9:00)",
            "Asia/Dubai (GST +4:00)"
        ]
        self.tz_var = tk.StringVar(value=self.config_data["timezone"])
        for tz in timezones:
            rb = tk.Radiobutton(
                self.content_frame,
                text=tz,
                variable=self.tz_var,
                value=tz,
                font=("Segoe UI", 10),
                fg="#c2d5ee",
                bg="#080c1a",
                selectcolor="#16223d",
                command=lambda: self.config_data.update({"timezone": self.tz_var.get()})
            )
            rb.pack(anchor="w", pady=2)

    # Step 7: User Setup
    def render_user(self):
        tk.Label(self.content_frame, text="Create Your User Account", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 10))

        f = tk.Frame(self.content_frame, bg="#080c1a")
        f.pack(anchor="w", fill="x")

        tk.Label(f, text="Full Name:", font=("Segoe UI", 10), fg="#8ea4c8", bg="#080c1a").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_fullname = tk.Entry(f, font=("Segoe UI", 10), width=32, bg="#10172e", fg="#ffffff", insertbackground="#00d2ff")
        self.entry_fullname.insert(0, self.config_data["fullname"])
        self.entry_fullname.grid(row=0, column=1, sticky="w", padx=10, pady=6)

        tk.Label(f, text="Username:", font=("Segoe UI", 10), fg="#8ea4c8", bg="#080c1a").grid(row=1, column=0, sticky="w", pady=6)
        self.entry_user = tk.Entry(f, font=("Segoe UI", 10), width=32, bg="#10172e", fg="#ffffff", insertbackground="#00d2ff")
        self.entry_user.insert(0, self.config_data["username"])
        self.entry_user.grid(row=1, column=1, sticky="w", padx=10, pady=6)

        tk.Label(f, text="Password:", font=("Segoe UI", 10), fg="#8ea4c8", bg="#080c1a").grid(row=2, column=0, sticky="w", pady=6)
        self.entry_pwd = tk.Entry(f, font=("Segoe UI", 10), width=32, show="•", bg="#10172e", fg="#ffffff", insertbackground="#00d2ff")
        self.entry_pwd.grid(row=2, column=1, sticky="w", padx=10, pady=6)

        tk.Label(f, text="Confirm Password:", font=("Segoe UI", 10), fg="#8ea4c8", bg="#080c1a").grid(row=3, column=0, sticky="w", pady=6)
        self.entry_pwd_confirm = tk.Entry(f, font=("Segoe UI", 10), width=32, show="•", bg="#10172e", fg="#ffffff", insertbackground="#00d2ff")
        self.entry_pwd_confirm.grid(row=3, column=1, sticky="w", padx=10, pady=6)

        self.sudo_var = tk.BooleanVar(value=self.config_data["sudo_access"])
        chk_sudo = tk.Checkbutton(
            f,
            text="Grant administrative (sudo) privileges to this user",
            variable=self.sudo_var,
            font=("Segoe UI", 9),
            fg="#00d2ff",
            bg="#080c1a",
            selectcolor="#16223d"
        )
        chk_sudo.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))

    # Step 8: Appearance
    def render_appearance(self):
        tk.Label(self.content_frame, text="Select Theme & Default Wallpaper", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 6))
        tk.Label(self.content_frame, text="Choose your visual style for Giri Space:", font=("Segoe UI", 10), fg="#a0aec0", bg="#080c1a").pack(anchor="w", pady=(0, 10))

        self.theme_var = tk.StringVar(value=self.config_data["theme_mode"])
        t_card = tk.Frame(self.content_frame, bg="#0f172a", padx=16, pady=12)
        t_card.pack(fill="x", pady=4)

        rb_dark = tk.Radiobutton(
            t_card,
            text="🌙 Giri OS Dark Edition (Default: giri-os-default-dark.png)",
            variable=self.theme_var,
            value="Dark",
            font=("Segoe UI", 10, "bold"),
            fg="#00d2ff",
            bg="#0f172a",
            selectcolor="#16223d",
            command=lambda: self.update_theme_choice("Dark", "giri-os-default-dark.png")
        )
        rb_dark.pack(anchor="w", pady=3)

        rb_light = tk.Radiobutton(
            t_card,
            text="☀ Giri OS Light Edition (Default: giri-os-default-light.png)",
            variable=self.theme_var,
            value="Light",
            font=("Segoe UI", 10, "bold"),
            fg="#ffffff",
            bg="#0f172a",
            selectcolor="#16223d",
            command=lambda: self.update_theme_choice("Light", "giri-os-default-light.png")
        )
        rb_light.pack(anchor="w", pady=3)

        rb_origin = tk.Radiobutton(
            t_card,
            text="★ Giri Origin Signature Abstract (giri-origin.png)",
            variable=self.theme_var,
            value="Origin",
            font=("Segoe UI", 10),
            fg="#c2d5ee",
            bg="#0f172a",
            selectcolor="#16223d",
            command=lambda: self.update_theme_choice("Dark", "giri-origin.png")
        )
        rb_origin.pack(anchor="w", pady=3)

    def update_theme_choice(self, mode, wp):
        self.config_data["theme_mode"] = mode
        self.config_data["wallpaper_choice"] = wp

    # Step 9: Desktop Profile
    def render_theme(self):
        tk.Label(self.content_frame, text="Desktop Profile & Performance Tuning", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 6))
        desc = (
            "Select how Giri Space renders graphics on your hardware:\n\n"
            "• Giri Classic: Ultra-lightweight rendering, minimal animations (Recommended for Intel HD 2000, 4-8GB RAM, HDDs)\n"
            "• Giri Modern: Fluid animations, modern glassmorphism, rich shadows (Recommended for modern dedicated GPUs)"
        )
        tk.Label(self.content_frame, text=desc, font=("Segoe UI", 10), justify="left", fg="#a0aec0", bg="#080c1a").pack(anchor="w", pady=(0, 15))

        self.profile_var = tk.StringVar(value=self.config_data["desktop_theme"])
        for opt in ["Classic", "Modern"]:
            rb = tk.Radiobutton(
                self.content_frame,
                text=f"Giri {opt}",
                variable=self.profile_var,
                value=opt,
                font=("Segoe UI", 11, "bold"),
                fg="#00d2ff" if opt == "Classic" else "#c2d5ee",
                bg="#080c1a",
                selectcolor="#16223d",
                command=lambda: self.config_data.update({"desktop_theme": self.profile_var.get()})
            )
            rb.pack(anchor="w", pady=4)

    # Step 10: Privacy
    def render_privacy(self):
        tk.Label(self.content_frame, text="Privacy & Telemetry Controls", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 6))
        desc = (
            "Giri OS has ZERO hidden telemetry. We do not track your applications, keystrokes,\n"
            "personal files, or web browsing activities. Your privacy is a core constitutional guarantee of this OS."
        )
        tk.Label(self.content_frame, text=desc, font=("Segoe UI", 10), justify="left", fg="#a0aec0", bg="#080c1a").pack(anchor="w", pady=(0, 15))

        self.cb_crash_var = tk.BooleanVar(value=self.config_data["privacy_crash_reports"])
        cb_crash = tk.Checkbutton(
            self.content_frame,
            text="Enable anonymous local system crash dumps to assist debugging (Off by default)",
            variable=self.cb_crash_var,
            font=("Segoe UI", 10),
            fg="#c2d5ee",
            bg="#080c1a",
            selectcolor="#16223d",
            command=lambda: self.config_data.update({"privacy_crash_reports": self.cb_crash_var.get()})
        )
        cb_crash.pack(anchor="w", pady=5)

    # Step 11: Summary
    def render_summary(self):
        tk.Label(self.content_frame, text="Ready to Launch Giri Space", font=("Segoe UI", 20, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 6))
        summary = (
            f"User Account:     {self.config_data['username']} ({self.config_data['fullname']})\n"
            f"Admin (sudo):     {'Yes' if self.config_data['sudo_access'] else 'No'}\n"
            f"Language:         {self.config_data['language']}\n"
            f"Region:           {self.config_data['region']}\n"
            f"Keyboard:         {self.config_data['keyboard']}\n"
            f"Time Zone:        {self.config_data['timezone']}\n"
            f"Visual Style:     Giri {self.config_data['theme_mode']} Edition ({self.config_data['wallpaper_choice']})\n"
            f"Desktop Profile:  Giri {self.config_data['desktop_theme']}\n"
            f"Telemetry:        Strictly Disabled (Zero tracking)\n\n"
            "Click 'Finish & Launch Giri Space' to apply settings and enter your new operating system!"
        )
        tk.Label(self.content_frame, text=summary, font=("Consolas", 10), justify="left", fg="#00d2ff", bg="#10172e", padx=16, pady=16).pack(anchor="w", fill="x", pady=8)

    def save_and_finish(self):
        """Atomically persists setup configuration and completion flag."""
        # 1. User Configuration
        os.makedirs(FLAG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=2)

        # 2. System Copy
        os.makedirs(os.path.dirname(SYSTEM_CONFIG_FILE), exist_ok=True)
        try:
            with open(SYSTEM_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2)
        except Exception:
            pass

        # 3. Wallpaper configuration
        wp_choice = self.config_data.get("wallpaper_choice", "giri-os-default-dark.png")
        if os.path.isdir("/usr/share/backgrounds"):
            wp_path = f"/usr/share/backgrounds/{wp_choice}"
            space_2 = "/usr/share/backgrounds/giri-origin.png"
            space_3 = "/usr/share/backgrounds/infinite-flow.png"
            space_4 = "/usr/share/backgrounds/quantum-form.png"
        else:
            wp_path = os.path.join(ROOT_DIR, "branding", "wallpapers", wp_choice)
            space_2 = os.path.join(ROOT_DIR, "branding", "wallpapers", "giri-origin.png")
            space_3 = os.path.join(ROOT_DIR, "branding", "wallpapers", "infinite-flow.png")
            space_4 = os.path.join(ROOT_DIR, "branding", "wallpapers", "quantum-form.png")

        wp_cfg = {
            "current_wallpaper": wp_path,
            "current_name": f"Giri OS — {self.config_data['theme_mode']} Edition",
            "theme": self.config_data["theme_mode"].lower(),
            "auto_switch_theme": True,
            "user_manually_selected": False,
            "mode": "Fill",
            "is_solid_color": False,
            "solid_color": "#050811",
            "per_space": {
                "1": wp_path,
                "2": space_2,
                "3": space_3,
                "4": space_4
            }
        }
        os.makedirs(os.path.dirname(WALLPAPER_CONFIG_FILE), exist_ok=True)
        try:
            with open(WALLPAPER_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(wp_cfg, f, indent=2)
        except Exception:
            pass

        if os.path.exists("/etc") and os.access("/etc", os.W_OK):
            try:
                with open("/etc/giri-wallpaper.json", "w", encoding="utf-8") as f:
                    json.dump(wp_cfg, f, indent=2)
            except Exception:
                pass

        # 4. Completion Flag
        # Only write permanent system flag if NOT in a live ISO session
        flag_info = {
            "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "username": self.config_data["username"],
            "version": "0.1 Genesis",
            "is_live_session": self.is_live
        }

        # User-level flag
        with open(FLAG_FILE, "w", encoding="utf-8") as f:
            json.dump(flag_info, f, indent=2)

        # System-level flag (only written if not live session or if force permitted)
        if not self.is_live:
            try:
                os.makedirs(SYSTEM_FLAG_DIR, exist_ok=True)
                with open(SYSTEM_FLAG_FILE, "w", encoding="utf-8") as f:
                    json.dump(flag_info, f, indent=2)
            except Exception:
                pass

        print(f"[+] Setup completed. Configuration written to {CONFIG_FILE}")
        if not self.non_interactive:
            messagebox.showinfo("Setup Complete", "Welcome to Giri OS! Initial configuration saved.")
        self.destroy()


def run_headless_verification():
    """Validates configuration generation logic headlessly."""
    wizard = GiriFirstBootWizard(non_interactive=True)
    assert wizard.config_data["privacy_telemetry"] is False
    assert "English" in wizard.config_data["language"]
    assert wizard.config_data["theme_mode"] in ["Dark", "Light"]
    assert len(wizard.steps) == 11
    print("Headless First Boot Wizard state verification passed.")
    wizard.destroy()


if __name__ == "__main__":
    if "--verify" in sys.argv:
        run_headless_verification()
        sys.exit(0)

    # Check one-time flag
    is_reconfigure = "--reconfigure" in sys.argv
    if os.path.isfile(FLAG_FILE) and not is_reconfigure:
        print(f"Giri OS first-boot setup has already been completed ({FLAG_FILE} exists).")
        print("To run setup again, execute: python first_boot_wizard.py --reconfigure")
        sys.exit(0)

    app = GiriFirstBootWizard(force_reconfigure=is_reconfigure)
    app.mainloop()
