# Quick Start Guide

## First Time Setup on Windows

### Step 1: Install Node.js
1. Download Node.js from https://nodejs.org/ (LTS version recommended)
2. Run the installer
3. Verify installation:
   ```bash
   node --version
   npm --version
   ```

### Step 2: Install Dependencies
Run the setup script:
```bash
cd d:\saledeed_2025\fronted
setup.bat
```

Or manually:
```bash
npm install
```

### Step 3: Start Backend
Make sure the backend API is running:
```bash
cd d:\saledeed_2025\sale_deed_processor\backend
# Activate virtual environment
venv\Scripts\activate
# Start backend
uvicorn app.main:app --reload
```

Backend should be accessible at: http://localhost:8000

### Step 4: Start Frontend
In a new terminal:
```bash
cd d:\saledeed_2025\fronted
start-dev.bat
```

Or manually:
```bash
npm run electron-dev
```

## Using the Application

### Control Panel

1. **Upload PDFs**
   - Click the upload area or drag & drop PDF files
   - Select single or multiple files
   - Click "Upload PDFs" button

2. **Start PDF Processing**
   - Click "Start Processing" to begin OCR + LLM extraction
   - Monitor progress in real-time
   - Click "Stop Processing" to halt (current tasks will complete)

3. **Start Vision Processing**
   - Click "Start Vision" to extract registration fees from tables
   - Monitor progress and statistics
   - Click "Stop Vision" to halt

### Data View

1. **View Data**
   - Navigate to "Data View" from menu
   - Browse all processed documents in Excel-like table
   - Document IDs span multiple rows for multiple buyers/sellers

2. **Search**
   - Use search box to filter by any field
   - Results update in real-time

3. **Download Excel**
   - "Download Excel (DB)": Downloads from database via API
   - "Download Excel (Client)": Exports currently loaded data
   - Files saved to Downloads folder

### Theme Switching

- Click Sun/Moon icon in header
- Switches between light and dark themes
- Preference saved automatically

## Troubleshooting

### Backend Not Running
**Error**: "Failed to fetch documents" or connection errors

**Solution**: Start the backend server:
```bash
cd d:\saledeed_2025\sale_deed_processor\backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Port Already in Use
**Error**: "Port 3000 is already in use"

**Solution**: React will prompt to use another port. Press 'Y' to accept.

### Dependencies Not Installed
**Error**: Module not found errors

**Solution**: Run setup again:
```bash
npm install
```

### Electron Window Not Opening
**Error**: Window opens but shows blank screen

**Solution**:
1. Check if React dev server started (look for "Compiled successfully!")
2. Open DevTools (Ctrl+Shift+I) and check Console for errors
3. Verify backend is running at http://localhost:8000

### Database Empty
**Error**: "No documents found"

**Solution**:
1. Upload PDFs via Control Panel
2. Start processing
3. Wait for processing to complete
4. Refresh Data View

## Building for Production

### Create Executable

```bash
# Build React app
npm run build

# Create Windows installer
npm run dist
```

Installer will be created in `dist/` folder.

### Running Production Build

```bash
# Run built app
npm run electron
```

## API Configuration

Default API URL: `http://localhost:8000/api`

To change the backend URL, edit:
```javascript
// src/services/api.js
const API_BASE_URL = 'http://localhost:8000/api';
```

## File Locations

- **Frontend Code**: `d:\saledeed_2025\fronted\`
- **Backend Code**: `d:\saledeed_2025\sale_deed_processor\backend\`
- **PDFs to Upload**: Place in any folder, upload via UI
- **Processed PDFs**: `d:\saledeed_2025\sale_deed_processor\backend\data\processed\`
- **Failed PDFs**: `d:\saledeed_2025\sale_deed_processor\backend\data\failed\`

## Support

For issues or questions:
1. Check Console logs (F12 in Electron)
2. Check backend logs
3. Verify all prerequisites are installed
4. Refer to README.md for detailed documentation
