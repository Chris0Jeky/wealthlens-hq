/**
 * Interactive tools and related help pages shown on the home page and /tools.
 * Keep the route, title, and short description together so navigation surfaces
 * cannot drift apart as the tool set changes.
 */
export interface ToolDefinition {
  to: string
  name: string
  blurb: string
}

export const TOOLS: readonly ToolDefinition[] = [
  {
    to: "/tools/wealth-scale",
    name: "The wealth scale",
    blurb: "1 pixel = £1,000. Scroll UK wealth drawn to scale.",
  },
  {
    to: "/tools/wealth-calculator",
    name: "Where do you fit?",
    blurb: "Enter your household wealth, see your place in the distribution.",
  },
  {
    to: "/tools/tax-calculator",
    name: "Your real tax rate",
    blurb: "How much of your income actually goes in tax.",
  },
  {
    to: "/tools/wealth-tax-simulator",
    name: "Wealth tax simulator",
    blurb: "Set thresholds and rates; see what a wealth tax would raise.",
  },
  {
    to: "/faq",
    name: "FAQ & glossary",
    blurb: "The questions everyone asks, and the terms the charts use.",
  },
] as const
