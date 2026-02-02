"""
Text Chunking Strategies
"""
from typing import List, Dict
from ..config import settings


class TextChunker:
    """Service for chunking text into appropriate sizes for embedding"""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

    def chunk_by_slide(self, slides: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Chunk text at slide level (one chunk per slide)

        Args:
            slides: List of slide dicts with page_number and content

        Returns:
            List of chunks with metadata
        """
        chunks = []

        for slide in slides:
            content = slide["content"].strip()

            # Skip empty slides
            if not content or content == "[OCR required - scanned image]":
                continue

            # If slide is too long, split it
            if len(content) > self.chunk_size * 1.5:
                sub_chunks = self._split_long_text(content)
                for i, sub_chunk in enumerate(sub_chunks):
                    chunks.append({
                        "slide_number": slide["page_number"],
                        "content": sub_chunk,
                        "sub_chunk_index": i
                    })
            else:
                chunks.append({
                    "slide_number": slide["page_number"],
                    "content": content,
                    "sub_chunk_index": 0
                })

        return chunks

    def chunk_with_overlap(self, text: str, metadata: Dict = None) -> List[Dict[str, any]]:
        """
        Chunk text with overlap for better context preservation

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks

        Returns:
            List of chunks with overlap
        """
        chunks = []
        words = text.split()

        # Calculate words per chunk
        words_per_chunk = self.chunk_size // 5  # Approximate words
        overlap_words = self.chunk_overlap // 5

        start = 0
        chunk_index = 0

        while start < len(words):
            end = start + words_per_chunk
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            chunk_data = {
                "content": chunk_text,
                "chunk_index": chunk_index
            }

            if metadata:
                chunk_data.update(metadata)

            chunks.append(chunk_data)

            # Move start position with overlap
            start = end - overlap_words
            chunk_index += 1

        return chunks

    def _split_long_text(self, text: str) -> List[str]:
        """
        Split long text into chunks

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        chunks = []
        words = text.split()
        words_per_chunk = self.chunk_size // 5

        for i in range(0, len(words), words_per_chunk):
            chunk = " ".join(words[i:i + words_per_chunk])
            chunks.append(chunk)

        return chunks

    def chunk_by_sentences(self, text: str, max_sentences: int = 5) -> List[str]:
        """
        Chunk text by sentences

        Args:
            text: Text to chunk
            max_sentences: Maximum sentences per chunk

        Returns:
            List of text chunks
        """
        # Simple sentence splitting (could use spaCy for better results)
        sentences = []
        for s in text.split(". "):
            s = s.strip()
            if s:
                if not s.endswith("."):
                    s += "."
                sentences.append(s)

        chunks = []
        current_chunk = []

        for sentence in sentences:
            current_chunk.append(sentence)

            if len(current_chunk) >= max_sentences:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        # Add remaining sentences
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


# Singleton instance
text_chunker = TextChunker()
