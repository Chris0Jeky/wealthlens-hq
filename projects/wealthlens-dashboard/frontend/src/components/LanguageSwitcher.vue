<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

/**
 * Available languages for the dashboard.
 * Currently English only — Welsh and Scots Gaelic planned for future.
 */
const languages = [
  { code: 'en', label: 'English' },
  // { code: 'cy', label: 'Cymraeg' },   // Welsh — future
  // { code: 'gd', label: 'Gàidhlig' },  // Scots Gaelic — future
] as const

function setLocale(code: string) {
  locale.value = code
}
</script>

<template>
  <div class="lang-switcher">
    <label for="lang-select" class="sr-only">Select language</label>
    <select
      id="lang-select"
      :value="locale"
      class="lang-select"
      @change="setLocale(($event.target as HTMLSelectElement).value)"
    >
      <option
        v-for="lang in languages"
        :key="lang.code"
        :value="lang.code"
      >
        {{ lang.label }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.lang-switcher {
  display: inline-flex;
  align-items: center;
}

.lang-select {
  font-family: var(--wl-mono, monospace);
  font-size: 12px;
  padding: 4px 8px;
  border: 1px solid var(--wl-rule, #ccc);
  border-radius: var(--wl-radius, 4px);
  background: var(--wl-bg, #fff);
  color: var(--wl-ink, #111);
  cursor: pointer;
}

.lang-select:focus-visible {
  outline: 2px solid var(--wl-red, #c00);
  outline-offset: 2px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
