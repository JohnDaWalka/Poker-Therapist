<template>
  <div class="voice-recorder" :class="{ 'recording': isRecording, 'processing': isProcessing }">
    <!-- Header -->
    <div class="recorder-header">
      <h2 class="title">
        <span class="rex-icon">🦖</span>
        Therapy Rex Voice Session
      </h2>
      <div v-if="urgencyLevel" class="urgency-alert" :class="`urgency-${urgencyLevel}`">
        <span class="alert-icon">⚠️</span>
        {{ urgencyMessages[urgencyLevel] }}
      </div>
    </div>

    <!-- Recording Controls -->
    <div class="recording-section">
      <div class="visualizer" v-if="isRecording">
        <div 
          v-for="(bar, index) in visualizerBars" 
          :key="index"
          class="visualizer-bar"
          :style="{ height: bar + '%' }"
        ></div>
      </div>

      <div class="controls">
        <button 
          @click="startRecording" 
          v-if="!isRecording && !isProcessing"
          class="btn btn-primary btn-record"
          :disabled="!isSupported"
        >
          <span class="btn-icon">🎤</span>
          Start Recording
        </button>

        <button 
          @click="stopRecording" 
          v-if="isRecording"
          class="btn btn-danger btn-stop"
        >
          <span class="btn-icon">⏹️</span>
          Stop Recording
        </button>

        <div v-if="isRecording" class="recording-timer">
          {{ formatTime(recordingTime) }}
        </div>
      </div>

      <div v-if="!isSupported" class="error-message">
        <span class="error-icon">❌</span>
        Your browser doesn't support audio recording. Please use a modern browser.
      </div>

      <div v-if="error" class="error-message">
        <span class="error-icon">❌</span>
        {{ error }}
      </div>
    </div>

    <!-- 4-7-8 Breathing Protocol -->
    <div v-if="showBreathingProtocol" class="breathing-protocol">
      <h3 class="protocol-title">🌬️ 4-7-8 Breathing Exercise</h3>
      <div class="breathing-animation">
        <div class="breath-circle" :class="breathPhase">
          <div class="breath-text">{{ breathText }}</div>
          <div class="breath-count">{{ breathCount }}</div>
        </div>
      </div>
      <div class="protocol-instructions">
        <p><strong>Inhale</strong> through nose (4 seconds)</p>
        <p><strong>Hold</strong> your breath (7 seconds)</p>
        <p><strong>Exhale</strong> through mouth (8 seconds)</p>
      </div>
      <button @click="toggleBreathing" class="btn btn-secondary">
        {{ isBreathing ? 'Stop' : 'Start' }} Breathing Exercise
      </button>
    </div>

    <!-- Response Display with Tilt-Based Rendering -->
    <div v-if="response" class="response-section">
      <div class="response-header">
        <h3>🦖 Rex's Response</h3>
        <div class="tilt-indicator" :class="`tilt-${tiltSeverity}`">
          Tilt Level: {{ tiltSeverity.toUpperCase() }}
        </div>
      </div>

      <div class="response-content" :class="`tilt-${tiltSeverity}`">
        <div class="response-text" v-html="formattedResponse"></div>
        
        <!-- Tilt-Based Recommendations -->
        <div class="tilt-recommendations">
          <h4>{{ tiltRecommendations[tiltSeverity]?.title }}</h4>
          <ul>
            <li v-for="(rec, index) in tiltRecommendations[tiltSeverity]?.items" :key="index">
              {{ rec }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Rex Signature Closers -->
      <div class="rex-closers">
        <div class="closer-message">{{ getRandomCloser() }}</div>
        <div class="rex-signature">
          <span class="signature-icon">🦖</span>
          <span class="signature-text">- Therapy Rex</span>
        </div>
      </div>
    </div>

    <!-- Audio Playback -->
    <div v-if="audioUrl" class="playback-section">
      <h4>Your Recording:</h4>
      <audio :src="audioUrl" controls class="audio-player"></audio>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VoiceRecorder',
  
  data() {
    return {
      // Recording state
      isRecording: false,
      isProcessing: false,
      isSupported: false,
      mediaRecorder: null,
      audioChunks: [],
      audioUrl: null,
      recordingTime: 0,
      recordingTimer: null,
      
      // Visualizer
      visualizerBars: Array(20).fill(10),
      visualizerInterval: null,
      audioContext: null,
      analyser: null,
      
      // Response data
      response: null,
      tiltSeverity: 'low',
      urgencyLevel: null,
      
      // Breathing protocol
      showBreathingProtocol: true,
      isBreathing: false,
      breathPhase: 'inhale',
      breathCount: 4,
      breathTimer: null,
      breathText: 'Inhale',
      
      // Error handling
      error: null,
      
      // Constants
      urgencyMessages: {
        low: '✅ Stable - Continue monitoring',
        medium: '⚠️ Elevated tilt detected - Consider a break',
        high: '🚨 HIGH ALERT - Immediate intervention recommended',
        critical: '🆘 CRITICAL - Stop playing NOW'
      },
      
      tiltRecommendations: {
        low: {
          title: '✅ You\'re Playing Well',
          items: [
            'Maintain your current mindset',
            'Stay aware of variance',
            'Keep reviewing hands objectively',
            'Remember to take regular breaks'
          ]
        },
        medium: {
          title: '⚠️ Warning Signs Detected',
          items: [
            'Take a 10-minute break',
            'Review your recent decisions',
            'Practice 4-7-8 breathing exercise',
            'Consider ending session if it persists',
            'Stay hydrated and eat something'
          ]
        },
        high: {
          title: '🚨 High Tilt State',
          items: [
            'STOP PLAYING immediately for 30 minutes',
            'Do 5 rounds of 4-7-8 breathing',
            'Go for a walk or physical activity',
            'Journal about what triggered you',
            'Don\'t return until calm and centered'
          ]
        },
        critical: {
          title: '🆘 Critical Intervention Required',
          items: [
            'END YOUR SESSION NOW',
            'Close all poker tables immediately',
            'Step away from the computer',
            'Call a friend or support person',
            'Do not play again today',
            'Schedule session review with coach'
          ]
        }
      },
      
      rexClosers: [
        'Remember: even T-Rex had short arms, but he adapted. You got this! 🦖',
        'Variance is temporary, bankroll management is forever. Rawr! 🦖',
        'You\'re not tilting, you\'re just recalibrating. Take care! 🦖',
        'Every fold is a decision, every decision is progress. Keep roaring! 🦖',
        'Bad beats happen to everyone. Even dinosaurs. Stay strong! 🦖',
        'Your mental game is your edge. Protect it like a T-Rex protects its territory! 🦖',
        'Take breaks, stay hydrated, crush it. That\'s the Rex way! 🦖',
        'Poker is a marathon, not a sprint. Pace yourself, champion! 🦖',
        'You came here for help, and that\'s already a winning decision. 🦖',
        'One session at a time. One hand at a time. You\'re doing great! 🦖'
      ]
    };
  },
  
  computed: {
    formattedResponse() {
      if (!this.response) return '';
      // Convert markdown-style formatting to HTML
      return this.response
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/- (.*?)(?=<br>|$)/g, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    }
  },
  
  mounted() {
    this.checkMediaRecorderSupport();
  },
  
  beforeUnmount() {
    this.cleanup();
  },
  
  methods: {
    checkMediaRecorderSupport() {
      this.isSupported = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    },
    
    async startRecording() {
      try {
        this.error = null;
        this.audioChunks = [];
        this.recordingTime = 0;
        
        const stream = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            sampleRate: 44100
          } 
        });
        
        // Setup MediaRecorder
        const mimeType = MediaRecorder.isTypeSupported('audio/webm') 
          ? 'audio/webm' 
          : 'audio/mp4';
        
        this.mediaRecorder = new MediaRecorder(stream, { mimeType });
        
        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };
        
        this.mediaRecorder.onstop = () => {
          this.handleRecordingStop();
        };
        
        // Setup visualizer
        this.setupVisualizer(stream);
        
        // Start recording
        this.mediaRecorder.start(100);
        this.isRecording = true;
        
        // Start timer
        this.recordingTimer = setInterval(() => {
          this.recordingTime++;
        }, 1000);
        
      } catch (err) {
        console.error('Error starting recording:', err);
        this.error = 'Failed to access microphone. Please check permissions.';
      }
    },
    
    setupVisualizer(stream) {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      const source = this.audioContext.createMediaStreamSource(stream);
      source.connect(this.analyser);
      this.analyser.fftSize = 64;
      
      const bufferLength = this.analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      this.visualizerInterval = setInterval(() => {
        this.analyser.getByteFrequencyData(dataArray);
        this.visualizerBars = Array.from(dataArray)
          .slice(0, 20)
          .map(value => (value / 255) * 100);
      }, 50);
    },
    
    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.mediaRecorder.stop();
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        this.isRecording = false;
        
        if (this.recordingTimer) {
          clearInterval(this.recordingTimer);
        }
        
        if (this.visualizerInterval) {
          clearInterval(this.visualizerInterval);
        }
        
        if (this.audioContext) {
          this.audioContext.close();
        }
      }
    },
    
    async handleRecordingStop() {
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
      this.audioUrl = URL.createObjectURL(audioBlob);
      
      // Upload to API
      await this.uploadAudio(audioBlob);
    },
    
    async uploadAudio(audioBlob) {
      try {
        this.isProcessing = true;
        this.error = null;
        
        const formData = new FormData();
        formData.append('audio', audioBlob, 'voice-recording.webm');
        formData.append('timestamp', new Date().toISOString());
        
        const response = await fetch('/api/v1/therapy/voice', {
          method: 'POST',
          body: formData,
          headers: {
            'Accept': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        this.handleResponse(data);
        
      } catch (err) {
        console.error('Error uploading audio:', err);
        this.error = 'Failed to upload recording. Please try again.';
      } finally {
        this.isProcessing = false;
      }
    },
    
    handleResponse(data) {
      this.response = data.response || data.message || 'Response received';
      
      // Determine tilt severity from response
      this.tiltSeverity = data.tiltLevel || this.analyzeTiltFromResponse(data);
      
      // Set urgency level
      this.urgencyLevel = this.mapTiltToUrgency(this.tiltSeverity);
      
      // Show breathing protocol for medium+ tilt
      if (['medium', 'high', 'critical'].includes(this.tiltSeverity)) {
        this.showBreathingProtocol = true;
      }
      
      // Emit event for parent component
      this.$emit('response-received', {
        response: this.response,
        tiltLevel: this.tiltSeverity,
        urgency: this.urgencyLevel
      });
    },
    
    analyzeTiltFromResponse(data) {
      const text = (data.response || '').toLowerCase();
      
      if (text.includes('critical') || text.includes('stop playing')) {
        return 'critical';
      } else if (text.includes('high tilt') || text.includes('take a break')) {
        return 'high';
      } else if (text.includes('warning') || text.includes('elevated')) {
        return 'medium';
      }
      return 'low';
    },
    
    mapTiltToUrgency(tiltLevel) {
      const mapping = {
        low: 'low',
        medium: 'medium',
        high: 'high',
        critical: 'critical'
      };
      return mapping[tiltLevel] || 'low';
    },
    
    // Breathing Protocol Methods
    toggleBreathing() {
      if (this.isBreathing) {
        this.stopBreathing();
      } else {
        this.startBreathing();
      }
    },
    
    startBreathing() {
      this.isBreathing = true;
      this.breathPhase = 'inhale';
      this.breathCount = 4;
      this.breathText = 'Inhale';
      this.runBreathingCycle();
    },
    
    stopBreathing() {
      this.isBreathing = false;
      if (this.breathTimer) {
        clearTimeout(this.breathTimer);
      }
    },
    
    runBreathingCycle() {
      if (!this.isBreathing) return;
      
      const phases = [
        { name: 'inhale', duration: 4, text: 'Inhale' },
        { name: 'hold', duration: 7, text: 'Hold' },
        { name: 'exhale', duration: 8, text: 'Exhale' }
      ];
      
      let currentPhaseIndex = 0;
      
      const runPhase = () => {
        if (!this.isBreathing) return;
        
        const phase = phases[currentPhaseIndex];
        this.breathPhase = phase.name;
        this.breathText = phase.text;
        this.breathCount = phase.duration;
        
        const countdown = setInterval(() => {
          this.breathCount--;
          if (this.breathCount <= 0) {
            clearInterval(countdown);
            currentPhaseIndex = (currentPhaseIndex + 1) % phases.length;
            this.breathTimer = setTimeout(runPhase, 100);
          }
        }, 1000);
      };
      
      runPhase();
    },
    
    // Utility Methods
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    },
    
    getRandomCloser() {
      return this.rexClosers[Math.floor(Math.random() * this.rexClosers.length)];
    },
    
    cleanup() {
      this.stopRecording();
      this.stopBreathing();
      
      if (this.audioUrl) {
        URL.revokeObjectURL(this.audioUrl);
      }
    }
  }
};
</script>

<style scoped>
.voice-recorder {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

/* Header */
.recorder-header {
  margin-bottom: 2rem;
}

.title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 2rem;
  color: #2c3e50;
  margin: 0 0 1rem 0;
}

.rex-icon {
  font-size: 2.5rem;
}

/* Urgency Alerts */
.urgency-alert {
  padding: 1rem;
  border-radius: 8px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  animation: pulse 2s ease-in-out infinite;
}

.urgency-low {
  background: #d4edda;
  color: #155724;
  border: 2px solid #c3e6cb;
}

.urgency-medium {
  background: #fff3cd;
  color: #856404;
  border: 2px solid #ffeaa7;
}

.urgency-high {
  background: #f8d7da;
  color: #721c24;
  border: 2px solid #f5c6cb;
}

.urgency-critical {
  background: #d63031;
  color: white;
  border: 2px solid #c0392b;
  animation: urgentPulse 1s ease-in-out infinite;
}

@keyframes urgentPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

/* Recording Section */
.recording-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.visualizer {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 100px;
  margin-bottom: 2rem;
  gap: 4px;
}

.visualizer-bar {
  flex: 1;
  background: linear-gradient(to top, #6c5ce7, #a29bfe);
  border-radius: 4px 4px 0 0;
  transition: height 0.1s ease;
  min-height: 5px;
}

.controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #6c5ce7;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5f4dd1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
}

.btn-danger {
  background: #d63031;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.btn-secondary {
  background: #00b894;
  color: white;
}

.btn-secondary:hover {
  background: #00a085;
}

.btn-icon {
  font-size: 1.5rem;
}

.recording-timer {
  font-size: 2rem;
  font-weight: 700;
  color: #d63031;
  font-variant-numeric: tabular-nums;
}

.recording {
  animation: recordingPulse 2s ease-in-out infinite;
}

@keyframes recordingPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.processing {
  opacity: 0.7;
  pointer-events: none;
}

/* Breathing Protocol */
.breathing-protocol {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

.protocol-title {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
}

.breathing-animation {
  display: flex;
  justify-content: center;
  margin: 2rem 0;
}

.breath-circle {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 1s ease;
  border: 4px solid white;
}

.breath-circle.inhale {
  animation: breatheIn 4s ease-in-out;
}

.breath-circle.hold {
  animation: breatheHold 7s ease-in-out;
}

.breath-circle.exhale {
  animation: breatheOut 8s ease-in-out;
}

@keyframes breatheIn {
  0% { transform: scale(1); }
  100% { transform: scale(1.3); }
}

@keyframes breatheHold {
  0%, 100% { transform: scale(1.3); opacity: 1; }
  50% { opacity: 0.9; }
}

@keyframes breatheOut {
  0% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

.breath-text {
  font-size: 1.5rem;
  font-weight: 600;
  text-transform: uppercase;
}

.breath-count {
  font-size: 3rem;
  font-weight: 700;
  margin-top: 0.5rem;
}

.protocol-instructions {
  margin: 1.5rem 0;
  text-align: left;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.protocol-instructions p {
  margin: 0.5rem 0;
  font-size: 1.1rem;
}

/* Response Section */
.response-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.response-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.tilt-indicator {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.tilt-indicator.tilt-low {
  background: #d4edda;
  color: #155724;
}

.tilt-indicator.tilt-medium {
  background: #fff3cd;
  color: #856404;
}

.tilt-indicator.tilt-high {
  background: #f8d7da;
  color: #721c24;
}

.tilt-indicator.tilt-critical {
  background: #d63031;
  color: white;
}

.response-content {
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.response-content.tilt-low {
  background: #f0f9ff;
  border-left: 4px solid #0ea5e9;
}

.response-content.tilt-medium {
  background: #fffbeb;
  border-left: 4px solid #f59e0b;
}

.response-content.tilt-high {
  background: #fef2f2;
  border-left: 4px solid #ef4444;
}

.response-content.tilt-critical {
  background: #fee;
  border-left: 4px solid #dc2626;
}

.response-text {
  line-height: 1.8;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.response-text :deep(strong) {
  color: #1a202c;
}

.response-text :deep(ul) {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.response-text :deep(li) {
  margin: 0.5rem 0;
}

.tilt-recommendations {
  background: rgba(255, 255, 255, 0.7);
  padding: 1.5rem;
  border-radius: 8px;
}

.tilt-recommendations h4 {
  margin-top: 0;
  color: #1a202c;
}

.tilt-recommendations ul {
  margin: 0;
  padding-left: 1.5rem;
}

.tilt-recommendations li {
  margin: 0.75rem 0;
  line-height: 1.6;
}

/* Rex Closers */
.rex-closers {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 1.5rem;
}

.closer-message {
  font-size: 1.1rem;
  font-style: italic;
  margin-bottom: 1rem;
  line-height: 1.6;
}

.rex-signature {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 1.1rem;
}

.signature-icon {
  font-size: 1.5rem;
}

/* Playback Section */
.playback-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.playback-section h4 {
  margin-top: 0;
  color: #2c3e50;
}

.audio-player {
  width: 100%;
  margin-top: 1rem;
}

/* Error Messages */
.error-message {
  background: #fee;
  color: #c53030;
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  border: 1px solid #fc8181;
}

.error-icon,
.alert-icon {
  font-size: 1.2rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .voice-recorder {
    padding: 1rem;
  }
  
  .title {
    font-size: 1.5rem;
  }
  
  .breath-circle {
    width: 150px;
    height: 150px;
  }
  
  .breath-count {
    font-size: 2rem;
  }
  
  .response-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
