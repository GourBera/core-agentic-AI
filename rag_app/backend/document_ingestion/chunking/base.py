"""Base classes and abstractions for chunking strategies."""

from abc import ABC, abstractmethod
from typing import List

from ..metadata.models import ChunkingStrategyType, DocumentChunk, PreprocessedDocument


class ChunkingStrategy(ABC):
    """
    Abstract base class for all chunking strategies.
    
    Each strategy handles splitting preprocessed documents into chunks
    for embedding and retrieval. Different strategies optimize for different content types.
    """

    @abstractmethod
    def chunk(self, document: PreprocessedDocument) -> List[DocumentChunk]:
        """
        Split document into chunks using this strategy.
        
        Args:
            document: Preprocessed document to chunk
            
        Returns:
            List of DocumentChunk objects
        """
        pass

    @abstractmethod
    def get_strategy_type(self) -> ChunkingStrategyType:
        """
        Get the strategy type identifier.
        
        Returns:
            ChunkingStrategyType enum value
        """
        pass

    def is_applicable(self, document: PreprocessedDocument) -> bool:
        """
        Check if strategy should be applied to this document.
        
        Default: applies to all documents. Override for conditional application.
        
        Args:
            document: Document to check
            
        Returns:
            True if strategy should chunk this document
        """
        return True


class ChunkingStrategySelector:
    """
    Registry pattern: selects appropriate chunking strategy per document type.
    
    Allows different chunking approaches for different formats:
    - Structural for PDFs and Word docs
    - Table-aware for Excel
    - Slide-based for PowerPoint
    - Etc.
    """

    def __init__(self):
        """Initialize selector with empty strategy map."""
        self._strategies: dict = {}

    def register(
        self,
        document_type: str,
        strategy_class: type,
    ) -> "ChunkingStrategySelector":
        """
        Register a chunking strategy for a document type.
        
        Args:
            document_type: Document type key
            strategy_class: Chunking strategy class (not instantiated)
            
        Returns:
            Self for method chaining
        """
        self._strategies[document_type] = strategy_class
        return self

    def select(self, document_type: str) -> ChunkingStrategy:
        """
        Get chunking strategy for a document type.
        
        Args:
            document_type: Document type key
            
        Returns:
            Instantiated chunking strategy
            
        Raises:
            ValueError: If no strategy registered for type
        """
        strategy_class = self._strategies.get(document_type)
        if strategy_class is None:
            raise ValueError(
                f"No chunking strategy registered for type: {document_type}"
            )
        return strategy_class()

    def has_strategy(self, document_type: str) -> bool:
        """
        Check if strategy is registered for document type.
        
        Args:
            document_type: Document type key
            
        Returns:
            True if strategy is registered
        """
        return document_type in self._strategies
