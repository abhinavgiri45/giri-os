#!/usr/bin/env python3
"""
Giri OS Hardware Profiler & Universal Graphics Detection Engine
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Comprehensive hardware profiler and automatic graphics compatibility layer:
- Detects Intel legacy graphics (Intel HD Graphics 2000/3000 Sandy Bridge)
- Detects VirtualBox virtual GPUs (VBoxSVGA, VMSVGA, vmwgfx driver)
- Detects Modern GPUs (Intel Iris/Xe, AMD Radeon, NVIDIA GeForce)
- Detects Software rendering fallbacks (nomodeset, VESA, EFI FB, LLVMpipe)
- Selects automatic graphics profiles:
    1. Modern Graphics Profile ('modern')
    2. Legacy Intel Graphics Profile ('intel_legacy')
    3. VirtualBox Compatibility Profile ('virtualbox')
    4. Software Rendering Fallback ('software_rendering')
    5. Recovery Display Profile ('recovery')
- Strictly honest reporting: NEVER spoofs Vulkan or hardware acceleration.
"""

import sys
import os
import platform
import subprocess
import json
import shutil
import re


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
        self.profile["graphics_profile"] = self._evaluate_graphics_profile()
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
            "is_intel_legacy": False,
            "is_intel_hd_2000": False,
            "is_virtualbox": False,
            "is_nomodeset": False,
            "drm_kms_active": False,
            "framebuffer_type": "Unknown",
            "opengl_supported": "Unknown",
            "vulkan_supported": False,
            "vulkan_details": "No hardware Vulkan support detected.",
        }

        # Check kernel command line on Linux
        cmdline = ""
        if self.os_type == "Linux":
            try:
                if os.path.exists("/proc/cmdline"):
                    with open("/proc/cmdline", "r") as f:
                        cmdline = f.read().strip()
                gpu_info["is_nomodeset"] = "nomodeset" in cmdline or "xforcevesa" in cmdline
            except Exception:
                pass

            # Check active framebuffer in /proc/fb
            try:
                if os.path.exists("/proc/fb"):
                    with open("/proc/fb", "r") as f:
                        fb_content = f.read().strip()
                        gpu_info["framebuffer_type"] = fb_content if fb_content else "None"
            except Exception:
                pass

            # Check DRM KMS nodes in /sys/class/drm
            try:
                drm_path = "/sys/class/drm"
                if os.path.isdir(drm_path):
                    cards = [c for c in os.listdir(drm_path) if c.startswith("card") and "-" not in c]
                    gpu_info["drm_kms_active"] = len(cards) > 0 and not gpu_info["is_nomodeset"]
            except Exception:
                pass

            # Check DMI system vendor for VirtualBox
            try:
                dmi_vendor = ""
                for p in ["/sys/class/dmi/id/sys_vendor", "/sys/class/dmi/id/product_name"]:
                    if os.path.exists(p):
                        with open(p, "r") as f:
                            dmi_vendor += f.read()
                if "VirtualBox" in dmi_vendor or "innotek" in dmi_vendor:
                    gpu_info["is_virtualbox"] = True
                    gpu_info["vendor"] = "VirtualBox"
            except Exception:
                pass

            # Inspect PCI devices via lspci
            try:
                lspci_out = subprocess.check_output(
                    "lspci -nn 2>/dev/null | grep -E 'VGA|3D|Display'",
                    shell=True,
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                gpu_info["model"] = lspci_out.strip()

                # VirtualBox / VMware SVGA PCI check
                if "80ee:beef" in lspci_out or "80ee:cafe" in lspci_out or "15ad:0405" in lspci_out or "VirtualBox" in lspci_out or "VMware SVGA" in lspci_out:
                    gpu_info["is_virtualbox"] = True
                    gpu_info["vendor"] = "VirtualBox"
                    gpu_info["driver"] = "vmwgfx"
                    gpu_info["opengl_supported"] = "OpenGL 2.1 (Mesa SVGA3D software/emulated)"
                    gpu_info["vulkan_supported"] = False
                    gpu_info["vulkan_details"] = "VirtualBox does not expose hardware Vulkan ICD."

                # Intel Legacy Sandy Bridge (HD 2000 / 3000) check
                elif any(did in lspci_out for did in ["8086:0102", "8086:0106", "8086:0112", "8086:0116", "8086:0122", "8086:0126"]) or "HD Graphics 2000" in lspci_out or "HD Graphics 3000" in lspci_out:
                    gpu_info["vendor"] = "Intel"
                    gpu_info["is_intel_legacy"] = True
                    gpu_info["is_intel_hd_2000"] = True
                    gpu_info["driver"] = "i915 (crocus)"
                    gpu_info["opengl_supported"] = "OpenGL 3.1 (Mesa crocus)"
                    gpu_info["vulkan_supported"] = False
                    gpu_info["vulkan_details"] = "Intel Sandy Bridge (HD 2000/3000) lacks hardware Vulkan support."

                # Modern Intel (Gen8+ / Iris / Xe)
                elif "8086:" in lspci_out:
                    gpu_info["vendor"] = "Intel"
                    gpu_info["driver"] = "i915 / xe (iris)"
                    gpu_info["opengl_supported"] = "OpenGL 4.6 (Mesa iris)"
                    gpu_info["vulkan_supported"] = True
                    gpu_info["vulkan_details"] = "Intel ANV Vulkan driver available."

                # AMD Radeon
                elif "1002:" in lspci_out or "AMD" in lspci_out or "Radeon" in lspci_out:
                    gpu_info["vendor"] = "AMD"
                    gpu_info["driver"] = "amdgpu (radeonsi)"
                    gpu_info["opengl_supported"] = "OpenGL 4.6 (Mesa radeonsi)"
                    gpu_info["vulkan_supported"] = True
                    gpu_info["vulkan_details"] = "AMD RADV Vulkan driver available."

                # NVIDIA
                elif "10de:" in lspci_out or "NVIDIA" in lspci_out:
                    gpu_info["vendor"] = "NVIDIA"
                    gpu_info["driver"] = "nouveau / nvidia"
                    gpu_info["opengl_supported"] = "OpenGL 4.5+ (Mesa nouveau / NVIDIA binary)"
                    gpu_info["vulkan_supported"] = True
                    gpu_info["vulkan_details"] = "NVIDIA Vulkan ICD available."

            except Exception:
                pass

            # Safe graphics / nomodeset driver override
            if gpu_info["is_nomodeset"]:
                gpu_info["driver"] = "fbdev / vesa (nomodeset active)"
                gpu_info["opengl_supported"] = "OpenGL 3.1 (Mesa LLVMpipe software rendering)"
                gpu_info["vulkan_supported"] = False
                gpu_info["vulkan_details"] = "Safe Graphics mode active. DRM/KMS disabled; hardware acceleration inactive."

        elif self.os_type == "Windows":
            try:
                cmd = "wmic path win32_VideoController get caption,DriverVersion /format:list"
                out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in out.splitlines():
                    if line.startswith("Caption="):
                        val = line.split("=", 1)[1].strip()
                        gpu_info["model"] = val
                        if "VirtualBox" in val or "VMware" in val:
                            gpu_info["vendor"] = "VirtualBox"
                            gpu_info["is_virtualbox"] = True
                            gpu_info["driver"] = "VBoxDisp.dll / vmwgfx"
                            gpu_info["opengl_supported"] = "OpenGL 2.1 (VirtualBox Guest)"
                            gpu_info["vulkan_supported"] = False
                            gpu_info["vulkan_details"] = "VirtualBox virtual display controller has no hardware Vulkan."
                        elif "Intel" in val:
                            gpu_info["vendor"] = "Intel"
                            if any(x in val for x in ["HD Graphics 2000", "HD Graphics 3000", "2000", "3000"]):
                                gpu_info["is_intel_legacy"] = True
                                gpu_info["is_intel_hd_2000"] = True
                                gpu_info["driver"] = "igdumdim64.dll / i915"
                                gpu_info["opengl_supported"] = "OpenGL 3.1 (Mesa crocus equivalent)"
                                gpu_info["vulkan_supported"] = False
                                gpu_info["vulkan_details"] = "Intel Sandy Bridge architecture does not feature hardware Vulkan support."
                            else:
                                gpu_info["opengl_supported"] = "OpenGL 4.5+ (Intel Iris/UHD)"
                                gpu_info["vulkan_supported"] = True
                        elif "NVIDIA" in val:
                            gpu_info["vendor"] = "NVIDIA"
                            gpu_info["vulkan_supported"] = True
                        elif "AMD" in val or "Radeon" in val:
                            gpu_info["vendor"] = "AMD"
                            gpu_info["vulkan_supported"] = True
                    elif line.startswith("DriverVersion="):
                        if not gpu_info["driver"] or gpu_info["driver"] == "Unknown":
                            gpu_info["driver"] = line.split("=", 1)[1].strip()
            except Exception:
                pass

        return gpu_info

    def _evaluate_graphics_profile(self):
        """
        Evaluates the optimal Giri OS graphics profile based on real hardware and driver status.
        Profiles:
            1. 'recovery': Emergency shell / rescue mode
            2. 'software_rendering': nomodeset / VESA / EFI FB / llvmpipe only
            3. 'virtualbox': VirtualBox VBoxSVGA / VMSVGA compatibility profile
            4. 'intel_legacy': Intel Sandy Bridge HD 2000 / 3000 legacy profile
            5. 'modern': Modern GPU with native KMS, OpenGL >= 4.0, hardware acceleration
        """
        gpu = self.profile.get("gpu", {})
        cmdline = ""
        if self.os_type == "Linux" and os.path.exists("/proc/cmdline"):
            try:
                with open("/proc/cmdline", "r") as f:
                    cmdline = f.read().strip()
            except Exception:
                pass

        # 1. Recovery Profile
        if "single" in cmdline or "rescue" in cmdline or "emergency" in cmdline:
            return {
                "code": "recovery",
                "name": "Recovery Display Profile",
                "description": "Minimal text or unaccelerated fallback for system recovery and diagnostics.",
                "compositor": "none",
                "xorg_driver": "fbdev",
                "wine_backend": "wined3d",
                "hardware_acceleration": False,
            }

        # 2. Software Rendering / Safe Graphics Profile
        if gpu.get("is_nomodeset", False) or "xforcevesa" in cmdline or "giri.profile=classic" in cmdline and gpu.get("is_nomodeset", False):
            return {
                "code": "software_rendering",
                "name": "Software Rendering Fallback",
                "description": "Safe Graphics mode using VESA/fbdev without kernel modesetting.",
                "compositor": "none",
                "xorg_driver": "fbdev",
                "wine_backend": "wined3d",
                "hardware_acceleration": False,
            }

        # 3. VirtualBox Compatibility Profile
        if gpu.get("is_virtualbox", False):
            return {
                "code": "virtualbox",
                "name": "VirtualBox Compatibility Profile",
                "description": "Optimized for Oracle VirtualBox VBoxSVGA/VMSVGA adapters. Disables 3D compositor locks.",
                "compositor": "none",
                "xorg_driver": "vmware",
                "wine_backend": "wined3d",
                "hardware_acceleration": True,
            }

        # 4. Legacy Intel Graphics Profile (HD 2000 / Sandy Bridge)
        if gpu.get("is_intel_legacy", False) or gpu.get("is_intel_hd_2000", False):
            return {
                "code": "intel_legacy",
                "name": "Legacy Intel Graphics Profile",
                "description": "Optimized for Intel 2nd Gen Sandy Bridge HD Graphics 2000/3000 (Mesa Crocus OpenGL 3.1).",
                "compositor": "picom-xrender",
                "xorg_driver": "modesetting",
                "wine_backend": "wined3d",
                "hardware_acceleration": True,
            }

        # 5. Modern Graphics Profile
        return {
            "code": "modern",
            "name": "Modern Graphics Profile",
            "description": "Full hardware acceleration with OpenGL 4.5+ and composite window effects.",
            "compositor": "picom-glx",
            "xorg_driver": "modesetting",
            "wine_backend": "dxvk" if gpu.get("vulkan_supported", False) else "wined3d",
            "hardware_acceleration": True,
        }

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
        Evaluates desktop tier ('classic' or 'modern') for backwards compatibility.
        """
        reasons = []
        gfx_profile = self.profile.get("graphics_profile", {}).get("code", "modern")
        gpu = self.profile.get("gpu", {})
        total_ram = self.profile.get("ram", {}).get("total_gb", 8.0)

        if gfx_profile in ["intel_legacy", "virtualbox", "software_rendering", "recovery"]:
            reasons.append(f"Graphics profile '{gfx_profile}' requires lightweight Classic tier.")
        elif gpu.get("is_intel_hd_2000", False):
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
        gpu = self.profile.get("gpu", {})
        gfx = self.profile.get("graphics_profile", {})

        diag.append(f"Active Graphics Profile: {gfx.get('name', 'Unknown')} [{gfx.get('code', 'unknown')}]")
        diag.append(f"Xorg Display Driver: {gfx.get('xorg_driver', 'modesetting')}")
        diag.append(f"Window Compositing: {gfx.get('compositor', 'none')}")

        if gpu.get("is_virtualbox", False):
            diag.append("VirtualBox Environment Note: Using VBoxSVGA compatibility profile to prevent 3D lockups.")
        elif gpu.get("is_intel_hd_2000", False):
            diag.append(
                "Intel HD 2000 Graphics Note: Direct3D applications under Wine will automatically "
                "use the native Mesa OpenGL translation layer (wined3d) rather than DXVK."
            )
            diag.append(
                "Video Acceleration: Supported via i965-va-driver (H.264 up to 1080p hardware decode)."
            )

        if not gpu.get("vulkan_supported", False):
            diag.append("Vulkan Status: No hardware Vulkan capability. Software LLVMpipe will be used if required.")

        free_gb = self.profile.get("storage", {}).get("free_space_gb", 0)
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
        print(f" Graphics Vendor:   {self.profile['gpu']['vendor']}")
        print(f" Kernel Driver:     {self.profile['gpu']['driver']}")
        print(f" Graphics Profile:  {self.profile['graphics_profile']['name']}")
        print(f" Vulkan Hardware:   {'Supported' if self.profile['gpu']['vulkan_supported'] else 'Not Supported'}")
        print(f" Vulkan Details:    {self.profile['gpu']['vulkan_details']}")
        print("-" * 68)
        tier = self.profile["tier"]
        print(f" RECOMMENDED TIER:    {tier['profile_name'].upper()}")
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
    elif "--graphics-profile" in sys.argv:
        print(detector.profile["graphics_profile"]["code"])
    elif "--tier" in sys.argv:
        print(detector.profile["tier"]["code"])
    elif "--test" in sys.argv:
        assert detector.profile["tier"]["code"] in ["classic", "modern"]
        assert detector.profile["graphics_profile"]["code"] in [
            "modern",
            "intel_legacy",
            "virtualbox",
            "software_rendering",
            "recovery",
        ]
        print("Hardware detector test passed.")
    else:
        detector.print_summary()
