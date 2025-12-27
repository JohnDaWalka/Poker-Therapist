<template>
  <div class="triage-view">
    <h2>Quick Triage</h2>
    
    <div class="form-group">
      <label>What's happening right now?</label>
      <textarea v-model="situation" rows="4" placeholder="Describe the situation..."></textarea>
    </div>
    
    <div class="form-group">
      <label>Emotion</label>
      <select v-model="emotion">
        <option>Anger</option>
        <option>Shame</option>
        <option>Fear</option>
        <option>Frustration</option>
        <option>Entitlement</option>
        <option>Boredom</option>
      </select>
    </div>
    
    <div class="form-group">
      <label>Intensity: {{ intensity }}/10</label>
      <input type="range" v-model.number="intensity" min="1" max="10" />
    </div>
    
    <div class="form-group">
      <label>Physical sensations (optional)</label>
      <input type="text" v-model="bodySensation" placeholder="e.g., Heart racing, tense shoulders" />
    </div>
    
    <div class="form-group">
      <label>
        <input type="checkbox" v-model="stillPlaying" />
        Still playing?
      </label>
    </div>
    
    <button @click="analyzeTriage" :disabled="isLoading || !situation" class="btn-primary">
      {{ isLoading ? 'Analyzing...' : 'Analyze' }}
    </button>
    
    <div v-if="result" class="results">
      <div class="severity" :class="severityClass">
        <h3>Severity: {{ result.severity }}/10</h3>
      </div>
      
      <div v-if="result.warning_message" class="warning">
        {{ result.warning_message }}
      </div>
      
      <div class="guidance">
        <h4>Guidance</h4>
        <p>{{ result.ai_guidance }}</p>
      </div>
      
      <div class="action-plan">
        <h4>Action Plan</h4>
        <ul>
          <li v-for="(action, index) in result.micro_plan" :key="index">{{ action }}</li>
        </ul>
      </div>
      
      <button @click="showBreathingExercise" class="btn-secondary">
        Practice Breathing Exercise
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import api from '../services/api'

export default {
  name: 'TriageView',
  setup() {
    const situation = ref('')
    const emotion = ref('Frustration')
    const intensity = ref(5)
    const bodySensation = ref('')
    const stillPlaying = ref(false)
    const isLoading = ref(false)
    const result = ref(null)
    
    const severityClass = computed(() => {
      if (!result.value) return ''
      const sev = result.value.severity
      if (sev >= 8) return 'severity-high'
      if (sev >= 5) return 'severity-medium'
      return 'severity-low'
    })
    
    const analyzeTriage = async () => {
      isLoading.value = true
      try {
        result.value = await api.analyzeTriage({
          situation: situation.value,
          emotion: emotion.value,
          intensity: intensity.value,
          body_sensation: bodySensation.value,
          still_playing: stillPlaying.value
        })
      } catch (error) {
        console.error('Triage error:', error)
        alert('Error analyzing triage. Please try again.')
      } finally {
        isLoading.value = false
      }
    }
    
    const showBreathingExercise = () => {
      // TODO: Show breathing exercise modal
      alert('Breathing exercise modal coming soon!')
    }
    
    return {
      situation,
      emotion,
      intensity,
      bodySensation,
      stillPlaying,
      isLoading,
      result,
      severityClass,
      analyzeTriage,
      showBreathingExercise
    }
  }
}
</script>

<style scoped>
.triage-view {
  max-width: 800px;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group textarea,
.form-group input[type="text"],
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input[type="range"] {
  width: 100%;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #42b983;
  color: white;
}

.btn-primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #2c3e50;
  color: white;
  margin-top: 1rem;
}

.results {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.severity {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.severity-low { background-color: #d4edda; color: #155724; }
.severity-medium { background-color: #fff3cd; color: #856404; }
.severity-high { background-color: #f8d7da; color: #721c24; }

.warning {
  background-color: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-weight: 500;
}

.guidance,
.action-plan {
  margin-bottom: 1rem;
}

.action-plan ul {
  list-style-position: inside;
}
</style>
