"""
API routes for topic detection and management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import time

from ...database import get_db
from ...models import Topic, TopicAppearance, Lecture
from ...models.schemas import (
    TopicDetectionRequest,
    TopicDetectionResponse,
    TopicResponse,
    TopicAppearanceResponse,
    TopicMapResponse,
    TopicNode,
    TopicEdge
)
from ...services.topic_detector import topic_detector

router = APIRouter()


@router.post("/detect", response_model=TopicDetectionResponse)
async def detect_topics(
    request: TopicDetectionRequest,
    db: Session = Depends(get_db)
):
    """
    Run topic detection on a module

    This analyzes all lectures in a module to identify cross-lecture topics using clustering.
    The process:
    1. Retrieves all chunk embeddings from the module
    2. Clusters them using HDBSCAN or K-Means
    3. Generates topic labels using LLM
    4. Tracks topic appearances across weeks
    """
    start_time = time.time()

    # Check if module has lectures
    lecture_count = db.query(Lecture).filter(
        Lecture.module_code == request.module_code.upper()
    ).count()

    if lecture_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No lectures found for module {request.module_code}"
        )

    try:
        # Delete existing topics for this module
        db.query(Topic).filter(
            Topic.module_code == request.module_code.upper()
        ).delete()
        db.commit()

        # Run topic detection
        topics = topic_detector.detect_topics(
            module_code=request.module_code,
            db=db
        )

        processing_time = time.time() - start_time

        # Format response
        topic_responses = []
        for topic_data in topics:
            appearances = [
                TopicAppearanceResponse(
                    lecture_id=app["lecture_id"],
                    week_number=app["week_number"],
                    lecture_title=app["lecture_title"],
                    frequency=app["frequency"],
                    first_slide=app.get("first_slide")
                )
                for app in topic_data["appearances"]
            ]

            topic_responses.append(
                TopicResponse(
                    id=topic_data["id"],
                    name=topic_data["name"],
                    description=topic_data["description"],
                    module_code=request.module_code.upper(),
                    created_at=None,  # Will be set from DB
                    appearances=appearances
                )
            )

        return TopicDetectionResponse(
            status="success",
            module_code=request.module_code.upper(),
            topics_detected=len(topics),
            processing_time=processing_time,
            topics=topic_responses
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Topic detection failed: {str(e)}"
        )


@router.get("/{module_code}", response_model=List[TopicResponse])
async def get_topics(
    module_code: str,
    db: Session = Depends(get_db)
):
    """
    Get all detected topics for a module
    """
    topics = db.query(Topic).filter(
        Topic.module_code == module_code.upper()
    ).all()

    if not topics:
        return []

    # Build response with appearances
    topic_responses = []
    for topic in topics:
        # Get appearances with lecture info
        appearances_query = db.query(
            TopicAppearance,
            Lecture.week_number,
            Lecture.title
        ).join(
            Lecture, TopicAppearance.lecture_id == Lecture.id
        ).filter(
            TopicAppearance.topic_id == topic.id
        ).order_by(
            Lecture.week_number
        ).all()

        appearances = [
            TopicAppearanceResponse(
                lecture_id=str(app[0].lecture_id),
                week_number=app[1],
                lecture_title=app[2],
                frequency=app[0].frequency,
                first_slide=app[0].first_slide
            )
            for app in appearances_query
        ]

        topic_responses.append(
            TopicResponse(
                id=str(topic.id),
                name=topic.name,
                description=topic.description,
                module_code=topic.module_code,
                created_at=topic.created_at,
                appearances=appearances
            )
        )

    return topic_responses


@router.get("/{module_code}/map", response_model=TopicMapResponse)
async def get_topic_map(
    module_code: str,
    db: Session = Depends(get_db)
):
    """
    Get topic map data for visualization

    Returns nodes (topics) and edges (relationships) suitable for graph visualization
    """
    topics = db.query(Topic).filter(
        Topic.module_code == module_code.upper()
    ).all()

    if not topics:
        return TopicMapResponse(nodes=[], edges=[])

    # Build nodes
    nodes = []
    topics_list = []

    for topic in topics:
        # Count total appearances
        appearance_count = db.query(TopicAppearance).filter(
            TopicAppearance.topic_id == topic.id
        ).count()

        # Get all appearances for prerequisite inference
        appearances_query = db.query(
            TopicAppearance,
            Lecture.week_number,
            Lecture.title
        ).join(
            Lecture, TopicAppearance.lecture_id == Lecture.id
        ).filter(
            TopicAppearance.topic_id == topic.id
        ).all()

        appearances = [
            {
                "lecture_id": str(app[0].lecture_id),
                "week_number": app[1],
                "lecture_title": app[2],
                "frequency": app[0].frequency
            }
            for app in appearances_query
        ]

        topics_list.append({
            "id": str(topic.id),
            "name": topic.name,
            "appearances": appearances
        })

        nodes.append(
            TopicNode(
                id=str(topic.id),
                label=topic.name,
                size=appearance_count * 2,  # Scale node size by appearances
                color="#646cff"
            )
        )

    # Infer prerequisite relationships
    edges_data = topic_detector.infer_prerequisites(topics_list)

    edges = [
        TopicEdge(
            source=edge["source"],
            target=edge["target"],
            type=edge["type"]
        )
        for edge in edges_data
    ]

    return TopicMapResponse(nodes=nodes, edges=edges)


@router.delete("/{topic_id}")
async def delete_topic(
    topic_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a topic
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    db.delete(topic)
    db.commit()

    return {
        "status": "success",
        "message": f"Topic {topic_id} deleted successfully"
    }
