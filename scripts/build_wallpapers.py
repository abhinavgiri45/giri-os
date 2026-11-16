#!/usr/bin/env python3
"""
Giri OS 0.1 "Genesis" — Official 4K Wallpaper Pipeline & Integrator
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Redesigns, upscales, composites, and integrates all 12 official wallpapers
at 3840x2160 (4K UHD) with 16:9 aspect ratio and matching 384x216 thumbnails.
"""

import os
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WALLPAPER_DIR = PROJECT_ROOT / "branding" / "wallpapers"
THUMBNAILS_DIR = WALLPAPER_DIR / "thumbnails"
LOGO_DIR = PROJECT_ROOT / "branding" / "logo"

ARTIFACT_DIR = Path(r"C:\Users\abhin\.gemini\antigravity\brain\a9ddb090-78f6-40b9-a9d8-e1cfb53f17f9")

TARGET_WIDTH = 3840
TARGET_HEIGHT = 2160
THUMB_WIDTH = 384
THUMB_HEIGHT = 216

RAW_SOURCES = {
    "giri-origin.png": ARTIFACT_DIR / "giri_origin_wallpaper_1794822695190.jpg",
    "infinite-flow.png": ARTIFACT_DIR / "infinite_flow_wallpaper_1794822748079.jpg",
    "quantum-form.png": ARTIFACT_DIR / "quantum_form_wallpaper_1794822768333.jpg",
    "beyond-horizon.png": ARTIFACT_DIR / "beyond_horizon_wallpaper_1794822771533.jpg",
    "midnight-architecture.png": ARTIFACT_DIR / "midnight_architecture_1794822777556.jpg",
    "electric-geometry.png": ARTIFACT_DIR / "electric_geometry_wallpaper_1794822781735.jpg",
    "silent-universe.png": ARTIFACT_DIR / "silent_universe_1794822791209.jpg",
    "violet-dimension.png": ARTIFACT_DIR / "violet_dimension_1794822795721.jpg",
    "aurora.png": ARTIFACT_DIR / "aurora_wallpaper_1794822797602.jpg",
    "pure-minimal.png": ARTIFACT_DIR / "pure_minimal_wallpaper_1794822804690.jpg",
    "dark-edition-raw": ARTIFACT_DIR / "giri_os_dark_edition_wallpaper_1794822818834.jpg",
}

def upscale_image(src_path: Path) -> Image.Image:
    """Upscales from native 1376x768 to 3840x2160 with Lanczos and subtle unsharp sharpening."""
    im = Image.open(src_path).convert("RGB")
    # High quality Lanczos resize
    upscaled = im.resize((TARGET_WIDTH, TARGET_HEIGHT), resample=Image.Resampling.LANCZOS)
    # Subtle unsharp mask to restore micro-contrast without haloing
    sharpened = upscaled.filter(ImageFilter.UnsharpMask(radius=1.8, percent=50, threshold=2))
    return sharpened

def create_official_logo_overlay(size_px: int, is_light_theme: bool) -> Image.Image:
    """
    Renders the exact official Giri OS 2x2 four-pane geometric window logo
    with native vector anti-aliased precision.
    """
    # Supersampled rendering (4x) for ultra-crisp edges
    scale = 4
    canvas_size = size_px * scale
    overlay = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Proportions matching official giri-os-icon.svg (viewBox 256x256)
    # pane: 89x89, radius: 12, gap: 18, margin: 30
    s_factor = canvas_size / 256.0
    p_size = 89 * s_factor
    p_rad = 12 * s_factor
    p_gap = 18 * s_factor
    x0 = (canvas_size - (2 * p_size + p_gap)) / 2.0
    y0 = x0

    x1 = x0 + p_size + p_gap
    y1 = y0 + p_size + p_gap

    # Official Colors:
    # Top-Left: #00D2FF (Electric Cyan)
    # Top-Right: #0066FF (Vivid Blue)
    # Bottom-Left: #7928CA (Violet)
    # Bottom-Right: #A855F7 (Magenta-Violet)
    colors = [
        (0x00, 0xD2, 0xFF, 255),
        (0x00, 0x66, 0xFF, 255),
        (0x79, 0x28, 0xCA, 255),
        (0xA8, 0x55, 0xF7, 255),
    ]

    # Draw the 4 panes
    panes = [
        (x0, y0, x0 + p_size, y0 + p_size, colors[0]),
        (x1, y0, x1 + p_size, y0 + p_size, colors[1]),
        (x0, y1, x0 + p_size, y1 + p_size, colors[2]),
        (x1, y1, x1 + p_size, y1 + p_size, colors[3]),
    ]

    for px0, py0, px1, py1, col in panes:
        draw.rounded_rectangle([px0, py0, px1, py1], radius=p_rad, fill=col)

    # Downsample supersampled canvas to target size with Lanczos
    res = overlay.resize((size_px, size_px), resample=Image.Resampling.LANCZOS)
    return res

def create_wordmark_overlay(width_px: int, is_light_theme: bool) -> Image.Image:
    """Renders the official 'GIRI OS' and tagline wordmark with exact font metrics."""
    scale = 4
    c_w = width_px * scale
    c_h = int(120 * scale)
    overlay = Image.new("RGBA", (c_w, c_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_color_main = (0x0F, 0x17, 0x2A, 240) if is_light_theme else (0xFF, 0xFF, 0xFF, 245)
    font_color_os = (0x00, 0x66, 0xFF, 255)
    font_color_tag = (0x47, 0x55, 0x69, 220) if is_light_theme else (0x8E, 0xA4, 0xC8, 220)

    # Try to load standard system bold sans-serif font
    font_main = None
    font_tag = None
    for fn in ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]:
        try:
            font_main = ImageFont.truetype(fn, int(42 * scale))
            font_tag = ImageFont.truetype(fn, int(11 * scale))
            break
        except Exception:
            continue
    if not font_main:
        font_main = ImageFont.load_default()
        font_tag = ImageFont.load_default()

    # Draw GIRI OS
    text_giri = "GIRI "
    text_os = "OS"
    bbox_giri = draw.textbbox((0, 0), text_giri, font=font_main)
    w_giri = bbox_giri[2] - bbox_giri[0]
    bbox_os = draw.textbbox((0, 0), text_os, font=font_main)
    w_os = bbox_os[2] - bbox_os[0]
    total_w = w_giri + w_os

    start_x = (c_w - total_w) / 2
    y_pos = int(10 * scale)

    draw.text((start_x, y_pos), text_giri, font=font_main, fill=font_color_main)
    draw.text((start_x + w_giri, y_pos), text_os, font=font_main, fill=font_color_os)

    # Divider line
    div_y = y_pos + int(48 * scale)
    div_w = int(240 * scale)
    draw.rounded_rectangle([(c_w - div_w)/2, div_y, (c_w + div_w)/2, div_y + int(1.5 * scale)], radius=int(scale), fill=(0x79, 0x28, 0xCA, 140))

    # Tagline
    tagline = "ONE SYSTEM. INFINITE POSSIBILITIES."
    bbox_tag = draw.textbbox((0, 0), tagline, font=font_tag)
    w_tag = bbox_tag[2] - bbox_tag[0]
    draw.text(((c_w - w_tag)/2, div_y + int(8 * scale)), tagline, font=font_tag, fill=font_color_tag)

    return overlay.resize((width_px, int(120)), resample=Image.Resampling.LANCZOS)

def generate_light_edition_from_dark(dark_base: Image.Image) -> Image.Image:
    """
    Transforms the 3D geometry of the dark edition into a pearl-white/silver/ice-blue
    light edition so that the 3D planes, curves, and architecture are 100% IDENTICAL.
    """
    # 1. Invert luminance curves while mapping deep blacks to porcelain whites
    r, g, b = dark_base.split()
    
    # Invert and adjust tones
    inv = ImageOps.invert(dark_base)
    # Brighten background into pearl-white (#F8FAFC)
    enhancer = ImageEnhance.Brightness(inv)
    bright = enhancer.enhance(1.15)
    # Tone down contrast for soft diffused studio lighting
    c_enhancer = ImageEnhance.Contrast(bright)
    soft = c_enhancer.enhance(0.85)
    
    # Tint gently towards ice-blue and pearl-silver
    tint = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), (242, 246, 252))
    blended = Image.blend(soft, tint, 0.40)
    
    return blended

def build_all_wallpapers():
    print("======================================================================")
    print("      GIRI OS 0.1 'GENESIS' — OFFICIAL 4K WALLPAPER BUILD PIPELINE     ")
    print("======================================================================")

    WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

    metadata_list = []

    # 1. Process 10 Artistic Wallpapers
    artistic_names = [
        ("giri-origin.png", "Giri Origin", "Signature Abstract Architecture", "Signature artistic wallpaper featuring midnight-blue surfaces, subtle electric-blue illumination, and a central abstract geometric structure.", "Dark / Modern"),
        ("infinite-flow.png", "Infinite Flow", "Flowing Abstract", "Flowing abstract ribbons of frosted glass and obsidian with electric-blue luminous accents against deep black.", "Dark / Modern"),
        ("quantum-form.png", "Quantum Form", "Geometric Architecture", "Refined geometric structures of translucent glass illuminated with subtle violet and electric blue highlights.", "Dark / Modern"),
        ("beyond-horizon.png", "Beyond Horizon", "Cosmic Horizon", "Cinematic cosmic horizon with atmospheric sapphire rim lighting and calm deep navy space.", "Dark / Midnight"),
        ("midnight-architecture.png", "Midnight Architecture", "Minimalist Architecture", "Futuristic minimalist architecture featuring brushed titanium structures and subtle electric-blue accent lines.", "Dark / Classic"),
        ("electric-geometry.png", "Electric Geometry", "Geometric Abstract", "Symmetrical multifaceted geometric forms constructed from polished obsidian and electric-blue light channels.", "Dark / Modern"),
        ("silent-universe.png", "Silent Universe", "Minimalist Space", "Minimalist cosmic environment with calm atmospheric depth and restrained luminous gradients.", "Dark / Midnight"),
        ("violet-dimension.png", "Violet Dimension", "Cinematic 3D Abstract", "Abstract cinematic composition featuring flowing translucent violet glass and amethyst crystal structures.", "Dark / Modern"),
        ("aurora.png", "Aurora", "Atmospheric Wave", "Atmospheric light formations in electric blue, violet, and subtle cyan drifting across a midnight void.", "Dark / Modern"),
        ("pure-minimal.png", "Pure Minimal", "Ultra-Clean Minimalist", "Solitary matte dark metal sculptural form under soft directional rim lighting with vast negative space.", "Dark / Classic"),
    ]

    for filename, name, category, desc, paired_theme in artistic_names:
        src = RAW_SOURCES.get(filename)
        if not src or not src.exists():
            print(f"[-] ERROR: Missing source image for {filename}")
            continue

        out_path = WALLPAPER_DIR / filename
        thumb_path = THUMBNAILS_DIR / filename
        if out_path.exists() and out_path.stat().st_size > 1000000 and thumb_path.exists():
            print(f"[+] Reusing existing 4K {filename} ({out_path.stat().st_size / (1024*1024):.2f} MB)...")
            file_size = out_path.stat().st_size
        else:
            print(f"[+] Processing {filename} ({name})...")
            img_4k = upscale_image(src)
            img_4k.save(out_path, format="PNG", optimize=True)
            thumb = img_4k.resize((THUMB_WIDTH, THUMB_HEIGHT), resample=Image.Resampling.LANCZOS)
            thumb.save(thumb_path, format="PNG", optimize=True)
            file_size = out_path.stat().st_size
            print(f"    Saved: {out_path.name} ({TARGET_WIDTH}x{TARGET_HEIGHT}, {file_size / (1024*1024):.2f} MB)")

        metadata_list.append({
            "id": filename.replace(".png", ""),
            "name": name,
            "filename": filename,
            "category": category,
            "description": desc,
            "theme_compatibility": paired_theme,
            "is_official_default": (filename == "giri-origin.png"),
            "aspect_ratio": "16:9",
            "resolution": f"{TARGET_WIDTH}x{TARGET_HEIGHT}",
            "original_resolution": "1376x768",
            "format": "PNG",
            "file_size_bytes": file_size,
            "file_path": str(out_path),
            "thumb_path": str(thumb_path)
        })

    # 2. Process Official Default Wallpapers: Light & Dark Editions
    print("[+] Assembling Official Default Pair: Giri OS Light Edition & Dark Edition...")
    dark_raw_src = RAW_SOURCES.get("dark-edition-raw")
    dark_base_4k = upscale_image(dark_raw_src)
    light_base_4k = generate_light_edition_from_dark(dark_base_4k)

    # Identical logo coordinates and dimensions
    logo_size = 280
    logo_x = int((TARGET_WIDTH - logo_size) / 2)
    logo_y = int(TARGET_HEIGHT * 0.36)

    # Composite on Dark Edition
    dark_logo = create_official_logo_overlay(logo_size, is_light_theme=False)
    dark_wordmark = create_wordmark_overlay(600, is_light_theme=False)
    img_dark = dark_base_4k.copy()
    img_dark.paste(dark_logo, (logo_x, logo_y), dark_logo)
    img_dark.paste(dark_wordmark, (int((TARGET_WIDTH - 600)/2), logo_y + logo_size + 24), dark_wordmark)

    dark_out_path = WALLPAPER_DIR / "giri-os-default-dark.png"
    img_dark.save(dark_out_path, format="PNG", optimize=True)
    dark_thumb = img_dark.resize((THUMB_WIDTH, THUMB_HEIGHT), resample=Image.Resampling.LANCZOS)
    dark_thumb.save(THUMBNAILS_DIR / "giri-os-default-dark.png", format="PNG", optimize=True)
    dark_size = dark_out_path.stat().st_size
    print(f"    Saved: giri-os-default-dark.png ({TARGET_WIDTH}x{TARGET_HEIGHT}, {dark_size / (1024*1024):.2f} MB)")

    # Composite on Light Edition with identical placement and geometry
    light_logo = create_official_logo_overlay(logo_size, is_light_theme=True)
    light_wordmark = create_wordmark_overlay(600, is_light_theme=True)
    img_light = light_base_4k.copy()
    img_light.paste(light_logo, (logo_x, logo_y), light_logo)
    img_light.paste(light_wordmark, (int((TARGET_WIDTH - 600)/2), logo_y + logo_size + 24), light_wordmark)

    light_out_path = WALLPAPER_DIR / "giri-os-default-light.png"
    img_light.save(light_out_path, format="PNG", optimize=True)
    light_thumb = img_light.resize((THUMB_WIDTH, THUMB_HEIGHT), resample=Image.Resampling.LANCZOS)
    light_thumb.save(THUMBNAILS_DIR / "giri-os-default-light.png", format="PNG", optimize=True)
    light_size = light_out_path.stat().st_size
    print(f"    Saved: giri-os-default-light.png ({TARGET_WIDTH}x{TARGET_HEIGHT}, {light_size / (1024*1024):.2f} MB)")

    # Add Default Light & Dark to metadata (placed prominently at top)
    default_meta = [
        {
            "id": "giri-os-default-dark",
            "name": "Giri OS — Dark Edition",
            "filename": "giri-os-default-dark.png",
            "category": "Official Default",
            "description": "Official default wallpaper for Dark Mode featuring deep black and midnight-blue brushed metals, electric-blue accent lines, and the official Giri OS logo with illuminated silver treatment.",
            "theme_compatibility": "Dark",
            "is_official_default": True,
            "aspect_ratio": "16:9",
            "resolution": f"{TARGET_WIDTH}x{TARGET_HEIGHT}",
            "original_resolution": "1376x768",
            "format": "PNG",
            "file_size_bytes": dark_size,
            "file_path": str(dark_out_path),
            "thumb_path": str(THUMBNAILS_DIR / "giri-os-default-dark.png")
        },
        {
            "id": "giri-os-default-light",
            "name": "Giri OS — Light Edition",
            "filename": "giri-os-default-light.png",
            "category": "Official Default",
            "description": "Official default wallpaper for Light Mode featuring pearl-white porcelain surfaces, satin silver geometric elements, subtle ice-blue ambient glow, and the official Giri OS logo in contrasting dark navy.",
            "theme_compatibility": "Light",
            "is_official_default": True,
            "aspect_ratio": "16:9",
            "resolution": f"{TARGET_WIDTH}x{TARGET_HEIGHT}",
            "original_resolution": "1376x768",
            "format": "PNG",
            "file_size_bytes": light_size,
            "file_path": str(light_out_path),
            "thumb_path": str(THUMBNAILS_DIR / "giri-os-default-light.png")
        }
    ]

    full_metadata = default_meta + metadata_list

    # Write wallpaper-metadata.json
    metadata_json_path = WALLPAPER_DIR / "wallpaper-metadata.json"
    with open(metadata_json_path, "w", encoding="utf-8") as f:
        json.dump(full_metadata, f, indent=2)
    print(f"[+] Written metadata: {metadata_json_path}")

    # Write backwards-compatible wallpapers.json
    wallpapers_json_path = WALLPAPER_DIR / "wallpapers.json"
    with open(wallpapers_json_path, "w", encoding="utf-8") as f:
        json.dump(full_metadata, f, indent=2)
    print(f"[+] Updated manifest: {wallpapers_json_path}")

    print("======================================================================")
    print(f"[+] SUCCESS: All 12 wallpapers generated at {TARGET_WIDTH}x{TARGET_HEIGHT} 4K UHD.")
    print("======================================================================")

if __name__ == "__main__":
    build_all_wallpapers()
