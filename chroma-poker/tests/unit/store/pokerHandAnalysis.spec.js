import Vuex from 'vuex';
import { createLocalVue } from '@vue/test-utils';
import {
  getHandDetails,
  getHandStrength,
  getHandRank,
  getWinningProbability,
  getSuggestedActions,
  getOpponentAnalysis,
  getHistoricalData,
  getVisualElements,
} from '@/api/pokerHandAnalysis';
import pokerHandAnalysis from '@/store/modules/pokerHandAnalysis';

const localVue = createLocalVue();
localVue.use(Vuex);

jest.mock('@/api/pokerHandAnalysis');

describe('pokerHandAnalysis Vuex module', () => {
  let store;

  beforeEach(() => {
    store = new Vuex.Store({
      modules: {
        pokerHandAnalysis,
      },
    });
  });

  it('fetches and sets hand details', async () => {
    const handDetails = { details: 'Hand details' };
    getHandDetails.mockResolvedValue(handDetails);

    await store.dispatch('fetchHandDetails');
    expect(store.state.pokerHandAnalysis.handDetails).toEqual(handDetails);
  });

  it('fetches and sets hand strength', async () => {
    const handStrength = 'Hand strength';
    getHandStrength.mockResolvedValue(handStrength);

    await store.dispatch('fetchHandStrength');
    expect(store.state.pokerHandAnalysis.handStrength).toEqual(handStrength);
  });

  it('fetches and sets hand rank', async () => {
    const handRank = 'Hand rank';
    getHandRank.mockResolvedValue(handRank);

    await store.dispatch('fetchHandRank');
    expect(store.state.pokerHandAnalysis.handRank).toEqual(handRank);
  });

  it('fetches and sets winning probability', async () => {
    const winningProbability = 75;
    getWinningProbability.mockResolvedValue(winningProbability);

    await store.dispatch('fetchWinningProbability');
    expect(store.state.pokerHandAnalysis.winningProbability).toEqual(winningProbability);
  });

  it('fetches and sets suggested actions', async () => {
    const suggestedActions = ['Fold', 'Call'];
    getSuggestedActions.mockResolvedValue(suggestedActions);

    await store.dispatch('fetchSuggestedActions');
    expect(store.state.pokerHandAnalysis.suggestedActions).toEqual(suggestedActions);
  });

  it('fetches and sets opponent analysis', async () => {
    const opponentAnalysis = { analysis: 'Opponent analysis' };
    getOpponentAnalysis.mockResolvedValue(opponentAnalysis);

    await store.dispatch('fetchOpponentAnalysis');
    expect(store.state.pokerHandAnalysis.opponentAnalysis).toEqual(opponentAnalysis);
  });

  it('fetches and sets historical data', async () => {
    const historicalData = [{ id: 1, data: 'Historical data' }];
    getHistoricalData.mockResolvedValue(historicalData);

    await store.dispatch('fetchHistoricalData');
    expect(store.state.pokerHandAnalysis.historicalData).toEqual(historicalData);
  });

  it('fetches and sets visual elements', async () => {
    const visualElements = { elements: 'Visual elements' };
    getVisualElements.mockResolvedValue(visualElements);

    await store.dispatch('fetchVisualElements');
    expect(store.state.pokerHandAnalysis.visualElements).toEqual(visualElements);
  });
});
