import { ChatbotManager, ChatbotProvider } from '@/api/chatbots';
import PerplexityClient from '@/api/chatbots/perplexity';
import OpenAIClient from '@/api/chatbots/openai';

jest.mock('@/api/chatbots/perplexity');
jest.mock('@/api/chatbots/openai');

describe('ChatbotManager', () => {
  let manager;
  let mockPerplexityClient;
  let mockOpenAIClient;

  beforeEach(() => {
    mockPerplexityClient = {
      getPokerAdvice: jest.fn(),
      analyzeHandHistory: jest.fn(),
    };
    mockOpenAIClient = {
      getPokerAdvice: jest.fn(),
      analyzeHandImage: jest.fn(),
      analyzeHandWithImage: jest.fn(),
    };

    PerplexityClient.mockImplementation(() => mockPerplexityClient);
    OpenAIClient.mockImplementation(() => mockOpenAIClient);

    manager = new ChatbotManager({
      perplexityApiKey: 'test-perplexity-key',
      openaiApiKey: 'test-openai-key',
      defaultProvider: ChatbotProvider.PERPLEXITY,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('initialization', () => {
    it('initializes with provided API keys', () => {
      expect(PerplexityClient).toHaveBeenCalledWith('test-perplexity-key');
      expect(OpenAIClient).toHaveBeenCalledWith('test-openai-key');
    });

    it('sets default provider', () => {
      expect(manager.defaultProvider).toBe(ChatbotProvider.PERPLEXITY);
    });
  });

  describe('getClient', () => {
    it('returns the correct client', () => {
      const client = manager.getClient(ChatbotProvider.PERPLEXITY);
      expect(client).toBe(mockPerplexityClient);
    });

    it('throws error for unconfigured provider', () => {
      expect(() => manager.getClient(ChatbotProvider.ANTHROPIC))
        .toThrow("Chatbot provider 'anthropic' is not configured");
    });
  });

  describe('getAvailableProviders', () => {
    it('returns list of available providers', () => {
      const providers = manager.getAvailableProviders();
      expect(providers).toEqual(['perplexity', 'openai']);
    });
  });

  describe('isProviderAvailable', () => {
    it('returns true for available provider', () => {
      expect(manager.isProviderAvailable(ChatbotProvider.PERPLEXITY)).toBe(true);
    });

    it('returns false for unavailable provider', () => {
      expect(manager.isProviderAvailable(ChatbotProvider.ANTHROPIC)).toBe(false);
    });
  });

  describe('getPokerAdvice', () => {
    it('gets advice using default provider', async () => {
      mockPerplexityClient.getPokerAdvice.mockResolvedValue('Good advice');

      const result = await manager.getPokerAdvice('Pocket aces', 'Pre-flop');

      expect(mockPerplexityClient.getPokerAdvice).toHaveBeenCalledWith('Pocket aces', 'Pre-flop');
      expect(result.success).toBe(true);
      expect(result.advice).toBe('Good advice');
      expect(result.provider).toBe(ChatbotProvider.PERPLEXITY);
    });

    it('gets advice using specified provider', async () => {
      mockOpenAIClient.getPokerAdvice.mockResolvedValue('OpenAI advice');

      const result = await manager.getPokerAdvice('Pair of tens', 'Middle position', ChatbotProvider.OPENAI);

      expect(mockOpenAIClient.getPokerAdvice).toHaveBeenCalledWith('Pair of tens', 'Middle position');
      expect(result.success).toBe(true);
      expect(result.advice).toBe('OpenAI advice');
      expect(result.provider).toBe(ChatbotProvider.OPENAI);
    });

    it('handles errors gracefully', async () => {
      mockPerplexityClient.getPokerAdvice.mockRejectedValue(new Error('API error'));

      const result = await manager.getPokerAdvice('Bad hand', 'Late position');

      expect(result.success).toBe(false);
      expect(result.error).toBe('API error');
    });
  });

  describe('analyzeHandHistory', () => {
    it('analyzes hand history successfully', async () => {
      mockPerplexityClient.analyzeHandHistory.mockResolvedValue('Good analysis');

      const result = await manager.analyzeHandHistory('Hand history text');

      expect(mockPerplexityClient.analyzeHandHistory).toHaveBeenCalledWith('Hand history text');
      expect(result.success).toBe(true);
      expect(result.analysis).toBe('Good analysis');
    });

    it('falls back to getPokerAdvice if method not available', async () => {
      const clientWithoutMethod = {
        getPokerAdvice: jest.fn().mockResolvedValue('Fallback advice'),
      };
      manager.clients[ChatbotProvider.PERPLEXITY] = clientWithoutMethod;

      const result = await manager.analyzeHandHistory('Hand history text');

      expect(clientWithoutMethod.getPokerAdvice).toHaveBeenCalled();
      expect(result.success).toBe(true);
    });
  });

  describe('analyzeHandImage', () => {
    it('analyzes image successfully', async () => {
      mockOpenAIClient.analyzeHandImage.mockResolvedValue('Image analysis');

      const result = await manager.analyzeHandImage('base64-image-data', 'What do you see?', ChatbotProvider.OPENAI);

      expect(mockOpenAIClient.analyzeHandImage).toHaveBeenCalledWith('base64-image-data', 'What do you see?');
      expect(result.success).toBe(true);
      expect(result.analysis).toBe('Image analysis');
    });

    it('rejects non-multimodal providers', async () => {
      const result = await manager.analyzeHandImage('image-data', 'Question', ChatbotProvider.PERPLEXITY);

      expect(result.success).toBe(false);
      expect(result.error).toContain('does not support image analysis');
    });
  });

  describe('analyzeHandWithImage', () => {
    it('analyzes hand with text and image', async () => {
      mockOpenAIClient.analyzeHandWithImage.mockResolvedValue('Combined analysis');

      const result = await manager.analyzeHandWithImage('Hand description', 'image-data', ChatbotProvider.OPENAI);

      expect(mockOpenAIClient.analyzeHandWithImage).toHaveBeenCalledWith('Hand description', 'image-data');
      expect(result.success).toBe(true);
      expect(result.analysis).toBe('Combined analysis');
    });

    it('rejects non-multimodal providers', async () => {
      const result = await manager.analyzeHandWithImage('text', 'image', ChatbotProvider.PERPLEXITY);

      expect(result.success).toBe(false);
      expect(result.error).toContain('does not support multimodal analysis');
    });
  });
});
