import PerplexityClient from './perplexity';
import OpenAIClient from './openai';
import AnthropicClient from './anthropic';
import GeminiClient from './gemini';

/**
 * Chatbot providers enum
 */
export const ChatbotProvider = {
  PERPLEXITY: 'perplexity',
  OPENAI: 'openai',
  ANTHROPIC: 'anthropic',
  GEMINI: 'gemini',
};

/**
 * Unified chatbot manager for poker coaching
 * Provides a consistent interface to multiple AI chatbot providers
 */
export class ChatbotManager {
  constructor(config = {}) {
    this.clients = {};
    
    // Initialize clients with API keys from config
    if (config.perplexityApiKey) {
      this.clients[ChatbotProvider.PERPLEXITY] = new PerplexityClient(config.perplexityApiKey);
    }
    
    if (config.openaiApiKey) {
      this.clients[ChatbotProvider.OPENAI] = new OpenAIClient(config.openaiApiKey);
    }
    
    if (config.anthropicApiKey) {
      this.clients[ChatbotProvider.ANTHROPIC] = new AnthropicClient(config.anthropicApiKey);
    }
    
    if (config.geminiApiKey) {
      this.clients[ChatbotProvider.GEMINI] = new GeminiClient(config.geminiApiKey);
    }

    // Set default provider
    this.defaultProvider = config.defaultProvider || ChatbotProvider.PERPLEXITY;
  }

  /**
   * Get a specific chatbot client
   * @param {string} provider - Provider name from ChatbotProvider enum
   * @returns {Object} Chatbot client instance
   */
  getClient(provider) {
    const client = this.clients[provider];
    if (!client) {
      throw new Error(`Chatbot provider '${provider}' is not configured. Please add API key.`);
    }
    return client;
  }

  /**
   * Get available chatbot providers
   * @returns {Array<string>} Array of available provider names
   */
  getAvailableProviders() {
    return Object.keys(this.clients);
  }

  /**
   * Check if a provider is available
   * @param {string} provider - Provider name
   * @returns {boolean} True if provider is configured
   */
  isProviderAvailable(provider) {
    return provider in this.clients;
  }

  /**
   * Get poker coaching advice using specified or default provider
   * @param {string} handDescription - Description of the poker hand
   * @param {string} situation - Current game situation
   * @param {string} provider - Optional provider override
   * @returns {Promise<Object>} Response with advice and metadata
   */
  async getPokerAdvice(handDescription, situation, provider = null) {
    const selectedProvider = provider || this.defaultProvider;
    const client = this.getClient(selectedProvider);
    
    try {
      const advice = await client.getPokerAdvice(handDescription, situation);
      return {
        success: true,
        provider: selectedProvider,
        advice: advice,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        provider: selectedProvider,
        error: error.message,
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Analyze a poker hand history using specified or default provider
   * @param {string} handHistory - Complete hand history text
   * @param {string} provider - Optional provider override
   * @returns {Promise<Object>} Response with analysis and metadata
   */
  async analyzeHandHistory(handHistory, provider = null) {
    const selectedProvider = provider || this.defaultProvider;
    const client = this.getClient(selectedProvider);
    
    // Not all clients have this method, use a fallback
    try {
      if (typeof client.analyzeHandHistory === 'function') {
        const analysis = await client.analyzeHandHistory(handHistory);
        return {
          success: true,
          provider: selectedProvider,
          analysis: analysis,
          timestamp: new Date().toISOString(),
        };
      } else {
        // Fallback to getPokerAdvice for providers without dedicated method
        const analysis = await client.getPokerAdvice(handHistory, 'Please analyze this hand history');
        return {
          success: true,
          provider: selectedProvider,
          analysis: analysis,
          timestamp: new Date().toISOString(),
        };
      }
    } catch (error) {
      return {
        success: false,
        provider: selectedProvider,
        error: error.message,
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Analyze a poker hand from an image (multimodal)
   * @param {string} imageData - Base64 encoded image or URL
   * @param {string} question - Question about the hand
   * @param {string} provider - Provider (must support multimodal)
   * @returns {Promise<Object>} Response with analysis and metadata
   */
  async analyzeHandImage(imageData, question = 'Analyze this poker hand and provide strategic advice.', provider = null) {
    const selectedProvider = provider || ChatbotProvider.OPENAI;
    const client = this.getClient(selectedProvider);
    
    // Only some providers support image analysis
    if (!['openai', 'anthropic', 'gemini'].includes(selectedProvider)) {
      return {
        success: false,
        provider: selectedProvider,
        error: `Provider '${selectedProvider}' does not support image analysis. Use OpenAI, Anthropic, or Gemini.`,
        timestamp: new Date().toISOString(),
      };
    }
    
    try {
      const analysis = await client.analyzeHandImage(imageData, question);
      return {
        success: true,
        provider: selectedProvider,
        analysis: analysis,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        provider: selectedProvider,
        error: error.message,
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Analyze a poker hand with both text and image (multimodal)
   * @param {string} handDescription - Description of the poker hand
   * @param {string} imageData - Base64 encoded image or URL
   * @param {string} provider - Provider (must support multimodal)
   * @returns {Promise<Object>} Response with analysis and metadata
   */
  async analyzeHandWithImage(handDescription, imageData, provider = null) {
    const selectedProvider = provider || ChatbotProvider.OPENAI;
    const client = this.getClient(selectedProvider);
    
    // Only some providers support image analysis
    if (!['openai', 'anthropic', 'gemini'].includes(selectedProvider)) {
      return {
        success: false,
        provider: selectedProvider,
        error: `Provider '${selectedProvider}' does not support multimodal analysis. Use OpenAI, Anthropic, or Gemini.`,
        timestamp: new Date().toISOString(),
      };
    }
    
    try {
      const analysis = await client.analyzeHandWithImage(handDescription, imageData);
      return {
        success: true,
        provider: selectedProvider,
        analysis: analysis,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        provider: selectedProvider,
        error: error.message,
        timestamp: new Date().toISOString(),
      };
    }
  }
}

export default ChatbotManager;
