import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import OpenAIClient from '@/api/chatbots/openai';

describe('OpenAIClient', () => {
  let mock;
  let client;

  beforeEach(() => {
    mock = new MockAdapter(axios);
    client = new OpenAIClient('test-api-key');
  });

  afterEach(() => {
    mock.restore();
  });

  describe('sendMessage', () => {
    it('sends a message successfully', async () => {
      const messages = [
        { role: 'system', content: 'You are a poker coach' },
        { role: 'user', content: 'Analyze my hand' },
      ];
      const responseData = {
        choices: [
          {
            message: {
              content: 'Your hand has good potential',
            },
          },
        ],
      };

      mock.onPost('https://api.openai.com/v1/chat/completions').reply(200, responseData);

      const result = await client.sendMessage(messages);
      expect(result).toEqual(responseData);
    });

    it('handles API errors', async () => {
      const messages = [{ role: 'user', content: 'Test' }];
      mock.onPost('https://api.openai.com/v1/chat/completions').reply(500, { error: 'Server error' });

      await expect(client.sendMessage(messages)).rejects.toThrow('OpenAI API error');
    });
  });

  describe('analyzeHandImage', () => {
    it('analyzes hand image successfully', async () => {
      const imageUrl = 'data:image/jpeg;base64,/9j/4AAQ...';
      const question = 'What cards do you see?';
      const responseData = {
        choices: [
          {
            message: {
              content: 'I can see you have a pair of kings',
            },
          },
        ],
      };

      mock.onPost('https://api.openai.com/v1/chat/completions').reply(200, responseData);

      const result = await client.analyzeHandImage(imageUrl, question);
      expect(result).toBe('I can see you have a pair of kings');
    });
  });

  describe('getPokerAdvice', () => {
    it('gets poker advice successfully', async () => {
      const handDescription = 'Pair of tens';
      const situation = 'Middle position';
      const responseData = {
        choices: [
          {
            message: {
              content: 'Pair of tens in middle position is a solid hand. Consider raising.',
            },
          },
        ],
      };

      mock.onPost('https://api.openai.com/v1/chat/completions').reply(200, responseData);

      const result = await client.getPokerAdvice(handDescription, situation);
      expect(result).toBe('Pair of tens in middle position is a solid hand. Consider raising.');
    });
  });

  describe('analyzeHandWithImage', () => {
    it('analyzes hand with both text and image', async () => {
      const handDescription = 'I have a flush draw';
      const imageUrl = 'data:image/jpeg;base64,/9j/4AAQ...';
      const responseData = {
        choices: [
          {
            message: {
              content: 'Your flush draw has good equity. Consider semi-bluffing.',
            },
          },
        ],
      };

      mock.onPost('https://api.openai.com/v1/chat/completions').reply(200, responseData);

      const result = await client.analyzeHandWithImage(handDescription, imageUrl);
      expect(result).toBe('Your flush draw has good equity. Consider semi-bluffing.');
    });
  });
});
