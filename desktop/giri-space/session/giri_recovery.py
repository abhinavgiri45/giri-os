#!/usr/bin/env python3
"""
Giri Space — Session Recovery & Diagnostic Interface
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Provides an emergency recovery dialog and fail-safe environment
whenever the main Giri Space desktop shell encounters an unexpected crash.
Ensures the user is NEVER trapped in a black screen.
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import ttk


def get_recent_log_lines(log_file, n=20):
    if not os.path.isfile(log_file):
        return ["(No previous session log found)"]
    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return [l.rstrip() for l in lines[-n:]]
    except Exception as e:
        return [f"Error reading session log: {e}"]


class GiriRecoveryDialog(tk.Tk):
    def __init__(self, log_path=None):
        super().__init__()
        self.title("Giri Space — Session Recovery")
        self.geometry("680x480")
        self.minsize(560, 400)
        self.configure(bg="#0a0e1a")

        self.log_path = log_path or os.path.expanduser("~/.local/share/giri/logs/session.log")

        # Center on screen
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        # Header Banner
        header = tk.Frame(self, bg="#121829", height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title_lbl = tk.Label(
            header,
            text="Giri Space — Session Recovery",
            font=("DejaVu Sans", 14, "bold"),
            fg="#00d2ff",
            bg="#121829"
        )
        title_lbl.pack(side="left", padx=16, pady=8)

        status_lbl = tk.Label(
            header,
            text="DIAGNOSTIC RESCUE MODE",
            font=("DejaVu Sans", 9, "bold"),
            fg="#ff5555",
            bg="#121829"
        )
        status_lbl.pack(side="right", padx=16)

        # Content Area
        content = tk.Frame(self, bg="#0a0e1a", padx=20, pady=16)
        content.pack(fill="both", expand=True)

        msg_lbl = tk.Label(
            content,
            text="The Giri Space graphical shell stopped unexpectedly.\n"
                 "A recovery session has been started to prevent a black screen.\n"
                 "Select an option below or open a terminal to inspect system state.",
            font=("DejaVu Sans", 10),
            fg="#c2d5ee",
            bg="#0a0e1a",
            justify="left"
        )
        msg_lbl.pack(anchor="w", pady=(0, 12))

        # Log Frame
        log_frame = tk.LabelFrame(
            content,
            text=f" Recent Diagnostic Output ({os.path.basename(self.log_path)}) ",
            font=("DejaVu Sans", 9, "bold"),
            fg="#7928ca",
            bg="#0a0e1a",
            padx=8,
            pady=8
        )
        log_frame.pack(fill="both", expand=True, pady=(0, 16))

        self.log_text = tk.Text(
            log_frame,
            bg="#05070f",
            fg="#00ffcc",
            insertbackground="#00d2ff",
            font=("DejaVu Sans Mono", 8),
            wrap="none",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#1b253b"
        )
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        log_lines = get_recent_log_lines(self.log_path, 25)
        self.log_text.insert("end", "\n".join(log_lines) + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

        # Action Buttons
        btn_bar = tk.Frame(self, bg="#121829", height=54, padx=16)
        btn_bar.pack(fill="x", side="bottom")
        btn_bar.pack_propagate(False)

        # Terminal Button
        tk.Button(
            btn_bar,
            text="Open Terminal",
            font=("DejaVu Sans", 9, "bold"),
            bg="#1b2a47",
            fg="#00d2ff",
            activebackground="#2a3f68",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.open_terminal
        ).pack(side="left", padx=4, pady=10)

        # Safe Graphics Retry Button
        tk.Button(
            btn_bar,
            text="Retry (Safe Graphics)",
            font=("DejaVu Sans", 9, "bold"),
            bg="#203a30",
            fg="#00ff88",
            activebackground="#2c5244",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.retry_safe_graphics
        ).pack(side="left", padx=4, pady=10)

        # Reboot Button
        tk.Button(
            btn_bar,
            text="Reboot System",
            font=("DejaVu Sans", 9),
            bg="#3a2a10",
            fg="#ffaa44",
            activebackground="#543c16",
            activeforeground="#ffffff",
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.reboot
        ).pack(side="right", padx=4, pady=10)

        # Power Off Button
        tk.Button(
            btn_bar,
            text="Power Off",
            font=("DejaVu Sans", 9),
            bg="#3a1418",
            fg="#ff5555",
            activebackground="#541c22",
            activeforeground="#ffffff",
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.power_off
        ).pack(side="right", padx=4, pady=10)

    def open_terminal(self):
        for term in ["kitty", "xterm", "xfce4-terminal"]:
            try:
                subprocess.Popen([term])
                return
            except FileNotFoundError:
                continue

    def retry_safe_graphics(self):
        self.destroy()
        # Exit code 42 indicates request to restart in safe graphics mode
        sys.exit(42)

    def reboot(self):
        try:
            subprocess.run(["systemctl", "reboot"], check=False)
        except Exception:
            try:
                subprocess.run(["reboot"], check=False)
            except Exception:
                pass
        self.destroy()
        sys.exit(0)

    def power_off(self):
        try:
            subprocess.run(["systemctl", "poweroff"], check=False)
        except Exception:
            try:
                subprocess.run(["poweroff"], check=False)
            except Exception:
                pass
        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    log_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = GiriRecoveryDialog(log_file)
    app.mainloop()
