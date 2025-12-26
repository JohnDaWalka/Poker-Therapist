import { shallowMount, createLocalVue } from '@vue/test-utils';
import Vuex from 'vuex';
import PokerCoachChat from '@/components/PokerCoachChat.vue';

const localVue = createLocalVue();
localVue.use(Vuex);

describe('PokerCoachChat.vue', () => {
  let store;
  let actions;
  let getters;
  let wrapper;

  beforeEach(() => {
    actions = {
      sendChatMessage: jest.fn(),
      setProvider: jest.fn(),
      initializeChatbot: jest.fn(),
    };

    getters = {
      messages: () => [
        {
          role: 'user',
          content: 'What should I do with pocket aces?',
          timestamp: new Date('2024-01-01T12:00:00'),
        },
        {
          role: 'assistant',
          content: 'Pocket aces are the strongest starting hand. You should raise pre-flop.',
          timestamp: new Date('2024-01-01T12:00:05'),
        },
      ],
      availableProviders: () => ['perplexity', 'openai', 'anthropic'],
      selectedProvider: () => 'perplexity',
    };

    store = new Vuex.Store({
      modules: {
        chatbot: {
          namespaced: true,
          actions,
          getters,
        },
      },
    });

    wrapper = shallowMount(PokerCoachChat, {
      store,
      localVue,
    });
  });

  afterEach(() => {
    wrapper.destroy();
  });

  describe('Component initialization', () => {
    it('renders the component', () => {
      expect(wrapper.exists()).toBe(true);
    });

    it('initializes chatbot on mount', () => {
      expect(actions.initializeChatbot).toHaveBeenCalled();
    });

    it('displays the chat header', () => {
      expect(wrapper.find('.chat-header h2').text()).toContain('Poker Coach AI');
    });
  });

  describe('Messages display', () => {
    it('displays messages from store', () => {
      const messages = wrapper.findAll('.message');
      expect(messages.length).toBe(2);
    });

    it('displays user message correctly', () => {
      const userMessage = wrapper.find('.message.user');
      expect(userMessage.exists()).toBe(true);
      expect(userMessage.find('.message-text').text()).toContain('What should I do with pocket aces?');
    });

    it('displays assistant message correctly', () => {
      const assistantMessage = wrapper.find('.message.assistant');
      expect(assistantMessage.exists()).toBe(true);
      expect(assistantMessage.find('.message-text').text()).toContain('Pocket aces are the strongest');
    });
  });

  describe('Provider selection', () => {
    it('displays provider dropdown', () => {
      const select = wrapper.find('#chatbot-provider');
      expect(select.exists()).toBe(true);
    });

    it('shows available providers in dropdown', () => {
      const options = wrapper.findAll('#chatbot-provider option');
      expect(options.length).toBe(3);
      expect(options.at(0).text()).toContain('Perplexity');
      expect(options.at(1).text()).toContain('OpenAI');
      expect(options.at(2).text()).toContain('Claude');
    });

    it('calls setProvider when provider changes', async () => {
      const select = wrapper.find('#chatbot-provider');
      select.element.value = 'openai';
      await select.trigger('change');

      expect(actions.setProvider).toHaveBeenCalled();
    });
  });

  describe('Sending messages', () => {
    it('sends message when send button is clicked', async () => {
      wrapper.setData({ userInput: 'Test message' });
      await wrapper.vm.$nextTick();

      const sendButton = wrapper.find('.send-btn');
      await sendButton.trigger('click');

      expect(actions.sendChatMessage).toHaveBeenCalled();
    });

    it('clears input after sending message', async () => {
      wrapper.setData({ userInput: 'Test message' });
      await wrapper.vm.$nextTick();

      await wrapper.vm.sendMessage();
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.userInput).toBe('');
    });

    it('disables send button when input is empty', () => {
      wrapper.setData({ userInput: '' });
      const sendButton = wrapper.find('.send-btn');
      expect(sendButton.attributes('disabled')).toBe('disabled');
    });

    it('enables send button when input has text', async () => {
      wrapper.setData({ userInput: 'Test message' });
      await wrapper.vm.$nextTick();

      const sendButton = wrapper.find('.send-btn');
      expect(sendButton.attributes('disabled')).toBeUndefined();
    });
  });

  describe('Image upload', () => {
    it('displays image upload button', () => {
      const uploadBtn = wrapper.find('.image-upload-btn');
      expect(uploadBtn.exists()).toBe(true);
    });

    it('shows image preview when image is selected', async () => {
      wrapper.setData({ selectedImage: 'data:image/jpeg;base64,/9j/4AAQ...' });
      await wrapper.vm.$nextTick();

      const preview = wrapper.find('.image-preview');
      expect(preview.exists()).toBe(true);
    });

    it('clears image when clear button is clicked', async () => {
      wrapper.setData({ selectedImage: 'data:image/jpeg;base64,/9j/4AAQ...' });
      await wrapper.vm.$nextTick();

      const clearBtn = wrapper.find('.clear-image-btn');
      await clearBtn.trigger('click');

      expect(wrapper.vm.selectedImage).toBeNull();
    });
  });

  describe('Quick actions', () => {
    it('displays quick action buttons', () => {
      const quickBtns = wrapper.findAll('.quick-btn');
      expect(quickBtns.length).toBe(3);
    });

    it('sets input text when quick action is clicked', async () => {
      const analyzeBtn = wrapper.findAll('.quick-btn').at(0);
      await analyzeBtn.trigger('click');

      expect(wrapper.vm.userInput).toContain('analyze');
    });

    it('disables quick actions when loading', async () => {
      wrapper.setData({ isLoading: true });
      await wrapper.vm.$nextTick();

      const quickBtns = wrapper.findAll('.quick-btn');
      quickBtns.wrappers.forEach((btn) => {
        expect(btn.attributes('disabled')).toBe('disabled');
      });
    });
  });

  describe('Loading state', () => {
    it('shows loading indicator when isLoading is true', async () => {
      wrapper.setData({ isLoading: true });
      await wrapper.vm.$nextTick();

      const loadingIndicator = wrapper.find('.typing-indicator');
      expect(loadingIndicator.exists()).toBe(true);
    });

    it('disables inputs when loading', async () => {
      wrapper.setData({ isLoading: true });
      await wrapper.vm.$nextTick();

      const textarea = wrapper.find('textarea');
      const sendBtn = wrapper.find('.send-btn');
      const providerSelect = wrapper.find('#chatbot-provider');

      expect(textarea.attributes('disabled')).toBe('disabled');
      expect(sendBtn.attributes('disabled')).toBe('disabled');
      expect(providerSelect.attributes('disabled')).toBe('disabled');
    });
  });

  describe('Helper methods', () => {
    it('formats provider name correctly', () => {
      expect(wrapper.vm.formatProviderName('perplexity')).toBe('Perplexity AI');
      expect(wrapper.vm.formatProviderName('openai')).toBe('OpenAI GPT-4');
      expect(wrapper.vm.formatProviderName('anthropic')).toBe('Claude (Anthropic)');
      expect(wrapper.vm.formatProviderName('gemini')).toBe('Google Gemini');
    });

    it('formats time correctly', () => {
      const timestamp = new Date('2024-01-01T12:34:56');
      const formatted = wrapper.vm.formatTime(timestamp);
      expect(formatted).toMatch(/\d{1,2}:\d{2}/);
    });
  });
});
