# Smart Lecture Assistant

An AI-powered web application that helps university students synthesize and understand lecture materials across entire course modules through cross-lecture topic detection, relationship mapping, and RAG-based summarization.

## Features

- **PDF Ingestion**: Upload lecture slides with metadata (week, module code, title)
- **Cross-Lecture Topic Detection**: Automatically identify topics that span multiple lectures
- **Topic Evolution Tracking**: See how concepts are introduced and developed over time
- **RAG-Based Q&A**: Ask questions grounded in your lecture content with source citations
- **Interactive Visualizations**: Topic maps and timeline views
- **Course Awareness**: Temporal understanding prevents future content from explaining past concepts

## Project Structure

```
smart-lecture-assistant/
├── backend/           # FastAPI backend (Python)
├── frontend/          # React + TypeScript frontend
├── docker/            # Docker configuration for PostgreSQL
└── docs/              # Project documentation
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop
- (Optional) Ollama for local LLM testing

### 1. Clone the Repository

```bash
git clone <repository-url>
cd smart-lecture-assistant
```

### 2. Start the Database

```bash
cd docker
docker-compose up -d
```

Verify PostgreSQL with pgvector is running:
- Database: http://localhost:5432
- pgAdmin: http://localhost:5050 (admin@admin.com / admin)

### 3. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the server
uvicorn app.main:app --reload
```

Backend will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 4. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL + pgvector**: Vector database for embeddings
- **SQLAlchemy**: ORM for database operations
- **Sentence Transformers**: Local embeddings
- **Ollama/OpenAI/Anthropic**: LLM providers
- **HDBSCAN**: Clustering for topic detection

### Frontend
- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool
- **React Query**: Server state management
- **React Flow**: Topic map visualization
- **Recharts**: Analytics charts

## Development Workflow

### Backend Development

```bash
cd backend

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black app/
isort app/

# Type checking
mypy app/
```

### Frontend Development

```bash
cd frontend

# Lint code
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation powered by FastAPI's automatic OpenAPI generation.

## Project Timeline

This is a BSc Computer Science Final Year Project at the University of Southampton.

- **Author**: Hossameldin Tammam
- **Supervisor**: Dr Mike Wald
- **Duration**: February 2026 - May 2026

## Key Deliverables

1. Functional prototype processing 12-week modules
2. Cross-lecture topic detection with clustering
3. RAG pipeline with temporal awareness
4. Interactive web dashboard
5. Evaluation using LLM-as-a-Judge and user studies

## Documentation

- [Architecture Documentation](docs/architecture.md)
- [API Specification](docs/api-spec.md)
- [Deployment Guide](docs/deployment.md)
- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

## License

This project is developed as part of academic research at the University of Southampton.

## Contact

For questions or feedback, please contact:
- **Email**: hossamtammam5@gmail.com
- **GitHub**: [@hossamtft](https://github.com/hossamtft)

## Acknowledgments

- Dr Mike Wald (Project Supervisor)
- University of Southampton Computer Science Department
- Research based on cognitive load theory and educational scaffolding principles
