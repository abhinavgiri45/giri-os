#!/usr/bin/env python3
"""
Giri OS — Official Wallpaper & Background Generation Engine
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Generates the complete 10-piece signature wallpaper collection for Giri OS:
1.  Giri Origin (Signature Default)
2.  Cosmic Horizon
3.  Infinite Motion
4.  Digital Dimensions
5.  Midnight Flow
6.  Electric Geometry
7.  Beyond Space
8.  Quantum
9.  Aurora
10. Pure Minimal

Adheres strictly to brand rules:
- 16:9 aspect ratio
- No text, no logos, no watermarks, no signatures
- Deep black, midnight navy, electric blue, and violet palette
- Clean perimeter margins for desktop icons and panels
- Procedurally rendered with high performance and zero external dependencies (Pillow only)
"""

import os
import math
import json
from PIL import Image, ImageDraw, ImageFilter


WIDTH = 1920
HEIGHT = 1080
THUMB_WIDTH = 320
THUMB_HEIGHT = 180


def create_base_canvas(color=(6, 10, 20, 255)):
    return Image.new("RGBA", (WIDTH, HEIGHT), color)


# 1. Giri Origin (Signature Default Wallpaper)
def render_giri_origin():
    img = create_base_canvas((4, 6, 12, 255))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Subtle radial glow from center
    for r in range(480, 0, -20):
        alpha = int(45 * (1.0 - r / 480.0))
        draw.ellipse([cx - r * 1.6, cy - r, cx + r * 1.6, cy + r], fill=(0, 110, 255, alpha))

    # Dynamic central geometric composition (Layered translucent diamond/hexagonal glass facets)
    facets = [
        # Top-left wing
        ([(cx - 320, cy), (cx - 80, cy - 160), (cx, cy), (cx - 160, cy + 80)], (0, 210, 255, 120)),
        # Top-right wing
        ([(cx, cy), (cx + 80, cy - 160), (cx + 320, cy), (cx + 160, cy + 80)], (0, 102, 255, 120)),
        # Bottom-left core
        ([(cx - 240, cy + 40), (cx, cy), (cx - 60, cy + 220), (cx - 200, cy + 180)], (121, 40, 202, 130)),
        # Bottom-right core
        ([(cx, cy), (cx + 240, cy + 40), (cx + 200, cy + 180), (cx + 60, cy + 220)], (168, 85, 247, 130)),
        # Center crystal diamond
        ([(cx, cy - 110), (cx + 90, cy), (cx, cy + 110), (cx - 90, cy)], (0, 230, 255, 160)),
        # Inner violet core
        ([(cx, cy - 65), (cx + 55, cy), (cx, cy + 65), (cx - 55, cy)], (147, 51, 234, 180)),
    ]

    for poly, col in facets:
        draw.polygon(poly, fill=col)

    # Blur overlay slightly for sophisticated glassmorphism
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=8))
    final_img = Image.alpha_composite(img, overlay)

    # Sharp crisp inner accents
    crisp = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(crisp)
    cdraw.polygon([(cx, cy - 90), (cx + 70, cy), (cx, cy + 90), (cx - 70, cy)], outline=(0, 240, 255, 210), width=2)
    cdraw.polygon([(cx, cy - 45), (cx + 35, cy), (cx, cy + 45), (cx - 35, cy)], outline=(199, 125, 255, 220), width=2)

    return Image.alpha_composite(final_img, crisp).convert("RGB")


# 2. Cosmic Horizon
def render_cosmic_horizon():
    img = create_base_canvas((3, 5, 14, 255))
    draw = ImageDraw.Draw(img)

    # Upper sky gradient
    for y in range(HEIGHT // 2):
        t = y / (HEIGHT / 2)
        r = int(3 + t * 12)
        g = int(5 + t * 24)
        b = int(14 + t * 50)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # Planetary curved horizon arc
    arc_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    adraw = ImageDraw.Draw(arc_layer)
    cx, cy = WIDTH // 2, HEIGHT + 480
    rad = 900

    # Glowing atmospheric limb
    for glow in range(80, 0, -4):
        alpha = int(90 * (1.0 - glow / 80.0))
        adraw.ellipse([cx - (rad + glow) * 1.8, cy - (rad + glow), cx + (rad + glow) * 1.8, cy + (rad + glow)],
                      outline=(0, 180, 255, alpha), width=3)

    # Horizon violet border
    adraw.ellipse([cx - rad * 1.8, cy - rad, cx + rad * 1.8, cy + rad], fill=(8, 12, 28, 255), outline=(138, 43, 226, 240), width=3)
    arc_layer = arc_layer.filter(ImageFilter.GaussianBlur(radius=4))

    return Image.alpha_composite(img, arc_layer).convert("RGB")


# 3. Infinite Motion
def render_infinite_motion():
    img = create_base_canvas((4, 7, 16, 255))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Smooth harmonic sine waves
    waves = [
        (0.0022, 140, HEIGHT // 2 - 60, (0, 210, 255, 60), 4),
        (0.0028, 110, HEIGHT // 2, (0, 110, 255, 75), 6),
        (0.0034, 160, HEIGHT // 2 + 50, (121, 40, 202, 70), 5),
        (0.0019, 190, HEIGHT // 2 - 20, (168, 85, 247, 50), 4),
        (0.0040, 80, HEIGHT // 2 + 90, (0, 240, 255, 90), 3),
    ]

    for freq, amp, y_mid, col, thickness in waves:
        points = []
        for x in range(0, WIDTH, 4):
            y = y_mid + amp * math.sin(x * freq + amp) + (amp * 0.4) * math.cos(x * freq * 1.5)
            points.append((x, y))
        draw.line(points, fill=col, width=thickness, joint="curve")

    # Wide diffuse flow ribbon
    ribbon = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(ribbon)
    ribbon_pts = []
    for x in range(0, WIDTH, 8):
        y = HEIGHT // 2 + 100 * math.sin(x * 0.0025)
        ribbon_pts.append((x, y))
    rdraw.line(ribbon_pts, fill=(0, 140, 255, 45), width=70, joint="curve")
    ribbon = ribbon.filter(ImageFilter.GaussianBlur(radius=18))

    res = Image.alpha_composite(img, ribbon)
    return Image.alpha_composite(res, overlay).convert("RGB")


# 4. Digital Dimensions
def render_digital_dimensions():
    img = create_base_canvas((5, 8, 18, 255))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    cx, cy = WIDTH // 2, HEIGHT // 2

    # Isometric minimal futuristic planes
    planes = [
        ([(cx - 300, cy - 100), (cx, cy - 220), (cx + 300, cy - 100), (cx, cy + 20)], (0, 102, 255, 50), (0, 210, 255, 160)),
        ([(cx - 300, cy - 100), (cx, cy + 20), (cx, cy + 220), (cx - 300, cy + 100)], (121, 40, 202, 60), (121, 40, 202, 170)),
        ([(cx + 300, cy - 100), (cx, cy + 20), (cx, cy + 220), (cx + 300, cy + 100)], (168, 85, 247, 50), (168, 85, 247, 160)),
        # Inner hovering floating plane
        ([(cx - 160, cy - 20), (cx, cy - 90), (cx + 160, cy - 20), (cx, cy + 50)], (0, 220, 255, 90), (0, 240, 255, 220)),
    ]

    for poly, fill_col, outline_col in planes:
        draw.polygon(poly, fill=fill_col, outline=outline_col)

    # Accent perspective lines
    draw.line([(cx, cy - 220), (cx, cy - 360)], fill=(0, 210, 255, 120), width=1)
    draw.line([(cx - 300, cy - 100), (cx - 460, cy - 160)], fill=(0, 102, 255, 100), width=1)
    draw.line([(cx + 300, cy - 100), (cx + 460, cy - 160)], fill=(168, 85, 247, 100), width=1)

    return Image.alpha_composite(img, overlay).convert("RGB")


# 5. Midnight Flow
def render_midnight_flow():
    img = create_base_canvas((2, 3, 7, 255))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Ultra-deep nocturnal caustics
    for i in range(5):
        cx = int(WIDTH * (0.2 + i * 0.15))
        cy = int(HEIGHT * (0.4 + (i % 3) * 0.15))
        rx = 340 + i * 40
        ry = 220 + i * 30
        col = (0, 60 + i * 18, 140 + i * 20, 28) if i % 2 == 0 else (70 + i * 15, 20 + i * 10, 130 + i * 20, 26)
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)

    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=55))
    return Image.alpha_composite(img, overlay).convert("RGB")


# 6. Electric Geometry
def render_electric_geometry():
    img = create_base_canvas((4, 6, 14, 255))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    cx, cy = WIDTH // 2, HEIGHT // 2

    # Angular modern polygons intersecting in central space
    polys = [
        ([(cx - 360, cy - 180), (cx - 100, cy - 260), (cx - 40, cy - 40), (cx - 280, cy)], (0, 180, 255, 90)),
        ([(cx + 100, cy - 260), (cx + 360, cy - 180), (cx + 280, cy), (cx + 40, cy - 40)], (0, 102, 255, 90)),
        ([(cx - 280, cy), (cx - 40, cy - 40), (cx, cy + 180), (cx - 200, cy + 220)], (121, 40, 202, 100)),
        ([(cx + 40, cy - 40), (cx + 280, cy), (cx + 200, cy + 220), (cx, cy + 180)], (168, 85, 247, 100)),
    ]

    for p, col in polys:
        draw.polygon(p, fill=col, outline=(0, 230, 255, 140))

    # Center floating shard
    draw.polygon([(cx, cy - 70), (cx + 60, cy), (cx, cy + 70), (cx - 60, cy)],
                 fill=(0, 220, 255, 170), outline=(255, 255, 255, 210))

    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=3))
    return Image.alpha_composite(img, overlay).convert("RGB")


# 7. Beyond Space
def render_beyond_space():
    img = create_base_canvas((3, 4, 10, 255))
    nebula = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(nebula)

    # Layered atmospheric cosmic clouds
    clouds = [
        (WIDTH * 0.45, HEIGHT * 0.45, 520, 320, (0, 120, 220, 42)),
        (WIDTH * 0.55, HEIGHT * 0.52, 480, 290, (120, 40, 190, 48)),
        (WIDTH * 0.50, HEIGHT * 0.40, 360, 220, (0, 190, 240, 45)),
        (WIDTH * 0.52, HEIGHT * 0.58, 420, 240, (160, 70, 220, 40)),
    ]

    for x, y, rx, ry, col in clouds:
        draw.ellipse([x - rx, y - ry, x + rx, y + ry], fill=col)

    nebula = nebula.filter(ImageFilter.GaussianBlur(radius=60))
    return Image.alpha_composite(img, nebula).convert("RGB")


# 8. Quantum
def render_quantum():
    img = create_base_canvas((5, 7, 16, 255))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    cx, cy = WIDTH // 2, HEIGHT // 2

    # Concentric probability density rings (No orbits/circuits, pure math waves)
    for r in range(40, 380, 35):
        alpha = int(120 * (1.0 - r / 380.0))
        col = (0, 210, 255, alpha) if (r // 35) % 2 == 0 else (168, 85, 247, alpha)
        draw.ellipse([cx - r * 1.5, cy - r, cx + r * 1.5, cy + r], outline=col, width=1)

    # Quantum nodal energy nodes
    nodes = [
        (cx - 160, cy - 60, 14, (0, 220, 255, 220)),
        (cx + 160, cy - 60, 14, (0, 120, 255, 220)),
        (cx - 90, cy + 80, 16, (121, 40, 202, 220)),
        (cx + 90, cy + 80, 16, (168, 85, 247, 220)),
        (cx, cy, 20, (0, 240, 255, 255)),
    ]
    for nx, ny, rad, col in nodes:
        draw.ellipse([nx - rad, ny - rad, nx + rad, ny + rad], fill=col)

    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=2))
    return Image.alpha_composite(img, overlay).convert("RGB")


# 9. Aurora
def render_aurora():
    img = create_base_canvas((3, 5, 12, 255))
    aurora_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(aurora_layer)

    # Vertical atmospheric light curtains
    for x in range(0, WIDTH, 12):
        t = x / WIDTH
        curtain_h = int(320 + 160 * math.sin(t * 7.0) + 90 * math.cos(t * 13.0))
        y_top = int(140 + 60 * math.sin(t * 4.5))
        
        # Color transition from cyan to violet
        col_cyan = (0, 220, 255, int(70 * math.sin(t * math.pi)))
        col_violet = (150, 60, 230, int(65 * math.sin(t * math.pi)))

        draw.line([(x, y_top), (x, y_top + curtain_h // 2)], fill=col_cyan, width=14)
        draw.line([(x, y_top + curtain_h // 2), (x, y_top + curtain_h)], fill=col_violet, width=14)

    aurora_layer = aurora_layer.filter(ImageFilter.GaussianBlur(radius=26))
    return Image.alpha_composite(img, aurora_layer).convert("RGB")


# 10. Pure Minimal
def render_pure_minimal():
    img = create_base_canvas((4, 6, 12, 255))
    draw = ImageDraw.Draw(img)

    # Subtle smooth dark vertical gradient
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(4 + t * 6)
        g = int(6 + t * 8)
        b = int(12 + t * 16)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # Extremely subtle 2x2 four-pane geometric window watermark in center
    cx, cy = WIDTH // 2, HEIGHT // 2
    pane = 42
    gap = 10
    x0 = cx - (pane * 2 + gap) // 2
    y0 = cy - (pane * 2 + gap) // 2
    x1 = x0 + pane + gap
    y1 = y0 + pane + gap

    # Very low contrast for distraction-free purity
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rounded_rectangle([x0, y0, x0 + pane, y0 + pane], radius=6, fill=(0, 210, 255, 30))
    odraw.rounded_rectangle([x1, y0, x1 + pane, y0 + pane], radius=6, fill=(0, 102, 255, 30))
    odraw.rounded_rectangle([x0, y1, x0 + pane, y1 + pane], radius=6, fill=(121, 40, 202, 30))
    odraw.rounded_rectangle([x1, y1, x1 + pane, y1 + pane], radius=6, fill=(168, 85, 247, 30))

    return Image.alpha_composite(img, overlay).convert("RGB")


WALLPAPER_ROSTER = [
    ("giri-origin.png", "Giri Origin", "Signature Default", "Giri Dark / Modern", render_giri_origin, True),
    ("cosmic-horizon.png", "Cosmic Horizon", "Space Landscape", "Giri Midnight", render_cosmic_horizon, False),
    ("infinite-motion.png", "Infinite Motion", "Flowing Abstract", "Giri Modern", render_infinite_motion, False),
    ("digital-dimensions.png", "Digital Dimensions", "Futuristic Architecture", "Giri Dark", render_digital_dimensions, False),
    ("midnight-flow.png", "Midnight Flow", "Deep Contrast", "Giri Midnight", render_midnight_flow, False),
    ("electric-geometry.png", "Electric Geometry", "Geometric Abstract", "Giri Dark", render_electric_geometry, False),
    ("beyond-space.png", "Beyond Space", "Cosmic Nebula", "Giri Midnight", render_beyond_space, False),
    ("quantum.png", "Quantum", "Scientific Minimal", "Giri Modern", render_quantum, False),
    ("aurora.png", "Aurora", "Atmospheric Wave", "Giri Dark", render_aurora, False),
    ("pure-minimal.png", "Pure Minimal", "Ultra-Clean Gradient", "Giri Classic", render_pure_minimal, False),
]


def generate_all_wallpapers(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    thumb_dir = os.path.join(out_dir, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)

    manifest = []

    print(f"[+] Generating {len(WALLPAPER_ROSTER)} official Giri OS wallpapers (1920x1080)...")
    for filename, name, category, theme, render_fn, is_default in WALLPAPER_ROSTER:
        full_path = os.path.join(out_dir, filename)
        thumb_path = os.path.join(thumb_dir, filename)

        print(f"    -> Rendering '{name}' ({filename})...")
        img = render_fn()
        img.save(full_path, "PNG", optimize=True)

        # Generate lightweight 320x180 thumbnail for instant loading in Giri Control
        thumb = img.resize((THUMB_WIDTH, THUMB_HEIGHT), Image.Resampling.BILINEAR)
        thumb.save(thumb_path, "PNG", optimize=True)

        manifest.append({
            "id": filename.replace(".png", ""),
            "name": name,
            "filename": filename,
            "category": category,
            "paired_theme": theme,
            "is_default": is_default,
            "aspect_ratio": "16:9",
            "resolution": f"{WIDTH}x{HEIGHT}",
            "file_path": full_path,
            "thumb_path": thumb_path
        })

    # Save wallpaper metadata
    manifest_file = os.path.join(out_dir, "wallpapers.json")
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"[+] All 10 wallpapers and thumbnails generated successfully.")
    print(f"    Metadata index saved to: {manifest_file}")


if __name__ == "__main__":
    target = os.path.dirname(os.path.abspath(__file__))
    generate_all_wallpapers(target)
