import { createRouter, createWebHistory } from 'vue-router'
import TriageView from '../views/TriageView.vue'

const routes = [
  {
    path: '/',
    redirect: '/triage'
  },
  {
    path: '/triage',
    name: 'Triage',
    component: TriageView
  },
  {
    path: '/deep',
    name: 'DeepSession',
    component: () => import('../views/DeepSessionView.vue')
  },
  {
    path: '/hand',
    name: 'HandAnalysis',
    component: () => import('../views/HandAnalysisView.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
