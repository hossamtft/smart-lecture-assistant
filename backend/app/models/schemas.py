"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


# Lecture Schemas
class LectureBase(BaseModel):
    module_code: str = Field(..., max_length=20, description="Module code (e.g., COMP3001)")
    week_number: int = Field(..., ge=1, le=24, description="Week number (1-24)")
    title: str = Field(..., max_length=255, description="Lecture title")


class LectureCreate(LectureBase):
    filename: str
    num_pages: Optional[int] = None


class LectureResponse(LectureBase):
    id: UUID
    filename: str
    upload_date: datetime
    num_pages: Optional[int] = None

    class Config:
        from_attributes = True


class LectureDetail(LectureResponse):
    chunks_count: int = 0


# Chunk Schemas
class ChunkBase(BaseModel):
    content: str
    slide_number: int = Field(..., ge=1)


class ChunkCreate(ChunkBase):
    lecture_id: UUID


class ChunkResponse(ChunkBase):
    id: UUID
    lecture_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Topic Schemas
class TopicBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    module_code: str = Field(..., max_length=20)


class TopicCreate(TopicBase):
    pass


class TopicAppearanceResponse(BaseModel):
    lecture_id: UUID
    week_number: int
    lecture_title: str
    frequency: int
    first_slide: Optional[int] = None

    class Config:
        from_attributes = True


class TopicResponse(TopicBase):
    id: UUID
    created_at: datetime
    appearances: List[TopicAppearanceResponse] = []

    class Config:
        from_attributes = True


# Query Schemas
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User question")
    module_code: str = Field(..., max_length=20)
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    temporal_filter: bool = Field(default=True, description="Filter to only past lectures")
    current_week: Optional[int] = Field(default=None, ge=1, le=24)


class SourceResponse(BaseModel):
    lecture_title: str
    week_number: int
    slide_number: int
    content: str
    similarity_score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceResponse]
    processing_time: float


# Topic Detection Schemas
class TopicDetectionRequest(BaseModel):
    module_code: str = Field(..., max_length=20)
    min_cluster_size: Optional[int] = Field(default=3, ge=2)
    clustering_method: Optional[str] = Field(default="hdbscan", pattern="^(hdbscan|kmeans)$")


class TopicDetectionResponse(BaseModel):
    status: str
    module_code: str
    topics_detected: int
    processing_time: float
    topics: List[TopicResponse]


# Topic Map Schemas
class TopicNode(BaseModel):
    id: str
    label: str
    size: int
    color: Optional[str] = None


class TopicEdge(BaseModel):
    source: str
    target: str
    type: str = Field(..., pattern="^(prerequisite|related)$")


class TopicMapResponse(BaseModel):
    nodes: List[TopicNode]
    edges: List[TopicEdge]


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_lectures: int
    total_topics: int
    modules: List[str]
    recent_uploads: List[LectureResponse]


class ModuleDashboard(BaseModel):
    module_code: str
    total_lectures: int
    total_topics: int
    weeks_covered: List[int]
    lectures: List[LectureResponse]


# Upload Response
class UploadResponse(BaseModel):
    status: str
    message: str
    lecture: LectureResponse
    chunks_created: int


# Health Check
class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    embedding_provider: str
    database_connected: bool = True
