"""Base classes and abstractions for document loaders."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

from ..metadata.models import DocumentType, RawDocument


class DocumentLoader(ABC):
    """
    Abstract base class for all document loaders.
    
    Each concrete implementation handles a specific document type (PDF, DOCX, etc.)
    and extracts raw content into a standardized RawDocument format.
    """

    @abstractmethod
    def load(self, source: Union[str, Path]) -> List[RawDocument]:
        """
        Load and extract content from a document source.
        
        Args:
            source: File path or URI to the document
            
        Returns:
            List of RawDocument objects extracted from the source
            
        Raises:
            FileNotFoundError: If source file does not exist
            ValueError: If source format is invalid
            Exception: For document-specific loading errors
        """
        pass

    @abstractmethod
    def supports(self, source: Union[str, Path]) -> bool:
        """
        Check if this loader can handle the given source.
        
        Args:
            source: File path or URI to check
            
        Returns:
            True if loader can handle this source, False otherwise
        """
        pass

    @abstractmethod
    def get_document_type(self) -> DocumentType:
        """
        Get the DocumentType this loader handles.
        
        Returns:
            DocumentType enum value for this loader
        """
        pass

    def validate_source(self, source: Union[str, Path]) -> Path:
        """
        Validate that source exists and is accessible.
        
        Args:
            source: File path or URI
            
        Returns:
            Validated Path object
            
        Raises:
            FileNotFoundError: If source does not exist
        """
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        return path
