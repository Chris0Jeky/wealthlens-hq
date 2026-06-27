declare module "vitest-axe" {
  export interface AxeNode {
    target: string[]
  }

  export interface AxeViolation {
    id: string
    impact: "minor" | "moderate" | "serious" | "critical" | null
    nodes: AxeNode[]
  }

  export interface AxeResults {
    passes: AxeViolation[]
    violations: AxeViolation[]
    incomplete: AxeViolation[]
  }

  export function axe(element: Element, options?: Record<string, unknown>): Promise<AxeResults>
}

declare module "vitest-axe/extend-expect"
