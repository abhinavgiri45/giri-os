# Giri OS 0.1 Genesis — Automated Cloud ISO Build & Testing Guide

**Founder & Lead Architect:** Abhinav Giri  
**Tagline:** ONE SYSTEM. INFINITE POSSIBILITIES.  
**Operating System:** Giri OS 0.1 Genesis (Debian 12 Bookworm amd64)  
**Target Architecture:** AMD64 / x86_64  
**Build Platform:** GitHub Actions Cloud Runners  
**Testing Target:** Oracle VirtualBox on Drive `E:\GiriOS-Testing\`

---

## 🌟 Overview: Why Build in the Cloud?

Building a real Linux operating system with Debian `live-build` requires:
1. Root privileges (`UID 0`) with native Linux kernel block driver access.
2. Loopback block device mounting (`/dev/loop*`) and chroot namespace isolation.
3. 15–20 GB of free workspace disk space.
4. Sustained CPU compilation and SquashFS high-ratio compression.

Because your local computer runs Windows 10 with limited drive space on `C:`, **we compile the entire operating system in GitHub's high-speed cloud infrastructure**. GitHub Actions runs on a clean Ubuntu 24.04 virtual machine with dedicated high-bandwidth connectivity to Debian mirror repositories, generates the genuine `giri-os-0.1-genesis-amd64.iso`, validates it with QEMU, and packages it as a downloadable ZIP artifact.

---

## 🚀 Step-by-Step Instructions

### Step 1: Push the Source Code to GitHub

Open **Command Prompt** or **PowerShell** in your project folder (`c:\Users\abhin\OneDrive\Desktop\giri-os`):

1. Check your Git status:
   ```cmd
   git status
   ```

2. If you haven't linked your GitHub repository yet, add your GitHub remote URL (replace with your actual GitHub username/repo):
   ```cmd
   git remote add origin https://github.com/<YOUR-GITHUB-USERNAME>/giri-os.git
   ```

3. Stage, commit, and push your branch to GitHub:
   ```cmd
   git branch -M master
   git push -u origin master
   ```

---

### Step 2: Trigger the Cloud Build on GitHub

1. Open your web browser and navigate to your GitHub repository:
   `https://github.com/<YOUR-GITHUB-USERNAME>/giri-os`
2. Click on the **Actions** tab at the top of the repository.
3. In the left sidebar, click on **Build Giri OS 0.1 Genesis ISO**.
4. Click the **Run workflow** dropdown on the right side of the page.
5. Select branch `feature/genesis-stabilization` (or `master`) and leave *Execute automated QEMU headless boot smoke test* checked.
6. Click the green **Run workflow** button.
   - The workflow executes the full 16-test pre-flight suite (`tests/test_giri_suite.py`).
   - Compiles the Debian 12 Bookworm live-build ISO with all stabilized Giri OS components and 4K wallpapers.
   - Tests the resulting ISO in headless QEMU.
   - Packages the artifact as `Giri-OS-0.1-Genesis-AMD64.zip`.

---

### Step 3: Monitor the Build in Real Time

1. The new workflow run will appear at the top of the list with a yellow spinner indicating it is in progress.
2. Click on the workflow run name (e.g., *Build Giri OS 0.1 Genesis ISO*).
3. Click on the job **Build Giri OS 0.1 Genesis ISO (Debian 12 Bookworm amd64)**.
4. You can expand the logs in real time to watch:
   - **Maximize Runner Disk Space:** Frees up over 30 GB of storage.
   - **Install Distribution Engineering Toolchain:** Installs `live-build`, `debootstrap`, `xorriso`, and `ovmf`.
   - **Run Giri OS Pre-Flight Test Suite:** Validates all 9 automated checks.
   - **Compile Giri OS 0.1 Genesis Bootable ISO:** Downloads the official Debian 12 Bookworm base packages, configures the chroot, installs the custom Giri branding, wallpapers, GRUB theme, Plymouth splash, and compiles the SquashFS filesystem.
   - **Validate ISO Filesystem & Bootloader:** Mounts the ISO, checks `/live/vmlinuz` and `filesystem.squashfs`, and checks SHA256 checksums.
   - **Automated Headless QEMU Boot Smoke Test:** Verifies that virtual BIOS/UEFI firmware successfully executes the bootloader.

> ⏱️ **Estimated Duration:** Debian live-build downloads approximately 1.5–2.5 GB of packages and compresses them into SquashFS. On GitHub runners, this typically takes **15 to 25 minutes**.

---

### Step 4: Download the ISO Artifact

Once the workflow finishes with a green checkmark (✅):

1. Click on the completed workflow run title to open the **Summary** page.
2. Scroll down to the **Artifacts** section at the bottom of the page.
3. Click on **`Giri-OS-0.1-Genesis-AMD64`** (it will download as a `.zip` file, typically ~1.5 to 2.5 GB).

---

### Step 5: Extract the ISO to Your Testing Drive

1. Locate the downloaded file: `Giri-OS-0.1-Genesis-AMD64.zip` (usually in your `Downloads` folder).
2. Right-click the `.zip` file and select **Extract All...**.
3. Inside the extracted folder, you will find:
   - `giri-os-0.1-genesis-amd64.iso` (The genuine bootable ISO)
   - `SHA256SUMS.txt` (Cryptographic verification checksum)
   - `BUILD-REPORT.md` (Detailed cloud build audit)
   - `build.log` (Complete live-build compilation log)
4. Copy `giri-os-0.1-genesis-amd64.iso` directly into your testing ISO folder:
   ```
   E:\GiriOS-Testing\ISO\
   ```

---

### Step 6: Verify the Cryptographic Checksum (Optional but Recommended)

Open **PowerShell** on Windows and run:

```powershell
Get-FileHash E:\GiriOS-Testing\ISO\giri-os-0.1-genesis-amd64.iso -Algorithm SHA256
```

Compare the resulting hash with the hash inside `SHA256SUMS.txt`. If they match, your ISO download is 100% bit-perfect and uncorrupted.

---

### Step 7: Boot Giri OS in VirtualBox

You already have the automated Giri OS test environment configured on drive `E:`!

1. Open **File Explorer** and go to:
   ```
   E:\GiriOS-Testing\
   ```
2. Double-click:
   ```
   Launch-GiriOS-Testing.bat
   ```
3. The launcher will automatically:
   - Verify VirtualBox.
   - Detect `giri-os-0.1-genesis-amd64.iso` in `E:\GiriOS-Testing\ISO\`.
   - Attach the ISO to the virtual optical drive of the **Giri OS** VM.
   - Launch the virtual machine!

> [!TIP]
> If your motherboard firmware has **Intel VT-x** enabled in BIOS, the 64-bit Debian VM will power on immediately. (If you see a VT-x error, remember to restart your PC, press `F2` or `Del`, navigate to `Advanced -> CPU Configuration`, and set `Intel Virtualization Technology` to `Enabled`).

---

### Step 8: Exploring the Giri OS Live Environment

When the virtual machine boots:

1. **Bootloader Screen (GRUB / ISOLINUX):**
   - Press `Enter` on **1. Giri OS 0.1 (Genesis) — Standard Session**.
   - If testing legacy graphics fallback, choose **2. Safe Graphics Mode**.
2. **Plymouth Boot Splash:**
   - Watch the smooth deep navy splash screen with the official 2×2 window logo and the tagline: *ONE SYSTEM. INFINITE POSSIBILITIES.*
3. **Desktop Session (Giri Space):**
   - The system automatically logs into the live user (`giri`).
   - You will see the signature **Giri Origin** wallpaper on the desktop.
   - The **Giri Space Top Bar** displays Spaces 1–4, system clock, and Quick Settings.
   - The **Giri Space Dock** displays quick launchers.
   - Double-click **Giri Control Center** on the desktop to preview wallpapers, hardware specs, and visual profiles.

---

### Step 9: Testing the Calamares Installer Safely

> [!CAUTION]
> **Host Safety Guarantee:** The VirtualBox VM is completely isolated from your real Windows computer. The installer runs inside the virtual machine and only sees the **30 GB virtual hard disk (`Giri OS.vdi`) on `E:\GiriOS-Testing\VirtualMachines\`.** It can NEVER touch or format your physical `C:` or `E:` drives.

To test the installation process:

1. On the live desktop, double-click the **Install Giri OS 0.1 Genesis** icon.
2. The custom-branded **Calamares** installer will open.
3. Walk through the installation steps:
   - **Welcome:** Shows Giri OS branding and Debian 12 foundation notice.
   - **Partitions:** Select **Erase disk** (this erases ONLY the 30 GB virtual disk inside VirtualBox).
   - **Users:** Create a test user account and password.
   - **Summary:** Review settings and click **Install**.
4. When installation finishes, shut down the VM, detach the ISO in VirtualBox settings, and boot from the virtual hard disk to verify installed boot!

---

### Step 10: Complete the Quality Assurance Report

After testing, document your findings in your QA test report template at:
`E:\GiriOS-Testing\Reports\GiriOS-Test-Report.md`
