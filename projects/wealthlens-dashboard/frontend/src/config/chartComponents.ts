/**
 * Chart component loaders, keyed by routed chart slug.
 *
 * One entry per VALID_CHART_NAMES member (guard-tested). The embed route
 * builds its async component from this map; ChartView still declares its own
 * async components (predates this map — fold it in when that file is next
 * touched, so the two cannot drift).
 */
import type { Component } from "vue"

export const CHART_COMPONENT_LOADERS: Record<string, () => Promise<{ default: Component }>> = {
  "wealth-shares": () => import("@/components/WealthSharesChart.vue"),
  "housing-affordability": () => import("@/components/HousingAffordabilityChart.vue"),
  "wealth-by-decile": () => import("@/components/WealthByDecileChart.vue"),
  "cgt-concentration": () => import("@/components/CgtConcentrationChart.vue"),
  "wage-stagnation": () => import("@/components/WageStagChart.vue"),
  "inheritance-tax": () => import("@/components/InheritanceTaxChart.vue"),
  "productivity-pay": () => import("@/components/ProductivityPayChart.vue"),
  "gdhi-by-region": () => import("@/components/GdhiByRegionChart.vue"),
  "tax-composition": () => import("@/components/TaxCompositionChart.vue"),
  "boe-rates": () => import("@/components/BoeRatesChart.vue"),
  "child-poverty": () => import("@/components/ChildPovertyChart.vue"),
  "generational-wealth": () => import("@/components/GenerationalWealthChart.vue"),
}
