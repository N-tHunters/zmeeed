const {app, BrowserWindow} = require('electron')
const url = require('url')
const path = require('path')

let win

function createWindow() {
    win = new BrowserWindow({autoHideMenuBar: true, width: 800, height: 600,
                             webPreferences: {
                                 nodeIntegration: true,
                                 contextIsolation: false
                             }})
    win.loadURL(url.format ({
        pathname: path.join(__dirname, 'index.html'),
        protocol: 'file:',
        slashes: true,
    }))
}

app.on('ready', createWindow)
