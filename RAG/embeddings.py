"""Layer 3a: Embeddings - Generate and cache embeddings using Sentence Transformers."""

import logging
from typing import List, Dict, Any, Optional
from functools import lru_cache
import structlog

logger = structlog.get_logger(__name__)


class EmbeddingEngine:
    """Layer 3a: Generate embeddings using Sentence Transformers."""
    
    def __init__(self, config: "EmbeddingConfig"):
        """Initialize embedding engine."""
        self.config = config
        self.embeddings_generated = 0
        
        try:
            from sentence_transformers import SentenceTransformer
            
            self.model = SentenceTransformer(
                config.model_name,
                device=config.device
            )
            
            logger.info(
                "embedding_model_loaded",
                model_name=config.model_name,
                device=config.device,
                dimension=config.embedding_dim
            )
        
        except ImportError:
            logger.error("sentence_transformers_not_installed")
            raise
        except Exception as e:
            logger.error("embedding_model_load_error", error=str(e))
            raise
    
    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        logger.debug("embedding_single_text", text_length=len(text))
        
        try:
            embedding = self.model.encode(
                text,
                normalize_embeddings=self.config.normalize_embeddings,
                convert_to_numpy=False
            )
            
            self.embeddings_generated += 1
            return embedding.tolist() if hasattr(embedding, 'tolist') else embedding
        
        except Exception as e:
            logger.error("embedding_generation_error", error=str(e))
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        logger.info(
            "embedding_batch",
            batch_size=len(texts),
            avg_text_length=sum(len(t) for t in texts) // len(texts) if texts else 0
        )
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=self.config.batch_size,
                normalize_embeddings=self.config.normalize_embeddings,
                show_progress_bar=True,
                convert_to_numpy=False
            )
            
            self.embeddings_generated += len(texts)
            
            # Convert to list of lists
            result = []
            for emb in embeddings:
                if hasattr(emb, 'tolist'):
                    result.append(emb.tolist())
                else:
                    result.append(emb)
            
            logger.info(
                "embedding_batch_complete",
                count=len(result),
                dimension=len(result[0]) if result else 0
            )
            
            return result
        
        except Exception as e:
            logger.error("batch_embedding_error", error=str(e))
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get embedding statistics."""
        return {
            "embeddings_generated": self.embeddings_generated,
            "model_name": self.config.model_name,
            "dimension": self.config.embedding_dim,
            "device": self.config.device,
        }
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch."""
        try:
            embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()


class OpenAIEmbedding(EmbeddingModel):
    """OpenAI embedding API."""

    def __init__(self, model_name: str = "text-embedding-3-small", api_key: Optional[str] = None):
        """Initialize OpenAI embedding."""
        try:
            import openai
            from openai import OpenAI

            self.api_key = api_key
            self.model_name = model_name
            self.client = OpenAI(api_key=api_key)
            logger.info(f"Initialized OpenAI embedding model: {model_name}")
        except ImportError:
            logger.error("openai not installed. Install with: pip install openai")
            raise

    def embed(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API."""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model_name,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding from OpenAI: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch."""
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model_name,
            )
            # Sort by index to maintain order
            embeddings = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in embeddings]
        except Exception as e:
            logger.error(f"Error generating embeddings from OpenAI: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        if self.model_name == "text-embedding-3-small":
            return 1536
        elif self.model_name == "text-embedding-3-large":
            return 3072
        else:
            return 1536


class EmbeddingCache:
    """Cache for embeddings."""

    def __init__(self, cache_size: int = 10000):
        """Initialize cache."""
        self.cache_size = cache_size
        self.cache = {}

    def get(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache."""
        return self.cache.get(text)

    def set(self, text: str, embedding: List[float]):
        """Set embedding in cache."""
        if len(self.cache) >= self.cache_size:
            # Simple eviction: remove first item
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        self.cache[text] = embedding

    def clear(self):
        """Clear cache."""
        self.cache.clear()
