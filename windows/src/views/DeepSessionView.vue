<template>
  <div class="deep-session-view">
    <div class="chat-container">
      <div class="chat-messages" ref="chatContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role]"
        >
          <div class="message-content">{{ message.content }}</div>
          <div class="message-timestamp">{{ message.timestamp }}</div>
        </div>
        <div v-if="isTyping" class="message assistant">
          <div class="typing-animation">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
      <div class="chat-input">
        <textarea
          v-model="userInput"
          @keydown.enter.prevent="sendMessage"
          placeholder="Type your message..."
          rows="3"
        ></textarea>
        <button @click="sendMessage" :disabled="!userInput.trim() || isTyping">
          Send
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue';
import api from '../services/api';

export default {
  name: 'DeepSessionView',
  setup() {
    const messages = ref([
      {
        role: 'assistant',
        content: 'Welcome to Deep Session Analysis. How can I help you analyze your poker session today?',
        timestamp: new Date().toLocaleTimeString()
      }
    ]);
    const userInput = ref('');
    const isTyping = ref(false);
    const chatContainer = ref(null);

    const scrollToBottom = async () => {
      await nextTick();
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
      }
    };

    const sendMessage = async () => {
      if (!userInput.value.trim() || isTyping.value) return;

      const userMessage = {
        role: 'user',
        content: userInput.value,
        timestamp: new Date().toLocaleTimeString()
      };

      messages.value.push(userMessage);
      const messageContent = userInput.value;
      userInput.value = '';
      
      await scrollToBottom();
      isTyping.value = true;

      try {
        const response = await api.startDeepSession({
          message: messageContent,
          history: messages.value
        });

        const assistantMessage = {
          role: 'assistant',
          content: response.data.message || response.data.response,
          timestamp: new Date().toLocaleTimeString()
        };

        messages.value.push(assistantMessage);
      } catch (error) {
        const errorMessage = {
          role: 'assistant',
          content: 'Sorry, there was an error processing your request. Please try again.',
          timestamp: new Date().toLocaleTimeString()
        };
        messages.value.push(errorMessage);
        console.error('Error sending message:', error);
      } finally {
        isTyping.value = false;
        await scrollToBottom();
      }
    };

    return {
      messages,
      userInput,
      isTyping,
      chatContainer,
      scrollToBottom,
      sendMessage
    };
  }
};
</script>

<style scoped>
.deep-session-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
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
  display: flex;
  flex-direction: column;
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  animation: fadeIn 0.3s ease-in;
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

.message.user {
  align-self: flex-end;
  background-color: #007bff;
  color: white;
}

.message.assistant {
  align-self: flex-start;
  background-color: #f1f3f5;
  color: #333;
}

.message-content {
  margin-bottom: 4px;
  word-wrap: break-word;
}

.message-timestamp {
  font-size: 0.75rem;
  opacity: 0.7;
  align-self: flex-end;
}

.typing-animation {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-animation span {
  width: 8px;
  height: 8px;
  background-color: #666;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-animation span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-animation span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.chat-input {
  display: flex;
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  gap: 12px;
  background: #fafafa;
}

.chat-input textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-family: inherit;
  font-size: 14px;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input textarea:focus {
  border-color: #007bff;
}

.chat-input button {
  padding: 12px 24px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.chat-input button:hover:not(:disabled) {
  background-color: #0056b3;
}

.chat-input button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
