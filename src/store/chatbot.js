import { ChatbotManager, ChatbotProvider } from '../../api/chatbots';

// Initialize chatbot manager with API keys from environment or config
const chatbotManager = new ChatbotManager({
  perplexityApiKey: process.env.VUE_APP_PERPLEXITY_API_KEY,
  openaiApiKey: process.env.VUE_APP_OPENAI_API_KEY,
  anthropicApiKey: process.env.VUE_APP_ANTHROPIC_API_KEY,
  geminiApiKey: process.env.VUE_APP_GEMINI_API_KEY,
  defaultProvider: ChatbotProvider.PERPLEXITY,
});

const state = {
  messages: [],
  availableProviders: [],
  selectedProvider: ChatbotProvider.PERPLEXITY,
  isInitialized: false,
  conversationContext: [],
};

const mutations = {
  ADD_MESSAGE(state, message) {
    state.messages.push({
      ...message,
      timestamp: message.timestamp || new Date(),
    });
  },
  
  SET_AVAILABLE_PROVIDERS(state, providers) {
    state.availableProviders = providers;
  },
  
  SET_SELECTED_PROVIDER(state, provider) {
    state.selectedProvider = provider;
  },
  
  SET_INITIALIZED(state, value) {
    state.isInitialized = value;
  },
  
  ADD_TO_CONTEXT(state, contextItem) {
    state.conversationContext.push(contextItem);
    // Keep only last 10 messages for context
    if (state.conversationContext.length > 10) {
      state.conversationContext.shift();
    }
  },
  
  CLEAR_MESSAGES(state) {
    state.messages = [];
    state.conversationContext = [];
  },
};

const actions = {
  /**
   * Initialize the chatbot system
   */
  initializeChatbot({ commit, state }) {
    if (state.isInitialized) {
      return;
    }
    
    const providers = chatbotManager.getAvailableProviders();
    commit('SET_AVAILABLE_PROVIDERS', providers);
    
    // Set default provider to first available if current is not available
    if (providers.length > 0 && !providers.includes(state.selectedProvider)) {
      commit('SET_SELECTED_PROVIDER', providers[0]);
    }
    
    commit('SET_INITIALIZED', true);
  },
  
  /**
   * Send a chat message to the AI coach
   */
  async sendChatMessage({ commit, state }, messageData) {
    // Add user message to chat
    const userMessage = {
      role: 'user',
      content: messageData.content,
      image: messageData.image,
      timestamp: messageData.timestamp || new Date(),
    };
    commit('ADD_MESSAGE', userMessage);
    
    try {
      let response;
      
      // Determine which API method to use based on message content
      if (messageData.image && messageData.content) {
        // Text + image analysis
        response = await chatbotManager.analyzeHandWithImage(
          messageData.content,
          messageData.image,
          state.selectedProvider
        );
      } else if (messageData.image) {
        // Image only analysis
        response = await chatbotManager.analyzeHandImage(
          messageData.image,
          'Analyze this poker hand and provide strategic advice.',
          state.selectedProvider
        );
      } else if (messageData.content.toLowerCase().includes('hand history')) {
        // Hand history analysis
        response = await chatbotManager.analyzeHandHistory(
          messageData.content,
          state.selectedProvider
        );
      } else {
        // General poker advice
        response = await chatbotManager.getPokerAdvice(
          messageData.content,
          'Provide strategic poker coaching advice.',
          state.selectedProvider
        );
      }
      
      if (response.success) {
        const assistantMessage = {
          role: 'assistant',
          content: response.advice || response.analysis,
          provider: response.provider,
          timestamp: new Date(),
        };
        commit('ADD_MESSAGE', assistantMessage);
        
        // Add to conversation context
        commit('ADD_TO_CONTEXT', {
          user: messageData.content,
          assistant: response.advice || response.analysis,
        });
      } else {
        const errorMessage = {
          role: 'assistant',
          content: `I'm sorry, I encountered an error: ${response.error}. Please try again or select a different AI provider.`,
          provider: response.provider,
          timestamp: new Date(),
          isError: true,
        };
        commit('ADD_MESSAGE', errorMessage);
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `I'm sorry, something went wrong. Please try again. Error: ${error.message}`,
        timestamp: new Date(),
        isError: true,
      };
      commit('ADD_MESSAGE', errorMessage);
      throw error;
    }
  },
  
  /**
   * Change the selected AI provider
   */
  setProvider({ commit, state }, provider) {
    if (!chatbotManager.isProviderAvailable(provider)) {
      console.error(`Provider ${provider} is not available`);
      return;
    }
    commit('SET_SELECTED_PROVIDER', provider);
  },
  
  /**
   * Clear chat history
   */
  clearChat({ commit }) {
    commit('CLEAR_MESSAGES');
  },
};

const getters = {
  messages: (state) => state.messages,
  availableProviders: (state) => state.availableProviders,
  selectedProvider: (state) => state.selectedProvider,
  isInitialized: (state) => state.isInitialized,
  conversationContext: (state) => state.conversationContext,
  lastMessage: (state) => {
    return state.messages.length > 0 
      ? state.messages[state.messages.length - 1] 
      : null;
  },
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
};
