"""
Semantic Chunker.

Splits long documents into semantically meaningful chunks suitable for
embedding and storage in the vector memory.
"""

from backend.models.knowledge import Chunk


class SemanticChunker:
    """Split text into overlapping chunks for embedding.

    Args:
        chunk_size: Approximate character length of each chunk.
        overlap: Number of characters to overlap between consecutive chunks.
    """

    def __init__(self, chunk_size: int = 512, overlap: int = 64) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, source: str = "") -> list[Chunk]:
        """Split *text* into a list of :class:`~backend.models.knowledge.Chunk` objects.

        Args:
            text: The document text to split.
            source: An optional identifier for the originating document.

        Returns:
            Ordered list of chunks covering the full document.
        """
        chunks: list[Chunk] = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(Chunk(text=chunk_text, source=source))
            start += self.chunk_size - self.overlap
        return chunks
