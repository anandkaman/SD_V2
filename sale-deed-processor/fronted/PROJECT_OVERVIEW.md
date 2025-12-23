# SaleDeed Processor Frontend - Project Overview

## Architecture

### Technology Stack
- **Framework**: Electron.js (Desktop Application)
- **UI Library**: React 18
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Excel Export**: xlsx (SheetJS)
- **Icons**: Lucide React
- **Build Tool**: React Scripts (Create React App)
- **Package Manager**: npm

### Application Structure

```
Electron Desktop App
├── Main Process (electron/main.js)
│   └── Creates native window, manages lifecycle
└── Renderer Process (React App)
    ├── Theme Context (Light/Dark)
    ├── API Service Layer
    ├── Pages (Control Panel, Data View)
    └── Shared Components (Layout, Footer)
```

## Key Features Implementation

### 1. Control Panel (`src/pages/ControlPanel.js`)

**PDF Upload**
- Multi-file selection support
- Drag & drop capability (UI ready)
- File validation (PDF only)
- Upload progress feedback
- API: `POST /api/upload`

**PDF Processing Control**
- Start/Stop batch processing
- Real-time statistics polling (2s interval)
- Progress bar with percentage
- Worker count display
- API: `POST /api/process/start`, `POST /api/process/stop`, `GET /api/process/stats`

**Vision Processing Control**
- Start/Stop vision extraction
- Separate progress tracking
- Registration fee table extraction
- API: `POST /api/vision/start`, `POST /api/vision/stop`, `GET /api/vision/stats`

### 2. Data View (`src/pages/DataView.js`)

**Excel-like Table Display**
- Database columns mapped to table headers
- Document ID with rowspan for multiple buyers/sellers
- Sticky header row (stays visible on scroll)
- Sticky first column (Document ID stays visible on horizontal scroll)
- Responsive design

**Row Spanning Logic**
```javascript
// For each document:
// - Get max count of buyers/sellers
// - Create that many rows
// - First row: span document ID and property columns
// - All rows: show buyer/seller data side-by-side
```

**Search Functionality**
- Real-time filter across all fields
- Case-insensitive matching
- Searches: Document ID, names, addresses
- Updates table instantly

**Excel Download**
- **Server-side**: API generates Excel from database
  - Handles large datasets efficiently
  - Direct database query
  - API: `GET /api/export/excel`

- **Client-side**: xlsx library generates from loaded data
  - Works offline
  - Uses currently filtered/loaded data
  - Good for quick exports of visible data

### 3. Theme System (`src/context/ThemeContext.js`)

**Implementation**
- React Context API for global state
- LocalStorage persistence
- CSS variables for theming
- Smooth transitions

**Theme Variables**
```css
Light Theme:
- Background: #ffffff, #f5f5f5
- Text: #1a1a1a, #666666
- Accent: #2563eb

Dark Theme:
- Background: #1a1a1a, #2a2a2a
- Text: #f0f0f0, #b0b0b0
- Accent: #3b82f6
```

### 4. Footer (`src/components/Footer.js`)

**System Health Check**
- API health status
- Auto-refresh every 10 seconds
- Visual indicators (checkmarks/x-marks)

**System Information**
- CUDA availability and device count
- Tesseract OCR status
- Ollama LLM connection
- YOLO model loaded status
- Poppler availability

**Folder Statistics**
- Newly uploaded PDF count
- Processed PDF count
- Failed PDF count
- Left over registration fee images count

### 5. API Service Layer (`src/services/api.js`)

**Centralized API Client**
- Axios instance with base URL
- Consistent error handling
- All backend endpoints wrapped
- File upload with FormData
- Blob responses for Excel downloads

**Endpoints Coverage**
```javascript
Upload: uploadPDFs(files)
Process: startProcessing(), stopProcessing(), getProcessingStats()
Vision: startVisionProcessing(), stopVisionProcessing(), getVisionStats()
Data: getDocuments(), getDocument(id), exportToExcel()
System: getSystemInfo(), getFolderStats(), healthCheck()
```

## Data Flow

### Upload & Processing Flow
```
User selects PDFs
    ↓
Upload to /api/upload
    ↓
PDFs stored in newly_uploaded/
    ↓
User clicks Start Processing
    ↓
Backend processes with OCR + LLM
    ↓
Stats update every 2 seconds
    ↓
Processed PDFs moved to processed/
    ↓
Data saved to database
    ↓
Available in Data View
```

### Data View Flow
```
Component mounts
    ↓
Fetch documents from API
    ↓
Transform data for display
    ↓
Group by document_id
    ↓
Apply rowspan logic
    ↓
Render Excel-like table
    ↓
User searches → Filter rows
    ↓
User downloads → Export to Excel
```

## Database Schema to UI Mapping

### Database Tables
1. **document_details**
   - document_id (PK)
   - transaction_date
   - registration_office

2. **property_details**
   - document_id (FK)
   - total_land_area
   - address, pincode, state
   - sale_consideration
   - stamp_duty_fee
   - registration_fee
   - guidance_value

3. **buyer_details**
   - document_id (FK)
   - name, gender
   - aadhaar_number, pan_card_number
   - address, pincode, state
   - phone_number, secondary_phone_number, email

4. **seller_details**
   - document_id (FK)
   - (same fields as buyer)
   - property_share

### UI Table Columns (30 total)
```
Document ID | Transaction Date | Registration Office |
Land Area | Property Address | Property Pincode | Property State |
Sale Consideration | Stamp Duty | Registration Fee | Guidance Value |
Buyer Name | Buyer Gender | Buyer Aadhaar | Buyer PAN |
Buyer Address | Buyer Pincode | Buyer State | Buyer Phone | Buyer Email |
Seller Name | Seller Gender | Seller Aadhaar | Seller PAN |
Seller Address | Seller Pincode | Seller State | Seller Phone | Seller Email | Seller Share
```

### Rowspan Example
```
Document: DOC001 has 2 buyers, 3 sellers → Creates 3 rows

Row 1: [DOC001 (rowspan=3)] [Property Data (rowspan=3)] [Buyer1] [Seller1]
Row 2:                                                    [Buyer2] [Seller2]
Row 3:                                                    [-]      [Seller3]
```

## Styling Approach

### CSS Architecture
- **Global styles**: `App.css` (variables, utilities, buttons, alerts)
- **Component styles**: Separate CSS file per component
- **Theme variables**: CSS custom properties (--var-name)
- **No CSS framework**: Pure CSS for full control

### Responsive Design
- Desktop-first approach (Electron app)
- Breakpoints for smaller screens
- Flexible grids and flexbox
- Mobile considerations for future web version

### Design Principles
- Clean, professional interface
- Consistent spacing (8px grid)
- Clear visual hierarchy
- Accessible color contrasts
- Smooth transitions

## Development Workflow

### Hot Reload Development
```bash
npm run electron-dev
```
- Starts React dev server
- Waits for server ready
- Launches Electron
- Hot reload on save
- DevTools open automatically

### Production Build
```bash
npm run build    # Build React app
npm run dist     # Create installer
```

### File Watching
- React: Auto-reload on src/ changes
- Electron: Restart on electron/ changes

## Configuration Files

### package.json
- Dependencies
- Scripts
- Electron builder config
- Browserslist

### Electron Builder
```json
{
  "appId": "com.saledeed.processor",
  "productName": "SaleDeed Processor",
  "win": {
    "target": "nsis",
    "icon": "public/icon.png"
  }
}
```

## Performance Considerations

### Data Loading
- Pagination support in API (limit: 1000 default)
- Lazy loading for large datasets (future)
- Memoization for expensive renders (future)

### Stats Polling
- Control Panel: 2 second interval
- Footer: 10 second interval
- Cleanup on unmount

### Table Rendering
- Virtual scrolling for 1000+ rows (future optimization)
- Sticky positioning for headers/columns
- Efficient rowspan calculation

## Security Considerations

### No Sensitive Data Exposure
- API calls over localhost only
- No authentication (local network assumed)
- No data sent to external services

### File Handling
- PDF validation on upload
- File size checks (future)
- Malicious file scanning (future)

## Future Enhancements

### Planned Features
1. **Drag & Drop Upload** (UI ready, needs implementation)
2. **Virtual Scrolling** for large datasets
3. **Column Sorting** in Data View
4. **Column Filtering** per field
5. **Export to PDF** report generation
6. **Batch Operations** (delete, re-process)
7. **Data Editing** inline in table
8. **User Settings** (API URL, polling interval)
9. **Notifications** for process completion
10. **Multi-language Support** (Kannada, Hindi)

### Potential Improvements
- WebSocket for real-time updates (instead of polling)
- Offline mode with local caching
- Advanced search with filters
- Data visualization (charts, graphs)
- Audit logs for data changes
- User authentication for multi-user scenarios

## Troubleshooting Guide

### Common Issues

**1. Blank Electron Window**
- Check: React dev server started
- Check: Console errors (F12)
- Solution: Restart dev server

**2. API Connection Failed**
- Check: Backend running on port 8000
- Check: CORS enabled in backend
- Solution: Start backend first

**3. Data Not Loading**
- Check: Database has data
- Check: API response in Network tab
- Solution: Process PDFs first

**4. Excel Download Fails**
- Check: Backend /export/excel endpoint
- Check: Blob response handling
- Solution: Check API response type

**5. Theme Not Persisting**
- Check: LocalStorage enabled
- Check: Browser compatibility
- Solution: Clear cache, restart

## Deployment

### Desktop Distribution

**Windows**
```bash
npm run dist
```
Creates: `dist/SaleDeed Processor Setup X.X.X.exe`

**Installation**
- Double-click installer
- Follow wizard
- App installed to Program Files
- Desktop shortcut created
- Start menu entry added

### Network Deployment

**Shared Network Drive**
1. Build production version
2. Copy to network drive
3. Users run from network
4. Backend on central server

**Portable Version**
```bash
npm run pack
```
Creates unpacked app folder (no installation needed)

## Maintenance

### Updating Dependencies
```bash
npm update          # Update all
npm outdated        # Check versions
npm install pkg@latest  # Update specific
```

### Version Bumping
```bash
npm version patch   # 1.0.0 → 1.0.1
npm version minor   # 1.0.0 → 1.1.0
npm version major   # 1.0.0 → 2.0.0
```

### Log Files
- React: Browser console
- Electron: Main process console
- Backend: Backend logs

## Code Quality

### Best Practices Followed
- Component composition
- Single responsibility principle
- DRY (Don't Repeat Yourself)
- Consistent naming conventions
- Comments for complex logic
- Error handling throughout

### Code Style
- 2-space indentation
- Semicolons
- ES6+ features
- Functional components
- React Hooks

## Testing Strategy (Future)

### Recommended Testing
1. **Unit Tests**: Jest + React Testing Library
2. **Integration Tests**: API service tests
3. **E2E Tests**: Electron Spectron
4. **Manual Tests**: User acceptance testing

## Documentation

### Available Docs
- README.md: Main documentation
- QUICKSTART.md: Getting started guide
- PROJECT_OVERVIEW.md: This file
- Code comments: Inline documentation

## Support & Resources

### Internal Resources
- Backend API docs: http://localhost:8000/docs
- API documentation: api_doc_old.md

### External Resources
- React: https://react.dev/
- Electron: https://www.electronjs.org/
- React Router: https://reactrouter.com/
- Axios: https://axios-http.com/
- xlsx: https://sheetjs.com/

## License

Proprietary - Internal Use Only

---

**Last Updated**: 2025-11-28
**Version**: 1.0.0
**Author**: AI-Generated with Claude
