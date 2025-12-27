import { createStore } from 'vuex'

export default createStore({
  state: {
    user: {
      id: 'default',
      profile: null
    },
    sessions: []
  },
  mutations: {
    SET_PROFILE(state, profile) {
      state.user.profile = profile
    },
    ADD_SESSION(state, session) {
      state.sessions.push(session)
    }
  },
  actions: {
    async loadProfile({ commit }) {
      // TODO: Load profile from API
      commit('SET_PROFILE', {})
    },
    saveSession({ commit }, session) {
      commit('ADD_SESSION', session)
    }
  },
  getters: {
    userProfile: state => state.user.profile,
    recentSessions: state => state.sessions.slice(-10)
  }
})
