# Giri OS — VirtualBox ISO Testing Environment

## 1. Overview & Setup Topology

To ensure 100% host safety, Giri OS ISO images are tested exclusively inside **Oracle VirtualBox** using virtual disks (`.vdi`) located on secondary storage (`E:\`). The physical host operating system (Windows 10 Pro) and physical drive partitions remain completely untouched.

```
Host Computer (Windows 10, Intel Core i5-2400, 8 GB RAM)
 │
 ├── C:\Program Files\Oracle\VirtualBox\VBoxManage.exe
 │
 └── E:\GiriOS-Testing\
      ├── ISO\                   <- Store compiled Giri OS ISO images here
      ├── VirtualMachines\       <- VM configuration (Giri OS.vbox) & 30 GB dynamic disk (Giri OS.vdi)
      ├── Snapshots\             <- Virtual machine recovery snapshots
      ├── Logs\                  <- VirtualBox hypervisor execution logs
      ├── Reports\               <- GiriOS-Test-Report.md (Structured QA checklist)
      ├── Screenshots\           <- Visual captures of boot, login, and desktop
      ├── Launch-GiriOS-Testing.bat   <- One-click Windows batch launcher
      └── Launch-GiriOS-Testing.ps1   <- Companion PowerShell interactive launcher
```

---

## 2. Virtual Machine Technical Specifications

The virtual machine has been provisioned and registered in Oracle VirtualBox as follows:

- **Virtual Machine Name:** `Giri OS`
- **Guest OS Type:** `Debian (64-bit)` (`Debian_64`)
- **Base Memory (RAM):** `3072 MB` (Preserves 5 GB for the host Windows 10 OS)
- **Processor Cores:** `2 vCPUs` (50% of the 4 physical i5-2400 cores)
- **Video Memory (VRAM):** `128 MB`
- **Graphics Controller:** `VMSVGA` (Native Linux DRM kernel driver support)
- **3D Acceleration:** `Disabled` (Ensures safe software rasterization & stability on Intel HD 2000)
- **Firmware:** `BIOS` (EFI disabled initially)
- **Storage Controller:** `SATA (Intel AHCI)`
  - **Port 0 (Hard Disk):** `E:\GiriOS-Testing\VirtualMachines\Giri OS\Giri OS.vdi` (30 GB, dynamically allocated)
  - **Port 1 (Optical Drive):** Virtual CD/DVD reader configured for dynamic ISO mounting
- **Network Adapter:** `NAT` (Direct internet access via host network stack)
- **Boot Order:** 1. DVD -> 2. Hard Disk

---

## 3. Intel VT-x Hardware Virtualization Advisory

During system diagnostics, the following hardware status was detected:
- **Processor:** Intel Core i5-2400 (Supports VT-x and SLAT in hardware)
- **Firmware Status:** `Virtualization Enabled In Firmware: No`

> [!IMPORTANT]
> **Enabling Intel VT-x in BIOS:**
> Because 64-bit guest operating systems in VirtualBox require hardware-assisted virtualization:
> 1. Reboot your PC and press `F2` or `Delete` during boot to enter BIOS/UEFI setup.
> 2. Navigate to **Advanced CPU Configuration** (or **Security / Virtualization**).
> 3. Locate **Intel Virtualization Technology (VT-x)** and change it to **Enabled**.
> 4. Press `F10` to save and reboot back into Windows.

---

## 4. How to Test an ISO Image

1. **Place your ISO file:**
   Copy your built Giri OS ISO image (e.g., `giri-os-0.1-genesis-amd64.iso`) into:
   ```text
   E:\GiriOS-Testing\ISO\
   ```
2. **Launch the Testing Environment:**
   Double-click:
   ```text
   E:\GiriOS-Testing\Launch-GiriOS-Testing.bat
   ```
   *(Or right-click and run `Launch-GiriOS-Testing.ps1` with PowerShell)*.
3. **Select the ISO:**
   The launcher will list all `.iso` files found in `E:\GiriOS-Testing\ISO\`. Enter the corresponding number.
4. **Boot & Test:**
   The launcher automatically mounts the selected ISO to Port 1 of the SATA Controller and powers on the VM in GUI mode.
5. **Document Results:**
   Record your findings in:
   ```text
   E:\GiriOS-Testing\Reports\GiriOS-Test-Report.md
   ```
