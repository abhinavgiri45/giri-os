#!/usr/bin/env python3
"""
Giri OS — Logo & Icon PNG Export Engine
Author: Abhinav Giri / Giri OS Core Engineering Team
License: GPL-3.0-or-later

Renders high-resolution transparent PNG exports for:
1. giri-os-icon.png (512x512 symbol-only)
2. giri-os-logo.png (1520x400 transparent full logo)
"""

import os
from PIL import Image, ImageDraw, ImageFont


def render_icon_png(output_path, size=512):
    """
    Renders the four-pane geometric window symbol on a transparent 512x512 canvas.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Dimensions for 512x512 canvas
    # Total symbol area: 392x392, centered at (256, 256)
    # Start: x0 = 60, y0 = 60
    # Spacing between panes: 36px
    # Pane size: (392 - 36) / 2 = 178x178
    # Radius: 24px
    pane_size = 178
    gap = 36
    radius = 24

    x0 = 60
    y0 = 60
    x1 = x0 + pane_size + gap
    y1 = y0 + pane_size + gap

    # Colors
    c_tl = (0, 210, 255, 255)   # #00D2FF (Electric Cyan-Blue)
    c_tr = (0, 102, 255, 255)   # #0066FF (Vivid Electric Blue)
    c_bl = (121, 40, 202, 255)  # #7928CA (Electric Violet)
    c_br = (168, 85, 247, 255)  # #A855F7 (Bright Violet)

    # Draw the 4 panes
    draw.rounded_rectangle([x0, y0, x0 + pane_size, y0 + pane_size], radius=radius, fill=c_tl)
    draw.rounded_rectangle([x1, y0, x1 + pane_size, y0 + pane_size], radius=radius, fill=c_tr)
    draw.rounded_rectangle([x0, y1, x0 + pane_size, y1 + pane_size], radius=radius, fill=c_bl)
    draw.rounded_rectangle([x1, y1, x1 + pane_size, y1 + pane_size], radius=radius, fill=c_br)

    img.save(output_path, "PNG")
    print(f"[+] Saved {output_path} ({size}x{size})")


def render_logo_png(output_path, width=1520, height=400):
    """
    Renders the full horizontal logo (Symbol + Wordmark + Tagline) on a transparent canvas.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scale 2x relative to 760x200 SVG
    # Symbol: x from 70, y from 60
    # Pane size: 128x128, gap: 24px, radius: 20px
    pane_size = 128
    gap = 24
    radius = 20

    x0 = 70
    y0 = 60
    x1 = x0 + pane_size + gap
    y1 = y0 + pane_size + gap

    c_tl = (0, 210, 255, 255)   # #00D2FF
    c_tr = (0, 102, 255, 255)   # #0066FF
    c_bl = (121, 40, 202, 255)  # #7928CA
    c_br = (168, 85, 247, 255)  # #A855F7

    draw.rounded_rectangle([x0, y0, x0 + pane_size, y0 + pane_size], radius=radius, fill=c_tl)
    draw.rounded_rectangle([x1, y0, x1 + pane_size, y0 + pane_size], radius=radius, fill=c_tr)
    draw.rounded_rectangle([x0, y1, x0 + pane_size, y1 + pane_size], radius=radius, fill=c_bl)
    draw.rounded_rectangle([x1, y1, x1 + pane_size, y1 + pane_size], radius=radius, fill=c_br)

    # Wordmark typography
    # Attempt to load clean sans-serif font
    font_large = None
    font_tagline = None
    system_fonts = [
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\calibrib.ttf",
    ]
    for fpath in system_fonts:
        if os.path.exists(fpath):
            try:
                font_large = ImageFont.truetype(fpath, 140)
                font_tagline = ImageFont.truetype(fpath, 28)
                break
            except Exception:
                pass

    if not font_large:
        font_large = ImageFont.load_default()
        font_tagline = ImageFont.load_default()

    # Draw Wordmark: "GIRI OS"
    text_x = 450
    text_y = 65

    # GIRI in #0066FF
    draw.text((text_x, text_y), "GIRI", fill=(0, 102, 255, 255), font=font_large)

    # Compute bounding box to offset "OS"
    bbox = draw.textbbox((text_x, text_y), "GIRI", font=font_large)
    os_x = bbox[2] + 35
    # OS in #7928CA
    draw.text((os_x, text_y), "OS", fill=(121, 40, 202, 255), font=font_large)

    # Divider bar
    bar_y = 250
    draw.rectangle([text_x, bar_y, text_x + 920, bar_y + 4], fill=(0, 210, 255, 120))

    # Tagline: "ONE SYSTEM. INFINITE POSSIBILITIES."
    tagline_y = 280
    draw.text((text_x + 2, tagline_y), "ONE SYSTEM. INFINITE POSSIBILITIES.", fill=(100, 116, 139, 255), font=font_tagline)

    img.save(output_path, "PNG")
    print(f"[+] Saved {output_path} ({width}x{height})")


if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    icon_out = os.path.join(out_dir, "giri-os-icon.png")
    logo_out = os.path.join(out_dir, "giri-os-logo.png")

    render_icon_png(icon_out)
    render_logo_png(logo_out)
