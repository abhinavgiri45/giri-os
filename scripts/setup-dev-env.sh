#!/usr/bin/env bash
# ====================================================================
# GIRI OS — Development Environment Setup Script
# Installs all required compilers, live-build tools, and QEMU
# ====================================================================

set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
    echo "[-] Error: Please run with sudo: sudo $0"
    exit 1
fi

echo "[+] Updating Debian / Ubuntu package lists..."
apt-get update

echo "[+] Installing core distribution engineering toolchain..."
apt-get install -y \
    live-build \
    debootstrap \
    squashfs-tools \
    xorriso \
    isolinux \
    syslinux-common \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    dosfstools \
    python3 \
    python3-pip \
    python3-tk \
    python3-psutil \
    qemu-system-x86 \
    ovmf

echo "[+] Development toolchain installation complete."
