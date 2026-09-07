"""Example usage of the RAG pipeline."""

import logging
from pathlib import Path
from app import RAGApplication
from config import RAGConfig, EmbeddingConfig, ChunkingConfig, LLMConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Example: Basic RAG pipeline usage."""
    logger.info("=" * 50)
    logger.info("Example 1: Basic RAG Pipeline Usage")
    logger.info("=" * 50)

    # Initialize RAG application with default config
    rag_app = RAGApplication(use_llm=True)

    # Check if sample documents exist
    sample_docs_dir = Path("./data/documents")
    if sample_docs_dir.exists() and list(sample_docs_dir.glob("*")):
        # Ingest documents
        num_chunks = rag_app.ingest(str(sample_docs_dir))
        logger.info(f"Ingested documents, created {num_chunks} chunks")

        # Get statistics
        stats = rag_app.get_pipeline_stats()
        logger.info(f"Pipeline stats: {stats}")

        # Answer a question
        query = "What is the main topic of the documents?"
        result = rag_app.answer(query)
        logger.info(f"Query: {query}")
        logger.info(f"Answer: {result['answer']}")
        logger.info(f"Sources: {result['sources']}")
    else:
        logger.warning("No documents found in ./data/documents directory")
        logger.info("Create sample documents to test the pipeline")


def example_custom_config():
    """Example: RAG pipeline with custom configuration."""
    logger.info("\n" + "=" * 50)
    logger.info("Example 2: Custom Configuration")
    logger.info("=" * 50)

    # Create custom configuration
    config = RAGConfig(
        embedding=EmbeddingConfig(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
        ),
        chunking=ChunkingConfig(
            chunk_size=500,
            chunk_overlap=50,
        ),
        llm=LLMConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=1024,
        ),
        top_k=3,
        similarity_threshold=0.3,
    )

    # Initialize with custom config
    rag_app = RAGApplication(config=config, use_llm=False)  # Use mock LLM for demo
    logger.info("Initialized RAG with custom configuration")
    logger.info(f"Config: {config}")


def example_retrieval_only():
    """Example: Using only retrieval without LLM generation."""
    logger.info("\n" + "=" * 50)
    logger.info("Example 3: Retrieval Only")
    logger.info("=" * 50)

    rag_app = RAGApplication(use_llm=False)

    sample_docs_dir = Path("./data/documents")
    if sample_docs_dir.exists() and list(sample_docs_dir.glob("*")):
        # Ingest documents
        rag_app.ingest(str(sample_docs_dir))

        # Retrieve documents
        query = "Tell me about transformers"
        result = rag_app.pipeline.query(query, top_k=5)

        logger.info(f"Query: {query}")
        logger.info(f"Number of retrieved documents: {len(result['retrieved_documents'])}")
        for i, doc in enumerate(result["retrieved_documents"], 1):
            logger.info(f"\nDocument {i}:")
            logger.info(f"  Relevance: {doc['relevance']:.2%}")
            logger.info(f"  Content: {doc['content'][:100]}...")
    else:
        logger.warning("No documents found in ./data/documents directory")


def create_sample_documents():
    """Create sample documents for testing."""
    logger.info("\n" + "=" * 50)
    logger.info("Creating Sample Documents")
    logger.info("=" * 50)

    sample_docs = {
        "sample1.txt": """Transformer architecture revolutionized natural language processing.
        
The Transformer model, introduced in 2017, uses self-attention mechanisms to process sequences 
in parallel, making it more efficient than previous RNN-based approaches. The architecture consists 
of an encoder and decoder, both built from stacked self-attention layers.

Key components include:
- Multi-head self-attention for parallel processing
- Feed-forward networks
- Positional encoding for sequence order
- Layer normalization and residual connections

This architecture forms the basis for modern large language models like BERT, GPT, and T5.""",
        "sample2.txt": """Attention mechanisms are the core of modern NLP models.

Attention allows models to focus on different parts of input sequences when producing outputs.
Self-attention specifically computes attention weights between all pairs of positions in a sequence,
enabling the model to relate different positions to each other regardless of their distance.

The attention mechanism computes:
1. Query, Key, Value projections from input
2. Similarity scores between queries and keys
3. Weights normalized using softmax
4. Weighted sum of values

This enables the model to capture long-range dependencies effectively.""",
    }

    docs_dir = Path("./data/documents")
    docs_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in sample_docs.items():
        file_path = docs_dir / filename
        file_path.write_text(content)
        logger.info(f"Created: {file_path}")


if __name__ == "__main__":
    # Create sample documents first
    create_sample_documents()

    # Run examples
    example_basic_usage()
    example_custom_config()
    example_retrieval_only()

    logger.info("\n" + "=" * 50)
    logger.info("Examples completed!")
    logger.info("=" * 50)
