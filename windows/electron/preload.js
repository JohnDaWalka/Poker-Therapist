const { contextBridge, ipcRenderer } = require('electron')

// Expose a minimal API for future renderer-to-main communication.
contextBridge.exposeInMainWorld('electronAPI', {
  onNavigate: (callback) => ipcRenderer.on('navigate', (_event, route) => callback(route))
})
