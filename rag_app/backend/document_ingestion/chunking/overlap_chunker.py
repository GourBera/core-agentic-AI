"""Overlap chunking strategy - Recursive character splitting with overlap."""

from typing import List

from ..metadata.models import ChunkingStrategyType, DocumentChunk, PreprocessedDocument
from .base import ChunkingStrategy


class OverlapChunker(ChunkingStrategy):
    """
    Recursive character-based chunking with configurable overlap.
    
    Features:
    - Fixed chunk size (tokens or characters)
    - Configurable overlap percentage
    - Respects separator boundaries (newlines, spaces)
    - Optimal for continuous prose content
    
    Best for: General text, articles, documentation
    """

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Initialize overlap chunker.
        
        Args:
            chunk_size: Target size per chunk in characters/tokens
            overlap: Overlap size between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: PreprocessedDocument) -> List[DocumentChunk]:
        """
        Split document using overlap strategy.
        
        Args:
            document: Preprocessed document to chunk
            
        Returns:
            List of chunks with overlap
        """
        pass

    def get_strategy_type(self) -> ChunkingStrategyType:
        """Return ChunkingStrategyType.OVERLAP."""
        pass

    def _split_by_character(self, text: str) -> List[str]:
        """Split text into chunks with character-level overlap."""
        pass

    def _calculate_optimal_split_points(self, text: str) -> List[int]:
        """Find optimal split points respecting boundaries."""
        pass

    def _create_chunks_with_overlap(self, chunks: List[str]) -> List[str]:
        """Add overlap between consecutive chunks."""
        pass
