import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import PerplexityClient from '@/api/chatbots/perplexity';

describe('PerplexityClient', () => {
  let mock;
  let client;

  beforeEach(() => {
    mock = new MockAdapter(axios);
    client = new PerplexityClient('test-api-key');
  });

  afterEach(() => {
    mock.restore();
  });

  describe('sendMessage', () => {
    it('sends a message successfully', async () => {
      const messages = [
        { role: 'system', content: 'You are a poker coach' },
        { role: 'user', content: 'What should I do with pocket aces?' },
      ];
      const responseData = {
        choices: [
          {
            message: {
              content: 'Pocket aces are the best starting hand in poker. You should raise pre-flop.',
            },
          },
        ],
      };

      mock.onPost('https://api.perplexity.ai/chat/completions').reply(200, responseData);

      const result = await client.sendMessage(messages);
      expect(result).toEqual(responseData);
    });

    it('handles API errors', async () => {
      const messages = [{ role: 'user', content: 'Test' }];
      mock.onPost('https://api.perplexity.ai/chat/completions').reply(500, { error: 'Server error' });

      await expect(client.sendMessage(messages)).rejects.toThrow('Perplexity API error');
    });
  });

  describe('getPokerAdvice', () => {
    it('gets poker advice successfully', async () => {
      const handDescription = 'Pocket aces';
      const situation = 'Pre-flop, 6-player game';
      const responseData = {
        choices: [
          {
            message: {
              content: 'With pocket aces in a 6-player game, you should raise 3-4 big blinds.',
            },
          },
        ],
      };

      mock.onPost('https://api.perplexity.ai/chat/completions').reply(200, responseData);

      const result = await client.getPokerAdvice(handDescription, situation);
      expect(result).toBe('With pocket aces in a 6-player game, you should raise 3-4 big blinds.');
    });
  });

  describe('analyzeHandHistory', () => {
    it('analyzes hand history successfully', async () => {
      const handHistory = 'Player 1 raises to 100, Player 2 calls...';
      const responseData = {
        choices: [
          {
            message: {
              content: 'The initial raise was standard, but the call suggests a drawing hand.',
            },
          },
        ],
      };

      mock.onPost('https://api.perplexity.ai/chat/completions').reply(200, responseData);

      const result = await client.analyzeHandHistory(handHistory);
      expect(result).toBe('The initial raise was standard, but the call suggests a drawing hand.');
    });
  });
});
