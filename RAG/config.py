"""
Production-grade configuration for 7-layer RAG pipeline.

Configuration supports:
- Pinecone for vector storage
- Local Ollama for LLM
- Hybrid chunking (overlap + semantic)
- Metadata-based access control
- Cross-encoder reranking
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path
import os
from dotenv import load_dotenv


load_dotenv()


@dataclass
class EmbeddingConfig:
    """Configuration for embedding model (Layer 3)."""
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = field(default_factory=lambda: os.getenv("EMBEDDING_DEVICE", "cuda"))
    batch_size: int = 32
    normalize_embeddings: bool = True
    embedding_dim: int = 384
    cache_embeddings: bool = True


@dataclass
class PineconeConfig:
    """Configuration for Pinecone vector store (Layer 3)."""
    api_key: str = field(default_factory=lambda: os.getenv("PINECONE_API_KEY", ""))
    environment: str = field(default_factory=lambda: os.getenv("PINECONE_ENVIRONMENT", "prod"))
    index_name: str = field(default_factory=lambda: os.getenv("PINECONE_INDEX_NAME", "rag-production"))
    metric: str = "cosine"
    dimension: int = 384  # Must match embedding_dim
    timeout: int = 30
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")


@dataclass
class OllamaConfig:
    """Configuration for local Ollama LLM (Layer 7)."""
    base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    model_name: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama2"))
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    max_tokens: int = 2048
    timeout: int = 300  # 5 minutes


@dataclass
class ChunkingConfig:
    """Configuration for document chunking strategies (Layer 2)."""
    # Overlap chunking (recursive character splitting)
    overlap_chunk_size: int = 1000
    overlap_chunk_overlap: int = 200
    separator: str = "\n\n"
    
    # Semantic chunking
    semantic_chunk_size: int = 512
    breakpoint_percentile_threshold: int = 95
    
    # Hybrid strategy
    use_semantic_chunking: bool = True
    use_overlap_chunking: bool = True
    semantic_weight: float = 0.6  # Balance: semantic (0.6) vs overlap (0.4)


@dataclass
class MetadataConfig:
    """Configuration for metadata filtering (Layer 5)."""
    enable_access_control: bool = True
    
    # Metadata fields required for filtering
    required_fields: List[str] = field(default_factory=lambda: [
        "user_id",
        "team_id",
        "access_level"
    ])
    
    # Access levels (hierarchical)
    access_levels: Dict[str, int] = field(default_factory=lambda: {
        "public": 0,      # Anyone
        "internal": 1,    # Organization
        "team": 2,        # Team members
        "private": 3,     # Creator only
    })


@dataclass
class RetrievalConfig:
    """Configuration for retrieval strategy (Layer 6)."""
    top_k: int = 5
    similarity_threshold: float = 0.5
    
    # Metadata filtering
    filter_by_user: bool = True
    filter_by_team: bool = True
    filter_by_access_level: bool = True
    
    # Reranking
    enable_reranking: bool = True
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"
    rerank_top_k: int = 3


@dataclass
class RAGConfig:
    """Main configuration for 7-layer RAG pipeline."""
    # Component configs
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    pinecone: PineconeConfig = field(default_factory=PineconeConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    metadata: MetadataConfig = field(default_factory=MetadataConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    
    # Paths
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("RAG_DATA_DIR", "./data")))
    cache_dir: Path = field(default_factory=lambda: Path(os.getenv("RAG_CACHE_DIR", "./cache")))
    
    # Logging
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_format: str = "json"  # json or text
    
    # Performance
    enable_caching: bool = True
    cache_ttl: int = 3600  # seconds
    batch_processing: bool = True
    batch_size: int = 32
    
    def __post_init__(self):
        """Validate and initialize configuration."""
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate Pinecone config
        if not self.pinecone.api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        # Ensure embedding dimension matches
        if self.embedding.embedding_dim != self.pinecone.dimension:
            raise ValueError(
                f"Embedding dimension ({self.embedding.embedding_dim}) "
                f"must match Pinecone dimension ({self.pinecone.dimension})"
            )
