/** Escape HTML special characters to prevent XSS in tooltip content. */
export function escapeHtml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/** Safely compute min/max from a number array without spreading (stack-safe). */
export function safeMinMax(arr: number[]): { min: number; max: number } {
  if (arr.length === 0) return { min: 0, max: 0 };
  let min = arr[0];
  let max = arr[0];
  for (let i = 1; i < arr.length; i++) {
    if (arr[i] < min) min = arr[i];
    if (arr[i] > max) max = arr[i];
  }
  return { min, max };
}
