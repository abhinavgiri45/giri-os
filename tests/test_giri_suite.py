#!/usr/bin/env python3
"""
Giri OS — Comprehensive System Integration Test Suite
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Validates all Giri OS subsystems headlessly:
- Hardware Profiler & Tier Classification
- First Boot Setup Wizard State & Zero Telemetry
- Giri Space Desktop Shell (Classic & Modern Profiles)
- Giri Bridge Windows PE Header Parser
- Giri Gaming Governor & Safe Fallback Engine
- Giri Update Cryptographic Integrity Verifier
- Wallpaper Collection Integrity & Default Assignment
"""

import unittest
import sys
import os
import hashlib
import json
import importlib.util
from PIL import Image

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def load_module(mod_name, rel_path):
    full_path = os.path.join(ROOT_DIR, rel_path)
    spec = importlib.util.spec_from_file_location(mod_name, full_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# Load components
hw_mod = load_module("detector", "hardware/giri-hw/detector.py")
wizard_mod = load_module("first_boot_wizard", "installer/first-boot/first_boot_wizard.py")
space_mod = load_module("giri_space", "desktop/giri-space/shell/giri_space.py")
bridge_mod = load_module("analyzer", "compatibility/giri-bridge/analyzer.py")
gaming_mod = load_module("governor", "gaming/giri-gaming/governor.py")
updater_mod = load_module("client", "updater/giri-update/client.py")
control_mod = load_module("control_center", "desktop/giri-space/control-center/control_center.py")

HardwareDetector = hw_mod.HardwareDetector
GiriFirstBootWizard = wizard_mod.GiriFirstBootWizard
GiriSpaceDesktop = space_mod.GiriSpaceDesktop
PEAnalyzer = bridge_mod.PEAnalyzer
GiriGameGovernor = gaming_mod.GiriGameGovernor
GiriUpdateClient = updater_mod.GiriUpdateClient
GiriControlCenter = control_mod.GiriControlCenter


class TestGiriOSCore(unittest.TestCase):
    def test_01_hardware_profiler(self):
        detector = HardwareDetector()
        profile = detector.profile
        self.assertIn("cpu", profile)
        self.assertIn("ram", profile)
        self.assertIn("gpu", profile)
        self.assertIn("tier", profile)
        self.assertIn(profile["tier"]["code"], ["classic", "modern"])

    def test_02_first_boot_wizard_privacy(self):
        wizard = GiriFirstBootWizard(non_interactive=True)
        self.assertFalse(wizard.config_data["privacy_telemetry"])
        self.assertFalse(wizard.config_data["privacy_crash_reports"])
        wizard.destroy()

    def test_03_giri_bridge_pe_analyzer(self):
        analyzer = PEAnalyzer()
        test_pe = os.path.join(os.path.dirname(__file__), "test_sample.exe")
        analyzer.create_mock_pe(test_pe, is_64bit=True)
        report = analyzer.analyze(test_pe)
        self.assertTrue(report["valid_pe"])
        self.assertTrue(report["is_64bit"])
        self.assertEqual(report["recommended_prefix"], "win64")
        if os.path.exists(test_pe):
            os.remove(test_pe)

    def test_04_giri_gaming_governor(self):
        governor = GiriGameGovernor()
        res = governor.activate_game_mode()
        self.assertEqual(res["status"], "ACTIVE")
        self.assertIn("anti_cheat_advisory", res)
        deact = governor.deactivate_game_mode()
        self.assertEqual(deact["status"], "INACTIVE")

    def test_05_giri_update_crypto_verification(self):
        client = GiriUpdateClient(root_dir=ROOT_DIR)
        payload = b"Giri OS 0.1 Update Signature Payload"
        valid_sha = hashlib.sha256(payload).hexdigest()
        self.assertTrue(client.verify_payload(payload, valid_sha))
        self.assertFalse(client.verify_payload(payload, "invalid_sha256_hash"))

    def test_06_giri_space_desktop_shell(self):
        desktop_classic = GiriSpaceDesktop(profile="classic", non_interactive=True)
        self.assertEqual(desktop_classic.profile, "classic")
        desktop_classic.destroy()

        desktop_modern = GiriSpaceDesktop(profile="modern", non_interactive=True)
        self.assertEqual(desktop_modern.profile, "modern")
        desktop_modern.destroy()

    def test_07_wallpaper_collection(self):
        wp_dir = os.path.join(ROOT_DIR, "branding", "wallpapers")
        manifest_path = os.path.join(wp_dir, "wallpapers.json")
        self.assertTrue(os.path.isfile(manifest_path))

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        self.assertGreaterEqual(len(manifest), 10)

        # Confirm giri-origin is default
        default_wp = [w for w in manifest if w.get("is_default")]
        self.assertEqual(len(default_wp), 1)
        self.assertEqual(default_wp[0]["filename"], "giri-origin.png")

        # Verify each image file exists, is valid PNG, and has 16:9 ratio
        for wp in manifest:
            img_path = os.path.join(wp_dir, wp["filename"])
            self.assertTrue(os.path.isfile(img_path), f"Missing wallpaper: {img_path}")

            with Image.open(img_path) as im:
                w, h = im.size
                ratio = w / h
                self.assertAlmostEqual(ratio, 16.0 / 9.0, delta=0.02)

            thumb_path = os.path.join(wp_dir, "thumbnails", wp["filename"])
            self.assertTrue(os.path.isfile(thumb_path), f"Missing thumbnail: {thumb_path}")


if __name__ == "__main__":
    unittest.main()
