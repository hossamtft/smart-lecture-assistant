"""
API routes for dashboard data
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from ...database import get_db
from ...models import Lecture, Topic, TopicAppearance
from ...models.schemas import DashboardStats, ModuleDashboard, LectureResponse

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get overall dashboard statistics
    """
    # Total lectures
    total_lectures = db.query(Lecture).count()

    # Total topics
    total_topics = db.query(Topic).count()

    # Unique modules
    modules = db.query(distinct(Lecture.module_code)).all()
    modules_list = [module[0] for module in modules]

    # Recent uploads (last 5)
    recent_lectures = db.query(Lecture).order_by(
        Lecture.upload_date.desc()
    ).limit(5).all()

    recent_uploads = [
        LectureResponse.from_orm(lecture)
        for lecture in recent_lectures
    ]

    return DashboardStats(
        total_lectures=total_lectures,
        total_topics=total_topics,
        modules=modules_list,
        recent_uploads=recent_uploads
    )


@router.get("/{module_code}", response_model=ModuleDashboard)
async def get_module_dashboard(
    module_code: str,
    db: Session = Depends(get_db)
):
    """
    Get dashboard data for a specific module
    """
    module_code = module_code.upper()

    # Get lectures
    lectures = db.query(Lecture).filter(
        Lecture.module_code == module_code
    ).order_by(Lecture.week_number).all()

    if not lectures:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No lectures found for module {module_code}"
        )

    # Total topics
    total_topics = db.query(Topic).filter(
        Topic.module_code == module_code
    ).count()

    # Weeks covered
    weeks_covered = sorted(set(lecture.week_number for lecture in lectures))

    # Convert lectures to response format
    lecture_responses = [
        LectureResponse.from_orm(lecture)
        for lecture in lectures
    ]

    return ModuleDashboard(
        module_code=module_code,
        total_lectures=len(lectures),
        total_topics=total_topics,
        weeks_covered=weeks_covered,
        lectures=lecture_responses
    )
