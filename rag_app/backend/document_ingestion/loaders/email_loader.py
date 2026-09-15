"""Email Document Loader - Handles email files and messages."""

from pathlib import Path
from typing import List, Union

from ..metadata.models import DocumentType, RawDocument
from .base import DocumentLoader


class EmailLoader(DocumentLoader):
    """
    Load and extract content from email files (EML, MSG, MBOX).
    
    Features:
    - MIME message parsing
    - Recursive attachment extraction and processing
    - Thread/conversation structure preservation
    - Header metadata extraction (sender, recipient, date, subject)
    - HTML and plain text body extraction
    - Attachment type detection and loader routing
    """

    def load(self, source: Union[str, Path]) -> List[RawDocument]:
        """
        Load email file and extract message content.
        
        Args:
            source: Path to email file (EML, MSG, MBOX)
            
        Returns:
            List of RawDocument objects (including attachments)
        """
        pass

    def supports(self, source: Union[str, Path]) -> bool:
        """Check if source is a valid email file."""
        pass

    def get_document_type(self) -> DocumentType:
        """Return DocumentType.EMAIL."""
        pass

    def _parse_mime_message(self, source: Path) -> dict:
        """Parse MIME message structure."""
        pass

    def _extract_headers(self, source: Path) -> dict:
        """Extract email headers (from, to, date, subject, etc.)."""
        pass

    def _extract_body(self, source: Path) -> dict:
        """Extract both HTML and plain text body."""
        pass

    def _extract_attachments(self, source: Path) -> List[dict]:
        """Extract all attachments and route to appropriate loaders."""
        pass

    def _preserve_thread_structure(self, source: Path) -> dict:
        """Track in-reply-to and thread relationships."""
        pass

    def _recursively_process_attachments(
        self, attachments: List[dict], registry
    ) -> List[RawDocument]:
        """
        Recursively process each attachment using FileTypeRegistry.
        
        Args:
            attachments: List of attachment metadata
            registry: FileTypeRegistry instance for routing
            
        Returns:
            List of processed RawDocument objects from attachments
        """
        pass
