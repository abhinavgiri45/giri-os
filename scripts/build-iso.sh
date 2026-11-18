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
mkdir -p "${LIVE_BUILD_DIR}/config/hooks/binary"
if [ -f "${LIVE_BUILD_DIR}/config/hooks/live/99-link-canonical-kernel.hook.binary" ]; then
    cp -f "${LIVE_BUILD_DIR}/config/hooks/live/99-link-canonical-kernel.hook.binary" "${LIVE_BUILD_DIR}/config/hooks/binary/99-link-canonical-kernel.hook.binary" 2>/dev/null || true
fi
chmod +x "${LIVE_BUILD_DIR}/auto/"* 2>/dev/null || true
chmod +x "${LIVE_BUILD_DIR}/config/hooks/live/"* 2>/dev/null || true
chmod +x "${LIVE_BUILD_DIR}/config/hooks/binary/"* 2>/dev/null || true

# Patch live-build helper scripts for Debian Bookworm archive layout and bootloader compatibility
if [ -f "${PROJECT_ROOT}/scripts/patch-live-build.py" ]; then
    echo "[+] Running Giri OS live-build compatibility patcher..."
    python3 "${PROJECT_ROOT}/scripts/patch-live-build.py" || true
fi

# Helper: Locate and copy 32-bit BIOS Syslinux COM32 modules (strictly excluding 64-bit EFI modules)
copy_bios_com32_module() {
    local mod="$1"
    local dest_dir="$2"
    local found=""

    # Prioritized search list: explicit 32-bit BIOS syslinux module paths
    for candidate in \
        "/usr/lib/syslinux/modules/bios/${mod}" \
        "/usr/lib/ISOLINUX/${mod}" \
        "/usr/share/syslinux/themes/debian-bookworm/isolinux-live/${mod}" \
        "/usr/share/syslinux/${mod}"; do
        if [ -f "${candidate}" ]; then
            case "${candidate}" in
                *efi*) ;; # Explicitly skip 64-bit EFI modules
                *) found="${candidate}"; break ;;
            esac
        fi
    done

    # Fallback search strictly excluding any path containing 'efi'
    if [ -z "${found}" ]; then
        found=$(find /usr/lib/syslinux /usr/share/syslinux -not -path "*/efi*" -name "${mod}" 2>/dev/null | head -n 1 || true)
    fi

    if [ -n "${found}" ] && [ -f "${found}" ]; then
        mkdir -p "${dest_dir}"
        # Remove any existing destination file or dangling symlink first to prevent cp write-through errors
        rm -f "${dest_dir}/${mod}" 2>/dev/null || true
        cp -fL "${found}" "${dest_dir}/${mod}" 2>/dev/null || cp -f "${found}" "${dest_dir}/${mod}" || true
    fi
}

# Dereference and replace any symlinks in host live-build bootloader templates with actual binaries
if [ -d /usr/share/live/build/bootloaders ]; then
    echo "[+] Resolving and dereferencing bootloader template symlinks in /usr/share/live/build/bootloaders..."
    for bin_path in /usr/lib/ISOLINUX/isolinux.bin /usr/share/isolinux/isolinux.bin /usr/lib/syslinux/isolinux.bin; do
        if [ -f "$bin_path" ]; then
            rm -f /usr/share/live/build/bootloaders/isolinux/isolinux.bin 2>/dev/null || true
            cp -fL "$bin_path" /usr/share/live/build/bootloaders/isolinux/isolinux.bin 2>/dev/null || true
            break
        fi
    done
    for mod in vesamenu.c32 ldlinux.c32 libcom32.c32 libutil.c32 libmenu.c32 libgpl.c32 hdt.c32 chain.c32 menu.c32; do
        copy_bios_com32_module "$mod" /usr/share/live/build/bootloaders/syslinux_common
        copy_bios_com32_module "$mod" /usr/share/live/build/bootloaders/isolinux
    done
fi

# 4. Stage Chroot Overlays (Branding, Themes, Desktop, Core Services)
echo "[+] Staging Giri OS branding and desktop components into chroot overlays..."
INCLUDES_CHROOT="${LIVE_BUILD_DIR}/config/includes.chroot"
mkdir -p "${INCLUDES_CHROOT}/usr/share/plymouth/themes/giri-genesis"
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
cp -rf "${PROJECT_ROOT}/boot/plymouth/giri-genesis/"* "${INCLUDES_CHROOT}/usr/share/plymouth/themes/giri-genesis/"

# 4c. Copy GRUB Theme
cp -rf "${PROJECT_ROOT}/boot/grub/"* "${INCLUDES_CHROOT}/usr/share/grub/themes/giri/"

# 4d. Copy Giri Space Desktop
cp -rf "${PROJECT_ROOT}/desktop/giri-space/"* "${INCLUDES_CHROOT}/usr/share/giri-space/"
mkdir -p "${INCLUDES_CHROOT}/usr/share/xsessions"
cp -f "${PROJECT_ROOT}/desktop/giri-space/session/"*.desktop "${INCLUDES_CHROOT}/usr/share/xsessions/" || true

# 4e. Copy Core Giri Subsystems
cp -rf "${PROJECT_ROOT}/hardware/"* "${INCLUDES_CHROOT}/usr/lib/giri/hardware/"
cp -rf "${PROJECT_ROOT}/compatibility/"* "${INCLUDES_CHROOT}/usr/lib/giri/compatibility/"
cp -rf "${PROJECT_ROOT}/gaming/"* "${INCLUDES_CHROOT}/usr/lib/giri/gaming/"
cp -rf "${PROJECT_ROOT}/updater/"* "${INCLUDES_CHROOT}/usr/lib/giri/updater/"
cp -rf "${PROJECT_ROOT}/installer/first-boot/"* "${INCLUDES_CHROOT}/usr/lib/giri/first-boot/"
mkdir -p "${INCLUDES_CHROOT}/usr/bin"

# Ensure execution permissions on all session scripts and core binaries
chmod +x "${INCLUDES_CHROOT}/usr/share/giri-space/session/giri-session" 2>/dev/null || true
chmod +x "${INCLUDES_CHROOT}/usr/share/giri-space/shell/"*.py 2>/dev/null || true
chmod +x "${INCLUDES_CHROOT}/usr/share/giri-space/control-center/"*.py 2>/dev/null || true
chmod +x "${INCLUDES_CHROOT}/usr/share/giri-space/launcher/"*.py 2>/dev/null || true
chmod +x "${INCLUDES_CHROOT}/usr/share/giri-space/shortcuts/"*.py 2>/dev/null || true
chmod +x "${INCLUDES_CHROOT}/usr/lib/giri/hardware/giri-hw/"*.py 2>/dev/null || true
chmod +x "${INCLUDES_CHROOT}/usr/lib/giri/compatibility/giri-bridge/"*.py 2>/dev/null || true
chmod +x "${INCLUDES_CHROOT}/usr/lib/giri/gaming/giri-gaming/"*.py 2>/dev/null || true
chmod +x "${INCLUDES_CHROOT}/usr/lib/giri/updater/giri-update/"*.py 2>/dev/null || true
chmod +x "${INCLUDES_CHROOT}/usr/lib/giri/first-boot/"*.py 2>/dev/null || true

# Direct binary in /usr/bin with explicit 0755 permissions
cp -f "${PROJECT_ROOT}/desktop/giri-space/session/giri-session" "${INCLUDES_CHROOT}/usr/bin/giri-session" 2>/dev/null || true
chmod 0755 "${INCLUDES_CHROOT}/usr/bin/giri-session" 2>/dev/null || true
chmod 0755 "${INCLUDES_CHROOT}/usr/share/giri-space/session/giri-session" 2>/dev/null || true
ln -sf /usr/share/xsessions/giri-space-classic.desktop "${INCLUDES_CHROOT}/usr/share/xsessions/default.desktop" 2>/dev/null || true
ln -sf /usr/share/giri-space/shell/giri_space.py "${INCLUDES_CHROOT}/usr/bin/giri-space" 2>/dev/null || true
ln -sf /usr/lib/giri/hardware/giri-hw/detector.py "${INCLUDES_CHROOT}/usr/bin/giri-hw" 2>/dev/null || true
ln -sf /usr/lib/giri/compatibility/giri-bridge/runner.py "${INCLUDES_CHROOT}/usr/bin/giri-bridge" 2>/dev/null || true
ln -sf /usr/lib/giri/gaming/giri-gaming/governor.py "${INCLUDES_CHROOT}/usr/bin/giri-game" 2>/dev/null || true
ln -sf /usr/lib/giri/updater/giri-update/client.py "${INCLUDES_CHROOT}/usr/bin/giri-update" 2>/dev/null || true
ln -sf /usr/share/giri-space/session/giri_recovery.py "${INCLUDES_CHROOT}/usr/bin/giri-recovery" 2>/dev/null || true
chmod 0755 "${INCLUDES_CHROOT}/usr/share/giri-space/session/giri_recovery.py" 2>/dev/null || true

# Display setup script to cleanly terminate Plymouth and initialize xrandr
cat << 'EOF' > "${INCLUDES_CHROOT}/usr/bin/giri-display-setup"
#!/bin/sh
if command -v plymouth >/dev/null 2>&1; then
    plymouth --quit || true
fi
if command -v xrandr >/dev/null 2>&1; then
    xrandr --auto || true
fi
exit 0
EOF
chmod +x "${INCLUDES_CHROOT}/usr/bin/giri-display-setup"

# Preconfigure LightDM in includes.chroot
mkdir -p "${INCLUDES_CHROOT}/etc/lightdm/lightdm.conf.d"
cat << 'EOF' > "${INCLUDES_CHROOT}/etc/lightdm/lightdm.conf.d/01-giri-defaults.conf"
[Seat:*]
greeter-session=lightdm-gtk-greeter
user-session=giri-space-classic
autologin-user=giri
autologin-user-timeout=0
display-setup-script=/usr/bin/giri-display-setup
EOF
cat << 'EOF' > "${INCLUDES_CHROOT}/usr/bin/giri-welcome"
#!/bin/sh
exec python3 /usr/lib/giri/first-boot/giri_welcome.py "$@"
EOF
chmod +x "${INCLUDES_CHROOT}/usr/bin/giri-welcome"

cat << 'EOF' > "${INCLUDES_CHROOT}/usr/bin/giri-firstboot"
#!/bin/sh
exec python3 /usr/lib/giri/first-boot/first_boot_wizard.py "$@"
EOF
chmod +x "${INCLUDES_CHROOT}/usr/bin/giri-firstboot"

cat << 'EOF' > "${INCLUDES_CHROOT}/usr/bin/giri-search"
#!/bin/sh
exec python3 /usr/share/giri-space/launcher/quick_search.py "$@"
EOF
chmod +x "${INCLUDES_CHROOT}/usr/bin/giri-search"

cat << 'EOF' > "${INCLUDES_CHROOT}/usr/bin/giri-snip"
#!/bin/sh
exec python3 /usr/share/giri-space/shortcuts/giri_snip.py "$@"
EOF
chmod +x "${INCLUDES_CHROOT}/usr/bin/giri-snip"

cat << 'EOF' > "${INCLUDES_CHROOT}/usr/bin/giri-nightlight"
#!/bin/sh
exec python3 /usr/share/giri-space/shell/giri_nightlight.py "$@"
EOF
chmod +x "${INCLUDES_CHROOT}/usr/bin/giri-nightlight"

cat << 'EOF' > "${INCLUDES_CHROOT}/usr/bin/giri-control"
#!/bin/sh
exec python3 /usr/share/giri-space/control-center/control_center.py "$@"
EOF
chmod +x "${INCLUDES_CHROOT}/usr/bin/giri-control"

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

# 4h. Copy Desktop shortcuts and user skeleton configs
cp -f "${PROJECT_ROOT}/desktop/giri-space/shortcuts/"*.desktop "${INCLUDES_CHROOT}/etc/skel/Desktop/" || true
cp -f "${PROJECT_ROOT}/desktop/giri-space/shortcuts/"*.desktop "${INCLUDES_CHROOT}/usr/share/applications/" || true
mkdir -p "${INCLUDES_CHROOT}/etc/skel/.config/openbox"
cp -rf "${PROJECT_ROOT}/system/skel/.config/openbox/"* "${INCLUDES_CHROOT}/etc/skel/.config/openbox/" 2>/dev/null || true

# 4i. Stage Binary ISO Bootloader Assets (GRUB and ISOLINUX)
echo "[+] Staging binary bootloader configurations for hybrid BIOS/UEFI boot..."
INCLUDES_BINARY="${LIVE_BUILD_DIR}/config/includes.binary"
BOOTLOADERS_ISOLINUX="${LIVE_BUILD_DIR}/config/bootloaders/isolinux"
BOOTLOADERS_COMMON="${LIVE_BUILD_DIR}/config/bootloaders/syslinux_common"
BOOTLOADERS_GRUBEFI="${LIVE_BUILD_DIR}/config/bootloaders/grub-efi"

mkdir -p "${INCLUDES_BINARY}/boot/grub/themes/giri"
mkdir -p "${INCLUDES_BINARY}/isolinux"
mkdir -p "${BOOTLOADERS_ISOLINUX}"
mkdir -p "${BOOTLOADERS_COMMON}"
mkdir -p "${BOOTLOADERS_GRUBEFI}"
mkdir -p "${INCLUDES_CHROOT}/usr/lib/ISOLINUX"
mkdir -p "${INCLUDES_CHROOT}/usr/lib/syslinux/modules/bios"

cp -f "${PROJECT_ROOT}/boot/grub/grub.cfg" "${INCLUDES_BINARY}/boot/grub/grub.cfg" || true
cp -rf "${PROJECT_ROOT}/boot/grub/"* "${INCLUDES_BINARY}/boot/grub/themes/giri/" || true
cp -f "${PROJECT_ROOT}/boot/grub/grub.cfg" "${BOOTLOADERS_GRUBEFI}/grub.cfg" || true
cp -rf "${PROJECT_ROOT}/boot/grub/"* "${BOOTLOADERS_GRUBEFI}/" || true
cp -f "${PROJECT_ROOT}/boot/isolinux/isolinux.cfg" "${INCLUDES_BINARY}/isolinux/isolinux.cfg" || true
cp -f "${PROJECT_ROOT}/boot/isolinux/isolinux.cfg" "${BOOTLOADERS_ISOLINUX}/isolinux.cfg" || true

# Copy real isolinux.bin and isohdpfx.bin into bootloaders, includes.binary, and includes.chroot
for bin_path in /usr/lib/ISOLINUX/isolinux.bin /usr/share/isolinux/isolinux.bin /usr/lib/syslinux/isolinux.bin; do
    if [ -f "${bin_path}" ]; then
        rm -f "${BOOTLOADERS_ISOLINUX}/isolinux.bin" 2>/dev/null || true
        cp -fL "${bin_path}" "${BOOTLOADERS_ISOLINUX}/isolinux.bin" 2>/dev/null || true
        rm -f "${INCLUDES_BINARY}/isolinux/isolinux.bin" 2>/dev/null || true
        cp -fL "${bin_path}" "${INCLUDES_BINARY}/isolinux/isolinux.bin" 2>/dev/null || true
        rm -f "${INCLUDES_CHROOT}/usr/lib/ISOLINUX/isolinux.bin" 2>/dev/null || true
        cp -fL "${bin_path}" "${INCLUDES_CHROOT}/usr/lib/ISOLINUX/isolinux.bin" 2>/dev/null || true
        break
    fi
done

for mbr_path in /usr/lib/ISOLINUX/isohdpfx.bin /usr/share/isolinux/isohdpfx.bin /usr/lib/syslinux/isohdpfx.bin; do
    if [ -f "${mbr_path}" ]; then
        rm -f "${BOOTLOADERS_ISOLINUX}/isohdpfx.bin" 2>/dev/null || true
        cp -fL "${mbr_path}" "${BOOTLOADERS_ISOLINUX}/isohdpfx.bin" 2>/dev/null || true
        rm -f "${INCLUDES_CHROOT}/usr/lib/ISOLINUX/isohdpfx.bin" 2>/dev/null || true
        cp -fL "${mbr_path}" "${INCLUDES_CHROOT}/usr/lib/ISOLINUX/isohdpfx.bin" 2>/dev/null || true
        break
    fi
done

# Copy real 32-bit BIOS COM32 modules into bootloaders, includes.binary, and includes.chroot
for mod in vesamenu.c32 ldlinux.c32 libcom32.c32 libutil.c32 libmenu.c32 libgpl.c32 hdt.c32 chain.c32 menu.c32; do
    copy_bios_com32_module "${mod}" "${BOOTLOADERS_COMMON}"
    copy_bios_com32_module "${mod}" "${BOOTLOADERS_ISOLINUX}"
    copy_bios_com32_module "${mod}" "${INCLUDES_BINARY}/isolinux"
    copy_bios_com32_module "${mod}" "${INCLUDES_CHROOT}/usr/lib/syslinux/modules/bios"
done

# Verify that all staged COM32 modules are genuine 32-bit BIOS modules (not 64-bit EFI)
echo "[+] Verifying staged BIOS COM32 module architectures..."
for staged_mod in "${INCLUDES_BINARY}/isolinux/"*.c32; do
    if [ -f "${staged_mod}" ]; then
        if command -v python3 >/dev/null 2>&1; then
            python3 -c "
import sys
with open('${staged_mod}', 'rb') as f:
    hdr = f.read(16)
    if hdr.startswith(b'\x7fELF'):
        ei_class = hdr[4]
        if ei_class == 2:
            print('[-] ERROR: ${staged_mod} is a 64-bit ELF binary, incompatible with BIOS COM32!')
            sys.exit(1)
"
        fi
    fi
done
echo "[+] Staged BIOS COM32 modules verified (32-bit BIOS compatible)."

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
ISO_FILENAME="${ISO_FILENAME:-giri-os-0.1-genesis-v6-amd64.iso}"
TARGET_ISO="${RELEASES_DIR}/${ISO_FILENAME}"
mv -f "${ISO_OUTPUT}" "${TARGET_ISO}"

echo "[+] Computing SHA-256 checksum..."
cd "${RELEASES_DIR}"
sha256sum "${ISO_FILENAME}" > "SHA256SUMS.txt"
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
