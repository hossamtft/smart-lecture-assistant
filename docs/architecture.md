# Architecture Documentation

## System Overview

The Smart Lecture Assistant is built as a three-tier application with clear separation between the presentation layer (React frontend), application layer (FastAPI backend), and data layer (PostgreSQL + pgvector).

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  - Upload Interface  - Topic Maps  - Q&A Chat  - Dashboard  │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API (HTTP/JSON)
┌─────────────────────▼───────────────────────────────────────┐
│                  Backend (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ PDF Processor│  │Topic Detector│  │  RAG Engine  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌────────────────────────────────────────────────────┐    │
│  │           LLM Provider Abstraction                  │    │
│  │  (Ollama / OpenAI / Anthropic)                     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │ SQL + Vector Queries
┌─────────────────────▼───────────────────────────────────────┐
│           PostgreSQL 16 + pgvector Extension                │
│  - Lectures  - Chunks  - Topics  - Vector Embeddings       │
└─────────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Core Components

#### 1. PDF Processor Service
- **Purpose**: Extract and structure content from PDF lecture slides
- **Key Functions**:
  - Text extraction (PyPDF2, pdfplumber)
  - OCR fallback for scanned PDFs (pytesseract)
  - Slide boundary preservation
  - Metadata attachment (week, module, slide number)

#### 2. Embedding Service
- **Purpose**: Generate vector embeddings for text chunks
- **Providers**:
  - Local: sentence-transformers (all-MiniLM-L6-v2)
  - Cloud: OpenAI text-embedding-3
- **Features**:
  - Batch processing for efficiency
  - Caching to avoid recomputation
  - Dimension consistency validation

#### 3. Topic Detection Service
- **Purpose**: Identify cross-lecture topics using clustering
- **Algorithm**:
  1. Embed all chunks using sentence-transformers
  2. Cluster embeddings (HDBSCAN or K-Means)
  3. Generate topic labels using LLM
  4. Track topic appearances by week
  5. Infer prerequisite relationships from temporal ordering
- **Output**: Topic graph with nodes (topics) and edges (relationships)

#### 4. RAG Engine
- **Purpose**: Answer queries using retrieval-augmented generation
- **Pipeline**:
  1. Embed user query
  2. Vector similarity search in pgvector
  3. Temporal filtering (only past lectures)
  4. Assemble context with metadata
  5. Generate answer with LLM
  6. Return response with source citations

#### 5. LLM Provider Abstraction
- **Purpose**: Unified interface for multiple LLM providers
- **Base Class**: `LLMProvider`
  - Methods: `generate()`, `embed()`, `check_health()`
- **Implementations**:
  - `OllamaProvider`: Local development
  - `OpenAIProvider`: Production (GPT-4)
  - `AnthropicProvider`: Production (Claude)
- **Configuration**: Environment-based selection

### Data Models

#### Lecture
```python
{
  "id": UUID,
  "module_code": str,
  "week_number": int,
  "title": str,
  "filename": str,
  "upload_date": datetime,
  "num_pages": int
}
```

#### Chunk
```python
{
  "id": UUID,
  "lecture_id": UUID,  # Foreign key
  "content": str,
  "slide_number": int,
  "embedding": vector(384),  # pgvector type
  "created_at": datetime
}
```

#### Topic
```python
{
  "id": UUID,
  "name": str,
  "description": str,
  "module_code": str,
  "created_at": datetime
}
```

#### TopicAppearance
```python
{
  "id": UUID,
  "topic_id": UUID,  # Foreign key
  "lecture_id": UUID,  # Foreign key
  "frequency": int,  # Number of mentions
  "first_slide": int
}
```

## Frontend Architecture

### Component Hierarchy

```
App
├── Navbar
└── Router
    ├── Dashboard
    │   ├── StatsCards
    │   ├── RecentUploads
    │   └── ModuleSelector
    ├── Upload
    │   └── FileDropzone
    ├── Topics
    │   ├── TopicMap (React Flow)
    │   └── Timeline (Recharts)
    └── Query
        ├── ChatInterface
        └── SummaryViewer
```

### State Management

- **Server State**: React Query (TanStack Query)
  - Automatic caching and refetching
  - Optimistic updates
  - Background synchronization
- **Local State**: React hooks (useState, useReducer)
- **URL State**: React Router for navigation

### API Client

Centralized Axios instance with:
- Base URL configuration
- Request/response interceptors
- Error handling
- TypeScript type safety

## Database Schema

### pgvector Integration

pgvector extends PostgreSQL with vector similarity search:

```sql
CREATE EXTENSION vector;

CREATE TABLE chunks (
  id UUID PRIMARY KEY,
  lecture_id UUID REFERENCES lectures(id),
  content TEXT,
  slide_number INTEGER,
  embedding vector(384),  -- 384 dimensions for MiniLM
  created_at TIMESTAMP
);

-- Create HNSW index for fast similarity search
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);
```

### Query Example

```sql
-- Find top 5 most similar chunks to query embedding
SELECT
  c.content,
  c.slide_number,
  l.title,
  l.week_number,
  1 - (c.embedding <=> $1::vector) as similarity
FROM chunks c
JOIN lectures l ON c.lecture_id = l.id
WHERE l.module_code = $2
  AND l.week_number <= $3  -- Temporal filter
ORDER BY c.embedding <=> $1::vector
LIMIT 5;
```

## LLM Integration

### Ollama (Development)

```python
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama2",
        "prompt": prompt,
        "stream": False
    }
)
```

### OpenAI (Production)

```python
from openai import OpenAI
client = OpenAI(api_key=settings.openai_api_key)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant..."},
        {"role": "user", "content": query}
    ]
)
```

## Security Considerations

1. **Input Validation**: Pydantic schemas validate all API inputs
2. **File Upload**: Size limits (50MB), extension whitelist (.pdf)
3. **SQL Injection**: SQLAlchemy ORM prevents injection attacks
4. **API Keys**: Stored in environment variables, never committed
5. **CORS**: Restricted to specific origins

## Performance Optimizations

1. **Vector Search**: HNSW index for sub-linear search time
2. **Batch Processing**: Embed multiple chunks in parallel
3. **Connection Pooling**: SQLAlchemy manages DB connections
4. **Caching**: React Query caches API responses
5. **Lazy Loading**: Components load on demand

## Scalability Considerations

- **Horizontal Scaling**: Stateless backend can run multiple instances
- **Database**: PostgreSQL supports read replicas
- **File Storage**: Move to S3 for production (currently local)
- **Vector DB**: pgvector scales to millions of vectors
- **Async Operations**: FastAPI supports async/await

## Deployment Architecture (Future)

```
Load Balancer (Nginx)
    │
    ├─► Frontend (Static files on CDN)
    │
    └─► Backend (Multiple FastAPI instances)
            │
            ├─► PostgreSQL (Primary + Read Replicas)
            │
            └─► LLM API (OpenAI/Anthropic)
```

## Monitoring & Logging

- **Backend**: FastAPI logs requests/responses
- **Database**: PostgreSQL query logs
- **LLM Calls**: Log prompts, responses, latency
- **Errors**: Centralized error tracking (future: Sentry)

## Testing Strategy

1. **Unit Tests**: Individual service functions
2. **Integration Tests**: API endpoints with test database
3. **E2E Tests**: Full user workflows (future)
4. **LLM Evaluation**: G-Eval methodology for RAG quality
