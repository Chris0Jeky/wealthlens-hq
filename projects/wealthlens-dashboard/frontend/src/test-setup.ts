/**
 * Vitest global setup — extends matchers with axe-core accessibility assertions.
 *
 * This adds `toHaveNoViolations()` to vitest's expect API, enabling
 * assertions like: expect(await axe(element)).toHaveNoViolations()
 */
import "vitest-axe/extend-expect";
