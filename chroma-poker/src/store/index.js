import Vue from 'vue';
import Vuex from 'vuex';
import {
  getHandDetails,
  getHandStrength,
  getHandRank,
  getWinningProbability,
  getSuggestedActions,
  getOpponentAnalysis,
  getHistoricalData,
  getVisualElements,
} from '../api/pokerHandAnalysis';

Vue.use(Vuex);

const state = {
  handDetails: {},
  handStrength: '',
  handRank: '',
  winningProbability: 0,
  suggestedActions: [],
  opponentAnalysis: {},
  historicalData: [],
  visualElements: {},
};

const mutations = {
  SET_HAND_DETAILS(state, details) {
    state.handDetails = details;
  },
  SET_HAND_STRENGTH(state, strength) {
    state.handStrength = strength;
  },
  SET_HAND_RANK(state, rank) {
    state.handRank = rank;
  },
  SET_WINNING_PROBABILITY(state, probability) {
    state.winningProbability = probability;
  },
  SET_SUGGESTED_ACTIONS(state, actions) {
    state.suggestedActions = actions;
  },
  SET_OPPONENT_ANALYSIS(state, analysis) {
    state.opponentAnalysis = analysis;
  },
  SET_HISTORICAL_DATA(state, data) {
    state.historicalData = data;
  },
  SET_VISUAL_ELEMENTS(state, elements) {
    state.visualElements = elements;
  },
};

const actions = {
  async fetchHandDetails({ commit }) {
    const details = await getHandDetails();
    commit('SET_HAND_DETAILS', details);
  },
  async fetchHandStrength({ commit }) {
    const strength = await getHandStrength();
    commit('SET_HAND_STRENGTH', strength);
  },
  async fetchHandRank({ commit }) {
    const rank = await getHandRank();
    commit('SET_HAND_RANK', rank);
  },
  async fetchWinningProbability({ commit }) {
    const probability = await getWinningProbability();
    commit('SET_WINNING_PROBABILITY', probability);
  },
  async fetchSuggestedActions({ commit }) {
    const actions = await getSuggestedActions();
    commit('SET_SUGGESTED_ACTIONS', actions);
  },
  async fetchOpponentAnalysis({ commit }) {
    const analysis = await getOpponentAnalysis();
    commit('SET_OPPONENT_ANALYSIS', analysis);
  },
  async fetchHistoricalData({ commit }) {
    const data = await getHistoricalData();
    commit('SET_HISTORICAL_DATA', data);
  },
  async fetchVisualElements({ commit }) {
    const elements = await getVisualElements();
    commit('SET_VISUAL_ELEMENTS', elements);
  },
};

const getters = {
  handDetails: (state) => state.handDetails,
  handStrength: (state) => state.handStrength,
  handRank: (state) => state.handRank,
  winningProbability: (state) => state.winningProbability,
  suggestedActions: (state) => state.suggestedActions,
  opponentAnalysis: (state) => state.opponentAnalysis,
  historicalData: (state) => state.historicalData,
  visualElements: (state) => state.visualElements,
};

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
});
