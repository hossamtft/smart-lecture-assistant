# Quick Start Guide

Get the Smart Lecture Assistant running in under 5 minutes.

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python --version  # or py --version on Windows

# Check Node.js version (need 18+)
node --version

# Check Docker
docker --version
```

## Step 1: Start Database (1 minute)

```bash
cd docker
docker-compose up -d
```

Verify it's running:
- PostgreSQL: `docker ps` should show `lecture_assistant_db`
- pgAdmin: Visit http://localhost:5050 (admin@admin.com / admin)

## Step 2: Set Up Backend (2 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env  # Windows
# cp .env.example .env  # Mac/Linux

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

Backend is now running at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Interactive API docs)

## Step 3: Set Up Frontend (2 minutes)

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend is now running at: http://localhost:5173

## Test the Setup

### 1. Check Backend Health

Visit http://localhost:8000/docs and try the `/health` endpoint.

### 2. Test File Upload

Using the interactive docs at http://localhost:8000/docs:

1. Find `POST /api/lectures/upload`
2. Click "Try it out"
3. Upload a PDF file
4. Fill in:
   - `module_code`: TEST101
   - `week_number`: 1
   - `lecture_title`: Test Lecture
5. Click "Execute"

You should see a success response with the lecture details.

### 3. View Uploaded Lectures

Try `GET /api/lectures` to see your uploaded lecture.

## Common Issues

### Database Connection Error

```
Check:
1. Is Docker running? (docker ps)
2. Is PostgreSQL container up? (docker logs lecture_assistant_db)
3. Is DATABASE_URL correct in .env?
```

### Embedding Model Download

On first run, sentence-transformers will download the model (∼90MB). This is one-time and automatic.

### Port Already in Use

```bash
# Backend (port 8000)
# Kill process on Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Frontend (port 5173)
# Kill process on Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

## What's Working

✅ Database with pgvector extension
✅ PDF upload and text extraction
✅ Automatic text chunking
✅ Embedding generation (local or OpenAI)
✅ Vector storage with similarity search
✅ RESTful API with OpenAPI docs
✅ React frontend with routing

## What's Next

The following features are in progress:

🔧 Topic detection across lectures
🔧 RAG-based Q&A system
🔧 Interactive topic map visualization
🔧 Timeline view of topics

## Development Workflow

### Backend Changes

```bash
# The server auto-reloads on file changes
# Check logs in terminal for errors

# Run tests (when available)
pytest

# Format code
black app/
```

### Frontend Changes

```bash
# Vite auto-reloads on file changes
# Check browser console for errors

# Build for production
npm run build
```

### Database Changes

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## Testing with Sample Data

### Create Test Module

```bash
# Use the API docs at http://localhost:8000/docs
# Upload 3-5 PDFs with:
# - Same module_code: COMP3001
# - Different week_number: 1, 2, 3, etc.
# - Different titles
```

### Query Lectures

```python
import requests

# Get all lectures
response = requests.get("http://localhost:8000/api/lectures")
print(response.json())

# Filter by module
response = requests.get("http://localhost:8000/api/lectures?module_code=COMP3001")
print(response.json())
```

## Stopping Services

```bash
# Stop backend: Ctrl+C in terminal

# Stop frontend: Ctrl+C in terminal

# Stop database:
cd docker
docker-compose down

# Remove database data (careful!):
docker-compose down -v
```

## Getting Help

- **API Documentation**: http://localhost:8000/docs
- **Backend Logs**: Check terminal running uvicorn
- **Database**: Use pgAdmin at http://localhost:5050
- **Frontend Logs**: Check browser developer console

## Next Steps

1. Try uploading lecture PDFs
2. Explore the API endpoints in the docs
3. Check the generated embeddings in the database
4. Start building frontend components for visualization

Happy developing! 🚀
