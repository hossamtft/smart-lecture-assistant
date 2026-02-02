"""
RAG (Retrieval-Augmented Generation) Engine
Implements question answering with temporal awareness
"""
from typing import List, Dict, Optional
import time
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models import Lecture, Chunk
from .embeddings import embedding_service
from .llm_provider import llm_provider
from ..config import settings


class RAGEngine:
    """Service for RAG-based question answering"""

    def __init__(self):
        self.top_k = settings.retrieval_top_k

    def query(
        self,
        query: str,
        module_code: str,
        db: Session,
        top_k: int = None,
        temporal_filter: bool = True,
        current_week: Optional[int] = None
    ) -> Dict:
        """
        Answer a question using RAG

        Args:
            query: User's question
            module_code: Module code to search in
            db: Database session
            top_k: Number of chunks to retrieve
            temporal_filter: Only retrieve from past lectures
            current_week: Current week for temporal filtering

        Returns:
            Dictionary with answer and sources
        """
        start_time = time.time()

        top_k = top_k or self.top_k

        print(f"RAG Query: {query}")
        print(f"Module: {module_code}, Top-K: {top_k}, Temporal Filter: {temporal_filter}")

        # Generate query embedding
        query_embedding = embedding_service.embed_text(query)

        # Retrieve relevant chunks
        retrieved_chunks = self._retrieve_chunks(
            query_embedding=query_embedding,
            module_code=module_code,
            db=db,
            top_k=top_k,
            temporal_filter=temporal_filter,
            current_week=current_week
        )

        if not retrieved_chunks:
            return {
                "answer": "I couldn't find any relevant information in the uploaded lectures for this module.",
                "sources": [],
                "processing_time": time.time() - start_time
            }

        print(f"Retrieved {len(retrieved_chunks)} chunks")

        # Generate answer
        answer = self._generate_answer(query, retrieved_chunks)

        # Format sources
        sources = self._format_sources(retrieved_chunks)

        processing_time = time.time() - start_time
        print(f"RAG query completed in {processing_time:.2f}s")

        return {
            "answer": answer,
            "sources": sources,
            "processing_time": processing_time
        }

    def _retrieve_chunks(
        self,
        query_embedding: List[float],
        module_code: str,
        db: Session,
        top_k: int,
        temporal_filter: bool,
        current_week: Optional[int]
    ) -> List[Dict]:
        """
        Retrieve relevant chunks using vector similarity

        Uses pgvector's cosine distance operator (<=>)
        """
        # Build base query
        query = db.query(
            Chunk.id,
            Chunk.content,
            Chunk.slide_number,
            Lecture.title.label("lecture_title"),
            Lecture.week_number,
            Lecture.id.label("lecture_id"),
            # Cosine similarity (1 - cosine distance)
            (1 - Chunk.embedding.cosine_distance(query_embedding)).label("similarity")
        ).join(
            Lecture, Chunk.lecture_id == Lecture.id
        ).filter(
            Lecture.module_code == module_code.upper()
        ).filter(
            Chunk.embedding.isnot(None)
        )

        # Apply temporal filter
        if temporal_filter and current_week:
            query = query.filter(Lecture.week_number <= current_week)

        # Order by similarity and limit
        results = query.order_by(
            (1 - Chunk.embedding.cosine_distance(query_embedding)).desc()
        ).limit(top_k).all()

        # Convert to list of dicts
        chunks = []
        for row in results:
            chunks.append({
                "chunk_id": str(row.id),
                "content": row.content,
                "slide_number": row.slide_number,
                "lecture_title": row.lecture_title,
                "week_number": row.week_number,
                "lecture_id": str(row.lecture_id),
                "similarity": float(row.similarity)
            })

        return chunks

    def _generate_answer(self, query: str, chunks: List[Dict]) -> str:
        """Generate answer using LLM with retrieved context"""
        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i} - {chunk['lecture_title']}, Week {chunk['week_number']}, Slide {chunk['slide_number']}]\n"
                f"{chunk['content']}"
            )

        context = "\n\n".join(context_parts)

        # Build prompt
        prompt = f"""Answer the following question based on the provided lecture content. Use information from the sources to provide a comprehensive answer. When referencing information, mention which source (e.g., "According to Source 1...").

Question: {query}

Lecture Content:
{context}

Instructions:
- Provide a clear, well-structured answer
- Cite sources when making specific claims
- If information from multiple lectures is relevant, explain how concepts connect
- If the sources don't contain enough information to fully answer the question, acknowledge this
- Maintain academic tone appropriate for university-level content

Answer:"""

        system_prompt = """You are an intelligent teaching assistant helping university students understand lecture content. Your role is to:
1. Synthesize information from multiple lecture sources
2. Explain concepts clearly and accurately
3. Show how ideas connect across lectures
4. Acknowledge when information is incomplete
5. Maintain academic rigor while being accessible"""

        try:
            answer = llm_provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500
            )
            return answer.strip()

        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            return "I encountered an error while generating the answer. Please try again."

    def _format_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Format retrieved chunks as source citations"""
        sources = []

        for chunk in chunks:
            sources.append({
                "lecture_title": chunk["lecture_title"],
                "week_number": chunk["week_number"],
                "slide_number": chunk["slide_number"],
                "content": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                "similarity_score": round(chunk["similarity"], 3)
            })

        return sources

    def generate_topic_summary(
        self,
        topic_id: str,
        module_code: str,
        db: Session
    ) -> Dict:
        """
        Generate a comprehensive summary for a specific topic

        Args:
            topic_id: Topic ID
            module_code: Module code
            db: Database session

        Returns:
            Dictionary with summary and key points
        """
        from ..models import Topic, TopicAppearance

        # Get topic with appearances
        topic = db.query(Topic).filter(
            and_(
                Topic.id == topic_id,
                Topic.module_code == module_code.upper()
            )
        ).first()

        if not topic:
            raise ValueError("Topic not found")

        # Get all chunks related to this topic's appearances
        appearances = db.query(TopicAppearance).filter(
            TopicAppearance.topic_id == topic_id
        ).all()

        lecture_ids = [str(app.lecture_id) for app in appearances]

        # Get chunks from these lectures
        chunks = db.query(
            Chunk.content,
            Chunk.slide_number,
            Lecture.title.label("lecture_title"),
            Lecture.week_number
        ).join(
            Lecture, Chunk.lecture_id == Lecture.id
        ).filter(
            Lecture.id.in_(lecture_ids)
        ).order_by(
            Lecture.week_number,
            Chunk.slide_number
        ).limit(20).all()  # Limit to avoid overwhelming the LLM

        # Build context
        context_parts = []
        for chunk in chunks:
            context_parts.append(
                f"[Week {chunk.week_number} - {chunk.lecture_title}, Slide {chunk.slide_number}]\n"
                f"{chunk.content}"
            )

        context = "\n\n".join(context_parts)

        # Generate summary
        prompt = f"""Provide a comprehensive summary of the topic "{topic.name}" based on how it is presented across multiple lectures.

Topic Description: {topic.description}

Lecture Content:
{context}

Please provide:
1. A synthesis of how this topic is introduced and developed across the lectures
2. Key concepts and definitions
3. How the topic evolves or is applied in later lectures
4. 3-5 bullet points of the most important takeaways

Format your response as:
SUMMARY: <comprehensive summary>
KEY POINTS:
- <point 1>
- <point 2>
- <point 3>
..."""

        try:
            response = llm_provider.generate(
                prompt=prompt,
                system_prompt="You are an expert at synthesizing educational content across multiple sources.",
                temperature=0.7,
                max_tokens=800
            )

            # Parse response
            summary, key_points = self._parse_summary_response(response)

            return {
                "topic_name": topic.name,
                "summary": summary,
                "key_points": key_points,
                "sources": [
                    {
                        "lecture_title": app.lecture.title,
                        "week_number": app.lecture.week_number,
                        "frequency": app.frequency
                    }
                    for app in appearances
                ]
            }

        except Exception as e:
            print(f"Error generating topic summary: {str(e)}")
            return {
                "topic_name": topic.name,
                "summary": topic.description or "Summary unavailable",
                "key_points": [],
                "sources": []
            }

    def _parse_summary_response(self, response: str) -> tuple:
        """Parse summary response from LLM"""
        lines = response.strip().split("\n")
        summary = ""
        key_points = []
        in_key_points = False

        for line in lines:
            line = line.strip()
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("KEY POINTS:"):
                in_key_points = True
            elif in_key_points and line.startswith("-"):
                key_points.append(line[1:].strip())
            elif in_key_points and not line.startswith("-") and line:
                # Multi-line summary
                if not summary:
                    summary += " " + line
                else:
                    summary += " " + line

        # If parsing failed, use entire response as summary
        if not summary:
            summary = response.strip()

        return summary, key_points


# Singleton instance
rag_engine = RAGEngine()
