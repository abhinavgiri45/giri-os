#!/usr/bin/env bash
# ====================================================================
# GIRI OS 0.1 "Genesis" — Master ISO Build Script
# Author: Abhinav Giri / Giri OS Core Engineering Team
# License: GPL-3.0-or-later
# Base: Debian 12 (Bookworm) amd64
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

# Ensure DEBOOTSTRAP_OPTIONS points to Debian archive keyring when running on Ubuntu
export DEBOOTSTRAP_OPTIONS="${DEBOOTSTRAP_OPTIONS:---keyring=/usr/share/keyrings/debian-archive-keyring.gpg}"

# 2. Disk Space Safety Check
echo "[+] Checking available disk space..."
mkdir -p "${LIVE_BUILD_DIR}"
mkdir -p "${RELEASES_DIR}"
AVAILABLE_KB=$(df -P "${LIVE_BUILD_DIR}" | awk 'NR==2 {print $4}')
REQUIRED_KB=$((12 * 1024 * 1024)) # 12 GB in KB minimum

if [[ "${AVAILABLE_KB}" -lt "${REQUIRED_KB}" ]]; then
    echo "[-] Error: Insufficient free disk space."
    echo "    Available: $((AVAILABLE_KB / 1024 / 1024)) GB"
    echo "    Required:  12 GB minimum for Debian live-build caching and squashfs."
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

# Ensure executable permissions on helper scripts and hooks
chmod +x "${LIVE_BUILD_DIR}/auto/"* 2>/dev/null || true
chmod +x "${LIVE_BUILD_DIR}/config/hooks/live/"* 2>/dev/null || true

# Patch live-build helper scripts for Debian Bookworm archive layout and bootloader compatibility
if [ -f "${PROJECT_ROOT}/scripts/patch-live-build.py" ]; then
    echo "[+] Running Giri OS live-build compatibility patcher..."
    python3 "${PROJECT_ROOT}/scripts/patch-live-build.py" || true
fi

# Dereference and replace any symlinks in host live-build bootloader templates with actual binaries
if [ -d /usr/share/live/build/bootloaders ]; then
    echo "[+] Resolving and dereferencing bootloader template symlinks in /usr/share/live/build/bootloaders..."
    for bin_path in /usr/lib/ISOLINUX/isolinux.bin /usr/share/isolinux/isolinux.bin /usr/lib/syslinux/isolinux.bin; do
        if [ -f "$bin_path" ]; then
            cp -fL "$bin_path" /usr/share/live/build/bootloaders/isolinux/isolinux.bin 2>/dev/null || true
            break
        fi
    done
    for mod in vesamenu.c32 ldlinux.c32 libcom32.c32 libutil.c32 libmenu.c32 libgpl.c32 hdt.c32 chain.c32 menu.c32; do
        find /usr/lib/syslinux /usr/share/syslinux -name "$mod" -exec cp -fL {} /usr/share/live/build/bootloaders/syslinux_common/ 2>/dev/null \; || true
        find /usr/lib/syslinux /usr/share/syslinux -name "$mod" -exec cp -fL {} /usr/share/live/build/bootloaders/isolinux/ 2>/dev/null \; || true
    done
fi

# 4. Stage Chroot Overlays (Branding, Themes, Desktop, Core Services)
echo "[+] Staging Giri OS branding and desktop components into chroot overlays..."
INCLUDES_CHROOT="${LIVE_BUILD_DIR}/config/includes.chroot"
mkdir -p "${INCLUDES_CHROOT}/usr/share/plymouth/themes/giri-orbit"
mkdir -p "${INCLUDES_CHROOT}/usr/share/grub/themes/giri"
mkdir -p "${INCLUDES_CHROOT}/usr/share/backgrounds/thumbnails"
mkdir -p "${INCLUDES_CHROOT}/usr/share/pixmaps"
mkdir -p "${INCLUDES_CHROOT}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${INCLUDES_CHROOT}/usr/share/icons/hicolor/48x48/apps"
mkdir -p "${INCLUDES_CHROOT}/usr/share/applications"
mkdir -p "${INCLUDES_CHROOT}/usr/share/giri-space"
mkdir -p "${INCLUDES_CHROOT}/usr/lib/giri/hardware"
mkdir -p "${INCLUDES_CHROOT}/usr/lib/giri/compatibility"
mkdir -p "${INCLUDES_CHROOT}/usr/lib/giri/gaming"
mkdir -p "${INCLUDES_CHROOT}/usr/lib/giri/updater"
mkdir -p "${INCLUDES_CHROOT}/usr/lib/giri/first-boot"
mkdir -p "${INCLUDES_CHROOT}/etc/calamares/modules"
mkdir -p "${INCLUDES_CHROOT}/etc/calamares/branding/giri"
mkdir -p "${INCLUDES_CHROOT}/usr/share/calamares/branding/giri"
mkdir -p "${INCLUDES_CHROOT}/etc/skel/Desktop"

# 4a. Copy Wallpapers, Thumbnails, Metadata & Logos
cp -f "${PROJECT_ROOT}/branding/wallpapers/"*.png "${INCLUDES_CHROOT}/usr/share/backgrounds/" || true
cp -f "${PROJECT_ROOT}/branding/wallpapers/"*.svg "${INCLUDES_CHROOT}/usr/share/backgrounds/" || true
cp -f "${PROJECT_ROOT}/branding/wallpapers/"*.json "${INCLUDES_CHROOT}/usr/share/backgrounds/" || true
cp -f "${PROJECT_ROOT}/branding/wallpapers/thumbnails/"*.png "${INCLUDES_CHROOT}/usr/share/backgrounds/thumbnails/" || true
cp -f "${PROJECT_ROOT}/branding/logo/"*.svg "${INCLUDES_CHROOT}/usr/share/backgrounds/" || true
cp -f "${PROJECT_ROOT}/branding/logo/"*.png "${INCLUDES_CHROOT}/usr/share/backgrounds/" || true
cp -f "${PROJECT_ROOT}/branding/logo/giri-os-icon.png" "${INCLUDES_CHROOT}/usr/share/pixmaps/giri-os-icon.png" || true
cp -f "${PROJECT_ROOT}/branding/logo/giri-os-icon.svg" "${INCLUDES_CHROOT}/usr/share/icons/hicolor/scalable/apps/giri-os-icon.svg" || true
cp -f "${PROJECT_ROOT}/branding/logo/giri-os-icon.png" "${INCLUDES_CHROOT}/usr/share/icons/hicolor/48x48/apps/giri-os-icon.png" || true

# 4b. Copy Plymouth Theme
cp -rf "${PROJECT_ROOT}/boot/plymouth/giri-orbit/"* "${INCLUDES_CHROOT}/usr/share/plymouth/themes/giri-orbit/"

# 4c. Copy GRUB Theme
cp -rf "${PROJECT_ROOT}/boot/grub/"* "${INCLUDES_CHROOT}/usr/share/grub/themes/giri/"

# 4d. Copy Giri Space Desktop
cp -rf "${PROJECT_ROOT}/desktop/giri-space/"* "${INCLUDES_CHROOT}/usr/share/giri-space/"

# 4e. Copy Core Giri Subsystems
cp -rf "${PROJECT_ROOT}/hardware/"* "${INCLUDES_CHROOT}/usr/lib/giri/hardware/"
cp -rf "${PROJECT_ROOT}/compatibility/"* "${INCLUDES_CHROOT}/usr/lib/giri/compatibility/"
cp -rf "${PROJECT_ROOT}/gaming/"* "${INCLUDES_CHROOT}/usr/lib/giri/gaming/"
cp -rf "${PROJECT_ROOT}/updater/"* "${INCLUDES_CHROOT}/usr/lib/giri/updater/"
cp -rf "${PROJECT_ROOT}/installer/first-boot/"* "${INCLUDES_CHROOT}/usr/lib/giri/first-boot/"

# 4f. Copy Calamares Installer Settings & Modules
cp -f "${PROJECT_ROOT}/installer/calamares/settings.conf" "${INCLUDES_CHROOT}/etc/calamares/" || true
cp -rf "${PROJECT_ROOT}/installer/calamares/modules/"* "${INCLUDES_CHROOT}/etc/calamares/modules/" || true
cp -f "${PROJECT_ROOT}/installer/calamares/modules/branding.desc" "${INCLUDES_CHROOT}/etc/calamares/branding/giri/branding.desc" || true
cp -f "${PROJECT_ROOT}/installer/calamares/modules/branding.desc" "${INCLUDES_CHROOT}/usr/share/calamares/branding/giri/branding.desc" || true

# 4g. Copy System release files and configurations
cp -f "${PROJECT_ROOT}/system/etc/os-release" "${INCLUDES_CHROOT}/etc/os-release"
cp -f "${PROJECT_ROOT}/system/etc/issue" "${INCLUDES_CHROOT}/etc/issue"
cp -f "${PROJECT_ROOT}/system/etc/lsb-release" "${INCLUDES_CHROOT}/etc/lsb-release"
cp -f "${PROJECT_ROOT}/system/etc/giri-wallpaper.json" "${INCLUDES_CHROOT}/etc/giri-wallpaper.json" || true
cp -f "${PROJECT_ROOT}/system/etc/giri-desktop-prefs.json" "${INCLUDES_CHROOT}/etc/giri-desktop-prefs.json" || true

# 4h. Copy Desktop shortcuts to /etc/skel/Desktop and /usr/share/applications
cp -f "${PROJECT_ROOT}/desktop/giri-space/shortcuts/"*.desktop "${INCLUDES_CHROOT}/etc/skel/Desktop/" || true
cp -f "${PROJECT_ROOT}/desktop/giri-space/shortcuts/"*.desktop "${INCLUDES_CHROOT}/usr/share/applications/" || true

# 4i. Stage Binary ISO Bootloader Assets (GRUB and ISOLINUX)
echo "[+] Staging binary bootloader configurations for hybrid BIOS/UEFI boot..."
INCLUDES_BINARY="${LIVE_BUILD_DIR}/config/includes.binary"
BOOTLOADERS_ISOLINUX="${LIVE_BUILD_DIR}/config/bootloaders/isolinux"
BOOTLOADERS_COMMON="${LIVE_BUILD_DIR}/config/bootloaders/syslinux_common"

mkdir -p "${INCLUDES_BINARY}/boot/grub/themes/giri"
mkdir -p "${INCLUDES_BINARY}/isolinux"
mkdir -p "${BOOTLOADERS_ISOLINUX}"
mkdir -p "${BOOTLOADERS_COMMON}"
mkdir -p "${INCLUDES_CHROOT}/usr/lib/ISOLINUX"
mkdir -p "${INCLUDES_CHROOT}/usr/lib/syslinux/modules/bios"

cp -f "${PROJECT_ROOT}/boot/grub/grub.cfg" "${INCLUDES_BINARY}/boot/grub/grub.cfg" || true
cp -rf "${PROJECT_ROOT}/boot/grub/"* "${INCLUDES_BINARY}/boot/grub/themes/giri/" || true
cp -f "${PROJECT_ROOT}/boot/isolinux/isolinux.cfg" "${INCLUDES_BINARY}/isolinux/isolinux.cfg" || true
cp -f "${PROJECT_ROOT}/boot/isolinux/isolinux.cfg" "${BOOTLOADERS_ISOLINUX}/isolinux.cfg" || true

# Copy real isolinux.bin and isohdpfx.bin into bootloaders, includes.binary, and includes.chroot
for bin_path in /usr/lib/ISOLINUX/isolinux.bin /usr/share/isolinux/isolinux.bin /usr/lib/syslinux/isolinux.bin; do
    if [ -f "${bin_path}" ]; then
        cp -fL "${bin_path}" "${BOOTLOADERS_ISOLINUX}/isolinux.bin"
        cp -fL "${bin_path}" "${INCLUDES_BINARY}/isolinux/isolinux.bin"
        cp -fL "${bin_path}" "${INCLUDES_CHROOT}/usr/lib/ISOLINUX/isolinux.bin"
        break
    fi
done

for mbr_path in /usr/lib/ISOLINUX/isohdpfx.bin /usr/share/isolinux/isohdpfx.bin /usr/lib/syslinux/isohdpfx.bin; do
    if [ -f "${mbr_path}" ]; then
        cp -fL "${mbr_path}" "${BOOTLOADERS_ISOLINUX}/isohdpfx.bin"
        cp -fL "${mbr_path}" "${INCLUDES_CHROOT}/usr/lib/ISOLINUX/isohdpfx.bin"
        break
    fi
done

# Copy real COM32 modules into bootloaders, includes.binary, and includes.chroot
for mod in vesamenu.c32 ldlinux.c32 libcom32.c32 libutil.c32 libmenu.c32 libgpl.c32 hdt.c32 chain.c32 menu.c32; do
    find /usr/lib/syslinux /usr/share/syslinux -name "${mod}" -exec cp -fL {} "${BOOTLOADERS_COMMON}/" \; 2>/dev/null || true
    find /usr/lib/syslinux /usr/share/syslinux -name "${mod}" -exec cp -fL {} "${BOOTLOADERS_ISOLINUX}/" \; 2>/dev/null || true
    find /usr/lib/syslinux /usr/share/syslinux -name "${mod}" -exec cp -fL {} "${INCLUDES_BINARY}/isolinux/" \; 2>/dev/null || true
    find /usr/lib/syslinux /usr/share/syslinux -name "${mod}" -exec cp -fL {} "${INCLUDES_CHROOT}/usr/lib/syslinux/modules/bios/" \; 2>/dev/null || true
done

# Provide fallback bootlogo cpio archive for Ubuntu live-build host tool compatibility
echo -n "" | cpio -o -H newc > "${BOOTLOADERS_ISOLINUX}/bootlogo" 2>/dev/null || touch "${BOOTLOADERS_ISOLINUX}/bootlogo" || true
cp -f "${BOOTLOADERS_ISOLINUX}/bootlogo" "${INCLUDES_BINARY}/isolinux/bootlogo" 2>/dev/null || true

# Stage isohybrid utility directly into chroot overlays
if command -v isohybrid >/dev/null 2>&1; then
    mkdir -p "${INCLUDES_CHROOT}/usr/bin"
    cp -fL "$(command -v isohybrid)" "${INCLUDES_CHROOT}/usr/bin/isohybrid"
    chmod +x "${INCLUDES_CHROOT}/usr/bin/isohybrid"
fi

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
sha256sum "giri-os-0.1-genesis-amd64.iso" > "SHA256SUMS.txt"
cp -f "SHA256SUMS.txt" "SHA256SUMS"

ISO_SIZE_BYTES=$(stat -c%s "${TARGET_ISO}")
ISO_SIZE_MB=$((ISO_SIZE_BYTES / 1024 / 1024))

echo "======================================================================"
echo "[+] BUILD SUCCESSFUL!"
echo "    ISO Artifact: ${TARGET_ISO}"
echo "    Size:         ${ISO_SIZE_MB} MB (${ISO_SIZE_BYTES} bytes)"
echo "    Checksum:     $(cat SHA256SUMS.txt)"
echo "    To test:      ./scripts/test-qemu.sh"
echo "======================================================================"
