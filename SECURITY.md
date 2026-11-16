# Security Policy & Vulnerability Reporting

Security and user trust are primary design pillars of **Giri OS**. As a Linux distribution designed to integrate external application compatibility, gaming, and automatic system updates, rigorous security controls are maintained at every tier.

---

## 🔒 Supported Versions

| Version | Supported | Security Maintenance Level |
| :--- | :--- | :--- |
| **0.1 (Genesis)** | ✅ Yes | Active development / Base system patches |
| **Future Releases** | ✅ Yes | Upstream Debian security tracking + Giri updates |

---

## 🛡️ Security Principles of Giri OS

1. **Cryptographically Signed Updates:**
   - All Giri OS package indices and repository metadata (`Release`, `InRelease`) are signed with an official GPG key.
   - SHA-256 / SHA-512 package checksums are strictly verified prior to installation.
   - Giri Update rejects unsigned or tampered packages by default.

2. **Isolation for Windows Applications (Giri Bridge):**
   - Untrusted `.exe` and `.msi` files are never silently executed with host root permissions.
   - Giri Bridge runs Windows binaries within isolated prefix containers with restricted direct system access.
   - Windows software requiring proprietary kernel drivers or ring-0 anti-cheat mechanisms are explicitly flagged, warning the user of security and compatibility boundaries.

3. **Linux PAM Authentication:**
   - Giri OS never stores passwords in plaintext or unhashed formats.
   - Standard Linux PAM (`pam_unix`, `pam_faillock`) handles user authentication, session escalation via `sudo`/`polkit`, and login verification.

4. **Zero Hidden Telemetry:**
   - No background behavioral profiling, keystroke logging, or unsolicited network telemetry is embedded within Giri OS.
   - All update network requests query only official, transparent repository mirrors.

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability in Giri OS:

1. **Do not create a public GitHub issue.**
2. Prepare a detailed vulnerability report including:
   - Component affected (e.g., Giri Bridge, Giri Update, Giri Space shell, bootloader script).
   - Steps to reproduce or proof-of-concept (PoC).
   - Potential impact (privilege escalation, denial of service, sandbox bypass).
   - Mitigation suggestions if known.
3. Submit the report directly to the lead architect:
   - **Contact:** `security@girios.org` (or directly via private vulnerability reporting on the GitHub repository).
4. You will receive an initial acknowledgment within **48 hours**, followed by a timeline for remediation and public disclosure.
