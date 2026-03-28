<template>
  <div id="app">
    <PokerHandAnalysis />
  </div>
</template>

<script>
import PokerHandAnalysis from './components/PokerHandAnalysis.vue';

export default {
  name: 'App',
  components: {
    PokerHandAnalysis,
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
