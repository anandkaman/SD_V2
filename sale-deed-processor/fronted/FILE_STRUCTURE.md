# Frontend File Structure

## Complete File Tree

```
d:\saledeed_2025\fronted\
├── electron/
│   └── main.js                     # Electron main process entry point
│
├── public/
│   ├── index.html                  # HTML template
│   └── icon.png.txt               # Icon placeholder instructions
│
├── src/
│   ├── components/
│   │   ├── Layout.js              # Main layout with header and navigation
│   │   └── Footer.js              # Footer with health check and system info
│   │
│   ├── context/
│   │   └── ThemeContext.js        # Theme management (light/dark)
│   │
│   ├── pages/
│   │   ├── ControlPanel.js        # PDF upload and processing control
│   │   └── DataView.js            # Excel-like data table viewer
│   │
│   ├── services/
│   │   └── api.js                 # API service layer for backend calls
│   │
│   ├── styles/
│   │   ├── App.css                # Global styles and theme variables
│   │   ├── Layout.css             # Layout component styles
│   │   ├── Footer.css             # Footer component styles
│   │   ├── ControlPanel.css       # Control panel page styles
│   │   └── DataView.css           # Data view page styles
│   │
│   ├── App.js                     # Main App component with routing
│   └── index.js                   # React entry point
│
├── .gitignore                     # Git ignore rules
├── package.json                   # Dependencies and scripts
├── setup.bat                      # Windows setup script
├── start-dev.bat                  # Windows development startup script
├── README.md                      # Main documentation
├── QUICKSTART.md                  # Quick start guide
├── INSTALLATION_GUIDE.md          # Complete installation guide
├── PROJECT_OVERVIEW.md            # Technical overview and architecture
└── FILE_STRUCTURE.md             # This file
```

## File Descriptions

### Root Configuration Files

**package.json**
- NPM package configuration
- Dependencies: React, Electron, Axios, xlsx, etc.
- Scripts: start, build, electron-dev, dist
- Electron builder configuration

**.gitignore**
- Excludes node_modules, build, dist from git
- Standard React + Electron ignore rules

### Scripts

**setup.bat**
- Automated Windows setup
- Runs npm install
- Shows instructions

**start-dev.bat**
- Quick development startup
- Launches electron-dev mode

### Documentation

**README.md** (Main)
- Features overview
- Installation instructions
- API endpoints
- Project structure
- Usage guide

**QUICKSTART.md**
- First time setup for Windows
- Step-by-step usage guide
- Common troubleshooting

**INSTALLATION_GUIDE.md**
- Detailed installation steps
- Prerequisites setup
- Configuration options
- Advanced deployment

**PROJECT_OVERVIEW.md**
- Architecture details
- Implementation notes
- Data flow diagrams
- Future enhancements

**FILE_STRUCTURE.md** (This file)
- Complete file tree
- File descriptions
- Purpose of each file

### Electron Files

**electron/main.js**
- Creates BrowserWindow
- Loads React app (dev or prod)
- Manages app lifecycle
- Platform-specific behavior

### Public Assets

**public/index.html**
- HTML template for React
- Single div#root element
- Meta tags and title

**public/icon.png.txt**
- Instructions to add app icon
- Recommended sizes and sources

### Source Files

#### Components

**src/components/Layout.js**
- Main app layout wrapper
- Header with logo and navigation
- Theme toggle button
- Menu bar (Control Panel, Data View)
- Wraps page content
- Includes Footer

**src/components/Footer.js**
- Health status display
- System info (CUDA, Tesseract, Ollama, YOLO, Poppler)
- Folder statistics
- Auto-refresh every 10 seconds
- Visual status indicators

#### Context

**src/context/ThemeContext.js**
- React Context for theme state
- Light/Dark theme toggle
- LocalStorage persistence
- Theme provider wrapper

#### Pages

**src/pages/ControlPanel.js**
- PDF file upload interface
- Multi-file selection support
- PDF processing controls (start/stop)
- Vision processing controls (start/stop)
- Real-time statistics display
- Progress bars and status badges
- Updates every 2 seconds

**src/pages/DataView.js**
- Excel-like data table
- Document ID rowspan for multiple buyers/sellers
- Sticky header and first column
- Search across all fields
- Download Excel (server and client-side)
- Refresh data button
- Row count display

#### Services

**src/services/api.js**
- Axios HTTP client
- Base URL configuration
- All API endpoint wrappers:
  - Upload: uploadPDFs
  - Process: start, stop, stats
  - Vision: start, stop, stats
  - Data: getDocuments, getDocument, exportToExcel
  - System: healthCheck, getSystemInfo, getFolderStats
- Error handling
- Blob response for Excel downloads

#### Styles

**src/styles/App.css**
- CSS variable definitions
- Light theme colors
- Dark theme colors
- Global reset styles
- Utility classes (.spin, .btn, .alert)
- Button variants (primary, secondary, success, danger)
- Alert variants (success, error, warning)
- Loading and empty states

**src/styles/Layout.css**
- App container layout
- Header styling (fixed, sticky)
- Logo and navigation
- Theme toggle button
- Main content area
- Responsive design

**src/styles/Footer.css**
- Footer container
- Three-column grid
- Status icons (green/red checkmarks)
- Stats grid layout
- Footer bottom section

**src/styles/ControlPanel.css**
- Panel sections
- Upload area (drag & drop ready)
- File list display
- Control buttons
- Progress bars
- Stats cards and grids
- Status badges (running/idle)

**src/styles/DataView.css**
- Data table styling
- Sticky header and column
- Search box
- Table container with scroll
- Rowspan cell styling
- Hover effects
- Footer stats
- Responsive breakpoints

#### App Files

**src/App.js**
- Main App component
- Router setup (BrowserRouter)
- Routes configuration:
  - / → redirect to /control-panel
  - /control-panel → ControlPanel
  - /data → DataView
- ThemeProvider wrapper
- Layout wrapper

**src/index.js**
- React DOM rendering
- Root element mounting
- StrictMode wrapper

## File Dependencies

### Import Chain

```
index.js
  └─ App.js
      ├─ ThemeContext (Provider)
      ├─ Router
      └─ Layout
          ├─ Header (inline)
          ├─ Routes
          │   ├─ ControlPanel
          │   │   └─ api service
          │   └─ DataView
          │       └─ api service
          └─ Footer
              └─ api service

Theme Context used by:
  - Layout (theme toggle)
  - All CSS (via body class)

API Service used by:
  - ControlPanel (all process APIs)
  - DataView (data and export APIs)
  - Footer (health and system APIs)
```

### Style Dependencies

```
App.css (global)
  ├─ Variables used by all components
  ├─ Utility classes used everywhere
  └─ Base styles

Component CSS files:
  - Layout.css (imports App.css variables)
  - Footer.css (imports App.css variables)
  - ControlPanel.css (imports App.css variables)
  - DataView.css (imports App.css variables)
```

## File Sizes (Approximate)

### Code Files
- main.js: ~1 KB
- index.html: ~0.5 KB
- Layout.js: ~2 KB
- Footer.js: ~4 KB
- ThemeContext.js: ~1 KB
- ControlPanel.js: ~10 KB
- DataView.js: ~12 KB
- api.js: ~3 KB
- App.js: ~1 KB
- index.js: ~0.3 KB

### Style Files
- App.css: ~4 KB
- Layout.css: ~2 KB
- Footer.css: ~2 KB
- ControlPanel.css: ~3 KB
- DataView.css: ~2 KB

### Documentation
- README.md: ~6 KB
- QUICKSTART.md: ~5 KB
- INSTALLATION_GUIDE.md: ~12 KB
- PROJECT_OVERVIEW.md: ~16 KB
- FILE_STRUCTURE.md: ~4 KB

**Total Source Code**: ~50 KB
**Total Documentation**: ~43 KB
**node_modules**: ~300-400 MB (after npm install)
**build**: ~1-2 MB (production build)

## Build Output

After `npm run build`:
```
build/
├── static/
│   ├── css/
│   │   └── main.[hash].css
│   └── js/
│       ├── main.[hash].js
│       └── [chunks].js
├── index.html
└── asset-manifest.json
```

After `npm run dist`:
```
dist/
├── SaleDeed Processor Setup 1.0.0.exe  (~100 MB)
├── win-unpacked/                        (~150 MB)
└── builder-*.yml
```

## Key Features by File

### Control Panel Features (ControlPanel.js)
- ✓ PDF upload (single/multiple)
- ✓ Start/Stop PDF processing
- ✓ Start/Stop Vision processing
- ✓ Real-time stats (2s polling)
- ✓ Progress bars
- ✓ Worker count display
- ✓ Success/Error alerts

### Data View Features (DataView.js)
- ✓ Excel-like table
- ✓ Document ID rowspan
- ✓ Sticky header
- ✓ Sticky first column
- ✓ Search functionality
- ✓ Excel download (server)
- ✓ Excel download (client)
- ✓ Refresh button
- ✓ Row count display

### Layout Features (Layout.js)
- ✓ Responsive header
- ✓ Logo and branding
- ✓ Menu navigation
- ✓ Active page highlight
- ✓ Theme toggle
- ✓ Smooth transitions

### Footer Features (Footer.js)
- ✓ Health check display
- ✓ System info (5 services)
- ✓ Folder statistics (4 folders)
- ✓ Auto-refresh (10s)
- ✓ Status icons
- ✓ Copyright info

### Theme Features (ThemeContext.js)
- ✓ Light/Dark themes
- ✓ LocalStorage persistence
- ✓ Global state management
- ✓ Smooth transitions
- ✓ CSS variable based

### API Features (api.js)
- ✓ 13 API methods
- ✓ Error handling
- ✓ FormData support
- ✓ Blob responses
- ✓ Centralized config

## Files to Modify for Customization

### Branding
- `src/components/Layout.js` → Logo and title
- `src/styles/App.css` → Colors and fonts
- `public/icon.png` → App icon

### API Configuration
- `src/services/api.js` → API_BASE_URL

### Polling Intervals
- `src/pages/ControlPanel.js` → Stats refresh (line ~25)
- `src/components/Footer.js` → Health refresh (line ~15)

### Table Columns
- `src/pages/DataView.js` → Column headers and data mapping

### Theme Colors
- `src/styles/App.css` → :root and body.dark variables

## Files You Shouldn't Modify

### Auto-generated
- `node_modules/` → Dependencies (reinstall if broken)
- `build/` → Production build (regenerated)
- `dist/` → Electron build (regenerated)

### Core Framework
- `public/index.html` → Minimal template (rarely change)
- `src/index.js` → React mounting (rarely change)

### Unless You Know What You're Doing
- `electron/main.js` → Electron config (affects window behavior)
- `package.json` → Dependencies (can break build)

## Missing Files (Need to Add)

### Icon
- `public/icon.png` → 512x512 PNG app icon
- Currently has `icon.png.txt` with instructions

### Optional Additions
- `.env` → Environment variables (API URL, etc.)
- `tests/` → Test files (not included)
- `docs/images/` → Screenshots for documentation
- `LICENSE` → License file

## File Checklist for Deployment

Before distributing to users:

- [ ] Add real icon: `public/icon.png`
- [ ] Update version in `package.json`
- [ ] Test all features in production build
- [ ] Update README.md with latest info
- [ ] Check all API endpoints work
- [ ] Test Excel downloads
- [ ] Verify theme switching
- [ ] Check footer health status
- [ ] Test on fresh Windows machine
- [ ] Create installer with `npm run dist`

---

**File Structure Version**: 1.0.0
**Total Files Created**: 28 files
**Lines of Code**: ~2,000 lines
**Last Updated**: 2025-11-28
