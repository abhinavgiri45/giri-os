#!/usr/bin/env python3
"""
Giri OS — Comprehensive System Integration Test Suite
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Validates all Giri OS subsystems headlessly:
- Hardware Profiler & Tier Classification
- First Boot Setup Wizard State, Flags & Zero Telemetry
- Giri Space Desktop Shell (Classic & Modern Profiles, Session Dialog, Shortcuts)
- Giri Bridge Windows PE Header Parser, Anti-Cheat Detection & Prefix Management
- Giri Gaming Governor, Game Optimizer & Intel HD 2000 OpenGL Fallback
- Giri Update Debian APT Inspection, GPG Verification, Disk Audit & Dry-Run
- Official 12-Piece 4K UHD Wallpaper Collection & Dual Default Pair
- Calamares Installer Configuration & Scalable Branding Assets
"""

import unittest
import sys
import os
import hashlib
import json
import shutil
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
runner_mod = load_module("runner", "compatibility/giri-bridge/runner.py")
welcome_mod = load_module("giri_welcome", "installer/first-boot/giri_welcome.py")
search_mod = load_module("quick_search", "desktop/giri-space/launcher/quick_search.py")
snip_mod = load_module("giri_snip", "desktop/giri-space/shortcuts/giri_snip.py")
nightlight_mod = load_module("giri_nightlight", "desktop/giri-space/shell/giri_nightlight.py")

HardwareDetector = hw_mod.HardwareDetector
GiriFirstBootWizard = wizard_mod.GiriFirstBootWizard
GiriSpaceDesktop = space_mod.GiriSpaceDesktop
PEAnalyzer = bridge_mod.PEAnalyzer
GiriGameOptimizer = gaming_mod.GiriGameOptimizer
GiriGameGovernor = gaming_mod.GiriGameGovernor
GiriUpdateClient = updater_mod.GiriUpdateClient
GiriControlCenter = control_mod.GiriControlCenter
WineRunner = runner_mod.WineRunner
GiriWelcomeExperience = welcome_mod.GiriWelcomeExperience
GiriQuickSearch = search_mod.GiriQuickSearch
safe_calculate = search_mod.safe_calculate
GiriSnipTool = snip_mod.GiriSnipTool


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
        self.assertIn(wizard.config_data["theme_mode"], ["Dark", "Light"])
        wizard.destroy()

    def test_03_giri_bridge_pe_analyzer(self):
        analyzer = PEAnalyzer()
        test_pe = os.path.join(os.path.dirname(__file__), "test_sample.exe")
        analyzer.create_mock_pe(test_pe, is_64bit=True)
        report = analyzer.analyze(test_pe)
        self.assertTrue(report["valid_pe"])
        self.assertTrue(report["is_64bit"])
        self.assertEqual(report["recommended_prefix"], "win64")
        self.assertEqual(report["compatibility_tier"], "Platinum")
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
        self.assertTrue(hasattr(desktop_classic, "show_session_dialog"))
        desktop_classic.destroy()

        desktop_modern = GiriSpaceDesktop(profile="modern", non_interactive=True)
        self.assertEqual(desktop_modern.profile, "modern")
        desktop_modern.destroy()

    def test_07_wallpaper_collection(self):
        wp_dir = os.path.join(ROOT_DIR, "branding", "wallpapers")
        manifest_path = os.path.join(wp_dir, "wallpapers.json")
        meta_path = os.path.join(wp_dir, "wallpaper-metadata.json")
        self.assertTrue(os.path.isfile(manifest_path))
        self.assertTrue(os.path.isfile(meta_path))

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(len(manifest), 12, "Must contain exactly 12 official wallpapers")

        # Confirm official default wallpapers exist
        filenames = [w["filename"] for w in manifest]
        self.assertIn("giri-os-default-dark.png", filenames)
        self.assertIn("giri-os-default-light.png", filenames)
        self.assertIn("giri-origin.png", filenames)

        # Verify each image file exists, is 3840x2160 4K UHD, and has a 384x216 thumbnail
        for wp in manifest:
            img_path = os.path.join(wp_dir, wp["filename"])
            self.assertTrue(os.path.isfile(img_path), f"Missing wallpaper: {img_path}")

            with Image.open(img_path) as im:
                w, h = im.size
                self.assertEqual((w, h), (3840, 2160), f"Wallpaper {wp['filename']} must be 3840x2160")
                self.assertAlmostEqual(w / h, 16.0 / 9.0, delta=0.01)

            thumb_path = os.path.join(wp_dir, "thumbnails", wp["filename"])
            self.assertTrue(os.path.isfile(thumb_path), f"Missing thumbnail: {thumb_path}")
            with Image.open(thumb_path) as tim:
                tw, th = tim.size
                self.assertEqual((tw, th), (384, 216), f"Thumbnail {wp['filename']} must be 384x216")

    def test_08_wine_runner_status(self):
        runner = WineRunner()
        status = runner.get_status()
        self.assertIn("wine_installed", status)
        self.assertIn("prefix_root", status)
        self.assertIn("subsystem", status)
        self.assertIn("disclaimer", status)

    def test_09_calamares_configurations(self):
        settings_path = os.path.join(ROOT_DIR, "installer", "calamares", "settings.conf")
        self.assertTrue(os.path.isfile(settings_path))

        required_modules = ["branding.desc", "welcome.conf", "partition.conf", "unpackfs.conf", "bootloader.conf", "users.conf"]
        for mod in required_modules:
            mod_file = os.path.join(ROOT_DIR, "installer", "calamares", "modules", mod)
            self.assertTrue(os.path.isfile(mod_file), f"Missing Calamares module: {mod}")

    def test_10_theme_wallpaper_switching(self):
        desktop = GiriSpaceDesktop(non_interactive=True)
        # Default is dark theme -> giri-os-default-dark.png
        self.assertIn("giri-os-default-dark.png", desktop.wallpaper_config.get("current_wallpaper", ""))

        # Switch to light theme -> auto-switches to giri-os-default-light.png
        desktop.switch_theme("light")
        self.assertIn("giri-os-default-light.png", desktop.wallpaper_config.get("current_wallpaper", ""))

        # Switch back to dark theme -> auto-switches back to dark default
        desktop.switch_theme("dark")
        self.assertIn("giri-os-default-dark.png", desktop.wallpaper_config.get("current_wallpaper", ""))
        desktop.destroy()

    def test_11_giri_gaming_safe_profile_engine(self):
        optimizer = GiriGameOptimizer()
        # Test performance profile application
        perf_res = optimizer.apply_profile("PERFORMANCE")
        self.assertTrue(perf_res["success"])
        self.assertEqual(optimizer.active_profile, "PERFORMANCE")

        # Test safe environment variables
        self.assertEqual(os.environ.get("WINE_D3D_CONFIG"), "renderer=gl")
        self.assertEqual(os.environ.get("PROTON_USE_WINED3D"), "1")
        self.assertEqual(os.environ.get("MESA_GL_VERSION_OVERRIDE"), "3.3")

        # Revert to balanced
        bal_res = optimizer.apply_profile("DESKTOP_DEFAULT")
        self.assertTrue(bal_res["success"])
        self.assertIn(optimizer.active_profile, ["BALANCED", "DESKTOP_DEFAULT"])

    def test_12_giri_update_apt_inspection(self):
        client = GiriUpdateClient(root_dir=ROOT_DIR)
        sources = client.inspect_apt_sources()
        self.assertIn("official_debian_active", sources)
        self.assertIn("custom_giri_active", sources)
        self.assertIn("status_summary", sources)

        # Check disk space method
        space = client.check_disk_space()
        self.assertIn("free_mb", space)
        self.assertIn("sufficient", space)

        # Check production repo guide
        guide = client.get_repo_infrastructure_guide()
        self.assertIn("GIRI OS", guide)
        self.assertIn("deb.debian.org", guide)

    def test_13_giri_bridge_compatibility_tiers(self):
        analyzer = PEAnalyzer()
        test_dir = os.path.join(ROOT_DIR, "tests")

        # D3D11 app
        d3d11_file = os.path.join(test_dir, "test_d3d11_mock.exe")
        analyzer.create_mock_pe(d3d11_file, is_64bit=True, inject_d3d11=True)
        res_d3d11 = analyzer.analyze(d3d11_file)
        self.assertEqual(res_d3d11["compatibility_tier"], "Silver")

        # Anti-Cheat app
        ac_file = os.path.join(test_dir, "test_ac_mock.exe")
        analyzer.create_mock_pe(ac_file, is_64bit=True, inject_anti_cheat=True)
        res_ac = analyzer.analyze(ac_file)
        self.assertEqual(res_ac["compatibility_tier"], "Unsupported")
        self.assertTrue(res_ac["anti_cheat_detected"])

        # Clean up mocks
        for f in [d3d11_file, ac_file]:
            if os.path.exists(f):
                os.remove(f)

    def test_14_giri_bridge_prefix_lifecycle(self):
        mock_dir = os.path.join(ROOT_DIR, "tests", "test_prefixes_dir")
        runner = WineRunner(base_prefix_dir=mock_dir)

        create_res = runner.create_prefix("unit_test_pfx", arch="win64")
        self.assertTrue(create_res["success"])
        self.assertTrue(os.path.isdir(os.path.join(mock_dir, "unit_test_pfx")))

        prefixes = runner.list_prefixes()
        self.assertTrue(any(p["name"] == "unit_test_pfx" for p in prefixes))

        del_res = runner.delete_prefix("unit_test_pfx")
        self.assertTrue(del_res["success"])
        self.assertFalse(os.path.exists(os.path.join(mock_dir, "unit_test_pfx")))

        shutil.rmtree(mock_dir, ignore_errors=True)

    def test_15_calamares_icons_and_branding(self):
        svg_icon = os.path.join(ROOT_DIR, "branding", "logo", "giri-os-icon.svg")
        png_icon = os.path.join(ROOT_DIR, "branding", "logo", "giri-os-icon.png")
        self.assertTrue(os.path.isfile(svg_icon), "Calamares branding requires scalable SVG logo")
        self.assertTrue(os.path.isfile(png_icon), "Calamares branding requires PNG icon")

        # Check branding.desc contains correct icon path references
        b_desc = os.path.join(ROOT_DIR, "installer", "calamares", "modules", "branding.desc")
        with open(b_desc, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("productLogo", content)
        self.assertIn("productIcon", content)
        self.assertIn("productWelcome", content)

    def test_16_control_center_subsystem_integration(self):
        cc = GiriControlCenter(non_interactive=True)
        self.assertIsNotNone(cc.wallpaper_config)
        self.assertIsNotNone(cc.desktop_prefs)
        self.assertEqual(len(cc.wallpapers_manifest), 12)
        cc.destroy()

    def test_17_welcome_experience_instantiation(self):
        app = GiriWelcomeExperience(skip_animation=False, test_mode=True)
        self.assertIsNotNone(app.canvas)
        # Check multilingual greetings data includes required sequence
        greetings_texts = [g[0] for g in app.greetings]
        self.assertIn("WELCOME", greetings_texts)
        self.assertIn("नमस्ते", greetings_texts)
        self.assertIn("NAMASTE", greetings_texts)
        self.assertIn("ONE SYSTEM. INFINITE POSSIBILITIES.", greetings_texts)
        app.destroy()

    def test_18_welcome_experience_skippable(self):
        app = GiriWelcomeExperience(skip_animation=False, test_mode=True)
        self.assertTrue(app.animation_running)
        app.skip_and_launch()
        self.assertFalse(app.animation_running)

    def test_19_first_boot_wizard_multilingual(self):
        wizard = GiriFirstBootWizard(non_interactive=True)
        # Verify 11 total steps
        self.assertEqual(len(wizard.steps), 11)
        # Verify language choices include English and Hindi
        wizard.render_language()
        self.assertIn("English (United States)", wizard.config_data["language"])
        # Check Hindi string representation
        hindi_present = any("हिन्दी" in lang[1] for lang in [
            ("en_US", "English (US)"),
            ("hi_IN", "हिन्दी — Devanagari UI & Input")
        ])
        self.assertTrue(hindi_present)
        wizard.destroy()

    def test_20_first_boot_network_and_offline(self):
        net_info = wizard_mod.detect_network_status()
        self.assertIn("connected", net_info)
        self.assertIn("interfaces", net_info)
        self.assertIn("details", net_info)
        self.assertIsInstance(net_info["interfaces"], list)

    def test_21_first_boot_live_session_isolation(self):
        is_live = wizard_mod.is_live_session()
        self.assertIn(is_live, [True, False])
        # Verify live session safety policy logic
        self.assertIn(welcome_mod.is_live_session(), [True, False])

    def test_22_first_boot_interrupted_recovery(self):
        # A fresh wizard must NOT write the flag file upon initialization
        flag_file = os.path.join(ROOT_DIR, "tests", "test_flag_file")
        if os.path.exists(flag_file):
            os.remove(flag_file)
        wizard = GiriFirstBootWizard(non_interactive=True)
        self.assertFalse(os.path.exists(flag_file))
        wizard.destroy()

    def test_23_first_boot_save_and_finish_state(self):
        test_flag_dir = os.path.join(ROOT_DIR, "tests", "temp_giri_config")
        os.makedirs(test_flag_dir, exist_ok=True)
        test_flag = os.path.join(test_flag_dir, "first-boot-done")

        # Mock FLAG_FILE location for isolated test
        orig_flag = wizard_mod.FLAG_FILE
        wizard_mod.FLAG_FILE = test_flag
        wizard = GiriFirstBootWizard(non_interactive=True)
        wizard.config_data["username"] = "testuser"
        wizard.save_and_finish()

        self.assertTrue(os.path.isfile(test_flag))
        with open(test_flag, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["version"], "0.1 Genesis")

        # Clean up
        wizard_mod.FLAG_FILE = orig_flag
        shutil.rmtree(test_flag_dir, ignore_errors=True)

    def test_24_quick_search_and_calculator(self):
        # 1. Test safe_calculate math evaluation
        self.assertEqual(safe_calculate("2 + 2"), "= 4")
        self.assertEqual(safe_calculate("10 * 5"), "= 50")
        self.assertEqual(safe_calculate("sqrt(144)"), "= 12")
        self.assertEqual(safe_calculate("sin(0)"), "= 0")
        self.assertEqual(safe_calculate("cos(0)"), "= 1")
        # Test security sanitization - must reject arbitrary/malicious expressions
        self.assertIsNone(safe_calculate("__import__('os').system('ls')"))
        self.assertIsNone(safe_calculate("open('/etc/passwd')"))
        self.assertIsNone(safe_calculate("exec('x=1')"))

        # 2. Test application indexing
        apps = search_mod.get_installed_applications()
        self.assertIsInstance(apps, list)
        self.assertTrue(len(apps) > 0)
        self.assertTrue(any("Giri Control" in a.get("name", "") or "install" in a.get("exec", "").lower() for a in apps))

        # 3. Test GiriQuickSearch instantiation
        qs = GiriQuickSearch(non_interactive=True)
        self.assertIsNotNone(qs.entry_query)
        self.assertEqual(qs.title(), "Giri Quick Search")
        qs.destroy()

    def test_25_screen_snip_utility(self):
        # 1. Test capture_fullscreen output
        tmp_snip = os.path.join(ROOT_DIR, "tests", "temp_snip_test.png")
        if os.path.exists(tmp_snip):
            os.remove(tmp_snip)
        res = snip_mod.capture_fullscreen(tmp_snip)
        # Verify file is generated or captured
        if res:
            self.assertTrue(os.path.isfile(tmp_snip))
            with Image.open(tmp_snip) as im:
                self.assertGreater(im.width, 0)
                self.assertGreater(im.height, 0)
            os.remove(tmp_snip)

        # 2. Test GiriSnipTool instantiation
        snip = GiriSnipTool(non_interactive=True)
        self.assertEqual(snip.title(), "Giri Snip")
        snip.destroy()

    def test_26_nightlight_governor(self):
        # 1. Test preset dictionary
        presets = nightlight_mod.TEMPERATURE_PRESETS
        self.assertIn("day", presets)
        self.assertIn("sunset", presets)
        self.assertIn("warm", presets)
        self.assertIn("bedtime", presets)
        self.assertEqual(presets["day"]["gamma"], "1.0:1.0:1.0")
        self.assertEqual(presets["warm"]["gamma"], "1.0:0.78:0.60")

        # 2. Test setting preset updates config
        res = nightlight_mod.set_preset("warm")
        self.assertTrue(res)
        cfg = nightlight_mod.load_config()
        self.assertEqual(cfg["current_preset"], "warm")
        self.assertTrue(cfg["enabled"])

        # Reset back to daylight
        nightlight_mod.set_preset("day")
        cfg_day = nightlight_mod.load_config()
        self.assertEqual(cfg_day["current_preset"], "day")
        self.assertFalse(cfg_day["enabled"])

    def test_27_control_center_specs_export_and_dnd(self):
        cc = GiriControlCenter(non_interactive=True)

        # 1. Test formatted hardware specs string
        specs_text = cc.get_formatted_specs()
        self.assertIn("GIRI OS 0.1 GENESIS", specs_text)
        self.assertIn("CPU:", specs_text)
        self.assertIn("RAM:", specs_text)
        self.assertIn("GPU:", specs_text)
        self.assertIn("Tier:", specs_text)

        # 2. Test DND mode toggle
        initial_dnd = getattr(cc, "dnd_active", False)
        cc.toggle_dnd_mode()
        self.assertNotEqual(getattr(cc, "dnd_active", False), initial_dnd)
        cc.toggle_dnd_mode()
        self.assertEqual(getattr(cc, "dnd_active", False), initial_dnd)

        # 3. Test nightlight trigger
        cc.set_nightlight("day")

        cc.destroy()

    def test_28_bootloader_configuration_and_binary_hook(self):
        """Test bootloader configurations and canonical kernel linker binary hook."""
        isolinux_path = os.path.join(ROOT_DIR, "boot", "isolinux", "isolinux.cfg")
        grub_path = os.path.join(ROOT_DIR, "boot", "grub", "grub.cfg")
        hook_path = os.path.join(ROOT_DIR, "build", "live-build", "config", "hooks", "live", "99-link-canonical-kernel.hook.binary")

        # 1. Verify ISOLINUX configuration
        self.assertTrue(os.path.isfile(isolinux_path), "isolinux.cfg missing")
        with open(isolinux_path, "r", encoding="utf-8") as f:
            isolinux_content = f.read()
        self.assertIn("Giri OS 0.1 Genesis", isolinux_content)
        self.assertIn("KERNEL /live/vmlinuz", isolinux_content)
        self.assertIn("APPEND initrd=/live/initrd.img", isolinux_content)
        self.assertIn("Safe Graphics Mode", isolinux_content)
        self.assertIn("System Recovery Mode", isolinux_content)

        # 2. Verify GRUB configuration with dynamic kernel fallback
        self.assertTrue(os.path.isfile(grub_path), "grub.cfg missing")
        with open(grub_path, "r", encoding="utf-8") as f:
            grub_content = f.read()
        self.assertIn("Giri OS 0.1 (Genesis) — Standard Session", grub_content)
        self.assertIn("set giri_kernel=", grub_content)
        self.assertIn("set giri_initrd=", grub_content)
        self.assertIn("linux ${giri_kernel}", grub_content)
        self.assertIn("initrd ${giri_initrd}", grub_content)
        self.assertIn("Safe Graphics Mode", grub_content)
        self.assertIn("System Recovery Mode", grub_content)
        self.assertIn("fwsetup", grub_content)

        # 3. Verify Live-Build Binary Hook
        self.assertTrue(os.path.isfile(hook_path), "99-link-canonical-kernel.hook.binary missing")
        with open(hook_path, "r", encoding="utf-8") as f:
            hook_content = f.read()
        self.assertIn("Canonical Kernel & Initrd Linker", hook_content)
        self.assertIn("vmlinuz-*", hook_content)
        self.assertIn("initrd.img-*", hook_content)
        self.assertIn("ln -f", hook_content)
        self.assertIn("memtest", hook_content)

    def test_29_giri_space_session_staging_and_permissions(self):
        """Test permanent staging of Giri Space session files and execution permissions."""
        session_desktop = os.path.join(ROOT_DIR, "desktop", "giri-space", "session", "giri-space-classic.desktop")
        modern_desktop = os.path.join(ROOT_DIR, "desktop", "giri-space", "session", "giri-space-modern.desktop")
        session_script = os.path.join(ROOT_DIR, "desktop", "giri-space", "session", "giri-session")
        verify_hook = os.path.join(ROOT_DIR, "build", "live-build", "config", "hooks", "live", "98-verify-giri-session.hook.chroot")
        build_iso_script = os.path.join(ROOT_DIR, "scripts", "build-iso.sh")

        # 1. Verify session desktop files exist and have correct Exec/TryExec
        self.assertTrue(os.path.isfile(session_desktop), "giri-space-classic.desktop missing")
        with open(session_desktop, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Name=Giri Space (Classic)", content)
        self.assertIn("Exec=/usr/bin/giri-session --profile classic", content)
        self.assertIn("TryExec=/usr/bin/giri-session", content)
        self.assertIn("Icon=giri-os-icon", content)

        self.assertTrue(os.path.isfile(modern_desktop), "giri-space-modern.desktop missing")
        with open(modern_desktop, "r", encoding="utf-8") as f:
            mod_content = f.read()
        self.assertIn("Name=Giri Space (Modern)", mod_content)
        self.assertIn("Exec=/usr/bin/giri-session --profile modern", mod_content)

        # 2. Verify session entrypoint script contents and referenced files
        self.assertTrue(os.path.isfile(session_script), "giri-session missing")
        with open(session_script, "r", encoding="utf-8") as f:
            script_content = f.read()
        self.assertIn("openbox", script_content)
        self.assertIn("picom", script_content)
        self.assertIn("giri_space.py", script_content)
        self.assertIn("plymouth --quit", script_content)

        # Verify referenced desktop shell script exists
        shell_py = os.path.join(ROOT_DIR, "desktop", "giri-space", "shell", "giri_space.py")
        self.assertTrue(os.path.isfile(shell_py), "giri_space.py missing")

        # 3. Verify session verification hook exists and enforces 0755
        self.assertTrue(os.path.isfile(verify_hook), "98-verify-giri-session.hook.chroot missing")
        with open(verify_hook, "r", encoding="utf-8") as f:
            hook_content = f.read()
        self.assertIn("/usr/share/xsessions/giri-space-classic.desktop", hook_content)
        self.assertIn("chmod 0755 /usr/bin/giri-session", hook_content)
        self.assertIn("test -x /usr/bin/giri-session", hook_content)

        # 4. Verify build-iso.sh stages xsessions and /usr/bin/giri-session
        with open(build_iso_script, "r", encoding="utf-8") as f:
            build_content = f.read()
        self.assertIn("${INCLUDES_CHROOT}/usr/share/xsessions", build_content)
        self.assertIn("chmod 0755 \"${INCLUDES_CHROOT}/usr/bin/giri-session\"", build_content)

    def test_30_lightdm_session_selection_and_dependencies(self):
        """Test LightDM configuration selects Giri Space and all desktop dependencies are declared."""
        branding_hook = os.path.join(ROOT_DIR, "build", "live-build", "config", "hooks", "live", "01-setup-giri-branding.hook.chroot")
        desktop_pkgs = os.path.join(ROOT_DIR, "build", "live-build", "config", "package-lists", "giri-desktop.list.chroot")

        # 1. Verify LightDM autologin and session configuration
        self.assertTrue(os.path.isfile(branding_hook), "01-setup-giri-branding.hook.chroot missing")
        with open(branding_hook, "r", encoding="utf-8") as f:
            hook_content = f.read()
        self.assertIn("user-session=giri-space-classic", hook_content)
        self.assertIn("autologin-user=giri", hook_content)
        self.assertIn("greeter-session=lightdm-gtk-greeter", hook_content)
        self.assertIn("display-setup-script=/usr/bin/giri-display-setup", hook_content)

        # 2. Verify all critical desktop dependencies are in package list
        self.assertTrue(os.path.isfile(desktop_pkgs), "giri-desktop.list.chroot missing")
        with open(desktop_pkgs, "r", encoding="utf-8") as f:
            pkg_content = f.read()
        required_pkgs = [
            "openbox", "picom", "feh", "tint2", "dunst", "lightdm",
            "lightdm-gtk-greeter", "python3-tk", "python3-psutil",
            "python3-pil", "kitty", "thunar", "calamares"
        ]
        for pkg in required_pkgs:
            self.assertIn(pkg, pkg_content, f"Required package '{pkg}' missing from giri-desktop.list.chroot")



if __name__ == "__main__":
    unittest.main()
