"""
7-Layer Production RAG Pipeline Architecture
==============================================

This module implements a production-grade RAG system with clear separation of concerns:

Layer 1: Document Processing
    ├── Load documents (PDF, DOCX, TXT, MD, etc.)
    ├── Normalize & clean text
    └── Enrich with metadata (user_id, team_id, access_level)

Layer 2: Chunking Strategy
    ├── Overlap Chunking: Recursive character splitting
    ├── Semantic Chunking: AI-aware chunk boundaries
    └── Hybrid: Combine both strategies

Layer 3: Embedding + Storage
    ├── Generate embeddings (Sentence Transformers)
    ├── Cache embeddings for performance
    └── Store in Pinecone with metadata

Layer 4: Query Processing
    ├── Normalize & expand queries
    ├── Detect intent
    └── Cache query results

Layer 5: Permission Filtering
    ├── RBAC/ABAC access control
    ├── Filter by user, team, access_level
    └── Enforce data governance

Layer 6: Reranking
    ├── Cross-encoder based reranking
    ├── Multiple ranking strategies
    └── Confidence scoring

Layer 7: LLM Generation
    ├── Local Ollama integration
    ├── Prompt engineering
    └── Response generation & streaming
"""

import logging
import structlog
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

logger = structlog.get_logger(__name__)


class RAGLayer(str, Enum):
    """Enumeration of RAG pipeline layers."""
    DOCUMENT_PROCESSING = "document_processing"
    CHUNKING = "chunking"
    EMBEDDING_STORAGE = "embedding_storage"
    QUERY_PROCESSING = "query_processing"
    PERMISSION_FILTERING = "permission_filtering"
    RERANKING = "reranking"
    LLM_GENERATION = "llm_generation"


@dataclass
class ProcessingContext:
    """Context tracking through all 7 layers."""
    layer: RAGLayer
    timestamp: datetime
    duration_ms: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer": self.layer.value,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata or {}
        }


class RAGPipeline:
    """
    Production-grade 7-layer RAG pipeline with complete separation of concerns.
    
    Supports:
    - Pinecone for vector storage
    - Local Ollama for LLM inference
    - Hybrid chunking (overlap + semantic)
    - Metadata-based access control
    - Cross-encoder reranking
    """

    def __init__(self, config: "RAGConfig"):
        """Initialize RAG pipeline with all 7 layers."""
        self.config = config
        self.processing_history: List[ProcessingContext] = []
        
        logger.info("initializing_rag_pipeline", layers=7)
        self._initialize_all_layers()
        logger.info("rag_pipeline_initialized", status="ready")

    def _initialize_all_layers(self) -> None:
        """Initialize all 7 pipeline layers."""
        # Layer 1: Document Processing
        logger.info("initializing_layer", layer=1, name="Document Processing")
        from .document_loader import DocumentProcessor
        self.document_processor = DocumentProcessor(self.config)

        # Layer 2: Chunking Strategy
        logger.info("initializing_layer", layer=2, name="Chunking Strategy")
        from .chunking_strategy import HybridChunker
        self.chunker = HybridChunker(self.config.chunking)

        # Layer 3: Embedding + Storage
        logger.info("initializing_layer", layer=3, name="Embedding + Storage")
        from .embeddings import EmbeddingEngine
        from .vector_store import PineconeVectorStore
        self.embedding_engine = EmbeddingEngine(self.config.embedding)
        self.vector_store = PineconeVectorStore(self.config.pinecone)

        # Layer 4: Query Processing
        logger.info("initializing_layer", layer=4, name="Query Processing")
        from .query_processor import QueryProcessor
        self.query_processor = QueryProcessor(self.config)

        # Layer 5: Permission Filtering
        logger.info("initializing_layer", layer=5, name="Permission Filtering")
        from .access_control import AccessControl
        self.access_control = AccessControl(self.config.metadata)

        # Layer 6: Reranking
        logger.info("initializing_layer", layer=6, name="Reranking")
        from .reranker import CrossEncoderReranker
        self.reranker = CrossEncoderReranker(self.config.retrieval)

        # Layer 7: LLM Generation
        logger.info("initializing_layer", layer=7, name="LLM Generation")
        from .llm_client import OllamaClient
        self.llm_client = OllamaClient(self.config.ollama)

    async def ingest_documents(
        self,
        documents_path: str,
        metadata: Dict[str, Any]
    ) -> int:
        """
        Ingest documents through layers 1-3.
        
        Flow:
        1. Document Processing: Load & normalize
        2. Chunking: Split into chunks
        3. Embedding + Storage: Generate embeddings & store in Pinecone
        
        Args:
            documents_path: Path to documents directory
            metadata: Document metadata (user_id, team_id, access_level, etc.)
        
        Returns:
            Number of chunks ingested
        """
        logger.info("ingest_start", path=documents_path, metadata=metadata)

        # Layer 1: Document Processing
        logger.info("layer_1_processing")
        documents = await self.document_processor.load_documents(documents_path)
        documents = await self.document_processor.preprocess(documents, metadata)
        logger.info("layer_1_complete", document_count=len(documents))

        # Layer 2: Chunking Strategy
        logger.info("layer_2_chunking")
        chunks = await self.chunker.create_chunks(documents)
        logger.info("layer_2_complete", chunk_count=len(chunks))

        # Layer 3: Embedding + Storage
        logger.info("layer_3_embedding_storage")
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = await self.embedding_engine.embed_batch(chunk_texts)
        stored_count = await self.vector_store.add_documents(
            chunks, 
            embeddings, 
            metadata
        )
        logger.info("layer_3_complete", stored_count=stored_count)

        logger.info("ingest_complete", chunks_stored=stored_count)
        return stored_count

    async def query(
        self,
        query_text: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute full 7-layer RAG query pipeline.
        
        Flow:
        1. Query Processing: Normalize & expand query
        2. Embedding: Generate query embedding
        3. Retrieval: Search Pinecone (layer 3)
        4. Permission Filtering: Apply RBAC/ABAC (layer 5)
        5. Reranking: Cross-encoder reranking (layer 6)
        6. LLM Generation: Generate response with Ollama (layer 7)
        
        Args:
            query_text: User query
            user_context: User info {user_id, team_id, access_level}
        
        Returns:
            Complete response with metadata and source attribution
        """
        logger.info("query_start", query=query_text, user=user_context.get("user_id"))

        # Layer 4: Query Processing
        logger.info("layer_4_query_processing")
        processed_query = await self.query_processor.process(query_text)
        logger.info("layer_4_complete", normalized=processed_query.normalized_text)

        # Layer 3: Embedding + Retrieval
        logger.info("layer_3_retrieval")
        query_embedding = await self.embedding_engine.embed(
            processed_query.normalized_text
        )
        candidates = await self.vector_store.search(
            query_embedding,
            top_k=20
        )
        logger.info("layer_3_retrieval_complete", candidates=len(candidates))

        # Layer 5: Permission Filtering
        logger.info("layer_5_permission_filtering")
        filtered_results = await self.access_control.filter_results(
            candidates,
            user_context
        )
        logger.info(
            "layer_5_complete",
            before_filter=len(candidates),
            after_filter=len(filtered_results)
        )

        # Layer 6: Reranking
        logger.info("layer_6_reranking")
        ranked_results = await self.reranker.rerank(
            query_text,
            filtered_results,
            top_k=5
        )
        logger.info("layer_6_complete", ranked_count=len(ranked_results))

        # Layer 7: LLM Generation
        logger.info("layer_7_llm_generation")
        response = await self.llm_client.generate_response(
            query=query_text,
            context_docs=ranked_results
        )
        logger.info("layer_7_complete", response_tokens=len(response.text.split()))

        result = {
            "query": query_text,
            "processed_query": processed_query.dict() if hasattr(processed_query, 'dict') else {},
            "pipeline_metrics": {
                "retrieved_documents": len(candidates),
                "filtered_documents": len(filtered_results),
                "ranked_documents": len(ranked_results),
            },
            "response": response.text,
            "confidence": response.confidence,
            "sources": [
                {
                    "content": doc.content[:100],
                    "metadata": doc.metadata,
                }
                for doc in ranked_results
            ],
            "timestamp": datetime.now().isoformat(),
            "all_layers_used": [layer.value for layer in RAGLayer]
        }

        logger.info("query_complete", result_keys=list(result.keys()))
        return result

    async def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get statistics for all 7 layers."""
        return {
            "layer_1_document_processing": {
                "documents_processed": await self.document_processor.get_stats()
            },
            "layer_2_chunking": {
                "total_chunks": await self.chunker.get_stats()
            },
            "layer_3_embedding_storage": {
                "embeddings_generated": await self.embedding_engine.get_stats(),
                "vectors_stored": await self.vector_store.get_stats()
            },
            "layer_4_query_processing": {
                "queries_processed": await self.query_processor.get_stats()
            },
            "layer_5_permission_filtering": {
                "access_control_stats": await self.access_control.get_stats()
            },
            "layer_6_reranking": {
                "reranking_stats": await self.reranker.get_stats()
            },
            "layer_7_llm_generation": {
                "responses_generated": await self.llm_client.get_stats()
            }
        }
