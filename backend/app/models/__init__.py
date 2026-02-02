"""
Database models
"""
from .lecture import Lecture, Chunk
from .topic import Topic, TopicAppearance

__all__ = ["Lecture", "Chunk", "Topic", "TopicAppearance"]
