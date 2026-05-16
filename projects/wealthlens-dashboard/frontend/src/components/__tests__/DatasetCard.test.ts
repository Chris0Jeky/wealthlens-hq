import { describe, it, expect } from "vitest";
import { mount, RouterLinkStub } from "@vue/test-utils";
import DatasetCard from "@/components/DatasetCard.vue";

describe('DatasetCard', () => {
  const defaultProps = {
    name: 'wealth-shares',
    description: 'Top 1% and 10% wealth shares (WID)',
  }

  const routerLinkStub = {
    template: '<a :href="to"><slot /></a>',
    props: ['to'],
  }

  function factory(props = defaultProps) {
    return mount(DatasetCard, {
      props,
      global: { stubs: { 'router-link': routerLinkStub } },
    })
  }

  it('renders the name prop', () => {
    const wrapper = factory()
    expect(wrapper.text()).toContain(defaultProps.name)
  })

  it('renders the description prop', () => {
    const wrapper = factory()
    expect(wrapper.text()).toContain(defaultProps.description)
  })

  it("uses a semantic article element with aria-label", () => {
    const wrapper = mount(DatasetCard, { props: defaultProps });
    expect(wrapper.element.tagName).toBe("ARTICLE");
    expect(wrapper.attributes("aria-label")).toBe(
      `Dataset: ${defaultProps.name}`,
    );
  });

  it("renders view-chart link with aria-label when chart is available", () => {
    const wrapper = mount(DatasetCard, {
      props: { ...defaultProps, hasChart: true },
      global: { stubs: { RouterLink: RouterLinkStub } },
    });
    const link = wrapper.findComponent(RouterLinkStub);
    expect(link.exists()).toBe(true);
    expect(link.attributes("aria-label")).toBe(
      `View ${defaultProps.name} chart`,
    );
  });

  it('uses an h3 for the dataset name', () => {
    const wrapper = factory()
    const heading = wrapper.find('h3')
    expect(heading.exists()).toBe(true)
    expect(heading.text()).toBe(defaultProps.name)
  })

  it('shows chart link when hasChart is true', () => {
    const wrapper = factory({ name: 'wealth-shares', description: 'D', hasChart: true })
    expect(wrapper.html()).toContain('/charts/wealth-shares')
  })

  it('shows "coming soon" for unsupported datasets', () => {
    const wrapper = factory({ name: 'unknown-dataset', description: 'Test' })
    expect(wrapper.text()).toContain('coming soon')
  })

  it('renders download CSV link', () => {
    const wrapper = factory()
    const downloadLink = wrapper.find('a[download]')
    expect(downloadLink.exists()).toBe(true)
    expect(downloadLink.attributes('href')).toBe('/api/data/wealth-shares/download')
  })

  it('download link has accessible label', () => {
    const wrapper = factory()
    const downloadLink = wrapper.find('a[download]')
    expect(downloadLink.attributes('aria-label')).toBe('Download wealth-shares as CSV')
  })

  it('respects hasChart prop override', () => {
    const wrapper = factory({ name: 'unknown', description: 'D', hasChart: true })
    expect(wrapper.text()).toContain('View Chart')
  })
});
