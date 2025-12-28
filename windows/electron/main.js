const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron');
const path = require('path');

let mainWindow;
let tray;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        }
    });

    // Load app
    if (process.env.NODE_ENV === 'development') {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    }
}

function createTray() {
    tray = new Tray(path.join(__dirname, '../public/icon.png'));
    
    const contextMenu = Menu.buildFromTemplate([
        { label: 'Quick Triage', click: () => {
            mainWindow.show();
            mainWindow.webContents.send('navigate', '/triage');
        }},
        { label: 'Deep Session', click: () => {
            mainWindow.show();
            mainWindow.webContents.send('navigate', '/deep');
        }},
        { type: 'separator' },
        { label: 'Show App', click: () => mainWindow.show() },
        { label: 'Quit', click: () => app.quit() }
    ]);
    
    tray.setToolTip('Therapy Rex');
    tray.setContextMenu(contextMenu);
    
    tray.on('click', () => {
        mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    });
}

app.whenReady().then(() => {
    createWindow();
    createTray();
    
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// IPC handlers
ipcMain.handle('get-user-data-path', () => {
    return app.getPath('userData');
});
