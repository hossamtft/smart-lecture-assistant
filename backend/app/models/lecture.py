"""
Database models for lectures and chunks
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid

from ..database import Base


class Lecture(Base):
    """Lecture model - represents a single lecture PDF"""
    __tablename__ = "lectures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_code = Column(String(20), nullable=False, index=True)
    week_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    num_pages = Column(Integer, nullable=True)

    # Relationships
    chunks = relationship("Chunk", back_populates="lecture", cascade="all, delete-orphan")
    topic_appearances = relationship("TopicAppearance", back_populates="lecture", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lecture {self.module_code} Week {self.week_number}: {self.title}>"


class Chunk(Base):
    """Chunk model - represents a text chunk from a lecture with embedding"""
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(UUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    slide_number = Column(Integer, nullable=False)

    # Vector embedding (384 dimensions for all-MiniLM-L6-v2)
    # This will be configurable based on the embedding model used
    embedding = Column(Vector(384), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lecture = relationship("Lecture", back_populates="chunks")

    def __repr__(self):
        return f"<Chunk {self.id} from Lecture {self.lecture_id}, Slide {self.slide_number}>"
