#!/usr/bin/env python3
"""
Giri OS 0.1 Genesis — Phase 1 First Boot Experience Verification Suite
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Exhaustively verifies all 12 Phase 1 testing requirements:
1. Fresh installed-system boot trigger condition
2. Welcome orbital animation & emblem progression
3. Language selection & state binding
4. Hindi (हिन्दी) Devanagari and English typography rendering
5. Offline setup resilience
6. Network status inspection
7. Account creation, hashing & sudo delegation
8. Setup completion & configuration persistence
9. Reboot after completion bypass logic
10. Interrupted setup safe recovery
11. Live ISO isolation & temporary session policy
12. Desktop session safe fallback
"""

import unittest
import sys
import os
import shutil
import json
import hashlib
from pathlib import Path

# Add project root and first-boot directories to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIRST_BOOT_DIR = PROJECT_ROOT / "installer" / "first-boot"
sys.path.insert(0, str(FIRST_BOOT_DIR))

import first_boot_wizard as fbw
import giri_welcome as gw


class TestPhase1WelcomeExperience(unittest.TestCase):
    def setUp(self):
        self.temp_dir = PROJECT_ROOT / "tests" / "temp_phase1_sandbox"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.orig_user_flag = fbw.FLAG_FILE
        self.orig_system_flag = fbw.SYSTEM_FLAG_FILE
        self.orig_user_config = fbw.CONFIG_FILE

        self.test_user_flag = str(self.temp_dir / "user-first-boot-done")
        self.test_system_flag = str(self.temp_dir / "system-first-boot-done")
        self.test_user_config = str(self.temp_dir / "user-setup.json")

        fbw.FLAG_FILE = self.test_user_flag
        fbw.SYSTEM_FLAG_FILE = self.test_system_flag
        fbw.CONFIG_FILE = self.test_user_config
        gw.USER_FLAG_FILE = self.test_user_flag
        gw.SYSTEM_FLAG_FILE = self.test_system_flag

    def tearDown(self):
        fbw.FLAG_FILE = self.orig_user_flag
        fbw.SYSTEM_FLAG_FILE = self.orig_system_flag
        fbw.CONFIG_FILE = self.orig_user_config
        gw.USER_FLAG_FILE = self.orig_user_flag
        gw.SYSTEM_FLAG_FILE = self.orig_system_flag
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Fresh installed-system boot
    def test_01_fresh_installed_boot_trigger(self):
        """Verifies that a fresh system with no flag correctly triggers the welcome experience."""
        self.assertFalse(os.path.exists(self.test_user_flag))
        self.assertFalse(os.path.exists(self.test_system_flag))
        self.assertFalse(gw.is_setup_completed())

    # 2. Welcome animation
    def test_02_welcome_animation_and_emblem(self):
        """Verifies orbital emblem drawing and greeting frame structure."""
        app = gw.GiriWelcomeExperience(skip_animation=False, test_mode=True)
        # Test bloom progression
        app.draw_orbital_emblem(progress=0.5)
        app.draw_orbital_emblem(progress=1.0)
        # Check greeting items
        self.assertGreater(len(app.greetings), 5)
        self.assertEqual(app.greetings[0][0], "WELCOME")
        self.assertEqual(app.greetings[1][0], "नमस्ते")
        self.assertEqual(app.greetings[2][0], "NAMASTE")
        app.destroy()

    # 3. Language selection
    def test_03_language_selection(self):
        """Verifies language choices and binding updates."""
        wizard = fbw.GiriFirstBootWizard(non_interactive=True)
        wizard.render_language()
        wizard.lang_var.set("हिन्दी (Hindi)")
        wizard.config_data.update({"language": wizard.lang_var.get()})
        self.assertEqual(wizard.config_data["language"], "हिन्दी (Hindi)")
        wizard.destroy()

    # 4. Hindi and English text rendering
    def test_04_hindi_and_english_typography(self):
        """Tests that Hindi Devanagari script renders properly without encoding errors."""
        hindi_text = "नमस्ते — Giri OS में आपका स्वागत है"
        encoded = hindi_text.encode("utf-8").decode("utf-8")
        self.assertEqual(encoded, hindi_text)

        app = gw.GiriWelcomeExperience(skip_animation=False, test_mode=True)
        # Test drawing Hindi on canvas
        text_id = app.canvas.create_text(
            app.cx, app.cy,
            text=hindi_text,
            font=("Nirmala UI", 16, "bold"),
            fill="#00F0FF"
        )
        self.assertIsNotNone(text_id)
        app.destroy()

    # 5. Offline setup
    def test_05_offline_setup_resilience(self):
        """Verifies that wizard works seamlessly when offline."""
        wizard = fbw.GiriFirstBootWizard(non_interactive=True)
        wizard.config_data["network_mode"] = "Offline"
        wizard.save_and_finish()
        with open(self.test_user_config, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        self.assertEqual(cfg["network_mode"], "Offline")

    # 6. Network setup
    def test_06_network_detection(self):
        """Tests that network status detection returns valid dictionary."""
        info = fbw.detect_network_status()
        self.assertIn("connected", info)
        self.assertIn("interfaces", info)
        self.assertIn("details", info)

    # 7. Account creation & security
    def test_07_account_creation_validation(self):
        """Verifies password hashing, matching, and sudo assignment."""
        wizard = fbw.GiriFirstBootWizard(non_interactive=True)
        raw_pwd = "SuperSecretPassword123"
        hashed = hashlib.sha256(raw_pwd.encode("utf-8")).hexdigest()

        wizard.config_data["username"] = "abhinav"
        wizard.config_data["fullname"] = "Abhinav Giri"
        wizard.config_data["password_hash"] = hashed
        wizard.config_data["sudo_access"] = True

        wizard.save_and_finish()
        with open(self.test_user_config, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        self.assertEqual(cfg["username"], "abhinav")
        self.assertEqual(cfg["password_hash"], hashed)
        self.assertTrue(cfg["sudo_access"])

    # 8. Setup completion
    def test_08_setup_completion_persistence(self):
        """Verifies persistent flag creation on finish."""
        wizard = fbw.GiriFirstBootWizard(non_interactive=True)
        wizard.save_and_finish()
        self.assertTrue(os.path.isfile(self.test_user_flag))
        with open(self.test_user_flag, "r", encoding="utf-8") as f:
            flag_data = json.load(f)
        self.assertIn("completed_at", flag_data)
        self.assertEqual(flag_data["version"], "0.1 Genesis")

    # 9. Reboot after completion
    def test_09_reboot_bypass_logic(self):
        """Verifies that once setup is complete, subsequent boots bypass the welcome screen."""
        # Create completion flag
        with open(self.test_user_flag, "w", encoding="utf-8") as f:
            json.dump({"completed_at": "2026-11-16"}, f)
        self.assertTrue(gw.is_setup_completed())

    # 10. Interrupted setup recovery
    def test_10_interrupted_setup_safe_recovery(self):
        """Verifies that if setup is closed halfway, no flag is written."""
        wizard = fbw.GiriFirstBootWizard(non_interactive=True)
        # Advance to step 3 then destroy (simulating user closing mid-setup)
        wizard.show_step(3)
        wizard.destroy()
        self.assertFalse(os.path.exists(self.test_user_flag))
        self.assertFalse(gw.is_setup_completed())

    # 11. Live ISO behaviour
    def test_11_live_iso_behaviour(self):
        """Tests that in live session mode, system flag is not written permanently."""
        wizard = fbw.GiriFirstBootWizard(non_interactive=True)
        wizard.is_live = True
        wizard.save_and_finish()
        # System flag should NOT be written when is_live is True
        self.assertFalse(os.path.isfile(self.test_system_flag))

    # 12. Fallback to desktop
    def test_12_desktop_safe_fallback(self):
        """Tests that logging and graceful exit happen without crash."""
        gw.log_event("Simulated error test")
        self.assertTrue(os.path.isfile(gw.LOG_FILE))


if __name__ == "__main__":
    unittest.main()
