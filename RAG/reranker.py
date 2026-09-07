"""Layer 6: Reranking - Cross-encoder based document reranking."""

import logging
from typing import List, Dict, Any, Tuple
import structlog

logger = structlog.get_logger(__name__)


class CrossEncoderReranker:
    """Layer 6: Rerank documents using cross-encoder models."""
    
    def __init__(self, retrieval_config: "RetrievalConfig"):
        """Initialize cross-encoder reranker."""
        self.config = retrieval_config
        self.reranked_count = 0
        
        if self.config.enable_reranking:
            try:
                from sentence_transformers import CrossEncoder
                self.model = CrossEncoder(self.config.rerank_model)
                logger.info(
                    "cross_encoder_loaded",
                    model=self.config.rerank_model
                )
            except ImportError:
                logger.warning(
                    "cross_encoder_unavailable",
                    msg="Install sentence-transformers for reranking"
                )
                self.model = None
        else:
            self.model = None
        
        logger.info(
            "reranker_initialized",
            enabled=self.config.enable_reranking,
            model=self.config.rerank_model if self.config.enable_reranking else "disabled"
        )
    
    async def rerank(
        self,
        query: str,
        documents: List["Chunk"],
        top_k: int = 5
    ) -> List["Chunk"]:
        """Rerank documents using cross-encoder."""
        logger.info(
            "reranking_start",
            query_snippet=query[:30],
            document_count=len(documents),
            top_k=top_k
        )
        
        if not self.config.enable_reranking or not self.model or not documents:
            logger.info("reranking_skipped", reason="disabled_or_no_documents")
            return documents[:top_k]
        
        try:
            # Prepare query-document pairs
            pairs = [
                (query, doc.content[:512])  # Limit content length
                for doc in documents
            ]
            
            # Get scores from cross-encoder
            scores = self.model.predict(pairs)
            
            # Create scored tuples
            scored_docs = [
                (doc, float(score))
                for doc, score in zip(documents, scores)
            ]
            
            # Sort by score (descending)
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            # Return top_k
            reranked = [doc for doc, _ in scored_docs[:top_k]]
            
            self.reranked_count += len(documents)
            
            logger.info(
                "reranking_complete",
                original_count=len(documents),
                returned_count=len(reranked),
                top_score=scores.max() if len(scores) > 0 else 0
            )
            
            return reranked
        
        except Exception as e:
            logger.error("reranking_failed", error=str(e))
            # Fallback: return top_k by original order
            return documents[:top_k]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get reranker statistics."""
        return {
            "total_reranked": self.reranked_count,
            "reranker_enabled": self.config.enable_reranking,
            "model": self.config.rerank_model if self.config.enable_reranking else "disabled",
        }
