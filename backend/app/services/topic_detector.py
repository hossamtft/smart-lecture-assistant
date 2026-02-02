"""
Topic Detection Service
Uses clustering to identify cross-lecture topics
"""
from typing import List, Dict, Tuple
import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict, Counter
from sqlalchemy.orm import Session
from sqlalchemy import func

try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False

from ..models import Lecture, Chunk, Topic, TopicAppearance
from .llm_provider import llm_provider
from ..config import settings


class TopicDetector:
    """Service for detecting topics across lectures"""

    def __init__(self, clustering_method: str = None, min_cluster_size: int = None):
        self.clustering_method = clustering_method or settings.clustering_method
        self.min_cluster_size = min_cluster_size or settings.min_cluster_size
        self.min_samples = settings.min_samples

    def detect_topics(self, module_code: str, db: Session) -> List[Dict]:
        """
        Detect topics across all lectures in a module

        Args:
            module_code: Module code to analyze
            db: Database session

        Returns:
            List of detected topics with appearances
        """
        print(f"Starting topic detection for module: {module_code}")

        # Get all chunks for this module with their embeddings
        chunks = self._get_module_chunks(module_code, db)

        if len(chunks) < self.min_cluster_size:
            raise ValueError(
                f"Not enough chunks for clustering. "
                f"Found {len(chunks)}, need at least {self.min_cluster_size}"
            )

        print(f"Found {len(chunks)} chunks from {len(set(c['lecture_id'] for c in chunks))} lectures")

        # Extract embeddings
        embeddings = np.array([chunk["embedding"] for chunk in chunks])
        print(f"Embeddings shape: {embeddings.shape}")

        # Perform clustering
        labels = self._cluster_embeddings(embeddings)
        print(f"Clustering produced {len(set(labels)) - (1 if -1 in labels else 0)} clusters")

        # Group chunks by cluster
        cluster_groups = self._group_by_cluster(chunks, labels)

        # Generate topic labels using LLM
        topics_data = self._generate_topic_labels(cluster_groups, db)

        # Store topics in database
        stored_topics = self._store_topics(module_code, topics_data, db)

        return stored_topics

    def _get_module_chunks(self, module_code: str, db: Session) -> List[Dict]:
        """Get all chunks for a module with metadata"""
        results = db.query(
            Chunk.id,
            Chunk.lecture_id,
            Chunk.content,
            Chunk.slide_number,
            Chunk.embedding,
            Lecture.week_number,
            Lecture.title.label("lecture_title")
        ).join(
            Lecture, Chunk.lecture_id == Lecture.id
        ).filter(
            Lecture.module_code == module_code.upper()
        ).filter(
            Chunk.embedding.isnot(None)
        ).all()

        chunks = []
        for row in results:
            chunks.append({
                "chunk_id": str(row.id),
                "lecture_id": str(row.lecture_id),
                "content": row.content,
                "slide_number": row.slide_number,
                "embedding": row.embedding,
                "week_number": row.week_number,
                "lecture_title": row.lecture_title
            })

        return chunks

    def _cluster_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """Cluster embeddings using configured method"""
        if self.clustering_method == "hdbscan" and HDBSCAN_AVAILABLE:
            return self._cluster_hdbscan(embeddings)
        else:
            return self._cluster_kmeans(embeddings)

    def _cluster_hdbscan(self, embeddings: np.ndarray) -> np.ndarray:
        """Cluster using HDBSCAN (density-based)"""
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric='euclidean'
        )
        labels = clusterer.fit_predict(embeddings)
        return labels

    def _cluster_kmeans(self, embeddings: np.ndarray) -> np.ndarray:
        """Cluster using K-Means"""
        # Estimate number of clusters (heuristic: sqrt(n/2))
        n_clusters = max(3, min(20, int(np.sqrt(len(embeddings) / 2))))
        print(f"Using K-Means with {n_clusters} clusters")

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        return labels

    def _group_by_cluster(self, chunks: List[Dict], labels: np.ndarray) -> Dict[int, List[Dict]]:
        """Group chunks by cluster label"""
        cluster_groups = defaultdict(list)

        for chunk, label in zip(chunks, labels):
            if label != -1:  # Skip noise points in HDBSCAN
                cluster_groups[label].append(chunk)

        # Filter out small clusters
        filtered_groups = {
            label: chunks
            for label, chunks in cluster_groups.items()
            if len(chunks) >= self.min_cluster_size
        }

        return filtered_groups

    def _generate_topic_labels(self, cluster_groups: Dict[int, List[Dict]], db: Session) -> List[Dict]:
        """Generate topic labels using LLM"""
        topics_data = []

        for cluster_id, chunks in cluster_groups.items():
            print(f"Generating label for cluster {cluster_id} with {len(chunks)} chunks")

            # Sample representative chunks (max 5)
            sample_size = min(5, len(chunks))
            sampled_chunks = np.random.choice(chunks, size=sample_size, replace=False)

            # Build prompt for LLM
            chunks_text = "\n\n".join([
                f"Chunk {i+1}: {chunk['content'][:200]}..."
                for i, chunk in enumerate(sampled_chunks)
            ])

            prompt = f"""Analyze these text excerpts from university lecture slides and identify the main topic.

{chunks_text}

Provide:
1. A concise topic name (2-5 words)
2. A brief description (1 sentence)

Format your response as:
TOPIC: <topic name>
DESCRIPTION: <description>"""

            try:
                response = llm_provider.generate(
                    prompt=prompt,
                    system_prompt="You are an expert at analyzing educational content and identifying key topics."
                )

                # Parse response
                topic_name, description = self._parse_llm_response(response)

                # Track appearances across lectures and weeks
                appearances = self._track_appearances(chunks)

                topics_data.append({
                    "name": topic_name,
                    "description": description,
                    "chunks": chunks,
                    "appearances": appearances
                })

            except Exception as e:
                print(f"Error generating label for cluster {cluster_id}: {str(e)}")
                # Fallback: use most common words
                topics_data.append({
                    "name": f"Topic {cluster_id}",
                    "description": "Auto-generated topic",
                    "chunks": chunks,
                    "appearances": self._track_appearances(chunks)
                })

        return topics_data

    def _parse_llm_response(self, response: str) -> Tuple[str, str]:
        """Parse LLM response to extract topic name and description"""
        lines = response.strip().split("\n")
        topic_name = "Untitled Topic"
        description = ""

        for line in lines:
            line = line.strip()
            if line.startswith("TOPIC:"):
                topic_name = line.replace("TOPIC:", "").strip()
            elif line.startswith("DESCRIPTION:"):
                description = line.replace("DESCRIPTION:", "").strip()

        return topic_name, description

    def _track_appearances(self, chunks: List[Dict]) -> List[Dict]:
        """Track topic appearances across lectures"""
        lecture_appearances = defaultdict(lambda: {"chunks": [], "slides": set()})

        for chunk in chunks:
            lecture_id = chunk["lecture_id"]
            lecture_appearances[lecture_id]["chunks"].append(chunk)
            lecture_appearances[lecture_id]["slides"].add(chunk["slide_number"])

        appearances = []
        for lecture_id, data in lecture_appearances.items():
            # Get first chunk for metadata
            first_chunk = data["chunks"][0]

            appearances.append({
                "lecture_id": lecture_id,
                "week_number": first_chunk["week_number"],
                "lecture_title": first_chunk["lecture_title"],
                "frequency": len(data["chunks"]),
                "first_slide": min(data["slides"])
            })

        # Sort by week number
        appearances.sort(key=lambda x: x["week_number"])

        return appearances

    def _store_topics(self, module_code: str, topics_data: List[Dict], db: Session) -> List[Dict]:
        """Store topics in database"""
        stored_topics = []

        for topic_data in topics_data:
            # Create topic
            topic = Topic(
                name=topic_data["name"],
                description=topic_data["description"],
                module_code=module_code.upper()
            )
            db.add(topic)
            db.flush()  # Get ID without committing

            # Create topic appearances
            for appearance in topic_data["appearances"]:
                topic_appearance = TopicAppearance(
                    topic_id=topic.id,
                    lecture_id=appearance["lecture_id"],
                    frequency=appearance["frequency"],
                    first_slide=appearance["first_slide"]
                )
                db.add(topic_appearance)

            db.commit()
            db.refresh(topic)

            stored_topics.append({
                "id": str(topic.id),
                "name": topic.name,
                "description": topic.description,
                "appearances": topic_data["appearances"]
            })

        return stored_topics

    def infer_prerequisites(self, topics: List[Dict]) -> List[Dict]:
        """
        Infer prerequisite relationships between topics based on temporal ordering

        Args:
            topics: List of topics with appearances

        Returns:
            List of edges representing prerequisites
        """
        edges = []

        for i, topic1 in enumerate(topics):
            first_week1 = min(app["week_number"] for app in topic1["appearances"])

            for topic2 in topics[i+1:]:
                first_week2 = min(app["week_number"] for app in topic2["appearances"])

                # If topic1 appears before topic2, it might be a prerequisite
                if first_week1 < first_week2:
                    # Check if they co-occur in later lectures
                    topic1_weeks = set(app["week_number"] for app in topic1["appearances"])
                    topic2_weeks = set(app["week_number"] for app in topic2["appearances"])

                    overlap = topic1_weeks & topic2_weeks

                    if overlap:  # They appear together later
                        edges.append({
                            "source": topic1["id"],
                            "target": topic2["id"],
                            "type": "prerequisite"
                        })

        return edges


# Singleton instance
topic_detector = TopicDetector()
