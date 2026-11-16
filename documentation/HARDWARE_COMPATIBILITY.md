# Giri OS — Hardware Compatibility & Baseline Guide

## 1. Development Baseline Hardware

Giri OS is specifically optimized to perform smoothly on real-world legacy and modern hardware. The foundational development baseline is:

- **Processor:** Intel Core i5-2400 (4 Cores / 4 Threads @ 3.10 GHz, Sandy Bridge architecture)
- **Memory:** 8 GB DDR3 RAM
- **Graphics:** Integrated Intel HD Graphics 2000 (PCI ID: `8086:0102`)
- **Storage:** Mechanical Hard Disk Drive (HDD)
- **Host OS:** Windows 10 Pro 22H2 64-bit
- **Available Storage Space:** 20–50 GB

---

## 2. Technical Analysis of Intel HD Graphics 2000 on Linux

Understanding the exact Linux kernel and Mesa support for Intel HD 2000 is critical for operating system stability:

### Supported Technologies
- **Driver:** Linux kernel `i915` DRM driver + Mesa `crocus` / `i965` driver.
- **OpenGL Level:** OpenGL 3.1 (Desktop) / OpenGL ES 3.0 (with software extensions).
- **DirectX under Wine:** DirectX 9.0c (via Wine OpenGL translation) and basic DirectX 10/11 emulation.
- **Video Acceleration (VA-API):** Supported via `i965-va-driver` for hardware H.264 decoding up to 1080p.

### Unsupported Technologies (Important Limitations)
- **Vulkan:** **NOT supported in hardware.** Intel HD 2000 lacks hardware support for Vulkan 1.0+.
- **DXVK:** Because DXVK requires Vulkan 1.1+, Windows games requiring DXVK cannot run via Vulkan on Intel HD 2000.
- **Modern Compositors:** Heavy Gaussian blur and complex fragment shaders will cause frame drops on Sandy Bridge.

### Giri OS Architecture Response
1. **Mesa OpenGL Backend for Wine:** Giri Bridge automatically disables DXVK and forces Wine's native OpenGL translation (`wined3d`) when Intel HD 2000 is detected.
2. **Giri Classic Desktop Profile:** Reduces compositor load, disables window backdrop blurs, and utilizes crisp 2D Cairo/X11 rendering to ensure steady 60 FPS desktop responsiveness.
3. **Mesa LLVMpipe / Zink Fallback:** For tools requiring basic Vulkan software queries, Giri OS routes through LLVMpipe CPU rasterization instead of crashing.

---

## 3. Storage & Disk Safety Rules

Developing an operating system on a Windows 10 machine requires strict disk safety protocols:

> [!CAUTION]
> **Zero Host Drive Overwrites:**
> 1. Never execute disk formatting commands (`dd`, `fdisk`, `mkfs`) targeting host drive letters (`C:`, `D:`) or physical disk numbers without verifying target device identifiers.
> 2. ISO builds will be assembled inside isolated directory trees (`build/live-build/`) and tested inside virtualized environments (QEMU, VirtualBox) or written only to a user-confirmed USB drive.
> 3. Giri OS provides a **Live USB mode** allowing full system testing directly from RAM without modifying internal Windows partitions.

---

## 4. Hardware Matrix & Tier Classification

| Hardware Tier | CPU | GPU | RAM | Default Desktop Mode | Giri Gaming Capability |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1 (Legacy / Value)** | Intel Core 2 Duo / Core i3/i5 2nd-3rd Gen | Intel HD 2000 / 3000 / 4000 | 4 GB – 8 GB | **Giri Classic** | Retro games, 2D titles, DirectX 9 classics, DOSBox |
| **Tier 2 (Mainstream)** | Intel Core 4th-8th Gen / AMD FX & Ryzen 1st Gen | Intel HD 4600 / Vega iGPU / GTX 750Ti | 8 GB – 16 GB | **Giri Modern** | Indie titles, eSports, DirectX 10/11 games via Wine |
| **Tier 3 (Performance)** | Intel Core 9th+ Gen / AMD Ryzen 2000+ | Dedicated NVIDIA GTX/RTX, AMD RX 5000+ | 16 GB+ | **Giri Modern (High Effects)** | Full AAA Steam/Proton gaming, Vulkan 1.3, DXVK |
