# Contributing to Giri OS

Thank you for your interest in contributing to **Giri OS**! Our mission is to build an independent, open-source Linux desktop operating system combining flexibility, genuine Windows compatibility, optimized gaming, and accessible hardware performance.

---

## 🧭 Code of Conduct

Giri OS is committed to providing a welcoming, inclusive, and harassment-free environment for all contributors, regardless of experience level, background, gender identity, sexual orientation, disability, or nationality.

- **Be respectful and collaborative:** Treat fellow contributors with kindness.
- **Listen actively:** Constructive feedback drives quality engineering.
- **Maintain focus on technical excellence:** Ground debates in architectural rationale and empirical testing.

---

## 🛠️ How to Contribute

We welcome contributions across multiple disciplines:

1. **Core System & Desktop (Giri Space):** Shell widgets, window management scripts, dock, launcher, and system settings.
2. **Compatibility (Giri Bridge):** Wine prefixes, Proton tuning, dependency auto-detection recipes, and troubleshooting scripts.
3. **Gaming (Giri Gaming):** Performance profiles, Mesa/Vulkan fallback scripts, game mode scheduling, controller mapping.
4. **Hardware Testing & Profiling:** Testing Giri OS across diverse hardware (e.g., Intel HD 2000/3000, legacy Radeon, NVIDIA Optimus, modern APUs).
5. **Design & Artwork:** Vector iconography, wallpapers, sound themes, and documentation illustrations.
6. **Documentation & Translations:** Guides, installation walkthroughs, and UI localization.

---

## 💻 Development Workflow

1. **Fork and Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/giri-os.git
   cd giri-os
   ```

2. **Create a Dedicated Topic Branch:**
   ```bash
   git checkout -b feature/giri-bridge-dependency-checker
   # or
   git checkout -b fix/plymouth-resolution-fallback
   ```

3. **Follow Coding & Architectural Standards:**
   - **Modularity:** Keep system daemons separate from visual desktop components.
   - **Hardware Safety:** Never assume modern Vulkan or AVX2 extensions without a runtime fallback. Always test against the baseline (Intel Core i5-2400 / Intel HD 2000).
   - **No Plaintext Passwords:** System authentication must interface with standard Linux PAM.
   - **No Telemetry:** Do not introduce hidden analytical beacons or network pings.

4. **Test Before Submitting:**
   - Execute the test suite: `python3 -m unittest discover tests/`
   - Test UI components with both `--profile modern` and `--profile classic`.
   - Validate live-build configuration syntax before issuing pull requests.

5. **Commit Message Format:**
   We follow standard semantic commit guidelines:
   ```text
   feat(bridge): implement 32-bit vs 64-bit PE binary analyzer
   fix(boot): resolve GRUB menu font cutoff on 1024x768 displays
   docs(hw): add Intel HD 2000 mesa fallback guidance
   ```

6. **Submit a Pull Request (PR):**
   Explain the rationale, tests conducted, hardware tested on, and screenshots/logs where relevant.

---

## ⚖️ Contributor License Agreement (CLA)

By contributing to Giri OS, you agree that your code contributions will be licensed under the **GNU General Public License v3.0 (GPL-3.0-or-later)**, and any documentation or artwork will be licensed under **Creative Commons Attribution 4.0 (CC BY 4.0)**.
