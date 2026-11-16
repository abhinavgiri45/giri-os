#!/usr/bin/env bash
# ====================================================================
# GIRI OS 0.1 "Genesis" — Master ISO Build Script
# Author: Abhinav Giri / Giri OS Core Engineering Team
# License: GPL-3.0-or-later
# ====================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LIVE_BUILD_DIR="${PROJECT_ROOT}/build/live-build"
RELEASES_DIR="${PROJECT_ROOT}/releases"

echo "======================================================================"
echo "          GIRI OS 0.1 'GENESIS' — OFFICIAL ISO BUILD PIPELINE          "
echo "                Founder & Lead Architect: Abhinav Giri                "
echo "                 One System. Infinite Possibilities.                  "
echo "======================================================================"

# 1. Privileges Pre-Flight Check
if [[ "${EUID}" -ne 0 ]]; then
    echo "[-] Error: ISO generation requires root privileges to configure chroot"
    echo "    and manage loop devices. Please re-run with: sudo $0"
    exit 1
fi

# 2. Disk Space Safety Check
echo "[+] Checking available disk space..."
AVAILABLE_KB=$(df -P "${LIVE_BUILD_DIR}" | awk 'NR==2 {print $4}')
REQUIRED_KB=$((15 * 1024 * 1024)) # 15 GB in KB

if [[ "${AVAILABLE_KB}" -lt "${REQUIRED_KB}" ]]; then
    echo "[-] Error: Insufficient free disk space."
    echo "    Available: $((AVAILABLE_KB / 1024 / 1024)) GB"
    echo "    Required:  15 GB minimum for Debian live-build caching and squashfs."
    exit 1
fi
echo "[+] Disk space verified: $((AVAILABLE_KB / 1024 / 1024)) GB free."

# 3. Check Required Tools
MISSING_TOOLS=()
for tool in lb debootstrap mksquashfs xorriso; do
    if ! command -v "${tool}" >/dev/null 2>&1; then
        MISSING_TOOLS+=("${tool}")
    fi
done

if [[ ${#MISSING_TOOLS[@]} -gt 0 ]]; then
    echo "[-] Error: Missing required build tools: ${MISSING_TOOLS[*]}"
    echo "    Please run: sudo ./scripts/setup-dev-env.sh"
    exit 1
fi

# 4. Stage Chroot Assets (Branding, Themes, Desktop components)
echo "[+] Staging Giri OS branding and desktop components into chroot overlays..."
INCLUDES_CHROOT="${LIVE_BUILD_DIR}/config/includes.chroot"
mkdir -p "${INCLUDES_CHROOT}/usr/share/plymouth/themes/giri-orbit"
mkdir -p "${INCLUDES_CHROOT}/usr/share/grub/themes/giri"
mkdir -p "${INCLUDES_CHROOT}/usr/share/backgrounds"
mkdir -p "${INCLUDES_CHROOT}/usr/share/giri-space"
mkdir -p "${INCLUDES_CHROOT}/etc"

# Copy Wallpapers & Logos
cp -f "${PROJECT_ROOT}/branding/wallpapers/"*.png "${INCLUDES_CHROOT}/usr/share/backgrounds/" || true
cp -f "${PROJECT_ROOT}/branding/wallpapers/"*.svg "${INCLUDES_CHROOT}/usr/share/backgrounds/" || true
cp -f "${PROJECT_ROOT}/branding/logo/"*.svg "${INCLUDES_CHROOT}/usr/share/backgrounds/" || true
cp -f "${PROJECT_ROOT}/branding/logo/"*.png "${INCLUDES_CHROOT}/usr/share/backgrounds/" || true

# Copy Plymouth Theme
cp -rf "${PROJECT_ROOT}/boot/plymouth/giri-orbit/"* "${INCLUDES_CHROOT}/usr/share/plymouth/themes/giri-orbit/"

# Copy GRUB Theme
cp -rf "${PROJECT_ROOT}/boot/grub/"* "${INCLUDES_CHROOT}/usr/share/grub/themes/giri/"

# Copy Giri Space Desktop
cp -rf "${PROJECT_ROOT}/desktop/giri-space/"* "${INCLUDES_CHROOT}/usr/share/giri-space/"

# Copy Calamares Installer Settings & Modules
mkdir -p "${INCLUDES_CHROOT}/etc/calamares/modules"
cp -f "${PROJECT_ROOT}/installer/calamares/settings.conf" "${INCLUDES_CHROOT}/etc/calamares/" || true
cp -rf "${PROJECT_ROOT}/installer/calamares/modules/"* "${INCLUDES_CHROOT}/etc/calamares/modules/" || true

# Copy System release files
cp -f "${PROJECT_ROOT}/system/etc/os-release" "${INCLUDES_CHROOT}/etc/os-release"
cp -f "${PROJECT_ROOT}/system/etc/issue" "${INCLUDES_CHROOT}/etc/issue"
cp -f "${PROJECT_ROOT}/system/etc/lsb-release" "${INCLUDES_CHROOT}/etc/lsb-release"

# 5. Execute Live-Build Process
echo "[+] Initializing live-build configuration..."
cd "${LIVE_BUILD_DIR}"
lb clean
lb config
echo "[+] Starting Debian base debootstrap and chroot assembly (this may take 15-30 minutes)..."
lb build

# 6. Archive and Checksum Resulting ISO
ISO_OUTPUT=$(ls -t "${LIVE_BUILD_DIR}"/*.iso 2>/dev/null | head -n 1 || true)
if [[ -z "${ISO_OUTPUT}" || ! -f "${ISO_OUTPUT}" ]]; then
    echo "[-] Error: Build completed without generating an ISO file."
    echo "    Please inspect build logs for chroot compilation errors."
    exit 1
fi

mkdir -p "${RELEASES_DIR}"
TARGET_ISO="${RELEASES_DIR}/giri-os-0.1-genesis-amd64.iso"
mv -f "${ISO_OUTPUT}" "${TARGET_ISO}"

echo "[+] Computing SHA-256 checksum..."
cd "${RELEASES_DIR}"
sha256sum "giri-os-0.1-genesis-amd64.iso" > "SHA256SUMS"

echo "======================================================================"
echo "[+] BUILD SUCCESSFUL!"
echo "    ISO Artifact: ${TARGET_ISO}"
echo "    Checksum:     $(cat SHA256SUMS)"
echo "    To test:      ./scripts/test-qemu.sh"
echo "======================================================================"
