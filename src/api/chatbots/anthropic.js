import axios from 'axios';

const ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages';

/**
 * Anthropic Claude multimodal client for poker coaching
 * Supports text and image analysis with Claude's advanced reasoning
 */
export class AnthropicClient {
  constructor(apiKey) {
    this.apiKey = apiKey || process.env.VUE_APP_ANTHROPIC_API_KEY;
    this.model = 'claude-3-5-sonnet-20241022';
    this.apiVersion = '2023-06-01'; // Anthropic API version
  }

  /**
   * Send a message to Anthropic Claude
   * @param {Array} messages - Array of message objects with role and content
   * @param {Object} options - Additional options like temperature, max_tokens
   * @returns {Promise<Object>} Response from Anthropic
   */
  async sendMessage(messages, options = {}) {
    try {
      const response = await axios.post(
        ANTHROPIC_API_URL,
        {
          model: options.model || this.model,
          messages: messages,
          max_tokens: options.max_tokens || 1024,
          temperature: options.temperature || 0.7,
          system: options.system || 'You are an expert poker coach with deep knowledge of game theory optimal (GTO) play, tournament strategy, and cash game tactics.',
        },
        {
          headers: {
            'x-api-key': this.apiKey,
            'anthropic-version': this.apiVersion,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error calling Anthropic API:', error);
      throw new Error(`Anthropic API error: ${error.message}`);
    }
  }

  /**
   * Get poker coaching advice
   * @param {string} handDescription - Description of the poker hand
   * @param {string} situation - Current game situation
   * @returns {Promise<string>} Coaching advice
   */
  async getPokerAdvice(handDescription, situation) {
    const userMessage = {
      role: 'user',
      content: `Hand: ${handDescription}\nSituation: ${situation}\n\nPlease provide strategic advice for this poker situation.`,
    };

    const response = await this.sendMessage([userMessage]);
    return response.content[0].text;
  }

  /**
   * Analyze a poker hand from an image
   * @param {string} imageData - Base64 encoded image data
   * @param {string} question - Question about the hand
   * @param {string} mediaType - Media type (e.g., 'image/jpeg', 'image/png')
   * @returns {Promise<string>} Analysis from the image
   */
  async analyzeHandImage(imageData, question = 'Analyze this poker hand and provide strategic advice.', mediaType = 'image/jpeg') {
    const messages = [
      {
        role: 'user',
        content: [
          {
            type: 'image',
            source: {
              type: 'base64',
              media_type: mediaType,
              data: imageData,
            },
          },
          {
            type: 'text',
            text: question,
          },
        ],
      },
    ];

    const response = await this.sendMessage(messages, {
      system: 'You are an expert poker coach. Analyze poker hands from images and provide strategic advice.',
    });
    return response.content[0].text;
  }

  /**
   * Analyze a poker hand with both text and image
   * @param {string} handDescription - Description of the poker hand
   * @param {string} imageData - Base64 encoded image data
   * @param {string} mediaType - Media type
   * @returns {Promise<string>} Combined analysis
   */
  async analyzeHandWithImage(handDescription, imageData, mediaType = 'image/jpeg') {
    const messages = [
      {
        role: 'user',
        content: [
          {
            type: 'text',
            text: `Hand Description: ${handDescription}\n\nPlease analyze this hand and provide strategic advice.`,
          },
          {
            type: 'image',
            source: {
              type: 'base64',
              media_type: mediaType,
              data: imageData,
            },
          },
        ],
      },
    ];

    const response = await this.sendMessage(messages, {
      system: 'You are an expert poker coach. Analyze poker hands using both text description and visual information.',
    });
    return response.content[0].text;
  }

  /**
   * Analyze a poker hand history
   * @param {string} handHistory - Complete hand history text
   * @returns {Promise<string>} Analysis and advice
   */
  async analyzeHandHistory(handHistory) {
    const userMessage = {
      role: 'user',
      content: `Please analyze this hand history:\n\n${handHistory}`,
    };

    const response = await this.sendMessage([userMessage], {
      system: 'You are a professional poker coach analyzing hand histories. Break down the action street by street, identify mistakes, and suggest improvements based on game theory optimal play.',
    });
    return response.content[0].text;
  }
}

export default AnthropicClient;
