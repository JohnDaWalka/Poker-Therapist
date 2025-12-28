import axios from 'axios'

const API_URL = 'http://localhost:8000'
const USER_ID = 'default'

const api = {
  async analyzeTriage(data) {
    const response = await axios.post(`${API_URL}/api/triage`, {
      ...data,
      user_id: USER_ID
    })
    return response.data
  },
  
  async startDeepSession(data) {
    const response = await axios.post(`${API_URL}/api/deep-session`, {
      ...data,
      user_id: USER_ID
    })
    return response.data
  },
  
  async analyzeHand(data) {
    const response = await axios.post(`${API_URL}/api/analyze/hand`, {
      ...data,
      user_id: USER_ID
    })
    return response.data
  },
  
  async getProfile() {
    const response = await axios.get(`${API_URL}/api/profile/${USER_ID}`)
    return response.data
  },
  
  async getPlaybook() {
    const response = await axios.get(`${API_URL}/api/playbook/${USER_ID}`)
    return response.data
  },
  
  async getUserProfile() {
    const response = await axios.get(`${API_URL}/api/profile/${USER_ID}`)
    return response
  },
  
  async getUserStats() {
    const response = await axios.get(`${API_URL}/api/stats/${USER_ID}`)
    return response
  }
}

export default api
