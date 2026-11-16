"""
Giri OS GRUB Theme Asset Generator
Generates pixel-perfect PNG assets for GRUB gfxmenu featuring the official
four-pane geometric window logo (2x2 symmetrical formation).
"""

import os
import struct
import zlib
import math

def create_png(width, height, pixel_func, output_path):
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # Filter type 0 (None)
        for x in range(width):
            r, g, b, a = pixel_func(x, y)
            raw_data.extend((r, g, b, a))
            
    compressed = zlib.compress(bytes(raw_data), level=9)
    
    png = bytearray()
    png.extend(b"\x89PNG\r\n\x1a\n")
    
    # IHDR
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png.extend(struct.pack(">I", 13))
    png.extend(b"IHDR")
    png.extend(ihdr_data)
    png.extend(struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data)))
    
    # IDAT
    png.extend(struct.pack(">I", len(compressed)))
    png.extend(b"IDAT")
    png.extend(compressed)
    png.extend(struct.pack(">I", zlib.crc32(b"IDAT" + compressed)))
    
    # IEND
    png.extend(struct.pack(">I", 0))
    png.extend(b"IEND")
    png.extend(struct.pack(">I", zlib.crc32(b"IEND")))
    
    with open(output_path, "wb") as f:
        f.write(png)

def generate_assets(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Background image (1920x1080)
    bg_path = os.path.join(out_dir, "background.png")
    print(f"Generating {bg_path} (1920x1080)...")
    def bg_pixel(x, y):
        # Clean minimalist deep navy/black gradient
        dx = (x - 960) / 960.0
        dy = (y - 500) / 540.0
        dist = math.sqrt(dx*dx + dy*dy)
        
        base_r = int(max(6, 16 - dist * 10))
        base_g = int(max(10, 22 - dist * 14))
        base_b = int(max(24, 48 - dist * 28))
        return (base_r, base_g, base_b, 255)
        
    create_png(1920, 1080, bg_pixel, bg_path)
    
    # 2. Header Logo with 2x2 Geometric Window Pane (440x90)
    logo_path = os.path.join(out_dir, "logo.png")
    print(f"Generating {logo_path}...")
    def logo_pixel(x, y):
        # Left symbol: x from 20 to 88, y from 11 to 79 (68x68 total, 8px gap)
        # Panes are 30x30 with 8px gap
        if 20 <= x <= 88 and 11 <= y <= 79:
            # Top-left pane: x in [20, 50], y in [11, 41]
            if 20 <= x <= 50 and 11 <= y <= 41:
                return (0, 210, 255, 255)  # #00D2FF
            # Top-right pane: x in [58, 88], y in [11, 41]
            elif 58 <= x <= 88 and 11 <= y <= 41:
                return (0, 102, 255, 255)  # #0066FF
            # Bottom-left pane: x in [20, 50], y in [49, 79]
            elif 20 <= x <= 50 and 49 <= y <= 79:
                return (121, 40, 202, 255) # #7928CA
            # Bottom-right pane: x in [58, 88], y in [49, 79]
            elif 58 <= x <= 88 and 49 <= y <= 79:
                return (168, 85, 247, 255) # #A855F7
            return (0, 0, 0, 0)
            
        return (0, 0, 0, 0)
    create_png(440, 90, logo_pixel, logo_path)
    
    # 3. Selection Box Pixmaps
    for part in ["c", "n", "s", "w", "e", "nw", "ne", "sw", "se"]:
        p_path = os.path.join(out_dir, f"select_box_{part}.png")
        create_png(32, 32, lambda x, y: (0, 102, 255, 180), p_path)

    # 4. Menu Box Pixmaps
    for part in ["c", "n", "s", "w", "e", "nw", "ne", "sw", "se"]:
        m_path = os.path.join(out_dir, f"menu_box_{part}.png")
        create_png(32, 32, lambda x, y: (12, 18, 36, 190), m_path)

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
