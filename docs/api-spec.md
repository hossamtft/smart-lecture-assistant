# API Specification

Base URL: `http://localhost:8000`

## Authentication

Currently, the API does not require authentication. Future versions will implement JWT-based authentication.

## Endpoints

### Health & Status

#### GET /health
Check API health status

**Response:**
```json
{
  "status": "healthy",
  "llm_provider": "ollama",
  "embedding_provider": "local"
}
```

---

### Lecture Management

#### POST /api/lectures/upload
Upload a new lecture PDF with metadata

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: PDF file (max 50MB)
  - `module_code`: string (e.g., "COMP3001")
  - `week_number`: integer (1-24)
  - `lecture_title`: string

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "module_code": "COMP3001",
  "week_number": 1,
  "title": "Introduction to Algorithms",
  "filename": "lecture_01.pdf",
  "upload_date": "2026-02-01T10:00:00Z",
  "num_pages": 45
}
```

#### GET /api/lectures
List all lectures

**Query Parameters:**
- `module_code` (optional): Filter by module code

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "module_code": "COMP3001",
    "week_number": 1,
    "title": "Introduction to Algorithms",
    "filename": "lecture_01.pdf",
    "upload_date": "2026-02-01T10:00:00Z",
    "num_pages": 45
  }
]
```

#### GET /api/lectures/{lecture_id}
Get a specific lecture

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "module_code": "COMP3001",
  "week_number": 1,
  "title": "Introduction to Algorithms",
  "filename": "lecture_01.pdf",
  "upload_date": "2026-02-01T10:00:00Z",
  "num_pages": 45,
  "chunks_count": 120
}
```

#### DELETE /api/lectures/{lecture_id}
Delete a lecture and its associated chunks

**Response:**
```json
{
  "status": "success",
  "message": "Lecture deleted successfully"
}
```

---

### Topic Detection

#### POST /api/topics/detect
Run topic detection on a module

**Request:**
```json
{
  "module_code": "COMP3001",
  "min_cluster_size": 3,
  "clustering_method": "hdbscan"
}
```

**Response:**
```json
{
  "status": "success",
  "module_code": "COMP3001",
  "topics_detected": 15,
  "processing_time": 12.5,
  "topics": [
    {
      "id": "topic-001",
      "name": "Recursion and Base Cases",
      "description": "Fundamental concepts of recursive algorithms",
      "appearances": [
        {
          "lecture_id": "...",
          "week_number": 2,
          "lecture_title": "Recursion Basics",
          "frequency": 5
        },
        {
          "lecture_id": "...",
          "week_number": 8,
          "lecture_title": "Tree Traversal",
          "frequency": 3
        }
      ]
    }
  ]
}
```

#### GET /api/topics/{module_code}
Get all detected topics for a module

**Response:**
```json
[
  {
    "id": "topic-001",
    "name": "Recursion and Base Cases",
    "description": "Fundamental concepts of recursive algorithms",
    "module_code": "COMP3001",
    "appearances": [...]
  }
]
```

#### GET /api/topics/{module_code}/map
Get topic map data for visualization

**Response:**
```json
{
  "nodes": [
    {
      "id": "topic-001",
      "label": "Recursion",
      "size": 8,
      "color": "#646cff"
    }
  ],
  "edges": [
    {
      "source": "topic-001",
      "target": "topic-005",
      "type": "prerequisite"
    }
  ]
}
```

---

### Query & RAG

#### POST /api/query
Ask a question using RAG

**Request:**
```json
{
  "query": "How does recursion relate to tree traversal?",
  "module_code": "COMP3001",
  "top_k": 5,
  "temporal_filter": true,
  "current_week": 8
}
```

**Response:**
```json
{
  "answer": "Recursion is fundamental to tree traversal algorithms. In Week 2, recursion was introduced with the concept of base cases...",
  "sources": [
    {
      "lecture_title": "Recursion Basics",
      "week_number": 2,
      "slide_number": 12,
      "content": "A recursive function must have a base case...",
      "similarity_score": 0.89
    },
    {
      "lecture_title": "Tree Traversal",
      "week_number": 8,
      "slide_number": 5,
      "content": "Pre-order traversal uses recursion to visit nodes...",
      "similarity_score": 0.85
    }
  ],
  "processing_time": 2.3
}
```

#### POST /api/query/summary
Generate a topic summary

**Request:**
```json
{
  "topic_id": "topic-001",
  "module_code": "COMP3001"
}
```

**Response:**
```json
{
  "topic_name": "Recursion and Base Cases",
  "summary": "Recursion is introduced in Week 2 as a programming technique...",
  "key_points": [
    "Base case prevents infinite loops",
    "Recursive case breaks down the problem",
    "Applied in tree and graph algorithms"
  ],
  "sources": [...]
}
```

---

### Dashboard

#### GET /api/dashboard/stats
Get overall dashboard statistics

**Response:**
```json
{
  "total_lectures": 48,
  "total_topics": 67,
  "modules": ["COMP3001", "COMP3002", "COMP3003"],
  "recent_uploads": [
    {
      "id": "...",
      "module_code": "COMP3001",
      "title": "Advanced Sorting",
      "upload_date": "2026-02-01T15:30:00Z"
    }
  ]
}
```

#### GET /api/dashboard/{module_code}
Get dashboard data for a specific module

**Response:**
```json
{
  "module_code": "COMP3001",
  "total_lectures": 12,
  "total_topics": 15,
  "weeks_covered": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
  "topic_timeline": [
    {
      "week": 1,
      "topics": ["Introduction", "Complexity Analysis"]
    },
    {
      "week": 2,
      "topics": ["Recursion", "Divide and Conquer"]
    }
  ],
  "lectures": [...]
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File exceeds size limit
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server-side error

### Example Error Response

```json
{
  "detail": "File size exceeds maximum allowed (50MB)"
}
```

---

## Rate Limiting

Currently not implemented. Future versions will include rate limiting to prevent abuse.

---

## WebSocket Endpoints (Future)

### WS /api/ws/upload/{upload_id}
Real-time upload progress

**Messages:**
```json
{
  "type": "progress",
  "percentage": 45,
  "stage": "extracting_text"
}
```

---

## Pagination

For endpoints returning lists, pagination will be added:

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8
}
```

---

## API Versioning

Current version: `v1` (implicit)

Future versions will use URL versioning: `/api/v2/...`
