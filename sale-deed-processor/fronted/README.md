# SaleDeed Processor - Frontend

Electron + React desktop application for managing and processing Sale Deed PDFs.

## Features

- **Control Panel**
  - Upload single or multiple PDF files
  - Start/Stop PDF processing (OCR + LLM extraction)
  - Start/Stop Vision processing (Registration fee extraction)
  - Real-time processing statistics and progress tracking

- **Data View**
  - Excel-like table display with database data
  - Document ID row spanning for multiple buyers/sellers
  - Search functionality across all fields
  - Download Excel files (both from database and client-side)
  - Responsive table with sticky headers and first column

- **System Features**
  - Dark/Light theme switcher
  - Health check monitoring
  - System info display (CUDA, Tesseract, Ollama, YOLO, Poppler)
  - Folder statistics
  - Runs as standalone desktop application (no browser needed)

## Prerequisites

- Node.js 18+ and npm
- Backend API running at `http://localhost:8000`

## Installation

```bash
# Install dependencies
npm install
```

## Running the Application

### Development Mode

```bash
# Start React development server and Electron
npm run electron-dev
```

The application will:
1. Start React dev server on `http://localhost:3000`
2. Wait for the server to be ready
3. Launch Electron window
4. Hot reload on code changes

### Production Build

```bash
# Build React app
npm run build

# Run Electron with production build
npm run electron

# Or build desktop installer
npm run dist
```

## Project Structure

```
fronted/
├── public/
│   └── index.html              # HTML template
├── src/
│   ├── components/
│   │   ├── Layout.js           # Main layout with header/footer
│   │   └── Footer.js           # Footer with system info
│   ├── context/
│   │   └── ThemeContext.js     # Theme management
│   ├── pages/
│   │   ├── ControlPanel.js     # Processing control page
│   │   └── DataView.js         # Data table viewer
│   ├── services/
│   │   └── api.js              # API service layer
│   ├── styles/
│   │   ├── App.css             # Global styles
│   │   ├── Layout.css          # Layout styles
│   │   ├── Footer.css          # Footer styles
│   │   ├── ControlPanel.css    # Control panel styles
│   │   └── DataView.css        # Data view styles
│   ├── App.js                  # Main App component
│   └── index.js                # React entry point
├── electron/
│   └── main.js                 # Electron main process
├── package.json                # Dependencies and scripts
└── README.md                   # This file
```

## API Endpoints Used

### Upload
- `POST /api/upload` - Upload PDF files

### Processing Control
- `POST /api/process/start` - Start PDF processing
- `POST /api/process/stop` - Stop PDF processing
- `GET /api/process/stats` - Get processing statistics

### Vision Processing
- `POST /api/vision/start` - Start vision processing
- `POST /api/vision/stop` - Stop vision processing
- `GET /api/vision/stats` - Get vision statistics

### Data Retrieval
- `GET /api/documents` - Get all documents (paginated)
- `GET /api/documents/{id}` - Get specific document
- `GET /api/export/excel` - Export to Excel (server-side)

### System
- `GET /health` - Health check
- `GET /api/system/info` - System information
- `GET /api/system/folders` - Folder statistics

## Features Detail

### Data View Table

The Data View implements an Excel-like table with:
- **Row Spanning**: Document ID and property details span multiple rows when there are multiple buyers/sellers
- **Sticky Headers**: Column headers remain visible while scrolling
- **Sticky First Column**: Document ID column stays fixed while scrolling horizontally
- **Search**: Real-time search across all fields
- **Download Options**:
  - Server-side: Downloads directly from database via API
  - Client-side: Exports currently loaded data using xlsx library

### Theme Switching

- Light and dark themes
- Theme preference saved to localStorage
- Smooth transitions between themes
- All components styled for both themes

### Real-time Updates

- Processing statistics update every 2 seconds
- System health info updates every 10 seconds
- Progress bars show real-time processing status

## Building for Distribution

### Windows

```bash
npm run dist
```

Creates installer in `dist/` folder.

### Configuration

Edit `package.json` > `build` section to customize:
- App ID
- Product name
- Icons
- Target platforms

## Troubleshooting

### Backend Connection Issues

Ensure backend is running:
```bash
cd ../backend
uvicorn app.main:app --reload
```

### Port Already in Use

If port 3000 is in use, React will prompt to use another port.

### Electron Window Not Opening

Check that `wait-on` is properly waiting for the dev server:
```bash
npm install wait-on --save-dev
```

## Development Tips

- Use Chrome DevTools in Electron (automatically opens in dev mode)
- Check Console for API errors
- Network tab shows API calls
- React DevTools works in Electron

## License

Proprietary - Internal Use Only
