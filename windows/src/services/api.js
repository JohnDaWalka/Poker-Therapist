import axios from 'axios'
import authService from './authService'

const API_URL = 'http://localhost:8000'
const USER_ID = 'default'

// Create axios instance with auth interceptor
const axiosInstance = axios.create({
  baseURL: API_URL
})

// Add authentication token to all requests
axiosInstance.interceptors.request.use(
  (config) => {
    const token = authService.getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle 401 responses (unauthorized)
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - redirect to login
      await authService.signOut()
      // Emit event for app to handle login redirect
      window.dispatchEvent(new CustomEvent('auth-required'))
    }
    return Promise.reject(error)
  }
)

const api = {
  async analyzeTriage(data) {
    const response = await axiosInstance.post('/api/triage', {
      ...data,
      user_id: USER_ID
    })
    return response.data
  },
  
  async startDeepSession(data) {
    const response = await axiosInstance.post('/api/deep-session', {
      ...data,
      user_id: USER_ID
    })
    return response.data
  },
  
  async analyzeHand(data) {
    const response = await axiosInstance.post('/api/analyze/hand', {
      ...data,
      user_id: USER_ID
    })
    return response.data
  },
  
  async getProfile() {
    const response = await axiosInstance.get(`/api/profile/${USER_ID}`)
    return response.data
  },
  
  async getPlaybook() {
    const response = await axiosInstance.get(`/api/playbook/${USER_ID}`)
    return response.data
  },
  
  async getUserProfile() {
    const response = await axiosInstance.get(`/api/profile/${USER_ID}`)
    return response.data
  },
  
  async getUserStats() {
    const response = await axiosInstance.get(`/api/stats/${USER_ID}`)
    return response.data
  }
}

export default api
