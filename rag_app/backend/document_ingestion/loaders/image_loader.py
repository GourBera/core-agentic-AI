"""Image Document Loader - Handles image files with OCR."""

from pathlib import Path
from typing import List, Union

from ..metadata.models import DocumentType, RawDocument
from .base import DocumentLoader


class ImageLoader(DocumentLoader):
    """
    Load and extract content from image files.
    
    Features:
    - OCR text extraction (Tesseract, EasyOCR)
    - Image metadata extraction (resolution, camera data, etc.)
    - Confidence scoring for OCR results
    - Support for multiple languages via OCR
    - Automatic image rotation/preprocessing for better OCR
    """

    def load(self, source: Union[str, Path]) -> List[RawDocument]:
        """
        Load image and extract text via OCR.
        
        Args:
            source: Path to image file
            
        Returns:
            List of RawDocument objects (typically single item)
        """
        pass

    def supports(self, source: Union[str, Path]) -> bool:
        """Check if source is a valid image file."""
        pass

    def get_document_type(self) -> DocumentType:
        """Return DocumentType.IMAGE."""
        pass

    def _extract_text_via_ocr(self, source: Path) -> str:
        """Extract text from image using OCR."""
        pass

    def _preprocess_image(self, source: Path) -> Path:
        """Enhance image for better OCR (rotation, contrast, etc.)."""
        pass

    def _extract_metadata(self, source: Path) -> dict:
        """Extract EXIF and other image metadata."""
        pass

    def _get_ocr_confidence_score(self) -> float:
        """Calculate confidence score for OCR extraction."""
        pass

    def _detect_language(self, source: Path) -> str:
        """Detect language of text in image."""
        pass
