import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FreshnessIndicator from '@/components/FreshnessIndicator.vue'
import type { DatasetFreshnessEntry } from '@/types/api'

function factory(freshness: DatasetFreshnessEntry) {
  return mount(FreshnessIndicator, { props: { freshness } })
}

describe('FreshnessIndicator', () => {
  describe('dot colour', () => {
    it('shows green dot for fresh status', () => {
      const wrapper = factory({
        last_updated: '2026-05-15T10:00:00+00:00',
        age_hours: 24,
        status: 'fresh',
      })
      const dot = wrapper.find('[data-testid="freshness-dot"]')
      expect(dot.classes()).toContain('bg-green-500')
    })

    it('shows yellow dot for stale status', () => {
      const wrapper = factory({
        last_updated: '2026-05-01T10:00:00+00:00',
        age_hours: 360,
        status: 'stale',
      })
      const dot = wrapper.find('[data-testid="freshness-dot"]')
      expect(dot.classes()).toContain('bg-yellow-500')
    })

    it('shows red dot for expired status', () => {
      const wrapper = factory({
        last_updated: '2026-03-01T10:00:00+00:00',
        age_hours: 1800,
        status: 'expired',
      })
      const dot = wrapper.find('[data-testid="freshness-dot"]')
      expect(dot.classes()).toContain('bg-red-500')
    })

    it('shows gray dot for unknown status', () => {
      const wrapper = factory({
        last_updated: null,
        age_hours: null,
        status: 'unknown',
      })
      const dot = wrapper.find('[data-testid="freshness-dot"]')
      expect(dot.classes()).toContain('bg-gray-400')
    })
  })

  describe('text label', () => {
    it('displays "Fresh" for fresh status', () => {
      const wrapper = factory({
        last_updated: '2026-05-15T10:00:00+00:00',
        age_hours: 24,
        status: 'fresh',
      })
      const label = wrapper.find('[data-testid="freshness-label"]')
      expect(label.text()).toBe('Fresh')
    })

    it('displays "Stale" for stale status', () => {
      const wrapper = factory({
        last_updated: '2026-05-01T10:00:00+00:00',
        age_hours: 360,
        status: 'stale',
      })
      const label = wrapper.find('[data-testid="freshness-label"]')
      expect(label.text()).toBe('Stale')
    })

    it('displays "Expired" for expired status', () => {
      const wrapper = factory({
        last_updated: '2026-03-01T10:00:00+00:00',
        age_hours: 1800,
        status: 'expired',
      })
      const label = wrapper.find('[data-testid="freshness-label"]')
      expect(label.text()).toBe('Expired')
    })

    it('displays "Unknown" for unknown status', () => {
      const wrapper = factory({
        last_updated: null,
        age_hours: null,
        status: 'unknown',
      })
      const label = wrapper.find('[data-testid="freshness-label"]')
      expect(label.text()).toBe('Unknown')
    })
  })

  describe('tooltip text', () => {
    it('shows hours when age is less than 24h', () => {
      const wrapper = factory({
        last_updated: '2026-05-16T06:00:00+00:00',
        age_hours: 5,
        status: 'fresh',
      })
      const tooltip = wrapper.find('[data-testid="freshness-tooltip"]')
      expect(tooltip.text()).toBe('Last updated: 5 hours ago')
    })

    it('shows days when age is 24h or more', () => {
      const wrapper = factory({
        last_updated: '2026-05-14T10:00:00+00:00',
        age_hours: 48,
        status: 'fresh',
      })
      const tooltip = wrapper.find('[data-testid="freshness-tooltip"]')
      expect(tooltip.text()).toBe('Last updated: 2 days ago')
    })

    it('shows singular "day" for 1 day', () => {
      const wrapper = factory({
        last_updated: '2026-05-15T10:00:00+00:00',
        age_hours: 24,
        status: 'fresh',
      })
      const tooltip = wrapper.find('[data-testid="freshness-tooltip"]')
      expect(tooltip.text()).toBe('Last updated: 1 day ago')
    })

    it('shows "less than an hour ago" for very fresh data', () => {
      const wrapper = factory({
        last_updated: '2026-05-16T10:00:00+00:00',
        age_hours: 0.3,
        status: 'fresh',
      })
      const tooltip = wrapper.find('[data-testid="freshness-tooltip"]')
      expect(tooltip.text()).toBe('Last updated: less than an hour ago')
    })

    it('shows file not found message for unknown status', () => {
      const wrapper = factory({
        last_updated: null,
        age_hours: null,
        status: 'unknown',
      })
      const tooltip = wrapper.find('[data-testid="freshness-tooltip"]')
      expect(tooltip.text()).toBe('Data file not found')
    })
  })

  describe('accessibility', () => {
    it('has an aria-label combining label and tooltip', () => {
      const wrapper = factory({
        last_updated: '2026-05-14T10:00:00+00:00',
        age_hours: 48,
        status: 'fresh',
      })
      const root = wrapper.find('.freshness-indicator')
      expect(root.attributes('aria-label')).toBe('Fresh: Last updated: 2 days ago')
    })

    it('includes sr-only text for screen readers', () => {
      const wrapper = factory({
        last_updated: '2026-05-14T10:00:00+00:00',
        age_hours: 48,
        status: 'fresh',
      })
      const srOnly = wrapper.find('.sr-only')
      expect(srOnly.exists()).toBe(true)
      expect(srOnly.text()).toBe('Last updated: 2 days ago')
    })

    it('is focusable via tabindex', () => {
      const wrapper = factory({
        last_updated: '2026-05-15T10:00:00+00:00',
        age_hours: 24,
        status: 'fresh',
      })
      const root = wrapper.find('.freshness-indicator')
      expect(root.attributes('tabindex')).toBe('0')
    })

    it('dot is aria-hidden', () => {
      const wrapper = factory({
        last_updated: '2026-05-15T10:00:00+00:00',
        age_hours: 24,
        status: 'fresh',
      })
      const dot = wrapper.find('[data-testid="freshness-dot"]')
      expect(dot.attributes('aria-hidden')).toBe('true')
    })
  })
})
