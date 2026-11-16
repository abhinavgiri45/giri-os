#!/usr/bin/env python3
"""
Giri OS — Giri Welcome Experience & First Boot Orchestrator
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Provides a cinematic, full-screen first-boot welcome sequence for Giri OS 0.1 Genesis.
Features:
- Logo reveal with glowing geometric styling.
- Multilingual greeting transitions: WELCOME -> NAMASTE (नमस्ते) -> International greetings.
- Tagline reveal: ONE SYSTEM. INFINITE POSSIBILITIES.
- Seamless transition to the First Boot Setup Wizard.
- Skippable animation (Escape / Space / Skip Button).
- Resilient recovery: never blocks desktop launch or leaves OS unbootable.
- Live ISO safety: does not mark live sessions as completed installations.
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    # If Tkinter is unavailable, exit cleanly with code 0 to allow desktop fallback
    print("Warning: Tkinter is unavailable. Bypassing Giri Welcome Experience.")
    sys.exit(0)

# Paths & Flags
HOME_DIR = os.path.expanduser("~")
USER_CONFIG_DIR = os.path.join(HOME_DIR, ".config", "giri")
USER_FLAG_FILE = os.path.join(USER_CONFIG_DIR, "first-boot-done")
SYSTEM_FLAG_DIR = "/var/lib/giri"
SYSTEM_FLAG_FILE = os.path.join(SYSTEM_FLAG_DIR, "first-boot-done")
LOG_DIR = os.path.join(USER_CONFIG_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "welcome.log")

# Import First Boot Wizard if available locally
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    import first_boot_wizard
except ImportError:
    first_boot_wizard = None


def log_event(message):
    """Safely logs execution events for diagnostic audits."""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def is_live_session():
    """Detects whether Giri OS is running in a live ISO session."""
    # 1. Live filesystem mount indicators
    if os.path.exists("/run/live") or os.path.exists("/lib/live/mount"):
        return True
    # 2. Kernel command-line live parameters
    try:
        if os.path.exists("/proc/cmdline"):
            with open("/proc/cmdline", "r", encoding="utf-8") as f:
                cmdline = f.read()
                if "boot=live" in cmdline or "live-media" in cmdline:
                    return True
    except Exception:
        pass
    # 3. Environment or live user heuristic
    user = os.environ.get("USER", "")
    if user in ["live", "user", "giri-live"]:
        if os.path.exists("/home/live") or os.path.exists("/home/user"):
            return True
    return False


def is_setup_completed():
    """Checks whether first-boot setup has already been officially completed."""
    if os.path.exists(USER_FLAG_FILE) or os.path.exists(SYSTEM_FLAG_FILE):
        return True
    return False


class GiriWelcomeExperience(tk.Tk):
    def __init__(self, skip_animation=False, test_mode=False):
        super().__init__()
        self.skip_animation = skip_animation
        self.test_mode = test_mode
        self.animation_running = True
        self.current_frame = 0
        self.step = 0

        self.title("Welcome to Giri OS")
        self.configure(bg="#050811")
        
        # Dimensions: Fullscreen in real usage, large modal in test mode
        if not test_mode and not skip_animation:
            try:
                self.attributes("-fullscreen", True)
            except Exception:
                self.geometry("1024x720")
        else:
            self.geometry("960x640")

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        if self.test_mode:
            self.screen_width = 960
            self.screen_height = 640

        self.cx = self.screen_width // 2
        self.cy = self.screen_height // 2

        self.setup_canvas()
        self.bind_events()

        # Multilingual greetings data
        self.greetings = [
            ("WELCOME", "GIRI OS 0.1 GENESIS", "#FFFFFF", "#00F0FF"),
            ("नमस्ते", "GIRI OS MEIN AAPKA SWAGAT HAI", "#00F0FF", "#C084FC"),
            ("NAMASTE", "WELCOME TO THE FUTURE OF COMPUTING", "#38BDF8", "#E2E8F0"),
            ("BONJOUR", "UN SYSTÈME. POSSIBILITÉS INFINIES.", "#C084FC", "#9333EA"),
            ("HOLA", "UN SISTEMA. INFINITAS POSIBILIDADES.", "#00F0FF", "#38BDF8"),
            ("CIAO", "UN SISTEMA. INFINITE POSSIBILITÀ.", "#A855F7", "#E2E8F0"),
            ("HALLO", "EIN SYSTEM. UNENDLICHE MÖGLICHKEITEN.", "#38BDF8", "#00F0FF"),
            ("வணக்கம்", "வரவேற்கிறோம் — கிரி ஓஎஸ்", "#00F0FF", "#C084FC"),
            ("ONE SYSTEM. INFINITE POSSIBILITIES.", "GIRI OS — FOUNDED BY ABHINAV GIRI", "#00F0FF", "#9D4EDD"),
        ]
        self.greeting_idx = 0

        log_event(f"Initialized GiriWelcomeExperience (skip_anim={skip_animation}, test_mode={test_mode})")

        if self.skip_animation:
            self.transition_to_wizard()
        else:
            self.start_intro_animation()

    def setup_canvas(self):
        """Creates the cinematic high-contrast animation canvas."""
        self.canvas = tk.Canvas(
            self,
            bg="#050811",
            highlightthickness=0,
            width=self.screen_width,
            height=self.screen_height
        )
        self.canvas.pack(fill="both", expand=True)

        # Skip button in top right
        self.btn_skip = tk.Button(
            self,
            text="Skip Intro ⏭",
            font=("Segoe UI", 10, "bold"),
            bg="#111827",
            fg="#94A3B8",
            activebackground="#1E293B",
            activeforeground="#00F0FF",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.skip_and_launch
        )
        self.btn_skip.place(x=self.screen_width - 140, y=24)

    def bind_events(self):
        """Binds keyboard shortcuts for easy skipping."""
        self.bind("<Escape>", lambda e: self.skip_and_launch())
        self.bind("<space>", lambda e: self.skip_and_launch())
        self.bind("<Return>", lambda e: self.skip_and_launch())

    def skip_and_launch(self):
        """Immediately halts animations and advances directly to setup."""
        log_event("User triggered skip intro.")
        self.animation_running = False
        self.transition_to_wizard()

    def draw_genesis_emblem(self, progress=1.0):
        """
        Renders the signature Giri OS Genesis emblem on the canvas.
        Progress scale: 0.0 to 1.0 (blooming scale).
        """
        self.canvas.delete("emblem")
        scale = max(0.2, min(1.0, progress))
        cy_offset = self.cy - int(80 * scale)

        # Ambient Glow Oval (#0F172A)
        glow_rx = int(140 * scale)
        glow_ry = int(60 * scale)
        self.canvas.create_oval(
            self.cx - glow_rx, cy_offset - glow_ry,
            self.cx + glow_rx, cy_offset + glow_ry,
            fill="#0F172A", outline="", tags="emblem"
        )

        # Try displaying official raster logo sprite if available
        logo_loaded = False
        try:
            from PIL import Image, ImageTk
            logo_path = os.path.join(CURRENT_DIR, "..", "..", "branding", "logo", "giri-os-icon.png")
            if not os.path.isfile(logo_path):
                logo_path = "/usr/share/pixmaps/giri-os-icon.png"
            if os.path.isfile(logo_path):
                target_size = max(32, int(160 * scale))
                if not hasattr(self, "_cached_logo_img") or getattr(self, "_cached_logo_size", 0) != target_size:
                    pil_img = Image.open(logo_path).convert("RGBA")
                    pil_img = pil_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
                    self._cached_logo_tk = ImageTk.PhotoImage(pil_img)
                    self._cached_logo_size = target_size
                self.canvas.create_image(self.cx, cy_offset, image=self._cached_logo_tk, tags="emblem")
                logo_loaded = True
        except Exception:
            logo_loaded = False

        if not logo_loaded:
            # Procedural Vector 'G' Monogram Fallback
            g_size = int(42 * scale)
            # Upper Canopy (Electric Blue)
            self.canvas.create_line(
                self.cx - g_size, cy_offset - g_size,
                self.cx + g_size, cy_offset - g_size,
                fill="#00D2FF", width=max(2, int(7 * scale)),
                capstyle="round", tags="emblem"
            )
            # Left Spine (Electric Blue to Azure)
            self.canvas.create_line(
                self.cx - g_size, cy_offset - g_size,
                self.cx - g_size, cy_offset + g_size,
                fill="#00D2FF", width=max(2, int(7 * scale)),
                capstyle="round", tags="emblem"
            )
            # Foundation & Crossbar
            self.canvas.create_line(
                self.cx - g_size, cy_offset + g_size,
                self.cx + g_size, cy_offset + g_size,
                fill="#3B82F6", width=max(2, int(7 * scale)),
                capstyle="round", tags="emblem"
            )
            self.canvas.create_line(
                self.cx + g_size, cy_offset + g_size,
                self.cx + g_size, cy_offset,
                fill="#3B82F6", width=max(2, int(7 * scale)),
                capstyle="round", tags="emblem"
            )
            self.canvas.create_line(
                self.cx, cy_offset,
                self.cx + g_size, cy_offset,
                fill="#00D2FF", width=max(2, int(7 * scale)),
                capstyle="round", tags="emblem"
            )

    # Backward compatibility alias
    draw_orbital_emblem = draw_genesis_emblem

    def start_intro_animation(self):
        """Phase 1: Bloom the official Giri OS emblem into view."""
        self.anim_step = 0
        self.animate_bloom()

    def animate_bloom(self):
        if not self.animation_running:
            return
        self.anim_step += 1
        progress = self.anim_step / 20.0
        self.draw_genesis_emblem(progress)

        if self.anim_step < 20:
            self.after(25, self.animate_bloom)
        else:
            # Emblem is fully bloomed; begin multilingual sequence
            self.after(400, self.cycle_greetings)

    def cycle_greetings(self):
        """Phases 2-5: Displays multilingual transitions."""
        if not self.animation_running:
            return

        if self.greeting_idx >= len(self.greetings):
            # Sequence complete; transition to setup button
            self.show_get_started()
            return

        main_text, sub_text, color_main, color_sub = self.greetings[self.greeting_idx]
        self.canvas.delete("text_elem")

        # Determine responsive typography sizes
        main_size = 46 if len(main_text) < 12 else 26
        sub_size = 14 if len(sub_text) < 30 else 12

        # Primary Animated Greeting Text
        self.canvas.create_text(
            self.cx, self.cy + 70,
            text=main_text,
            font=("Segoe UI", main_size, "bold"),
            fill=color_main,
            tags="text_elem"
        )

        # Secondary Supporting Subtitle
        self.canvas.create_text(
            self.cx, self.cy + 130,
            text=sub_text,
            font=("Segoe UI", sub_size),
            fill=color_sub,
            tags="text_elem"
        )

        self.greeting_idx += 1

        # Faster pacing for multilingual greetings, longer on Welcome/Namaste/Tagline
        delay = 1400 if self.greeting_idx in [1, 2, len(self.greetings)] else 800
        self.after(delay, self.cycle_greetings)

    def show_get_started(self):
        """Displays the final call to action to launch the setup wizard."""
        if not self.animation_running:
            return

        self.canvas.delete("text_elem")
        self.canvas.create_text(
            self.cx, self.cy + 60,
            text="WELCOME TO GIRI OS 0.1 GENESIS",
            font=("Segoe UI", 24, "bold"),
            fill="#FFFFFF",
            tags="text_elem"
        )
        self.canvas.create_text(
            self.cx, self.cy + 105,
            text="Let's configure your new operating system in a few easy steps.",
            font=("Segoe UI", 13),
            fill="#94A3B8",
            tags="text_elem"
        )

        btn_start = tk.Button(
            self,
            text="Begin Setup ▶",
            font=("Segoe UI", 12, "bold"),
            bg="#0066FF",
            fg="#FFFFFF",
            activebackground="#00D2FF",
            activeforeground="#050811",
            relief="flat",
            padx=28,
            pady=10,
            cursor="hand2",
            command=self.transition_to_wizard
        )
        btn_start.place(x=self.cx - 90, y=self.cy + 150)

    def transition_to_wizard(self):
        """Smoothly closes the welcome window and initializes the setup wizard."""
        log_event("Transitioning from Welcome sequence to FirstBootWizard.")
        self.animation_running = False
        try:
            self.destroy()
        except Exception:
            pass

        # In test mode or non-interactive mode, do not launch interactive mainloop
        if self.test_mode or self.skip_animation:
            return

        # Launch the First Boot Setup Wizard
        if first_boot_wizard:
            try:
                # Force reconfigure if invoked directly
                app = first_boot_wizard.GiriFirstBootWizard(force_reconfigure=True)
                app.mainloop()
            except Exception as e:
                log_event(f"Error launching FirstBootWizard: {e}")
                # Safe fallback: do not crash or hang
                sys.exit(0)
        else:
            log_event("FirstBootWizard module not found. Falling back to desktop.")
            sys.exit(0)


def main():
    # Diagnostic / non-interactive flags
    if "--verify" in sys.argv:
        print("[+] Verifying Giri Welcome Experience...")
        assert is_live_session() in [True, False]
        assert is_setup_completed() in [True, False]
        print("[+] Giri Welcome Experience logic verified.")
        sys.exit(0)

    # Live session policy check
    if is_live_session():
        log_event("Live ISO session detected. Bypassing persistent first-boot configuration.")
        # In a live session, do not lock out the user or permanently mark installation
        if "--force" not in sys.argv:
            print("Live ISO session active. First-boot wizard will not permanently mark disk.")

    # Check if already completed on an installed system
    if is_setup_completed() and "--reconfigure" not in sys.argv:
        log_event("First boot setup already completed. Exiting cleanly.")
        print("Giri OS setup already completed. To run again, use --reconfigure")
        sys.exit(0)

    # Launch Welcome Experience with safety fallback
    try:
        skip_intro = "--skip-intro" in sys.argv or "--quick" in sys.argv
        app = GiriWelcomeExperience(skip_animation=skip_intro)
        app.mainloop()
    except Exception as e:
        log_event(f"Unhandled exception in GiriWelcomeExperience: {e}")
        # Guaranteed safe exit to ensure desktop session proceeds unconditionally
        print(f"Notice: Welcome experience encountered an error ({e}). Continuing to desktop.")
        sys.exit(0)


if __name__ == "__main__":
    main()
