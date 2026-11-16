"""
Giri OS Plymouth Theme Asset Generator
Generates pixel-perfect PNG assets for Plymouth boot splash.
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
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data)
    png.extend(struct.pack(">I", 13))
    png.extend(b"IHDR")
    png.extend(ihdr_data)
    png.extend(struct.pack(">I", ihdr_crc))
    
    idat_crc = zlib.crc32(b"IDAT" + compressed)
    png.extend(struct.pack(">I", len(compressed)))
    png.extend(b"IDAT")
    png.extend(compressed)
    png.extend(struct.pack(">I", idat_crc))
    
    iend_crc = zlib.crc32(b"IEND")
    png.extend(struct.pack(">I", 0))
    png.extend(b"IEND")
    png.extend(struct.pack(">I", iend_crc))
    
    with open(output_path, "wb") as f:
        f.write(png)

def generate_plymouth_assets(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Logo sprite (160x160)
    logo_path = os.path.join(out_dir, "logo.png")
    print(f"Generating {logo_path}...")
    def logo_pixel(x, y):
        cx, cy = 80, 80
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx*dx + dy*dy)
        
        # Outer boundary of 'G'
        if dist > 68 or dist < 22:
            return (0, 0, 0, 0)
            
        # Draw dynamic G letter arc
        angle = math.atan2(dy, dx)
        # Gap between -40 deg and 30 deg on the right
        if -0.7 < angle < 0.5 and dist > 35:
            # Check for horizontal bar
            if abs(dy) < 8 and 10 < dx < 50:
                return (0, 240, 255, 255)
            return (0, 0, 0, 0)
            
        # Electric blue to violet gradient across X
        t = (x - 20) / 120.0
        r = int(min(255, max(0, 0 + t * 150)))
        g = int(min(255, max(0, 240 - t * 140)))
        b = int(min(255, max(0, 255)))
        return (r, g, b, 255)
        
    create_png(160, 160, logo_pixel, logo_path)
    
    # 2. Orbital ring sprite (240x240)
    ring_path = os.path.join(out_dir, "ring.png")
    print(f"Generating {ring_path}...")
    def ring_pixel(x, y):
        cx, cy = 120, 120
        dx = (x - cx)
        dy = (y - cy) * 2.2 # Elliptical
        dist = math.sqrt(dx*dx + dy*dy)
        
        # Thin ring between 98 and 106
        if 98 <= dist <= 106:
            # Satellite node at the tip
            if abs(x - 220) < 6 and abs(y - 120) < 6:
                return (255, 255, 255, 255)
            alpha = int(220 * (1.0 - abs(dist - 102) / 4.0))
            return (0, 210, 255, alpha)
        return (0, 0, 0, 0)
        
    create_png(240, 240, ring_pixel, ring_path)
    
    # 3. Progress bar background (320x8)
    pbg_path = os.path.join(out_dir, "progress_bg.png")
    create_png(320, 8, lambda x, y: (16, 24, 44, 230), pbg_path)
    
    # 4. Progress bar foreground fill (316x4)
    pfg_path = os.path.join(out_dir, "progress_fg.png")
    def pfg_pixel(x, y):
        # Gradient cyan to violet
        t = x / 316.0
        r = int(0 + t * 120)
        g = int(220 - t * 60)
        b = 255
        return (r, g, b, 255)
    create_png(316, 4, pfg_pixel, pfg_path)
    
    print("All Plymouth boot splash assets generated successfully.")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_plymouth_assets(target)
