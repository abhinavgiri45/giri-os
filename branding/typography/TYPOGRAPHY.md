# Giri OS — Official Typography Specification

The Giri OS brand typography is engineered for clarity, technical precision, and modern legibility across displays ranging from 1024×768 legacy CRT/LCD monitors to 4K high-DPI panels.

---

## 1. Typeface Hierarchy

### A. Primary Brand Display & Wordmark
- **Font Family:** Modern Geometric Sans-Serif (Inter, Space Grotesk, or DejaVu Sans Bold)
- **Weight:** Bold / Extra-Bold (700 / 800)
- **Case:** Strict Uppercase (`GIRI OS`)
- **Letterspacing (Tracking):** `+0.08em` to `+0.12em` (wide, structured stance)
- **Coloration:**
  - Dark Mode: `#FFFFFF` with optional `#00D2FF` electric accent on `OS`
  - Light Mode: `#0F172A` (Slate 900)
  - Monochrome: Single solid tone

### B. Tagline & Subtitles
- **Text:** `ONE SYSTEM. INFINITE POSSIBILITIES.`
- **Weight:** Semi-Bold (600)
- **Case:** Uppercase
- **Letterspacing:** `+0.18em` (generous tracking for balance beneath the wordmark)
- **Coloration:** `#64748B` (Light mode) / `#94A3B8` (Dark mode)

### C. Desktop User Interface (Giri Space)
- **Primary Interface Font:** `Inter Regular / Medium / SemiBold` (Fallback: `DejaVu Sans`)
- **UI Sizes:**
  - Window Titles: 11pt Bold
  - Top Bar & Menu Headers: 10pt Semi-Bold
  - Body & Settings: 10pt Regular
  - Dock Tooltips & Badges: 8pt Bold
  - Monospace / Terminal: `JetBrains Mono` / `DejaVu Sans Mono` 10pt

---

## 2. Web & System Font Fallbacks

```css
/* Giri OS UI Font Stack */
--giri-font-sans: "Inter", "DejaVu Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
--giri-font-mono: "JetBrains Mono", "DejaVu Sans Mono", "Fira Code", monospace;
```
