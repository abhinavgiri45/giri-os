#!/usr/bin/env python3
"""
Giri OS 0.1 Genesis — Graphics, Boot & System Stabilization Test Suite
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Validates all 18 requirements from Part 10:
 1. Graphics hardware detection
 2. Intel legacy profile selection
 3. VirtualBox profile selection
 4. Modern GPU profile selection
 5. Missing driver handling
 6. Software-rendering fallback
 7. LightDM configuration
 8. Live-user consistency
 9. PAM autologin configuration
10. Giri session executable
11. Desktop dependency availability
12. Bootloader kernel paths
13. Initrd paths
14. Recovery entry
15. Safe Graphics entry
16. Standard Session entry
17. Plymouth configuration
18. Calamares safety configuration
"""

import unittest
import sys
import os
import re

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "hardware", "giri-hw"))
from detector import HardwareDetector


class TestGraphicsAndBootStabilization(unittest.TestCase):
    def setUp(self):
        self.detector = HardwareDetector()

    def test_01_graphics_hardware_detection(self):
        profile = self.detector.profile
        self.assertIn("gpu", profile)
        self.assertIn("graphics_profile", profile)
        gpu = profile["gpu"]
        self.assertIn("vendor", gpu)
        self.assertIn("driver", gpu)
        self.assertIn("vulkan_supported", gpu)
        self.assertIn("vulkan_details", gpu)
        self.assertIsInstance(gpu["vulkan_supported"], bool)

    def test_02_intel_legacy_profile_selection(self):
        # Mock Intel HD 2000 environment
        det = HardwareDetector()
        det.profile["gpu"] = {
            "model": "Intel 2nd Generation Core Processor Family Integrated Graphics [8086:0102]",
            "vendor": "Intel",
            "driver": "i915 (crocus)",
            "is_intel_legacy": True,
            "is_intel_hd_2000": True,
            "is_virtualbox": False,
            "is_nomodeset": False,
            "vulkan_supported": False,
            "vulkan_details": "No hardware Vulkan on Sandy Bridge.",
        }
        gfx_prof = det._evaluate_graphics_profile()
        self.assertEqual(gfx_prof["code"], "intel_legacy")
        self.assertEqual(gfx_prof["compositor"], "picom-xrender")
        self.assertEqual(gfx_prof["wine_backend"], "wined3d")
        self.assertFalse(det.profile["gpu"]["vulkan_supported"])

    def test_03_virtualbox_profile_selection(self):
        # Mock VirtualBox VBoxSVGA / VMware SVGA II environment
        det = HardwareDetector()
        det.profile["gpu"] = {
            "model": "VMware SVGA II Adapter [15ad:0405] in Oracle VirtualBox",
            "vendor": "VirtualBox",
            "driver": "vmwgfx",
            "is_intel_legacy": False,
            "is_intel_hd_2000": False,
            "is_virtualbox": True,
            "is_nomodeset": False,
            "vulkan_supported": False,
            "vulkan_details": "VirtualBox does not expose hardware Vulkan ICD.",
        }
        gfx_prof = det._evaluate_graphics_profile()
        self.assertEqual(gfx_prof["code"], "virtualbox")
        self.assertEqual(gfx_prof["compositor"], "none")
        self.assertEqual(gfx_prof["xorg_driver"], "vmware")
        self.assertEqual(gfx_prof["wine_backend"], "wined3d")

    def test_04_modern_gpu_profile_selection(self):
        # Mock modern GPU (e.g. AMD Radeon RX 6600 or NVIDIA RTX)
        det = HardwareDetector()
        det.profile["gpu"] = {
            "model": "Navi 23 [Radeon RX 6600 / 6600 XT] [1002:73ff]",
            "vendor": "AMD",
            "driver": "amdgpu",
            "is_intel_legacy": False,
            "is_intel_hd_2000": False,
            "is_virtualbox": False,
            "is_nomodeset": False,
            "vulkan_supported": True,
            "vulkan_details": "AMD RADV Vulkan driver available.",
        }
        gfx_prof = det._evaluate_graphics_profile()
        self.assertEqual(gfx_prof["code"], "modern")
        self.assertEqual(gfx_prof["compositor"], "picom-glx")
        self.assertEqual(gfx_prof["wine_backend"], "dxvk")
        self.assertTrue(gfx_prof["hardware_acceleration"])

    def test_05_missing_driver_handling(self):
        # Mock unknown / missing graphics driver
        det = HardwareDetector()
        det.profile["gpu"] = {
            "model": "Unrecognized Video Controller",
            "vendor": "Unknown",
            "driver": "Unknown",
            "is_intel_legacy": False,
            "is_intel_hd_2000": False,
            "is_virtualbox": False,
            "is_nomodeset": False,
            "vulkan_supported": False,
            "vulkan_details": "Unknown hardware.",
        }
        gfx_prof = det._evaluate_graphics_profile()
        self.assertIsNotNone(gfx_prof)
        self.assertIn("code", gfx_prof)

    def test_06_software_rendering_fallback(self):
        # Mock nomodeset / Safe Graphics fallback
        det = HardwareDetector()
        det.profile["gpu"] = {
            "model": "VESA VGA / Framebuffer",
            "vendor": "Generic",
            "driver": "fbdev / vesa",
            "is_intel_legacy": False,
            "is_intel_hd_2000": False,
            "is_virtualbox": False,
            "is_nomodeset": True,
            "vulkan_supported": False,
            "vulkan_details": "Safe Graphics mode active.",
        }
        gfx_prof = det._evaluate_graphics_profile()
        self.assertEqual(gfx_prof["code"], "software_rendering")
        self.assertEqual(gfx_prof["compositor"], "none")
        self.assertEqual(gfx_prof["xorg_driver"], "fbdev")
        self.assertFalse(gfx_prof["hardware_acceleration"])

    def test_07_lightdm_configuration(self):
        hook_path = os.path.join(ROOT_DIR, "build", "live-build", "config", "hooks", "live", "01-setup-giri-branding.hook.chroot")
        with open(hook_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("autologin-user=giri", content)
        self.assertIn("user-session=giri-space-classic", content)
        self.assertIn("display-setup-script=/usr/bin/giri-display-setup", content)

    def test_08_live_user_consistency(self):
        isolinux_path = os.path.join(ROOT_DIR, "boot", "isolinux", "isolinux.cfg")
        grub_path = os.path.join(ROOT_DIR, "boot", "grub", "grub.cfg")
        auto_config_path = os.path.join(ROOT_DIR, "build", "live-build", "auto", "config")

        with open(isolinux_path, "r", encoding="utf-8") as f:
            iso_content = f.read()
        with open(grub_path, "r", encoding="utf-8") as f:
            grub_content = f.read()
        with open(auto_config_path, "r", encoding="utf-8") as f:
            auto_content = f.read()

        self.assertIn("username=giri", iso_content)
        self.assertIn("hostname=giri-os", iso_content)
        self.assertIn("username=giri", grub_content)
        self.assertIn("hostname=giri-os", grub_content)
        self.assertIn("username=giri", auto_content)
        self.assertIn("hostname=giri-os", auto_content)

    def test_09_pam_autologin_configuration(self):
        hook_path = os.path.join(ROOT_DIR, "build", "live-build", "config", "hooks", "live", "01-setup-giri-branding.hook.chroot")
        with open(hook_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("groupadd -f -r autologin", content)
        self.assertIn("autologin", content)
        self.assertIn("/etc/sudoers.d/giri-live", content)

    def test_10_giri_session_executable(self):
        session_path = os.path.join(ROOT_DIR, "desktop", "giri-space", "session", "giri-session")
        self.assertTrue(os.path.isfile(session_path))
        with open(session_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue(content.startswith("#!/bin/sh"))
        self.assertIn("openbox", content)
        self.assertIn("plymouth --quit", content)
        self.assertIn("giri_space.py", content)

    def test_11_desktop_dependency_availability(self):
        desktop_list_path = os.path.join(ROOT_DIR, "build", "live-build", "config", "package-lists", "giri-desktop.list.chroot")
        with open(desktop_list_path, "r", encoding="utf-8") as f:
            pkgs = f.read().splitlines()
        clean_pkgs = [p.strip() for p in pkgs if p.strip() and not p.strip().startswith("#")]

        required = [
            "xorg",
            "xserver-xorg",
            "xserver-xorg-video-fbdev",
            "xserver-xorg-video-vesa",
            "xserver-xorg-video-vmware",
            "openbox",
            "lightdm",
            "feh",
            "dunst",
            "python3-tk",
            "python3-pil",
            "calamares",
        ]
        for req in required:
            self.assertIn(req, clean_pkgs, f"Required package '{req}' missing from giri-desktop.list.chroot")

    def test_12_bootloader_kernel_paths(self):
        isolinux_path = os.path.join(ROOT_DIR, "boot", "isolinux", "isolinux.cfg")
        grub_path = os.path.join(ROOT_DIR, "boot", "grub", "grub.cfg")

        with open(isolinux_path, "r", encoding="utf-8") as f:
            iso_content = f.read()
        with open(grub_path, "r", encoding="utf-8") as f:
            grub_content = f.read()

        self.assertIn("KERNEL /live/vmlinuz", iso_content)
        self.assertIn("/live/vmlinuz", grub_content)

    def test_13_bootloader_initrd_paths(self):
        isolinux_path = os.path.join(ROOT_DIR, "boot", "isolinux", "isolinux.cfg")
        grub_path = os.path.join(ROOT_DIR, "boot", "grub", "grub.cfg")

        with open(isolinux_path, "r", encoding="utf-8") as f:
            iso_content = f.read()
        with open(grub_path, "r", encoding="utf-8") as f:
            grub_content = f.read()

        self.assertIn("initrd=/live/initrd.img", iso_content)
        self.assertIn("/live/initrd.img", grub_content)

    def test_14_recovery_entry(self):
        isolinux_path = os.path.join(ROOT_DIR, "boot", "isolinux", "isolinux.cfg")
        grub_path = os.path.join(ROOT_DIR, "boot", "grub", "grub.cfg")

        with open(isolinux_path, "r", encoding="utf-8") as f:
            iso_content = f.read()
        with open(grub_path, "r", encoding="utf-8") as f:
            grub_content = f.read()

        self.assertIn("LABEL recovery", iso_content)
        self.assertIn("systemd.unit=rescue.target", iso_content)
        self.assertIn("System Recovery Mode", grub_content)
        self.assertIn("systemd.unit=rescue.target", grub_content)

    def test_15_safe_graphics_entry(self):
        isolinux_path = os.path.join(ROOT_DIR, "boot", "isolinux", "isolinux.cfg")
        grub_path = os.path.join(ROOT_DIR, "boot", "grub", "grub.cfg")

        with open(isolinux_path, "r", encoding="utf-8") as f:
            iso_content = f.read()
        with open(grub_path, "r", encoding="utf-8") as f:
            grub_content = f.read()

        self.assertIn("LABEL classic", iso_content)
        self.assertIn("nomodeset", iso_content)
        self.assertIn("giri.profile=classic", iso_content)
        self.assertIn("plymouth.enable=0", iso_content)

        self.assertIn("Safe Graphics Mode", grub_content)
        self.assertIn("nomodeset", grub_content)
        self.assertIn("giri.profile=classic", grub_content)
        self.assertIn("plymouth.enable=0", grub_content)

    def test_16_standard_session_entry(self):
        isolinux_path = os.path.join(ROOT_DIR, "boot", "isolinux", "isolinux.cfg")
        grub_path = os.path.join(ROOT_DIR, "boot", "grub", "grub.cfg")

        with open(isolinux_path, "r", encoding="utf-8") as f:
            iso_content = f.read()
        with open(grub_path, "r", encoding="utf-8") as f:
            grub_content = f.read()

        self.assertIn("Standard Session", iso_content)
        self.assertIn("boot=live components", iso_content)
        self.assertIn("Standard Session", grub_content)
        self.assertIn("boot=live components", grub_content)

    def test_17_plymouth_configuration(self):
        plymouth_dir = os.path.join(ROOT_DIR, "boot", "plymouth", "giri-genesis")
        self.assertTrue(os.path.isdir(plymouth_dir))
        theme_file = os.path.join(plymouth_dir, "giri-genesis.plymouth")
        self.assertTrue(os.path.isfile(theme_file))
        with open(theme_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Name=Giri Genesis", content)

    def test_18_calamares_safety_configuration(self):
        calamares_settings = os.path.join(ROOT_DIR, "installer", "calamares", "settings.conf")
        self.assertTrue(os.path.isfile(calamares_settings))
        with open(calamares_settings, "r", encoding="utf-8") as f:
            content = f.read()
        # Verify Calamares prompts before execution and does not bypass confirmation
        self.assertIn("prompt-install: true", content)
        self.assertIn("branding: giri", content)


if __name__ == "__main__":
    unittest.main()
