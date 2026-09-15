"""Metadata management for document chunks."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .models import ChunkMetadata, DocumentChunk

logger = logging.getLogger(__name__)


class ChunkMetadataManager:
    """
    Manages metadata for document chunks.
    
    Responsibilities:
    - Track chunk metadata across pipeline
    - Enrich chunks with additional metadata
    - Manage access control and permissions
    - Track chunk lineage and provenance
    """

    def __init__(self):
        """Initialize metadata manager."""
        self.chunk_registry: Dict[str, DocumentChunk] = {}
        logger.info("ChunkMetadataManager initialized")

    def register_chunk(self, chunk: DocumentChunk) -> None:
        """
        Register a chunk and its metadata.
        
        Args:
            chunk: DocumentChunk to register
        """
        self.chunk_registry[chunk.chunk_id] = chunk
        logger.debug(f"Registered chunk: {chunk.chunk_id}")

    def get_chunk(self, chunk_id: str) -> Optional[DocumentChunk]:
        """
        Retrieve chunk by ID.
        
        Args:
            chunk_id: Unique chunk identifier
            
        Returns:
            DocumentChunk or None if not found
        """
        return self.chunk_registry.get(chunk_id)

    def update_metadata(
        self, chunk_id: str, metadata_updates: Dict[str, Any]
    ) -> None:
        """
        Update metadata for a specific chunk.
        
        Args:
            chunk_id: Chunk identifier
            metadata_updates: Dictionary of metadata fields to update
        """
        chunk = self.chunk_registry.get(chunk_id)
        if not chunk:
            raise ValueError(f"Chunk not found: {chunk_id}")

        for key, value in metadata_updates.items():
            if hasattr(chunk.metadata, key):
                setattr(chunk.metadata, key, value)

        logger.debug(f"Updated metadata for chunk: {chunk_id}")

    def set_access_level(self, chunk_id: str, access_level: int) -> None:
        """
        Set access control level for chunk.
        
        Args:
            chunk_id: Chunk identifier
            access_level: AccessLevel value
        """
        chunk = self.chunk_registry.get(chunk_id)
        if chunk:
            chunk.metadata.access_level = access_level

    def get_chunks_by_document(self, document_id: str) -> List[DocumentChunk]:
        """
        Get all chunks for a specific document.
        
        Args:
            document_id: Document identifier
            
        Returns:
            List of DocumentChunk objects for the document
        """
        return [
            chunk for chunk in self.chunk_registry.values()
            if chunk.document_id == document_id
        ]

    def get_chunks_by_access_level(self, access_level: int) -> List[DocumentChunk]:
        """
        Get chunks by access level.
        
        Args:
            access_level: AccessLevel value
            
        Returns:
            List of chunks with matching access level
        """
        return [
            chunk for chunk in self.chunk_registry.values()
            if chunk.metadata.access_level == access_level
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get metadata statistics for all registered chunks.
        
        Returns:
            Dictionary with statistics
        """
        chunks = list(self.chunk_registry.values())
        
        if not chunks:
            return {
                "total_chunks": 0,
                "documents": 0,
                "avg_chunk_size": 0,
            }

        total_content_size = sum(len(chunk.content) for chunk in chunks)
        unique_documents = set(chunk.document_id for chunk in chunks)

        return {
            "total_chunks": len(chunks),
            "unique_documents": len(unique_documents),
            "avg_chunk_size": total_content_size / len(chunks) if chunks else 0,
            "total_content_size": total_content_size,
            "chunking_strategies": list(set(chunk.strategy_type.value for chunk in chunks)),
        }

    def clear(self) -> None:
        """Clear all registered chunks."""
        self.chunk_registry.clear()
        logger.info("ChunkMetadataManager cleared")
