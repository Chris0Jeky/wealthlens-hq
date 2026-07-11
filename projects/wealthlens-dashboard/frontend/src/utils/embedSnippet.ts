/**
 * Copy-paste embed snippet for the chrome-free /embed/{slug} route (RFC-001f).
 *
 * The iframe points at the embed shell (chart + source line + backlink only),
 * NOT the full article page — embedding the article iframed the whole site
 * chrome (the RFC's "fake embed" problem). The companion script listens for
 * the shell's `wealthlens-embed` height messages (see EmbedChartView) and
 * auto-sizes the iframe, so embedded charts never scroll internally.
 *
 * Sandbox: `allow-scripts` is required for the chart itself; `allow-popups`
 * lets the shell's backlink open the full article. No `allow-same-origin`:
 * the embed carries no cookies, storage, or tracking (the no-cookies pledge).
 */

export const EMBED_MESSAGE_SOURCE = "wealthlens-embed"

export function embedUrl(baseUrl: string, chartName: string): string {
  return `${baseUrl.replace(/\/$/, "")}/embed/${chartName}`
}

export function buildEmbedSnippet(
  baseUrl: string,
  chartName: string,
  chartTitle: string,
  width: string = "100%",
): string {
  const src = embedUrl(baseUrl, chartName)
  const iframe = `<iframe src="${src}" width="${width}" height="560" style="border:0" loading="lazy" sandbox="allow-scripts allow-popups" title="${chartTitle} — WealthLens UK"></iframe>`
  const resizer =
    `<script>window.addEventListener("message",function(e){` +
    `var d=e.data;if(!d||d.source!=="${EMBED_MESSAGE_SOURCE}"||d.chart!=="${chartName}")return;` +
    `var f=document.querySelector('iframe[src="${src}"]');` +
    `if(f&&typeof d.height==="number"&&d.height>0)f.style.height=Math.ceil(d.height)+"px"});` +
    `</${"script"}>`
  return `${iframe}\n${resizer}`
}
