"""
Giri OS GRUB Theme Asset Generator
Generates pixel-perfect PNG assets for GRUB gfxmenu without external dependencies (pure Python struct + zlib).
"""

import os
import struct
import zlib
import math

def create_png(width, height, pixel_func, output_path):
    """
    Creates a valid 24-bit RGB or 32-bit RGBA PNG file.
    pixel_func(x, y) returns (r, g, b, a) with 0-255 values.
    """
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # Filter type 0 (None)
        for x in range(width):
            r, g, b, a = pixel_func(x, y)
            raw_data.extend((r, g, b, a))
            
    compressed = zlib.compress(bytes(raw_data), level=9)
    
    png = bytearray()
    png.extend(b"\x89PNG\r\n\x1a\n")
    
    # IHDR chunk
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data)
    png.extend(struct.pack(">I", 13))
    png.extend(b"IHDR")
    png.extend(ihdr_data)
    png.extend(struct.pack(">I", ihdr_crc))
    
    # IDAT chunk
    idat_crc = zlib.crc32(b"IDAT" + compressed)
    png.extend(struct.pack(">I", len(compressed)))
    png.extend(b"IDAT")
    png.extend(compressed)
    png.extend(struct.pack(">I", idat_crc))
    
    # IEND chunk
    iend_crc = zlib.crc32(b"IEND")
    png.extend(struct.pack(">I", 0))
    png.extend(b"IEND")
    png.extend(struct.pack(">I", iend_crc))
    
    with open(output_path, "wb") as f:
        f.write(png)

def generate_assets(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Background image (1920x1080)
    bg_path = os.path.join(out_dir, "background.png")
    print(f"Generating {bg_path} (1920x1080)...")
    def bg_pixel(x, y):
        # Center glow around (960, 500)
        dx = (x - 960) / 960.0
        dy = (y - 500) / 540.0
        dist = math.sqrt(dx*dx + dy*dy)
        
        # Deep space dark gradient
        base_r = int(max(4, 18 - dist * 12))
        base_g = int(max(7, 24 - dist * 16))
        base_b = int(max(18, 55 - dist * 35))
        
        # Subtle orbital glow tint
        if dist < 0.6:
            factor = (0.6 - dist) / 0.6
            base_r = int(min(255, base_r + 20 * factor))
            base_g = int(min(255, base_g + 50 * factor))
            base_b = int(min(255, base_b + 90 * factor))
            
        return (base_r, base_g, base_b, 255)
        
    create_png(1920, 1080, bg_pixel, bg_path)
    
    # 2. Logo image (440x90)
    logo_path = os.path.join(out_dir, "logo.png")
    print(f"Generating {logo_path}...")
    def logo_pixel(x, y):
        # Emblazoned header badge with electric blue and violet gradient
        if x < 4 or x >= 436 or y < 4 or y >= 86:
            return (0, 0, 0, 0)
        # Inner fill
        t = x / 440.0
        r = int(12 + 15 * t)
        g = int(22 + 40 * t)
        b = int(48 + 90 * t)
        return (r, g, b, 230)
    create_png(440, 90, logo_pixel, logo_path)
    
    # 3. Selection Box Pixmaps (Used for active menu item highlight)
    for part in ["c", "n", "s", "w", "e", "nw", "ne", "sw", "se"]:
        p_path = os.path.join(out_dir, f"select_box_{part}.png")
        def select_pixel(x, y):
            # Electric cyan-violet selection highlight with 50% transparency
            return (18, 120, 220, 200)
        create_png(32, 32, select_pixel, p_path)

    # 4. Menu Box Pixmaps (Background container for boot list)
    for part in ["c", "n", "s", "w", "e", "nw", "ne", "sw", "se"]:
        m_path = os.path.join(out_dir, f"menu_box_{part}.png")
        def menu_pixel(x, y):
            # Subtle deep navy translucent panel
            return (10, 16, 32, 175)
        create_png(32, 32, menu_pixel, m_path)

    # 5. Progress Bar
    pbar_path = os.path.join(out_dir, "progress_bar_c.png")
    create_png(16, 8, lambda x, y: (20, 30, 50, 220), pbar_path)
    
    phl_path = os.path.join(out_dir, "progress_highlight_c.png")
    create_png(16, 8, lambda x, y: (0, 210, 255, 255), phl_path)
    
    print("All GRUB 2 theme assets generated successfully.")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_assets(target)
