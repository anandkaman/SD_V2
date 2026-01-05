const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { exec } = require('child_process');
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

let mainWindow;
let isQuitting = false;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    icon: path.join(__dirname, '../public/icon.png')
  });

  // Load the app
  const startURL = isDev
    ? 'http://localhost:4000'
    : `file://${path.join(__dirname, '../build/index.html')}`;

  mainWindow.loadURL(startURL);

  // DevTools disabled - uncomment below line if needed for debugging
  // if (isDev) {
  //   mainWindow.webContents.openDevTools();
  // }

  // Handle window close event
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();

      // Show confirmation dialog
      dialog.showMessageBox(mainWindow, {
        type: 'question',
        buttons: ['Yes', 'No'],
        defaultId: 1,
        title: 'Exit Application',
        message: 'Do you want to exit?',
        detail: 'This will close the application and stop all services.'
      }).then((response) => {
        if (response.response === 0) { // User clicked "Yes"
          isQuitting = true;

          // Kill all processes directly instead of calling STOP.bat
          const commands = [
            'taskkill /F /IM python.exe',
            'taskkill /F /IM node.exe',
            'for /f "tokens=5" %a in (\'netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"\') do taskkill /F /PID %a',
            'for /f "tokens=5" %a in (\'netstat -aon ^| findstr ":4000" ^| findstr "LISTENING"\') do taskkill /F /PID %a'
          ].join(' & ');

          exec(commands, (error) => {
            if (error) {
              console.log('Cleanup completed with some warnings (normal)');
            }
            // Give processes time to close, then exit
            setTimeout(() => {
              mainWindow.destroy();
              app.quit();
              process.exit(0);
            }, 500);
          });
        }
        // If "No", do nothing - window stays open
      });
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
