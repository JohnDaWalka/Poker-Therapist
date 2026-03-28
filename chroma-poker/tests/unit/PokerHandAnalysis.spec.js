import { shallowMount } from '@vue/test-utils';
import PokerHandAnalysis from '@/components/PokerHandAnalysis.vue';
import Vuex from 'vuex';
import Vue from 'vue';

Vue.use(Vuex);

describe('PokerHandAnalysis.vue', () => {
  let actions;
  let getters;
  let store;

  beforeEach(() => {
    actions = {
      fetchPokerHandAnalysis: jest.fn(),
    };
    getters = {
      handStrengths: () => ['High Card', 'Pair', 'Two Pair'],
      filteredHands: () => [
        { id: 1, details: 'Hand 1', strength: 'Pair', rank: 1, probability: 50, actions: 'Call' },
        { id: 2, details: 'Hand 2', strength: 'High Card', rank: 2, probability: 30, actions: 'Fold' },
      ],
      chartData: () => ({ labels: ['Hand 1', 'Hand 2'], datasets: [{ data: [50, 30] }] }),
    };
    store = new Vuex.Store({
      actions,
      getters,
    });
  });

  it('renders poker hand analysis component', () => {
    const wrapper = shallowMount(PokerHandAnalysis, { store, Vue });
    expect(wrapper.find('.poker-hand-analysis').exists()).toBe(true);
  });

  it('renders hand strengths in filter options', () => {
    const wrapper = shallowMount(PokerHandAnalysis, { store, Vue });
    const options = wrapper.findAll('option');
    expect(options.length).toBe(4); // including the "All" option
    expect(options.at(1).text()).toBe('High Card');
    expect(options.at(2).text()).toBe('Pair');
    expect(options.at(3).text()).toBe('Two Pair');
  });

  it('renders chart with correct data', () => {
    const wrapper = shallowMount(PokerHandAnalysis, { store, Vue });
    const chart = wrapper.findComponent({ name: 'Chart' });
    expect(chart.exists()).toBe(true);
    expect(chart.props().data).toEqual({ labels: ['Hand 1', 'Hand 2'], datasets: [{ data: [50, 30] }] });
  });

  it('renders table with correct data', () => {
    const wrapper = shallowMount(PokerHandAnalysis, { store, Vue });
    const rows = wrapper.findAll('tbody tr');
    expect(rows.length).toBe(2);
    expect(rows.at(0).find('td').text()).toBe('Hand 1');
    expect(rows.at(1).find('td').text()).toBe('Hand 2');
  });

  it('calls fetchPokerHandAnalysis action on created', () => {
    shallowMount(PokerHandAnalysis, { store, Vue });
    expect(actions.fetchPokerHandAnalysis).toHaveBeenCalled();
  });

  it('sorts table by column when header is clicked', async () => {
    const wrapper = shallowMount(PokerHandAnalysis, { store, Vue });
    const headers = wrapper.findAll('th');
    await headers.at(1).trigger('click'); // Sort by strength
    const rows = wrapper.findAll('tbody tr');
    expect(rows.at(0).find('td').text()).toBe('Hand 2'); // High Card should come before Pair
  });
});
