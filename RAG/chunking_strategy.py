"""Layer 2: Chunking Strategy - Overlap and Semantic chunking."""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class Chunk:
    """Represents a document chunk."""
    id: str
    content: str
    document_id: str
    chunk_index: int
    strategy: str  # "overlap", "semantic", or "hybrid"
    metadata: Dict[str, Any]


class ChunkingStrategy(str, Enum):
    """Available chunking strategies."""
    OVERLAP = "overlap"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class HybridChunker:
    """Layer 2: Hybrid chunking combining overlap and semantic strategies."""
    
    def __init__(self, config: "ChunkingConfig"):
        """Initialize hybrid chunker."""
        self.config = config
        self.chunks_created = 0
        logger.info(
            "hybrid_chunker_initialized",
            overlap_size=config.overlap_chunk_size,
            semantic_size=config.semantic_chunk_size,
            semantic_weight=config.semantic_weight
        )
    
    async def create_chunks(self, documents: List["Document"]) -> List[Chunk]:
        """Create chunks using hybrid strategy."""
        logger.info("creating_chunks", document_count=len(documents))
        
        all_chunks = []
        
        for doc in documents:
            # Generate overlap-based chunks
            if self.config.use_overlap_chunking:
                overlap_chunks = self._create_overlap_chunks(doc)
                logger.info(
                    "overlap_chunks_created",
                    doc_id=doc.id,
                    chunk_count=len(overlap_chunks)
                )
                all_chunks.extend(overlap_chunks)
            
            # Generate semantic chunks
            if self.config.use_semantic_chunking:
                semantic_chunks = await self._create_semantic_chunks(doc)
                logger.info(
                    "semantic_chunks_created",
                    doc_id=doc.id,
                    chunk_count=len(semantic_chunks)
                )
                all_chunks.extend(semantic_chunks)
        
        self.chunks_created += len(all_chunks)
        logger.info("chunks_creation_complete", total_chunks=len(all_chunks))
        return all_chunks
    
    def _create_overlap_chunks(self, document: "Document") -> List[Chunk]:
        """Create chunks with overlap using recursive character splitting."""
        chunks = []
        text = document.content
        chunk_size = self.config.overlap_chunk_size
        overlap = self.config.overlap_chunk_overlap
        
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]
            
            chunk = Chunk(
                id=f"{document.id}_overlap_{chunk_index}",
                content=chunk_text,
                document_id=document.id,
                chunk_index=chunk_index,
                strategy=ChunkingStrategy.OVERLAP.value,
                metadata={
                    **document.metadata,
                    "chunking_strategy": "overlap",
                    "chunk_start": start,
                    "chunk_end": end,
                }
            )
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap
            chunk_index += 1
            
            # Stop if we've reached the end
            if end == len(text):
                break
        
        return chunks
    
    async def _create_semantic_chunks(self, document: "Document") -> List[Chunk]:
        """Create semantically coherent chunks."""
        chunks = []
        sentences = self._split_into_sentences(document.content)
        
        chunk_size = self.config.semantic_chunk_size
        current_chunk = []
        current_length = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > chunk_size and current_chunk:
                # Create a chunk
                chunk_text = " ".join(current_chunk)
                chunk = Chunk(
                    id=f"{document.id}_semantic_{chunk_index}",
                    content=chunk_text,
                    document_id=document.id,
                    chunk_index=chunk_index,
                    strategy=ChunkingStrategy.SEMANTIC.value,
                    metadata={
                        **document.metadata,
                        "chunking_strategy": "semantic",
                        "sentence_count": len(current_chunk),
                    }
                )
                chunks.append(chunk)
                
                # Start new chunk
                current_chunk = [sentence]
                current_length = sentence_length
                chunk_index += 1
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk = Chunk(
                id=f"{document.id}_semantic_{chunk_index}",
                content=chunk_text,
                document_id=document.id,
                chunk_index=chunk_index,
                strategy=ChunkingStrategy.SEMANTIC.value,
                metadata={
                    **document.metadata,
                    "chunking_strategy": "semantic",
                    "sentence_count": len(current_chunk),
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting on common delimiters
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get chunker statistics."""
        return {
            "total_chunks_created": self.chunks_created,
            "strategies_enabled": {
                "overlap": self.config.use_overlap_chunking,
                "semantic": self.config.use_semantic_chunking,
            }
        }
