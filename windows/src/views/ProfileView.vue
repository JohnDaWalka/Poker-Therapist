<template>
  <div class="profile-view">
    <div v-if="loading">Loading...</div>
    <div v-else class="content">
      <div class="header">
        <h2>{{ user.username || 'Unknown User' }}</h2>
        <p>Mental Score: {{ stats.mentalScore || 0 }}/100</p>
      </div>
      <div class="stats">
        <div>Sessions: {{ stats.totalSessions || 0 }}</div>
        <div>Hands: {{ stats.totalHands || 0 }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import api from '../services/api';

export default {
  name: 'ProfileView',
  setup() {
    const loading = ref(true);
    const user = ref({});
    const stats = ref({});

    onMounted(async () => {
      try {
        const [u, s] = await Promise.all([api.getUserProfile(), api.getUserStats()]);
        user.value = u;
        stats.value = s;
      } catch (e) {
        console.error('Failed to load profile data:', e);
      } finally {
        loading.value = false;
      }
    });

    return { loading, user, stats };
  }
};
</script>

<style scoped>
.profile-view { padding: 40px; max-width: 800px; margin: 0 auto; }
.header { border-bottom: 1px solid #eee; padding-bottom: 20px; }
.stats { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
</style>
