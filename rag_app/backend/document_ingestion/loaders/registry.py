"""File type registry for mapping extensions and types to document loaders."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Type, Union

from ..metadata.models import DocumentType
from .base import DocumentLoader

logger = logging.getLogger(__name__)


class FileTypeRegistry:
    """
    Central registry for managing document loaders and type detection.
    
    Uses singleton pattern to ensure single registry instance across application.
    Maps file extensions to loader classes and provides type detection/routing.
    """

    _instance: Optional["FileTypeRegistry"] = None
    _loaders: Dict[DocumentType, Type[DocumentLoader]] = {}
    _extensions: Dict[str, DocumentType] = {}

    def __new__(cls) -> "FileTypeRegistry":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize registry (called once per singleton instance)."""
        if self._initialized:
            return
        self._loaders = {}
        self._extensions = {}
        self._initialized = True
        logger.info("FileTypeRegistry initialized")

    def register(
        self,
        document_type: DocumentType,
        loader_class: Type[DocumentLoader],
        extensions: List[str],
    ) -> None:
        """
        Register a loader for a specific document type.
        
        Args:
            document_type: DocumentType enum value
            loader_class: Loader class (not instantiated)
            extensions: List of file extensions this loader handles (e.g., ['.pdf'])
            
        Raises:
            ValueError: If loader_class is not a DocumentLoader subclass
        """
        if not issubclass(loader_class, DocumentLoader):
            raise ValueError(
                f"{loader_class.__name__} must be a subclass of DocumentLoader"
            )

        # Register loader for type
        self._loaders[document_type] = loader_class
        
        # Register extensions
        normalized_extensions = [
            ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            for ext in extensions
        ]
        for ext in normalized_extensions:
            self._extensions[ext] = document_type

        logger.info(
            f"Registered {loader_class.__name__} for {document_type.value}",
            extensions=normalized_extensions
        )

    def get_document_type(self, source: Union[str, Path]) -> Optional[DocumentType]:
        """
        Detect document type from file extension.
        
        Args:
            source: File path
            
        Returns:
            DocumentType if recognized, None otherwise
        """
        path = Path(source)
        ext = path.suffix.lower()
        
        doc_type = self._extensions.get(ext)
        if doc_type:
            logger.debug(f"Detected {doc_type.value} for {path.name}")
        else:
            logger.warning(f"Unknown extension: {ext} for {path.name}")
        
        return doc_type

    def get_loader(self, document_type: DocumentType) -> DocumentLoader:
        """
        Get a loader instance for a specific document type.
        
        Args:
            document_type: DocumentType enum value
            
        Returns:
            Instantiated loader for the type
            
        Raises:
            ValueError: If document type is not registered
        """
        loader_class = self._loaders.get(document_type)
        if loader_class is None:
            raise ValueError(
                f"No loader registered for document type: {document_type.value}"
            )
        
        logger.debug(f"Creating loader for {document_type.value}")
        return loader_class()

    def is_registered(self, document_type: DocumentType) -> bool:
        """
        Check if a document type is registered.
        
        Args:
            document_type: DocumentType enum value
            
        Returns:
            True if registered, False otherwise
        """
        return document_type in self._loaders

    def get_supported_extensions(self) -> List[str]:
        """
        Get list of all supported file extensions.
        
        Returns:
            List of supported extensions (e.g., ['.pdf', '.docx', ...])
        """
        return sorted(self._extensions.keys())

    def get_supported_types(self) -> List[DocumentType]:
        """
        Get list of all registered document types.
        
        Returns:
            List of registered DocumentType values
        """
        return list(self._loaders.keys())

    def get_extensions_for_type(self, document_type: DocumentType) -> List[str]:
        """
        Get all extensions for a specific document type.
        
        Args:
            document_type: DocumentType enum value
            
        Returns:
            List of extensions for this type
        """
        return [
            ext for ext, dtype in self._extensions.items()
            if dtype == document_type
        ]

    def reset(self) -> None:
        """Clear all registered loaders and extensions (useful for testing)."""
        self._loaders.clear()
        self._extensions.clear()
        logger.info("FileTypeRegistry reset")
