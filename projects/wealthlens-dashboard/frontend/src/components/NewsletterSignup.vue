<script setup lang="ts">
import { ref, computed } from 'vue'

type FormState = 'idle' | 'submitting' | 'success' | 'error'

const email = ref('')
const state = ref<FormState>('idle')
const errorMessage = ref('')

const newsletterId = import.meta.env.VITE_BUTTONDOWN_NEWSLETTER_ID || 'wealthlens'
const apiUrl = import.meta.env.VITE_BUTTONDOWN_API_URL
  || `https://buttondown.email/api/emails/embed-subscribe/${newsletterId}`

const isValidEmail = computed(() => {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return pattern.test(email.value)
})

const isDisabled = computed(() => state.value === 'submitting')

async function handleSubmit() {
  if (!isValidEmail.value || isDisabled.value) return

  state.value = 'submitting'
  errorMessage.value = ''

  try {
    const body = new FormData()
    body.append('email', email.value)

    const response = await fetch(apiUrl, {
      method: 'POST',
      body,
    })

    if (!response.ok) {
      throw new Error(`Subscription failed (${response.status})`)
    }

    state.value = 'success'
    email.value = ''
  } catch (err) {
    state.value = 'error'
    errorMessage.value =
      err instanceof Error ? err.message : 'Something went wrong. Please try again.'
  }
}
</script>

<template>
  <section class="newsletter" aria-labelledby="newsletter-heading">
    <h3 id="newsletter-heading" class="newsletter__title">Stay informed</h3>
    <p class="newsletter__subtitle">
      Monthly updates on UK wealth data — no spam, unsubscribe anytime.
    </p>

    <form
      v-if="state !== 'success'"
      class="newsletter__form"
      @submit.prevent="handleSubmit"
      novalidate
    >
      <label for="newsletter-email" class="sr-only">Email address</label>
      <input
        id="newsletter-email"
        v-model="email"
        type="email"
        inputmode="email"
        autocomplete="email"
        placeholder="you@example.com"
        required
        pattern="[^\s@]+@[^\s@]+\.[^\s@]+"
        class="newsletter__input"
        :disabled="isDisabled"
        aria-describedby="newsletter-status"
      />
      <button
        type="submit"
        class="newsletter__btn wl-btn"
        :disabled="isDisabled || !isValidEmail"
        :aria-busy="state === 'submitting'"
      >
        <span v-if="state === 'submitting'" class="newsletter__spinner" aria-hidden="true" />
        {{ state === 'submitting' ? 'Subscribing...' : 'Subscribe' }}
      </button>
    </form>

    <div
      id="newsletter-status"
      class="newsletter__status"
      aria-live="polite"
      aria-atomic="true"
    >
      <p v-if="state === 'success'" class="newsletter__success">
        You're subscribed!
      </p>
      <p v-if="state === 'error'" class="newsletter__error">
        {{ errorMessage }}
      </p>
    </div>
  </section>
</template>

<style scoped>
.newsletter {
  max-width: 420px;
}

.newsletter__title {
  font-family: var(--wl-serif);
  font-size: 20px;
  font-weight: 700;
  color: var(--wl-ink);
  margin: 0 0 6px;
}

.newsletter__subtitle {
  font-size: 13px;
  color: var(--wl-ink-muted);
  margin: 0 0 16px;
  line-height: 1.5;
}

.newsletter__form {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.newsletter__input {
  flex: 1 1 200px;
  min-width: 0;
  padding: 10px 14px;
  border: 1px solid var(--wl-rule-strong);
  border-radius: var(--wl-radius);
  background: var(--wl-card);
  color: var(--wl-ink-body);
  font-size: 14px;
  transition: border-color 0.15s ease;
}

.newsletter__input::placeholder {
  color: var(--wl-ink-muted);
}

.newsletter__input:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
  border-color: var(--wl-red);
}

.newsletter__input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.newsletter__btn {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border: none;
  border-radius: var(--wl-radius);
  background: var(--wl-red);
  color: var(--wl-paper);
  font-family: var(--wl-mono);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: opacity 0.15s ease, background-color 0.15s ease;
}

.newsletter__btn:hover:not(:disabled) {
  opacity: 0.88;
}

.newsletter__btn:focus-visible {
  outline: 2px solid var(--wl-red);
  outline-offset: 2px;
}

.newsletter__btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.newsletter__spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid var(--wl-paper);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.newsletter__status {
  margin-top: 10px;
  min-height: 24px;
}

.newsletter__success {
  font-size: 14px;
  color: #16a34a;
  margin: 0;
  font-weight: 500;
}

.newsletter__error {
  font-size: 14px;
  color: var(--wl-red);
  margin: 0;
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

@media (max-width: 480px) {
  .newsletter__form {
    flex-direction: column;
  }

  .newsletter__btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
