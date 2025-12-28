const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    getUserDataPath: () => ipcRenderer.invoke('get-user-data-path'),
    onNavigate: (callback) => ipcRenderer.on('navigate', callback)
});
