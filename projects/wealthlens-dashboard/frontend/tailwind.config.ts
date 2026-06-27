/**
 * WealthLens UK — Tailwind CSS Configuration
 *
 * This project uses Tailwind CSS v4 with the @tailwindcss/vite plugin.
 * In v4, theme customisation is primarily done via @theme directives in CSS
 * (see src/style.css). This config file serves as a reference mapping of the
 * WealthLens design tokens for tooling that reads tailwind.config.ts
 * (e.g. editor plugins, Prettier plugin).
 *
 * The canonical design tokens live in:
 *   - docs/redesign/tokens.css          (source of truth)
 *   - src/assets/tokens.css             (CSS custom properties, themes)
 *   - src/style.css                     (@theme block for Tailwind utilities)
 */

import type { Config } from "tailwindcss"

export default {
  content: ["./index.html", "./src/**/*.{vue,ts,tsx,js,jsx}"],
  theme: {
    extend: {
      /* Colour tokens — use as bg-wl-paper, text-wl-ink, etc.
         These reference CSS custom properties so theme switching (via
         data-theme attribute) works automatically. */
      colors: {
        wl: {
          paper: "var(--wl-paper)",
          "paper-tint": "var(--wl-paper-tint)",
          "paper-deep": "var(--wl-paper-deep)",
          ink: "var(--wl-ink)",
          "ink-body": "var(--wl-ink-body)",
          "ink-muted": "var(--wl-ink-muted)",
          "ink-faint": "var(--wl-ink-faint)",
          rule: "var(--wl-rule)",
          "rule-strong": "var(--wl-rule-strong)",
          bg: "var(--wl-bg)",
          "bg-muted": "var(--wl-bg-muted)",
          "bg-section": "var(--wl-bg-section)",
          card: "var(--wl-card)",
          red: "var(--wl-red)",
          "red-deep": "var(--wl-red-deep)",
          "red-soft": "var(--wl-red-soft)",
          gold: "var(--wl-gold)",
          "gold-soft": "var(--wl-gold-soft)",
          teal: "var(--wl-teal)",
        },
      },
      /* Font families — use as font-wl-serif, font-wl-sans, font-wl-mono */
      fontFamily: {
        "wl-serif": ["Newsreader", "Source Serif Pro", "Georgia", "Times New Roman", "serif"],
        "wl-sans": [
          "IBM Plex Sans",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "system-ui",
          "sans-serif",
        ],
        "wl-mono": [
          "IBM Plex Mono",
          "JetBrains Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Consolas",
          "monospace",
        ],
      },
      /* Border radius — broadsheet: crisp, low radii */
      borderRadius: {
        wl: "3px",
        "wl-sm": "2px",
        "wl-lg": "4px",
      },
      /* Shadows — subtle, print-like */
      boxShadow: {
        "wl-sm": "0 1px 0 rgba(17,17,17,0.06)",
        wl: "0 1px 2px rgba(17,17,17,0.08)",
        "wl-lg": "0 8px 24px rgba(17,17,17,0.10), 0 2px 6px rgba(17,17,17,0.06)",
      },
      /* Container max-width */
      maxWidth: {
        wl: "1280px",
      },
    },
  },
  plugins: [],
} satisfies Config
