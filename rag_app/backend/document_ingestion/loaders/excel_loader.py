"""Excel Document Loader - Handles spreadsheet files."""

from pathlib import Path
from typing import List, Union

from ..metadata.models import DocumentType, RawDocument
from .base import DocumentLoader


class ExcelLoader(DocumentLoader):
    """
    Load and extract content from Excel/XLSX files.
    
    Features:
    - Sheet-by-sheet extraction
    - Preserves table structure and formulas
    - Cell metadata and formatting awareness
    - Handles merged cells and named ranges
    """

    def load(self, source: Union[str, Path]) -> List[RawDocument]:
        """
        Load Excel file and extract sheet data.
        
        Args:
            source: Path to Excel file
            
        Returns:
            List of RawDocument objects (one per sheet)
        """
        pass

    def supports(self, source: Union[str, Path]) -> bool:
        """Check if source is a valid Excel file."""
        pass

    def get_document_type(self) -> DocumentType:
        """Return DocumentType.XLSX."""
        pass

    def _extract_sheets(self, source: Path) -> List[dict]:
        """Extract all sheets with structure preserved."""
        pass

    def _extract_formulas(self, source: Path) -> List[dict]:
        """Extract formulas and calculated values."""
        pass

    def _extract_named_ranges(self, source: Path) -> dict:
        """Extract named ranges and their definitions."""
        pass

    def _format_as_markdown_tables(self, sheets: List[dict]) -> str:
        """Convert sheet data to markdown table format for better chunking."""
        pass
