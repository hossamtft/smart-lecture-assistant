# Smart Lecture Assistant - Backend

FastAPI backend for the Smart Lecture Assistant application.

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For development:
```bash
pip install -r requirements-dev.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```

### 5. Start Database

Navigate to the docker directory and start PostgreSQL:
```bash
cd ../docker
docker-compose up -d
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   ├── config.py         # Configuration
│   ├── database.py       # Database setup
│   └── main.py           # FastAPI app
├── tests/                # Unit tests
├── requirements.txt      # Production dependencies
└── requirements-dev.txt  # Development dependencies
```

## Development

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
isort app/
```

### Type Checking
```bash
mypy app/
```

## API Endpoints

Coming soon...
