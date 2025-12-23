# Complete Installation Guide - Windows

## Prerequisites Installation

### 1. Install Node.js

**Download and Install**
1. Visit https://nodejs.org/
2. Download LTS version (recommended: 18.x or higher)
3. Run the installer (e.g., `node-v18.19.0-x64.msi`)
4. Follow installation wizard:
   - Accept license agreement
   - Keep default installation path: `C:\Program Files\nodejs\`
   - Check "Automatically install necessary tools" (optional)
   - Click Install

**Verify Installation**
Open Command Prompt (cmd) or PowerShell:
```bash
node --version
# Should show: v18.x.x or higher

npm --version
# Should show: 9.x.x or higher
```

### 2. Verify Backend Setup

**Check Backend Location**
```bash
cd d:\saledeed_2025\sale_deed_processor\backend
dir
```
Should see: `app/`, `venv/`, `requirements.txt`, etc.

**Activate Virtual Environment**
```bash
venv\Scripts\activate
```
You should see `(venv)` prefix in command prompt.

**Verify Backend Dependencies**
```bash
pip list
```
Should show: fastapi, uvicorn, sqlalchemy, etc.

**Test Backend**
```bash
uvicorn app.main:app --reload
```
Open browser: http://localhost:8000/docs
You should see API documentation.

## Frontend Installation

### Method 1: Using Setup Script (Recommended)

**Step 1: Navigate to Frontend Directory**
```bash
cd d:\saledeed_2025\fronted
```

**Step 2: Run Setup**
Double-click `setup.bat` or run in command prompt:
```bash
setup.bat
```

This will:
- Install all npm dependencies
- Set up node_modules folder
- Show completion message

**Expected Output**
```
Installing dependencies...
[Progress indicators...]
added XXX packages in XXs
Setup Complete!
```

### Method 2: Manual Installation

**Step 1: Navigate to Frontend**
```bash
cd d:\saledeed_2025\fronted
```

**Step 2: Install Dependencies**
```bash
npm install
```

**Step 3: Wait for Completion**
This may take 2-5 minutes depending on internet speed.

**Expected Packages**
- react, react-dom (UI framework)
- react-router-dom (navigation)
- axios (HTTP client)
- electron (desktop framework)
- lucide-react (icons)
- xlsx (Excel export)
- react-scripts (build tools)
- electron-builder (packaging)
- concurrently, wait-on (dev tools)

## Verification Steps

### 1. Check Installation

**Verify node_modules exists**
```bash
dir node_modules
```
Should show many folders (300+ packages).

**Check package.json**
```bash
type package.json
```
Should show project configuration.

### 2. Test React Build

**Build React app (optional)**
```bash
npm run build
```
Should create `build/` folder with compiled app.

## Running the Application

### Development Mode (Recommended for Development)

**Terminal 1: Start Backend**
```bash
cd d:\saledeed_2025\sale_deed_processor\backend
venv\Scripts\activate
uvicorn app.main:app --reload
```
Keep this running. Backend at: http://localhost:8000

**Terminal 2: Start Frontend**
```bash
cd d:\saledeed_2025\fronted
start-dev.bat
```
Or manually:
```bash
npm run electron-dev
```

**Expected Behavior**
1. React dev server starts on port 3000
2. Browser opens temporarily (ignore this)
3. Electron window opens with app
4. DevTools open automatically (for debugging)

**Success Indicators**
- Electron window shows "SaleDeed Processor" header
- Control Panel page visible
- Footer shows system info
- No console errors (press F12 to check)

### Production Mode (For End Users)

**Option 1: Run Built App**
```bash
npm run build
npm run electron
```

**Option 2: Create Installer**
```bash
npm run dist
```
Installer created in `dist/` folder.
Share the `.exe` file with end users.

## First Time Usage

### Step 1: Verify Backend Connection

1. Open the app
2. Check footer at bottom
3. Look for "Health Status" section
4. Should show green checkmark for API
5. System Info should show statuses for:
   - CUDA (may be red if no GPU)
   - Tesseract OCR (should be green)
   - Ollama LLM (should be green)
   - YOLO Model (should be green)
   - Poppler (should be green)

**If All Red**
- Backend not running or wrong URL
- Start backend first
- Check http://localhost:8000/health in browser

### Step 2: Upload Test PDF

1. Click "Control Panel" in header
2. Click upload area or select files
3. Choose one or more PDF files
4. Click "Upload PDFs"
5. Success message should appear

### Step 3: Process PDFs

1. Click "Start Processing"
2. Watch progress bar
3. Stats update in real-time:
   - Total files
   - Processed count
   - Failed count
   - Active workers

**Processing Status**
- Running: Blue badge with spinner
- Idle: Gray badge

### Step 4: Start Vision Processing

1. After PDF processing completes
2. Click "Start Vision"
3. Monitor vision processing progress
4. Registration fees extracted from tables

### Step 5: View Data

1. Click "Data View" in header
2. Table shows all processed documents
3. Each document ID spans multiple rows
4. Scroll horizontally to see all fields

### Step 6: Download Excel

**Server-side Download (Recommended)**
1. Click "Download Excel (DB)"
2. Downloads all data from database
3. File saved to Downloads folder

**Client-side Download**
1. Click "Download Excel (Client)"
2. Exports currently loaded data
3. Instant download

### Step 7: Search Data

1. Use search box at top
2. Type document ID, name, or address
3. Table filters instantly
4. Case-insensitive search

### Step 8: Switch Theme

1. Click Sun/Moon icon in header
2. Switches between light/dark
3. Preference saved automatically

## Troubleshooting

### Installation Issues

**Problem: npm install fails**
```
Error: Cannot find module 'npm'
```
**Solution**: Reinstall Node.js, ensure npm is included

**Problem: Permission denied**
```
Error: EACCES: permission denied
```
**Solution**: Run Command Prompt as Administrator

**Problem: Network error**
```
Error: network timeout
```
**Solution**:
- Check internet connection
- Try: `npm install --verbose`
- Use different network if behind firewall

### Runtime Issues

**Problem: Electron window blank**
**Solution**:
1. Open DevTools (F12)
2. Check Console for errors
3. Ensure React server started (look for "Compiled successfully!")
4. Restart: Close Electron, Ctrl+C React server, restart

**Problem: Cannot connect to backend**
**Solution**:
1. Verify backend running: http://localhost:8000/docs
2. Check backend terminal for errors
3. Restart backend
4. Check Windows Firewall (allow port 8000)

**Problem: Upload fails**
**Solution**:
1. Check file is PDF
2. Check file size (very large files may timeout)
3. Verify backend has write permissions to upload folder
4. Check backend logs for errors

**Problem: Processing stuck**
**Solution**:
1. Click "Stop Processing"
2. Check backend logs
3. Verify Ollama is running: `ollama list`
4. Restart Ollama: `ollama serve`
5. Restart processing

**Problem: Data not showing**
**Solution**:
1. Check database has data (use DB client)
2. Click Refresh button
3. Check browser Console (F12) for API errors
4. Verify backend API endpoints work

**Problem: Excel download fails**
**Solution**:
1. Try client-side download instead
2. Check backend /export/excel endpoint
3. Check available disk space
4. Check Downloads folder permissions

### Performance Issues

**Problem: Slow table rendering**
**Solution**:
- Reduce number of documents shown
- Use search to filter results
- Close other applications

**Problem: High memory usage**
**Solution**:
- Close and reopen Electron app
- Clear browser cache
- Reduce polling intervals (code change needed)

## Advanced Configuration

### Change API URL

**File**: `src/services/api.js`
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
// Change to your backend URL
```

### Change Polling Intervals

**Control Panel Stats**: `src/pages/ControlPanel.js`
```javascript
const interval = setInterval(fetchStats, 2000); // 2 seconds
// Change 2000 to desired milliseconds
```

**Footer Updates**: `src/components/Footer.js`
```javascript
const interval = setInterval(fetchSystemData, 10000); // 10 seconds
// Change 10000 to desired milliseconds
```

### Customize Theme Colors

**File**: `src/styles/App.css`
```css
:root {
  --accent-primary: #2563eb; /* Change primary color */
  --accent-success: #16a34a; /* Change success color */
  /* etc. */
}
```

## Building for Distribution

### Create Windows Installer

**Step 1: Build React App**
```bash
npm run build
```
Creates optimized production build in `build/` folder.

**Step 2: Build Electron Package**
```bash
npm run dist
```

**Output**
```
dist/
├── SaleDeed Processor Setup 1.0.0.exe  (Installer)
└── win-unpacked/                       (Unpacked app)
```

**Step 3: Distribute**
- Share the `.exe` installer
- Users double-click to install
- App installs to Program Files
- Desktop shortcut created

### Portable Version (No Installation)

```bash
npm run pack
```
Creates `dist/win-unpacked/` folder with portable app.
Users can run `SaleDeed Processor.exe` directly.

## Network Deployment

### Shared Network Setup

**Scenario**: Multiple users, one backend server

**Backend Server** (192.168.1.100)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend Clients**
Change API URL in `src/services/api.js`:
```javascript
const API_BASE_URL = 'http://192.168.1.100:8000/api';
```
Rebuild and distribute.

## Backup and Restore

### Backup Important Data

**Database**
```bash
# Backup PostgreSQL database
pg_dump dbname > backup.sql
```

**Processed Files**
```bash
xcopy d:\saledeed_2025\sale_deed_processor\backend\data d:\backup\data /E /I
```

**Frontend Settings**
- LocalStorage (theme) stored in Electron user data
- Location: `%APPDATA%\SaleDeed Processor\`

### Restore Data

**Database**
```bash
psql dbname < backup.sql
```

**Files**
```bash
xcopy d:\backup\data d:\saledeed_2025\sale_deed_processor\backend\data /E /I
```

## Uninstallation

### Uninstall Application

**Windows**
1. Open Settings → Apps
2. Find "SaleDeed Processor"
3. Click Uninstall

### Remove Development Files

```bash
# Remove node_modules (saves space)
cd d:\saledeed_2025\fronted
rmdir /S /Q node_modules

# Remove build files
rmdir /S /Q build
rmdir /S /Q dist
```

### Clean Reinstall

```bash
# Remove everything
rmdir /S /Q node_modules build dist

# Reinstall
npm install
```

## Getting Help

### Check Logs

**React Console**
- Press F12 in Electron
- Check Console tab
- Look for red errors

**Backend Logs**
- Check terminal running backend
- Look for stack traces

**Electron Main Process**
- Check terminal running electron-dev
- Shows main process logs

### Common Log Messages

**"Compiled successfully!"**
✓ React app ready

**"webpack compiled with X warnings"**
⚠ Check warnings, usually safe to ignore

**"ECONNREFUSED"**
✗ Backend not running

**"404 Not Found"**
✗ API endpoint issue, check backend

**"Failed to fetch"**
✗ Network issue or CORS problem

## Next Steps

After successful installation:

1. **Read Documentation**
   - README.md: Overview and features
   - QUICKSTART.md: Quick reference
   - PROJECT_OVERVIEW.md: Technical details

2. **Process Test Documents**
   - Upload sample PDFs
   - Run processing
   - Check data extraction quality

3. **Customize**
   - Adjust theme colors
   - Change polling intervals
   - Add custom branding

4. **Deploy**
   - Build installer
   - Distribute to users
   - Set up network backend if needed

## Support

For issues not covered in this guide:
1. Check Console logs (F12)
2. Check backend logs
3. Verify all prerequisites installed
4. Try clean reinstall
5. Check PROJECT_OVERVIEW.md for architecture details

---

**Installation Guide Version**: 1.0.0
**Last Updated**: 2025-11-28
