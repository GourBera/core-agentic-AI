"""Layer 7: LLM Generation - Local Ollama integration for response generation."""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
import structlog
import httpx

logger = structlog.get_logger(__name__)


@dataclass
class GeneratedResponse:
    """Represents an LLM-generated response."""
    text: str
    model: str
    confidence: float
    tokens_used: int


class OllamaClient:
    """Layer 7: Generate responses using local Ollama LLM."""
    
    def __init__(self, config: "OllamaConfig"):
        """Initialize Ollama client."""
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout
        )
        self.responses_generated = 0
        
        logger.info(
            "ollama_client_initialized",
            base_url=config.base_url,
            model=config.model_name,
            temperature=config.temperature
        )
    
    async def generate_response(
        self,
        query: str,
        context_docs: List["Chunk"]
    ) -> GeneratedResponse:
        """Generate response using Ollama."""
        logger.info(
            "generating_response",
            query=query[:30],
            context_docs=len(context_docs)
        )
        
        # Build prompt
        prompt = self._build_prompt(query, context_docs)
        
        try:
            # Call Ollama API
            response = await self.client.post(
                "/api/generate",
                json={
                    "model": self.config.model_name,
                    "prompt": prompt,
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "top_k": self.config.top_k,
                    "num_predict": self.config.max_tokens,
                    "stream": False,
                }
            )
            
            if response.status_code != 200:
                logger.error(
                    "ollama_error",
                    status_code=response.status_code,
                    error=response.text
                )
                return GeneratedResponse(
                    text="Error generating response",
                    model=self.config.model_name,
                    confidence=0.0,
                    tokens_used=0
                )
            
            data = response.json()
            generated_text = data.get("response", "").strip()
            tokens_used = len(generated_text.split())
            
            # Calculate confidence based on response quality
            confidence = self._calculate_confidence(generated_text, len(context_docs))
            
            result = GeneratedResponse(
                text=generated_text,
                model=self.config.model_name,
                confidence=confidence,
                tokens_used=tokens_used
            )
            
            self.responses_generated += 1
            
            logger.info(
                "response_generated",
                tokens=tokens_used,
                confidence=confidence,
                model=self.config.model_name
            )
            
            return result
        
        except Exception as e:
            logger.error("generation_failed", error=str(e))
            return GeneratedResponse(
                text=f"Error: {str(e)}",
                model=self.config.model_name,
                confidence=0.0,
                tokens_used=0
            )
    
    def _build_prompt(self, query: str, context_docs: List["Chunk"]) -> str:
        """Build prompt with context."""
        # Build context from documents
        context_parts = []
        for i, doc in enumerate(context_docs, 1):
            context_parts.append(f"[Source {i}]:\n{doc.content[:500]}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question accurately and concisely.

Context:
{context}

Question: {query}

Answer:"""
        
        return prompt
    
    def _calculate_confidence(self, response: str, context_docs_count: int) -> float:
        """Calculate confidence score for response."""
        # Simple confidence heuristic
        confidence = 0.5
        
        # More context = higher confidence
        confidence += min(context_docs_count * 0.1, 0.3)
        
        # Longer response = potentially more thoughtful
        response_length = len(response.split())
        if response_length > 50:
            confidence += 0.1
        
        return min(confidence, 0.95)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get LLM client statistics."""
        return {
            "responses_generated": self.responses_generated,
            "model": self.config.model_name,
            "base_url": self.config.base_url,
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
