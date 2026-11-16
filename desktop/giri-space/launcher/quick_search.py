#!/usr/bin/env python3
"""
Giri OS — Quick Search & Universal HUD Command Runner (Giri Search)
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Provides a keyboard-driven universal HUD search bar for Giri OS 0.1 Genesis.
Features:
- Instant search across installed applications (.desktop files)
- Built-in safe mathematical calculator (evaluates expressions on the fly)
- Direct system action shortcuts (Lock, Logout, Reboot, Shutdown, Control Center, Terminal)
- Settings and configuration deep-linking
- Deep midnight navy and electric cyan aesthetic
- Non-blocking execution and full keyboard navigation (Up, Down, Enter, Escape)
"""

import sys
import os
import math
import subprocess
import glob
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    print("Warning: Tkinter is required for Giri Quick Search.")
    sys.exit(0)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))


def safe_calculate(expr):
    """Safely evaluates basic mathematical expressions without arbitrary code execution."""
    cleaned = expr.strip().lower()
    # Allowed tokens
    allowed_chars = set("0123456789+-*/()., %^ e pi sqrt sin cos tan log abs")
    # Simple sanity check
    if not all(c in allowed_chars for c in cleaned):
        return None

    # Replace syntax tokens
    calc_expr = cleaned.replace("^", "**")
    
    # Safe namespace
    safe_dict = {
        "__builtins__": None,
        "pi": math.pi,
        "e": math.e,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log10,
        "ln": math.log,
        "abs": abs
    }

    try:
        # Evaluate within isolated math scope
        val = eval(calc_expr, {"__builtins__": None}, safe_dict)
        if isinstance(val, (int, float)):
            # Format nicely
            if isinstance(val, float) and val.is_integer():
                val = int(val)
            return f"= {val}"
    except Exception:
        pass
    return None


def get_installed_applications():
    """Parses standard XDG .desktop files to index installed applications."""
    apps = []
    seen_names = set()

    search_dirs = [
        "/usr/share/applications",
        "/usr/local/share/applications",
        os.path.expanduser("~/.local/share/applications"),
        os.path.join(ROOT_DIR, "desktop", "giri-space", "shortcuts"),
        os.path.join(ROOT_DIR, "desktop", "giri-space", "session")
    ]

    for sdir in search_dirs:
        if not os.path.isdir(sdir):
            continue
        for dpath in glob.glob(os.path.join(sdir, "*.desktop")):
            try:
                name, exec_cmd, icon, comment = None, None, None, ""
                with open(dpath, "r", encoding="utf-8", errors="ignore") as f:
                    in_desktop_entry = False
                    for line in f:
                        line = line.strip()
                        if line == "[Desktop Entry]":
                            in_desktop_entry = True
                            continue
                        elif line.startswith("[") and in_desktop_entry:
                            break
                        if in_desktop_entry and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip()
                            if k == "Name" and not name:
                                name = v
                            elif k == "Exec" and not exec_cmd:
                                # Strip field codes (%u, %f, etc.)
                                exec_cmd = " ".join([token for token in v.split() if not token.startswith("%")])
                            elif k == "Icon" and not icon:
                                icon = v
                            elif k == "Comment" and not comment:
                                comment = v
                            elif k == "NoDisplay" and v.lower() == "true":
                                name = None
                                break

                if name and exec_cmd and name.lower() not in seen_names:
                    seen_names.add(name.lower())
                    apps.append({
                        "name": name,
                        "cmd": exec_cmd,
                        "type": "Application",
                        "comment": comment or "System Application",
                        "icon": icon or "application-x-executable"
                    })
            except Exception:
                continue

    # Default core built-in Giri OS shortcuts
    core_actions = [
        {"name": "Giri Control Center", "cmd": "giri-control", "type": "System Tool", "comment": "System settings, wallpapers, display & hardware"},
        {"name": "Giri Hardware Center", "cmd": "giri-hw", "type": "System Tool", "comment": "Hardware detection, GPU tiers & diagnostics"},
        {"name": "Giri Gaming Governor", "cmd": "giri-game", "type": "Gaming Tool", "comment": "CPU performance tuning & game mode"},
        {"name": "Giri Compatibility Bridge", "cmd": "giri-bridge", "type": "Compatibility Tool", "comment": "Windows PE runner & Wine prefix manager"},
        {"name": "Giri Screen Snip", "cmd": "giri-snip", "type": "Utility", "comment": "Screen capture, active window & region snip"},
        {"name": "Giri Night Light", "cmd": "giri-nightlight", "type": "Display", "comment": "Circadian blue light filter & eye comfort"},
        {"name": "Lock Screen", "cmd": "xflock4", "type": "Session Action", "comment": "Lock desktop display session"},
        {"name": "Reboot System", "cmd": "systemctl reboot", "type": "Session Action", "comment": "Restart computer"},
        {"name": "Power Off System", "cmd": "systemctl poweroff", "type": "Session Action", "comment": "Shut down computer"}
    ]

    for item in core_actions:
        if item["name"].lower() not in seen_names:
            apps.append(item)
            seen_names.add(item["name"].lower())

    return apps


class GiriQuickSearch(tk.Tk):
    def __init__(self, non_interactive=False):
        super().__init__()
        self.non_interactive = non_interactive

        self.title("Giri Quick Search")
        self.configure(bg="#0B0F19")
        self.overrideredirect(True)  # Frameless HUD window
        self.attributes("-topmost", True)

        self.width = 680
        self.height = 420
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        x = (self.screen_width - self.width) // 2
        y = int(self.screen_height * 0.22)  # Position upper center of screen
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")

        self.apps = get_installed_applications()
        self.results = []
        self.selected_idx = 0

        self.setup_ui()
        self.bind_events()
        self.update_search("")

        if self.non_interactive:
            self.withdraw()

    def setup_ui(self):
        # Outer Border Box
        self.outer_frame = tk.Frame(self, bg="#0B0F19", highlightthickness=2, highlightbackground="#00F0FF")
        self.outer_frame.pack(fill="both", expand=True)

        # Search Bar Header
        self.search_frame = tk.Frame(self.outer_frame, bg="#111827", height=64)
        self.search_frame.pack(fill="x", padx=4, pady=4)

        # Search Icon (Lens / G indicator)
        self.lbl_icon = tk.Label(
            self.search_frame,
            text="🔍",
            font=("Segoe UI", 16),
            fg="#00F0FF",
            bg="#111827"
        )
        self.lbl_icon.pack(side="left", padx=(16, 8), pady=12)

        # Search Entry Field
        self.entry_query = tk.Entry(
            self.search_frame,
            font=("Segoe UI", 16),
            bg="#111827",
            fg="#FFFFFF",
            insertbackground="#00F0FF",
            relief="flat"
        )
        self.entry_query.pack(side="left", fill="x", expand=True, padx=8, pady=12)
        self.entry_query.focus_set()
        self.entry_query.bind("<KeyRelease>", self.on_query_change)

        # Esc hint badge
        self.lbl_badge = tk.Label(
            self.search_frame,
            text="ESC to close",
            font=("Segoe UI", 9, "bold"),
            fg="#94A3B8",
            bg="#1F2937",
            padx=8,
            pady=3
        )
        self.lbl_badge.pack(side="right", padx=16)

        # Results List Box Container
        self.results_frame = tk.Frame(self.outer_frame, bg="#0B0F19")
        self.results_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        self.canvas_list = tk.Canvas(self.results_frame, bg="#0B0F19", highlightthickness=0)
        self.canvas_list.pack(fill="both", expand=True)

    def bind_events(self):
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Down>", self.move_selection_down)
        self.bind("<Up>", self.move_selection_up)
        self.bind("<Return>", self.execute_selection)

    def on_query_change(self, event=None):
        query = self.entry_query.get().strip()
        self.update_search(query)

    def update_search(self, query):
        self.selected_idx = 0
        self.results = []

        # 1. Calculator Check
        calc_result = safe_calculate(query)
        if calc_result:
            self.results.append({
                "name": calc_result,
                "cmd": None,
                "type": "Calculator",
                "comment": f"Math expression: {query}",
                "is_calc": True
            })

        # 2. Match Applications & Actions
        q_lower = query.lower()
        if q_lower:
            # Name starts with
            starts = [a for a in self.apps if a["name"].lower().startswith(q_lower)]
            # Name contains
            contains = [a for a in self.apps if q_lower in a["name"].lower() and a not in starts]
            # Comment contains
            comments = [a for a in self.apps if q_lower in a["comment"].lower() and a not in starts and a not in contains]
            matched = starts + contains + comments
        else:
            # Show default top actions
            matched = self.apps[:8]

        self.results.extend(matched[:7])
        self.render_results()

    def render_results(self):
        self.canvas_list.delete("all")
        if not self.results:
            self.canvas_list.create_text(
                self.width // 2, 80,
                text="No matching applications, commands, or math expressions found.",
                font=("Segoe UI", 11),
                fill="#64748B"
            )
            return

        item_height = 46
        y = 6
        for idx, item in enumerate(self.results):
            is_selected = (idx == self.selected_idx)
            bg_col = "#1E293B" if is_selected else "#0B0F19"
            accent_col = "#00F0FF" if is_selected else "#FFFFFF"
            sub_col = "#38BDF8" if is_selected else "#94A3B8"
            tag_col = "#C084FC" if item.get("type") in ["System Tool", "Gaming Tool"] else "#64748B"

            # Selection rectangle
            self.canvas_list.create_rectangle(
                8, y, self.width - 16, y + item_height - 4,
                fill=bg_col, outline="#00F0FF" if is_selected else "",
                width=1 if is_selected else 0
            )

            # Indicator dot
            dot_col = "#00F0FF" if is_selected else "#334155"
            self.canvas_list.create_oval(
                22, y + 17, 28, y + 23,
                fill=dot_col, outline=""
            )

            # Item Name
            self.canvas_list.create_text(
                40, y + 14,
                text=item["name"],
                font=("Segoe UI", 11, "bold" if is_selected else "normal"),
                fill=accent_col,
                anchor="w"
            )

            # Item Comment / Subtitle
            self.canvas_list.create_text(
                40, y + 30,
                text=item["comment"],
                font=("Segoe UI", 9),
                fill=sub_col,
                anchor="w"
            )

            # Type badge on right
            self.canvas_list.create_text(
                self.width - 32, y + 20,
                text=item.get("type", "App"),
                font=("Segoe UI", 9, "bold"),
                fill=tag_col,
                anchor="e"
            )

            y += item_height

    def move_selection_down(self, event=None):
        if self.results:
            self.selected_idx = (self.selected_idx + 1) % len(self.results)
            self.render_results()

    def move_selection_up(self, event=None):
        if self.results:
            self.selected_idx = (self.selected_idx - 1) % len(self.results)
            self.render_results()

    def execute_selection(self, event=None):
        if not self.results:
            return
        item = self.results[self.selected_idx]
        cmd = item.get("cmd")
        
        # If calculator result, copy to clipboard
        if item.get("is_calc"):
            val_text = item["name"].replace("= ", "")
            try:
                self.clipboard_clear()
                self.clipboard_append(val_text)
            except Exception:
                pass
            self.destroy()
            return

        if cmd:
            self.destroy()
            try:
                # Launch asynchronously
                subprocess.Popen(cmd, shell=True)
            except Exception as e:
                print(f"Error launching {cmd}: {e}")


def main():
    if "--verify" in sys.argv:
        print("[+] Verifying Giri Quick Search...")
        apps = get_installed_applications()
        assert len(apps) > 0
        assert safe_calculate("2 + 2") == "= 4"
        assert safe_calculate("sqrt(16)") == "= 4"
        assert safe_calculate("1024 * 768") == "= 786432"
        assert safe_calculate("import os") is None
        print(f"[+] Verified {len(apps)} applications indexed. Calculator checks passed.")
        sys.exit(0)

    app = GiriQuickSearch()
    app.mainloop()


if __name__ == "__main__":
    main()
