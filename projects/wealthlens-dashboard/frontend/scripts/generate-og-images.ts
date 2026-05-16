/**
 * OG Image Generator for WealthLens UK
 *
 * Generates 1200x630 PNG Open Graph images for each chart page using
 * satori (HTML-to-SVG) and @resvg/resvg-js (SVG-to-PNG).
 *
 * Design: Broadsheet newspaper style with:
 * - Paper texture background (#faf9f6)
 * - Serif headline
 * - Red accent rule (#c00)
 * - Source citation and access date
 * - WealthLens UK branding footer
 *
 * Usage: npx tsx scripts/generate-og-images.ts
 *
 * Output: public/og/<chart-slug>.png + public/og/og-default.png
 */

import satori from "satori";
import { Resvg } from "@resvg/resvg-js";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "fs";
import { resolve, join, dirname } from "path";
import { fileURLToPath } from "url";
import { OG_METADATA, type OgMetadataEntry } from "../src/constants/ogMetadata";
import { VALID_CHART_NAMES } from "../src/constants/charts";

// --- Configuration ---

type SatoriNode = Parameters<typeof satori>[0];

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const WIDTH = 1200;
const HEIGHT = 630;
const OUTPUT_DIR = resolve(__dirname, "../public/og");
const FONTS_DIR = resolve(__dirname, "fonts");

// Colors matching broadsheet newspaper design
const COLORS = {
  background: "#faf9f6",
  headline: "#1a1a1a",
  subtitle: "#333333",
  source: "#666666",
  accent: "#cc0000",
  footer: "#555555",
  footerBg: "#f0eeeb",
};

// --- Font loading ---

/**
 * Load font files for satori. We bundle two weights of a serif and a sans font.
 * Falls back to fetching from Google Fonts if local fonts are not available.
 */
async function loadFonts(): Promise<
  Array<{ name: string; data: ArrayBuffer; weight: number; style: string }>
> {
  // Try to load local font files first
  const fonts: Array<{
    name: string;
    data: ArrayBuffer;
    weight: number;
    style: string;
  }> = [];

  // We'll use system-available fonts bundled with the script
  // For the build script, we download and cache fonts on first run
  const fontCacheDir = FONTS_DIR;
  if (!existsSync(fontCacheDir)) {
    mkdirSync(fontCacheDir, { recursive: true });
  }

  // Use Inter for sans-serif (subtitle, source, footer)
  const interRegularPath = join(fontCacheDir, "Inter-Regular.ttf");
  const interBoldPath = join(fontCacheDir, "Inter-Bold.ttf");

  // Use Playfair Display for serif headlines
  const playfairBoldPath = join(fontCacheDir, "PlayfairDisplay-Bold.ttf");

  // Download fonts if not cached
  if (
    !existsSync(interRegularPath) ||
    !existsSync(interBoldPath) ||
    !existsSync(playfairBoldPath)
  ) {
    console.log("Downloading fonts (first run only)...");
    await downloadFont(
      "https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-400-normal.ttf",
      interRegularPath
    );
    await downloadFont(
      "https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-700-normal.ttf",
      interBoldPath
    );
    await downloadFont(
      "https://cdn.jsdelivr.net/fontsource/fonts/playfair-display@latest/latin-700-normal.ttf",
      playfairBoldPath
    );
    console.log("Fonts cached successfully.");
  }

  fonts.push({
    name: "Inter",
    data: readFileSync(interRegularPath).buffer as ArrayBuffer,
    weight: 400,
    style: "normal",
  });
  fonts.push({
    name: "Inter",
    data: readFileSync(interBoldPath).buffer as ArrayBuffer,
    weight: 700,
    style: "normal",
  });
  fonts.push({
    name: "Playfair Display",
    data: readFileSync(playfairBoldPath).buffer as ArrayBuffer,
    weight: 700,
    style: "normal",
  });

  return fonts;
}

async function downloadFont(url: string, dest: string): Promise<void> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to download font from ${url}: ${response.statusText}`);
  }
  const buffer = Buffer.from(await response.arrayBuffer());
  writeFileSync(dest, buffer);
}

// --- Image generation ---

/**
 * Build the satori-compatible JSX structure for a chart OG image.
 * Satori uses a subset of CSS Flexbox for layout.
 */
function buildChartLayout(metadata: OgMetadataEntry): SatoriNode {
  return {
    type: "div",
    props: {
      style: {
        display: "flex",
        flexDirection: "column",
        width: "100%",
        height: "100%",
        backgroundColor: COLORS.background,
        padding: "0",
      },
      children: [
        // Main content area
        {
          type: "div",
          props: {
            style: {
              display: "flex",
              flexDirection: "column",
              flex: "1",
              padding: "60px 70px 30px 70px",
              justifyContent: "center",
            },
            children: [
              // Red accent line at top
              {
                type: "div",
                props: {
                  style: {
                    width: "80px",
                    height: "4px",
                    backgroundColor: COLORS.accent,
                    marginBottom: "30px",
                  },
                },
              },
              // Headline
              {
                type: "div",
                props: {
                  style: {
                    fontFamily: "Playfair Display",
                    fontSize: "52px",
                    fontWeight: 700,
                    color: COLORS.headline,
                    lineHeight: "1.2",
                    marginBottom: "20px",
                  },
                  children: metadata.title,
                },
              },
              // Subtitle / key stat
              {
                type: "div",
                props: {
                  style: {
                    fontFamily: "Inter",
                    fontSize: "26px",
                    fontWeight: 400,
                    color: COLORS.subtitle,
                    lineHeight: "1.4",
                    marginBottom: "24px",
                  },
                  children: metadata.subtitle,
                },
              },
              // Source citation
              {
                type: "div",
                props: {
                  style: {
                    fontFamily: "Inter",
                    fontSize: "16px",
                    fontWeight: 400,
                    color: COLORS.source,
                    lineHeight: "1.4",
                  },
                  children: `Source: ${metadata.source} (accessed ${metadata.sourceAccessDate})`,
                },
              },
            ],
          },
        },
        // Footer strip
        {
          type: "div",
          props: {
            style: {
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              backgroundColor: COLORS.footerBg,
              padding: "20px 70px",
              borderTop: `1px solid #ddd`,
            },
            children: [
              // Brand name
              {
                type: "div",
                props: {
                  style: {
                    fontFamily: "Inter",
                    fontSize: "18px",
                    fontWeight: 700,
                    color: COLORS.footer,
                  },
                  children: "WealthLens UK",
                },
              },
              // Tagline
              {
                type: "div",
                props: {
                  style: {
                    fontFamily: "Inter",
                    fontSize: "16px",
                    fontWeight: 400,
                    color: COLORS.footer,
                  },
                  children: "wealthlens.uk · Open-source · Source-backed data",
                },
              },
            ],
          },
        },
      ],
    },
  } as SatoriNode;
}

/**
 * Build layout for the default OG image (non-chart pages).
 */
function buildDefaultLayout(): SatoriNode {
  return {
    type: "div",
    props: {
      style: {
        display: "flex",
        flexDirection: "column",
        width: "100%",
        height: "100%",
        backgroundColor: COLORS.background,
        padding: "0",
      },
      children: [
        // Main content area
        {
          type: "div",
          props: {
            style: {
              display: "flex",
              flexDirection: "column",
              flex: "1",
              padding: "60px 70px 30px 70px",
              justifyContent: "center",
              alignItems: "center",
            },
            children: [
              // Red accent line
              {
                type: "div",
                props: {
                  style: {
                    width: "80px",
                    height: "4px",
                    backgroundColor: COLORS.accent,
                    marginBottom: "40px",
                  },
                },
              },
              // Brand name large
              {
                type: "div",
                props: {
                  style: {
                    fontFamily: "Playfair Display",
                    fontSize: "64px",
                    fontWeight: 700,
                    color: COLORS.headline,
                    lineHeight: "1.2",
                    marginBottom: "24px",
                    textAlign: "center",
                  },
                  children: "WealthLens UK",
                },
              },
              // Mission statement
              {
                type: "div",
                props: {
                  style: {
                    fontFamily: "Inter",
                    fontSize: "28px",
                    fontWeight: 400,
                    color: COLORS.subtitle,
                    lineHeight: "1.5",
                    textAlign: "center",
                    maxWidth: "800px",
                  },
                  children:
                    "Making UK wealth inequality data accessible, interactive, and impossible to ignore.",
                },
              },
            ],
          },
        },
        // Footer strip
        {
          type: "div",
          props: {
            style: {
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: COLORS.footerBg,
              padding: "20px 70px",
              borderTop: `1px solid #ddd`,
            },
            children: [
              {
                type: "div",
                props: {
                  style: {
                    fontFamily: "Inter",
                    fontSize: "18px",
                    fontWeight: 400,
                    color: COLORS.footer,
                  },
                  children: "wealthlens.uk · Open-source · Source-backed data",
                },
              },
            ],
          },
        },
      ],
    },
  } as SatoriNode;
}

/**
 * Render a satori layout to a PNG buffer.
 */
async function renderToPng(
  layout: SatoriNode,
  fonts: Awaited<ReturnType<typeof loadFonts>>
): Promise<Buffer> {
  const svg = await satori(layout, {
    width: WIDTH,
    height: HEIGHT,
    fonts: fonts.map((f) => ({
      name: f.name,
      data: f.data,
      weight: f.weight as 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900,
      style: f.style as "normal" | "italic",
    })),
  });

  const resvg = new Resvg(svg, {
    fitTo: { mode: "width", value: WIDTH },
  });
  const pngData = resvg.render();
  return Buffer.from(pngData.asPng());
}

// --- Main ---

async function main() {
  console.log("=== WealthLens OG Image Generator ===\n");

  // Ensure output directory exists
  if (!existsSync(OUTPUT_DIR)) {
    mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // Load fonts
  console.log("Loading fonts...");
  const fonts = await loadFonts();
  console.log("Fonts loaded.\n");

  let generated = 0;

  // Generate images for each chart
  for (const chartName of VALID_CHART_NAMES) {
    const metadata = OG_METADATA[chartName];
    if (!metadata) {
      console.warn(`WARNING: No OG metadata for chart "${chartName}" - skipping`);
      continue;
    }

    const layout = buildChartLayout(metadata);
    const png = await renderToPng(layout, fonts);
    const outputPath = join(OUTPUT_DIR, `${chartName}.png`);
    writeFileSync(outputPath, png);

    const sizeKb = (png.length / 1024).toFixed(1);
    console.log(`  Generated: ${chartName}.png (${sizeKb} KB)`);
    generated++;
  }

  // Generate default OG image
  const defaultLayout = buildDefaultLayout();
  const defaultPng = await renderToPng(defaultLayout, fonts);
  const defaultOutputPath = join(OUTPUT_DIR, "og-default.png");
  writeFileSync(defaultOutputPath, defaultPng);

  const defaultSizeKb = (defaultPng.length / 1024).toFixed(1);
  console.log(`  Generated: og-default.png (${defaultSizeKb} KB)`);
  generated++;

  console.log(`\nDone! Generated ${generated} OG images in ${OUTPUT_DIR}`);
}

main().catch((error) => {
  console.error("Error generating OG images:", error);
  process.exit(1);
});
