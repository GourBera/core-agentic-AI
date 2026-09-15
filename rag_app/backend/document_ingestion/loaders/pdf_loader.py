"""PDF Document Loader - Handles PDF files with text and OCR extraction."""

from pathlib import Path
from typing import List, Union

from ..metadata.models import DocumentType, RawDocument
from .base import DocumentLoader


class PDFLoader(DocumentLoader):
    """
    Load and extract content from PDF files.
    
    Features:
    - Text extraction via pdfplumber or PyPDF2
    - Page-by-page extraction with metadata tracking
    - OCR fallback for scanned PDFs (using pytesseract)
    - Preserves page numbers and table structures
    """

    def load(self, source: Union[str, Path]) -> List[RawDocument]:
        """
        Load PDF and extract text from all pages.
        
        Args:
            source: Path to PDF file
            
        Returns:
            List of RawDocument objects (one per page or merged)
            
        Raises:
            FileNotFoundError: If PDF file does not exist
            ValueError: If PDF is corrupted or unreadable
        """
        pass

    def supports(self, source: Union[str, Path]) -> bool:
        """Check if source is a valid PDF file."""
        pass

    def get_document_type(self) -> DocumentType:
        """Return DocumentType.PDF."""
        pass

    def _extract_text_with_layout(self, source: Path) -> str:
        """Extract text while preserving document layout."""
        pass

    def _extract_with_ocr(self, source: Path) -> str:
        """Extract text from scanned pages using OCR."""
        pass

    def _extract_tables(self, source: Path) -> List[dict]:
        """Extract and structure table data from PDF."""
        pass
