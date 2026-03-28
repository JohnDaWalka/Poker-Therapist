<template>
  <div class="poker-hand-analysis">
    <h2>Poker Hand Analysis</h2>
    <div class="filters">
      <label for="handStrength">Hand Strength:</label>
      <select v-model="filters.handStrength" @change="applyFilters">
        <option value="">All</option>
        <option v-for="strength in handStrengths" :key="strength" :value="strength">{{ strength }}</option>
      </select>
    </div>
    <div class="charts">
      <chart :data="chartData" />
    </div>
    <div class="tables">
      <table>
        <thead>
          <tr>
            <th @click="sortTable('hand')">Hand</th>
            <th @click="sortTable('strength')">Strength</th>
            <th @click="sortTable('rank')">Rank</th>
            <th @click="sortTable('probability')">Winning Probability</th>
            <th @click="sortTable('actions')">Suggested Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="hand in filteredHands" :key="hand.id">
            <td>{{ hand.details }}</td>
            <td>{{ hand.strength }}</td>
            <td>{{ hand.rank }}</td>
            <td>{{ hand.probability }}%</td>
            <td>{{ hand.actions }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import Chart from './Chart.vue';

export default {
  name: 'PokerHandAnalysis',
  components: {
    Chart,
  },
  data() {
    return {
      filters: {
        handStrength: '',
      },
      sortKey: '',
      sortOrder: 1,
    };
  },
  computed: {
    ...mapGetters(['handStrengths', 'filteredHands', 'chartData']),
  },
  methods: {
    ...mapActions(['fetchPokerHandAnalysis']),
    applyFilters() {
      this.fetchPokerHandAnalysis(this.filters);
    },
    sortTable(key) {
      if (this.sortKey === key) {
        this.sortOrder *= -1;
      } else {
        this.sortKey = key;
        this.sortOrder = 1;
      }
      this.filteredHands.sort((a, b) => {
        if (a[key] < b[key]) return -1 * this.sortOrder;
        if (a[key] > b[key]) return 1 * this.sortOrder;
        return 0;
      });
    },
  },
  created() {
    this.fetchPokerHandAnalysis();
  },
};
</script>

<style scoped>
.poker-hand-analysis {
  padding: 20px;
}

.filters {
  margin-bottom: 20px;
}

.charts {
  margin-bottom: 20px;
}

.tables {
  margin-bottom: 20px;
}

th {
  cursor: pointer;
}
</style>
