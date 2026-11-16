#!/usr/bin/env python3
"""
Giri OS Hardware Profiler & Tier Detection Engine
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Inspects CPU, RAM, GPU, Storage, and Peripheral subsystems.
Automatically recommends 'Giri Modern' or 'Giri Classic' desktop profiles.
Provides specific driver guidance for legacy graphics such as Intel HD 2000.
"""

import sys
import os
import platform
import subprocess
import json
import shutil


class HardwareDetector:
    def __init__(self):
        self.os_type = platform.system()
        self.profile = {}
        self.detect_all()

    def detect_all(self):
        self.profile["os"] = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }
        self.profile["cpu"] = self._detect_cpu()
        self.profile["ram"] = self._detect_ram()
        self.profile["gpu"] = self._detect_gpu()
        self.profile["storage"] = self._detect_storage()
        self.profile["tier"] = self._evaluate_tier()
        self.profile["diagnostics"] = self._generate_diagnostics()

    def _detect_cpu(self):
        cpu_info = {
            "model": platform.processor() or "Unknown CPU",
            "cores_logical": os.cpu_count() or 1,
            "architecture": platform.machine(),
            "avx_supported": False,
            "sse4_2_supported": False,
        }

        if self.os_type == "Linux":
            try:
                with open("/proc/cpuinfo", "r") as f:
                    content = f.read()
                    for line in content.splitlines():
                        if "model name" in line:
                            cpu_info["model"] = line.split(":", 1)[1].strip()
                            break
                    cpu_info["avx_supported"] = "avx" in content
                    cpu_info["sse4_2_supported"] = "sse4_2" in content
            except Exception:
                pass
        elif self.os_type == "Windows":
            try:
                # Query WMI on Windows
                cmd = "wmic cpu get name,NumberOfCores,NumberOfLogicalProcessors /format:list"
                out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in out.splitlines():
                    if line.startswith("Name="):
                        cpu_info["model"] = line.split("=", 1)[1].strip()
                    elif line.startswith("NumberOfCores="):
                        val = line.split("=", 1)[1].strip()
                        if val.isdigit():
                            cpu_info["cores_physical"] = int(val)
            except Exception:
                pass

        return cpu_info

    def _detect_ram(self):
        ram_info = {"total_gb": 8.0, "estimated_free_gb": 4.0}
        if self.os_type == "Linux":
            try:
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            kb = int(line.split()[1])
                            ram_info["total_gb"] = round(kb / (1024 * 1024), 2)
                        elif line.startswith("MemAvailable:"):
                            kb = int(line.split()[1])
                            ram_info["estimated_free_gb"] = round(kb / (1024 * 1024), 2)
            except Exception:
                pass
        elif self.os_type == "Windows":
            try:
                cmd = "wmic computersystem get TotalPhysicalMemory /format:list"
                out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in out.splitlines():
                    if line.startswith("TotalPhysicalMemory="):
                        bytes_val = int(line.split("=", 1)[1].strip())
                        ram_info["total_gb"] = round(bytes_val / (1024**3), 2)
            except Exception:
                pass
        return ram_info

    def _detect_gpu(self):
        gpu_info = {
            "model": "Generic / Integrated Graphics",
            "vendor": "Unknown",
            "driver": "Unknown",
            "opengl_supported": "Unknown",
            "vulkan_supported": False,
            "is_intel_hd_2000": False,
        }

        if self.os_type == "Linux":
            try:
                lspci_out = subprocess.check_output("lspci -nn | grep -i vga", shell=True, text=True, stderr=subprocess.DEVNULL)
                gpu_info["model"] = lspci_out.strip()
                if "8086:0102" in lspci_out or "HD Graphics 2000" in lspci_out:
                    gpu_info["vendor"] = "Intel"
                    gpu_info["is_intel_hd_2000"] = True
                    gpu_info["vulkan_supported"] = False
                    gpu_info["opengl_supported"] = "OpenGL 3.1 (Mesa crocus)"
                    gpu_info["driver"] = "i915 / crocus"
            except Exception:
                pass
        elif self.os_type == "Windows":
            try:
                cmd = "wmic path win32_VideoController get caption,DriverVersion /format:list"
                out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in out.splitlines():
                    if line.startswith("Caption="):
                        val = line.split("=", 1)[1].strip()
                        gpu_info["model"] = val
                        if "Intel" in val:
                            gpu_info["vendor"] = "Intel"
                        if "HD Graphics 2000" in val or "Intel(R) HD Graphics" in val:
                            gpu_info["is_intel_hd_2000"] = True
                            gpu_info["vulkan_supported"] = False
                    elif line.startswith("DriverVersion="):
                        gpu_info["driver"] = line.split("=", 1)[1].strip()
            except Exception:
                pass

        return gpu_info

    def _detect_storage(self):
        storage_info = {
            "type": "HDD / SATA",
            "is_rotational": True,
            "free_space_gb": 0.0,
        }
        try:
            total, used, free = shutil.disk_usage(".")
            storage_info["free_space_gb"] = round(free / (1024**3), 2)
            storage_info["total_space_gb"] = round(total / (1024**3), 2)
        except Exception:
            pass
        return storage_info

    def _evaluate_tier(self):
        """
        Determines whether the system should run 'Giri Modern' or 'Giri Classic'.
        """
        reasons = []
        is_intel_hd_2000 = self.profile["gpu"].get("is_intel_hd_2000", False)
        total_ram = self.profile["ram"].get("total_gb", 8.0)
        is_rotational = self.profile["storage"].get("is_rotational", False)

        if is_intel_hd_2000:
            reasons.append("Intel HD 2000 detected (OpenGL 3.1 max, no hardware Vulkan).")
        if total_ram < 6.0:
            reasons.append(f"Physical memory ({total_ram} GB) is below 6 GB threshold.")

        if reasons:
            return {
                "profile_name": "Giri Classic",
                "code": "classic",
                "recommended": True,
                "reasons": reasons,
                "compositor_effects": "Minimal (No backdrop blur, reduced animation speed, low CPU overhead)",
            }
        else:
            return {
                "profile_name": "Giri Modern",
                "code": "modern",
                "recommended": True,
                "reasons": ["Hardware satisfies modern GPU and memory requirements."],
                "compositor_effects": "Full (Glassmorphism, orbital transitions, smooth window snapping)",
            }

    def _generate_diagnostics(self):
        diag = []
        if self.profile["gpu"].get("is_intel_hd_2000", False):
            diag.append(
                "Intel HD 2000 Graphics Note: Direct3D applications under Wine will automatically "
                "use the native Mesa OpenGL translation layer (wined3d) rather than DXVK."
            )
            diag.append(
                "Video Acceleration: Supported via i965-va-driver (H.264 up to 1080p hardware decode)."
            )
        free_gb = self.profile["storage"].get("free_space_gb", 0)
        if free_gb < 15.0:
            diag.append(
                f"Warning: Low disk space ({free_gb} GB free). Full ISO compilation requires at least 15-20 GB."
            )
        else:
            diag.append(f"Storage: {free_gb} GB free space available. Sufficient for Giri OS development.")
        return diag

    def print_summary(self):
        print("=" * 68)
        print("       GIRI OS HARDWARE PROFILER & ADAPTATION ENGINE")
        print("=" * 68)
        print(f" CPU Model:         {self.profile['cpu']['model']}")
        print(f" CPU Cores:         {self.profile['cpu']['cores_logical']} Logical")
        print(f" Memory (RAM):      {self.profile['ram']['total_gb']} GB Total")
        print(f" Storage Free:      {self.profile['storage'].get('free_space_gb', 'N/A')} GB Free")
        print(f" GPU Device:        {self.profile['gpu']['model']}")
        print(f" Graphics Driver:   {self.profile['gpu']['driver']}")
        print(f" Vulkan Hardware:   {'Supported' if self.profile['gpu']['vulkan_supported'] else 'Not Supported (Mesa LLVMpipe fallback)'}")
        print("-" * 68)
        tier = self.profile["tier"]
        print(f" RECOMMENDED PROFILE: {tier['profile_name'].upper()}")
        print(f" Compositor Tuning:   {tier['compositor_effects']}")
        if tier["reasons"]:
            print(" Profile Rationale:")
            for r in tier["reasons"]:
                print(f"   • {r}")
        print("-" * 68)
        print(" HARDWARE DIAGNOSTICS & ADVICE:")
        for d in self.profile["diagnostics"]:
            print(f"   ℹ {d}")
        print("=" * 68)


if __name__ == "__main__":
    detector = HardwareDetector()
    if "--json" in sys.argv:
        print(json.dumps(detector.profile, indent=2))
    elif "--tier" in sys.argv:
        print(detector.profile["tier"]["code"])
    elif "--test" in sys.argv:
        assert detector.profile["tier"]["code"] in ["classic", "modern"]
        print("Hardware detector test passed.")
    else:
        detector.print_summary()
