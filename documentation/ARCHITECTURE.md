# Giri OS — Architectural Specification

## 1. Executive Architecture Summary

Giri OS is structured in clean, decoupled functional layers built atop a battle-tested **Debian GNU/Linux** foundation. The distribution is architected to guarantee stability, maximum practical Windows binary execution, low-overhead gaming performance, and reliable updates without sacrificing responsiveness on modest hardware.

```
+---------------------------------------------------------------------------------+
|                                 USER INTERACTION                                |
|  Giri Launch | Giri Dock | Giri Top Bar | Giri Control | Giri Files | Giri Bridge|
+---------------------------------------------------------------------------------+
|                         GIRI SPACE DESKTOP SUBSYSTEM                            |
|       Giri Modern (Compositor + Blur)   /   Giri Classic (Low Overhead)         |
|  - Window Manager (Openbox / KWin-lite / Weston-Wayland session)                |
|  - Giri Shell Toolkit (PyQt6 / GTK3 / Custom SVG Widget Engine)                 |
|  - Desktop Notification & Quick Settings Daemon                                 |
+---------------------------------------------------------------------------------+
|                       SPECIALIZED RUNTIME SUBSYSTEMS                            |
|  [ Giri Bridge ]             [ Giri Gaming ]              [ Giri Update ]       |
|  - PE32/PE64 Analyzer        - GameMode Governor          - APT / InRelease GPG |
|  - Wine/Proton Prefix Mgr    - PipeWire Pro-Audio Profile - Signature Verifier  |
|  - Isolated WINEPREFIX       - Controller Remapper        - Channel Switcher    |
|  - Dependency Engine         - Mesa/LLVMpipe Fallback     - Rollback Registry   |
+---------------------------------------------------------------------------------+
|                           HARDWARE PROFILER & ADAPTER                           |
|  [ giri-hw Engine ]                                                             |
|  - CPU capabilities & frequency governor detection                             |
|  - GPU detection (Intel HD 2000, Radeon, NVIDIA, Intel Arc)                     |
|  - Automatic Profile Selector (Modern vs Classic desktop activation)           |
+---------------------------------------------------------------------------------+
|                              BASE SYSTEM & DRIVERS                              |
|  - Linux Kernel (Debian LTS / Liquorix gaming kernel target)                   |
|  - Mesa 3D Graphics Stack (OpenGL 3.1+ for Intel HD 2000; Vulkan where present) |
|  - Systemd init, udev hardware manager, NetworkManager, PipeWire audio          |
|  - Linux PAM user authentication & Polkit security boundaries                   |
+---------------------------------------------------------------------------------+
|                                HARDWARE & FIRMWARE                              |
|       Legacy BIOS / UEFI 64-bit | Storage (HDD / SSD) | Memory (4GB - 16GB+)    |
+---------------------------------------------------------------------------------+
```

---

## 2. Core Layers Detailed

### Layer 1: Base Operating System & Kernel
- **Upstream:** Debian GNU/Linux (Bookworm / Trixie). Debian provides unmatched package stability, deterministic dependency resolution, and multi-architecture library support (`amd64` + `i386` multiarch), which is crucial for running 32-bit Windows games and utilities.
- **Kernel Strategy:**
  - *Standard Tier:* Debian LTS Linux Kernel (`linux-image-amd64`) with full hardware ACPI/AHCI driver coverage.
  - *Gaming Tier (Future):* Low-latency kernel patches (preempt-rt or Liquorix) tuned for real-time audio and frame pacing.
- **Multiarch Configuration:** Debian's native `dpkg --add-architecture i386` enables both 32-bit and 64-bit Wine compatibility out of the box.

### Layer 2: Hardware Adaptation & The Dual-Tier Engine (`giri-hw`)
A core differentiator of Giri OS is that it does not assume high-end hardware.
- Upon session start, `giri-hw` probes:
  1. **GPU Vendor & Device ID:** Identifies Sandy Bridge (Intel HD 2000/3000), Haswell/Broadwell, modern Iris, AMD Radeon, or NVIDIA.
  2. **Vulkan Availability:** Checks for active ICD loaders (`vulkaninfo`).
  3. **Total Physical Memory:** Checks whether RAM is < 6GB, 8GB, or >= 16GB.
  4. **Drive Type:** Detects rotational HDD vs SSD/NVMe (via `/sys/block/*/queue/rotational`).
- **Profile Outcomes:**
  - **Giri Classic Profile:** Activated automatically when Intel HD 2000/3000 is detected, or RAM < 6GB, or on mechanical HDDs. Disables desktop blurs, drops frame rate animations, uses lightweight software rendering buffers, and reserves RAM.
  - **Giri Modern Profile:** Activated on modern GPUs with hardware compositor acceleration. Enables fluid glassmorphism, orbital glow transitions, and dynamic widgets.

### Layer 3: Giri Space Desktop Environment
- **Aesthetic Direction:** Deep navy (`#0d1326`), midnight black (`#07090e`), electric cyan/blue (`#00d2ff`), and royal violet (`#7928ca`).
- **Components:**
  1. **Giri Top Bar:** Displays active workspace, Giri Space status, system stats (CPU, RAM, Network), battery, and Giri Quick Settings panel.
  2. **Giri Dock:** Centered or bottom-pinned taskbar featuring fluid hover scaling, running instance badges, and quick-launcher integration.
  3. **Giri Launch:** High-speed application directory featuring categorized search, recent files, and Giri Bridge application shortcuts.
  4. **Giri Control:** Central control panel for display resolutions, audio outputs, hardware profiles, Giri Bridge manager, and system updates.

### Layer 4: Giri Bridge (Windows Compatibility System)
Windows compatibility is not an afterthought in Giri OS; it is treated as a native OS service.
- **Architecture:**
  - **Binary Inspector:** Analyzes Windows PE headers (`.exe`, `.msi`) using Python `pefile` or custom header parsing to determine whether the target is 32-bit (`x86`) or 64-bit (`x64`), its subsystem (GUI vs Console), and required DLL imports.
  - **Prefix Manager:** Isolates every application or suite in a clean `WINEPREFIX` under `~/.giri/bridge/prefixes/<app-id>`, preventing DLL version hell between different Windows programs.
  - **Runner Selection:** Automatically chooses between system Wine (Debian), Wine-GE/Proton (for DirectX9-12 games), or DOSBox (for legacy 16-bit/DOS software).
  - **Virtual Machine Fallback:** For applications requiring unsupported ring-0 anti-cheat or proprietary kernel drivers, Giri Bridge provides an optional headless QEMU/KVM Windows VM orchestrator.

### Layer 5: Giri Gaming
- **Performance Governor:** Automatically sets CPU governor to `performance`, boosts process nice priority, and adjusts GPU power states when a game launches.
- **Display Server Optimization:** Bypasses compositing (`unredirect fullscreen windows`) to eliminate input lag.
- **Audio Routing:** Routes through PipeWire with 48kHz / 128-sample low latency buffer.

### Layer 6: Giri Update & Repository Infrastructure
- Built directly on top of Debian's APT infrastructure with custom repository endpoints.
- Package indices are cryptographically signed with Giri OS GPG signing keys.
- Rollback registry records transaction states to ensure systems can safely boot to previous states if an update is interrupted.
