#!/usr/bin/env python3
"""
Giri OS — Brand Identity Proposals Generator
Generates full vector SVGs for 3 distinct proposed brand directions:
1. Concept 1: The Precision G (Architectural Monogram)
2. Concept 2: The Orbital Nexus (Celestial Horizon)
3. Concept 3: The Infinite Gateway (Hexagonal Möbius G)

For each concept, creates:
- Dark theme (full horizontal lockup with wordmark & tagline on #070913)
- Light theme (full horizontal lockup with wordmark & tagline on #FFFFFF)
- Monochrome (solid single-tone black on transparent, and white on black)
- Small icon (256x256 standalone symbol optimized for small-scale 16x16-32x32 legibility)
"""

import os

PROPOSALS_DIR = os.path.dirname(os.path.abspath(__file__))

# ==============================================================================
# CONCEPT 1: THE PRECISION G (ARCHITECTURAL MONOGRAM)
# ==============================================================================
# Geometry: Two interlocking dynamic geometric segments forming a futuristic 'G'
# Segment 1: Upper Canopy & Left Spine (Electric Cyan -> Blue)
# Segment 2: Base Foundation & Center Crossbar (Electric Violet -> Purple)
# Separated by an 8px diagonal negative space channel (angle 45°)

def get_concept_1_symbol(mode="dark", size=200):
    if mode == "mono_black":
        fill_1 = "#000000"
        fill_2 = "#000000"
        grad_def = ""
    elif mode == "mono_white":
        fill_1 = "#FFFFFF"
        fill_2 = "#FFFFFF"
        grad_def = ""
    elif mode == "light":
        grad_def = """
        <linearGradient id="c1_grad_a_lt" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#0066FF" />
          <stop offset="100%" stop-color="#003D99" />
        </linearGradient>
        <linearGradient id="c1_grad_b_lt" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#8B5CF6" />
          <stop offset="100%" stop-color="#6D28D9" />
        </linearGradient>
        """
        fill_1 = "url(#c1_grad_a_lt)"
        fill_2 = "url(#c1_grad_b_lt)"
    else: # dark
        grad_def = """
        <linearGradient id="c1_grad_a" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#00F0FF" />
          <stop offset="60%" stop-color="#0080FF" />
          <stop offset="100%" stop-color="#0055FF" />
        </linearGradient>
        <linearGradient id="c1_grad_b" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#C084FC" />
          <stop offset="60%" stop-color="#9333EA" />
          <stop offset="100%" stop-color="#6B21A8" />
        </linearGradient>
        <filter id="c1_glow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#00F0FF" flood-opacity="0.3"/>
        </filter>
        """
        fill_1 = "url(#c1_grad_a)"
        fill_2 = "url(#c1_grad_b)"

    # Clean geometric polygonal coordinates on a 200x200 box
    # Segment 1: Upper Canopy & Spine
    path_1 = """
    M 55,20 
    L 165,20 
    L 165,55 
    L 75,55 
    L 75,135 
    L 40,170 
    L 20,150 
    L 20,55 
    Z
    """

    # Segment 2: Base & Inward Locking Crossbar
    path_2 = """
    M 52,182 
    L 87,147 
    L 87,165 
    L 145,165 
    L 145,105 
    L 105,105 
    L 105,75 
    L 180,75 
    L 180,200 
    L 34,200 
    Z
    """

    glow_attr = 'filter="url(#c1_glow)"' if mode == "dark" else ""

    svg = f"""<g id="symbol-concept-1" {glow_attr}>
      <defs>{grad_def}</defs>
      <!-- Segment 1: Upper Spine & Canopy -->
      <path d="{path_1}" fill="{fill_1}" />
      <!-- Segment 2: Base & Locking Crossbar -->
      <path d="{path_2}" fill="{fill_2}" />
    </g>"""
    return svg


# ==============================================================================
# CONCEPT 2: THE ORBITAL NEXUS (CELESTIAL HORIZON)
# ==============================================================================
# Geometry: A cosmic aperture with an inclined planetary orbit ring, carrying an
# energy node, looping through a central geometric G core with a negative space slit.

def get_concept_2_symbol(mode="dark", size=200):
    if mode == "mono_black":
        ring_stroke = "#000000"
        core_fill = "#000000"
        node_fill = "#000000"
        grad_def = ""
    elif mode == "mono_white":
        ring_stroke = "#FFFFFF"
        core_fill = "#FFFFFF"
        node_fill = "#FFFFFF"
        grad_def = ""
    elif mode == "light":
        grad_def = """
        <linearGradient id="c2_core_lt" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#0284C7" />
          <stop offset="100%" stop-color="#0369A1" />
        </linearGradient>
        <linearGradient id="c2_ring_lt" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#7C3AED" />
          <stop offset="100%" stop-color="#0284C7" />
        </linearGradient>
        """
        core_fill = "url(#c2_core_lt)"
        ring_stroke = "url(#c2_ring_lt)"
        node_fill = "#0284C7"
    else: # dark
        grad_def = """
        <linearGradient id="c2_core_dk" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#00F0FF" />
          <stop offset="50%" stop-color="#0070F3" />
          <stop offset="100%" stop-color="#6366F1" />
        </linearGradient>
        <linearGradient id="c2_ring_dk" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#00F0FF" />
          <stop offset="50%" stop-color="#A855F7" />
          <stop offset="100%" stop-color="#6B21A8" stop-opacity="0.3" />
        </linearGradient>
        <filter id="c2_glow" x="-25%" y="-25%" width="150%" height="150%">
          <feDropShadow dx="0" dy="2" stdDeviation="5" flood-color="#00F0FF" flood-opacity="0.4"/>
        </filter>
        """
        core_fill = "url(#c2_core_dk)"
        ring_stroke = "url(#c2_ring_dk)"
        node_fill = "#00F0FF"

    glow_attr = 'filter="url(#c2_glow)"' if mode == "dark" else ""

    svg = f"""<g id="symbol-concept-2" {glow_attr}>
      <defs>{grad_def}</defs>
      
      <!-- Inclined Orbital Acceleration Ring (-28 deg) -->
      <g transform="rotate(-28 100 100)">
        <ellipse cx="100" cy="100" rx="92" ry="32" fill="none" stroke="{ring_stroke}" stroke-width="4" stroke-dasharray="190 20 40 15" stroke-linecap="round" />
        <!-- Orbital Satellite Node -->
        <circle cx="192" cy="100" r="5.5" fill="{node_fill}" />
        <circle cx="192" cy="100" r="2.5" fill="#FFFFFF" />
      </g>

      <!-- Center Geometric 'G' Aperture Body -->
      <!-- Smooth circular arc carving inward to form the G crossbar -->
      <path d="M 148,68 
               C 134,44 112,34 88,38 
               C 54,44 32,74 32,108 
               C 32,144 58,172 98,172 
               C 138,172 166,144 166,108 
               L 166,98 
               L 98,98 
               L 98,122 
               L 138,122 
               C 134,136 118,150 96,150 
               C 72,150 56,132 56,108 
               C 56,84 72,62 96,58 
               C 114,56 130,66 140,80 
               Z" 
            fill="{core_fill}" />

      <!-- Forefront Orbital Arc crossing in front of the G -->
      <g transform="rotate(-28 100 100)">
        <path d="M 52,122 C 78,132 122,132 152,122" fill="none" stroke="{node_fill}" stroke-width="4.5" stroke-linecap="round" />
      </g>
    </g>"""
    return svg


# ==============================================================================
# CONCEPT 3: THE INFINITE GATEWAY (HEXAGONAL MÖBIUS G)
# ==============================================================================
# Geometry: An isometric continuous hexagonal prism ribbon folding inward to form
# an abstract 'G' with an open infinite central portal.

def get_concept_3_symbol(mode="dark", size=200):
    if mode == "mono_black":
        f1 = "#000000"
        f2 = "#333333"
        f3 = "#666666"
        grad_def = ""
    elif mode == "mono_white":
        f1 = "#FFFFFF"
        f2 = "#CCCCCC"
        f3 = "#999999"
        grad_def = ""
    elif mode == "light":
        grad_def = """
        <linearGradient id="c3_f1_lt" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#0284C7" />
          <stop offset="100%" stop-color="#0369A1" />
        </linearGradient>
        <linearGradient id="c3_f2_lt" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#4F46E5" />
          <stop offset="100%" stop-color="#4338CA" />
        </linearGradient>
        <linearGradient id="c3_f3_lt" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#9333EA" />
          <stop offset="100%" stop-color="#7E22CE" />
        </linearGradient>
        """
        f1 = "url(#c3_f1_lt)"
        f2 = "url(#c3_f2_lt)"
        f3 = "url(#c3_f3_lt)"
    else: # dark
        grad_def = """
        <linearGradient id="c3_f1_dk" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#00F0FF" />
          <stop offset="100%" stop-color="#0072FF" />
        </linearGradient>
        <linearGradient id="c3_f2_dk" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#3B82F6" />
          <stop offset="100%" stop-color="#6366F1" />
        </linearGradient>
        <linearGradient id="c3_f3_dk" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#C084FC" />
          <stop offset="100%" stop-color="#9333EA" />
        </linearGradient>
        <filter id="c3_glow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#00F0FF" flood-opacity="0.35"/>
        </filter>
        """
        f1 = "url(#c3_f1_dk)"
        f2 = "url(#c3_f2_dk)"
        f3 = "url(#c3_f3_dk)"

    glow_attr = 'filter="url(#c3_glow)"' if mode == "dark" else ""

    # Hexagonal isometric facets forming a continuous 3D loop G
    # Top Horizon Roof
    p_top = "M 100,24 L 170,64 L 138,82 L 100,60 L 62,82 L 30,64 Z"
    # Left Descending Pillar
    p_left = "M 30,64 L 62,82 L 62,142 L 30,160 Z"
    # Bottom Inward Sweeping Foundation & Crossbar
    p_core = """
    M 30,160 
    L 62,142 
    L 100,164 
    L 138,142 
    L 138,106 
    L 94,106 
    L 94,86 
    L 168,86 
    L 168,160 
    L 100,200 
    Z
    """

    svg = f"""<g id="symbol-concept-3" {glow_attr}>
      <defs>{grad_def}</defs>
      <!-- Facet 1: Top Canopy (Cyan Horizon) -->
      <path d="{p_top}" fill="{f1}" />
      <!-- Facet 2: Left Pillar (Cobalt Anchor) -->
      <path d="{p_left}" fill="{f2}" />
      <!-- Facet 3: Foundation & Core Crossbar (Electric Violet Gateway) -->
      <path d="{p_core}" fill="{f3}" />
    </g>"""
    return svg


# ==============================================================================
# SVG FULL DOCUMENT BUILDERS
# ==============================================================================

def build_horizontal_logo(symbol_svg, title_color, os_color, tagline_color, bar_color, bg_color=None, width=820, height=220):
    bg_rect = f'<rect width="{width}" height="{height}" rx="16" fill="{bg_color}" />' if bg_color else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  {bg_rect}
  <!-- Brand Symbol -->
  <g transform="translate(35, 10)">
    {symbol_svg}
  </g>
  <!-- Wordmark Section -->
  <g transform="translate(265, 30)">
    <!-- Main Title -->
    <text x="0" y="78" font-family="'Inter', 'Space Grotesk', -apple-system, sans-serif" font-weight="800" font-size="76" letter-spacing="6">
      <tspan fill="{title_color}">GIRI</tspan>
      <tspan dx="14" fill="{os_color}">OS</tspan>
    </text>
    <!-- Divider Bar -->
    <rect x="2" y="98" width="480" height="2.5" rx="1.2" fill="{bar_color}" />
    <!-- Tagline -->
    <text x="3" y="128" font-family="'Inter', 'Space Grotesk', -apple-system, sans-serif" font-weight="600" font-size="14" letter-spacing="6" fill="{tagline_color}">ONE SYSTEM. INFINITE POSSIBILITIES.</text>
  </g>
</svg>"""

def build_icon_svg(symbol_svg, bg_color=None, size=256):
    bg_rect = f'<rect width="{size}" height="{size}" rx="56" fill="{bg_color}" />' if bg_color else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="100%" height="100%">
  {bg_rect}
  <g transform="translate(28, 28)">
    {symbol_svg}
  </g>
</svg>"""

def main():
    concepts = [
        ("concept-1-genesis-g", get_concept_1_symbol, "Precision G"),
        ("concept-2-orbital-nexus", get_concept_2_symbol, "Orbital Nexus"),
        ("concept-3-infinite-gateway", get_concept_3_symbol, "Infinite Gateway"),
    ]

    for folder_name, symbol_func, concept_title in concepts:
        target_dir = os.path.join(PROPOSALS_DIR, folder_name)
        os.makedirs(target_dir, exist_ok=True)

        # 1. Dark Theme
        sym_dark = symbol_func("dark")
        dark_logo = build_horizontal_logo(sym_dark, title_color="#FFFFFF", os_color="#00F0FF", tagline_color="#94A3B8", bar_color="#00F0FF", bg_color="#070913")
        with open(os.path.join(target_dir, f"{folder_name}-dark.svg"), "w", encoding="utf-8") as f:
            f.write(dark_logo)

        # 2. Light Theme
        sym_light = symbol_func("light")
        light_logo = build_horizontal_logo(sym_light, title_color="#0F172A", os_color="#0066FF", tagline_color="#64748B", bar_color="#0066FF", bg_color="#FFFFFF")
        with open(os.path.join(target_dir, f"{folder_name}-light.svg"), "w", encoding="utf-8") as f:
            f.write(light_logo)

        # 3. Monochrome (Black on transparent, and White on black)
        sym_mono_black = symbol_func("mono_black")
        mono_black_logo = build_horizontal_logo(sym_mono_black, title_color="#000000", os_color="#000000", tagline_color="#333333", bar_color="#000000", bg_color=None)
        with open(os.path.join(target_dir, f"{folder_name}-mono.svg"), "w", encoding="utf-8") as f:
            f.write(mono_black_logo)

        # 4. Small Icon (App launcher / favicon / dock)
        icon_dark = build_icon_svg(sym_dark, bg_color="#0B0F19", size=256)
        with open(os.path.join(target_dir, f"{folder_name}-icon.svg"), "w", encoding="utf-8") as f:
            f.write(icon_dark)

        print(f"[+] Generated all assets for: {concept_title} -> {target_dir}")

if __name__ == "__main__":
    main()
