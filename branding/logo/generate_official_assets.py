#!/usr/bin/env python3
"""
Giri OS — Official Logo Pipeline & Asset Generator
Processes the user-provided official Giri OS logo:
- Preserves 100% original pixel data in branding/logo/official/
- Generates high-resolution transparent master assets
- Generates light-theme optimized variant (with graphite wordmark)
- Generates square standalone 'G' emblem icon
- Exports standard multi-resolution icon sets (16, 24, 32, 48, 64, 128, 256, 512)
- Updates GRUB, Plymouth, Calamares, and desktop system targets
"""

import os
import shutil
import numpy as np
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
SOURCE_LOGO = r"C:/Users/abhin/.gemini/antigravity/brain/a9ddb090-78f6-40b9-a9d8-e1cfb53f17f9/.user_uploaded/media_1794846212170_0f70a10c.png"

def main():
    print("======================================================================")
    print("      GIRI OS 0.1 GENESIS — OFFICIAL LOGO ASSET PIPELINE             ")
    print("======================================================================")

    if not os.path.isfile(SOURCE_LOGO):
        print(f"[-] Error: Source logo file not found at {SOURCE_LOGO}")
        return 1

    # 1. Directory Structure
    official_dir = os.path.join(PROJECT_ROOT, "branding", "logo", "official")
    icons_dir = os.path.join(PROJECT_ROOT, "branding", "logo", "icons")
    os.makedirs(official_dir, exist_ok=True)
    os.makedirs(icons_dir, exist_ok=True)

    # 2. Archive Original Artwork
    archived_original = os.path.join(official_dir, "giri-os-official-original.png")
    shutil.copy2(SOURCE_LOGO, archived_original)
    print(f"[+] Archived original untouched artwork: {archived_original}")

    # 3. Load Source Image
    im = Image.open(SOURCE_LOGO).convert("RGBA")
    arr = np.array(im)
    alpha = arr[:, :, 3]

    # Find bounding box of all content
    y_idx, x_idx = np.where(alpha > 10)
    x_min, x_max = x_idx.min(), x_idx.max()
    y_min, y_max = y_idx.min(), y_idx.max()
    print(f"[+] Full Content Bounding Box: ({x_min}, {y_min}) to ({x_max}, {y_max}) -> {x_max - x_min + 1}x{y_max - y_min + 1}")

    # Crop full logo with slight padding (16px)
    pad = 16
    crop_x1 = max(0, x_min - pad)
    crop_y1 = max(0, y_min - pad)
    crop_x2 = min(im.width, x_max + pad + 1)
    crop_y2 = min(im.height, y_max + pad + 1)
    full_logo = im.crop((crop_x1, crop_y1, crop_x2, crop_y2))

    # Master full logo (Dark background / Transparent)
    master_dark = os.path.join(PROJECT_ROOT, "branding", "logo", "giri-os-logo.png")
    full_logo.save(master_dark, "PNG")
    print(f"[+] Saved Master Full Logo (Dark/Universal): {master_dark}")

    # 4. Generate Light-Theme Variant
    # For light backgrounds: the "Giri" text is white in original, so we darken the text region
    # while leaving the blue 'G' emblem 100% untouched.
    arr_light = np.array(full_logo)
    # The symbol ends around y = 205 in the cropped image
    # Detect text region where y is in bottom 40% and pixels are light/white
    h, w, _ = arr_light.shape
    text_y_threshold = int(h * 0.62)
    for y in range(text_y_threshold, h):
        for x in range(w):
            r, g, b, a = arr_light[y, x]
            if a > 20: # Visible pixel in text area
                # If it's near-white or silver text, darken to elegant deep navy/slate (#0F172A)
                if r > 180 and g > 180 and b > 180:
                    arr_light[y, x] = [15, 23, 42, a] # #0F172A slate
                elif r > 120 and g > 120 and b > 120:
                    arr_light[y, x] = [30, 41, 59, a] # #1E293B slate
    
    light_logo = Image.fromarray(arr_light)
    master_light = os.path.join(PROJECT_ROOT, "branding", "logo", "giri-os-logo-light.png")
    light_logo.save(master_light, "PNG")
    print(f"[+] Saved Light-Theme Full Logo: {master_light}")

    # 5. Extract Standalone 'G' Emblem (Icon Symbol)
    # Symbol is top part (y_min to ~380 in original coordinate space)
    symbol_y_max = 375
    sym_crop = im.crop((x_min - pad, y_min - pad, x_max + pad + 1, symbol_y_max))
    
    # Square padding to make it a perfect app icon
    sym_w, sym_h = sym_crop.size
    max_dim = max(sym_w, sym_h)
    square_icon = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
    offset_x = (max_dim - sym_w) // 2
    offset_y = (max_dim - sym_h) // 2
    square_icon.paste(sym_crop, (offset_x, offset_y))

    master_icon = os.path.join(PROJECT_ROOT, "branding", "logo", "giri-os-icon.png")
    square_icon.save(master_icon, "PNG")
    print(f"[+] Saved Master 'G' Icon Symbol: {master_icon}")

    # 6. Generate Standard Multi-Resolution Icon Set
    resolutions = [16, 24, 32, 48, 64, 128, 256, 512]
    for res in resolutions:
        resized = square_icon.resize((res, res), Image.Resampling.LANCZOS)
        out_path = os.path.join(icons_dir, f"giri-os-icon-{res}.png")
        resized.save(out_path, "PNG")
    print(f"[+] Generated standard icon set: {resolutions}")

    # 7. Update System Interface Targets
    # A. GRUB Bootloader Logo (boot/grub/themes/giri/logo.png)
    grub_logo_path = os.path.join(PROJECT_ROOT, "boot", "grub", "themes", "giri", "logo.png")
    os.makedirs(os.path.dirname(grub_logo_path), exist_ok=True)
    grub_logo = square_icon.resize((128, 128), Image.Resampling.LANCZOS)
    grub_logo.save(grub_logo_path, "PNG")
    print(f"[+] Updated GRUB Bootloader Logo: {grub_logo_path}")

    # B. Plymouth Boot Splash (boot/plymouth/giri-genesis/logo.png)
    plymouth_dir = os.path.join(PROJECT_ROOT, "boot", "plymouth", "giri-genesis")
    os.makedirs(plymouth_dir, exist_ok=True)
    plymouth_logo_path = os.path.join(plymouth_dir, "logo.png")
    plymouth_logo = square_icon.resize((192, 192), Image.Resampling.LANCZOS)
    plymouth_logo.save(plymouth_logo_path, "PNG")
    print(f"[+] Updated Plymouth Boot Splash Logo: {plymouth_logo_path}")

    # C. Calamares System Installer Branding
    calamares_branding_dir = os.path.join(PROJECT_ROOT, "installer", "calamares", "branding", "giri")
    os.makedirs(calamares_branding_dir, exist_ok=True)
    square_icon.resize((128, 128), Image.Resampling.LANCZOS).save(
        os.path.join(calamares_branding_dir, "productIcon.png"), "PNG"
    )
    full_logo.resize((320, int(320 * full_logo.height / full_logo.width)), Image.Resampling.LANCZOS).save(
        os.path.join(calamares_branding_dir, "productLogo.png"), "PNG"
    )
    print(f"[+] Updated Calamares System Installer Branding in {calamares_branding_dir}")

    print("[+] All official Giri OS logo assets generated successfully!")
    return 0

if __name__ == "__main__":
    main()
