"""
Embedding Service
Supports local (sentence-transformers) and OpenAI embeddings
"""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI

from ..config import settings


class EmbeddingService:
    """Service for generating text embeddings"""

    def __init__(self, provider: str = None, model: str = None):
        self.provider = provider or settings.embedding_provider
        self.model_name = model or settings.embedding_model
        self.dimension = settings.embedding_dimension

        if self.provider == "local":
            self._init_local_model()
        elif self.provider == "openai":
            self._init_openai_client()
        else:
            raise ValueError(f"Unknown embedding provider: {self.provider}")

    def _init_local_model(self):
        """Initialize local sentence-transformers model"""
        print(f"Loading local embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        # Update dimension based on actual model
        self.dimension = self.model.get_sentence_embedding_dimension()

    def _init_openai_client(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=settings.openai_api_key)
        # OpenAI text-embedding-3-small is 1536 dimensions
        # text-embedding-3-large is 3072 dimensions
        if "large" in self.model_name:
            self.dimension = 3072
        else:
            self.dimension = 1536

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if self.provider == "local":
            return self._embed_local([text])[0]
        elif self.provider == "openai":
            return self._embed_openai([text])[0]

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once

        Returns:
            List of embedding vectors
        """
        if self.provider == "local":
            return self._embed_local(texts, batch_size)
        elif self.provider == "openai":
            return self._embed_openai(texts, batch_size)

    def _embed_local(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings using local model"""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 10,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def _embed_openai(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        all_embeddings = []

        # Process in batches (OpenAI has rate limits)
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=batch
                )

                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

            except Exception as e:
                raise RuntimeError(f"OpenAI embedding error: {str(e)}")

        return all_embeddings

    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between -1 and 1
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def get_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service"""
        return self.dimension


# Singleton instance
embedding_service = EmbeddingService()
