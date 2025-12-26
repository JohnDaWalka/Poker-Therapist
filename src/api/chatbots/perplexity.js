import axios from 'axios';

const PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions';

/**
 * Perplexity AI client for poker coaching
 * Provides real-time, research-backed poker strategy advice
 */
export class PerplexityClient {
  constructor(apiKey) {
    this.apiKey = apiKey || process.env.VUE_APP_PERPLEXITY_API_KEY;
    this.model = 'llama-3.1-sonar-large-128k-online';
  }

  /**
   * Send a message to Perplexity AI
   * @param {Array} messages - Array of message objects with role and content
   * @param {Object} options - Additional options like temperature, max_tokens
   * @returns {Promise<Object>} Response from Perplexity AI
   */
  async sendMessage(messages, options = {}) {
    try {
      const response = await axios.post(
        PERPLEXITY_API_URL,
        {
          model: options.model || this.model,
          messages: messages,
          temperature: options.temperature || 0.7,
          max_tokens: options.max_tokens || 1000,
          stream: options.stream || false,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error calling Perplexity API:', error);
      throw new Error(`Perplexity API error: ${error.message}`);
    }
  }

  /**
   * Get poker coaching advice
   * @param {string} handDescription - Description of the poker hand
   * @param {string} situation - Current game situation
   * @returns {Promise<string>} Coaching advice
   */
  async getPokerAdvice(handDescription, situation) {
    const systemPrompt = {
      role: 'system',
      content: 'You are an expert poker coach with deep knowledge of game theory optimal (GTO) play, tournament strategy, and cash game tactics. Provide clear, actionable advice based on the latest poker theory and research.',
    };

    const userMessage = {
      role: 'user',
      content: `Hand: ${handDescription}\nSituation: ${situation}\n\nPlease provide strategic advice for this poker situation.`,
    };

    const response = await this.sendMessage([systemPrompt, userMessage]);
    return response.choices[0].message.content;
  }

  /**
   * Analyze a poker hand history
   * @param {string} handHistory - Complete hand history text
   * @returns {Promise<string>} Analysis and advice
   */
  async analyzeHandHistory(handHistory) {
    const systemPrompt = {
      role: 'system',
      content: 'You are a professional poker coach analyzing hand histories. Break down the action street by street, identify mistakes, and suggest improvements based on game theory optimal play.',
    };

    const userMessage = {
      role: 'user',
      content: `Please analyze this hand history:\n\n${handHistory}`,
    };

    const response = await this.sendMessage([systemPrompt, userMessage]);
    return response.choices[0].message.content;
  }
}

export default PerplexityClient;
