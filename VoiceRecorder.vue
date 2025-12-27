<template>
  <div class="voice-recorder">
    <div class="recorder-container">
      <!-- Visualization Canvas -->
      <canvas 
        ref="visualizer" 
        class="audio-visualizer"
        :class="{ 'recording': isRecording }"
      ></canvas>

      <!-- Recording Controls -->
      <div class="controls">
        <button
          v-if="!isRecording"
          @click="startRecording"
          class="btn btn-record"
          :disabled="isProcessing"
        >
          <i class="fas fa-microphone"></i>
          Start Recording
        </button>
        
        <div v-else class="recording-controls">
          <button
            @click="stopRecording"
            class="btn btn-stop"
          >
            <i class="fas fa-stop"></i>
            Stop Recording
          </button>
          <span class="recording-time">{{ formattedTime }}</span>
        </div>
      </div>

      <!-- Processing Spinner -->
      <div v-if="isProcessing" class="processing-overlay">
        <div class="spinner"></div>
        <p>Processing your recording...</p>
      </div>

      <!-- Transcription Display -->
      <div v-if="transcription" class="transcription-container">
        <h3>Transcription:</h3>
        <div class="transcription-text">{{ transcription }}</div>
        <button @click="clearTranscription" class="btn btn-clear">
          <i class="fas fa-times"></i>
          Clear
        </button>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        {{ error }}
      </div>
    </div>

    <!-- Rex Closer Dialog -->
    <div v-if="showRexCloser" class="rex-closer-overlay" @click="closeRexCloser">
      <div class="rex-closer-dialog" @click.stop>
        <div class="rex-avatar">
          <i class="fas fa-user-tie"></i>
        </div>
        <h2>{{ rexCloserTitle }}</h2>
        <p class="rex-message">{{ rexCloserMessage }}</p>
        <button @click="closeRexCloser" class="btn btn-primary">
          Got it!
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';

const MAX_RECORDING_DURATION = 300000; // 5 minutes in milliseconds
const REX_CLOSER_MESSAGES = [
  {
    title: "Great Session!",
    messages: [
      "Remember, the key to poker is reading your opponents, not just your cards.",
      "Every hand is a new opportunity. Don't let past losses cloud your judgment.",
      "The best players know when to fold. It's not about winning every hand.",
      "Your mental game is just as important as your technical skills.",
      "Stay patient, stay focused, and the wins will come."
    ]
  },
  {
    title: "Rex's Wisdom",
    messages: [
      "Position is power. Use it wisely.",
      "Aggression wins tournaments, but know when to pump the brakes.",
      "Your table image is your most valuable asset. Manage it carefully.",
      "Don't chase losses. The cards don't know you're behind.",
      "Trust your instincts, but verify with solid poker theory."
    ]
  },
  {
    title: "Session Complete",
    messages: [
      "Another step forward in your poker journey!",
      "Consistency beats intensity. Keep showing up.",
      "You're building skills that will last a lifetime.",
      "Remember to review this session and learn from it.",
      "The path to mastery is paved with practice and reflection."
    ]
  }
];

export default {
  name: 'VoiceRecorder',
  data() {
    return {
      isRecording: false,
      isProcessing: false,
      mediaRecorder: null,
      audioChunks: [],
      audioContext: null,
      analyser: null,
      animationId: null,
      recordingStartTime: null,
      recordingDuration: 0,
      maxDurationTimer: null,
      transcription: '',
      error: null,
      showRexCloser: false,
      rexCloserTitle: '',
      rexCloserMessage: ''
    };
  },
  computed: {
    ...mapState('session', ['currentSession']),
    formattedTime() {
      const seconds = Math.floor(this.recordingDuration / 1000);
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
  },
  methods: {
    ...mapActions('session', ['addNote', 'updateSession']),
    
    async startRecording() {
      try {
        this.error = null;
        this.transcription = '';
        
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Initialize audio context for visualization
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 2048;
        
        const source = this.audioContext.createMediaStreamSource(stream);
        source.connect(this.analyser);
        
        // Initialize media recorder
        this.mediaRecorder = new MediaRecorder(stream);
        this.audioChunks = [];
        
        this.mediaRecorder.addEventListener('dataavailable', event => {
          this.audioChunks.push(event.data);
        });
        
        this.mediaRecorder.addEventListener('stop', () => {
          this.handleRecordingStop();
        });
        
        this.mediaRecorder.start();
        this.isRecording = true;
        this.recordingStartTime = Date.now();
        this.recordingDuration = 0;
        
        // Start visualization
        this.visualize();
        
        // Start duration tracking
        this.trackDuration();
        
        // Set max duration timer
        this.maxDurationTimer = setTimeout(() => {
          if (this.isRecording) {
            this.stopRecording();
            this.error = `Recording automatically stopped after ${MAX_RECORDING_DURATION / 60000} minutes.`;
          }
        }, MAX_RECORDING_DURATION);
        
      } catch (err) {
        console.error('Error starting recording:', err);
        this.error = 'Failed to access microphone. Please check your permissions.';
      }
    },
    
    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.mediaRecorder.stop();
        this.isRecording = false;
        
        // Stop all tracks
        if (this.mediaRecorder.stream) {
          this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
        
        // Clear timers
        if (this.maxDurationTimer) {
          clearTimeout(this.maxDurationTimer);
          this.maxDurationTimer = null;
        }
        
        // Stop visualization
        if (this.animationId) {
          cancelAnimationFrame(this.animationId);
          this.animationId = null;
        }
        
        // Close audio context
        if (this.audioContext) {
          this.audioContext.close();
          this.audioContext = null;
        }
      }
    },
    
    trackDuration() {
      if (this.isRecording) {
        this.recordingDuration = Date.now() - this.recordingStartTime;
        requestAnimationFrame(() => this.trackDuration());
      }
    },
    
    visualize() {
      if (!this.isRecording || !this.analyser) return;
      
      const canvas = this.$refs.visualizer;
      if (!canvas) return;
      
      const canvasCtx = canvas.getContext('2d');
      const bufferLength = this.analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      const draw = () => {
        if (!this.isRecording) return;
        
        this.animationId = requestAnimationFrame(draw);
        
        this.analyser.getByteTimeDomainData(dataArray);
        
        canvasCtx.fillStyle = 'rgb(20, 20, 30)';
        canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
        
        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = 'rgb(0, 200, 100)';
        canvasCtx.beginPath();
        
        const sliceWidth = canvas.width / bufferLength;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
          const v = dataArray[i] / 128.0;
          const y = (v * canvas.height) / 2;
          
          if (i === 0) {
            canvasCtx.moveTo(x, y);
          } else {
            canvasCtx.lineTo(x, y);
          }
          
          x += sliceWidth;
        }
        
        canvasCtx.lineTo(canvas.width, canvas.height / 2);
        canvasCtx.stroke();
      };
      
      draw();
    },
    
    async handleRecordingStop() {
      this.isProcessing = true;
      
      try {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        
        // Convert to base64 for API
        const base64Audio = await this.blobToBase64(audioBlob);
        
        // Send to API for transcription
        await this.transcribeAudio(base64Audio);
        
        // Show random Rex closer
        this.showRandomRexCloser();
        
      } catch (err) {
        console.error('Error processing recording:', err);
        this.error = 'Failed to process recording. Please try again.';
      } finally {
        this.isProcessing = false;
        this.audioChunks = [];
      }
    },
    
    async transcribeAudio(base64Audio) {
      try {
        // Correct API contract: send audio as part of multimodal input
        const response = await fetch('/api/transcribe', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'gpt-4o-audio-preview',
            modalities: ['text', 'audio'],
            audio: {
              data: base64Audio,
              format: 'webm'
            }
          })
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        this.transcription = data.transcript || data.text || '';
        
        // Save to Vuex store with fallback
        if (this.transcription && this.currentSession) {
          try {
            await this.addNote({
              sessionId: this.currentSession.id,
              type: 'voice',
              content: this.transcription,
              timestamp: new Date().toISOString(),
              duration: this.recordingDuration
            });
          } catch (vuexError) {
            console.warn('Vuex store not available, using local storage fallback:', vuexError);
            this.saveTolocalStorage();
          }
        }
        
      } catch (err) {
        console.error('Error transcribing audio:', err);
        this.error = 'Failed to transcribe audio. Please try again.';
        throw err;
      }
    },
    
    saveTolocalStorage() {
      try {
        const notes = JSON.parse(localStorage.getItem('voiceNotes') || '[]');
        notes.push({
          id: Date.now(),
          content: this.transcription,
          timestamp: new Date().toISOString(),
          duration: this.recordingDuration
        });
        localStorage.setItem('voiceNotes', JSON.stringify(notes));
      } catch (err) {
        console.error('Error saving to localStorage:', err);
      }
    },
    
    blobToBase64(blob) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = reader.result.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    },
    
    clearTranscription() {
      this.transcription = '';
      this.error = null;
    },
    
    showRandomRexCloser() {
      // Improved randomness for Rex closer
      const categoryIndex = Math.floor(Math.random() * REX_CLOSER_MESSAGES.length);
      const category = REX_CLOSER_MESSAGES[categoryIndex];
      const messageIndex = Math.floor(Math.random() * category.messages.length);
      
      this.rexCloserTitle = category.title;
      this.rexCloserMessage = category.messages[messageIndex];
      this.showRexCloser = true;
    },
    
    closeRexCloser() {
      this.showRexCloser = false;
    }
  },
  
  beforeUnmount() {
    // Cleanup
    if (this.isRecording) {
      this.stopRecording();
    }
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    if (this.maxDurationTimer) {
      clearTimeout(this.maxDurationTimer);
    }
  }
};
</script>

<style scoped>
.voice-recorder {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.recorder-container {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  position: relative;
}

.audio-visualizer {
  width: 100%;
  height: 150px;
  border-radius: 10px;
  background: #14141e;
  margin-bottom: 20px;
  border: 2px solid transparent;
  transition: border-color 0.3s ease;
}

.audio-visualizer.recording {
  border-color: #00c864;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(0, 200, 100, 0.7);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(0, 200, 100, 0);
  }
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.recording-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.btn {
  padding: 12px 30px;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-record {
  background: linear-gradient(135deg, #00c864 0%, #00a854 100%);
  color: white;
}

.btn-record:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 200, 100, 0.4);
}

.btn-stop {
  background: linear-gradient(135deg, #ff4757 0%, #e84118 100%);
  color: white;
}

.btn-stop:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 71, 87, 0.4);
}

.btn-clear {
  background: #6c757d;
  color: white;
  padding: 8px 20px;
  font-size: 14px;
  margin-top: 10px;
}

.btn-clear:hover {
  background: #5a6268;
}

.recording-time {
  font-size: 24px;
  font-weight: 700;
  color: #ff4757;
  font-family: 'Courier New', monospace;
  min-width: 60px;
  text-align: center;
}

.processing-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(20, 20, 30, 0.95);
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(0, 200, 100, 0.3);
  border-top-color: #00c864;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.processing-overlay p {
  margin-top: 20px;
  color: #00c864;
  font-size: 16px;
  font-weight: 600;
}

.transcription-container {
  margin-top: 30px;
  padding: 20px;
  background: rgba(0, 200, 100, 0.1);
  border-radius: 10px;
  border-left: 4px solid #00c864;
}

.transcription-container h3 {
  margin: 0 0 15px 0;
  color: #00c864;
  font-size: 18px;
}

.transcription-text {
  color: #e0e0e0;
  line-height: 1.6;
  font-size: 15px;
  padding: 15px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.error-message {
  margin-top: 20px;
  padding: 15px;
  background: rgba(255, 71, 87, 0.1);
  border-radius: 8px;
  border-left: 4px solid #ff4757;
  color: #ff4757;
  display: flex;
  align-items: center;
  gap: 10px;
}

.rex-closer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.rex-closer-dialog {
  background: linear-gradient(135deg, #2d3561 0%, #1a1a2e 100%);
  border-radius: 20px;
  padding: 40px;
  max-width: 500px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.rex-avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #00c864 0%, #00a854 100%);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto 20px;
  font-size: 40px;
  color: white;
}

.rex-closer-dialog h2 {
  color: #00c864;
  margin-bottom: 20px;
  font-size: 28px;
}

.rex-message {
  color: #e0e0e0;
  font-size: 18px;
  line-height: 1.6;
  margin-bottom: 30px;
}

.btn-primary {
  background: linear-gradient(135deg, #00c864 0%, #00a854 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 200, 100, 0.5);
}

/* Responsive */
@media (max-width: 768px) {
  .recorder-container {
    padding: 20px;
  }
  
  .audio-visualizer {
    height: 100px;
  }
  
  .rex-closer-dialog {
    margin: 20px;
    padding: 30px 20px;
  }
}
</style>
