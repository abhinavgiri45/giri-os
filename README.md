# Giri OS

<div align="center">

```
   ██████╗ ██╗██████╗ ██╗     ██████╗ ███████╗
  ██╔════╝ ██║██╔══██╗██║    ██╔═══██╗██╔════╝
  ██║  ███╗██║██████╔╝██║    ██║   ██║███████╗
  ██║   ██║██║██╔══██╗██║    ██║   ██║╚════██║
  ╚██████╔╝██║██║  ██║██║    ╚██████╔╝███████║
   ╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝     ╚═════╝ ╚══════╝
```

### **One System. Infinite Possibilities.**

*An independent, open-source Linux operating system engineered for flexibility, modern aesthetics, hardware endurance, and deep application compatibility.*

---

**Founder & Lead Architect:** Abhinav Giri  
**Base Distribution:** Debian GNU/Linux 12 (Bookworm)  
**Target Architectures:** x86_64 (AMD64)  
**License:** GNU General Public License v3.0 (GPL-3.0-or-later) & CC-BY-4.0 (Assets & Docs)  
**Status:** Active Development — Milestone 0.1 ("Genesis")

</div>

---

## 🌌 Vision & Philosophy

Most operating systems demand that the user adapt to their walled garden. **Giri OS** reverses that relationship. Built from the Debian base, Giri OS delivers:

1. **Uncompromised Linux Independence:** Built directly upon robust Debian package ecosystems without being an Ubuntu or macOS clone.
2. **Dual-Tier Hardware Architecture:**
   - **Giri Modern:** Full compositor effects, glassmorphic accents, GPU-accelerated workspace transitions, and orbital widgets for contemporary hardware.
   - **Giri Classic:** Optimized pipeline tailored for older processors and legacy integrated graphics (such as Intel HD Graphics 2000/3000, 4–8 GB RAM, mechanical HDDs) consuming under 450 MB idle RAM.
3. **Giri Bridge:** A first-class compatibility engine fusing Wine, Proton, Bottles prefixes, and isolated application containers to run Windows applications seamlessly without erratic setup routines.
4. **Giri Gaming:** Dedicated Game Mode scheduler, controller mapping daemon, PipeWire ultra-low latency audio, and Vulkan/OpenGL fallback routing.
5. **Giri Update:** Cryptographically signed, APT-backed release streams (Stable, Beta, Developer) with zero telemetry and transparent rollback diagnostics.

---

## 📂 Repository Structure

```text
giri-os/
├── README.md                      # Primary project overview and getting started
├── LICENSE                        # GNU General Public License v3.0
├── CONTRIBUTING.md                 # Contribution standards and code of conduct
├── SECURITY.md                    # Security advisories and key management
│
├── branding/                      # Visual identity, SVG vectors, and typography
│   ├── logo/                      # Geometric 'G' + orbital ring vector assets
│   ├── wallpapers/                # 4K & standard Giri Orbit dark/light wallpapers
│   └── icons/                     # Desktop and application icon sets
│
├── boot/                          # Early startup and boot experience
│   ├── grub/                      # Branded GRUB 2 bootloader theme and configuration
│   ├── plymouth/                  # Plymouth boot splash animation ("giri-orbit")
│   └── isolinux/                  # Hybrid ISO isolinux/syslinux fallback configs
│
├── desktop/                       # Giri Space desktop environment
│   └── giri-space/
│       ├── shell/                 # Core compositor & window management rules
│       ├── dock/                  # Giri Dock component
│       ├── topbar/                # Giri Top Bar & Quick Settings panel
│       ├── launcher/              # Giri Launch application directory & search
│       ├── control-center/        # Giri Control center (settings & profiles)
│       └── themes/                # Giri Dark and Giri Light desktop themes
│
├── hardware/                      # Hardware detection and profile tier engine
│   └── giri-hw/                   # Hardware profiler (detects GPUs, CPU flags, RAM)
│
├── compatibility/                 # Windows application compatibility layer
│   └── giri-bridge/               # Giri Bridge launcher, prefix manager, & sandbox
│
├── gaming/                        # Gaming optimizations and runtime management
│   └── giri-gaming/               # Game Mode governor, FPS overlay, controller daemon
│
├── updater/                       # System updates and package delivery
│   └── giri-update/               # Cryptographic update client & repository manager
│
├── installer/                     # Operating system installer configurations
│   └── calamares/                 # Calamares installer distribution branding & modules
│
├── system/                        # Base system overlays and configurations
│   ├── etc/                       # os-release, issue, sysctl, and profile defaults
│   └── skel/                      # Default user skeleton directory
│
├── packaging/                     # Debian packaging specs (.deb recipes)
├── documentation/                 # Architectural blueprints and build guides
├── tests/                         # Unit tests, integration suites, and ISO check scripts
├── build/                         # Debian live-build recipe and manifest
└── scripts/                       # Developer automation and ISO generation scripts
```

---

## 💻 Target Development & Deployment Profile

Giri OS is engineered with real-world hardware compatibility at its core. From inception, the system is tuned and verified against everyday consumer hardware:

| Component | Minimum Specification (Classic Profile) | Recommended Specification (Modern Profile) |
| :--- | :--- | :--- |
| **CPU** | Intel Core i3/i5 2nd Gen (e.g. i5-2400) / AMD Athlon II | 4-Core / 8-Thread Modern x86_64 CPU |
| **RAM** | 4 GB DDR3 | 8 GB–16 GB DDR4/DDR5 |
| **Graphics** | Intel HD Graphics 2000 (Mesa OpenGL 3.1) | Dedicated AMD Radeon / NVIDIA / Intel Arc (Vulkan 1.3) |
| **Storage** | 20 GB HDD / SATA SSD | 64 GB+ NVMe SSD |
| **Boot Mode** | Legacy BIOS or 64-bit UEFI | 64-bit UEFI with Secure Boot support |

> **Developer Note on Intel HD 2000:** The 2nd Generation Sandy Bridge Intel HD 2000 lacks hardware Vulkan support and runs OpenGL 3.1 under Linux Mesa. Giri OS automatically routes 3D workloads through modern Mesa LLVMpipe software rasterizers or Wine OpenGL translation modes when Intel HD 2000 is detected, guaranteeing stability without crashing the desktop.

---

## 🛠️ Quick Start & Build Instructions

To build and test Giri OS components or compile the bootable ISO:

### Prerequisites (Debian/Ubuntu or WSL2)
```bash
sudo apt update
sudo apt install -y live-build debootstrap squashfs-tools xorriso \
    isolinux grub-pc-bin grub-efi-amd64-bin mtools python3 python3-pip
```

### Running the Hardware Profiler
```bash
python3 hardware/giri-hw/detector.py --summary
```

### Testing the Giri Space Desktop Prototype
```bash
python3 desktop/giri-space/shell/giri_space.py --profile modern
```

### Building the Giri OS 0.1 ISO
```bash
sudo ./scripts/build-iso.sh
```

---

## 🗺️ Release Roadmap

- **v0.1 — Genesis (Current):** Debian live-build foundation, Giri branding, GRUB theme, Plymouth boot splash, LightDM login theme, Giri Space prototype, hardware tier detector, and initial bootable ISO.
- **v0.2 — Bridge:** Giri Bridge GUI, Wine/Proton prefix isolation, EXE handler, and compatibility database.
- **v0.3 — Vanguard:** Giri Gaming dashboard, PipeWire audio profiles, Game Mode daemon, and controller mapping.
- **v0.4 — Horizon:** Giri Update GUI, GPG-signed repository pipeline, update channels (Stable/Beta/Dev), and recovery snapshots.
- **v0.5 — Cosmos:** Giri Store application catalog (Flatpak, APT, AppImage, Wine containers).
- **v1.0 — Public Release:** Production-certified release, comprehensive OEM installer, and multi-language support.

---

## 📄 License & Attribution

- **Giri OS Core & Components:** Licensed under the [GNU General Public License v3.0](LICENSE).
- **Branding, Artwork & Documentation:** Licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).
- *Debian, Linux, Wine, Proton, and other trademarks are the property of their respective owners. Giri OS is an independent distribution built upon the Debian open-source ecosystem.*
