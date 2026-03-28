import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import * as api from '@/api/pokerHandAnalysis';

describe('pokerHandAnalysis API', () => {
  let mock;

  beforeEach(() => {
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    mock.restore();
  });

  it('fetches hand details', async () => {
    const data = { details: 'Hand details' };
    mock.onGet('https://api.example.com/poker-hand-analysis/hand-details').reply(200, data);

    const result = await api.getHandDetails();
    expect(result).toEqual(data);
  });

  it('fetches hand strength', async () => {
    const data = { strength: 'Hand strength' };
    mock.onGet('https://api.example.com/poker-hand-analysis/hand-strength').reply(200, data);

    const result = await api.getHandStrength();
    expect(result).toEqual(data);
  });

  it('fetches hand rank', async () => {
    const data = { rank: 'Hand rank' };
    mock.onGet('https://api.example.com/poker-hand-analysis/hand-rank').reply(200, data);

    const result = await api.getHandRank();
    expect(result).toEqual(data);
  });

  it('fetches winning probability', async () => {
    const data = { probability: 75 };
    mock.onGet('https://api.example.com/poker-hand-analysis/winning-probability').reply(200, data);

    const result = await api.getWinningProbability();
    expect(result).toEqual(data);
  });

  it('fetches suggested actions', async () => {
    const data = { actions: 'Suggested actions' };
    mock.onGet('https://api.example.com/poker-hand-analysis/suggested-actions').reply(200, data);

    const result = await api.getSuggestedActions();
    expect(result).toEqual(data);
  });

  it('fetches opponent analysis', async () => {
    const data = { analysis: 'Opponent analysis' };
    mock.onGet('https://api.example.com/poker-hand-analysis/opponent-analysis').reply(200, data);

    const result = await api.getOpponentAnalysis();
    expect(result).toEqual(data);
  });

  it('fetches historical data', async () => {
    const data = { history: 'Historical data' };
    mock.onGet('https://api.example.com/poker-hand-analysis/historical-data').reply(200, data);

    const result = await api.getHistoricalData();
    expect(result).toEqual(data);
  });

  it('fetches visual elements', async () => {
    const data = { elements: 'Visual elements' };
    mock.onGet('https://api.example.com/poker-hand-analysis/visual-elements').reply(200, data);

    const result = await api.getVisualElements();
    expect(result).toEqual(data);
  });
});
