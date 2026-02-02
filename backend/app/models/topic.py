"""
Database models for topics and topic appearances
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database import Base


class Topic(Base):
    """Topic model - represents a cross-lecture topic"""
    __tablename__ = "topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    module_code = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    appearances = relationship("TopicAppearance", back_populates="topic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Topic {self.name} in {self.module_code}>"


class TopicAppearance(Base):
    """TopicAppearance model - tracks where topics appear in lectures"""
    __tablename__ = "topic_appearances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    lecture_id = Column(UUID(as_uuid=True), ForeignKey("lectures.id", ondelete="CASCADE"), nullable=False)
    frequency = Column(Integer, default=1)  # Number of times topic appears in this lecture
    first_slide = Column(Integer, nullable=True)  # First slide where topic appears
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    topic = relationship("Topic", back_populates="appearances")
    lecture = relationship("Lecture", back_populates="topic_appearances")

    def __repr__(self):
        return f"<TopicAppearance topic={self.topic_id} lecture={self.lecture_id} freq={self.frequency}>"
