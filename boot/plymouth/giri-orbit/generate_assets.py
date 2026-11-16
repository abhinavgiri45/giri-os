"""
Giri OS Plymouth Theme Asset Generator
Generates pixel-perfect PNG assets for Plymouth boot splash using the official
four-pane geometric window logo (2x2 symmetrical formation).
"""

import os
import struct
import zlib
import math

def create_png(width, height, pixel_func, output_path):
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)
        for x in range(width):
            r, g, b, a = pixel_func(x, y)
            raw_data.extend((r, g, b, a))
            
    compressed = zlib.compress(bytes(raw_data), level=9)
    png = bytearray()
    png.extend(b"\x89PNG\r\n\x1a\n")
    
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png.extend(struct.pack(">I", 13))
    png.extend(b"IHDR")
    png.extend(ihdr_data)
    png.extend(struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data)))
    
    png.extend(struct.pack(">I", len(compressed)))
    png.extend(b"IDAT")
    png.extend(compressed)
    png.extend(struct.pack(">I", zlib.crc32(b"IDAT" + compressed)))
    
    png.extend(struct.pack(">I", 0))
    png.extend(b"IEND")
    png.extend(struct.pack(">I", zlib.crc32(b"IEND")))
    
    with open(output_path, "wb") as f:
        f.write(png)

def generate_plymouth_assets(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Official Four-Pane Geometric Window Logo sprite (160x160)
    # Total symbol area: 136x136, centered (offset 12)
    # Panes are 62x62 with 12px gap
    logo_path = os.path.join(out_dir, "logo.png")
    print(f"Generating {logo_path}...")
    def logo_pixel(x, y):
        x0, y0 = 12, 12
        p_size = 62
        gap = 12
        r = 9  # corner radius
        
        x1 = x0 + p_size + gap
        y1 = y0 + p_size + gap
        
        def in_rounded_box(px, py, bx, by, size, rad):
            if not (bx <= px < bx + size and by <= py < by + size):
                return False
            # Check corners
            dx = min(px - bx, bx + size - 1 - px)
            dy = min(py - by, by + size - 1 - py)
            if dx < rad and dy < rad:
                dist = math.sqrt((rad - dx)**2 + (rad - dy)**2)
                return dist <= rad
            return True

        # Top-Left: #00D2FF
        if in_rounded_box(x, y, x0, y0, p_size, r):
            return (0, 210, 255, 255)
        # Top-Right: #0066FF
        elif in_rounded_box(x, y, x1, y0, p_size, r):
            return (0, 102, 255, 255)
        # Bottom-Left: #7928CA
        elif in_rounded_box(x, y, x0, y1, p_size, r):
            return (121, 40, 202, 255)
        # Bottom-Right: #A855F7
        elif in_rounded_box(x, y, x1, y1, p_size, r):
            return (168, 85, 247, 255)
            
        return (0, 0, 0, 0)
        
    create_png(160, 160, logo_pixel, logo_path)
    
    # 2. Subtle geometric accent beacon (200x200) replacing old orbital ring
    ring_path = os.path.join(out_dir, "ring.png")
    create_png(200, 200, lambda x, y: (0, 0, 0, 0), ring_path)
    
    # 3. Progress bar background (320x8)
    pbg_path = os.path.join(out_dir, "progress_bg.png")
    create_png(320, 8, lambda x, y: (16, 24, 44, 230), pbg_path)
    
    # 4. Progress bar foreground fill (316x4)
    pfg_path = os.path.join(out_dir, "progress_fg.png")
    def pfg_pixel(x, y):
        t = x / 316.0
        r = int(0 + t * 121)
        g = int(210 - t * 170)
        b = int(255 - t * 53)
        return (r, g, b, 255)
    create_png(316, 4, pfg_pixel, pfg_path)
    
    print("All Plymouth boot splash assets generated successfully.")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_plymouth_assets(target)
