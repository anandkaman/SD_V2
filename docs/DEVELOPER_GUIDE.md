# SaleDeed Processor - Developer Guide v1.0

**Target Audience**: Software Developers, Contributors
**Last Updated**: December 2024

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Code Standards](#code-standards)
5. [Adding Features](#adding-features)
6. [Testing](#testing)
7. [Debugging](#debugging)
8. [Common Tasks](#common-tasks)
9. [Contributing](#contributing)

---

## Getting Started

### Development Environment Setup

1. **Install Prerequisites**:
   - Python 3.11+
   - Node.js 18+
   - PostgreSQL 13+
   - Tesseract OCR
   - Poppler
   - Git

2. **Clone Repository**:
   ```bash
   git clone https://github.com/Nitinkaroshi/salesdeed.git
   cd salesdeed
   ```

3. **Setup Backend**:
   ```bash
   cd sale-deed-processor/sale_deed_processor/backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Setup Frontend**:
   ```bash
   cd fronted
   npm install
   ```

5. **Configure Environment**:
   - Copy `.env.example` to `.env`
   - Add your API keys

6. **Initialize Database**:
   ```bash
   createdb sale_deed_db
   cd backend
   python init_db.py
   ```

---

## Project Structure

### Repository Layout

```
salesdeed/
├── README.md                           # Main README
├── .gitignore                          # Git ignore rules
├── docs/                               # Technical documentation
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA_DESIGN.md
│   ├── ARCHITECTURE_DESIGN.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   └── SYSTEM_CONFIGURATION.md
│
└── sale-deed-processor/
    ├── fronted/                        # React + Electron UI
    │   ├── src/
    │   │   ├── components/             # Reusable components
    │   │   ├── pages/                  # Page components
    │   │   ├── services/               # API client
    │   │   ├── context/                # React context
    │   │   ├── styles/                 # CSS files
    │   │   ├── App.js                  # Main app
    │   │   └── index.js                # Entry point
    │   ├── electron/
    │   │   └── main.js                 # Electron main process
    │   ├── public/                     # Static assets
    │   └── package.json
    │
    └── sale_deed_processor/
        ├── backend/
        │   ├── app/
        │   │   ├── main.py             # FastAPI app
        │   │   ├── config.py           # Configuration
        │   │   ├── database.py         # DB connection
        │   │   ├── models.py           # SQLAlchemy models
        │   │   ├── schemas.py          # Pydantic schemas
        │   │   ├── api/
        │   │   │   └── routes.py       # REST endpoints
        │   │   ├── services/           # Business logic
        │   │   │   ├── ocr_service.py
        │   │   │   ├── llm_service*.py
        │   │   │   ├── vision_service*.py
        │   │   │   ├── pdf_processor*.py
        │   │   │   └── yolo_detector.py
        │   │   ├── workers/            # Batch processors
        │   │   │   ├── batch_processor.py
        │   │   │   ├── pipeline_processor_v2.py
        │   │   │   └── vision_batch_processor.py
        │   │   └── utils/              # Utilities
        │   │       ├── file_handler.py
        │   │       └── prompts.py
        │   └── requirements.txt
        │
        ├── models/                     # ML models
        │   └── table1.19.1.onnx
        │
        └── data/                       # Processing folders
            ├── newly_uploaded/
            ├── processed/
            ├── failed/
            ├── left_over_reg_fee/
            └── vision_failed/
```

---

## Development Workflow

### 1. Start Development Servers

**Terminal 1 - Backend**:
```bash
cd sale-deed-processor/sale_deed_processor/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd fronted
npm run electron-dev
```

### 2. Make Changes

- **Backend**: Edit Python files in `backend/app/`
- **Frontend**: Edit React files in `fronted/src/`
- Changes auto-reload (backend with --reload, frontend with hot reload)

### 3. Test Changes

- Test API endpoints: Use Swagger UI at `http://localhost:8000/docs`
- Test UI: Interact with Electron app
- Check logs: Terminal output for errors

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature-branch
```

---

## Code Standards

### Python (Backend)

**Style Guide**: PEP 8

```python
# Good: Function with type hints and docstring
def extract_text(pdf_path: Path) -> str:
    """
    Extract text from PDF using OCR.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted text content
    """
    pass

# Bad: No type hints, no docstring
def extract_text(pdf_path):
    pass
```

**Naming Conventions**:
- Classes: `PascalCase` (e.g., `PDFProcessor`)
- Functions/variables: `snake_case` (e.g., `extract_text`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_WORKERS`)

**Imports**:
```python
# Standard library
import os
from pathlib import Path

# Third-party
from fastapi import APIRouter
from sqlalchemy.orm import Session

# Local
from app.config import settings
from app.models import DocumentDetail
```

### JavaScript (Frontend)

**Style Guide**: Airbnb JavaScript Style Guide

```javascript
// Good: Arrow function with clear naming
const fetchDocuments = async (skip = 0, limit = 100) => {
  try {
    const response = await api.get('/documents', { params: { skip, limit } });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch documents:', error);
    throw error;
  }
};

// Bad: No error handling
const fetchDocuments = (skip, limit) => {
  return api.get('/documents', { params: { skip, limit } }).then(r => r.data);
};
```

**Naming Conventions**:
- Components: `PascalCase` (e.g., `ControlPanel`)
- Functions/variables: `camelCase` (e.g., `fetchDocuments`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)

**React Components**:
```javascript
// Functional component with hooks
const ControlPanel = () => {
  const [files, setFiles] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    // Fetch stats every 2 seconds
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="control-panel">
      {/* Component JSX */}
    </div>
  );
};
```

### SQL

**Style Guide**: Uppercase keywords, lowercase identifiers

```sql
-- Good
SELECT document_id, transaction_date
FROM document_details
WHERE batch_id = 'BATCH_20241223_130000_a1b2c3d4'
ORDER BY created_at DESC;

-- Bad
select * from document_details where batch_id='BATCH_20241223_130000_a1b2c3d4';
```

---

## Adding Features

### Adding a New API Endpoint

1. **Define Schema** (`backend/app/schemas.py`):
```python
class NewFeatureRequestSchema(BaseModel):
    param1: str
    param2: int

class NewFeatureResponseSchema(BaseModel):
    result: str
    status: str
```

2. **Add Route** (`backend/app/api/routes.py`):
```python
@router.post("/new-feature", response_model=NewFeatureResponseSchema)
async def new_feature_endpoint(
    request: NewFeatureRequestSchema,
    db: Session = Depends(get_db)
):
    """
    Description of what this endpoint does.
    """
    try:
        # Your logic here
        result = do_something(request.param1, request.param2)

        return {
            "result": result,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"New feature error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

3. **Add Frontend API Call** (`fronted/src/services/api.js`):
```javascript
export const newFeature = async (param1, param2) => {
  const response = await api.post('/new-feature', {
    param1,
    param2
  });
  return response.data;
};
```

4. **Use in Component**:
```javascript
const handleNewFeature = async () => {
  try {
    const result = await newFeature('value1', 123);
    console.log('Feature result:', result);
  } catch (error) {
    console.error('Feature failed:', error);
  }
};
```

### Adding a New Database Table

1. **Define Model** (`backend/app/models.py`):
```python
class NewTable(Base):
    __tablename__ = "new_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    value = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    related_id = Column(Integer, ForeignKey("other_table.id"))
    related = relationship("OtherTable", back_populates="new_items")
```

2. **Define Schema** (`backend/app/schemas.py`):
```python
class NewTableSchema(BaseModel):
    id: int
    name: str
    value: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

3. **Create Migration**:
```bash
alembic revision --autogenerate -m "Add new_table"
alembic upgrade head
```

Or manual SQL migration in `backend/app/migrations/`:
```sql
-- add_new_table.sql
CREATE TABLE new_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    value INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    related_id INTEGER REFERENCES other_table(id)
);

CREATE INDEX idx_new_table_related_id ON new_table(related_id);
```

### Adding a New LLM Backend

1. **Create Service** (`backend/app/services/my_llm_service.py`):
```python
import requests
import logging

logger = logging.getLogger(__name__)

class MyLLMService:
    """Integration with My LLM API"""

    def __init__(self, api_key: str, model: str = "default-model"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.myllm.com/v1"

    def extract_structured_data(self, text: str, prompt: str) -> dict:
        """Extract structured data using My LLM"""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": text}
                    ],
                    "temperature": 0.6,
                    "max_tokens": 16384
                },
                timeout=300
            )

            response.raise_for_status()
            result = response.json()

            # Parse response
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)

        except Exception as e:
            logger.error(f"My LLM error: {e}")
            raise
```

2. **Update Factory** (`backend/app/services/llm_service_factory.py`):
```python
from app.services.my_llm_service import MyLLMService

def get_llm_service(backend: str = None):
    backend = backend or settings.LLM_BACKEND

    if backend == "gemini":
        return GeminiLLMService(settings.GEMINI_API_KEY)
    elif backend == "my_llm":
        return MyLLMService(settings.MY_LLM_API_KEY)
    # ... other backends
```

3. **Update Config** (`backend/app/config.py`):
```python
class Settings(BaseSettings):
    # ... existing settings
    MY_LLM_API_KEY: str = ""
```

---

## Testing

### Manual Testing

1. **Test API Endpoints** (Swagger UI):
   - Navigate to `http://localhost:8000/docs`
   - Try each endpoint with sample data
   - Verify responses

2. **Test UI Workflows**:
   - Upload PDFs
   - Start/Stop processing
   - View data table
   - Export Excel
   - Test search and filters

3. **Test Error Cases**:
   - Upload invalid files
   - Test with empty database
   - Disconnect database and test error handling

### Unit Testing (Future)

**Backend Tests** (`backend/tests/test_services.py`):
```python
import pytest
from app.services.ocr_service import OCRService

def test_ocr_extraction():
    ocr = OCRService()
    text = ocr.extract_text("sample.pdf")
    assert len(text) > 0
    assert "Sale Deed" in text
```

**Frontend Tests** (`fronted/src/tests/ControlPanel.test.js`):
```javascript
import { render, screen } from '@testing-library/react';
import ControlPanel from './pages/ControlPanel';

test('renders upload button', () => {
  render(<ControlPanel />);
  const button = screen.getByText(/Choose Files/i);
  expect(button).toBeInTheDocument();
});
```

---

## Debugging

### Backend Debugging

**Enable Debug Logging**:
```python
# backend/app/main.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Use Python Debugger**:
```python
import pdb

def process_pdf(pdf_path):
    pdb.set_trace()  # Debugger breakpoint
    # Your code here
```

**VS Code Launch Configuration** (`.vscode/launch.json`):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false,
      "cwd": "${workspaceFolder}/sale-deed-processor/sale_deed_processor/backend"
    }
  ]
}
```

### Frontend Debugging

**Chrome DevTools**:
- Press `F12` in Electron app
- Use Console, Network, and React DevTools tabs

**React DevTools Extension**:
```bash
npm install -g react-devtools
react-devtools
```

**Console Logging**:
```javascript
console.log('Processing stats:', stats);
console.error('Upload failed:', error);
```

### Database Debugging

**Query Logs**:
```python
# backend/app/database.py
engine = create_engine(
    settings.DATABASE_URL,
    echo=True  # Enable SQL query logging
)
```

**Inspect Database**:
```bash
psql -U postgres sale_deed_db

\dt                    # List tables
\d document_details    # Describe table
SELECT COUNT(*) FROM document_details;
```

---

## Common Tasks

### Add a New Configuration Setting

1. **Update Config** (`backend/app/config.py`):
```python
class Settings(BaseSettings):
    NEW_SETTING: str = "default_value"
```

2. **Use in Code**:
```python
from app.config import settings

def some_function():
    value = settings.NEW_SETTING
```

3. **Add to .env**:
```env
NEW_SETTING=production_value
```

### Modify LLM Prompt

Edit `backend/app/utils/prompts.py`:

```python
def get_sale_deed_extraction_prompt() -> str:
    return """
You are an AI assistant specialized in extracting structured data from Indian property sale deed documents.

Extract the following information:
1. Document ID
2. Transaction Date
3. ... (your changes here)

Return ONLY a JSON object with no additional text.
"""
```

### Add New Excel Column

1. **Modify Export Logic** (`backend/app/api/routes.py`):
```python
# In export_to_excel endpoint
base_row = {
    # ... existing columns
    "New_Column": doc.new_field,  # Add new column
}

# Update column_order list
column_order = [
    # ... existing columns
    "New_Column"
]
```

2. **Update Database** if new field:
```python
# backend/app/models.py
class DocumentDetail(Base):
    # ... existing fields
    new_field = Column(String, nullable=True)
```

---

## Contributing

### Git Workflow

1. **Create Feature Branch**:
```bash
git checkout -b feature/my-new-feature
```

2. **Make Changes and Commit**:
```bash
git add .
git commit -m "feat: add new feature description"
```

3. **Push Branch**:
```bash
git push origin feature/my-new-feature
```

4. **Create Pull Request** (if applicable)

### Commit Message Convention

Use **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Add/update tests
- `chore`: Build process, dependencies

**Examples**:
```
feat(api): add batch filtering to export endpoint

Added query parameters to filter Excel export by batch IDs.
Supports comma-separated list of batch IDs.

Closes #123
```

```
fix(ocr): handle empty PDF pages gracefully

OCR now skips empty pages instead of crashing.
```

---

## Best Practices

### Code Quality

1. **Write Readable Code**: Use descriptive variable names, add comments for complex logic
2. **Keep Functions Small**: Single responsibility principle
3. **Handle Errors**: Always use try-except blocks for external operations
4. **Validate Input**: Use Pydantic schemas for API requests
5. **Log Appropriately**: Use logging levels (DEBUG, INFO, WARNING, ERROR)

### Performance

1. **Use Async/Await**: For I/O-bound operations
2. **Eager Loading**: Use `joinedload()` for relationships
3. **Pagination**: Always paginate large result sets
4. **Index Wisely**: Add indexes for frequently queried columns

### Security

1. **Never Commit Secrets**: Use `.env` for API keys
2. **Validate File Uploads**: Check file types and sizes
3. **Sanitize Inputs**: Prevent SQL injection with ORM
4. **Use HTTPS**: For production deployments

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Electron Docs**: https://www.electronjs.org/docs
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

**Document Version**: 1.0
**Last Updated**: December 23, 2024
