#!/usr/bin/env python3
"""
Giri OS — Live-Build Helper Scripts Compatibility Patcher
Fixes upstream Debian/Ubuntu live-build bugs for Debian 12 Bookworm on Ubuntu runners:
1. Bookworm repository layout (/dists/<suite>/main/Contents-<arch>.gz)
2. Ubuntu live-build unconditional bootlogo cpio hack in lb_binary_syslinux
"""

import glob
import os
import re
import sys

def patch_live_build():
    target_dirs = ["/usr/lib/live/build", "/usr/share/live/build/scripts/build"]
    patched_contents = 0
    patched_bootlogo = 0

    for d in target_dirs:
        if not os.path.isdir(d):
            continue
        for filepath in glob.glob(os.path.join(d, "*")):
            if not os.path.isfile(filepath):
                continue
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                modified = False

                # 1. Patch Contents index path for Bookworm layout
                if "Contents-" in content:
                    new_content = re.sub(
                        r'/dists/([^/]+)/(?:main/)*Contents-',
                        r'/dists/\1/main/Contents-',
                        content
                    )
                    if new_content != content:
                        content = new_content
                        modified = True
                        patched_contents += 1

                # 2. Patch Ubuntu unconditional bootlogo cpio extraction hack
                if "bootlogo" in content and "cpio -i" in content:
                    target_str = '(cd "$tmpdir" && cpio -i) < ${_TARGET}/bootlogo'
                    if target_str in content and 'if [ -f "${_TARGET}/bootlogo" ]; then' not in content:
                        content = content.replace(
                            target_str,
                            'if [ -f "${_TARGET}/bootlogo" ]; then\n(cd "$tmpdir" && cpio -i) < ${_TARGET}/bootlogo'
                        )
                        content = content.replace(
                            '(cd "$tmpdir" && ls -1 | cpio --quiet -o) > ${_TARGET}/bootlogo\nrm -rf "$tmpdir"',
                            '(cd "$tmpdir" && ls -1 | cpio --quiet -o) > ${_TARGET}/bootlogo\nfi\nrm -rf "$tmpdir"'
                        )
                        modified = True
                        patched_bootlogo += 1

                # 3. Patch isohybrid package dependency from syslinux to syslinux-utils for Debian Bookworm (idempotent)
                if "isohybrid" in content and "Check_package chroot/usr/bin/isohybrid syslinux-utils" not in content:
                    new_content = re.sub(
                        r'Check_package chroot/usr/bin/isohybrid syslinux(?!\S)',
                        'Check_package chroot/usr/bin/isohybrid syslinux-utils',
                        content
                    )
                    if new_content != content:
                        content = new_content
                        modified = True

                # 4. Patch binary_linux-image to automatically create canonical vmlinuz and initrd.img links
                if "binary_linux-image" in filepath or "lb_binary_linux-image" in filepath:
                    if "ln -sf" not in content and "binary/live" in content:
                        # Append canonical link creation in binary_linux-image
                        link_code = (
                            '\n\t\t# Giri OS: Create canonical kernel and initrd links in binary/live\n'
                            '\t\t(cd binary/live && for k in vmlinuz-*; do [ -f "$k" ] && cp -fL "$k" vmlinuz && break; done) 2>/dev/null || true\n'
                            '\t\t(cd binary/live && for i in initrd.img-*; do [ -f "$i" ] && cp -fL "$i" initrd.img && break; done) 2>/dev/null || true\n'
                        )
                        if link_code not in content:
                            content += link_code
                            modified = True

                if modified:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[+] Patched compatibility in {filepath}")

            except Exception as e:
                print(f"[-] Warning: Failed to process {filepath}: {e}", file=sys.stderr)

    print(f"[+] Live-build patch summary: {patched_contents} Contents patches, {patched_bootlogo} bootlogo patches applied.")

if __name__ == "__main__":
    patch_live_build()
