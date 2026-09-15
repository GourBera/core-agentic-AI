"""HTML Document Loader - Handles HTML files and content."""

from pathlib import Path
from typing import List, Union

from ..metadata.models import DocumentType, RawDocument
from .base import DocumentLoader


class HTMLLoader(DocumentLoader):
    """
    Load and extract content from HTML files.
    
    Features:
    - DOM parsing and semantic tag preservation
    - Text extraction with structure awareness
    - Link and metadata extraction
    - Script and style removal
    - Microdata and structured data extraction (schema.org)
    """

    def load(self, source: Union[str, Path]) -> List[RawDocument]:
        """
        Load HTML file and extract content.
        
        Args:
            source: Path to HTML file
            
        Returns:
            List of RawDocument objects
        """
        pass

    def supports(self, source: Union[str, Path]) -> bool:
        """Check if source is a valid HTML file."""
        pass

    def get_document_type(self) -> DocumentType:
        """Return DocumentType.HTML."""
        pass

    def _parse_dom_structure(self, source: Path) -> dict:
        """Parse HTML DOM and preserve semantic structure."""
        pass

    def _extract_metadata(self, source: Path) -> dict:
        """Extract title, meta tags, and other metadata."""
        pass

    def _extract_links(self, source: Path) -> List[dict]:
        """Extract and track all hyperlinks."""
        pass

    def _extract_structured_data(self, source: Path) -> dict:
        """Extract schema.org or microdata structured data."""
        pass

    def _clean_boilerplate(self, content: str) -> str:
        """Remove navigation, ads, and other boilerplate."""
        pass
