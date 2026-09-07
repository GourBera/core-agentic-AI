"""Layer 3b: Vector Store - Pinecone integration for semantic search."""

import logging
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class PineconeVectorStore:
    """Layer 3b: Manage vectors and documents in Pinecone."""
    
    def __init__(self, config: "PineconeConfig"):
        """Initialize Pinecone vector store."""
        self.config = config
        self.documents_stored = 0
        
        try:
            from pinecone import Pinecone
            
            # Initialize Pinecone
            self.pc = Pinecone(api_key=config.api_key)
            self.index = self.pc.Index(config.index_name)
            
            logger.info(
                "pinecone_initialized",
                index_name=config.index_name,
                dimension=config.dimension,
                metric=config.metric
            )
        
        except Exception as e:
            logger.error("pinecone_initialization_failed", error=str(e))
            raise
    
    async def add_documents(
        self,
        chunks: List["Chunk"],
        embeddings: List[List[float]],
        metadata: Dict[str, Any]
    ) -> int:
        """Add documents with embeddings to Pinecone."""
        logger.info(
            "adding_documents_to_pinecone",
            chunk_count=len(chunks),
            embedding_dim=len(embeddings[0]) if embeddings else 0
        )
        
        vectors_to_upsert = []
        
        for chunk, embedding in zip(chunks, embeddings):
            # Combine chunk metadata with document metadata
            vector_metadata = {
                **chunk.metadata,
                **metadata,
                "content": chunk.content[:1000],  # Limit content size in metadata
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
            }
            
            vectors_to_upsert.append((
                chunk.id,
                embedding,
                vector_metadata
            ))
        
        try:
            # Upsert to Pinecone in batches
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i+batch_size]
                self.index.upsert(vectors=batch)
                logger.info(
                    "batch_upserted",
                    batch_num=i//batch_size + 1,
                    batch_size=len(batch)
                )
            
            self.documents_stored += len(chunks)
            logger.info(
                "documents_added_to_pinecone",
                total_added=len(chunks),
                total_in_store=self.documents_stored
            )
            
            return len(chunks)
        
        except Exception as e:
            logger.error("upsert_failed", error=str(e))
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None
    ) -> List["Chunk"]:
        """Search for similar documents in Pinecone."""
        logger.info("searching_pinecone", top_k=top_k)
        
        try:
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace
            )
            
            # Convert results to Chunk objects
            chunks = []
            for match in results.get("matches", []):
                chunk = self._reconstruct_chunk(match)
                chunks.append(chunk)
            
            logger.info(
                "search_complete",
                results_found=len(chunks),
                top_score=results["matches"][0]["score"] if results["matches"] else 0
            )
            
            return chunks
        
        except Exception as e:
            logger.error("search_failed", error=str(e))
            return []
    
    def _reconstruct_chunk(self, match: Dict[str, Any]) -> "Chunk":
        """Reconstruct Chunk object from Pinecone match."""
        from .chunking_strategy import Chunk
        
        metadata = match.get("metadata", {})
        
        return Chunk(
            id=match["id"],
            content=metadata.get("content", ""),
            document_id=metadata.get("document_id", ""),
            chunk_index=metadata.get("chunk_index", 0),
            strategy=metadata.get("chunking_strategy", "unknown"),
            metadata=metadata
        )
    
    async def delete_documents(self, chunk_ids: List[str]) -> int:
        """Delete documents from Pinecone."""
        logger.info("deleting_documents", count=len(chunk_ids))
        
        try:
            self.index.delete(ids=chunk_ids)
            self.documents_stored -= len(chunk_ids)
            logger.info("documents_deleted", count=len(chunk_ids))
            return len(chunk_ids)
        except Exception as e:
            logger.error("delete_failed", error=str(e))
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        try:
            stats = self.index.describe_index_stats()
            return {
                "documents_stored": self.documents_stored,
                "index_name": self.config.index_name,
                "dimension": self.config.dimension,
                "total_vector_count": stats.get("total_vector_count", 0),
            }
        except Exception as e:
            logger.error("stats_retrieval_failed", error=str(e))
            return {
                "documents_stored": self.documents_stored,
                "error": str(e)
            }
                vector_id = f"{doc.source}_{doc.chunk_id}"
                vectors_to_upsert.append(
                    (vector_id, embedding, {"text": doc.content, **doc.metadata})
                )

            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i : i + batch_size]
                self.index.upsert(vectors=batch)

            logger.info(f"Added {len(documents)} documents to Pinecone")
        except Exception as e:
            logger.error(f"Error adding documents to Pinecone: {e}")
            raise

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Document, float]]:
        """Search Pinecone."""
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
            )

            documents = []
            for match in results.matches:
                metadata = match.metadata or {}
                text = metadata.pop("text", "")
                doc = Document(
                    content=text,
                    metadata=metadata,
                )
                documents.append((doc, match.score))

            return documents
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            raise

    def delete_collection(self):
        """Delete index."""
        try:
            self.pc.delete_index(self.index_name)
            logger.info(f"Deleted index: {self.index_name}")
        except Exception as e:
            logger.error(f"Error deleting index: {e}")
            raise

    def get_document_count(self) -> int:
        """Get number of documents."""
        try:
            stats = self.index.describe_index_stats()
            return stats.total_vector_count
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
