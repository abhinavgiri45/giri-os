#!/usr/bin/env python3
"""
Giri Bridge — Windows Application Execution Engine (Wine & Prefix Manager)
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Manages isolated WINEPREFIX containers, detects Wine installation,
configures 32-bit and 64-bit environments, and executes Windows applications
with automatic Intel HD 2000 OpenGL (wined3d) graphics routing.
"""

import sys
import os
import shutil
import subprocess
import json

# Import local analyzer
sys.path.insert(0, os.path.dirname(__file__))
from analyzer import PEAnalyzer


class WineRunner:
    def __init__(self, base_prefix_dir=None):
        if not base_prefix_dir:
            home = os.path.expanduser("~")
            self.base_prefix_dir = os.path.join(home, ".giri", "bridge", "prefixes")
        else:
            self.base_prefix_dir = base_prefix_dir

        self.wine_bin = shutil.which("wine") or shutil.which("wine64")
        self.winetricks_bin = shutil.which("winetricks")
        self.wineboot_bin = shutil.which("wineboot")
        self.is_wine_installed = bool(self.wine_bin)

    def get_status(self):
        return {
            "wine_installed": self.is_wine_installed,
            "wine_binary": self.wine_bin,
            "winetricks_available": bool(self.winetricks_bin),
            "prefix_root": self.base_prefix_dir,
            "subsystem": "Wine / Proton Multiarch Runner"
        }

    def prepare_prefix(self, prefix_name="default", arch="win64"):
        """
        Creates and initializes an isolated WINEPREFIX container.
        """
        prefix_path = os.path.join(self.base_prefix_dir, prefix_name)
        os.makedirs(prefix_path, exist_ok=True)

        env = os.environ.copy()
        env["WINEPREFIX"] = prefix_path
        env["WINEARCH"] = arch

        # If on Intel HD 2000 or legacy GPU, force OpenGL translation
        env["WINE_D3D_CONFIG"] = "renderer=gl"
        env["PROTON_USE_WINED3D"] = "1"

        if self.wineboot_bin:
            try:
                subprocess.run([self.wineboot_bin, "-u"], env=env, check=True, capture_output=True, timeout=60)
            except Exception as e:
                return {"success": False, "error": str(e), "prefix_path": prefix_path}

        return {"success": True, "prefix_path": prefix_path, "arch": arch}

    def launch(self, executable_path, prefix_name="default", custom_env=None):
        """
        Executes a Windows .exe or .msi inside the designated prefix container.
        """
        if not os.path.isfile(executable_path):
            return {"success": False, "error": f"File not found: {executable_path}"}

        analyzer = PEAnalyzer(executable_path)
        is_64bit = analyzer.report.get("is_64bit", True)
        arch = "win64" if is_64bit else "win32"

        prefix_res = self.prepare_prefix(prefix_name, arch=arch)
        if not prefix_res["success"] and self.is_wine_installed:
            return prefix_res

        prefix_path = os.path.join(self.base_prefix_dir, prefix_name)
        env = os.environ.copy()
        env["WINEPREFIX"] = prefix_path
        env["WINEARCH"] = arch
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
                "target_prefix": prefix_path
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
                "command": cmd
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    runner = WineRunner()
    print(json.dumps(runner.get_status(), indent=2))
