"""
API routes for RAG-based querying
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.schemas import QueryRequest, QueryResponse
from ...services.rag_engine import rag_engine

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def query_lectures(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question about lecture content using RAG

    The system will:
    1. Convert your question to an embedding
    2. Search for relevant lecture content using vector similarity
    3. Optionally filter to only past lectures (temporal awareness)
    4. Generate an answer using LLM with retrieved context
    5. Return answer with source citations

    **Temporal Filter**: When enabled and current_week is provided,
    only retrieves information from lectures up to that week.
    This prevents future content from explaining past concepts.
    """
    try:
        result = rag_engine.query(
            query=request.query,
            module_code=request.module_code,
            db=db,
            top_k=request.top_k,
            temporal_filter=request.temporal_filter,
            current_week=request.current_week
        )

        return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )


@router.post("/summary")
async def generate_topic_summary(
    topic_id: str,
    module_code: str,
    db: Session = Depends(get_db)
):
    """
    Generate a comprehensive summary for a specific topic

    This analyzes all appearances of a topic across lectures and generates:
    - A synthesis of how the topic is introduced and developed
    - Key concepts and definitions
    - Important takeaways
    """
    try:
        summary = rag_engine.generate_topic_summary(
            topic_id=topic_id,
            module_code=module_code,
            db=db
        )

        return summary

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )
