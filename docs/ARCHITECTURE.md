# Poker Therapist - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Poker Therapist UI                      │
│                         (Vue.js)                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐          ┌──────────────────┐          │
│  │  PokerCoachChat │          │ PokerHandAnalysis│          │
│  │   Component     │          │    Component     │          │
│  └────────┬────────┘          └──────────────────┘          │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────────────────────────────────┐            │
│  │          Vuex Store                          │            │
│  │  ┌──────────────┐  ┌────────────────────┐  │            │
│  │  │   chatbot    │  │   poker analysis   │  │            │
│  │  │    module    │  │       module       │  │            │
│  │  └──────┬───────┘  └────────────────────┘  │            │
│  └─────────┼─────────────────────────────────┘             │
│            │                                                  │
└────────────┼──────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                    ChatbotManager                            │
│                  (Unified Interface)                         │
└─────────────────────────────────────────────────────────────┘
             │
             ├───────────┬──────────┬──────────┬──────────┐
             ▼           ▼          ▼          ▼          │
┌──────────────┐ ┌──────────┐ ┌─────────┐ ┌─────────────┤
│ Perplexity   │ │  OpenAI  │ │ Claude  │ │   Gemini    │
│   Client     │ │  Client  │ │ Client  │ │   Client    │
└──────┬───────┘ └────┬─────┘ └────┬────┘ └──────┬──────┘
       │              │             │             │
       ▼              ▼             ▼             ▼
┌──────────────────────────────────────────────────────────┐
│                    External AI APIs                       │
│  ┌──────────┐  ┌────────┐  ┌─────────┐  ┌──────────┐   │
│  │Perplexity│  │OpenAI  │  │Anthropic│  │  Google  │   │
│  │   API    │  │  API   │  │   API   │  │   API    │   │
│  └──────────┘  └────────┘  └─────────┘  └──────────┘   │
└──────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. UI Layer (Vue Components)

#### PokerCoachChat.vue
- Interactive chat interface
- Message display with role-based styling
- Provider selection dropdown
- Image upload functionality
- Quick action buttons
- Real-time loading indicators

#### PokerHandAnalysis.vue
- Existing poker hand analysis dashboard
- Charts and tables
- Hand statistics

### 2. State Management (Vuex Store)

#### chatbot module (src/store/chatbot.js)
**State:**
- `messages[]` - Chat history
- `availableProviders[]` - List of configured AI providers
- `selectedProvider` - Currently active provider
- `conversationContext[]` - Recent conversation for context

**Actions:**
- `initializeChatbot()` - Initialize available providers
- `sendChatMessage()` - Send message and get AI response
- `setProvider()` - Switch between AI providers
- `clearChat()` - Clear conversation history

**Mutations:**
- `ADD_MESSAGE` - Add message to chat
- `SET_AVAILABLE_PROVIDERS` - Update provider list
- `SET_SELECTED_PROVIDER` - Change active provider
- `ADD_TO_CONTEXT` - Update conversation context

### 3. API Layer (Chatbot Clients)

#### ChatbotManager (src/api/chatbots/index.js)
Unified interface providing:
- Provider-agnostic methods
- Automatic provider selection
- Error handling
- Response normalization

Methods:
```javascript
getPokerAdvice(handDescription, situation, provider?)
analyzeHandHistory(handHistory, provider?)
analyzeHandImage(imageData, question, provider?)
analyzeHandWithImage(handDescription, imageData, provider?)
```

#### Individual Clients

**PerplexityClient** (perplexity.js)
- Text-only analysis
- Real-time research-backed advice
- Online model with latest information

**OpenAIClient** (openai.js)
- Text and image analysis
- GPT-4o multimodal support
- Advanced reasoning capabilities

**AnthropicClient** (anthropic.js)
- Text and image analysis
- Claude 3.5 Sonnet
- Deep analytical reasoning

**GeminiClient** (gemini.js)
- Text and image analysis
- Gemini 1.5 Pro
- Fast multimodal processing

## Data Flow

### Text Message Flow
```
1. User types message in PokerCoachChat
2. Component dispatches sendChatMessage action
3. Store calls ChatbotManager.getPokerAdvice()
4. Manager routes to selected provider client
5. Client calls external API
6. Response flows back through layers
7. Store commits ADD_MESSAGE mutation
8. Component re-renders with new message
```

### Image Analysis Flow
```
1. User uploads image + optional text
2. Component reads file as base64
3. Dispatches sendChatMessage with image data
4. Store calls ChatbotManager.analyzeHandWithImage()
5. Manager validates provider supports multimodal
6. Client sends multimodal request to API
7. Response includes image interpretation
8. Message added to chat history
```

## Configuration

### Environment Variables
```
VUE_APP_PERPLEXITY_API_KEY
VUE_APP_OPENAI_API_KEY
VUE_APP_ANTHROPIC_API_KEY
VUE_APP_GEMINI_API_KEY
```

### Provider Selection Logic
1. ChatbotManager initializes with configured API keys
2. Only providers with valid keys are available
3. Default provider is first available
4. User can switch providers via dropdown

## Error Handling

### Levels of Error Handling

1. **API Client Level**
   - Catches HTTP errors
   - Wraps errors with context
   - Throws descriptive errors

2. **Manager Level**
   - Catches client errors
   - Returns error response objects
   - Prevents UI crashes

3. **Store Level**
   - Catches manager errors
   - Adds error message to chat
   - Logs for debugging

4. **Component Level**
   - Shows loading states
   - Displays error messages
   - Allows retry

## Testing Strategy

### Unit Tests
- Individual client methods
- Manager routing logic
- Store mutations and actions
- Component methods

### Integration Tests
- Store + Manager interaction
- Component + Store integration
- End-to-end message flow

### Test Coverage
- API clients: 80%+
- Manager: 90%+
- Store: 85%+
- Components: 75%+

## Security Considerations

1. **API Keys**
   - Stored in environment variables
   - Never committed to repository
   - Loaded at build time

2. **User Input**
   - All inputs sanitized
   - No eval() or dangerous operations
   - Image size limits

3. **Rate Limiting**
   - Client-side throttling possible
   - Respect API limits
   - Show appropriate errors

4. **Data Privacy**
   - No data persisted to backend
   - Local storage only
   - User controls data

## Performance Optimizations

1. **Message Rendering**
   - Virtual scrolling for long chats
   - Lazy loading of images
   - Debounced input

2. **API Calls**
   - Single request per message
   - No redundant calls
   - Proper loading states

3. **State Management**
   - Limited context history (10 messages)
   - Efficient mutations
   - No unnecessary re-renders

## Future Enhancements

1. **Streaming Responses**
   - Real-time token streaming
   - Progressive message display
   - Better UX for long responses

2. **Conversation Memory**
   - Persist chat history
   - Resume conversations
   - Export/import chats

3. **Advanced Features**
   - Voice input support
   - Hand range calculator integration
   - Tournament-specific modes
   - Custom coaching personalities

4. **Performance**
   - Response caching
   - Prefetching common queries
   - Offline mode with local models
