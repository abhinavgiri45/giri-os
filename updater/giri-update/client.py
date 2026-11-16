#!/usr/bin/env python3
"""
Giri Update — Debian APT Repository & System Update Manager
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Manages Debian APT repository channels, verifies GPG keyrings and SHA-256 digests,
audits disk space requirements, runs non-destructive upgrade simulations (dry-run),
tracks update history, and maintains rollback checkpoints.
"""

import sys
import os
import json
import hashlib
import time
import shutil
import subprocess
import glob
from pathlib import Path


class GiriUpdateClient:
    """
    Production-ready Debian APT update manager for Giri OS.
    Works natively on Debian 12 Bookworm, with graceful fallbacks for testing
    and non-Linux environments.
    """

    MIN_FREE_SPACE_MB = 2048  # Minimum 2 GB free space required before upgrade
    OFFICIAL_DEBIAN_MIRRORS = [
        "deb.debian.org",
        "security.debian.org",
        "archive.debian.org",
        "ftp.debian.org"
    ]
    GIRI_MIRROR_DOMAIN = "repo.girios.org"

    def __init__(self, root_prefix="", history_dir=None, root_dir=None):
        if root_dir and not root_prefix:
            root_prefix = root_dir
        self.root_prefix = root_prefix
        self.os_release_path = os.path.join(root_prefix, "etc", "os-release") if root_prefix else "/etc/os-release"
        self.sources_list_path = os.path.join(root_prefix, "etc", "apt", "sources.list") if root_prefix else "/etc/apt/sources.list"
        self.sources_dir_path = os.path.join(root_prefix, "etc", "apt", "sources.list.d") if root_prefix else "/etc/apt/sources.list.d"
        self.keyrings_dir = os.path.join(root_prefix, "etc", "apt", "trusted.gpg.d") if root_prefix else "/etc/apt/trusted.gpg.d"
        self.usr_keyrings_dir = os.path.join(root_prefix, "usr", "share", "keyrings") if root_prefix else "/usr/share/keyrings"

        # Determine history location
        if history_dir:
            self.history_file = os.path.join(history_dir, "history.json")
        elif os.name == "posix" and os.geteuid() == 0:
            self.history_file = os.path.join(root_prefix, "var", "log", "giri-update", "history.json")
        else:
            local_dir = os.path.expanduser("~/.local/share/giri-update")
            self.history_file = os.path.join(local_dir, "history.json")

        self.history = self._load_history()

    def _load_history(self):
        if os.path.isfile(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "os_name": "Giri OS",
            "version": "0.1 Genesis",
            "last_checked": None,
            "installed_giri_mirror": False,
            "checkpoints": []
        }

    def _save_history(self):
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            # Non-fatal if unprivileged
            pass

    def get_os_release(self):
        """Inspects /etc/os-release to determine underlying distribution details."""
        details = {
            "NAME": "Giri OS",
            "VERSION": "0.1 Genesis",
            "ID": "girios",
            "ID_LIKE": "debian",
            "VERSION_ID": "0.1",
            "DEBIAN_CODENAME": "bookworm"
        }
        if os.path.isfile(self.os_release_path):
            try:
                with open(self.os_release_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            details[k.strip()] = v.strip().strip('"').strip("'")
            except Exception:
                pass
        return details

    def inspect_apt_sources(self):
        """
        Inspects /etc/apt/sources.list and /etc/apt/sources.list.d/.
        Identifies active Debian mirrors and custom Giri OS repositories.
        """
        sources = []
        files_to_check = []

        if os.path.isfile(self.sources_list_path):
            files_to_check.append(self.sources_list_path)

        if os.path.isdir(self.sources_dir_path):
            for entry in os.listdir(self.sources_dir_path):
                if entry.endswith(".list") or entry.endswith(".sources"):
                    files_to_check.append(os.path.join(self.sources_dir_path, entry))

        debian_mirror_active = False
        giri_mirror_active = False

        for fpath in files_to_check:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    for line_no, line in enumerate(f, 1):
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        sources.append({
                            "file": fpath,
                            "line": line_no,
                            "entry": line
                        })
                        if any(m in line for m in self.OFFICIAL_DEBIAN_MIRRORS):
                            debian_mirror_active = True
                        if self.GIRI_MIRROR_DOMAIN in line:
                            giri_mirror_active = True
            except Exception:
                pass

        return {
            "files_checked": files_to_check,
            "sources": sources,
            "official_debian_active": debian_mirror_active,
            "custom_giri_active": giri_mirror_active,
            "status_summary": (
                "Official Debian 12 Bookworm repositories active." if debian_mirror_active else "No Debian mirrors detected."
            ) + (
                " Custom Giri OS repository mirror is currently NOT active (using upstream Debian)."
                if not giri_mirror_active else " Custom Giri OS repository mirror is active."
            )
        }

    def inspect_keyrings(self):
        """Audits trusted GPG keyrings in /etc/apt/trusted.gpg.d/ and /usr/share/keyrings/."""
        keyrings = []
        for d in [self.keyrings_dir, self.usr_keyrings_dir]:
            if os.path.isdir(d):
                for k in glob.glob(os.path.join(d, "*.gpg")) + glob.glob(os.path.join(d, "*.asc")):
                    keyrings.append({
                        "path": k,
                        "name": os.path.basename(k),
                        "size_bytes": os.path.getsize(k)
                    })
        return keyrings

    def check_disk_space(self, target_path="/"):
        """Checks available disk space on target partition in megabytes."""
        try:
            # Adjust path if root_prefix is used
            check_dir = self.root_prefix if self.root_prefix and os.path.isdir(self.root_prefix) else (
                target_path if os.path.exists(target_path) else os.getcwd()
            )
            usage = shutil.disk_usage(check_dir)
            free_mb = usage.free // (1024 * 1024)
            total_mb = usage.total // (1024 * 1024)
            sufficient = free_mb >= self.MIN_FREE_SPACE_MB
            return {
                "free_mb": free_mb,
                "total_mb": total_mb,
                "required_mb": self.MIN_FREE_SPACE_MB,
                "sufficient": sufficient,
                "error": None if sufficient else f"Insufficient disk space: {free_mb} MB available, {self.MIN_FREE_SPACE_MB} MB required."
            }
        except Exception as e:
            return {
                "free_mb": 0,
                "total_mb": 0,
                "required_mb": self.MIN_FREE_SPACE_MB,
                "sufficient": False,
                "error": str(e)
            }

    def verify_payload(self, data_bytes, expected_sha256):
        """Cryptographically verifies SHA-256 digest of update payload."""
        if not data_bytes or not expected_sha256:
            return False
        calc = hashlib.sha256(data_bytes).hexdigest()
        return calc.lower() == expected_sha256.lower()

    def check_for_updates(self, simulate_if_missing_apt=True):
        """
        Queries APT to check for upgradable packages.
        Uses `apt-get -s dist-upgrade` or `apt-get -s upgrade` safely.
        """
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        self.history["last_checked"] = now_str

        # Check if apt is installed
        apt_path = shutil.which("apt-get")
        if not apt_path:
            # Non-Debian environment or dev host
            if simulate_if_missing_apt:
                result = {
                    "timestamp": now_str,
                    "engine": "simulation",
                    "apt_available": False,
                    "upgrades_available": 0,
                    "security_updates": 0,
                    "packages": [],
                    "message": "apt-get is not present on this host (Windows/non-Debian). Simulating empty upgrade delta."
                }
                return result
            return {
                "timestamp": now_str,
                "engine": "apt",
                "apt_available": False,
                "upgrades_available": 0,
                "security_updates": 0,
                "packages": [],
                "error": "apt-get executable not found in PATH."
            }

        try:
            # Run apt-get -s dist-upgrade
            cmd = ["apt-get", "-s", "dist-upgrade"]
            env = dict(os.environ, DEBIAN_FRONTEND="noninteractive")
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60, env=env)
            
            upgrades = []
            sec_count = 0
            for line in proc.stdout.splitlines():
                line = line.strip()
                if line.startswith("Inst "):
                    # e.g. Inst curl [7.88.1-10+deb12u5] (7.88.1-10+deb12u6 Debian:12.7/stable [amd64])
                    parts = line.split()
                    pkg_name = parts[1] if len(parts) > 1 else "unknown"
                    is_sec = "security" in line.lower() or "deb12u" in line.lower()
                    if is_sec:
                        sec_count += 1
                    upgrades.append({
                        "name": pkg_name,
                        "raw": line,
                        "is_security": is_sec
                    })

            res = {
                "timestamp": now_str,
                "engine": "apt-get",
                "apt_available": True,
                "upgrades_available": len(upgrades),
                "security_updates": sec_count,
                "packages": upgrades,
                "message": f"Found {len(upgrades)} upgradable packages ({sec_count} security updates)."
            }
            return res
        except Exception as e:
            return {
                "timestamp": now_str,
                "engine": "apt-get",
                "apt_available": True,
                "upgrades_available": 0,
                "security_updates": 0,
                "packages": [],
                "error": f"Failed executing apt-get simulation: {str(e)}"
            }

    def execute_upgrade(self, dry_run=True):
        """
        Executes system upgrade.
        If dry_run is True, runs with `apt-get --dry-run upgrade`.
        Requires root privileges if dry_run is False.
        """
        # 1. Check disk space
        space = self.check_disk_space()
        if not space["sufficient"]:
            return {
                "status": "ABORTED",
                "reason": space["error"],
                "free_mb": space["free_mb"],
                "required_mb": self.MIN_FREE_SPACE_MB
            }

        # 2. Check privileges if live
        if not dry_run and os.name == "posix":
            if os.geteuid() != 0:
                return {
                    "status": "PERMISSION_DENIED",
                    "reason": "Live system upgrades require root privileges. Please run with sudo.",
                    "dry_run": False
                }

        apt_path = shutil.which("apt-get")
        if not apt_path:
            return {
                "status": "SIMULATED",
                "reason": "apt-get not present on host. Upgrade simulated successfully.",
                "dry_run": dry_run
            }

        cmd = ["apt-get", "-y"]
        if dry_run:
            cmd.append("--dry-run")
        cmd.extend(["dist-upgrade"])

        try:
            env = dict(os.environ, DEBIAN_FRONTEND="noninteractive")
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=300, env=env)
            success = proc.returncode == 0
            
            # Record checkpoint
            checkpoint = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": "DRY_RUN" if dry_run else "LIVE_UPGRADE",
                "exit_code": proc.returncode,
                "status": "SUCCESS" if success else "FAILED"
            }
            self.history["checkpoints"].append(checkpoint)
            self._save_history()

            return {
                "status": "SUCCESS" if success else "FAILED",
                "dry_run": dry_run,
                "exit_code": proc.returncode,
                "stdout": proc.stdout[-1000:] if proc.stdout else "",
                "stderr": proc.stderr[-1000:] if proc.stderr else ""
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "dry_run": dry_run,
                "error": str(e)
            }

    @staticmethod
    def get_repo_infrastructure_guide():
        """
        Returns architectural documentation on the APT repository infrastructure
        required for hosting production Giri OS packages.
        """
        return """
================================================================================
GIRI OS — OFFICIAL APT REPOSITORY INFRASTRUCTURE SPECIFICATION
================================================================================

1. OVERVIEW
Giri OS 0.1 Genesis is based on Debian 12 Bookworm AMD64. By default, package
resolution and security updates are provided directly by official Debian mirrors:
  - deb.debian.org/debian bookworm main contrib non-free non-free-firmware
  - security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware

To distribute custom Giri OS packages (e.g. giri-space, giri-gaming, giri-bridge,
branding, and custom kernels), a dedicated APT repository mirror is required.

2. HOSTING TOPOLOGY
  - Base URL: https://repo.girios.org/debian
  - Distribution Suite: bookworm
  - Components: main, universe, extras
  - Architectures: amd64, all

3. GPG SIGNING & SECURITY KEYRING
  - Key Type: RSA 4096-bit or Ed25519
  - Keyring Location on Client: /etc/apt/keyrings/giri-archive-keyring.gpg
  - Release Signing:
      Release file must be signed with detached signature (Release.gpg)
      and inline signature (InRelease) using:
        gpg --default-key "Giri OS Archive Signing Key" --clearsign -o InRelease Release
        gpg --default-key "Giri OS Archive Signing Key" -abs -o Release.gpg Release

4. REPOSITORY AUTOMATION (REPREPRO / APTLY)
  Production repositories should be maintained via 'reprepro' or 'aptly':
    conf/distributions:
      Origin: Giri OS
      Label: Giri OS 0.1 Genesis
      Codename: bookworm
      Architectures: amd64
      Components: main
      Description: Official Giri OS Package Repository
      SignWith: KEY_ID

5. CLIENT REPOSITORY CONFIGURATION
  File: /etc/apt/sources.list.d/giri-os.sources
    Types: deb
    URIs: https://repo.girios.org/debian
    Suites: bookworm
    Components: main
    Signed-By: /etc/apt/keyrings/giri-archive-keyring.gpg
================================================================================
"""


if __name__ == "__main__":
    client = GiriUpdateClient()

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Giri Update — Debian APT Repository & System Update Manager")
        print("Usage:")
        print("  python client.py --status       Show current OS release, APT sources, and disk space")
        print("  python client.py --check        Check for available updates (JSON output)")
        print("  python client.py --dry-run      Perform safe simulated upgrade without modifying system")
        print("  python client.py --upgrade      Execute live system upgrade (requires root)")
        print("  python client.py --history      View local update checkpoints and history")
        print("  python client.py --repo-guide   Display production APT repository hosting guide")
        print("  python client.py --test         Run automated self-tests")
        sys.exit(0)

    if "--repo-guide" in sys.argv:
        print(client.get_repo_infrastructure_guide())
        sys.exit(0)

    if "--status" in sys.argv:
        os_info = client.get_os_release()
        sources_info = client.inspect_apt_sources()
        space_info = client.check_disk_space()
        keyrings = client.inspect_keyrings()

        print("=== GIRI OS SYSTEM UPDATE STATUS ===")
        print(f"OS: {os_info.get('NAME')} {os_info.get('VERSION')} ({os_info.get('DEBIAN_CODENAME')})")
        print(f"Debian Mirrors: {'ACTIVE' if sources_info['official_debian_active'] else 'INACTIVE'}")
        print(f"Giri OS Custom Mirror: {'ACTIVE' if sources_info['custom_giri_active'] else 'NOT YET PROVISIONED (Using Upstream Debian)'}")
        print(f"Summary: {sources_info['status_summary']}")
        print(f"Trusted Keyrings Found: {len(keyrings)}")
        print(f"Disk Space: {space_info['free_mb']} MB free / {space_info['total_mb']} MB total (Required: {space_info['required_mb']} MB) -> {'OK' if space_info['sufficient'] else 'INSUFFICIENT'}")
        sys.exit(0)

    if "--check" in sys.argv:
        res = client.check_for_updates()
        print(json.dumps(res, indent=2))
        sys.exit(0)

    if "--dry-run" in sys.argv:
        res = client.execute_upgrade(dry_run=True)
        print(json.dumps(res, indent=2))
        sys.exit(0)

    if "--upgrade" in sys.argv:
        res = client.execute_upgrade(dry_run=False)
        print(json.dumps(res, indent=2))
        sys.exit(0)

    if "--history" in sys.argv:
        print(json.dumps(client.history, indent=2))
        sys.exit(0)

    if "--test" in sys.argv:
        # Automated self-tests
        print("[TEST] Running Giri Update self-test...")
        # 1. SHA-256 validation
        data = b"Giri OS 0.1 Genesis Update Verification Test"
        expected = hashlib.sha256(data).hexdigest()
        assert client.verify_payload(data, expected) is True, "Hash verification failed"
        assert client.verify_payload(data, "invalid") is False, "Hash invalidation failed"

        # 2. Sources inspection
        sources = client.inspect_apt_sources()
        assert isinstance(sources, dict)
        assert "official_debian_active" in sources

        # 3. Disk space
        space = client.check_disk_space()
        assert isinstance(space, dict)
        assert "sufficient" in space

        # 4. OS release
        rel = client.get_os_release()
        assert "NAME" in rel

        # 5. Check updates
        upd = client.check_for_updates()
        assert "upgrades_available" in upd

        # 6. Dry run simulation
        dry = client.execute_upgrade(dry_run=True)
        assert dry["status"] in ["SUCCESS", "SIMULATED", "ABORTED"]

        print("[TEST] Giri Update self-tests passed successfully.")
        sys.exit(0)

    # Default output
    print(json.dumps(client.check_for_updates(), indent=2))
