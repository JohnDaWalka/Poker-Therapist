<template>
  <div id="app">
    <div class="app-header">
      <h1>🎰 Poker Therapist</h1>
      <div class="view-toggle">
        <button 
          @click="currentView = 'analysis'" 
          :class="{ active: currentView === 'analysis' }"
        >
          Hand Analysis
        </button>
        <button 
          @click="currentView = 'coach'" 
          :class="{ active: currentView === 'coach' }"
        >
          AI Coach
        </button>
      </div>
    </div>
    
    <div class="app-content">
      <PokerHandAnalysis v-if="currentView === 'analysis'" />
      <PokerCoachChat v-if="currentView === 'coach'" />
    </div>
  </div>
</template>

<script>
import PokerHandAnalysis from './components/PokerHandAnalysis.vue';
import PokerCoachChat from './components/PokerCoachChat.vue';

export default {
  name: 'App',
  components: {
    PokerHandAnalysis,
    PokerCoachChat,
  },
  data() {
    return {
      currentView: 'coach', // Default to coach view to showcase new feature
    };
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin: 0 0 16px 0;
  font-size: 2rem;
}

.view-toggle {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.view-toggle button {
  padding: 10px 24px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.view-toggle button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.view-toggle button.active {
  background: white;
  color: #667eea;
  border-color: white;
}

.app-content {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}
</style>
