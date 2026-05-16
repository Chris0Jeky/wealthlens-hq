<script setup lang="ts">
/**
 * ExportButton — Dropdown button for exporting charts as PNG or SVG.
 *
 * Renders a ghost button that toggles a dropdown menu with export format
 * options. Emits 'export' with the chosen format ('png' | 'svg').
 *
 * Accessibility:
 * - aria-haspopup and aria-expanded on trigger
 * - role="menu" / role="menuitem" on dropdown
 * - Escape closes the menu and returns focus to trigger
 * - Click outside closes the menu
 * - Focus trap within menu items using arrow keys
 *
 * @example
 * <ExportButton @export="handleExport" />
 */
import { ref, nextTick, onMounted, onUnmounted } from 'vue'

const emit = defineEmits<{
  (e: 'export', format: 'png' | 'svg'): void
}>()

const isOpen = ref(false)
const triggerRef = ref<HTMLButtonElement | null>(null)
const menuRef = ref<HTMLUListElement | null>(null)
const containerRef = ref<HTMLDivElement | null>(null)

function toggleMenu() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    nextTick(() => {
      // Focus the first menu item when opening
      const firstItem = menuRef.value?.querySelector<HTMLButtonElement>('[role="menuitem"]')
      firstItem?.focus()
    })
  }
}

function closeMenu() {
  isOpen.value = false
  triggerRef.value?.focus()
}

function selectFormat(format: 'png' | 'svg') {
  emit('export', format)
  closeMenu()
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    event.preventDefault()
    closeMenu()
    return
  }

  if (!isOpen.value) return

  const items = menuRef.value?.querySelectorAll<HTMLButtonElement>('[role="menuitem"]')
  if (!items || items.length === 0) return

  const currentIndex = Array.from(items).findIndex((el) => el === document.activeElement)

  switch (event.key) {
    case 'ArrowDown': {
      event.preventDefault()
      const next = (currentIndex + 1) % items.length
      items[next]?.focus()
      break
    }
    case 'ArrowUp': {
      event.preventDefault()
      const prev = (currentIndex - 1 + items.length) % items.length
      items[prev]?.focus()
      break
    }
  }
}

/** Close menu when clicking outside the container. */
function onClickOutside(event: Event) {
  if (!containerRef.value) return
  if (!containerRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('pointerdown', onClickOutside, true)
})

onUnmounted(() => {
  document.removeEventListener('pointerdown', onClickOutside, true)
})
</script>

<template>
  <div ref="containerRef" class="export-btn" @keydown="onKeydown">
    <button
      ref="triggerRef"
      class="wl-btn wl-btn--ghost wl-btn--sm"
      aria-haspopup="true"
      :aria-expanded="isOpen"
      @click="toggleMenu"
    >
      <svg
        class="export-btn__icon"
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="7 10 12 15 17 10" />
        <line x1="12" y1="15" x2="12" y2="3" />
      </svg>
      Export
    </button>
    <ul
      v-if="isOpen"
      ref="menuRef"
      class="export-btn__menu"
      role="menu"
    >
      <li role="none">
        <button role="menuitem" @click="selectFormat('png')">
          Download PNG
        </button>
      </li>
      <li role="none">
        <button role="menuitem" @click="selectFormat('svg')">
          Download SVG
        </button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.export-btn {
  position: relative;
  display: inline-block;
}

.wl-btn {
  font-family: var(--wl-mono, monospace);
  font-size: 11px;
  letter-spacing: 0.04em;
  cursor: pointer;
  border: 1px solid var(--wl-ink, #111);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background 0.15s ease, color 0.15s ease;
}

.wl-btn--ghost {
  background: transparent;
  color: var(--wl-ink, #111);
}
.wl-btn--ghost:hover {
  background: var(--wl-ink, #111);
  color: var(--wl-paper, #fff);
}

.wl-btn--sm {
  padding: 6px 12px;
}

.wl-btn:focus-visible {
  outline: 2px solid var(--wl-red, #dc2626);
  outline-offset: 2px;
}

.export-btn__icon {
  flex-shrink: 0;
}

.export-btn__menu {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  list-style: none;
  margin: 0;
  padding: 4px 0;
  background: var(--wl-card, #fff);
  border: 1px solid var(--wl-ink, #111);
  box-shadow: var(--wl-shadow-sm, 0 2px 8px rgba(0, 0, 0, 0.1));
  border-radius: var(--wl-radius, 2px);
  z-index: 50;
  min-width: 160px;
}

.export-btn__menu button {
  display: block;
  width: 100%;
  text-align: left;
  padding: 8px 16px;
  border: none;
  background: transparent;
  font-family: var(--wl-mono, monospace);
  font-size: 12px;
  color: var(--wl-ink, #111);
  cursor: pointer;
  white-space: nowrap;
}

.export-btn__menu button:hover,
.export-btn__menu button:focus {
  background: var(--wl-bg-muted, #f5f5f5);
  color: var(--wl-red, #dc2626);
  outline: none;
}

.export-btn__menu button:focus-visible {
  outline: 2px solid var(--wl-red, #dc2626);
  outline-offset: -2px;
}

/* Responsive: on small screens, keep button compact */
@media (max-width: 480px) {
  .wl-btn--sm {
    padding: 6px 8px;
    font-size: 0;
  }
  .export-btn__icon {
    width: 16px;
    height: 16px;
  }
  .export-btn__menu {
    right: auto;
    left: 0;
  }
}
</style>
