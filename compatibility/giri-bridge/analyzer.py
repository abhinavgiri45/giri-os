#!/usr/bin/env python3
"""
Giri Bridge — Windows Portable Executable (PE) Compatibility Analyzer
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Analyzes Windows .exe and .msi binaries directly from their PE headers.
Extracts architecture (32-bit vs 64-bit), Subsystem (GUI vs CLI), and
generates tailored Wine/Proton prefix execution profiles.
"""

import sys
import os
import struct
import json


class PEAnalyzer:
    IMAGE_FILE_MACHINE_I386 = 0x014C
    IMAGE_FILE_MACHINE_AMD64 = 0x8664
    IMAGE_FILE_MACHINE_ARM64 = 0xAA64

    SUBSYSTEM_NATIVE = 1
    SUBSYSTEM_WINDOWS_GUI = 2
    SUBSYSTEM_WINDOWS_CUI = 3  # Console
    SUBSYSTEM_POSIX_CUI = 7
    SUBSYSTEM_WINDOWS_CE_GUI = 9
    SUBSYSTEM_EFI_APPLICATION = 10

    def __init__(self, file_path=None):
        self.file_path = file_path
        self.report = {
            "valid_pe": False,
            "architecture": "Unknown",
            "is_64bit": False,
            "subsystem": "Unknown",
            "recommended_prefix": "win64",
            "recommended_graphics": "wined3d",
            "notes": []
        }
        if file_path:
            self.analyze(file_path)

    def analyze(self, path):
        self.file_path = path
        if not os.path.isfile(path):
            self.report["notes"].append(f"File not found: {path}")
            return self.report

        try:
            with open(path, "rb") as f:
                # 1. Check DOS Header (MZ)
                dos_header = f.read(64)
                if len(dos_header) < 64 or dos_header[:2] != b"MZ":
                    self.report["notes"].append("Not a valid DOS/Windows executable (Missing 'MZ' magic).")
                    return self.report

                # e_lfanew is at offset 0x3C (4-byte unsigned int pointing to PE signature)
                pe_offset = struct.unpack_from("<I", dos_header, 0x3C)[0]
                f.seek(pe_offset)

                # 2. Check PE Signature (PE\0\0)
                pe_sig = f.read(4)
                if pe_sig != b"PE\x00\x00":
                    self.report["notes"].append("Invalid PE signature.")
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

                # 4. Read Optional Header Magic & Subsystem
                if opt_hdr_size > 0:
                    opt_magic_bytes = f.read(2)
                    opt_magic = struct.unpack("<H", opt_magic_bytes)[0]
                    # Subsystem offset is at offset 68 for PE32 (0x10b) and offset 68 for PE32+ (0x20b)
                    f.seek(pe_offset + 24 + 68)
                    subsystem_bytes = f.read(2)
                    if len(subsystem_bytes) == 2:
                        subsystem = struct.unpack("<H", subsystem_bytes)[0]
                        if subsystem == self.SUBSYSTEM_WINDOWS_GUI:
                            self.report["subsystem"] = "Windows GUI"
                        elif subsystem == self.SUBSYSTEM_WINDOWS_CUI:
                            self.report["subsystem"] = "Windows Console (CLI)"
                        else:
                            self.report["subsystem"] = f"Subsystem Code {subsystem}"

                # Tuning recommendations
                if not self.report["is_64bit"]:
                    self.report["notes"].append("32-bit binary detected. Using Giri Bridge multiarch win32 prefix container.")
                else:
                    self.report["notes"].append("64-bit binary detected. Using Giri Bridge win64 container.")

                self.report["notes"].append("Graphics: wined3d (Mesa OpenGL) default enforced for maximum stability.")

        except Exception as e:
            self.report["notes"].append(f"Parsing error: {str(e)}")

        return self.report

    def create_mock_pe(self, output_path, is_64bit=True):
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


if __name__ == "__main__":
    if "--test" in sys.argv:
        # Run automated PE analyzer test
        test_file = "tests/test_mock_app.exe"
        os.makedirs("tests", exist_ok=True)
        analyzer = PEAnalyzer()
        analyzer.create_mock_pe(test_file, is_64bit=True)
        res = analyzer.analyze(test_file)
        assert res["valid_pe"] is True
        assert res["is_64bit"] is True
        assert res["subsystem"] == "Windows GUI"
        print("Giri Bridge PE Analyzer self-test passed successfully.")
    elif len(sys.argv) > 1 and sys.argv[1] != "--test":
        target = sys.argv[1]
        analyzer = PEAnalyzer(target)
        print(json.dumps(analyzer.report, indent=2))
    else:
        print("Usage: python analyzer.py <path-to-exe> or python analyzer.py --test")
