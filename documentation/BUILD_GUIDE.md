# Giri OS — Build & Development Guide

This guide provides complete instructions for setting up the Giri OS build toolchain, testing individual components, assembling Debian live-build configurations, and generating a bootable ISO.

---

## 1. Prerequisites & Environment Setup

Building a Debian-based Linux distribution requires a Linux userland with root privileges (to configure `chroot`, mount loopback filesystems, and create squashfs images).

### Option A: Using Windows Subsystem for Linux (WSL 2) on Windows 10
If developing directly from Windows 10:
1. Open PowerShell as Administrator and install Debian in WSL:
   ```powershell
   wsl --install -d Debian
   ```
2. Reboot when prompted, launch Debian, and navigate to the project directory:
   ```bash
   cd /mnt/c/Users/abhin/OneDrive/Desktop/giri-os
   ```

### Option B: Using a Dedicated Linux System or Virtual Machine
You can use a Debian 12 (Bookworm) or Ubuntu 22.04/24.04 virtual machine in VirtualBox or VMware with:
- At least 4 CPU cores assigned
- At least 4 GB RAM assigned
- At least 25 GB free disk space

---

## 2. Installing Required Build Tools

Run the provided helper script:
```bash
chmod +x scripts/setup-dev-env.sh
sudo ./scripts/setup-dev-env.sh
```

Or install the packages manually:
```bash
sudo apt update
sudo apt install -y \
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
    qemu-system-x86 \
    ovmf
```

---

## 3. Testing Individual System Components

Before generating a full 2–3 GB ISO, individual components can be developed, tested, and styled locally:

### A. Testing the Hardware Profiler
```bash
python3 hardware/giri-hw/detector.py --summary
```
*Outputs detailed hardware information (CPU cores, RAM, GPU vendor, active tier recommendation).*

### B. Testing Giri Space Desktop Interface
```bash
python3 desktop/giri-space/shell/giri_space.py --profile classic
# or
python3 desktop/giri-space/shell/giri_space.py --profile modern
```

### C. Testing the Giri Bridge Binary Analyzer
```bash
python3 compatibility/giri-bridge/analyzer.py --file /path/to/installer.exe
```
*Parses Windows Portable Executable (PE) headers, reports 32-bit vs 64-bit architecture, and recommends prefix parameters.*

### D. Testing the Giri Update Verification Engine
```bash
python3 updater/giri-update/client.py --check
```

---

## 4. Building the Giri OS 0.1 Bootable ISO

The build pipeline uses standard Debian `live-build`. The script `scripts/build-iso.sh` wraps the process with safety pre-checks:

```bash
chmod +x scripts/build-iso.sh
sudo ./scripts/build-iso.sh
```

### What Happens During the Build:
1. **Safety Check:** Verifies at least 15 GB of free disk space is available.
2. **Debootstrap Phase:** Downloads pristine Debian Bookworm `amd64` core packages.
3. **Chroot Customization:**
   - Installs the X11/Mesa graphics stack and audio drivers.
   - Applies the Giri OS branding (`/etc/os-release`, logo, wallpapers).
   - Installs the Giri GRUB theme and Plymouth "giri-orbit" boot animation.
   - Configures the Giri Space desktop session and default user (`giri`).
4. **Squashfs Compression:** Compresses the root filesystem into an ultra-fast SquashFS image.
5. **Hybrid ISO Generation:** Bundles UEFI 64-bit and Legacy BIOS bootloaders with `xorriso`.
6. **Output:** Generates `build/releases/giri-os-0.1-genesis-amd64.iso`.

---

## 5. Testing the ISO in QEMU Virtual Machine

To test your generated ISO without touching real disks:

```bash
chmod +x scripts/test-qemu.sh
./scripts/test-qemu.sh
```

Or run QEMU directly:
```bash
qemu-system-x86_64 \
    -m 4G \
    -smp 4 \
    -enable-kvm \
    -vga virtio \
    -cdrom build/releases/giri-os-0.1-genesis-amd64.iso \
    -boot d
```
*(On Windows or environments without KVM, omit `-enable-kvm`)*.

---

## 6. Writing to a USB Drive for Real Hardware Testing

Once verified in QEMU, write the image to a USB flash drive (minimum 8 GB):

- **On Windows:** Use [Rufus](https://rufus.ie/) in **DD Image Mode** or [BalenaEtcher](https://etcher.balena.io/). Select the Giri OS ISO and your USB drive.
- **On Linux:** Use `dd` (ensure target drive letter is accurate):
  ```bash
  sudo dd if=build/releases/giri-os-0.1-genesis-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync
  ```
