<template>
  <div class="poker-coach-chat">
    <div class="chat-header">
      <h2>🎰 Poker Coach AI</h2>
      <div class="provider-selector">
        <label for="chatbot-provider">AI Provider:</label>
        <select 
          id="chatbot-provider" 
          v-model="selectedProvider" 
          @change="onProviderChange"
          :disabled="isLoading"
        >
          <option 
            v-for="provider in availableProviders" 
            :key="provider" 
            :value="provider"
          >
            {{ formatProviderName(provider) }}
          </option>
        </select>
      </div>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div 
        v-for="(message, index) in messages" 
        :key="index" 
        :class="['message', message.role]"
      >
        <div class="message-header">
          <span class="message-role">{{ message.role === 'user' ? 'You' : 'Coach' }}</span>
          <span class="message-time">{{ formatTime(message.timestamp) }}</span>
        </div>
        <div class="message-content">
          <div v-if="message.image" class="message-image">
            <img :src="message.image" alt="Poker hand" />
          </div>
          <div class="message-text">{{ message.content }}</div>
        </div>
      </div>
      
      <div v-if="isLoading" class="message assistant loading">
        <div class="message-header">
          <span class="message-role">Coach</span>
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <div v-if="selectedImage" class="image-preview">
        <img :src="selectedImage" alt="Selected image" />
        <button @click="clearImage" class="clear-image-btn">×</button>
      </div>
      
      <div class="input-controls">
        <label for="image-upload" class="image-upload-btn" title="Upload hand screenshot">
          📷
          <input 
            id="image-upload" 
            type="file" 
            accept="image/*" 
            @change="onImageSelect"
            style="display: none;"
          />
        </label>
        
        <textarea
          v-model="userInput"
          @keydown.enter.prevent="onEnterPress"
          placeholder="Describe your poker hand or ask a question..."
          rows="3"
          :disabled="isLoading"
        ></textarea>
        
        <button 
          @click="sendMessage" 
          :disabled="isLoading || !userInput.trim()"
          class="send-btn"
        >
          Send
        </button>
      </div>
      
      <div class="quick-actions">
        <button 
          @click="quickAction('analyze')" 
          :disabled="isLoading"
          class="quick-btn"
        >
          Analyze Hand
        </button>
        <button 
          @click="quickAction('strategy')" 
          :disabled="isLoading"
          class="quick-btn"
        >
          GTO Strategy
        </button>
        <button 
          @click="quickAction('odds')" 
          :disabled="isLoading"
          class="quick-btn"
        >
          Calculate Odds
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'PokerCoachChat',
  data() {
    return {
      userInput: '',
      selectedImage: null,
      selectedImageFile: null,
      isLoading: false,
    };
  },
  computed: {
    ...mapGetters('chatbot', [
      'messages',
      'availableProviders',
      'selectedProvider',
    ]),
  },
  methods: {
    ...mapActions('chatbot', [
      'sendChatMessage',
      'setProvider',
      'initializeChatbot',
    ]),
    
    async sendMessage() {
      if (!this.userInput.trim() && !this.selectedImage) {
        return;
      }

      const messageData = {
        content: this.userInput.trim(),
        image: this.selectedImage,
        timestamp: new Date(),
      };

      this.isLoading = true;
      
      try {
        await this.sendChatMessage(messageData);
        this.userInput = '';
        this.clearImage();
        this.scrollToBottom();
      } catch (error) {
        console.error('Error sending message:', error);
        // Could add error notification here
      } finally {
        this.isLoading = false;
      }
    },
    
    onEnterPress(event) {
      if (!event.shiftKey) {
        this.sendMessage();
      } else {
        // Allow shift+enter for new lines
        this.userInput += '\n';
      }
    },
    
    onImageSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedImageFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
          this.selectedImage = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    
    clearImage() {
      this.selectedImage = null;
      this.selectedImageFile = null;
    },
    
    onProviderChange() {
      this.setProvider(this.selectedProvider);
    },
    
    quickAction(action) {
      const prompts = {
        analyze: 'Please analyze my last hand and tell me if I played it optimally.',
        strategy: 'What is the GTO (Game Theory Optimal) strategy for this situation?',
        odds: 'Can you help me calculate the pot odds and equity for this hand?',
      };
      
      this.userInput = prompts[action] || '';
    },
    
    formatProviderName(provider) {
      const names = {
        perplexity: 'Perplexity AI',
        openai: 'OpenAI GPT-4',
        anthropic: 'Claude (Anthropic)',
        gemini: 'Google Gemini',
      };
      return names[provider] || provider;
    },
    
    formatTime(timestamp) {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },
  },
  mounted() {
    this.initializeChatbot();
    this.scrollToBottom();
  },
  updated() {
    this.scrollToBottom();
  },
};
</script>

<style scoped>
.poker-coach-chat {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-height: 800px;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: #f9f9f9;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.provider-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.provider-selector label {
  font-size: 0.9rem;
}

.provider-selector select {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  background: white;
  color: #333;
  font-size: 0.9rem;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  animation: fadeIn 0.3s ease-in;
}

.message.user {
  align-self: flex-end;
  background: #667eea;
  color: white;
  margin-left: auto;
}

.message.assistant {
  align-self: flex-start;
  background: white;
  color: #333;
  border: 1px solid #e0e0e0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.85rem;
  opacity: 0.8;
}

.message-content {
  line-height: 1.5;
}

.message-image {
  margin-bottom: 12px;
}

.message-image img {
  max-width: 100%;
  border-radius: 8px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

.chat-input-area {
  background: white;
  padding: 16px;
  border-top: 1px solid #ddd;
}

.image-preview {
  position: relative;
  margin-bottom: 12px;
}

.image-preview img {
  max-width: 150px;
  max-height: 150px;
  border-radius: 8px;
  border: 2px solid #667eea;
}

.clear-image-btn {
  position: absolute;
  top: -8px;
  right: calc(100% - 150px - 8px);
  background: #ff4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}

.input-controls {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.image-upload-btn {
  font-size: 24px;
  cursor: pointer;
  padding: 8px;
  background: #f0f0f0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.image-upload-btn:hover {
  background: #e0e0e0;
}

textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: none;
  font-family: inherit;
  font-size: 0.95rem;
}

textarea:focus {
  outline: none;
  border-color: #667eea;
}

.send-btn {
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #5568d3;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.quick-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.quick-btn {
  padding: 8px 16px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.quick-btn:hover:not(:disabled) {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.quick-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}
</style>
