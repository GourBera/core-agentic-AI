"""Main RAG application with end-to-end integration."""

import logging
from typing import Dict, Any, Optional
from pipeline import RAGPipeline
from llm import OpenAILLM, MockLLM
from config import RAGConfig

logger = logging.getLogger(__name__)


class RAGApplication:
    """Complete RAG application."""

    def __init__(self, config: Optional[RAGConfig] = None, use_llm: bool = True):
        """Initialize RAG application."""
        self.config = config or RAGConfig()
        self.pipeline = RAGPipeline(self.config)

        # Initialize LLM if requested
        if use_llm:
            try:
                self.llm = OpenAILLM(
                    model=self.config.llm.model_name,
                    temperature=self.config.llm.temperature,
                    max_tokens=self.config.llm.max_tokens,
                    api_key=self.config.llm.api_key,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI LLM: {e}. Using mock LLM.")
                self.llm = MockLLM()
        else:
            self.llm = MockLLM()

        logger.info("RAG Application initialized")

    def ingest(self, documents_path: str) -> int:
        """Ingest documents."""
        return self.pipeline.ingest_documents(documents_path)

    def answer(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """Answer a question using RAG."""
        try:
            logger.info(f"Processing query: {query}")

            # Get retrieval results
            retrieval_result = self.pipeline.query(query, top_k)

            # Generate answer using LLM
            prompt = retrieval_result["prompt"]
            answer = self.llm.generate(prompt)

            result = {
                "query": query,
                "answer": answer,
                "retrieved_documents": retrieval_result["retrieved_documents"],
                "sources": [
                    doc.get("metadata", {}).get("original_source", "Unknown")
                    for doc in retrieval_result["retrieved_documents"]
                ],
            }

            logger.info("Query processing complete")
            return result
        except Exception as e:
            logger.error(f"Error answering query: {e}")
            raise

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return self.pipeline.get_stats()

    def clear(self):
        """Clear all data."""
        self.pipeline.clear()
