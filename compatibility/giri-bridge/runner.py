#!/usr/bin/env python3
"""
Giri Bridge — Windows Application Execution Engine & Prefix Manager
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Manages isolated WINEPREFIX containers, detects Wine installation,
configures 32-bit and 64-bit environments, and executes Windows applications
with automatic Intel HD 2000 OpenGL (wined3d) graphics routing.
Enforces realistic compatibility checks before launch.
"""

import sys
import os
import shutil
import subprocess
import json
import time

# Import local analyzer
sys.path.insert(0, os.path.dirname(__file__))
from analyzer import PEAnalyzer


class WineRunner:
    def __init__(self, base_prefix_dir=None):
        if not base_prefix_dir:
            home = os.path.expanduser("~")
            self.base_prefix_dir = os.path.join(home, ".local", "share", "giri-bridge", "prefixes")
        else:
            self.base_prefix_dir = base_prefix_dir

        self.wine_bin = shutil.which("wine") or shutil.which("wine64")
        self.winetricks_bin = shutil.which("winetricks")
        self.wineboot_bin = shutil.which("wineboot")
        self.wineserver_bin = shutil.which("wineserver")
        self.is_wine_installed = bool(self.wine_bin)

    def get_status(self):
        """Returns comprehensive status of Wine environment and prefix storage."""
        wine_version = None
        if self.wine_bin:
            try:
                out = subprocess.run([self.wine_bin, "--version"], capture_output=True, text=True, timeout=5)
                wine_version = out.stdout.strip()
            except Exception:
                wine_version = "Installed (version query failed)"

        prefixes = self.list_prefixes()

        return {
            "wine_installed": self.is_wine_installed,
            "wine_binary": self.wine_bin,
            "wine_version": wine_version,
            "winetricks_available": bool(self.winetricks_bin),
            "prefix_root": self.base_prefix_dir,
            "managed_prefixes_count": len(prefixes),
            "prefixes": prefixes,
            "subsystem": "Giri Bridge (Wine & Proton Translation Layer)",
            "disclaimer": "Giri Bridge uses Wine translation. It does not provide 100% Windows compatibility."
        }

    def list_prefixes(self):
        """Lists all existing prefixes in the prefix directory."""
        if not os.path.isdir(self.base_prefix_dir):
            return []

        results = []
        for entry in os.listdir(self.base_prefix_dir):
            p = os.path.join(self.base_prefix_dir, entry)
            if os.path.isdir(p):
                # Check architecture
                system_reg = os.path.join(p, "system.reg")
                arch = "Unknown"
                if os.path.isfile(system_reg):
                    try:
                        with open(system_reg, "r", encoding="utf-8", errors="ignore") as f:
                            first_few = f.read(500)
                            if "#arch=win64" in first_few:
                                arch = "win64"
                            elif "#arch=win32" in first_few:
                                arch = "win32"
                    except Exception:
                        pass

                results.append({
                    "name": entry,
                    "path": p,
                    "arch": arch,
                    "exists": True
                })
        return results

    def create_prefix(self, prefix_name="default", arch="win64"):
        """Creates and initializes an isolated WINEPREFIX container."""
        prefix_path = os.path.join(self.base_prefix_dir, prefix_name)
        os.makedirs(prefix_path, exist_ok=True)

        env = os.environ.copy()
        env["WINEPREFIX"] = prefix_path
        env["WINEARCH"] = arch

        # Force OpenGL translation for legacy hardware
        env["WINE_D3D_CONFIG"] = "renderer=gl"
        env["PROTON_USE_WINED3D"] = "1"

        if self.wineboot_bin:
            try:
                subprocess.run([self.wineboot_bin, "-u"], env=env, check=True, capture_output=True, timeout=60)
            except Exception as e:
                return {"success": False, "error": str(e), "prefix_path": prefix_path}

        return {"success": True, "prefix_path": prefix_path, "arch": arch}

    def clean_prefix(self, prefix_name="default"):
        """Terminates wineserver processes and clears temp files for a prefix."""
        prefix_path = os.path.join(self.base_prefix_dir, prefix_name)
        if not os.path.isdir(prefix_path):
            return {"success": False, "error": f"Prefix '{prefix_name}' does not exist."}

        if self.wineserver_bin:
            env = os.environ.copy()
            env["WINEPREFIX"] = prefix_path
            try:
                subprocess.run([self.wineserver_bin, "-k"], env=env, timeout=10)
            except Exception:
                pass

        # Clear tmp in prefix
        tmp_dir = os.path.join(prefix_path, "drive_c", "users", os.environ.get("USER", "root"), "Temp")
        if os.path.isdir(tmp_dir):
            try:
                shutil.rmtree(tmp_dir, ignore_errors=True)
                os.makedirs(tmp_dir, exist_ok=True)
            except Exception:
                pass

        return {"success": True, "prefix_path": prefix_path, "message": "Prefix cleaned and processes stopped."}

    def delete_prefix(self, prefix_name):
        """Safely removes a prefix container."""
        if not prefix_name or prefix_name in [".", "..", "/"]:
            return {"success": False, "error": "Invalid prefix name."}

        prefix_path = os.path.join(self.base_prefix_dir, prefix_name)
        if not os.path.isdir(prefix_path):
            return {"success": False, "error": f"Prefix '{prefix_name}' does not exist."}

        # Kill any active wineserver first
        self.clean_prefix(prefix_name)

        try:
            shutil.rmtree(prefix_path)
            return {"success": True, "deleted_prefix": prefix_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def launch(self, executable_path, prefix_name="default", custom_env=None, force=False):
        """
        Analyzes and executes a Windows .exe or .msi inside the designated prefix container.
        Refuses to run unsupported binaries (anti-cheat, kernel drivers) unless forced.
        """
        if not os.path.isfile(executable_path):
            return {"success": False, "error": f"File not found: {executable_path}"}

        analyzer = PEAnalyzer(executable_path)
        is_64bit = analyzer.report.get("is_64bit", True)
        tier = analyzer.report.get("compatibility_tier", "Unknown")
        arch = "win64" if is_64bit else "win32"

        # Check compatibility tier
        if tier == "Unsupported" and not force:
            return {
                "success": False,
                "error": f"Application is Unsupported: {analyzer.report.get('tier_description')}",
                "analysis": analyzer.report,
                "blocked_by_policy": True
            }

        prefix_res = self.create_prefix(prefix_name, arch=arch)
        if not prefix_res["success"] and self.is_wine_installed:
            return prefix_res

        prefix_path = os.path.join(self.base_prefix_dir, prefix_name)
        env = os.environ.copy()
        env["WINEPREFIX"] = prefix_path
        env["WINEARCH"] = arch

        # Enforce OpenGL fallback for Intel HD 2000
        env["WINE_D3D_CONFIG"] = "renderer=gl"
        env["PROTON_USE_WINED3D"] = "1"
        if custom_env:
            env.update(custom_env)

        if not self.is_wine_installed:
            # Running on host without Wine (e.g. Windows dev host)
            return {
                "success": False,
                "error": "Wine binary not found on host. Giri Bridge requires Wine to execute Windows applications.",
                "analysis": analyzer.report,
                "target_prefix": prefix_path,
                "simulated_launch": True
            }

        cmd = [self.wine_bin]
        if executable_path.lower().endswith(".msi"):
            cmd = [self.wine_bin, "msiexec", "/i", executable_path]
        else:
            cmd = [self.wine_bin, executable_path]

        try:
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return {
                "success": True,
                "pid": proc.pid,
                "prefix": prefix_path,
                "arch": arch,
                "command": cmd,
                "compatibility_tier": tier
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    runner = WineRunner()

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Giri Bridge — Windows Application Execution Engine & Prefix Manager")
        print("Usage:")
        print("  python runner.py --status                Show Wine runner status and prefixes")
        print("  python runner.py --list                  List managed Wine prefixes")
        print("  python runner.py --create <name> [arch]  Create new prefix (win64|win32)")
        print("  python runner.py --clean <name>          Clean prefix and terminate wineserver")
        print("  python runner.py --delete <name>         Delete prefix container")
        print("  python runner.py --analyze <path>        Analyze Windows PE binary compatibility")
        print("  python runner.py --launch <path> [name]  Launch Windows binary in prefix")
        print("  python runner.py --test                  Run automated self-tests")
        sys.exit(0)

    if "--test" in sys.argv:
        print("[TEST] Running Giri Bridge Runner self-tests...")
        # 1. Status check
        st = runner.get_status()
        assert isinstance(st, dict)
        assert "wine_installed" in st

        # 2. Mock prefix management
        temp_dir = os.path.join("tests", "mock_prefixes")
        mock_runner = WineRunner(base_prefix_dir=temp_dir)
        c_res = mock_runner.create_prefix("test_prefix", arch="win64")
        assert c_res["success"] is True
        assert os.path.isdir(os.path.join(temp_dir, "test_prefix"))

        # List
        plist = mock_runner.list_prefixes()
        assert len(plist) >= 1
        assert any(p["name"] == "test_prefix" for p in plist)

        # Delete
        d_res = mock_runner.delete_prefix("test_prefix")
        assert d_res["success"] is True
        assert not os.path.exists(os.path.join(temp_dir, "test_prefix"))

        # Clean up temp
        shutil.rmtree(temp_dir, ignore_errors=True)

        print("[TEST] Giri Bridge Runner self-tests passed successfully.")
        sys.exit(0)

    if "--status" in sys.argv:
        print(json.dumps(runner.get_status(), indent=2))
        sys.exit(0)

    if "--list" in sys.argv:
        print(json.dumps(runner.list_prefixes(), indent=2))
        sys.exit(0)

    if "--analyze" in sys.argv:
        idx = sys.argv.index("--analyze")
        if idx + 1 < len(sys.argv):
            an = PEAnalyzer(sys.argv[idx + 1])
            print(json.dumps(an.report, indent=2))
        else:
            print("Error: Specify binary path to analyze.")
        sys.exit(0)

    print(json.dumps(runner.get_status(), indent=2))
