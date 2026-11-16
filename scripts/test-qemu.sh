#!/usr/bin/env bash
# ====================================================================
# GIRI OS — QEMU Live ISO Virtual Machine Runner
# Tests the generated ISO safely in a virtual environment without touching disks
# ====================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ISO_PATH="${PROJECT_ROOT}/releases/giri-os-0.1-genesis-amd64.iso"

if [[ ! -f "${ISO_PATH}" ]]; then
    echo "[-] Error: ISO file not found at: ${ISO_PATH}"
    echo "    Please build the ISO first using: sudo ./scripts/build-iso.sh"
    exit 1
fi

echo "[+] Launching Giri OS 0.1 Genesis in QEMU Virtual Machine..."
echo "    Memory: 4 GB"
echo "    Cores:  4"
echo "    Display: VirtIO Graphics"

# Determine KVM acceleration
KVM_FLAG=""
if [[ -e /dev/kvm && -w /dev/kvm ]]; then
    KVM_FLAG="-enable-kvm"
fi

qemu-system-x86_64 \
    ${KVM_FLAG} \
    -m 4096 \
    -smp 4 \
    -vga virtio \
    -display default \
    -cdrom "${ISO_PATH}" \
    -boot d
