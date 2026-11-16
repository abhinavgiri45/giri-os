#!/usr/bin/env python3
"""
Giri OS — First Boot Setup Wizard
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Provides an elegant, zero-telemetry first-boot provisioning experience for Giri OS.
Handles localization, user configuration, theme & wallpaper selection,
hardware profile selection, and one-time flag persistence.
"""

import sys
import os
import json
import hashlib
import time

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("Error: Tkinter GUI toolkit is required to run the Giri OS Setup Wizard.")
    sys.exit(1)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
FLAG_DIR = os.path.expanduser("~/.config/giri")
FLAG_FILE = os.path.join(FLAG_DIR, "first-boot-done")
CONFIG_FILE = os.path.join(FLAG_DIR, "user-setup.json")
SYSTEM_CONFIG_FILE = os.path.join(ROOT_DIR, "system", "etc", "giri-firstboot.json")
WALLPAPER_CONFIG_FILE = os.path.join(ROOT_DIR, "system", "etc", "giri-wallpaper.json")


class GiriFirstBootWizard(tk.Tk):
    def __init__(self, non_interactive=False, force_reconfigure=False):
        super().__init__()
        self.non_interactive = non_interactive
        self.force_reconfigure = force_reconfigure

        self.title("Welcome to Giri OS — First Boot Setup")
        self.geometry("820x600")
        self.minsize(740, 520)
        self.configure(bg="#080c1a")

        # Configuration state
        self.config_data = {
            "language": "English (United States)",
            "keyboard": "US Standard (QWERTY)",
            "timezone": "UTC",
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
            ("Keyboard", self.render_keyboard),
            ("Time Zone", self.render_timezone),
            ("User Setup", self.render_user),
            ("Theme & Appearance", self.render_appearance),
            ("Desktop Profile", self.render_theme),
            ("Privacy", self.render_privacy),
            ("Ready to Launch", self.render_summary),
        ]

        self.setup_ui_shell()
        if not self.non_interactive:
            self.show_step(0)

    def setup_ui_shell(self):
        # Top banner with branding
        self.header_frame = tk.Frame(self, bg="#0d1428", height=64)
        self.header_frame.pack(side="top", fill="x")

        self.brand_title = tk.Label(
            self.header_frame,
            text="GIRI OS",
            font=("Segoe UI", 16, "bold"),
            fg="#00d2ff",
            bg="#0d1428"
        )
        self.brand_title.pack(side="left", padx=20, pady=14)

        self.step_label = tk.Label(
            self.header_frame,
            text=f"Step 1 of {len(self.steps)}: Welcome",
            font=("Segoe UI", 10),
            fg="#8ea4c8",
            bg="#0d1428"
        )
        self.step_label.pack(side="right", padx=20, pady=16)

        # Central content container
        self.content_frame = tk.Frame(self, bg="#080c1a")
        self.content_frame.pack(side="top", fill="both", expand=True, padx=30, pady=20)

        # Bottom navigation bar
        self.nav_frame = tk.Frame(self, bg="#0d1428", height=56)
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
            padx=14,
            pady=6,
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
            padx=18,
            pady=6,
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
            self.btn_next.config(text="Finish & Start Giri Space ★", bg="#00d2ff", fg="#050811")
        else:
            self.btn_next.config(text="Continue ▶", bg="#0077ff", fg="#ffffff")
        self.clear_content()
        render_func()

    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def next_step(self):
        # Validate current step before advancing
        if self.current_step == 4:  # User setup
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
        lbl_welcome = tk.Label(
            self.content_frame,
            text="Welcome to Giri OS",
            font=("Segoe UI", 24, "bold"),
            fg="#ffffff",
            bg="#080c1a"
        )
        lbl_welcome.pack(anchor="w", pady=(10, 4))

        lbl_tagline = tk.Label(
            self.content_frame,
            text="One System. Infinite Possibilities.",
            font=("Segoe UI", 12, "bold"),
            fg="#00d2ff",
            bg="#080c1a"
        )
        lbl_tagline.pack(anchor="w", pady=(0, 20))

        desc = (
            "Thank you for choosing Giri OS — an independent, open-source Linux operating system\n"
            "built for high performance, gaming capabilities, deep Windows application compatibility,\n"
            "and long-term reliability.\n\n"
            "Founder & Lead Architect: Abhinav Giri\n"
            "Base System: Debian GNU/Linux 12 (Bookworm AMD64)\n\n"
            "This initial setup wizard will help you configure language, input methods, accounts,\n"
            "desktop theme, and visual profiles in just a few minutes."
        )
        lbl_desc = tk.Label(
            self.content_frame,
            text=desc,
            font=("Segoe UI", 10),
            justify="left",
            fg="#a0aec0",
            bg="#080c1a"
        )
        lbl_desc.pack(anchor="w", pady=10)

    # Step 2: Language
    def render_language(self):
        tk.Label(self.content_frame, text="Select System Language", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 10))
        languages = ["English (United States)", "English (United Kingdom)", "English (India)", "Deutsch", "Español", "Français", "हिन्दी (Hindi)"]
        self.lang_var = tk.StringVar(value=self.config_data["language"])
        for lang in languages:
            rb = tk.Radiobutton(self.content_frame, text=lang, variable=self.lang_var, value=lang, font=("Segoe UI", 10), fg="#c2d5ee", bg="#080c1a", selectcolor="#16223d", activebackground="#080c1a", activeforeground="#ffffff", command=lambda: self.config_data.update({"language": self.lang_var.get()}))
            rb.pack(anchor="w", pady=3)

    # Step 3: Keyboard
    def render_keyboard(self):
        tk.Label(self.content_frame, text="Choose Keyboard Layout", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 10))
        keyboards = ["US Standard (QWERTY)", "UK Standard (QWERTY)", "US International with dead keys", "German (QWERTZ)", "French (AZERTY)"]
        self.kb_var = tk.StringVar(value=self.config_data["keyboard"])
        for kb in keyboards:
            rb = tk.Radiobutton(self.content_frame, text=kb, variable=self.kb_var, value=kb, font=("Segoe UI", 10), fg="#c2d5ee", bg="#080c1a", selectcolor="#16223d", activebackground="#080c1a", activeforeground="#ffffff", command=lambda: self.config_data.update({"keyboard": self.kb_var.get()}))
            rb.pack(anchor="w", pady=3)

    # Step 4: Time Zone
    def render_timezone(self):
        tk.Label(self.content_frame, text="Select Time Zone", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 10))
        timezones = ["Asia/Kolkata (IST +5:30)", "UTC (Coordinated Universal Time)", "America/New_York (EST)", "America/Los_Angeles (PST)", "Europe/London (GMT/BST)", "Europe/Berlin (CET)"]
        self.tz_var = tk.StringVar(value=self.config_data["timezone"])
        for tz in timezones:
            rb = tk.Radiobutton(self.content_frame, text=tz, variable=self.tz_var, value=tz, font=("Segoe UI", 10), fg="#c2d5ee", bg="#080c1a", selectcolor="#16223d", activebackground="#080c1a", activeforeground="#ffffff", command=lambda: self.config_data.update({"timezone": self.tz_var.get()}))
            rb.pack(anchor="w", pady=3)

    # Step 5: User Setup
    def render_user(self):
        tk.Label(self.content_frame, text="Create Your User Account", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 15))

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
        chk_sudo = tk.Checkbutton(f, text="Grant administrative (sudo) privileges to this user", variable=self.sudo_var, font=("Segoe UI", 9), fg="#00d2ff", bg="#080c1a", selectcolor="#16223d")
        chk_sudo.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))

    # Step 6: Theme & Appearance
    def render_appearance(self):
        tk.Label(self.content_frame, text="Select Theme & Default Wallpaper", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 10))

        tk.Label(self.content_frame, text="Choose your visual style for Giri Space:", font=("Segoe UI", 10), fg="#a0aec0", bg="#080c1a").pack(anchor="w", pady=(0, 12))

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
            text="★ Giri Origin Signature Abstract",
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

    # Step 7: Desktop Theme & Profile
    def render_theme(self):
        tk.Label(self.content_frame, text="Desktop Profile & Performance Tuning", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 10))
        desc = (
            "Select how Giri Space should render graphics on your computer:\n\n"
            "• Giri Classic: Ultra-lightweight rendering, minimal animations (Recommended for Intel HD 2000, 4-8GB RAM, HDDs)\n"
            "• Giri Modern: Fluid animations, orbital glassmorphism, rich shadows (Recommended for modern GPUs)"
        )
        tk.Label(self.content_frame, text=desc, font=("Segoe UI", 10), justify="left", fg="#a0aec0", bg="#080c1a").pack(anchor="w", pady=(0, 15))

        self.profile_var = tk.StringVar(value=self.config_data["desktop_theme"])
        for opt in ["Classic", "Modern"]:
            rb = tk.Radiobutton(self.content_frame, text=f"Giri {opt}", variable=self.profile_var, value=opt, font=("Segoe UI", 11, "bold"), fg="#00d2ff" if opt == "Classic" else "#c2d5ee", bg="#080c1a", selectcolor="#16223d", command=lambda: self.config_data.update({"desktop_theme": self.profile_var.get()}))
            rb.pack(anchor="w", pady=4)

    # Step 8: Privacy
    def render_privacy(self):
        tk.Label(self.content_frame, text="Privacy & Telemetry Controls", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 10))
        desc = (
            "Giri OS has ZERO hidden telemetry. We do not track your applications, keystrokes,\n"
            "or web browsing activities. Your privacy is a fundamental constitutional guarantee of this OS."
        )
        tk.Label(self.content_frame, text=desc, font=("Segoe UI", 10), justify="left", fg="#a0aec0", bg="#080c1a").pack(anchor="w", pady=(0, 15))

        self.cb_crash_var = tk.BooleanVar(value=self.config_data["privacy_crash_reports"])
        cb_crash = tk.Checkbutton(
            self.content_frame,
            text="Send anonymous local system crash reports to assist debugging (Off by default)",
            variable=self.cb_crash_var,
            font=("Segoe UI", 10),
            fg="#c2d5ee",
            bg="#080c1a",
            selectcolor="#16223d",
            command=lambda: self.config_data.update({"privacy_crash_reports": self.cb_crash_var.get()})
        )
        cb_crash.pack(anchor="w", pady=5)

    # Step 9: Summary
    def render_summary(self):
        tk.Label(self.content_frame, text="Ready to Launch Giri Space", font=("Segoe UI", 20, "bold"), fg="#ffffff", bg="#080c1a").pack(anchor="w", pady=(10, 10))
        summary = (
            f"User Account:     {self.config_data['username']} ({self.config_data['fullname']})\n"
            f"Admin (sudo):     {'Yes' if self.config_data['sudo_access'] else 'No'}\n"
            f"Language:         {self.config_data['language']}\n"
            f"Keyboard:         {self.config_data['keyboard']}\n"
            f"Time Zone:        {self.config_data['timezone']}\n"
            f"Visual Style:     Giri {self.config_data['theme_mode']} Edition ({self.config_data['wallpaper_choice']})\n"
            f"Desktop Profile:  Giri {self.config_data['desktop_theme']}\n"
            f"Telemetry:        Strictly Disabled (Zero tracking)\n\n"
            "Click 'Finish & Start Giri Space' to apply settings and enter your new operating system!"
        )
        tk.Label(self.content_frame, text=summary, font=("Consolas", 10), justify="left", fg="#00d2ff", bg="#10172e", padx=16, pady=16).pack(anchor="w", fill="x", pady=10)

    def save_and_finish(self):
        # 1. Save user configuration to user config dir
        os.makedirs(FLAG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=2)

        # 2. Save system copy
        os.makedirs(os.path.dirname(SYSTEM_CONFIG_FILE), exist_ok=True)
        try:
            with open(SYSTEM_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2)
        except Exception:
            pass

        # 3. Write wallpaper config
        wp_path = os.path.join(ROOT_DIR, "branding", "wallpapers", self.config_data["wallpaper_choice"])
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
                "2": os.path.join(ROOT_DIR, "branding", "wallpapers", "giri-origin.png"),
                "3": os.path.join(ROOT_DIR, "branding", "wallpapers", "infinite-flow.png"),
                "4": os.path.join(ROOT_DIR, "branding", "wallpapers", "quantum-form.png")
            }
        }
        try:
            with open(WALLPAPER_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(wp_cfg, f, indent=2)
        except Exception:
            pass

        # 4. Write completion flag
        with open(FLAG_FILE, "w", encoding="utf-8") as f:
            flag_info = {
                "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "username": self.config_data["username"],
                "version": "0.1 Genesis"
            }
            json.dump(flag_info, f, indent=2)

        print(f"Setup completed. Configuration written to {CONFIG_FILE}")
        messagebox.showinfo("Setup Complete", "Welcome to Giri OS! Initial configuration saved.")
        self.destroy()


def run_headless_verification():
    """Validates configuration generation logic headlessly."""
    wizard = GiriFirstBootWizard(non_interactive=True)
    assert wizard.config_data["privacy_telemetry"] is False
    assert wizard.config_data["language"] == "English (United States)"
    assert wizard.config_data["theme_mode"] in ["Dark", "Light"]
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
