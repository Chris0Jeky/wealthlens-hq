import { watchEffect, type Ref } from 'vue'

const BASE_TITLE = 'WealthLens UK'

export function useDocumentTitle(title: Ref<string | undefined>): void {
  watchEffect(() => {
    document.title = title.value
      ? `${title.value} — ${BASE_TITLE}`
      : BASE_TITLE
  })
}
