import axios from 'axios';

const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models';

/**
 * Google Gemini multimodal client for poker coaching
 * Supports text and image analysis with Gemini's advanced capabilities
 */
export class GeminiClient {
  constructor(apiKey) {
    this.apiKey = apiKey || process.env.GEMINI_API_KEY;
    this.model = 'gemini-1.5-pro';
  }

  /**
   * Send a message to Google Gemini
   * @param {Array} contents - Array of content objects
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Response from Gemini
   */
  async sendMessage(contents, options = {}) {
    try {
      const model = options.model || this.model;
      const response = await axios.post(
        `${GEMINI_API_URL}/${model}:generateContent?key=${this.apiKey}`,
        {
          contents: contents,
          generationConfig: {
            temperature: options.temperature || 0.7,
            maxOutputTokens: options.max_tokens || 1000,
          },
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error calling Gemini API:', error);
      throw new Error(`Gemini API error: ${error.message}`);
    }
  }

  /**
   * Get poker coaching advice
   * @param {string} handDescription - Description of the poker hand
   * @param {string} situation - Current game situation
   * @returns {Promise<string>} Coaching advice
   */
  async getPokerAdvice(handDescription, situation) {
    const systemPrompt = `You are an expert poker coach with deep knowledge of game theory optimal (GTO) play, tournament strategy, and cash game tactics. Provide clear, actionable advice.`;
    
    const contents = [
      {
        role: 'user',
        parts: [
          {
            text: `${systemPrompt}\n\nHand: ${handDescription}\nSituation: ${situation}\n\nPlease provide strategic advice for this poker situation.`,
          },
        ],
      },
    ];

    const response = await this.sendMessage(contents);
    return response.candidates[0].content.parts[0].text;
  }

  /**
   * Analyze a poker hand from an image
   * @param {string} imageData - Base64 encoded image data
   * @param {string} mimeType - MIME type (e.g., 'image/jpeg', 'image/png')
   * @param {string} question - Question about the hand
   * @returns {Promise<string>} Analysis from the image
   */
  async analyzeHandImage(imageData, mimeType = 'image/jpeg', question = 'Analyze this poker hand and provide strategic advice.') {
    const contents = [
      {
        role: 'user',
        parts: [
          {
            text: `You are an expert poker coach. ${question}`,
          },
          {
            inline_data: {
              mime_type: mimeType,
              data: imageData,
            },
          },
        ],
      },
    ];

    const response = await this.sendMessage(contents);
    return response.candidates[0].content.parts[0].text;
  }

  /**
   * Analyze a poker hand with both text and image
   * @param {string} handDescription - Description of the poker hand
   * @param {string} imageData - Base64 encoded image data
   * @param {string} mimeType - MIME type
   * @returns {Promise<string>} Combined analysis
   */
  async analyzeHandWithImage(handDescription, imageData, mimeType = 'image/jpeg') {
    const contents = [
      {
        role: 'user',
        parts: [
          {
            text: `You are an expert poker coach. Hand Description: ${handDescription}\n\nPlease analyze this hand and provide strategic advice.`,
          },
          {
            inline_data: {
              mime_type: mimeType,
              data: imageData,
            },
          },
        ],
      },
    ];

    const response = await this.sendMessage(contents);
    return response.candidates[0].content.parts[0].text;
  }

  /**
   * Analyze a poker hand history
   * @param {string} handHistory - Complete hand history text
   * @returns {Promise<string>} Analysis and advice
   */
  async analyzeHandHistory(handHistory) {
    const systemPrompt = `You are a professional poker coach analyzing hand histories. Break down the action street by street, identify mistakes, and suggest improvements based on game theory optimal play.`;
    
    const contents = [
      {
        role: 'user',
        parts: [
          {
            text: `${systemPrompt}\n\nPlease analyze this hand history:\n\n${handHistory}`,
          },
        ],
      },
    ];

    const response = await this.sendMessage(contents);
    return response.candidates[0].content.parts[0].text;
  }
}

export default GeminiClient;
