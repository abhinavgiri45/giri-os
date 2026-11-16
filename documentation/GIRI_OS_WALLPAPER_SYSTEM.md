# Giri OS 0.1 Genesis — Official Wallpaper System & Design Specification

**Founder & Lead Architect:** Abhinav Giri  
**Tagline:** ONE SYSTEM. INFINITE POSSIBILITIES.  
**Operating System:** Giri OS 0.1 Genesis  
**Desktop Environment:** Giri Space  
**Base Distribution:** Debian 12 (Bookworm) amd64  
**Date:** November 16, 2026  
**Status:** Integrated & Verified

---

## 1. Executive Summary & Design Philosophy

The official Giri OS wallpaper collection has been completely redesigned to establish an original, premium, and visually distinctive desktop identity. Replacing generic procedural gradients, the new collection presents **12 cohesive 4K UHD (3840 × 2160) artworks** rendered in a refined palette of deep black, midnight blue, electric blue, violet, pearl white, and satin silver.

### Core Visual Principles
- **Atmospheric Depth & Material Realism:** Sculptural 3D obsidian, frosted glass, brushed titanium, and porcelain surfaces.
- **Icon-First Composition:** Thoughtfully balanced negative space on left and right flanks, allowing desktop icons and dock elements to remain legible.
- **Unified Identity:** Rather than disparate stock visuals, every wallpaper adheres to the Giri OS cyber-architectural philosophy.
- **Identical Composition for Light & Dark Defaults:** The official default wallpapers (`giri-os-default-light.png` and `giri-os-default-dark.png`) feature the exact same 3D spatial geometry, perspective planes, and logo proportions, varying only in materials, lighting, and color grading.

---

## 2. Complete Wallpaper Catalog (12 Official Artworks)

All wallpapers are rendered at **3840 × 2160 (16:9 native 4K UHD)** in lossless PNG, with accompanying **384 × 216** thumbnails for instant UI rendering.

| # | Filename | Display Name | Category | Paired Theme | 4K Dimensions | File Size | Description |
|---|:---|:---|:---|:---|:---|:---|:---|
| **01** | `giri-os-default-dark.png` | **Giri OS — Dark Edition** | Official Default | Dark (Default) | 3840 × 2160 | 3.98 MB | Deep black & midnight-blue brushed metals, electric-blue accent lines, and the official Giri OS logo with illuminated silver treatment. |
| **02** | `giri-os-default-light.png` | **Giri OS — Light Edition** | Official Default | Light | 3840 × 2160 | 1.30 MB | Pearl-white porcelain surfaces, satin silver geometric elements, subtle ice-blue ambient glow, and official logo in contrasting dark navy. |
| **03** | `giri-origin.png` | **Giri Origin** | Signature Collection | Dark / Modern | 3840 × 2160 | 5.39 MB | Signature artistic wallpaper featuring midnight-blue surfaces, subtle electric-blue illumination, and a central abstract geometric structure. |
| **04** | `infinite-flow.png` | **Infinite Flow** | Flowing Abstract | Dark / Modern | 3840 × 2160 | 4.75 MB | Flowing abstract ribbons of frosted glass and obsidian with electric-blue luminous accents against deep black. |
| **05** | `quantum-form.png` | **Quantum Form** | Geometric Architecture | Dark / Modern | 3840 × 2160 | 5.27 MB | Refined geometric structures of translucent glass illuminated with subtle violet and electric blue highlights. |
| **06** | `beyond-horizon.png` | **Beyond Horizon** | Cosmic Horizon | Dark / Midnight | 3840 × 2160 | 3.93 MB | Cinematic cosmic horizon with atmospheric sapphire rim lighting and calm deep navy space. |
| **07** | `midnight-architecture.png` | **Midnight Architecture** | Minimalist Architecture | Dark / Classic | 3840 × 2160 | 4.66 MB | Futuristic minimalist architecture featuring brushed titanium structures and subtle electric-blue accent lines. |
| **08** | `electric-geometry.png` | **Electric Geometry** | Geometric Abstract | Dark / Modern | 3840 × 2160 | 3.80 MB | Symmetrical multifaceted geometric forms constructed from polished obsidian and electric-blue light channels. |
| **09** | `silent-universe.png` | **Silent Universe** | Minimalist Space | Dark / Midnight | 3840 × 2160 | 3.41 MB | Minimalist cosmic environment with calm atmospheric depth and restrained luminous gradients. |
| **10** | `violet-dimension.png` | **Violet Dimension** | Cinematic 3D Abstract | Dark / Modern | 3840 × 2160 | 5.42 MB | Abstract cinematic composition featuring flowing translucent violet glass and amethyst crystal structures. |
| **11** | `aurora.png` | **Aurora** | Atmospheric Wave | Dark / Modern | 3840 × 2160 | 3.12 MB | Atmospheric light formations in electric blue, violet, and subtle cyan drifting across a midnight void. |
| **12** | `pure-minimal.png` | **Pure Minimal** | Ultra-Clean Minimalist | Dark / Classic | 3840 × 2160 | 2.88 MB | Solitary matte dark metal sculptural form under soft directional rim lighting with vast negative space. |

---

## 3. Official Default Wallpapers: Light & Dark Pair Architecture

In strict compliance with Giri OS brand identity rules:
1. **Mathematical Symmetry & Proportions:**
   - Both `giri-os-default-light.png` and `giri-os-default-dark.png` are built upon the exact same architectural wireframe.
   - The central emblem is the official 4-pane geometric window logo derived directly from [`branding/logo/giri-os-icon.svg`](file:///c:/Users/abhin/OneDrive/Desktop/giri-os/branding/logo/giri-os-icon.svg), rendered at `280 × 280` px with supersampled Lanczos anti-aliasing.
   - Logo coordinates: Centered at `X = 1780`, `Y = 777` on both Light and Dark editions.
   - Wordmark lockup: `GIRI OS` and `ONE SYSTEM. INFINITE POSSIBILITIES.` set in geometric sans-serif typography centered identically at `Y = 1081`.
2. **Material Differentiation:**
   - **Light Edition:** The background transforms into pearl-white (`#F8FAFC`) with soft diffused ambient shadows, satin silver curves, and subtle ice-blue rim illumination (`#38BDF8`). The logo and typography adopt a contrasting dark slate (`#0F172A`) and sapphire tone.
   - **Dark Edition:** The background is deep obsidian black (`#050811`) with brushed midnight-blue titanium geometry, electric-blue glowing conduits (`#00D2FF`), and luminous silver typography.

---

## 4. Desktop Integration & Automatic Theme Switching

The wallpaper system is deeply integrated into **Giri Space** (`desktop/giri-space/shell/giri_space.py`) and **Giri Control Center** (`desktop/giri-space/control-center/control_center.py`):

### 4.1. Automatic Theme Switching Engine
- **When Light Mode is Enabled:**
  If `auto_switch_theme` is active (default), the desktop automatically applies `giri-os-default-light.png` across all spaces live without requiring a restart or logout.
- **When Dark Mode is Enabled:**
  If `auto_switch_theme` is active, the desktop automatically applies `giri-os-default-dark.png`.
- **Manual Preference Protection:**
  When a user manually selects any artistic wallpaper (e.g. `Beyond Horizon` or `Aurora`), `user_manually_selected` is flagged as `True`, and `auto_switch_theme` is deactivated. This prevents subsequent theme changes from overwriting the user's explicit preference.
- **One-Click Restore Actions:**
  - `★ Official Dark Default`: Re-applies `giri-os-default-dark.png` and resets theme to dark.
  - `☀ Official Light Default`: Re-applies `giri-os-default-light.png` and resets theme to light.
  - `↺ Giri Origin`: Applies signature `giri-origin.png`.

### 4.2. Configuration Persistence
All wallpaper preferences persist across reboots in `system/etc/giri-wallpaper.json`:
```json
{
  "current_wallpaper": "branding/wallpapers/giri-os-default-dark.png",
  "current_name": "Giri OS — Dark Edition",
  "theme": "dark",
  "auto_switch_theme": true,
  "user_manually_selected": false,
  "mode": "Fill",
  "is_solid_color": false,
  "solid_color": "#050811",
  "per_space": {
    "1": "branding/wallpapers/giri-os-default-dark.png",
    "2": "branding/wallpapers/giri-origin.png",
    "3": "branding/wallpapers/infinite-flow.png",
    "4": "branding/wallpapers/quantum-form.png"
  }
}
```

---

## 5. Debian Live-Build & ISO Inclusion

All 12 wallpapers and metadata are staged automatically during the ISO build pipeline in [`scripts/build-iso.sh`](file:///c:/Users/abhin/OneDrive/Desktop/giri-os/scripts/build-iso.sh):
- Wallpapers staged to: `/usr/share/backgrounds/`
- Thumbnails staged to: `/usr/share/backgrounds/thumbnails/`
- Metadata staged to: `/usr/share/backgrounds/wallpaper-metadata.json` and `wallpapers.json`
- Default config staged to: `/etc/giri-wallpaper.json`

Total ISO storage footprint for the entire uncompressed 4K collection: **~47.9 MB** (under 18 MB compressed in SquashFS).

---

## 6. Verification & Automated Test Results

The test suite [`tests/test_giri_suite.py`](file:///c:/Users/abhin/OneDrive/Desktop/giri-os/tests/test_giri_suite.py) validates the wallpaper subsystem:

```
Ran 10 tests in 3.417s - OK
```

- **`test_07_wallpaper_collection`**: Verified that all 12 files exist, match exact `3840 × 2160` dimensions, have 16:9 ratio, valid PNG format, and corresponding `384 × 216` thumbnails.
- **`test_10_theme_wallpaper_switching`**: Verified that switching to Light Mode applies `giri-os-default-light.png`, switching to Dark Mode applies `giri-os-default-dark.png`, and state persists cleanly.
