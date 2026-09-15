"""Slide chunking strategy - Presentation slide-aware splitting."""

from typing import List

from ..metadata.models import ChunkingStrategyType, DocumentChunk, PreprocessedDocument
from .base import ChunkingStrategy


class SlideChunker(ChunkingStrategy):
    """
    Chunk presentations with slide-aware strategy.
    
    Features:
    - One chunk per slide as primary unit
    - Speaker notes inclusion
    - Section/part awareness
    - Image and media reference tracking
    - Slide notes and annotations
    
    Best for: PowerPoint, Google Slides, Keynote
    """

    def __init__(
        self,
        include_speaker_notes: bool = True,
        include_slide_images: bool = True,
        max_chunk_size: int = 2000,
    ):
        """
        Initialize slide chunker.
        
        Args:
            include_speaker_notes: Include speaker notes in chunks
            include_slide_images: Include image descriptions
            max_chunk_size: Maximum chunk size in characters
        """
        self.include_speaker_notes = include_speaker_notes
        self.include_slide_images = include_slide_images
        self.max_chunk_size = max_chunk_size

    def chunk(self, document: PreprocessedDocument) -> List[DocumentChunk]:
        """
        Split presentation by slides.
        
        Args:
            document: Preprocessed presentation document
            
        Returns:
            List of slide-based chunks
        """
        pass

    def get_strategy_type(self) -> ChunkingStrategyType:
        """Return ChunkingStrategyType.SLIDE."""
        pass

    def _extract_slides(self) -> List[dict]:
        """Extract all slides from presentation."""
        pass

    def _create_slide_chunk(
        self, slide: dict, slide_number: int, total_slides: int
    ) -> DocumentChunk:
        """Create chunk from single slide."""
        pass

    def _format_slide_content(self, slide: dict) -> str:
        """Format slide text, titles, and content."""
        pass

    def _include_speaker_notes(self, slide: dict) -> str:
        """Format speaker notes with slide content."""
        pass

    def _include_slide_images(self, slide: dict) -> str:
        """Create descriptions for images and media."""
        pass

    def _detect_section_boundaries(self) -> dict:
        """Detect presentation section breaks."""
        pass

    def _add_slide_context(self, chunk: DocumentChunk, slide_number: int) -> DocumentChunk:
        """Add slide number and presentation context."""
        pass
