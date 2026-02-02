# Deployment Guide

This guide covers deploying the Smart Lecture Assistant in various environments.

## Development Deployment

### Local Development Setup

Already covered in main README. Quick reference:

```bash
# Terminal 1: Database
cd docker && docker-compose up

# Terminal 2: Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend
npm install && npm run dev
```

---

## Production Deployment

### Option 1: Docker Compose (Recommended for small deployments)

#### 1. Create Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: lecture_assistant
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/lecture_assistant
      LLM_PROVIDER: ${LLM_PROVIDER}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
    volumes:
      - ./uploads:/app/uploads
    networks:
      - app-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    depends_on:
      - backend
    ports:
      - "80:80"
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
```

#### 2. Create Backend Dockerfile

`backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3. Create Frontend Dockerfile

`frontend/Dockerfile`:

```dockerfile
FROM node:18 AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### 4. Create Nginx Configuration

`frontend/nginx.conf`:

```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Frontend routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://backend:8000/health;
    }
}
```

#### 5. Deploy

```bash
# Create .env file
cp .env.example .env
# Edit .env with production values

# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

### Option 2: Cloud Deployment (AWS/Azure/GCP)

#### Architecture

```
┌──────────────┐
│   CloudFront │  (CDN for frontend)
│   or Nginx   │
└──────┬───────┘
       │
  ┌────▼─────┐      ┌──────────────┐
  │ Frontend │      │   Backend    │
  │  (S3 or  │      │ (EC2/ECS or  │
  │  Static) │      │  Cloud Run)  │
  └──────────┘      └──────┬───────┘
                           │
                    ┌──────▼────────┐
                    │  PostgreSQL   │
                    │   (RDS/Cloud  │
                    │      SQL)     │
                    └───────────────┘
```

#### AWS Deployment Steps

1. **Database**: Use RDS PostgreSQL with pgvector
2. **Backend**: Deploy to ECS Fargate or EC2
3. **Frontend**: Host on S3 + CloudFront
4. **Secrets**: Store API keys in AWS Secrets Manager
5. **Monitoring**: Use CloudWatch for logs

#### Environment Variables for Production

```env
# Database (Use managed service)
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/lecture_assistant

# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=<your-key>

# Embedding Provider
EMBEDDING_PROVIDER=openai

# CORS (Your domain)
CORS_ORIGINS=https://your-domain.com

# Disable debug mode
DEBUG=False
RELOAD=False
```

---

## Database Migration

### Initial Setup

```bash
cd backend

# Install Alembic (included in requirements.txt)
pip install alembic

# Initialize Alembic
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### Creating Migrations

```bash
# Make changes to models in app/models/

# Generate migration
alembic revision --autogenerate -m "Add new field"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head
```

---

## Environment-Specific Configuration

### Development
- LLM: Ollama (local)
- Embeddings: sentence-transformers (local)
- Database: Docker PostgreSQL
- CORS: localhost:5173

### Staging
- LLM: OpenAI (with rate limits)
- Embeddings: OpenAI
- Database: Managed PostgreSQL
- CORS: staging.yourdomain.com

### Production
- LLM: OpenAI/Anthropic (production keys)
- Embeddings: OpenAI
- Database: Highly available PostgreSQL
- CORS: yourdomain.com
- SSL/TLS: Required
- Monitoring: Full observability

---

## Security Checklist

- [ ] Change default PostgreSQL password
- [ ] Store secrets in environment variables or secret manager
- [ ] Enable HTTPS/TLS for all connections
- [ ] Set up firewall rules (only necessary ports open)
- [ ] Enable rate limiting on API
- [ ] Validate and sanitize all inputs
- [ ] Set up regular database backups
- [ ] Enable logging and monitoring
- [ ] Review CORS settings
- [ ] Implement authentication (future)

---

## Performance Optimization

### Database

```sql
-- Create indexes for common queries
CREATE INDEX idx_lectures_module ON lectures(module_code);
CREATE INDEX idx_chunks_lecture ON chunks(lecture_id);

-- pgvector indexes (choose one based on data size)
-- HNSW: Better for large datasets
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);

-- IVFFlat: Faster build time
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Analyze tables for query optimization
ANALYZE lectures;
ANALYZE chunks;
ANALYZE topics;
```

### Backend

- Use connection pooling (already configured in SQLAlchemy)
- Enable Gunicorn workers for multi-process serving
- Cache frequent queries with Redis (future)
- Use async operations for I/O-bound tasks

```bash
# Production server with Gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Frontend

- Enable compression (gzip)
- Minify assets (Vite does this automatically)
- Use CDN for static assets
- Implement lazy loading for components
- Cache API responses with React Query

---

## Monitoring & Logging

### Backend Logging

Add structured logging:

```python
import logging
import json

logger = logging.getLogger(__name__)

# JSON formatter for centralized logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': record.created,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module
        })
```

### Monitoring Endpoints

```python
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest

app = FastAPI()

# Metrics
request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Health Checks

```python
@app.get("/health/ready")
async def readiness():
    """Check if service is ready to handle requests"""
    # Check database connection
    # Check LLM provider
    return {"status": "ready"}

@app.get("/health/live")
async def liveness():
    """Check if service is alive"""
    return {"status": "alive"}
```

---

## Backup Strategy

### Database Backups

```bash
# Daily automated backup
pg_dump \
  -h localhost \
  -U postgres \
  -d lecture_assistant \
  -F c \
  -f backup_$(date +%Y%m%d).dump

# Restore from backup
pg_restore \
  -h localhost \
  -U postgres \
  -d lecture_assistant \
  backup_20260201.dump
```

### File Backups

```bash
# Backup uploaded PDFs
rsync -av uploads/ /backup/uploads/
```

---

## Scaling Considerations

### Horizontal Scaling

1. **Backend**: Run multiple FastAPI instances behind load balancer
2. **Database**: Use read replicas for queries
3. **File Storage**: Move to S3/Cloud Storage
4. **Vector Search**: Consider dedicated vector DB (Pinecone) for very large scale

### Vertical Scaling

1. **Database**: Increase instance size for more RAM
2. **Backend**: Use larger instances for LLM operations
3. **Embeddings**: Use GPU instances for faster embedding generation

---

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check connection
psql -h localhost -U postgres -d lecture_assistant

# View logs
docker logs lecture_assistant_db
```

### pgvector Not Found

```sql
-- Install extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### LLM Connection Issues

```bash
# Test Ollama
curl http://localhost:11434/api/generate -d '{"model":"llama2","prompt":"test"}'

# Test OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## Maintenance

### Regular Tasks

- Weekly: Review logs for errors
- Monthly: Update dependencies
- Quarterly: Review and optimize database indexes
- Annually: Major version upgrades

### Dependency Updates

```bash
# Backend
pip list --outdated
pip install --upgrade <package>

# Frontend
npm outdated
npm update
```
