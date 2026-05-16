<script setup lang="ts">
/**
 * AccessibleDataTable — A collapsible data table for screen reader access
 * to chart data. WCAG AA requires that charts have a text alternative;
 * this component provides one.
 *
 * Usage: place below any chart component and pass the same data rows.
 * Collapsed by default via <details>/<summary> to avoid visual clutter.
 */
import type { DatasetRow } from "@/stores/data";

const props = defineProps<{
  /** Array of data objects to display as table rows. */
  rows: DatasetRow[];
  /** Column keys to display (controls order and which fields are shown). */
  columns: string[];
  /** Accessible caption describing the table content for screen readers. */
  caption: string;
}>();

/**
 * Format a cell value for display.
 * - null/undefined → em-dash "—"
 * - numbers → locale-formatted (en-GB)
 * - strings → as-is
 */
function formatCell(value: string | number | null | undefined): string {
  if (value === null || value === undefined) {
    return "—"; // em-dash
  }
  if (typeof value === "number") {
    return value.toLocaleString("en-GB");
  }
  return String(value);
}
</script>

<template>
  <details class="mt-4">
    <summary
      class="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded px-2 py-1"
    >
      View data as table
    </summary>

    <div class="overflow-x-auto mt-2">
      <table
        role="table"
        class="min-w-full border-collapse border border-gray-300 text-sm"
      >
        <caption class="sr-only">
          {{ props.caption }}
        </caption>

        <thead>
          <tr class="bg-gray-100">
            <th
              v-for="col in props.columns"
              :key="col"
              scope="col"
              class="border border-gray-300 px-3 py-2 text-left font-semibold text-gray-800"
            >
              {{ col }}
            </th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="(row, idx) in props.rows"
            :key="idx"
            :class="idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'"
          >
            <td
              v-for="col in props.columns"
              :key="col"
              class="border border-gray-300 px-3 py-2 text-gray-700"
            >
              {{ formatCell(row[col]) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </details>
</template>
