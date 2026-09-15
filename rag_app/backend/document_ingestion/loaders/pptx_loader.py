"""PPTX Document Loader - Handles PowerPoint presentations."""

from pathlib import Path
from typing import List, Union

from ..metadata.models import DocumentType, RawDocument
from .base import DocumentLoader


class PPTXLoader(DocumentLoader):
    """
    Load and extract content from PPTX (PowerPoint) files.
    
    Features:
    - Slide-by-slide extraction
    - Text from slide titles, body, speaker notes
    - Preservation of slide structure and hierarchy
    - Tracking of embedded images and shapes
    """

    def load(self, source: Union[str, Path]) -> List[RawDocument]:
        """
        Load PPTX and extract slide content.
        
        Args:
            source: Path to PPTX file
            
        Returns:
            List of RawDocument objects (one per slide)
        """
        pass

    def supports(self, source: Union[str, Path]) -> bool:
        """Check if source is a valid PPTX file."""
        pass

    def get_document_type(self) -> DocumentType:
        """Return DocumentType.PPTX."""
        pass

    def _extract_slides(self, source: Path) -> List[dict]:
        """Extract all slides with structure."""
        pass

    def _extract_speaker_notes(self, source: Path) -> dict:
        """Extract speaker notes from each slide."""
        pass

    def _extract_slide_images(self, source: Path) -> List[dict]:
        """Extract and track images in slides."""
        pass
