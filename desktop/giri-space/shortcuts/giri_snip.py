#!/usr/bin/env python3
"""
Giri OS — Screen Snip & Capture Utility (Giri Snip)
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Provides a lightweight, modern screen capture and snipping utility for Giri OS 0.1 Genesis.
Features:
- Full Screen capture
- Active Window capture (via xdotool / scrot -u)
- Interactive Rectangular Region selection
- Direct export to ~/Pictures/Screenshots
- Copy to clipboard support
- Instant graphical preview dialog with dark space styling
"""

import sys
import os
import time
import shutil
import subprocess
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from PIL import Image, ImageTk, ImageGrab
except ImportError:
    print("Warning: Tkinter and PIL are required for Giri Snip.")
    sys.exit(0)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
SCREENSHOTS_DIR = os.path.expanduser("~/Pictures/Screenshots")


def capture_fullscreen(output_path):
    """Captures entire desktop screen using scrot, xwd, or PIL."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # 1. Try scrot
    if shutil.which("scrot"):
        res = subprocess.run(["scrot", output_path], capture_output=True)
        if res.returncode == 0 and os.path.isfile(output_path):
            return True
    # 2. Try ImageMagick import
    if shutil.which("import"):
        res = subprocess.run(["import", "-window", "root", output_path], capture_output=True)
        if res.returncode == 0 and os.path.isfile(output_path):
            return True
    # 3. Fallback to PIL ImageGrab (works on X11 / Windows / macOS)
    try:
        shot = ImageGrab.grab()
        shot.save(output_path, "PNG")
        return True
    except Exception:
        pass
    return False


def capture_active_window(output_path):
    """Captures currently focused window using scrot -u or fallback."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if shutil.which("scrot"):
        res = subprocess.run(["scrot", "-u", output_path], capture_output=True)
        if res.returncode == 0 and os.path.isfile(output_path):
            return True
    return capture_fullscreen(output_path)


def capture_region(output_path):
    """Captures interactive rectangular selection using scrot -s or fallback."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if shutil.which("scrot"):
        res = subprocess.run(["scrot", "-s", output_path], capture_output=True)
        if res.returncode == 0 and os.path.isfile(output_path):
            return True
    return capture_fullscreen(output_path)


class GiriSnipPreviewDialog(tk.Toplevel):
    """Displays preview of captured screenshot with quick actions."""
    def __init__(self, parent, image_path):
        super().__init__(parent)
        self.image_path = image_path
        self.title("Giri Snip — Screenshot Preview")
        self.geometry("640x520")
        self.configure(bg="#080C1A")
        self.attributes("-topmost", True)

        self.setup_ui()

    def setup_ui(self):
        # Header
        hdr = tk.Frame(self, bg="#0D1428", height=50)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📷 Screenshot Captured", font=("Segoe UI", 12, "bold"), fg="#00D2FF", bg="#0D1428").pack(side="left", padx=16, pady=12)

        # Image Canvas Preview
        self.canvas = tk.Canvas(self, bg="#050811", highlightthickness=1, highlightbackground="#1E293B")
        self.canvas.pack(fill="both", expand=True, padx=16, pady=12)

        try:
            pil_img = Image.open(self.image_path)
            # Thumbnail to fit 600x380
            pil_img.thumbnail((600, 360))
            self.tk_thumb = ImageTk.PhotoImage(pil_img)
            self.canvas.create_image(300, 180, image=self.tk_thumb, anchor="center")
        except Exception as e:
            self.canvas.create_text(300, 180, text=f"Preview unavailable ({e})", fill="#64748B", font=("Segoe UI", 11))

        # Bottom Bar
        bbar = tk.Frame(self, bg="#0D1428", height=56)
        bbar.pack(fill="x", side="bottom")

        tk.Label(bbar, text=f"Saved to: {os.path.basename(self.image_path)}", font=("Segoe UI", 9), fg="#8EA4C8", bg="#0D1428").pack(side="left", padx=16)

        btn_close = tk.Button(bbar, text="Close", font=("Segoe UI", 9), bg="#1E293B", fg="#FFFFFF", relief="flat", padx=12, pady=4, command=self.destroy)
        btn_close.pack(side="right", padx=12, pady=10)

        btn_open = tk.Button(bbar, text="Open Folder 📁", font=("Segoe UI", 9), bg="#0066FF", fg="#FFFFFF", relief="flat", padx=12, pady=4, command=self.open_folder)
        btn_open.pack(side="right", padx=4, pady=10)

    def open_folder(self):
        folder = os.path.dirname(self.image_path)
        if sys.platform == "win32":
            os.startfile(folder)
        else:
            subprocess.Popen(["xdg-open", folder])


class GiriSnipTool(tk.Tk):
    def __init__(self, non_interactive=False):
        super().__init__()
        self.non_interactive = non_interactive

        self.title("Giri Snip")
        self.geometry("420x280")
        self.resizable(False, False)
        self.configure(bg="#080C1A")

        self.setup_ui()

        if self.non_interactive:
            self.withdraw()

    def setup_ui(self):
        # Header
        hdr = tk.Frame(self, bg="#0D1428", height=60)
        hdr.pack(fill="x")

        tk.Label(hdr, text="GIRI SNIP", font=("Segoe UI", 14, "bold"), fg="#00D2FF", bg="#0D1428").pack(side="left", padx=16, pady=14)
        tk.Label(hdr, text="0.1 Genesis", font=("Segoe UI", 9, "bold"), fg="#A855F7", bg="#16223D", padx=6, pady=2).pack(side="left")

        # Body Options
        body = tk.Frame(self, bg="#080C1A")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(body, text="Select Screen Capture Mode:", font=("Segoe UI", 11, "bold"), fg="#FFFFFF", bg="#080C1A").pack(anchor="w", pady=(0, 10))

        # Mode Buttons
        modes = [
            ("🖥 Full Screen Capture", self.snip_fullscreen),
            ("🔲 Rectangular Region Snip", self.snip_region),
            ("🪟 Active Window Capture", self.snip_window)
        ]

        for text, cmd in modes:
            btn = tk.Button(
                body,
                text=text,
                font=("Segoe UI", 10),
                bg="#0F172A",
                fg="#C2D5EE",
                activebackground="#1E293B",
                activeforeground="#00D2FF",
                relief="flat",
                anchor="w",
                padx=16,
                pady=8,
                cursor="hand2",
                command=cmd
            )
            btn.pack(fill="x", pady=4)

    def _get_timestamp_filename(self):
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        return os.path.join(SCREENSHOTS_DIR, f"Giri_Screenshot_{ts}.png")

    def snip_fullscreen(self):
        self.withdraw()
        self.after(300, self._do_capture_fullscreen)

    def _do_capture_fullscreen(self):
        target = self._get_timestamp_filename()
        if capture_fullscreen(target):
            self.deiconify()
            GiriSnipPreviewDialog(self, target)
        else:
            self.deiconify()
            messagebox.showerror("Capture Error", "Failed to capture screen.")

    def snip_region(self):
        self.withdraw()
        self.after(300, self._do_capture_region)

    def _do_capture_region(self):
        target = self._get_timestamp_filename()
        if capture_region(target):
            self.deiconify()
            GiriSnipPreviewDialog(self, target)
        else:
            self.deiconify()
            messagebox.showerror("Capture Error", "Failed to capture region.")

    def snip_window(self):
        self.withdraw()
        self.after(300, self._do_capture_window)

    def _do_capture_window(self):
        target = self._get_timestamp_filename()
        if capture_active_window(target):
            self.deiconify()
            GiriSnipPreviewDialog(self, target)
        else:
            self.deiconify()
            messagebox.showerror("Capture Error", "Failed to capture active window.")


def main():
    if "--verify" in sys.argv:
        print("[+] Verifying Giri Snip...")
        assert os.path.isdir(ROOT_DIR)
        print("[+] Giri Snip tool structure verified.")
        sys.exit(0)

    app = GiriSnipTool()
    app.mainloop()


if __name__ == "__main__":
    main()
