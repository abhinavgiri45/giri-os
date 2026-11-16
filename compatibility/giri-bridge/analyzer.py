#!/usr/bin/env python3
"""
Giri Bridge — Windows Portable Executable (PE) Compatibility Analyzer
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Analyzes Windows .exe, .msi, and .dll binaries directly from their PE headers.
Extracts architecture (32-bit vs 64-bit), Subsystem, imported DLL dependencies,
detects kernel-level anti-cheats, and calculates realistic compatibility ratings:
Platinum, Gold, Silver, Bronze, or Unsupported.
"""

import sys
import os
import struct
import json
import re


class PEAnalyzer:
    IMAGE_FILE_MACHINE_I386 = 0x014C
    IMAGE_FILE_MACHINE_AMD64 = 0x8664
    IMAGE_FILE_MACHINE_ARM64 = 0xAA64

    SUBSYSTEM_NATIVE = 1               # Device drivers and native system processes
    SUBSYSTEM_WINDOWS_GUI = 2          # Windows GUI application
    SUBSYSTEM_WINDOWS_CUI = 3          # Windows Console application
    SUBSYSTEM_POSIX_CUI = 7
    SUBSYSTEM_WINDOWS_CE_GUI = 9
    SUBSYSTEM_EFI_APPLICATION = 10

    # Anti-cheat signatures and drivers known to be incompatible with Wine
    ANTI_CHEAT_SIGNATURES = [
        "easyanticheat", "easyanticheat.sys", "easyanticheat_x64.so", "eac_server.dll",
        "battleye", "beservice.exe", "bedaisy.sys", "beclient.dll",
        "vanguard", "vgk.sys", "vgc.exe",
        "ricochet",
        "punkbuster", "pbsvc.exe",
        "equ8", "blackcall.sys", "nprotect", "gameguard"
    ]

    # Graphics APIs detected in imports
    GRAPHICS_APIS = {
        "d3d9.dll": "DirectX 9 (D3D9)",
        "d3d10.dll": "DirectX 10 (D3D10)",
        "d3d11.dll": "DirectX 11 (D3D11)",
        "d3d12.dll": "DirectX 12 (D3D12)",
        "dxgi.dll": "DirectX Graphics Infrastructure (DXGI)",
        "vulkan-1.dll": "Vulkan",
        "opengl32.dll": "OpenGL"
    }

    def __init__(self, file_path=None):
        self.file_path = file_path
        self.report = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path) if file_path else "",
            "valid_pe": False,
            "is_dos_16bit": False,
            "architecture": "Unknown",
            "is_64bit": False,
            "subsystem": "Unknown",
            "imported_dlls": [],
            "detected_apis": [],
            "anti_cheat_detected": False,
            "anti_cheat_name": None,
            "compatibility_tier": "Unknown",
            "tier_description": "",
            "recommended_prefix": "win64",
            "recommended_graphics": "wined3d",
            "hardware_notes": [],
            "notes": []
        }
        if file_path:
            self.analyze(file_path)

    def analyze(self, path):
        self.file_path = path
        self.report["file_path"] = path
        self.report["file_name"] = os.path.basename(path)

        if not os.path.isfile(path):
            self.report["notes"].append(f"File not found: {path}")
            self.report["compatibility_tier"] = "Unsupported"
            self.report["tier_description"] = "Target binary does not exist on disk."
            return self.report

        try:
            file_size = os.path.getsize(path)
            with open(path, "rb") as f:
                # 1. Check DOS Header (MZ)
                dos_header = f.read(64)
                if len(dos_header) < 64 or dos_header[:2] != b"MZ":
                    self.report["notes"].append("Not a valid DOS/Windows executable (Missing 'MZ' magic).")
                    self.report["compatibility_tier"] = "Unsupported"
                    self.report["tier_description"] = "Invalid executable format (missing DOS MZ header)."
                    return self.report

                # e_lfanew is at offset 0x3C (4-byte unsigned int pointing to PE signature)
                pe_offset = struct.unpack_from("<I", dos_header, 0x3C)[0]
                if pe_offset >= file_size or pe_offset < 64:
                    self.report["is_dos_16bit"] = True
                    self.report["notes"].append("Legacy 16-bit DOS application detected (no 32-bit/64-bit PE header).")
                    self.report["compatibility_tier"] = "Unsupported"
                    self.report["tier_description"] = "16-bit DOS binaries cannot run directly in 64-bit Wine (requires DOSBox)."
                    return self.report

                f.seek(pe_offset)
                # 2. Check PE Signature (PE\0\0)
                pe_sig = f.read(4)
                if pe_sig != b"PE\x00\x00":
                    self.report["is_dos_16bit"] = True
                    self.report["notes"].append("Invalid PE signature (possibly legacy NE/LE 16-bit executable).")
                    self.report["compatibility_tier"] = "Unsupported"
                    self.report["tier_description"] = "Non-PE executable format (unsupported by Giri Bridge)."
                    return self.report

                self.report["valid_pe"] = True

                # 3. Read COFF File Header (20 bytes)
                coff_header = f.read(20)
                machine, num_sections, timestamp, _, _, opt_hdr_size, characteristics = struct.unpack(
                    "<HHIIIHH", coff_header
                )

                if machine == self.IMAGE_FILE_MACHINE_I386:
                    self.report["architecture"] = "32-bit (x86)"
                    self.report["is_64bit"] = False
                    self.report["recommended_prefix"] = "win32"
                elif machine == self.IMAGE_FILE_MACHINE_AMD64:
                    self.report["architecture"] = "64-bit (x86_64)"
                    self.report["is_64bit"] = True
                    self.report["recommended_prefix"] = "win64"
                elif machine == self.IMAGE_FILE_MACHINE_ARM64:
                    self.report["architecture"] = "ARM64"
                    self.report["is_64bit"] = True
                    self.report["recommended_prefix"] = "arm64"
                else:
                    self.report["architecture"] = f"Unknown (Machine: 0x{machine:04x})"

                # 4. Read Optional Header
                subsystem = 0
                if opt_hdr_size > 0:
                    opt_header_data = f.read(opt_hdr_size)
                    if len(opt_header_data) >= 70:
                        opt_magic = struct.unpack_from("<H", opt_header_data, 0)[0]
                        subsystem = struct.unpack_from("<H", opt_header_data, 68)[0]
                        if subsystem == self.SUBSYSTEM_WINDOWS_GUI:
                            self.report["subsystem"] = "Windows GUI"
                        elif subsystem == self.SUBSYSTEM_WINDOWS_CUI:
                            self.report["subsystem"] = "Windows Console (CLI)"
                        elif subsystem == self.SUBSYSTEM_NATIVE:
                            self.report["subsystem"] = "Native Kernel Driver / System Subsystem"
                        else:
                            self.report["subsystem"] = f"Subsystem Code {subsystem}"

                # 5. Extract DLL Import Strings & Scan Anti-Cheat Signatures
                # Fast string scan over first 2MB or entire file for imports
                f.seek(0)
                scan_bytes = f.read(min(file_size, 4 * 1024 * 1024))
                
                # Scan for DLL names
                dll_pattern = re.compile(rb'[a-zA-Z0-9_\-\.]{3,64}\.dll', re.IGNORECASE)
                found_dlls = set()
                for match in dll_pattern.finditer(scan_bytes):
                    dll_name = match.group(0).decode("ascii", errors="ignore").lower()
                    found_dlls.add(dll_name)

                self.report["imported_dlls"] = sorted(list(found_dlls))[:30]

                # Identify APIs
                for dll in self.report["imported_dlls"]:
                    if dll in self.GRAPHICS_APIS:
                        self.report["detected_apis"].append(self.GRAPHICS_APIS[dll])

                # Scan anti-cheat patterns in raw bytes
                scan_str_lower = scan_bytes.lower()
                for ac in self.ANTI_CHEAT_SIGNATURES:
                    if ac.encode("ascii") in scan_str_lower:
                        self.report["anti_cheat_detected"] = True
                        self.report["anti_cheat_name"] = ac.title()
                        break

                # 6. Calculate Compatibility Tier
                self._calculate_tier(subsystem)

        except Exception as e:
            self.report["notes"].append(f"Parsing error: {str(e)}")
            self.report["compatibility_tier"] = "Unsupported"
            self.report["tier_description"] = f"Error reading PE structure: {str(e)}"

        return self.report

    def _calculate_tier(self, subsystem):
        """Calculates realistic compatibility rating and adds technical notes."""
        if subsystem == self.SUBSYSTEM_NATIVE or self.file_path.lower().endswith(".sys"):
            self.report["compatibility_tier"] = "Unsupported"
            self.report["tier_description"] = (
                "Windows Kernel Driver (.sys): Requires Windows NT kernel-mode execution. "
                "Kernel drivers cannot run in Wine user-space translation."
            )
            return

        if self.report["anti_cheat_detected"]:
            ac_name = self.report["anti_cheat_name"]
            self.report["compatibility_tier"] = "Unsupported"
            self.report["tier_description"] = (
                f"Kernel Anti-Cheat Detected ({ac_name}): Requires proprietary Windows kernel hooks "
                "and ring-0 drivers that cannot execute in Wine or Proton without official developer enablement."
            )
            return

        # Check graphics and APIs
        has_d3d12 = any("DirectX 12" in api for api in self.report["detected_apis"])
        has_vulkan = any("Vulkan" in api for api in self.report["detected_apis"])
        has_d3d11 = any("DirectX 11" in api for api in self.report["detected_apis"])
        has_d3d9 = any("DirectX 9" in api for api in self.report["detected_apis"])

        if has_d3d12:
            self.report["compatibility_tier"] = "Bronze"
            self.report["tier_description"] = (
                "DirectX 12 Application: Requires VKD3D-Proton and hardware Vulkan 1.3 support. "
                "Will fail or crash on legacy GPUs without Vulkan (such as Intel HD 2000)."
            )
            self.report["hardware_notes"].append("Warning: Intel HD 2000 does not support DirectX 12 translation.")
        elif has_vulkan:
            self.report["compatibility_tier"] = "Silver"
            self.report["tier_description"] = (
                "Vulkan Application: Requires host Vulkan graphics driver. On Intel HD 2000, "
                "Vulkan is unsupported by hardware and Mesa crocus driver."
            )
            self.report["hardware_notes"].append("Warning: Host GPU lacks Vulkan hardware support.")
        elif has_d3d11:
            self.report["compatibility_tier"] = "Silver"
            self.report["tier_description"] = (
                "DirectX 11 Application: Supported via DXVK (if Vulkan available) or wined3d OpenGL fallback. "
                "On Intel HD 2000, executes via wined3d with reduced framerate."
            )
            self.report["recommended_graphics"] = "wined3d"
        elif has_d3d9:
            self.report["compatibility_tier"] = "Gold"
            self.report["tier_description"] = (
                "DirectX 9 Application: High compatibility via Wine OpenGL (wined3d). "
                "Runs reliably on Intel HD 2000 and legacy graphics architectures."
            )
            self.report["recommended_graphics"] = "wined3d"
        else:
            # Standard GDI / User32 / CLI application
            self.report["compatibility_tier"] = "Platinum"
            self.report["tier_description"] = (
                "Standard Win32 Application: Relies on core Windows APIs (User32, Kernel32, GDI32). "
                "Excellent compatibility in standard Wine container."
            )

        # General disclaimer
        self.report["notes"].append(
            "Giri Bridge provides compatibility via Wine and translation layers. "
            "It does not claim 100% Windows compatibility."
        )

    def create_mock_pe(self, output_path, is_64bit=True, inject_anti_cheat=False, inject_d3d11=False):
        """Generates a synthetic valid PE binary for testing Giri Bridge parsing."""
        with open(output_path, "wb") as f:
            # DOS stub (64 bytes)
            dos = bytearray(64)
            dos[0:2] = b"MZ"
            struct.pack_into("<I", dos, 0x3C, 0x80)  # PE offset at 128
            f.write(dos)
            f.write(b"\x00" * 64)  # Padding up to offset 128

            # PE Header
            f.write(b"PE\x00\x00")
            # COFF Header (20 bytes)
            machine = self.IMAGE_FILE_MACHINE_AMD64 if is_64bit else self.IMAGE_FILE_MACHINE_I386
            coff = struct.pack("<HHIIIHH", machine, 1, 0x60000000, 0, 0, 224, 0x0102)
            f.write(coff)
            # Optional Header start (magic + fields)
            magic = 0x020B if is_64bit else 0x010B
            opt = bytearray(224)
            struct.pack_into("<H", opt, 0, magic)
            # Subsystem at offset 68: Windows GUI = 2
            struct.pack_into("<H", opt, 68, self.SUBSYSTEM_WINDOWS_GUI)
            f.write(opt)

            # Extra payload bytes
            if inject_anti_cheat:
                f.write(b"kernel32.dll\x00user32.dll\x00easyanticheat.sys\x00")
            elif inject_d3d11:
                f.write(b"kernel32.dll\x00user32.dll\x00d3d11.dll\x00dxgi.dll\x00")
            else:
                f.write(b"kernel32.dll\x00user32.dll\x00gdi32.dll\x00")


if __name__ == "__main__":
    if "--test" in sys.argv:
        test_dir = "tests"
        os.makedirs(test_dir, exist_ok=True)
        analyzer = PEAnalyzer()

        # 1. Test clean Win32 app -> Platinum
        mock_clean = os.path.join(test_dir, "test_clean.exe")
        analyzer.create_mock_pe(mock_clean, is_64bit=True)
        res_clean = analyzer.analyze(mock_clean)
        assert res_clean["valid_pe"] is True
        assert res_clean["compatibility_tier"] == "Platinum"

        # 2. Test D3D11 app -> Silver
        mock_d3d11 = os.path.join(test_dir, "test_d3d11.exe")
        analyzer.create_mock_pe(mock_d3d11, is_64bit=True, inject_d3d11=True)
        res_d3d11 = analyzer.analyze(mock_d3d11)
        assert res_d3d11["compatibility_tier"] == "Silver"

        # 3. Test Anti-Cheat app -> Unsupported
        mock_ac = os.path.join(test_dir, "test_ac.exe")
        analyzer.create_mock_pe(mock_ac, is_64bit=True, inject_anti_cheat=True)
        res_ac = analyzer.analyze(mock_ac)
        assert res_ac["compatibility_tier"] == "Unsupported"
        assert res_ac["anti_cheat_detected"] is True

        print("Giri Bridge PE Analyzer self-tests passed successfully.")
        sys.exit(0)
    elif len(sys.argv) > 1:
        target = sys.argv[1]
        analyzer = PEAnalyzer(target)
        print(json.dumps(analyzer.report, indent=2))
    else:
        print("Usage: python analyzer.py <path-to-exe> or python analyzer.py --test")
