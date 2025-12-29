import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

const app = createApp(App)
  .use(router)
  .use(store)

// Enable navigation requests from Electron tray/menu
if (window.electronAPI?.onNavigate) {
  window.electronAPI.onNavigate((route) => {
    router.push(route)
  })
}

app.mount('#app')
