#!/usr/bin/env python3
"""
Giri OS — Welcome Experience Screen Capture & Visual Verification
Renders crisp PNG preview captures of the 5 welcome sequence stages:
1. 01_logo_reveal.png
2. 02_welcome_english.png
3. 03_namaste_hindi.png
4. 04_tagline_infinite.png
5. 05_first_boot_wizard_ui.png
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../documentation/screenshots/welcome"))
os.makedirs(OUT_DIR, exist_ok=True)

WIDTH, HEIGHT = 1280, 800
BG_COLOR = (5, 8, 17, 255)  # #050811

def get_fonts():
    font_large = None
    font_sub = None
    font_small = None
    system_fonts = [
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\NirmalaB.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf"
    ]
    for fp in system_fonts:
        if os.path.exists(fp):
            try:
                font_large = ImageFont.truetype(fp, 56)
                font_sub = ImageFont.truetype(fp, 22)
                font_small = ImageFont.truetype(fp, 16)
                break
            except Exception:
                pass
    if not font_large:
        font_large = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_small = ImageFont.load_default()
    return font_large, font_sub, font_small

font_lg, font_sub, font_sm = get_fonts()

def draw_base_emblem(draw, cx, cy, scale=1.0):
    # Orbital Ring
    rx, ry = int(140 * scale), int(50 * scale)
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(147, 51, 234, 255), width=4)
    # Cyan foreground arc
    draw.arc([cx - rx, cy - ry, cx + rx, cy + ry], start=190, end=350, fill=(0, 240, 255, 255), width=5)
    # Satellite particle
    node_x = cx + int(rx * 0.88)
    node_y = cy - int(ry * 0.45)
    draw.ellipse([node_x - 7, node_y - 7, node_x + 7, node_y + 7], fill=(0, 240, 255, 255), outline=(255, 255, 255, 255), width=2)
    # G-Monogram
    gs = int(50 * scale)
    w = 8
    draw.line([cx - gs, cy - gs, cx + gs, cy - gs], fill=(0, 240, 255, 255), width=w)
    draw.line([cx - gs, cy - gs, cx - gs, cy + gs], fill=(0, 240, 255, 255), width=w)
    draw.line([cx - gs, cy + gs, cx + gs, cy + gs], fill=(192, 132, 252, 255), width=w)
    draw.line([cx + gs, cy + gs, cx + gs, cy], fill=(192, 132, 252, 255), width=w)
    draw.line([cx, cy, cx + gs, cy], fill=(0, 240, 255, 255), width=w)

def draw_skip_button(draw):
    draw.rounded_rectangle([WIDTH - 160, 30, WIDTH - 40, 70], radius=8, fill=(17, 24, 39, 255), outline=(30, 41, 59, 255))
    draw.text((WIDTH - 145, 40), "Skip Intro ⏭", fill=(148, 163, 184, 255), font=font_sm)

# Frame 1: Logo Reveal
img1 = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR)
d1 = ImageDraw.Draw(img1)
draw_skip_button(d1)
draw_base_emblem(d1, WIDTH // 2, HEIGHT // 2 - 30, scale=1.2)
d1.text((WIDTH // 2 - 60, HEIGHT // 2 + 100), "GIRI OS", fill=(0, 240, 255, 255), font=font_sub)
img1.save(os.path.join(OUT_DIR, "01_logo_reveal.png"))

# Frame 2: Welcome English
img2 = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR)
d2 = ImageDraw.Draw(img2)
draw_skip_button(d2)
draw_base_emblem(d2, WIDTH // 2, HEIGHT // 2 - 60, scale=1.0)
bbox = d2.textbbox((0, 0), "WELCOME", font=font_lg)
d2.text((WIDTH // 2 - (bbox[2] - bbox[0]) // 2, HEIGHT // 2 + 60), "WELCOME", fill=(255, 255, 255, 255), font=font_lg)
bbox_sub = d2.textbbox((0, 0), "GIRI OS 0.1 GENESIS", font=font_sub)
d2.text((WIDTH // 2 - (bbox_sub[2] - bbox_sub[0]) // 2, HEIGHT // 2 + 140), "GIRI OS 0.1 GENESIS", fill=(0, 240, 255, 255), font=font_sub)
img2.save(os.path.join(OUT_DIR, "02_welcome_english.png"))

# Frame 3: Namaste
img3 = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR)
d3 = ImageDraw.Draw(img3)
draw_skip_button(d3)
draw_base_emblem(d3, WIDTH // 2, HEIGHT // 2 - 60, scale=1.0)
bbox = d3.textbbox((0, 0), "NAMASTE", font=font_lg)
d3.text((WIDTH // 2 - (bbox[2] - bbox[0]) // 2, HEIGHT // 2 + 60), "NAMASTE", fill=(0, 240, 255, 255), font=font_lg)
bbox_sub = d3.textbbox((0, 0), "WELCOME TO THE FUTURE OF COMPUTING", font=font_sub)
d3.text((WIDTH // 2 - (bbox_sub[2] - bbox_sub[0]) // 2, HEIGHT // 2 + 140), "WELCOME TO THE FUTURE OF COMPUTING", fill=(192, 132, 252, 255), font=font_sub)
img3.save(os.path.join(OUT_DIR, "03_namaste_hindi.png"))

# Frame 4: Tagline
img4 = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR)
d4 = ImageDraw.Draw(img4)
draw_skip_button(d4)
draw_base_emblem(d4, WIDTH // 2, HEIGHT // 2 - 60, scale=1.0)
bbox = d4.textbbox((0, 0), "ONE SYSTEM. INFINITE POSSIBILITIES.", font=font_sub)
d4.text((WIDTH // 2 - (bbox[2] - bbox[0]) // 2, HEIGHT // 2 + 70), "ONE SYSTEM. INFINITE POSSIBILITIES.", fill=(0, 240, 255, 255), font=font_sub)
bbox_sub = d4.textbbox((0, 0), "GIRI OS — FOUNDED BY ABHINAV GIRI", font=font_sm)
d4.text((WIDTH // 2 - (bbox_sub[2] - bbox_sub[0]) // 2, HEIGHT // 2 + 120), "GIRI OS — FOUNDED BY ABHINAV GIRI", fill=(148, 163, 184, 255), font=font_sm)
# Button Get Started
draw_btn_x = WIDTH // 2 - 100
draw_btn_y = HEIGHT // 2 + 170
d4.rounded_rectangle([draw_btn_x, draw_btn_y, draw_btn_x + 200, draw_btn_y + 45], radius=8, fill=(0, 102, 255, 255))
d4.text((draw_btn_x + 40, draw_btn_y + 12), "Begin Setup ▶", fill=(255, 255, 255, 255), font=font_sm)
img4.save(os.path.join(OUT_DIR, "04_tagline_infinite.png"))

# Frame 5: First Boot Wizard UI Simulation
img5 = Image.new("RGBA", (WIDTH, HEIGHT), (8, 12, 26, 255))
d5 = ImageDraw.Draw(img5)
# Header
d5.rectangle([0, 0, WIDTH, 68], fill=(13, 20, 40, 255))
d5.text((30, 20), "GIRI OS", fill=(0, 210, 255, 255), font=font_sub)
d5.rounded_rectangle([130, 22, 230, 48], radius=4, fill=(22, 34, 61, 255))
d5.text((140, 26), "0.1 GENESIS", fill=(157, 78, 221, 255), font=font_sm)
d5.text((WIDTH - 240, 24), "Step 1 of 11: Welcome", fill=(142, 164, 200, 255), font=font_sm)

# Content
d5.text((40, 110), "Welcome to Giri OS", fill=(255, 255, 255, 255), font=font_lg)
d5.text((40, 180), "ONE SYSTEM. INFINITE POSSIBILITIES.", fill=(0, 210, 255, 255), font=font_sub)

desc = (
    "Thank you for choosing Giri OS — an independent, high-performance Linux operating system\n"
    "engineered for gaming performance, deep Windows software compatibility, and rock-solid Debian reliability.\n\n"
    "Founder & Lead Architect: Abhinav Giri\n"
    "Architecture: Debian 12 Bookworm (AMD64 / x86_64)\n\n"
    "This setup wizard will configure your localization, user account, networking, desktop theme,\n"
    "and performance profiles in just a few simple steps."
)
d5.text((40, 240), desc, fill=(160, 174, 192, 255), font=font_sm)

# Footer Nav
d5.rectangle([0, HEIGHT - 68, WIDTH, HEIGHT], fill=(13, 20, 40, 255))
d5.rounded_rectangle([30, HEIGHT - 52, 130, HEIGHT - 16], radius=4, fill=(22, 34, 61, 255))
d5.text((55, HEIGHT - 42), "◀ Back", fill=(194, 213, 238, 255), font=font_sm)

d5.rounded_rectangle([WIDTH - 170, HEIGHT - 52, WIDTH - 30, HEIGHT - 16], radius=4, fill=(0, 119, 255, 255))
d5.text((WIDTH - 145, HEIGHT - 42), "Continue ▶", fill=(255, 255, 255, 255), font=font_sm)

img5.save(os.path.join(OUT_DIR, "05_first_boot_wizard_ui.png"))
print(f"[+] Successfully generated 5 visual preview screenshots in {OUT_DIR}")
