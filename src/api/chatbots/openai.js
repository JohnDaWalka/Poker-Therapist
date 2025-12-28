import axios from 'axios';

const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';

/**
 * OpenAI GPT-4 multimodal client for poker coaching
 * Supports text and image analysis for poker hands
 */
export class OpenAIClient {
  constructor(apiKey) {
    this.apiKey = apiKey || process.env.VUE_APP_OPENAI_API_KEY;
    this.model = 'gpt-4o';
  }

  /**
   * Send a message to OpenAI
   * @param {Array} messages - Array of message objects with role and content
   * @param {Object} options - Additional options like temperature, max_tokens
   * @returns {Promise<Object>} Response from OpenAI
   */
  async sendMessage(messages, options = {}) {
    try {
      const response = await axios.post(
        OPENAI_API_URL,
        {
          model: options.model || this.model,
          messages: messages,
          temperature: options.temperature || 0.7,
          max_tokens: options.max_tokens || 1000,
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
      console.error('Error calling OpenAI API:', error);
      throw new Error(`OpenAI API error: ${error.message}`);
    }
  }

  /**
   * Analyze a poker hand from an image
   * @param {string} imageUrl - URL or base64 encoded image
   * @param {string} question - Question about the hand
   * @returns {Promise<string>} Analysis from the image
   */
  async analyzeHandImage(imageUrl, question = 'Analyze this poker hand and provide strategic advice.') {
    const messages = [
      {
        role: 'system',
        content: 'You are an expert poker coach. Analyze poker hands from images and provide strategic advice.',
      },
      {
        role: 'user',
        content: [
          {
            type: 'text',
            text: question,
          },
          {
            type: 'image_url',
            image_url: {
              url: imageUrl,
            },
          },
        ],
      },
    ];

    const response = await this.sendMessage(messages);
    return response.choices[0].message.content;
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
      content: 'You are an expert poker coach with deep knowledge of game theory optimal (GTO) play, tournament strategy, and cash game tactics. Provide clear, actionable advice.',
    };

    const userMessage = {
      role: 'user',
      content: `Hand: ${handDescription}\nSituation: ${situation}\n\nPlease provide strategic advice for this poker situation.`,
    };

    const response = await this.sendMessage([systemPrompt, userMessage]);
    return response.choices[0].message.content;
  }

  /**
   * Analyze a poker hand with both text and image
   * @param {string} handDescription - Description of the poker hand
   * @param {string} imageUrl - URL or base64 encoded image
   * @returns {Promise<string>} Combined analysis
   */
  async analyzeHandWithImage(handDescription, imageUrl) {
    const messages = [
      {
        role: 'system',
        content: 'You are an expert poker coach. Analyze poker hands using both text description and visual information.',
      },
      {
        role: 'user',
        content: [
          {
            type: 'text',
            text: `Hand Description: ${handDescription}\n\nPlease analyze this hand and provide strategic advice.`,
          },
          {
            type: 'image_url',
            image_url: {
              url: imageUrl,
            },
          },
        ],
      },
    ];

    const response = await this.sendMessage(messages);
    return response.choices[0].message.content;
  }
}

export default OpenAIClient;
