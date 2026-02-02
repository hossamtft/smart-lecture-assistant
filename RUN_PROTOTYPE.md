# 🚀 How to Run the Smart Lecture Assistant Prototype

## Quick Start (3 Steps)

### Step 1: Start Database
Double-click `start-database.bat` or run in terminal:
```bash
cd docker
docker compose up -d
```

**Verify it's running:**
- Open Docker Desktop - you should see `lecture_assistant_db` container running
- Or visit http://localhost:5050 (pgAdmin)

### Step 2: Start Backend
**Open a NEW terminal/command prompt**

Double-click `start-backend.bat` or run:
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

**Verify it's running:**
- You should see: `Application startup complete`
- Visit http://localhost:8000/docs (API documentation)
- You should see the interactive API interface

### Step 3: Start Frontend
**Open ANOTHER NEW terminal/command prompt**

Double-click `start-frontend.bat` or run:
```bash
cd frontend
npm run dev
```

**Verify it's running:**
- You should see: `Local: http://localhost:5173/`
- Your browser should open automatically
- Or manually visit http://localhost:5173

## 🎯 Access the Application

Once all three services are running:

### Main Application
**http://localhost:5173**

You'll see:
- Dashboard (home page)
- Upload (add lectures)
- Topics (view topic map)
- Q&A (chat interface)

### API Documentation
**http://localhost:8000/docs**

Interactive API where you can:
- Test all endpoints
- See request/response formats
- Try uploading files directly

### Database Admin
**http://localhost:5050**

Login with:
- Email: admin@admin.com
- Password: admin

## 📝 Test Workflow

### 1. Upload Lectures
1. Go to http://localhost:5173/upload
2. Drag and drop a PDF file (or click to select)
3. Fill in:
   - Module Code: `TEST101`
   - Week Number: `1`
   - Lecture Title: `Introduction to Testing`
4. Click "Upload Lecture"
5. Wait for processing (5-30 seconds)
6. You should see success message with chunks created

**Repeat for 2-3 more lectures** with different week numbers

### 2. Detect Topics
1. Go to http://localhost:5173/topics
2. Enter module code: `TEST101`
3. Click "Load Topics"
4. Click "Run Topic Detection"
5. Wait 30-60 seconds
6. You should see a graph with topic nodes and connections

### 3. Ask Questions
1. Go to http://localhost:5173/query
2. Enter module code: `TEST101`
3. Enable "Temporal Awareness"
4. Set current week to match your uploads
5. Type a question about your lecture content
6. Click "Send"
7. See answer with source citations!

## 🐛 Troubleshooting

### Database won't start
**Error:** `docker: command not found` or `docker compose: command not found`
- **Fix:** Install Docker Desktop from https://www.docker.com/products/docker-desktop/
- **Check:** Open Docker Desktop and ensure it's running

### Backend errors
**Error:** `python: command not found`
- **Fix:** Install Python 3.11+ from https://www.python.org/downloads/
- **Check:** Run `python --version` or `py --version`

**Error:** `ModuleNotFoundError`
- **Fix:** Make sure you activated virtual environment and installed dependencies:
  ```bash
  cd backend
  venv\Scripts\activate
  pip install -r requirements.txt
  ```

**Error:** `Connection refused` or database errors
- **Fix:** Make sure Docker database is running
- **Check:** Run `docker ps` to see running containers

**Error:** `Embedding model downloading`
- **Note:** First run downloads ~90MB model (sentence-transformers)
- **Wait:** This is normal and happens once

### Frontend errors
**Error:** `npm: command not found`
- **Fix:** Install Node.js 18+ from https://nodejs.org/
- **Check:** Run `node --version`

**Error:** `Module not found` or dependency errors
- **Fix:** Install dependencies:
  ```bash
  cd frontend
  npm install
  ```

**Error:** `Port 5173 already in use`
- **Fix:** Kill the process:
  ```bash
  netstat -ano | findstr :5173
  taskkill /PID <PID> /F
  ```

### API errors
**Error:** `LLM Provider error`
- **For Ollama:** Install and start Ollama from https://ollama.ai/
  ```bash
  ollama pull llama2
  ollama serve
  ```
- **For OpenAI:** Add your API key to `backend/.env`:
  ```
  LLM_PROVIDER=openai
  OPENAI_API_KEY=sk-your-key-here
  ```

## 🛑 Stopping Services

### Stop Frontend
Press `Ctrl+C` in the frontend terminal

### Stop Backend
Press `Ctrl+C` in the backend terminal

### Stop Database
```bash
cd docker
docker compose down
```

Or stop via Docker Desktop

## 🔄 Restarting

If you make changes:

**Backend code changes:**
- Server auto-reloads (no restart needed)

**Frontend code changes:**
- Vite auto-reloads (no restart needed)

**Database schema changes:**
- Stop backend
- Run: `alembic upgrade head`
- Restart backend

## 📊 Monitoring

### Check Backend Logs
Look at the backend terminal - you'll see:
- Incoming requests
- Processing status
- Errors (if any)

### Check Database
Use pgAdmin (http://localhost:5050) to:
- View tables
- Check uploaded lectures
- See embeddings
- Inspect topics

### Check Frontend Console
Open browser Developer Tools (F12):
- Console tab for errors
- Network tab for API calls

## ✅ Success Indicators

You'll know it's working when:

✅ Backend terminal shows: `Application startup complete`
✅ Frontend terminal shows: `Local: http://localhost:5173/`
✅ http://localhost:8000/docs loads successfully
✅ http://localhost:5173 shows the dashboard
✅ You can upload a file and see success message
✅ Topic detection completes and shows graph
✅ Questions return answers with sources

## 🎓 First-Time Setup Checklist

- [ ] Docker Desktop installed and running
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Git installed
- [ ] Code editor (VS Code recommended)
- [ ] Browser (Chrome/Firefox)
- [ ] (Optional) Ollama installed for local LLM

## 🆘 Getting Help

If you encounter issues:

1. Check the error message in the terminal
2. Look at the Troubleshooting section above
3. Check `backend/.env` is configured correctly
4. Ensure all ports are available (5173, 8000, 5432, 5050)
5. Try restarting Docker Desktop

## 🎉 Demo Script

For showing the prototype to others:

1. **Start everything** (3 terminals)
2. **Show Dashboard** - Overview and stats
3. **Upload 3 lectures** - Same module, different weeks
4. **Run topic detection** - Show the graph visualization
5. **Ask a question** - Demonstrate RAG with sources
6. **Show API docs** - Interactive Swagger UI

Estimated demo time: 10-15 minutes

---

**Need help?** Check QUICKSTART.md for detailed setup or IMPLEMENTATION_SUMMARY.md for technical details.
