<template>
  <div class="hand-analysis-view">
    <div class="container">
      <h2>Hand Analysis</h2>
      <div class="input-section">
        <div class="form-group">
          <label>Hand History</label>
          <textarea v-model="handHistory" rows="10" placeholder="Paste hand history..."></textarea>
        </div>
        <div class="controls">
          <select v-model="gameType">
            <option value="nlhe">NL Hold'em</option>
            <option value="plo">PLO</option>
            <option value="mtt">MTT</option>
          </select>
          <button @click="analyze" :disabled="!handHistory || loading">
            {{ loading ? 'Analyzing...' : 'Analyze' }}
          </button>
        </div>
      </div>
      <div v-if="result" class="results">
        <h3>Results</h3>
        <p>{{ result.analysis }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import api from '../services/api';

export default {
  name: 'HandAnalysisView',
  setup() {
    const handHistory = ref('');
    const gameType = ref('nlhe');
    const loading = ref(false);
    const result = ref(null);

    const analyze = async () => {
      loading.value = true;
      try {
        const res = await api.analyzeHand({ history: handHistory.value, type: gameType.value });
        result.value = res;
      } catch (e) {
        console.error('Failed to analyze hand:', e);
      } finally {
        loading.value = false;
      }
    };

    return { handHistory, gameType, loading, result, analyze };
  }
};
</script>

<style scoped>
.hand-analysis-view { padding: 20px; }
.container { max-width: 900px; margin: 0 auto; }
textarea { width: 100%; padding: 10px; font-family: monospace; }
.controls { display: flex; gap: 10px; margin-top: 10px; }
button { padding: 10px 20px; background: #42b983; color: white; border: none; cursor: pointer; }
button:disabled { opacity: 0.5; }
</style>
